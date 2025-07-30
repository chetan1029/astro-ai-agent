#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
/Users/elena/Public/Code/astro-ai-agent/.venv/bin/ruff format "$1"
/Users/elena/Public/Code/astro-ai-agent/.venv/bin/ruff check "$1"
