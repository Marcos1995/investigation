#!/usr/bin/env python3
"""One price refresh. Rules live here as constants. Do not add another scraper.

  python3 refresh_prices.py --replay    # must print REPLAY ok before any scrape
  python3 refresh_prices.py --check     # ranks and filters already in index.html
  python3 refresh_prices.py             # scrape and write index.html + PROJECT.md
"""
import base64, json, re, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
PROJECT = ROOT / "PROJECT.md"

# Frozen. Change only when the user changes the trip rules, then REGLAS.md in the same commit.
FOOD_DAY = 30
NIGHTS = 4
PAX = 6
FOOD_GROUP = FOOD_DAY * NIGHTS * PAX  # 720
ALIGN_EUR = 30          # max extra €/person to pull times together
PAY_GAP = 120           # minutes; pay that extra only if the cheap option is farther than this
EXPAND_EUR = 40         # €/person window of outbound cards to open
BOOK_FLOOR = 80         # ignore fake book prices below this
CLUSTER = 0.6           # cheapest < 0.6 × next → use the next
MILES_NEAR = 2.2
MILES_FAR = 4.0
MIN_AIRBNB = 3.0        # out of 5; missing rating is out
MIN_BOOKING = 6.0       # out of 10
AFTERNOON = 15 * 60
PRICE_STEPS = [500, 700, 950, 1300, 1800, 2600]
OUT_IN, OUT_OUT = "2026-12-04", "2026-12-08"
ORIGINS = ["BCN", "FRA", "HAM"]
DESTS = ["ATH", "WAW", "CDG", "LHR", "LIS", "MAD", "MXP", "FCO", "PMI", "VIE"]

BAG = {"Wizz Air": 64, "Ryanair": 56, "easyJet": 64, "Vueling": 56, "Eurowings": 44, "Iberia": 50, "Condor": 44}
SEAT = {"Wizz Air": 18, "Ryanair": 18, "easyJet": 16, "Vueling": 16, "Eurowings": 18, "Iberia": 20, "Condor": 16}

CITIES = [
    ("ATH", "Athens--Greece", "Athens", "-814876", [37.958, 23.705, 38.000, 23.755]),
    ("WAW", "Warsaw--Poland", "Warsaw", "-534433", [52.215, 20.970, 52.265, 21.055]),
    ("CDG", "Paris--France", "Paris", "-1456928", [48.830, 2.265, 48.895, 2.410]),
    ("LHR", "London--United-Kingdom", "London", "-2601889", [51.480, -0.195, 51.545, -0.055]),
    ("LIS", "Lisbon--Portugal", "Lisbon", "-2167973", [38.705, -9.170, 38.745, -9.130]),
    ("MAD", "Madrid--Spain", "Madrid", "-390625", [40.400, -3.725, 40.440, -3.680]),
    ("MXP", "Milan--Italy", "Milan", "-121726", [45.445, 9.155, 45.495, 9.230]),
    ("FCO", "Rome--Italy", "Rome", "-126693", [41.860, 12.445, 41.925, 12.535]),
    ("PMI", "Palma-de-Mallorca--Spain", "Palma de Mallorca", "-395224", [39.562, 2.625, 39.585, 2.668]),
    ("VIE", "Vienna--Austria", "Vienna", "-1995499", [48.185, 16.335, 48.235, 16.410]),
]
NAMES = {
    "ATH": "Atenas", "PMI": "Palma", "CDG": "París", "FCO": "Roma", "MXP": "Milán",
    "LIS": "Lisboa", "WAW": "Varsovia", "MAD": "Madrid", "LHR": "Londres", "VIE": "Viena",
}

def extras(air):
    return BAG.get(air, 0) + SEAT.get(air, 0)

def mins(hhmm):
    h, m = hhmm.split(":")
    return int(h) * 60 + int(m)

def half_up(total):
    return (total + 1) // 2

def norm(a):
    al = a.lower()
    if "hop" in al or "air france" in al:
        return "Air France"
    if "dolomiti" in al or "lufthansa" in al:
        return "Lufthansa"
    if "discover" in al:
        return "Discover Airlines"
    if "british" in al:
        return "British Airways"
    if "wizz" in al:
        return "Wizz Air"
    if "sky" in al:
        return "SKY express"
    if "vueling" in al:
        return "Vueling"
    if "ryan" in al:
        return "Ryanair"
    if "easy" in al:
        return "easyJet"
    if "eurowing" in al:
        return "Eurowings"
    if "iberia" in al:
        return "Iberia"
    if "tap" in al:
        return "TAP"
    if "aegean" in al:
        return "Aegean"
    if "austrian" in al:
        return "Austrian"
    if al.startswith("lot") or "lot " in al or "polish" in al:
        return "LOT"
    if re.search(r"\bita\b|ita airways", al):
        return "ITA"
    if "condor" in al:
        return "Condor"
    if "europa" in al:
        return "Air Europa"
    return a.strip()

