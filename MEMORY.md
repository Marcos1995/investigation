# Memory

Viaje fijo: 6 personas (2 BCN, 2 FRA, 2 HAM), viernes 4 – martes 8 dic 2026, 4 noches. Destinos e IATA en `PROJECT.md` (MXP, FCO, CDG, LHR). Comida 30 € por persona y día (720 en el grupo).

Vuelos: Google Flights, directos, tarde (salida ≥ 15:00). Precio = mínimo de `Book with` ≥ 80 €, mitad half-up `(total + 1) // 2`, más cabina y asiento de la ida. Si el botón esconde el precio (Wizz), vale el total de esa pareja en la lista. Ignorar «cheaper than usual». Alinear BCN/FRA/HAM solo como hace `align()`: mismo precio siempre; pagar hasta 30 € solo si el barato queda a más de 120 minutos.

Airbnb en español, nota ≥ 3/5 (sin nota, fuera). El más barato por debajo de 0,6 × el siguiente válido se descarta. Booking en inglés (`en-GB`): si no, el parser no ve «Scored» ni «Current price». Nota ≥ 6/10, 3 habitaciones que duerman a 6, precio = Current price (nunca el Original). 3 individuales no cuentan. Al hacer scroll se acumulan tarjetas por nombre.

24 sep 2026: cada refresco reescribió un scraper en `/tmp` y los precios se movieron (precio original, habitación individual, tarjeta perdida al scroll, lista en vez de reserva). El programa que reproduce esa página es `refresh_prices.py`. La prueba es `python3 refresh_prices.py --replay` contra `fixtures/replay-2026-09-24`. Quien gana entre hotel y Airbnb es el más barato de ese día, no el de la vez anterior.
