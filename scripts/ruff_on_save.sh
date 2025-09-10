#!/bin/bash
cd "$(dirname "$0")/.." || exit 1
/Users/elena/Public/Code/astro-ai-agent/.venv1/bin/ruff format "$1"
/Users/elena/Public/Code/astro-ai-agent/.venv1/bin/ruff check "$1"