def uvar(n):
    o = []
    while n > 127:
        o.append((n & 127) | 128)
        n //= 128
    o.append(n)
    return o

def fvar(f, n):
    return uvar((f << 3) | 0) + uvar(n)

def fbytes(f, arr):
    return uvar((f << 3) | 2) + uvar(len(arr)) + arr

def fstr(f, s):
    return fbytes(f, list(s.encode()))

def gf(frm, to):
    """Google Flights URL, all airlines, same proto as index.html without field 6."""
    place = lambda c: fvar(1, 1) + fstr(2, c)
    def leg(date, a, b):
        return fstr(2, date) + fvar(5, 0) + fbytes(13, place(a)) + fbytes(14, place(b))
    msg = fvar(1, 28) + fvar(2, 2)
    msg += fbytes(3, leg(OUT_IN, frm, to)) + fbytes(3, leg(OUT_OUT, to, frm))
    msg += fvar(8, 1) + fvar(8, 1) + fvar(9, 1)
    msg += fbytes(13, fvar(2, 2) + fvar(3, 0)) + fvar(14, 1) + fvar(19, 1)
    tfs = base64.b64encode(bytes(msg)).decode().replace("+", "-").replace("/", "_").rstrip("=")
    return "https://www.google.com/travel/flights/search?tfs=" + tfs + "&hl=en&curr=EUR"

def to24(s):
    m = re.match(r"(\d{1,2}):(\d{2})\s*([AP]M)", s.strip(), re.I)
    h, mi, ap = int(m.group(1)), m.group(2), m.group(3).upper()
    if ap == "PM" and h != 12:
        h += 12
    if ap == "AM" and h == 12:
        h = 0
    return f"{h:02d}:{mi}"

def dur_fmt(s):
    h = re.search(r"(\d+)\s*hr", s or "")
    m = re.search(r"(\d+)\s*min", s or "")
    return f"{int(h.group(1)) if h else 0}h {int(m.group(1)) if m else 0:02d}m"

def parse_card(t):
    if not t.startswith("From ") or "Nonstop" not in t:
        return None
    pm = re.search(r"From ([\d,]+) euros", t)
    am = re.search(r"with (.+?)\. Leaves", t)
    tm = re.search(r"Leaves .+? at (\d{1,2}:\d{2}\s*[AP]M).*?arrives at .+? at (\d{1,2}:\d{2}\s*[AP]M)", t)
    dm = re.search(r"Total duration ([^.]+)\.", t)
    if not (pm and am and tm):
        return None
    return {
        "price": int(pm.group(1).replace(",", "")),
        "air": am.group(1).strip(),
        "dep": to24(tm.group(1)),
        "arr": to24(tm.group(2)),
        "dur": dur_fmt(dm.group(1)) if dm else "",
        "label": t[:500],
    }

def best_returns(returns):
    """Afternoon return if one exists, else the latest. Keep same-price and +≤30 €/pp alternatives."""
    if not returns:
        return []
    aft = [r for r in returns if mins(r["dep"]) >= AFTERNOON]
    if aft:
        best = min(aft, key=lambda r: (r["price"], r["dep"]))
        pool = [r for r in aft if r["price"] <= best["price"] + ALIGN_EUR * 2]
    else:
        best = max(returns, key=lambda r: (mins(r["dep"]), -r["price"]))
        pool = [best]
    seen, out = set(), []
    for r in pool:
        k = (r["dep"], norm(r["air"]), r["price"])
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out

def combos(expanded):
    out = []
    for e in expanded:
        air = norm(e["out"]["air"])
        for r in best_returns(e["returns"]):
            p = half_up(r["price"])
            out.append({
                "air": air, "dep": e["out"]["dep"], "arr": e["out"]["arr"], "dur": e["out"]["dur"],
                "back_air": norm(r["air"]), "back_dep": r["dep"], "back_arr": r["arr"], "back_dur": r["dur"],
                "list": r["price"], "p": p, "fly": p + extras(air),
                "out_label": e["out"].get("label", ""), "ret_label": r.get("label", ""),
            })
    return out

def clock(a, b):
    d = abs(mins(a) - mins(b))
    return min(d, 24 * 60 - d)

def spread(c, others, field=None):
    """Sum of clock gaps to each other origin. field is arr or back_dep; both if omitted."""
    fields = ("arr", "back_dep") if field is None else (field,)
    return sum(clock(c[f], o[f]) for o in others for f in fields)

