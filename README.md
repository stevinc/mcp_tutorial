# MCP Tutorial: Team Notes

Piccolo MCP server con [FastMCP](https://gofastmcp.com) che espone:

- **Tool**: `add_note`, `search_notes`, `list_notes`, `import_notes` (con progress)
- **Resource**: `notes://all`, `notes://{note_id}`
- **Prompt**: `summarize_notes`

Le note sono **in memoria**: a ogni avvio si riparte dalle 3 note di esempio in `server.py`.

## Setup

```bash
uv sync
```

## Avviare il server

Due varianti, stesso codice (`server.py`), stessi tool:

|                 | Comando                      | Trasporto                                 | Chi lo avvia                                |
| --------------- | ---------------------------- | ----------------------------------------- | ------------------------------------------- |
| **stdio** | `uv run mcp-tutorial`      | stdin/stdout                              | il **client**, come processo figlio   |
| **HTTP**  | `uv run mcp-tutorial-http` | Streamable HTTP su `127.0.0.1:8001/mcp` | **tu**, e resta acceso (vedi punto 5) |

Con stdio di norma **non lo lanci a mano**: i punti 1-4 sotto lo avviano da soli (il client Python, Claude Code,
Claude Desktop). Se lanci `uv run mcp-tutorial` in un terminale sembra "bloccato": è normale, resta in attesa
di messaggi MCP su stdin (esci con `Ctrl+C`). Per vederlo funzionare senza un client vero usa l'Inspector (punto 2).

## 1. Client Python

```bash
uv run mcp-tutorial-client
```

Da VS Code: configurazione **Client MCP demo** in `.vscode/launch.json`.

## 2. MCP Inspector

Serve Node.js.

```bash
uv run fastmcp dev inspector src/mcp_tutorial/server.py --with-editable .
```

Apri l'URL stampato e premi **Connect**, poi prova le tab Tools, Resources e Prompts.

## 3. Claude Code

```bash
claude mcp add team-notes -- uv run --directory "$(pwd)" mcp-tutorial
```

Apri una nuova sessione `claude`, controlla con `/mcp` che il server sia connesso,
poi chiedi per esempio: *"Quali decisioni ha preso il team sul processo?"*

## 4. Claude Desktop

In **Settings → Developer → Edit Config** aggiungi (percorsi assoluti: `which uv` e `pwd`):

```json
{
  "mcpServers": {
    "team-notes": {
      "command": "/percorso/assoluto/uv",
      "args": ["run", "--directory", "/percorso/assoluto/mcp_tutorial", "mcp-tutorial"]
    }
  }
}
```

Chiudi Claude Desktop con `Cmd+Q`, riaprilo e trovi `team-notes` tra gli strumenti della chat.

## 5. Via HTTP (Open WebUI e altri client remoti)

I punti 1-4 usano il trasporto **stdio**: il client lancia il server come processo figlio e ci parla
via stdin/stdout, quindi serve sulla stessa macchina. Per client che non possono lanciare un processo
(es. Open WebUI in un container) c'è la variante **Streamable HTTP**: stesso codice, stessi tool,
ma il server resta in ascolto su una porta.

```bash
uv run mcp-tutorial-http              # http://127.0.0.1:8001/mcp
uv run mcp-tutorial-http --port 9000  # porta diversa
```

Cosa cambia rispetto a stdio: il server si avvia **da solo** e va tenuto acceso; il client si collega a
un URL; non c'è autenticazione, quindi di default ascolta solo su `127.0.0.1`.
In Open WebUI (in Docker) l'URL è `http://host.docker.internal:8001/mcp`.

Note pratiche:

- Avvialo **prima** di usare i tool da Open WebUI. Se è spento, il tool semplicemente non risponde.
- Se parte con "porta già in uso", c'è un altro server sulla 8001: `lsof -ti:8001 | xargs kill`, oppure usa `--port`.
- In Open WebUI: *Admin Settings → External Tools → +* → MCP (Streamable HTTP) → URL sopra; poi attiva lo strumento nel modello (serve Function Calling = Native).
