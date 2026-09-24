---
name: refresh-prices
description: Actualiza precios del viaje 4–8 dic 2026 (BCN, FRA, HAM) en index.html. Úsala cuando pidan actualizar, refrescar o revisar precios. No está dormida.
---

# Actualizar precios

Esta skill se carga sola con ese pedido. No lleva `disable-model-invocation`. El criterio es `REGLAS.md`. No lo copies ni lo cambies aquí.

1. Lee `SOUL.md`, `MEMORY.md` y `REGLAS.md`.
2. `python3 refresh_prices.py --replay` → `REPLAY ok`. Si falla, paras. No toques `align` ni las constantes.
3. `python3 refresh_prices.py` escribe `index.html` y la línea de ranking de `PROJECT.md`. Chrome: `/usr/local/bin/google-chrome`. Si falta Playwright: `pip install playwright`.
4. `python3 refresh_prices.py --check` → `CHECK ok`. Abre la web (`python3 -m http.server`) y confirma orden, total del grupo y consola sin errores.
5. Si una web cambia un botón o un texto, parchea solo la función que lo lee y anótalo en `MEMORY.md`.
6. Commit corto y push a `main`. No subas probes ni otro `.py`.
