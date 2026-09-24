---
name: review
description: Review git diff for correctness, tests, secrets, and waste. Fix critical issues only.
disable-model-invocation: true
---

# Review

Review the current git diff against the default branch. Do not re-read the whole repo.

## Check

- Correctness vs the request; edge cases; error handling
- Precios: el cambio respeta `REGLAS.md`; si toca una constante de `refresh_prices.py`, `REGLAS.md` cambia en el mismo commit
- Self-check: `python3 refresh_prices.py --replay` → `REPLAY ok` y `--check` → `CHECK ok`; `index.html` abre sin errores de consola
- No secrets, injection, auth bypass, or unsafe eval
- No dead code, speculative features, duplicate helpers, probes or a second scraper in the repo

## Do

1. Look at `git diff` / `git log` for the change set only
2. Fix Critical issues in place
3. Do not expand scope
4. Reply max 5 lines: `HECHO` or `FALLO` + what you found/fixed
