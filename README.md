# Orchestra

**Multi-agent content system for creators who publish across platforms.**

Orchestra takes a single idea and runs it through a coordinated team of AI agents — a planner, three platform writers, and a brand critic — each with a distinct voice and job. The result is platform-native content for Instagram, Threads, and LinkedIn, along with a visible log of how the agents collaborated to get there.

Built by [Meridian Global](https://github.com/MeridianGlobal).

---

## What it does

You type one idea. Orchestra handles the rest:

1. **Planner agent** reads your idea and your voice profile, then produces a structured brief — tone, audience, core angle, per-platform notes
2. **Platform agents** (Instagram, Threads, LinkedIn) each write natively for their medium, reading each other's output and reacting before finalizing
3. **Critic agent** reviews all three drafts against your brand voice and flags anything off
4. **You** review, edit inline, and publish — or export the interaction log as a shareable card sequence

---

## Why it's different

Most "AI content tools" call the same model three times with different format instructions. Orchestra doesn't do that.

The system is built around a **Brief object** — a structured JSON that the Planner produces and every downstream agent reads from. Agents don't just see the original prompt; they see what other agents wrote and react to it. The Critic reads all three drafts simultaneously.

This makes the outputs genuinely different from each other, and the interaction log genuinely interesting to read.

---

## Demo

> GIF coming on launch day — [watch this repo](https://github.com/MeridianGlobal/orchestra)

---

## Project structure

```
orchestra/
├── backend/
│   ├── agents/          # One file per agent — easy to extend
│   │   ├── base.py
│   │   ├── planner.py
│   │   ├── instagram.py
│   │   ├── threads.py
│   │   ├── linkedin.py
│   │   └── critic.py
│   ├── core/
│   │   ├── brief.py         # The Brief dataclass — system spine
│   │   ├── orchestrator.py  # Pipeline runner
│   │   └── voice_store.py   # Load/save brand voice YAML
│   ├── api/
│   │   └── routes.py        # FastAPI + SSE streaming endpoint
│   ├── db/
│   │   └── models.py        # SQLite via SQLModel
│   └── voice/
│       └── default.yaml     # Your brand voice — edit this first
├── frontend/
│   ├── app/                 # Next.js 14 app router
│   └── components/
│       ├── AgentCard.tsx    # Streaming agent output card
│       ├── BriefPanel.tsx   # Planner output display
│       └── ExportButton.tsx # Export interaction log as image
├── examples/
│   └── run_cli.py           # Run the full pipeline in terminal
└── docs/
    └── adding-an-agent.md   # How to add a new platform in 30 min
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
cp .env.example .env        # add your ANTHROPIC_API_KEY

# Edit your voice profile (do this before anything else)
nano backend/voice/default.yaml

# Run CLI demo
python examples/run_cli.py "your idea here"

# Start API server
uvicorn orchestra.backend.main:app --reload

# Stream the pipeline via API (separate terminal)
curl -N -X POST http://localhost:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"idea": "your idea here"}'

# Frontend (separate terminal)
cd frontend
npm install && npm run dev
```

Open [localhost:3000](http://localhost:3000).

---

## Your brand voice

The `backend/voice/default.yaml` file is where Orchestra learns who you are. Edit it before your first run:

```yaml
creator:
  name: "Your name"
  archetype: "How you'd describe yourself in one line"

voice:
  adjectives: ["direct", "grounded", "specific"]
  not: ["corporate", "hustle-bro", "preachy"]

signature_moves:
  - "Specific detail over general claim"
  - "End with a question, not a lesson"

content_rules:
  max_emojis: 2
  hashtag_style: "3-5 specific, never generic"
  cta_style: "implicit"
```

The Planner agent reads this on every run. The Critic uses it to flag off-brand language. The more specific you make it, the better the output.

---

## Adding a new platform agent

See [`docs/adding-an-agent.md`](docs/adding-an-agent.md) for the full walkthrough. The short version:

1. Create `backend/agents/your_platform.py`
2. Subclass `BaseAgent`, implement `build_prompt()`
3. Register in `orchestrator.py`

That's it. One file, three methods, no framework to learn.

---

## Tech stack

| Layer | Choice |
|---|---|
| LLM | Claude (Anthropic) |
| Backend | Python + FastAPI |
| Streaming | Server-Sent Events |
| Frontend | Next.js 14 + Tailwind |
| Storage | SQLite via SQLModel |
| Voice config | YAML |

No LangChain. No vector databases. No external queue. Runs entirely local except for the API call.

---

## Roadmap

- [x] Core pipeline (planner → agents → critic)
- [x] Brand voice YAML
- [x] FastAPI + SSE streaming
- [ ] Next.js frontend with streaming cards
- [ ] Inline edit before publish
- [ ] Export interaction log as image
- [ ] Optional scheduling (APScheduler)
- [ ] Platform publishing via APIs (Instagram Graph, LinkedIn API)

---

## Contributing

The best contribution is a new agent. If you add a platform that isn't here — Reddit, YouTube description, newsletter, Substack — open a PR. See [`docs/adding-an-agent.md`](docs/adding-an-agent.md).

---

## License

MIT — use it, fork it, build on it.

---

*Orchestra is a product of [Meridian Global](https://github.com/MeridianGlobal).*
