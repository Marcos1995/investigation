# Reglas de oro

Una sola lista. Los números están en `refresh_prices.py`. Si este texto y esas constantes no coinciden, mandan las constantes y se corrige este fichero en el mismo cambio. No se inventa un tercer criterio.

1. **Un programa.** `python3 refresh_prices.py`. No hay otro scraper ni scripts en `/tmp`.
2. **Antes de scrapear**, `--replay` imprime `REPLAY ok`. Si no, se para. **Después**, `--check` imprime `CHECK ok`.
3. **Mismo aeropuerto** para BCN, FRA y HAM: MXP, FCO, CDG, LHR, ATH, LIS, WAW, PMI, VIE, MAD.
4. **Vuelos.** Ida 2026-12-04, vuelta 2026-12-08, 2 adultos, EUR, solo directos. Tarde = salida ≥ 15:00. Si no hay vuelta de tarde, la más tardía. No se elige las 06:00 habiendo otra más tarde.
5. **Precio de vuelo.** El mínimo de `Book with` con importe ≥ 80. `p = (total + 1) // 2`. Si el botón esconde el precio, vale el total de esa pareja en la lista. No es precio «cheaper than usual» ni «is typical».
6. **Cabina y asientos** solo de la aerolínea de ida, ida y vuelta. Están en `BAG` y `SEAT` del programa (los mismos que `index.html`). Quien no esté ahí, extra 0. HOP se guarda como Air France. Dolomiti y Lufthansa City, como Lufthansa. Discover es Discover Airlines.
7. **Alinear** BCN, FRA y HAM es lo que hace `align()`: al mismo precio se puede acercar la hora; se pagan como mucho 30 € por persona solo si el barato queda a más de 120 minutos. Si cuesta más, se queda el barato y se dice en `why`.
8. **Airbnb.** Español, mapa del centro, 6 adultos, piso entero, 3 habitaciones, 3 camas, 2 baños, 4 noches. Nota ≥ 3/5; sin nota, fuera. Fechas parciales, fuera. Escalera de `price_max`: 500, 700, 950, 1300, 1800, 2600. Si el más barato es menor que 0,6 × el siguiente válido, se usa el siguiente. `stay` = ese total. `max` = `stay`.
9. **Hotel.** Entrar en booking.com antes de buscar. Inglés (`en-GB`). Nota ≥ 6/10. 3 habitaciones que duerman a 6. Fuera: hostel, dormitorio, guest house, apartamento entero, 3 individuales. A ≤ 2,2 millas; si no hay, ≤ 4. Precio = Current price, nunca el Original. Al hacer scroll se acumulan las tarjetas por nombre.
10. **Comida** 30 € × 4 × 6 = 720.
11. **Total del grupo** = 2 × (vuelo BCN + FRA + HAM, ya con cabina y asiento) + el más barato entre Airbnb y hotel + 720. El `rank` sale de ese total. Gana el alojamiento más barato de ese día, no el de la vez anterior.
12. **Si se rompe un selector**, se parchea solo la función que lee esa página y se anota en `MEMORY.md`. No se mueven estas reglas para encajar una ciudad.
