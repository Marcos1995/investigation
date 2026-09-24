<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: https://github.com/Marcos1995/investigation
- Vista: https://marcos1995.github.io/investigation/ (Chrome)
- Vista local: `index.html`

## Stack
- HTML + CSS + JS en un solo `index.html`

## Comandos utiles
- Instalar: no
- Test: `python3 refresh_prices.py --replay` → `REPLAY ok` y `python3 refresh_prices.py --check` → `CHECK ok`
- Dev: `python3 -m http.server` y abre `http://localhost:8000/`

## Viaje
- 6 personas: 2 BCN, 2 FRA, 2 HAM · viernes 4 – martes 8 dic 2026 · 4 noches
- Ranking: Atenas, París, Roma, Milán, Lisboa, Palma, Varsovia, Madrid, Londres, Viena
- Lean kit (ver AGENTS.md)

## Qué hacer cuando piden actualizar precios
No preguntes. Las reglas de oro están solo en `REGLAS.md`. Soul en `SOUL.md`, memoria en `MEMORY.md`, skill `.cursor/skills/refresh-prices` (no duerme). Ejecuta `refresh_prices.py`. No abras otro scraper. Producto: `index.html` + la línea de ranking de este fichero. Commit + push.

## Notas para el agente
- Hechos y fallos ya vistos: `MEMORY.md`. No los copies aquí.