def align(by_orig):
    """Cheapest fly, then same-price closer times, then pay ≤ ALIGN_EUR only if that cheap option sits more than PAY_GAP minutes off.

    Same price always may move (closer spread, then earlier departure). A dearer option is eligible only when it
    improves a dimension that is already farther than PAY_GAP. If that gap closes because another origin moved,
    the extra is dropped. This is the rule that reproduced the 24 Sep 2026 page; do not tune it per city.
    """
    chosen = {}
    for o in ORIGINS:
        opts = by_orig.get(o) or []
        chosen[o] = min(opts, key=lambda c: (c["fly"], c["dep"], c["back_dep"])) if opts else None
    start = dict(chosen)
    seen = set()
    notes = []
    for _ in range(8):
        have = [o for o in ORIGINS if chosen.get(o)]
        if len(have) < 2:
            break
        state = tuple((o, chosen[o]["dep"], chosen[o]["back_dep"], chosen[o]["fly"]) for o in have)
        if state in seen:
            break
        seen.add(state)
        changed = False
        for o in have:
            others = [chosen[x] for x in have if x != o]
            opts = by_orig[o]
            base = min(opts, key=lambda c: (c["fly"], c["dep"], c["back_dep"]))
            arr_s = spread(base, others, "arr")
            ret_s = spread(base, others, "back_dep")

            def eligible(c, arr_s=arr_s, ret_s=ret_s, others=others, base=base):
                extra = c["fly"] - base["fly"]
                if extra < 0 or extra > ALIGN_EUR:
                    return False
                if extra == 0:
                    return True
                if arr_s > PAY_GAP and spread(c, others, "arr") < arr_s:
                    return True
                if ret_s > PAY_GAP and spread(c, others, "back_dep") < ret_s:
                    return True
                return False

            best = min((c for c in opts if eligible(c)), key=lambda c: (spread(c, others), c["fly"], c["dep"], c["back_dep"]))
            cur = chosen[o]
            if (best["dep"], best["back_dep"], best["air"], best["fly"]) != (cur["dep"], cur["back_dep"], cur["air"], cur["fly"]):
                chosen[o] = best
                changed = True
        if not changed:
            break
    for o in ORIGINS:
        cur, base = chosen.get(o), start.get(o)
        opts = by_orig.get(o) or []
        if not cur:
            notes.append(f"{o}: sin vuelo de tarde")
            continue
        if (cur["dep"], cur["back_dep"], cur["air"]) != (base["dep"], base["back_dep"], base["air"]):
            notes.append(f"{o} alinea {base['dep']}→{cur['dep']} vuelta {base['back_dep']}→{cur['back_dep']} +{cur['fly'] - base['fly']} €")
            continue
        others = [chosen[x] for x in ORIGINS if x != o and chosen.get(x)]
        if not others:
            continue
        arr_s = spread(base, others, "arr")
        ret_s = spread(base, others, "back_dep")
        jumps = []
        for c in opts:
            extra = c["fly"] - base["fly"]
            if extra <= ALIGN_EUR:
                continue
            if (arr_s > PAY_GAP and spread(c, others, "arr") < arr_s) or (ret_s > PAY_GAP and spread(c, others, "back_dep") < ret_s):
                jumps.append(extra)
        if jumps:
            notes.append(f"{o} se queda en {base['dep']} (acercarlo pasa de +{min(jumps)} €)")
    return chosen, notes

def apply_book(opts, booked, orig, dest):
    """Replace list p with the booked total when we have one. Hidden button keeps the list total."""
    for o in opts:
        key = f"{orig}-{dest}-{o['dep']}-{o['back_dep']}"
        hit = booked.get(key)
        if not hit:
            continue
        if hit.get("total"):
            o["p"] = half_up(hit["total"])
            o["book"] = hit["total"]
        else:
            o["p"] = half_up(o["list"])
            o["book"] = None
            o["hidden"] = True
        o["fly"] = o["p"] + extras(o["air"])
    return opts

def rank_rows(flights, stays):
    rows = []
    for cid in DESTS:
        flys = {o: flights[cid][o]["p"] + extras(flights[cid][o]["air"]) for o in ORIGINS}
        bed = min(stays[cid]["stay"], stays[cid]["hotel"])
        group = 2 * sum(flys.values()) + bed + FOOD_GROUP
        rows.append((group, cid, flys, bed))
    rows.sort()
    return rows

# --- scrape (only this file talks to the sites) ---

def grab(page):
    raw = page.evaluate("""() => [...document.querySelectorAll('[aria-label]')]
        .map(e => e.getAttribute('aria-label') || '')
        .filter(t => t.startsWith('From ') && t.includes('round trip'))""")
    seen, out = set(), []
    for t in raw:
        if t in seen:
            continue
        seen.add(t)
        c = parse_card(t)
        if c:
            out.append(c)
    return out

