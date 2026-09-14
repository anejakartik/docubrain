# Deploy docubrain — server to Fly.io, domain via Vercel

> Outcome: `docubrain.kartikaneja.com` becomes a live, clickable demo.
> docubrain has no separate frontend — the FastAPI server renders its own
> landing/demo page at `/` — so the Vercel project here is a pure proxy: no
> build step, just a `vercel.json` rewrite that forwards every request to
> the Fly.io app. ~15 active minutes; longer if waiting on DNS + cert
> provisioning.

---

## Step 1 — Fly.io server (already done)

`docubrain-kartik.fly.dev` is deployed and healthy (`fly.toml` at repo root).

```bash
cd ~/github/docubrain
flyctl status -a docubrain-kartik   # confirm "started"
curl -I https://docubrain-kartik.fly.dev/   # expect HTTP/2 200
```

---

## Step 2 — Import to Vercel (proxy only, no build)

The repo root already has a `vercel.json`:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "https://docubrain-kartik.fly.dev/$1" }
  ]
}
```

1. Open https://vercel.com/new
2. Click "Import" next to `anejakartik/docubrain`
3. **Root Directory:** leave as repo root
4. **Framework Preset:** "Other" — there's no build step, `vercel.json` handles everything
5. Click **Deploy**

You'll get a `https://docubrain-<hash>.vercel.app` URL that transparently
proxies to the Fly.io app — visiting it should render the same demo page as
`docubrain-kartik.fly.dev`.

---

## Step 3 — Custom domain: docubrain.kartikaneja.com

In the Vercel project for `docubrain`:

1. **Settings → Domains → Add** → enter `docubrain.kartikaneja.com`
2. Vercel shows a DNS record to add at your registrar/DNS provider:
   - **Type:** CNAME
   - **Name:** `docubrain`
   - **Value:** `cname.vercel-dns.com`
3. Add that record (same place you added the `evalstack`/`tracelens` CNAMEs)
4. Back in Vercel, click "Refresh" — SSL cert auto-provisions once DNS propagates (1–30 min)

Verify:

```bash
curl -I https://docubrain.kartikaneja.com
# Expected: HTTP/2 200, x-vercel-id: ...
```

---

## Step 4 — Link from the portfolio + READMEs

After the domain is live:

1. **Update docubrain/README.md** — replace the `fly.dev` demo link with `https://docubrain.kartikaneja.com`
2. **Update portfolio-site** — add/update the "View live →" link on the docubrain project card
3. **LinkedIn** — swap the `fly.dev` link in the drafted post (`profile/linkedin-post-2026-09-14-docubrain-buildlog.md`) for the custom domain, if it goes live before posting

---

## Cost expectations

Same as evalstack/tracelens: Fly.io free tier + Vercel Hobby free tier = $0/mo.

---

## Troubleshooting

**Vercel shows a 404 or doesn't proxy**: confirm `vercel.json` is at the repo root and the Vercel project's Root Directory is the repo root.

**Fly server returns 502**: machine cold-starting after idle auto-stop (docubrain's `fly.toml` has `min_machines_running = 0`). First request takes 1–3s. To keep it warm, set `min_machines_running = 1` and redeploy — not worth it for a low-traffic portfolio demo.

**Custom domain stuck at "Invalid Configuration"**: DNS hasn't propagated. `dig docubrain.kartikaneja.com CNAME +short` should return `cname.vercel-dns.com`.
