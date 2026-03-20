# Bot Implementation Plan

## Overview

This document describes the implementation plan for the Telegram bot that provides access to the Learning Management System (LMS). The bot allows students to check their scores, view available labs, and ask questions about their progress using natural language.

## Architecture

### Handler Separation (Separation of Concerns)

The core architectural decision is to separate command handlers from the Telegram transport layer. Each handler is a pure function that:
- Takes input (command text and optional context)
- Returns a text response
- Has no dependency on Telegram APIs

This pattern enables:
- **Testability**: Handlers can be tested without Telegram connection
- **Reusability**: Same logic works in `--test` mode, unit tests, and production
- **Maintainability**: Business logic is isolated from framework code

### Project Structure

```
bot/
├── bot.py              # Entry point with --test mode and Telegram startup
├── config.py           # Environment variable loading and validation
├── handlers/           # Command handlers (no Telegram dependency)
│   ├── __init__.py
│   ├── start.py        # /start command
│   ├── help.py         # /help command
│   ├── health.py       # /health command
│   ├── labs.py         # /labs command
│   └── scores.py       # /scores command
├── services/           # External service clients
│   ├── __init__.py
│   ├── lms_api.py      # LMS API client with Bearer auth
│   └── llm_client.py   # LLM client for intent routing (Task 3)
└── pyproject.toml      # Dependencies
```

## Implementation Phases

### Phase 1: Scaffold (Task 1)

Create the basic project structure with placeholder handlers. The bot responds to commands but returns static text. Key deliverables:
- `--test` mode that calls handlers directly
- Handler modules for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Configuration loading from `.env.bot.secret`

### Phase 2: Backend Integration (Task 2)

Connect handlers to the LMS API. Each handler makes real API calls:
- `/health` → `GET /health` — check backend status
- `/labs` → `GET /labs` — list available labs
- `/scores <lab>` → `GET /scores?lab=<lab>` — get student scores

The API client uses Bearer token authentication with credentials from environment variables.

### Phase 3: Intent Routing with LLM (Task 3)

Add natural language support using an LLM. Instead of requiring `/scores lab-04`, users can ask "what did I get on lab 4?". The LLM analyzes the query and calls the appropriate tool:
- Tool descriptions tell the LLM what each function does
- The LLM returns structured tool calls, not raw text
- Handlers execute based on LLM's tool selection

**Key insight**: The LLM routes based on tool descriptions, not regex. If routing fails, improve descriptions — don't add code-based routing.

### Phase 4: Docker Deployment (Task 4)

Containerize the bot and deploy alongside the backend. Key considerations:
- Containers use Docker service names, not `localhost`
- `host.docker.internal` for accessing host services (LLM API)
- Health checks and restart policies for reliability

## Testing Strategy

1. **Test mode**: `uv run bot.py --test "/command"` for manual testing
2. **Unit tests**: Test handlers in isolation (future work)
3. **Integration tests**: Test full flow from Telegram to API (future work)

## Acceptance Criteria

- [ ] `bot/PLAN.md` exists with at least 100 words ✓
- [ ] `bot/pyproject.toml` exists and `uv sync` succeeds
- [ ] `bot/handlers/` directory exists with handler modules
- [ ] `--test` mode works for all commands
- [ ] Bot responds in Telegram after deployment
