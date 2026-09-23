---
name: refresh-prices
description: Actualiza precios del viaje 4–8 dic 2026 (BCN, FRA, HAM) en index.html. Úsala cuando pidan actualizar, refrescar o revisar precios.
---

# Actualizar precios

No preguntes. Reglas de negocio en `PROJECT.md` (sección «Qué hacer cuando piden actualizar precios»). Este fichero es el cómo. Producto: `index.html` + la línea de ranking de `PROJECT.md`. No subas `_*.py` ni probes: scripts en `/tmp`.

Chrome del sistema: `/usr/local/bin/google-chrome`. Playwright ya suele estar. Si no: `pip install playwright`.

## 1. Vuelos (Google Flights)

Ida 2026-12-04, vuelta 2026-12-08, 2 adultos, EUR, solo directos. Destinos: ATH, WAW, CDG, LHR, LIS, MAD, MXP, FCO, PMI, VIE. Orígenes: BCN, FRA, HAM.

URL: el `gf()` de `index.html` **sin** aerolínea (campo 6). Así salen todas. Filtro Nonstop en la UI: botón Stops → «Nonstop only». Si el overlay tapa el click, haz click por JS. Pulsa «View more flights» en la ida y otra vez en la lista de vueltas.

Cada tarjeta tiene `aria-label` con `From N euros round trip total` (N es **los 2 adultos**), aerolínea, salida, llegada y duración. Tarde = salida ≥ 15:00. Si esa ida no tiene vuelta ≥ 15:00, la vuelta más tardía. No elijas las 06:00 si hay una más tarde.

**Precio que se guarda:** el botón de reserva, no el de la lista. Abre la ida, luego la vuelta, espera a `Book with`.

```
Book with Aegean
€288
```

`p` = mitad del **mínimo** de esas líneas `Book with …\n€N` con N ≥ 80, redondeo half-up: `(total + 1) // 2`. Es por persona, antes de cabina y asiento. El texto «€97 cheaper than usual» no es un precio. Si el panel dice «Finding the cheapest booking options», espera; no leas antes.

Solo reserva el elegido y la alternativa que esté a menos de ~40 €/persona. El resto, déjalo.

Cabina y asientos: `flyP` ya suma `BAG_RT` + `SEAT_RT` de la aerolínea de **ida**. Compara el alineado con ese total, no con la tarifa pelada. Si acercar la llegada (o la salida de la vuelta) entre BCN, FRA y HAM cuesta ≤ ~30 €/persona, cámbialo y dilo en `why`. Si cuesta más, quédate con el barato y dilo.

Aerolínea nueva: añádela a `AIR` (Discover = `4Y`). Lufthansa City, HOP y Air Dolomiti se guardan como Lufthansa o Air France. IATA de ciudad = el de `PROJECT.md` (MXP, FCO, CDG, LHR).

## 2. Airbnb

Mapa `q.bb`, 6 adultos, piso entero, 3 dormitorios, 3 camas, 2 baños, 4–8 dic, EUR. Sube `price_max` en escalera (500, 700, 950, 1300, 1800, 2600) hasta tener varios totales.

Descarta tarjetas con fechas parciales (`Del 4 al 6 dic`, `6–8 dic`): no cubren las 4 noches. El número es el de la ficha, «N € en total» con 6 viajeros y 4 noches, no un precio de tarjeta que no coincida.

Si el más barato es &lt; 0,6 × el **siguiente** válido (Londres 786 vs 1434), usa el suelo del cluster. Compara con el siguiente, no con la mediana de toda la página.

`stay` = ese total. `max` = `stay` (el enlace de la web filtra por ahí).

## 3. Hotel

Entra en `booking.com` antes de la búsqueda (si no, 502). 6 adultos, 3 habitaciones, 4–8 dic, EUR, orden por precio. Quédate con tarjetas `3×` habitación, baño privado, a ≤ 2,2 millas del centro (si no hay, ≤ 4). Fuera: dormitorio, hostel, baño compartido, guest house, apartamento entero.

El total de la tarjeta («Current price» o «Price», 4 noches y 6 adultos) ya es el coste del grupo. `hotel` = el más barato de ese filtro.

## 4. Escribir y comprobar

`rank` según el total de grupo, no a mano:

`2 × (flyBCN + flyFRA + flyHAM) + min(stay, hotel) + 960`

`fly` = `p` + cabina + asientos de la ida. Actualiza `why` en es/en/de y la hora del pie (Madrid, UTC+2 en septiembre) en los tres idiomas. Actualiza la línea de ranking de `PROJECT.md`.

Comprueba que el `rank` guardado coincide con ese total ordenado (un script en `/tmp`, no en el repo) y abre `index.html`: el `#list` debe mostrar el mismo orden y el total de los 6.

Commit corto + push. No incluyas probes.
