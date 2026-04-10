# Orchestra

**Multi-agent content system for creators who publish across platforms.**

Orchestra takes a single idea and runs it through a coordinated team of AI agents — a planner, three platform writers, and a brand critic — each with a distinct role and job. The result is platform-native content for Instagram, Threads, and LinkedIn, along with a visible log of how the agents collaborated to get there.

Built by [Meridian Global](https://github.com/MeridianGlobal).

---

## What it does

You type one idea. Orchestra handles the rest:

1. **Strategic Brain (Planner)** reads your idea and your voice profile, then produces a structured brief — tone, audience, core angle, per-platform notes
2. **Platform agents** (Visual Storyteller, Narrative Builder, Professional Framer) each write natively for their medium, reading each other's output before finalizing
3. **Quality Judge (Critic)** reviews all three drafts against your brand voice, rewrites weak spots, and flags anything off-brand
4. **You** review the final outputs and copy to publish

---

## Why it's different

Most "AI content tools" call the same model three times with different format instructions. Orchestra doesn't do that.

The system is built around a **Brief object** — a structured dict that the Planner produces and every downstream agent reads from. Agents don't just see the original prompt; they see what other agents wrote and react to it. The Critic reads all three drafts simultaneously.

This makes the outputs genuinely different from each other, and the interaction log genuinely interesting to read.

---

## Demo

> GIF coming — [watch this repo](https://github.com/MeridianGlobal/orchestra)

---

## Project structure

```
.
├── orchestra/                   ← Python package
│   ├── backend/
│   │   ├── agents/              # One file per agent — easy to extend
│   │   │   ├── base.py
│   │   │   ├── planner.py
│   │   │   ├── instagram.py
│   │   │   ├── threads.py
│   │   │   ├── linkedin.py
│   │   │   └── critic.py
│   │   ├── core/
│   │   │   ├── brief.py         # The Brief dataclass — system spine
│   │   │   ├── orchestrator.py  # Pipeline runner + SSE event generator
│   │   │   └── voice_store.py   # Load brand voice YAML
│   │   ├── api/
│   │   │   ├── routes.py              # Core route: POST /api/run
│   │   │   └── integrations_routes.py # App-layer routes: Gmail + LinkedIn
│   │   ├── app_layer/
│   │   │   └── integrations/
│   │   │       ├── gmail_scanner.py
│   │   │       └── linkedin_publisher.py
│   │   └── main.py
│   ├── voice_profiles/
│   │   └── default.yaml         # Your brand voice — edit this first
│   └── examples/
│       ├── run_cli.py           # Run the full pipeline in terminal
├── frontend/                    # Next.js 15 app router
│   ├── app/
│   │   ├── page.tsx             # Main page — input, timeline, final outputs
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   └── StreamCard.tsx       # Live agent output card with reveal animation
│   └── lib/
│       └── sse.ts               # SSE parser (fetch + ReadableStream)
├── requirements.txt
└── env.example
```

---

## Quickstart

**Requirements:** Python 3.11+, Node 18+, an Anthropic API key

```bash
# Clone
git clone https://github.com/MeridianGlobal/orchestra.git
cd orchestra

# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-integrations.txt
cp env.example .env        # add your ANTHROPIC_API_KEY

# Edit your voice profile before your first run
nano orchestra/voice_profiles/default.yaml

# CLI demo (run from repo root)
python orchestra/examples/run_cli.py "your idea here"

# Start API server (run from repo root)
uvicorn orchestra.backend.main:app --reload

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

Open [localhost:3000](http://localhost:3000).

The API and frontend can also run independently. The frontend connects to the backend at `http://localhost:8000` by default — change this in `frontend/.env.local`.

---

## Local testing

There is now a small refactor-focused smoke suite for route wiring and import safety, plus a simple shell check for manual verification.

### Frontend

```bash
cd frontend
npm install
npm run build
npm run dev
```

What to verify:

- `npm run build` completes successfully
- the app loads at `http://localhost:3000`
- entering an idea and clicking `Run Orchestra` does not produce client-side errors
- the live timeline renders streaming cards and the final output cards appear

### Backend

```bash
source .venv/bin/activate
uvicorn orchestra.backend.main:app --reload
```

Useful smoke tests:

```bash
# Main pipeline route (streams SSE)
curl -N -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"idea":"A post about why small teams should document decisions","voice_profile":"default"}'

# Gmail scanner route
curl http://localhost:8000/api/ideas/scan

# OpenAPI/manual route smoke check
sh scripts/smoke_test_routes.sh
```

Expected behavior:

- `/api/run` streams `event:` / `data:` messages in order
- `/api/ideas/scan` returns Gmail ideas if authenticated
- if Gmail is not set up yet, `/api/ideas/scan` should return:
  `"Gmail not authenticated. Run: python orchestra/examples/gmail_auth.py"`

### Full stack

Run the backend on `:8000` and the frontend on `:3000`, then:

1. Open `http://localhost:3000`
2. Submit a test idea
3. Confirm the pipeline streams from planner through critic
4. Confirm the final Instagram, Threads, and LinkedIn outputs render
5. Check both terminals for errors

### Automated smoke tests

Run the refactor-focused backend smoke tests from the repo root:

```bash
pytest tests/test_app_smoke.py tests/test_route_boundaries.py tests/test_import_paths.py -q
```

---

## Environment variables

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-...

# Optional — defaults to claude-haiku-4-5 if not set
ANTHROPIC_MODEL=claude-haiku-4-5

# LinkedIn publishing (required for POST /api/publish/linkedin)
# Get your access token from the LinkedIn Developer Portal
# Get your person URN from https://api.linkedin.com/v2/userinfo
LINKEDIN_ACCESS_TOKEN=your_linkedin_personal_access_token
LINKEDIN_PERSON_URN=urn:li:person:your_person_id

# Gmail idea scanner
# 1. Enable the Gmail API in Google Cloud
# 2. Download OAuth desktop credentials
# 3. Run: python orchestra/examples/gmail_auth.py
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
```

---

## Your brand voice

`orchestra/voice_profiles/default.yaml` is where Orchestra learns who you are. Edit it before your first run:

```yaml
creator:
  name: "Your name"
  archetype: "How you'd describe yourself in one line"

voice:
  adjectives: ["direct", "grounded", "specific"]
  not: ["corporate", "hustle-bro", "preachy"]

signature_moves:
  - "Lead with a specific observation, not a general claim"
  - "End with a question or next step, not a lesson"

content_rules:
  max_emojis: 2
  hashtag_style: "3-5 specific, never generic"
  cta_style: "implicit"
  avoid_phrases:
    - "game changer"
    - "here's the thing"
```

The Planner reads this on every run. The Critic uses it to flag off-brand language. The more specific you make it, the better the output.

---

## Adding a new platform agent

1. Create `orchestra/backend/agents/your_platform.py`
2. Subclass `BaseAgent`, implement `build_prompt()` and `run()`
3. Register in `orchestrator.py`

That's it. One file, no framework to learn.

---

## Tech stack

| Layer        | Choice                              |
| ------------ | ----------------------------------- |
| LLM          | Claude (Anthropic)                  |
| Backend      | Python + FastAPI                    |
| App layer    | Gmail + LinkedIn integrations       |
| Streaming    | Server-Sent Events                  |
| Frontend     | Next.js 15 (app router, custom CSS) |
| Voice config | YAML                                |

No LangChain. No vector databases. No Tailwind. No external queue. Runs entirely local except for the API call.

---

## Roadmap

**Core**
- [x] Planner → platform agents → critic pipeline
- [x] Two-pass refinement (agents read each other's output)
- [x] Brand voice YAML (Critic enforces it)
- [x] FastAPI + SSE streaming endpoint
- [x] Next.js frontend with live agent timeline

**Publishing**
- [x] LinkedIn publish endpoint (`POST /api/publish/linkedin`)
- [ ] LinkedIn publish button in frontend (after generation completes)
- [ ] Instagram publishing via Graph API

**Input sources**
- [x] Gmail scanner endpoint (`GET /api/ideas/scan`)
- [ ] Input source toggle in frontend (manual ↔ Gmail scan mode)

**Later**
- [ ] Inline edit before publish
- [ ] Export interaction log as image
- [ ] Scheduling (APScheduler)

---

## Contributing

The best contribution is a new agent. If you add a platform that isn't here — Reddit, YouTube descriptions, newsletter, Substack — open a PR.

---

## License

MIT — use it, fork it, build on it.

---

_Orchestra is a product of [Meridian Global](https://github.com/MeridianGlobal)._
