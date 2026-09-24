# Memory

Viaje fijo: 6 personas (2 BCN, 2 FRA, 2 HAM), viernes 4 – martes 8 dic 2026, 4 noches. El criterio de elección es `REGLAS.md`, no este fichero.

24 sep 2026: cada refresco reescribió un scraper y los precios cambiaron sin cambiar el viaje (precio Original en vez de Current, 3 individuales contadas como cama para 6, el scroll perdía la tarjeta barata, la lista de Google Flights en vez del botón de reserva). El programa que reproduce la página de ese día es `refresh_prices.py`. La prueba es `python3 refresh_prices.py --replay` con `fixtures/replay-2026-09-24`.

24 sep 2026 (revisión): `write_html` sustituía el primer `es: "…"` de cada ciudad, que es el nombre, no el `why`; en en/de metía notas en español y la fecha del pie no cambiaba de día. Ahora `render_html` es pura, toca solo `why: {…}`, traduce las notas (`NOTE`) y reescribe fecha y hora. `--replay` renderiza la página y falla si cambian los nombres. Nada del criterio se movió.

Verificar la web: `python3 -m http.server` + Playwright con `/usr/local/bin/google-chrome`. `google-chrome --headless --dump-dom` se cuelga con los tiles del mapa. Consola sin errores (el favicon va inline). Leaflet lleva SRI: si cambias de versión, recalcula los dos `integrity` o el mapa no carga.

Cuando un selector se rompa, la nota va aquí: fecha, qué texto cambió la web, qué función se tocó. No se anota un umbral nuevo.
