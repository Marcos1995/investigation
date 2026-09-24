---
name: refresh-prices
description: Actualiza precios del viaje 4–8 dic 2026 (BCN, FRA, HAM) en index.html. Úsala cuando pidan actualizar, refrescar o revisar precios.
---

# Actualizar precios

Ejecuta `refresh_prices.py`. No reescribas el selector ni abras un script en `/tmp`.

1. Lee `SOUL.md` y `MEMORY.md`. Qué entra en el número está en `PROJECT.md`. Los umbrales están en el `.py`.
2. `python3 refresh_prices.py --replay` → tiene que salir `REPLAY ok`. Si no, paras. No toques `align` ni las constantes.
3. `python3 refresh_prices.py` escribe `index.html` y la línea de ranking. Chrome: `/usr/local/bin/google-chrome`. Si falta Playwright: `pip install playwright`.
4. `python3 refresh_prices.py --check` → `CHECK ok`. Abre `index.html` y confirma que el orden y el total del grupo coinciden.
5. Si una web cambia un botón o un texto, parchea solo esa función y anótalo en `MEMORY.md`.
6. Commit corto y push a `main`. No subas probes ni otro `.py`.