def click_more(page):
    for _ in range(4):
        btn = page.get_by_role("button", name=re.compile(r"View more", re.I))
        if btn.count() == 0:
            break
        try:
            btn.first.click(timeout=2000)
            page.wait_for_timeout(900)
        except Exception:
            break

def click_label(page, label):
    return page.evaluate("""(label) => {
      const el = [...document.querySelectorAll('[aria-label]')].find(e => {
        const t = e.getAttribute('aria-label') || '';
        return t.startsWith('From ') && t.startsWith(label.slice(0, 160));
      });
      if (!el) return 'missing';
      const btn = [...el.querySelectorAll('button')].find(b => /select flight/i.test((b.innerText||'')+(b.getAttribute('aria-label')||''))) || el.querySelector('button');
      (btn || el).click();
      return 'ok';
    }""", label)

def book_totals(page):
    for _ in range(16):
        text = page.inner_text("body")
        if "Finding the cheapest" in text:
            page.wait_for_timeout(800)
            continue
        if "Book with" in text:
            break
        page.wait_for_timeout(500)
    else:
        return []
    lines = [ln.strip() for ln in page.inner_text("body").splitlines() if ln.strip()]
    prices = []
    for i, ln in enumerate(lines):
        if not ln.startswith("Book with"):
            continue
        for nxt in lines[i + 1:i + 6]:
            if nxt.startswith("Book with") or "typical" in nxt.lower() or "cheaper" in nxt.lower():
                break
            m = re.search(r"€\s*([\d,]+)", nxt)
            if m:
                n = int(m.group(1).replace(",", ""))
                if n >= BOOK_FLOOR:
                    prices.append(n)
                break
    return prices

