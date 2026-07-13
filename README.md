# Panache Homes Lead Qualification Bot

A Telegram bot that qualifies potential Dubai real-estate investors/leads using an LLM (Cohere). When enough lead details are collected, it assigns a grade (A/B/C/D) and forwards the lead to an n8n webhook.

---

## What this project does

1. **Telegram chat bot** (`backend/app.py`)
   - Responds to users with a premium “Panache Homes” consultant tone.
   - Uses a conversation memory per Telegram user.
2. **Lead extraction** (`backend/extractor.py`)
   - The bot asks the LLM to output **exactly one JSON object** containing:
     - `name`, `country`, `budget`, `funding`, `timeline`, `purpose`
   - Normalizes values (e.g., converts budget/timeline to integers; restricts `funding` and `purpose` to supported values).
3. **Lead grading** (`backend/grading.py`)
   - Produces `grade` based on budget/timeline.
4. **Webhook forwarding** (`backend/automation.py`)
   - Sends the final lead payload to an n8n webhook via HTTP POST.

---

## Repository structure

- `backend/app.py` — Telegram bot entrypoint + LLM chat + extraction + grading + webhook send
- `backend/extractor.py` — JSON extraction prompt + parsing + normalization
- `backend/grading.py` — grading logic (A/B/C/D)
- `backend/prompts.py` — system prompt that drives assistant behavior
- `backend/knowledge.py` — knowledge base used by the LLM
- `backend/automation.py` — n8n webhook POST
- `backend/config.py` — env var names (currently not fully used by `automation.py`)
- `backend/sheet.py` — Google Sheets helper (present but not used in `backend/app.py`)
- `backend/database.py` — SQLite table setup (present but not used in `backend/app.py`)
- `backend/state_manager.py` — in-memory state scaffolding (present but not used in `backend/app.py`)
- `backend/requirements.txt` — Python dependencies

---

## Lead model (payload)

Final lead payload sent to n8n contains:

- `name` (first name only, or `null`)
- `country` (or `null`)
- `budget` (AED integer, or `null`)
- `funding` (`Cash` or `Mortgage`, or `null`)
- `timeline` (months integer, or `null`)
- `purpose` (`Investment` or `Personal Use`, or `null`)
- `grade` (`A`, `B`, `C`, `D`)

The bot saves/forwards only when **at least 4** of the 6 fields are present (`should_save_lead` in `backend/app.py`).

---

## Environment variables

Create a `.env` file (recommended) with at least:

- `TELEGRAM_BOT_TOKEN` — Telegram bot token
- `COHERE_API_KEY` — Cohere API key
- `N8N_WEBHOOK` — intended n8n webhook URL (note: `backend/automation.py` currently uses a hardcoded URL)

Example:

```env
TELEGRAM_BOT_TOKEN=xxxxxx
COHERE_API_KEY=yyyyyy
N8N_WEBHOOK=https://your-n8n-instance/webhook/path
```

> Note: `backend/automation.py` currently posts to a hardcoded n8n URL. To use `N8N_WEBHOOK`, update that file to read from `os.getenv("N8N_WEBHOOK")`.

---

## Setup

1. Install Python 3.11 (repo targets `backend/runtime.txt` -> Python 3.11.0)
2. Create and activate a virtual environment
   - `python -m venv .venv`
   - Windows (PowerShell): `.venv\\Scripts\\Activate.ps1`
   - Windows (cmd): `.venv\\Scripts\\activate.bat`
3. Install dependencies:

```bash
pip install -r backend/requirements.txt

```

4. Add environment variables in `.env`

---

## Run the bot

From the project root:

```bash
python backend/app.py in railway ai deployment
```

You should see `Bot Running...` in the terminal.

---

## Testing utilities

- `backend/test_bot.py` — checks Telegram bot connectivity (`get_me`)
- `backend/test_n8n.py` — sends a sample lead payload to the n8n webhook

---

## n8n integration

The bot sends an HTTP POST with `json=<lead payload>` to the n8n webhook URL.

If you want to reuse the existing config var, change `backend/automation.py` to:

- read `N8N_WEBHOOK` from environment
- fall back to the hardcoded URL only if not set

---

## Notes / current limitations (as implemented)

- The main bot flow forwards leads to n8n; Google Sheets and SQLite modules exist but are **not currently invoked** by `backend/app.py`.
- `search_files` is not part of runtime; it’s a tooling limitation in this environment.

---

## License

Add your project license here (not specified in the repository).
