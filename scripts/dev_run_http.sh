#!/usr/bin/env bash
set -euo pipefail

export EMAIL_MCP_TRANSPORT="streamable-http"
python -m email_mcp.main
