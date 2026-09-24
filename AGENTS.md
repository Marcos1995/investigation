<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Agent rules

Lean kit. No extra playbooks. Keep context small.

## Workflow

Think → Plan → Build → Review → Test.

1. Read `PROJECT.md`.
2. Search first; edit only what you need; verify with one check.
3. Telegram/headless: no questions; pick a reasonable option and continue.
4. Done = `git add -A` + short commit + push a `main`. No abras pull requests.
5. Final reply: max 5 lines. `HECHO`/`FALLO`.

`/review` loads `.cursor/skills/review` (esa skill duerme hasta `/review`). Actualizar precios carga ya `.cursor/skills/refresh-prices` (no duerme): `SOUL.md`, `MEMORY.md`, `REGLAS.md`, y ejecuta `refresh_prices.py`. No improvises el scrape. Keep context small.

Vista: HTML en el repo. Repo público: HECHO **siempre** con `https://<owner>.github.io/<repo>/` (la web en el navegador). `github.com` es el código. Nada de previews de terceros.

Kit synced by telegram-cursor-bot
