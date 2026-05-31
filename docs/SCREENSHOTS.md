# Screenshots to capture

Capture these on a **fake / anonymized deal** (no real founder name, no real
startup, no real client logo). Run the app locally with a throwaway tenant.

| File | Screen | What it must show | What to scrub |
|---|---|---|---|
| `01-verdict.png` | Screening result page | The colored verdict banner (SKIP / LOOK / PASS-ON), the two columns (reasons / red flags), and the 4-axis scoring bars + total /20. **This is the money shot.** | Fake startup name; no real founder/company; no real client accent color/logo if it identifies a network. |
| `02-dashboard.png` | Admin dashboard (`?admin=1`) | Budget consumed, cost-per-tool breakdown, verdict distribution, per-member activity. Signals ops maturity. | Real member names → replace with `Member A/B`; real € budget if confidential → blur or use demo values. |
| `03-login.png` _(optional)_ | Login screen | Clean multi-tenant entry (password identifies the network). | Remove any real client logo; use the generic project logo or a placeholder. |
| `04-memo.png` _(optional)_ | VC IC-memo / PDF export | The generated memo layout + reportlab PDF export. | Fake deal only. |

## How to capture cleanly

1. `cp .env.example .env`, set a throwaway `*_PASSWORD` and your API keys.
2. `make run` → http://localhost:8501
3. Analyze a **made-up** deck (e.g. a 3-slide dummy PDF) so nothing real leaks.
4. Take screenshots at a consistent width (~1280px) for a clean README grid.
5. Drop the PNGs in this `docs/` folder with the exact names above.

> The README references `docs/01-verdict.png` and `docs/02-dashboard.png`.
> Keep those two at minimum; the rest are optional.