def scrape_flights(cache):
    from playwright.sync_api import sync_playwright
    data = {}
    path = cache / "flights.json"
    if path.exists():
        data = json.loads(path.read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/local/bin/google-chrome", headless=False,
                                     args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_context(locale="en-GB", viewport={"width": 1400, "height": 1000}).new_page()
        first = True
        for dest in DESTS:
            for orig in ORIGINS:
                key = f"{orig}-{dest}"
                if data.get(key, {}).get("expanded"):
                    continue
                url = gf(orig, dest)
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(2500)
                if first and page.locator("button:has-text('Accept all')").count():
                    page.locator("button:has-text('Accept all')").first.click()
                    first = False
                click_more(page)
                outs = [c for c in grab(page) if mins(c["dep"]) >= AFTERNOON] or grab(page)
                outs.sort(key=lambda c: half_up(c["price"]) + extras(norm(c["air"])))
                if not outs:
                    data[key] = {"expanded": []}
                    continue
                best = half_up(outs[0]["price"]) + extras(norm(outs[0]["air"]))
                pool = [c for c in outs if half_up(c["price"]) + extras(norm(c["air"])) <= best + EXPAND_EUR][:4]
                expanded = []
                for cand in pool:
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(1800)
                    click_more(page)
                    click_label(page, cand["label"])
                    page.wait_for_timeout(2200)
                    click_more(page)
                    cards = grab(page)
                    rets = [c for c in cards if "December 8" in c["label"]]
                    if not rets:
                        rets = [c for c in cards if not (c["dep"] == cand["dep"] and c["arr"] == cand["arr"] and norm(c["air"]) == norm(cand["air"]))]
                    expanded.append({"out": cand, "returns": rets})
                data[key] = {"expanded": expanded}
                path.write_text(json.dumps(data))
                print("flights", key, len(expanded), flush=True)
        browser.close()
    return data

def scrape_books(cache, chosen):
    from playwright.sync_api import sync_playwright
    path = cache / "booked.json"
    done = json.loads(path.read_text()) if path.exists() else {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/local/bin/google-chrome", headless=False,
                                     args=["--disable-blink-features=AutomationControlled"])
        page = browser.new_context(locale="en-GB", viewport={"width": 1400, "height": 1000}).new_page()
        first = True
        for dest, by in chosen.items():
            for orig, opt in by.items():
                items = opt if isinstance(opt, list) else [opt]
                for opt in items:
                    if not opt:
                        continue
                    key = f"{orig}-{dest}-{opt['dep']}-{opt['back_dep']}"
                    if key in done:
                        continue
                    url = gf(orig, dest)
                    page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    page.wait_for_timeout(2000)
                    if first and page.locator("button:has-text('Accept all')").count():
                        page.locator("button:has-text('Accept all')").first.click()
                        first = False
                    click_more(page)
                    c1 = click_label(page, opt["out_label"])
                    page.wait_for_timeout(2000)
                    click_more(page)
                    c2 = click_label(page, opt["ret_label"])
                    page.wait_for_timeout(2500)
                    prices = book_totals(page)
                    done[key] = {"total": min(prices) if prices else None, "clicks": [c1, c2]}
                    path.write_text(json.dumps(done))
                    print("book", key, done[key]["total"], flush=True)
        browser.close()
    return done

def ab_url(slug, ss, bb, price_max):
    return (
        f"https://www.airbnb.es/s/{slug}/homes?query={ss.replace(' ', '%20')}"
        f"&checkin={OUT_IN}&checkout={OUT_OUT}&adults=6&min_bedrooms=3&min_beds=3&min_bathrooms=2"
        f"&room_types%5B%5D=Entire%20home%2Fapt&price_max={price_max}"
        f"&price_filter_num_nights=4&search_by_map=true"
        f"&sw_lat={bb[0]}&sw_lng={bb[1]}&ne_lat={bb[2]}&ne_lng={bb[3]}"
    )

def parse_ab(text):
    if re.search(r"\b\d+\s*[–-]\s*\d+\s*dic|\bdel\s+\d+\s+al\s+\d+", text, re.I):
        if not re.search(r"4\s*[–-]\s*8\s*dic", text, re.I):
            return None
    rm = re.search(r"Valoración media de\s*([\d,]+)\s*sobre\s*5", text) or re.search(r"(\d,\d{1,2})\s*\(", text)
    if not rm:
        return None
    rating = float(rm.group(1).replace(",", "."))
    if rating < MIN_AIRBNB:
        return None
    totals = [int(x.replace(".", "")) for x in re.findall(r"(\d[\d\.]*)\s*€\s*en total", text)]
    if not totals:
        return None
    return totals[-1]

def cluster_price(prices):
    prices = sorted(set(prices))
    if len(prices) >= 2 and prices[0] < CLUSTER * prices[1]:
        return prices[1], prices
    return (prices[0] if prices else None), prices

def bk_url(ss, dest):
    q = ss.replace(" ", "+")
    return (
        "https://www.booking.com/searchresults.html?ss=" + q + "&dest_id=" + dest + "&dest_type=city"
        f"&checkin={OUT_IN}&checkout={OUT_OUT}&group_adults=6&no_rooms=3&group_children=0"
        "&selected_currency=EUR&nflt=ht_id%3D204%3Broomfacility%3D38%3Breview_score%3D60&order=price&sb=1"
    )

def sleeps6(text):
    m = re.search(r"3\s*[x×]", text)
    if not m:
        return False
    chunk = text[m.start():m.start() + 180]
    if re.search(r"dormitory|bunk|hostel|guest house|entire apartment|entire home", text, re.I):
        return False
    if re.search(r"3\s*[x×]\s*.{0,40}(apartment|studio)\b", chunk, re.I):
        return False
    sm = re.search(r"(\d+)\s+single beds", chunk, re.I)
    dm = re.search(r"(\d+)\s+(?:extra-large |large )?double beds", chunk, re.I)
    cap = (int(sm.group(1)) if sm else 0) + 2 * (int(dm.group(1)) if dm else 0)
    if re.search(r"double or twin|twin or double|choice of beds", chunk, re.I):
        return True
    if cap >= 6:
        return True
    if re.search(r"3\s*[x×]\s*(?:\w+\s+){0,3}(double|twin)\b", chunk, re.I) and "single room" not in chunk.lower():
        return True
    return False

def price_of(text):
    cm = re.search(r"Current price €\s*([\d,]+)", text)
    if cm:
        return int(cm.group(1).replace(",", ""))
    pm = re.search(r"(?<![Oo]riginal )Price €\s*([\d,]+)", text)
    if pm:
        return int(pm.group(1).replace(",", ""))
    return None

def parse_bk(text):
    if "Scored" not in text or not sleeps6(text):
        return None
    score = float(re.search(r"Scored\s+([\d.]+)", text).group(1))
    if score < MIN_BOOKING or "4 nights" not in text or "6 adults" not in text:
        return None
    price = price_of(text)
    dist = None
    mm = re.search(r"([\d.]+)\s*miles from cent", text, re.I)
    if mm:
        dist = float(mm.group(1))
    if price is None or dist is None:
        return None
    return {"price": price, "score": score, "miles": dist, "name": text.splitlines()[0].strip()}

def pick_hotel(cards):
    near = [c for c in cards if c["miles"] <= MILES_NEAR]
    used = near or [c for c in cards if c["miles"] <= MILES_FAR]
    used.sort(key=lambda c: c["price"])
    return used[0] if used else None

def scrape_stays(cache):
    from playwright.sync_api import sync_playwright
    path = cache / "stays.json"
    done = json.loads(path.read_text()) if path.exists() else {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/local/bin/google-chrome", headless=False,
                                     args=["--disable-blink-features=AutomationControlled"])
        ab = browser.new_context(locale="es-ES", viewport={"width": 1400, "height": 1100}).new_page()
        bk = browser.new_context(locale="en-GB", viewport={"width": 1400, "height": 1100}).new_page()
        bk.goto("https://www.booking.com/", wait_until="domcontentloaded", timeout=60000)
        bk.wait_for_timeout(1200)
        if bk.locator("#onetrust-accept-btn-handler").count():
            bk.locator("#onetrust-accept-btn-handler").click()
        for cid, slug, ss, dest, bb in CITIES:
            row = done.get(cid, {})
            if "stay" not in row:
                prices = []
                for mx in PRICE_STEPS:
                    ab.goto(ab_url(slug, ss, bb, mx), wait_until="domcontentloaded", timeout=60000)
                    ab.wait_for_timeout(3000)
                    if ab.locator("button:has-text('Aceptar')").count():
                        try:
                            ab.locator("button:has-text('Aceptar')").first.click(timeout=1500)
                        except Exception:
                            pass
                    cards = ab.evaluate("""() => [...document.querySelectorAll('[data-testid="card-container"]')].map(c => c.innerText || '')""")
                    prices = []
                    for t in cards:
                        n = parse_ab(t)
                        if n:
                            prices.append(n)
                    if len(prices) >= 3:
                        break
                stay, allp = cluster_price(prices)
                row = {"stay": stay, "prices": allp}
            if "hotel" not in row:
                bk.goto(bk_url(ss, dest), wait_until="domcontentloaded", timeout=60000)
                bk.wait_for_timeout(3000)
                seen = {}
                for _ in range(6):
                    for t in bk.locator("[data-testid='property-card']").evaluate_all("els => els.map(e => e.innerText||'')"):
                        name = t.splitlines()[0].strip() if t else ""
                        if name:
                            seen.setdefault(name, t)
                    bk.mouse.wheel(0, 2200)
                    bk.wait_for_timeout(600)
                hotel = pick_hotel([c for t in seen.values() if (c := parse_bk(t))])
                row["hotel"] = hotel["price"] if hotel else None
                row["hotel_name"] = hotel["name"] if hotel else ""
                row["hotel_score"] = hotel["score"] if hotel else None
            done[cid] = row
            path.write_text(json.dumps(done))
            print("stay", cid, row.get("stay"), row.get("hotel"), flush=True)
        browser.close()
    return done

def euro(n):
    return f"{n:,}".replace(",", ".")

def write_html(flights, stays, notes):
    html = HTML.read_text()
    order = rank_rows(flights, stays)
    rank_of = {cid: i for i, (_, cid, _, _) in enumerate(order, 1)}
    for cid in DESTS:
        start = html.find(f'id: "{cid}"')
        nxt = html.find('id: "', start + 4)
        end = nxt if nxt != -1 else html.find("];", start)
        block = html[start:end]
        st, ht = stays[cid]["stay"], stays[cid]["hotel"]
        block2 = re.sub(
            r"(rank: )\d+(, ll: \[[^\]]+\], stay: )\d+(, hotel: )\d+(, max: )\d+",
            lambda m, r=rank_of[cid], s=st, h=ht: f"{m.group(1)}{r}{m.group(2)}{s}{m.group(3)}{h}{m.group(4)}{s}",
            block, count=1)
        why = why_text(cid, flights[cid], stays[cid], notes.get(cid, []))
        for lang, text in why.items():
            block2 = re.sub(rf'({lang}: )"(?:\\.|[^"\\])*"', lambda m, t=text: m.group(1) + json.dumps(t, ensure_ascii=False), block2, count=1)
        for o in ORIGINS:
            f = flights[cid][o]
            back = ""
            if f["back_air"] != f["air"]:
                back = f', backAir: "{f["back_air"]}"'
            line = (
                f'{o}: {{ air: "{f["air"]}"{back}, p: {f["p"]}, '
                f'out: ["{f["dep"]}", "{f["arr"]}", "{f["dur"]}"], '
                f'back: ["{f["back_dep"]}", "{f["back_arr"]}", "{f["back_dur"]}"] }}'
            )
            block2 = re.sub(rf"{o}: \{{[^}}]+\}}", line, block2, count=1)
        html = html[:start] + block2 + html[end:]
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    hm = now.strftime("%H:%M")
    html = re.sub(r"a las \d{2}:\d{2}", f"a las {hm}", html, count=1)
    html = re.sub(r"at \d{2}:\d{2}", f"at {hm}", html, count=1)
    html = re.sub(r"um \d{2}:\d{2}", f"um {hm}", html, count=1)
    months = {9: ("septiembre", "September", "September")}
    # date is already in the footer; only the clock moves on a same-day refresh
    HTML.write_text(html)
    ranking = ", ".join(NAMES[cid] for _, cid, _, _ in order)
    proj = PROJECT.read_text()
    proj = re.sub(r"- Ranking: .*", f"- Ranking: {ranking}", proj, count=1)
    PROJECT.write_text(proj)
    print("RANK", ranking)

def why_text(cid, fl, stay, notes):
    bits = "; ".join(notes) if notes else "horarios ya alineados o la diferencia pasa de 30 €"
    bed = "hotel" if stay["hotel"] <= stay["stay"] else "Airbnb"
    es = (f"BCN {fl['BCN']['air']} {fl['BCN']['dep']}–{fl['BCN']['arr']}, "
          f"FRA {fl['FRA']['air']} {fl['FRA']['dep']}–{fl['FRA']['arr']}, "
          f"HAM {fl['HAM']['air']} {fl['HAM']['dep']}–{fl['HAM']['arr']}. {bits}. "
          f"Entra el {bed}: hotel {euro(stay['hotel'])} €, Airbnb {euro(stay['stay'])} €.")
    en = (f"BCN {fl['BCN']['air']} {fl['BCN']['dep']}–{fl['BCN']['arr']}, "
          f"FRA {fl['FRA']['air']} {fl['FRA']['dep']}–{fl['FRA']['arr']}, "
          f"HAM {fl['HAM']['air']} {fl['HAM']['dep']}–{fl['HAM']['arr']}. {bits}. "
          f"Cheaper stay is the {bed}: hotel {euro(stay['hotel'])} €, Airbnb {euro(stay['stay'])} €.")
    de = (f"BCN {fl['BCN']['air']} {fl['BCN']['dep']}–{fl['BCN']['arr']}, "
          f"FRA {fl['FRA']['air']} {fl['FRA']['dep']}–{fl['FRA']['arr']}, "
          f"HAM {fl['HAM']['air']} {fl['HAM']['dep']}–{fl['HAM']['arr']}. {bits}. "
          f"Günstiger ist {bed}: Hotel {euro(stay['hotel'])} €, Airbnb {euro(stay['stay'])} €.")
    return {"es": es, "en": en, "de": de}

def decide(raw_flights, booked):
    flights, notes = {}, {}
    for dest in DESTS:
        by = {}
        for orig in ORIGINS:
            exp = raw_flights.get(f"{orig}-{dest}", {}).get("expanded", [])
            opts = apply_book(combos(exp), booked, orig, dest)
            by[orig] = opts
        chosen, notes[dest] = align(by)
        flights[dest] = chosen
    return flights, notes

def self_check():
    """Locked parsers. These strings are the cases that previously moved a price."""
    assert price_of("Original price € 916. Current price € 843") == 843
    assert price_of("Original price € 916") is None
    assert price_of("Price € 649") == 649
    assert parse_bk("Hotel Sophia\nScored 8.0\n3 × Single Room\n3 single beds\n1.2 miles from centre\n4 nights, 6 adults\nCurrent price € 1435") is None
    assert parse_bk("hub London Clerkenwell\nScored 8.3\n3 × Double Room\n3 double beds\n1.4 miles from centre\n4 nights, 6 adults\nCurrent price € 1463")["price"] == 1463
    assert cluster_price([961, 1927])[0] == 1927
    assert cluster_price([1581, 1700])[0] == 1581
    assert half_up(577) == 289 and half_up(322) == 161
    assert norm("Air Dolomiti") == "Lufthansa"
    assert norm("Air France. Operated by HOP!") == "Air France"
    assert norm("Lufthansa City Airlines") == "Lufthansa"
    assert extras("Discover Airlines") == 0 and extras("Wizz Air") == 82

def check():
    self_check()
    html = HTML.read_text()
    assert 'value="30"' in html and "let foodDay = 30" in html, "comida por defecto no es 30"
    assert "review_score%3D60" in html, "Booking sin filtro 6/10"
    flights, stays = {}, {}
    for cid in DESTS:
        start = html.find(f'id: "{cid}"')
        nxt = html.find('id: "', start + 4)
        block = html[start:nxt if nxt != -1 else html.find("];", start)]
        m = re.search(r"rank: (\d+).*?stay: (\d+), hotel: (\d+)", block)
        stays[cid] = {"stay": int(m.group(2)), "hotel": int(m.group(3)), "rank": int(m.group(1))}
        flights[cid] = {}
        for o in ORIGINS:
            fm = re.search(rf'{o}: \{{ air: "([^"]+)".*?p: (\d+)', block)
            flights[cid][o] = {"air": fm.group(1), "p": int(fm.group(2))}
    rows = rank_rows(flights, stays)
    for i, (group, cid, _, _) in enumerate(rows, 1):
        got = stays[cid]["rank"]
        if got != i:
            raise SystemExit(f"FALLO rank {cid}: guardado {got}, total {group} sería #{i}")
        print(f"#{i} {cid} {group}")
    print("CHECK ok")

def load_replay(folder):
    folder = Path(folder)
    raw = json.loads((folder / "flights_raw.json").read_text())
    booked_raw = json.loads((folder / "booked.json").read_text()) if (folder / "booked.json").exists() else {}
    booked = {}
    for k, v in booked_raw.items():
        parts = k.split("-")
        booked[f"{parts[0]}-{parts[1]}-{parts[2]}-{parts[3]}"] = v
    # FRA-MXP was booked outside that file: list/book 408 → p 204
    booked.setdefault("FRA-MXP-20:50-18:35", {"total": 408})
    return raw, booked

def shipped_flights():
    """Flights currently stored in index.html. Replay must reproduce these, not a new taste."""
    html = HTML.read_text()
    out = {}
    for cid in DESTS:
        start = html.find(f'id: "{cid}"')
        nxt = html.find('id: "', start + 4)
        block = html[start:nxt if nxt != -1 else html.find("];", start)]
        out[cid] = {}
        for o in ORIGINS:
            fm = re.search(
                rf'{o}: \{{ air: "([^"]+)"(?:, backAir: "([^"]+)")?, p: (\d+), '
                rf'out: \["([^"]+)", "([^"]+)", "[^"]+"\], back: \["([^"]+)", "([^"]+)"',
                block)
            if not fm:
                raise SystemExit(f"FALLO parse vuelo {cid} {o}")
            out[cid][o] = {
                "air": fm.group(1), "back_air": fm.group(2) or fm.group(1), "p": int(fm.group(3)),
                "dep": fm.group(4), "arr": fm.group(5), "back_dep": fm.group(6), "back_arr": fm.group(7),
            }
    return out

def replay(folder):
    self_check()
    raw, booked = load_replay(folder)
    flights, notes = decide(raw, booked)
    expect = shipped_flights()
    bad = 0
    for cid in DESTS:
        for o in ORIGINS:
            f = flights[cid].get(o) or {}
            e = expect[cid][o]
            got = (f.get("air"), f.get("back_air"), f.get("p"), f.get("dep"), f.get("arr"), f.get("back_dep"), f.get("back_arr"))
            want = (e["air"], e["back_air"], e["p"], e["dep"], e["arr"], e["back_dep"], e["back_arr"])
            if got != want:
                bad += 1
                print("DIFF", cid, o, got, "vs", want)
        if not any(True for o in ORIGINS if (flights[cid][o]["dep"], flights[cid][o]["back_dep"]) != (expect[cid][o]["dep"], expect[cid][o]["back_dep"])):
            print(cid, "ok", notes.get(cid))
    if bad:
        raise SystemExit(f"FALLO replay {bad} vuelos")
    print("REPLAY ok")

def book_plan(raw, flights, booked):
    """Book the chosen itinerary and the cheapest one when they differ, so the book price can still win."""
    plan = {}
    for dest in DESTS:
        plan[dest] = {}
        for orig in ORIGINS:
            exp = raw.get(f"{orig}-{dest}", {}).get("expanded", [])
            opts = apply_book(combos(exp), booked, orig, dest)
            items = []
            cur = (flights.get(dest) or {}).get(orig)
            if cur:
                items.append(cur)
            if opts:
                cheap = min(opts, key=lambda c: (c["fly"], c["dep"], c["back_dep"]))
                if not cur or (cheap["dep"], cheap["back_dep"]) != (cur["dep"], cur["back_dep"]):
                    items.append(cheap)
            plan[dest][orig] = items
    return plan

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        check()
        return
    if len(sys.argv) > 1 and sys.argv[1] == "--replay":
        replay(sys.argv[2] if len(sys.argv) > 2 else ROOT / "fixtures" / "replay-2026-09-24")
        return
    cache = Path("/tmp/refresh-cache")
    cache.mkdir(exist_ok=True)
    raw = scrape_flights(cache)
    booked = {}
    flights, notes = decide(raw, booked)
    booked = scrape_books(cache, book_plan(raw, flights, booked))
    flights, notes = decide(raw, booked)
    booked = scrape_books(cache, book_plan(raw, flights, booked))
    flights, notes = decide(raw, booked)
    stays = scrape_stays(cache)
    for cid in DESTS:
        if not stays[cid].get("stay") or not stays[cid].get("hotel"):
            raise SystemExit(f"FALLO alojamiento {cid}")
        if not all(flights[cid].get(o) for o in ORIGINS):
            raise SystemExit(f"FALLO vuelo {cid}")
    write_html(flights, stays, notes)
    check()

if __name__ == "__main__":
    main()
