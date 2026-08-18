<!-- managed-by-telegram-cursor-bot:agent-kit -->
# Contexto del proyecto

## Produccion
- URL: repo local / GitHub (investigacion, no hay deploy)
- Deploy: ninguno

## Stack
- Python stdlib (`score.py` → API publica GoPlus, sin deps)
- Nota de investigacion: `HALLAZGOS.md`

## Comandos utiles
- Instalar: nada (`python` 3)
- Test: `python score.py --check`
- Dev: `python score.py 1 0xdac17f958d2ee523a2206206994597c13d831ec7`

## Notas para el agente
- Esto es una investigacion, no un bot de trading ni un clon de TokenFomo
- No anadir dashboard, alertas, ni dependencias
- Ponytail siempre activo (ver AGENTS.md)
- Cosas que NO tocar: no convertir esto en sniper/listing-bot
