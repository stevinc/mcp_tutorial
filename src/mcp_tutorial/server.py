"""Server MCP di esempio: le note di un team, salvate in memoria.

- Tool     -> azioni che il modello decide di invocare
- Resource -> dati in sola lettura, identificati da un URI
- Prompt   -> template di messaggi riutilizzabili
"""

import asyncio
import json

from fastmcp import Context, FastMCP
from fastmcp.dependencies import CurrentContext
from fastmcp.exceptions import ResourceError, ToolError
from pydantic import BaseModel

mcp = FastMCP("Team Notes")

# "Database" in memoria: a ogni avvio si riparte da queste note.
notes_db: dict[int, dict] = {
    1: {
        "id": 1,
        "title": "Retro sprint 12",
        "content": "Decidiamo di introdurre code review obbligatorie. Azione: aggiornare il README.",
        "tags": ["retro", "processo"],
    },
    2: {
        "id": 2,
        "title": "Scelta database",
        "content": "Valutati Postgres e MongoDB: scelto Postgres per le transazioni.",
        "tags": ["architettura"],
    },
    3: {
        "id": 3,
        "title": "Rilascio v1.2",
        "content": "Rilascio previsto venerdì. Aperto: test di carico sull'API ordini.",
        "tags": ["release", "processo"],
    },
}


class NoteInput(BaseModel):
    title: str
    content: str


def save_note(title: str, content: str, tags: list[str] | None = None) -> dict:
    if not title.strip():
        raise ValueError("Il titolo della nota non può essere vuoto")
    note_id = max(notes_db, default=0) + 1
    note = {"id": note_id, "title": title.strip(), "content": content, "tags": tags or []}
    notes_db[note_id] = note
    return note


def find_notes(query: str) -> list[dict]:
    query = query.lower()
    return [
        note
        for note in notes_db.values()
        if query in note["title"].lower() or query in note["content"].lower() or query in note["tags"]
    ]


# --- Tools ------------------------------------------------------------------
# Docstring e type hint diventano la descrizione e lo schema che l'LLM vede.


@mcp.tool
def add_note(title: str, content: str, tags: list[str] | None = None) -> dict:
    """Crea una nuova nota e restituisce la nota salvata (con il suo id)."""
    try:
        return save_note(title, content, tags)
    except ValueError as error:
        raise ToolError(str(error)) from error


@mcp.tool
def search_notes(query: str) -> list[dict]:
    """Cerca note il cui titolo, contenuto o tag contiene `query`."""
    return find_notes(query)


@mcp.tool
def list_notes() -> list[dict]:
    """Restituisce tutte le note. Usala quando la ricerca per parole chiave non basta,
    ad esempio per domande su un argomento o un significato."""
    return list(notes_db.values())


@mcp.tool
async def import_notes(notes: list[NoteInput], ctx: Context = CurrentContext()) -> dict:
    """Importa più note in blocco, inviando notifiche di avanzamento."""
    # `ctx` è iniettato da FastMCP e non compare nello schema del tool.
    imported, skipped = [], []
    for index, note in enumerate(notes, start=1):
        await asyncio.sleep(0.3)  # simula lavoro, per vedere il progress
        try:
            imported.append(save_note(note.title, note.content))
        except ValueError as error:
            skipped.append(f"Nota #{index}: {error}")
        await ctx.report_progress(progress=index, total=len(notes), message=f"Importata {index}/{len(notes)}")
    return {"imported": imported, "skipped": skipped}


# --- Resources --------------------------------------------------------------


@mcp.resource("notes://all", mime_type="application/json")
def all_notes() -> str:
    """Elenco completo delle note."""
    return json.dumps(list(notes_db.values()), ensure_ascii=False, indent=2)


@mcp.resource("notes://{note_id}", mime_type="application/json")
def note_by_id(note_id: int) -> str:
    """Una singola nota, identificata dal suo id."""
    if note_id not in notes_db:
        raise ResourceError(f"Nota {note_id} non trovata")
    return json.dumps(notes_db[note_id], ensure_ascii=False, indent=2)


# --- Prompts ----------------------------------------------------------------


@mcp.prompt
def summarize_notes(topic: str) -> str:
    """Chiede all'LLM un riassunto delle note su un argomento."""
    found = find_notes(topic)
    if not found:
        return f"Non ci sono note su '{topic}'. Suggerisci quali informazioni raccogliere."
    bullet_list = "\n".join(f"- {note['title']}: {note['content']}" for note in found)
    return f"Riassumi in 3 punti le note del team su '{topic}', evidenziando decisioni e azioni aperte:\n\n{bullet_list}"


def main() -> None:
    # Trasporto stdio. Banner e log vanno su stderr, che i client (agenti, Claude Code...)
    # mostrano nel proprio terminale: li spegniamo per non coprire la chat.
    mcp.run(show_banner=False, log_level="WARNING")


if __name__ == "__main__":
    main()
