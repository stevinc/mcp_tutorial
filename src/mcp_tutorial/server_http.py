"""Stesso server di `server.py` (stessi tool, resource e prompt), esposto via HTTP.

Serve ai client che non possono lanciare un processo locale (es. Open WebUI in un container).
Endpoint: http://<host>:<porta>/mcp
"""

import argparse

from mcp_tutorial.server import mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Team Notes MCP server (Streamable HTTP)")
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Interfaccia in ascolto. 127.0.0.1 = solo questo Mac; 0.0.0.0 = raggiungibile anche dai container (nessuna autenticazione!)",
    )
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    mcp.run(transport="http", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
