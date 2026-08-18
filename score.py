"""Higiene de token EVM con un dict de GoPlus token_security. No predice exito."""

from __future__ import annotations

import json
import re
import sys
import urllib.request

GOPLUS = "https://api.gopluslabs.io/api/v1/token_security/{chain}?contract_addresses={addr}"
ADDR_RE = re.compile(r"^0x[0-9a-fA-F]{40}$")
# ponytail: umbral fijo 10% sell-tax → si GoPlus cambia escala, leer docs y ajustar
TAX_FAIL = 10.0
HARD = (
    ("is_honeypot", "honeypot"),
    ("cannot_buy", "no se puede comprar"),
    ("hidden_owner", "owner oculto"),
    ("selfdestruct", "selfdestruct"),
)
SOFT = (
    ("is_mintable", "mintable"),
    ("can_take_back_ownership", "pueden recuperar el owner"),
    ("is_proxy", "proxy upgradeable"),
    ("owner_change_balance", "owner cambia balances"),
    ("transfer_pausable", "pueden pausar transfers"),
    ("slippage_modifiable", "tax/slippage modificable"),
)


def _on(d: dict, k: str) -> bool:
    return str(d.get(k, "0")) == "1"


def _tax(d: dict, k: str) -> float:
    try:
        return float(d.get(k) or 0)
    except (TypeError, ValueError):
        return 0.0


def score(g: dict) -> tuple[str, list[str]]:
    """FAIL trampa obvia, WARN deployer armado, PASS higiene ok (sigue pudiendo morir)."""
    if not g:
        return "FAIL", ["sin datos GoPlus"]
    if _on(g, "trust_list"):
        return "PASS", ["trust_list (estable/conocido; no aplica filtro de meme nuevo)"]
    reasons: list[str] = []
    for k, label in HARD:
        if _on(g, k):
            reasons.append(label)
    if _tax(g, "sell_tax") >= TAX_FAIL:
        reasons.append(f"sell tax {_tax(g, 'sell_tax')}%")
    if reasons:
        return "FAIL", reasons
    for k, label in SOFT:
        if _on(g, k):
            reasons.append(label)
    try:
        if float(g.get("creator_percent") or 0) >= 0.05:
            reasons.append("creator >= 5%")
    except (TypeError, ValueError):
        pass
    owner = str(g.get("owner_address") or "").lower()
    if owner and owner not in ("", "0x0000000000000000000000000000000000000000", "0x"):
        reasons.append("owner no renunciado")
    return ("WARN", reasons) if reasons else ("PASS", ["higiene ok, no es prediccion de subida"])


def fetch(chain: str, addr: str) -> dict:
    if not chain.isdigit() or not ADDR_RE.match(addr):
        raise SystemExit("uso: python score.py <chain_id> <0xaddress>")
    url = GOPLUS.format(chain=chain, addr=addr.lower())
    with urllib.request.urlopen(url, timeout=20) as r:
        payload = json.load(r)
    if payload.get("code") != 1:
        raise SystemExit(payload.get("message") or "GoPlus error")
    result = payload.get("result") or {}
    return result.get(addr.lower()) or {}


def _check() -> None:
    honeypot = {"is_honeypot": "1", "sell_tax": "0"}
    assert score(honeypot)[0] == "FAIL"
    clean = {
        "is_honeypot": "0",
        "cannot_buy": "0",
        "hidden_owner": "0",
        "selfdestruct": "0",
        "is_mintable": "0",
        "sell_tax": "0",
        "owner_address": "0x0000000000000000000000000000000000000000",
        "creator_percent": "0.01",
    }
    assert score(clean)[0] == "PASS"
    armed = {**clean, "is_mintable": "1", "owner_address": "0x1111111111111111111111111111111111111111"}
    assert score(armed)[0] == "WARN"
    trusted = {"trust_list": "1", "is_mintable": "1", "is_honeypot": "0"}
    assert score(trusted)[0] == "PASS"
    print("ok")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--check":
        _check()
    elif len(sys.argv) == 3:
        g = fetch(sys.argv[1], sys.argv[2])
        verdict, reasons = score(g)
        name = g.get("token_symbol") or g.get("token_name") or sys.argv[2]
        print(f"{verdict} {name}: {', '.join(reasons)}")
    else:
        raise SystemExit("uso: python score.py --check | python score.py <chain_id> <0xaddress>")
