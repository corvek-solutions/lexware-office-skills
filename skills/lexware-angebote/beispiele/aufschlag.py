#!/usr/bin/env python3
"""aufschlag.py · Positionen eines Nachunternehmer-Angebots mit Aufschlag in Lexware-Positionen umrechnen.

    python3 aufschlag.py positionen.json 15 [--fee]  > lineItems.json

positionen.json: [{"name": "...", "description": "...", "quantity": 40, "unitName": "m²", "netAmount": 41.74}, ...]
Ohne --fee wird der Aufschlag in jeden Einzelpreis eingerechnet (je Position kaufmännisch auf Cent gerundet), mit
--fee bleiben die Positionen unverändert und eine Position „Handling Fee N %“ kommt dazu. Gibt auf stderr Einkauf,
Aufschlag und Angebotssumme aus, zum Abgleich mit der Summe, die Lexware nach dem Anlegen meldet.
Teil der Lexware Office Skills von Corvek Solutions (MIT-Lizenz).
"""
import json
import sys
from decimal import ROUND_HALF_UP, Decimal


def cent(x) -> Decimal:
    return Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    positionen = json.load(open(argv[0], encoding="utf-8"))
    prozent = Decimal(argv[1].replace(",", "."))
    fee = "--fee" in argv
    steuer = 19
    aus, einkauf, summe = [], Decimal(0), Decimal(0)
    for p in positionen:
        menge = Decimal(str(p["quantity"]))
        ek = cent(p["netAmount"])
        vk = ek if fee else cent(ek * (1 + prozent / 100))
        einkauf += cent(menge * ek)
        summe += cent(menge * vk)
        aus.append({"type": "custom", "name": p["name"][:255], **({"description": p["description"]} if p.get("description") else {}),
                    "quantity": float(menge), "unitName": p.get("unitName", "Stück"),
                    "unitPrice": {"currency": "EUR", "netAmount": float(vk), "taxRatePercentage": p.get("taxRatePercentage", steuer)},
                    "discountPercentage": 0})
    if fee:
        betrag = cent(einkauf * prozent / 100)
        summe += betrag
        aus.append({"type": "custom", "name": f"Handling Fee {str(prozent).replace('.', ',')} %", "quantity": 1,
                    "unitName": "psch", "unitPrice": {"currency": "EUR", "netAmount": float(betrag), "taxRatePercentage": steuer},
                    "discountPercentage": 0})
    print(json.dumps(aus, indent=2, ensure_ascii=False))
    print(f"Einkauf netto {einkauf} €, Aufschlag {summe - einkauf} €, Angebot netto {summe} €", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1:])
