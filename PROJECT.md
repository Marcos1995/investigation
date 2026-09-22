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
- Test: abrir `index.html`
- Dev: `python -m http.server`

## Viaje
- 6 personas: 2 BCN, 2 FRA, 2 HAM · viernes 4 – martes 8 dic 2026 · 4 noches
- Ranking: Atenas, Varsovia, París, Londres, Lisboa, Madrid, Milán, Roma, Palma, Viena
- Lean kit (ver AGENTS.md)

## Qué hacer cuando piden actualizar precios
No preguntes. Repite este checklist, cambia lo que haya cambiado, deja lo que no, commit + push. Producto: `index.html` + este fichero. No subas `_*.py` ni probes.

1. **Mismo aeropuerto de destino** para BCN, FRA y HAM. El código IATA de la ciudad es el aeropuerto, no “la ciudad”:
   - Milán **MXP** (no LIN) · Roma **FCO** (no CIA) · París **CDG** (no ORY) · Londres **LHR** (no LGW/STN/LTN)
   - Atenas ATH, Lisboa LIS, Varsovia WAW, Palma PMI, Viena VIE, Madrid MAD
2. **Filtros de vuelo:** ida y vuelta, solo **directos**, 2 adultos, cabina ~8 kg, **tarde ida y tarde vuelta** (~15:00). Si no hay vuelta de tarde, la más tardía (no emparejar con las 06:00). La vuelta puede ser otra aerolínea. Entre BCN, FRA y HAM, si hay alternativa, la ida que **llegue** a una hora parecida y la vuelta que **salga** a una hora parecida. Si alinearlo cuesta más de ~30 € por persona, quédate con el más barato y dilo en `why`.
3. **Precio de vuelo:** el de **reserva** en Google Flights (opciones de proveedor), no el de la lista que luego sube. El más barato entre aerolínea / Booking / etc. si es realista (no un parse de 15 €).
4. **Maleta de cabina 8–10 kg** en el número. Low-cost que la cobran aparte — extra **por persona, ida+vuelta** (`BAG_RT` en `index.html`): Wizz 64, Ryanair/Vueling 56, easyJet 64, Eurowings/Condor 44, Iberia Básica 50. LH / TAP / BA / AF / Aegean / SKY / LOT / Austrian: ya va incluida.
5. **Dos asientos juntos** (cada origen viaja en pareja). Low-cost cobran reserva de asiento — extra **por persona, ida+vuelta** (`SEAT_RT`): Wizz/Ryanair/Eurowings 18, easyJet/Vueling/Condor 16, Iberia 20. En LH/BA/AF/TAP/etc. se eligen juntos al check-in, 0.
6. **Airbnb:** 6 adultos, piso entero, 3 hab. + 2 baños, mapa del centro, 4–8 dic. Total de estancia (no precio/noche suelto). Si un mínimo es la mitad del resto del cluster (p. ej. Londres 786 vs 1434), usa el suelo del cluster.
7. **Hotel:** 3 habitaciones con baño × 4 noches = nightly × 12. Sin hostales. Se muestra al lado del Airbnb.
8. **Alojamiento en el ranking:** el **más barato** entre Airbnb y hotel. Varsovia y a veces Viena: hotel gana. El resto: Airbnb. El desglose por persona usa ese mínimo / 6, no el más caro.
9. **Comida:** 40 € × 4 días × 6 = 960 (el slider de la web).
10. **Total grupo** = 2×(BCN+FRA+HAM pp, ya con cabina y asientos) + min(Airbnb, hotel) + 960. Recalcula `rank` y el texto `why`.
11. **Hora** en el pie (es/en/de) y esta línea de ranking. Si una ciudad se dispara y hay otra con tarde desde los **tres** orígenes al **mismo** IATA y más barata, sustitúyela.

No olvidar ningún coste: ni vuelo, ni cabina, ni asientos juntos, ni el más barato entre Airbnb y hotel. Si no está en el checklist, no está en el número.

## Notas para el agente
-

