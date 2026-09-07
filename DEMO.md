# Demo — docubrain

## Status

No live-hosted demo yet (v0.1 is API-only, see ROADMAP.md P0 item). Try it locally — it's a 1-minute setup with zero API keys.

## What to try

```bash
git clone https://github.com/anejakartik/docubrain.git
cd docubrain
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 demo.py
```

This ingests a bundled 4-page synthetic contract (`sample_data/sample_contract.pdf`) and asks it 4 questions, printing each answer with its cited page number — entirely offline, no `OPENAI_API_KEY` needed.

## Try the API

```bash
uvicorn server.main:app --reload

# in another shell
curl -F "file=@sample_data/sample_contract.pdf" http://localhost:8000/ingest
curl -X POST http://localhost:8000/ask \
  -H "content-type: application/json" \
  -d '{"question": "Is there a cap on liability?", "top_k": 1}'
```

## Try it with your own PDF

Point `ingest_pdf()` (or the `/ingest` endpoint) at any PDF on disk — the demo dataset is just a stand-in.

## Local fallback / development

See the main [README.md](./README.md) quick-start — the "demo" and the "local dev setup" are the same thing for v0.1, since there's no separate hosted environment yet.
