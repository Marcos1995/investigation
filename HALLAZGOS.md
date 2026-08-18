# Tokens recien creados vs listing de prestigio

Pregunta: (1) se puede filtrar un token recien creado para que no sea fraude y aun asi triunfe; (2) se puede anticipar el listing en CoinMarketCap / CoinGecko y coger la subida.

Respuesta corta: (1) filtros de higiene si, prediccion de exito no. (2) el listing en CMC ya no es un evento raro; no hay cola publica que anticipar.

## 1. Token recien creado + filtros

El experimento TokenFomo ya era esta idea. El mercado empeoro.

- Solidus Labs (Pump.fun, ene 2024–mar 2025): ~7M tokens con trades; ~98.6% acaban con liquidez < $1k (rug / pump-and-dump). ~1.4% sobreviven.
- CoinGecko (18.7M tokens Pump.fun hasta jun 2026): 80% muertos en 24 h; 4.55% viven 90+ dias.
- Raydium: ~93% de pools con senales de “soft rug” (drenar LP poco a poco).

Filtros que SI existen (gratis, sin construir un scanner):

| Senal | Por que | Herramienta |
| --- | --- | --- |
| honeypot / no se puede vender | el dinero queda atrapado | GoPlus, honeypot.is, TokenSniffer (EVM) |
| mint / freeze / owner no renunciado | el deployer fabrica o congela | GoPlus (EVM), RugCheck (Solana) |
| LP sin lock / sin burn | pueden vaciar el pool | RugCheck, DexScreener |
| sell tax alto / tax modificable | impuesto o trampa diferida | GoPlus |
| holder/creator concentrado | un wallet tumba el precio | GoPlus holders, DexScreener |
| contrato igual a scams conocidos | copia-pega | TokenSniffer |

Techo: estos filtros quitan rugs amateur. No eligen ganadores. Rugs “profesionales” (honeypot diferido, drenaje lento, influs pagados) pasan el scan. Miles de bots ya corren exactamente esto; el resto es latencia, no una lista de reglas.

`score.py` aplica solo la higiene EVM via GoPlus. PASS = “no es trampa obvia”, no “va a subir”.

## 2. Listing en paginas de prestigio

La tesis vieja (“entra en CMC → retail FOMO → x10”) murio cuando CMC Dexscan empezo a indexar automatico 52M+ contratos. Salir en CMC/Dexscan no es un sello; es un feed on-chain.

Lo que todavia se “lista de verdad”:

- Pagina tracked/ranked en CMC o CoinGecko (revision humana, 7–30 dias, volumen organico, web, supply).
- Listing CEX (Binance, Coinbase, Upbit). Ahi si hay impacto de precio.

Por que no se anticipa con ventaja:

- No hay API de “cola de aprobacion”. El formulario es privado.
- El proyecto suele tuitear “hemos aplicado”; ese tweet ya lo leen bots.
- CoinGecko `/coins/list/new` (pago) avisa cuando YA esta listado, no antes.
- CMC tarda semanas: el mercado descuenta el anuncio, no el dia D.
- CMC ha listado scams; el logo no es garantia.

El analogo moderno de “a punto de publicarse” es la graduacion Pump.fun → Raydium. Es el trade mas saturado de Solana. CMC hasta publica tutoriales de bots de graduacion.

## 3. Que no construir

No clonar TokenFomo. No bot de listings. No dashboard. Cero edge propio: los datos son publicos y el fracaso base es ~98%.

Si se apuesta igual, a mano: pasar el contrato por `score.py`, exigir LP locked/burned y que el token ya lleve dias (no minutos). Seguir siendo mayoria perdedora.
