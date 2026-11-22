#!/usr/bin/env python3
"""check.py · Gesundheitscheck eines Lexware-Office-Kontos, nur lesend, als Ampel-Bericht in Markdown.

    python3 check.py [--konto NAME] [--tage-alt 180] > lexware-check.md

Prüft, was Automatisierungen und KI-Agenten in der Praxis scheitern lässt: Kunden ohne oder mit mehreren
Rechnungsadressen, Dubletten, Artikel ohne Nummer, uneinheitliche Einheiten, alte Entwürfe, sehr alte offene
Rechnungen (Zeichen für fehlenden Zahlungsabgleich), abgelaufene Angebote, Webhooks. Schreibt nichts.
Teil der Lexware Office Skills von Corvek Solutions (MIT-Lizenz).
"""
from __future__ import annotations

import datetime as dt
import os
import pathlib
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "lexware-grundlagen" / "scripts"))
os.environ["LEXWARE_NUR_LESEN"] = "1"          # dieser Check schreibt nie
import lexware  # noqa: E402

GRUEN, GELB, ROT = "🟢", "🟡", "🔴"
RECHTSFORM = re.compile(r"\b(gmbh|ug|ag|kg|ohg|gbr|e\.?\s?k\.?|mbh|co|haftungsbeschränkt|&)\b", re.I)
EINHEIT = {"st": "Stück", "stk": "Stück", "stck": "Stück", "stück": "Stück", "std": "Stunde", "h": "Stunde",
           "stunde": "Stunde", "stunden": "Stunde", "psch": "Pauschal", "pauschal": "Pauschal", "pausch": "Pauschal",
           "m2": "m²", "qm": "m²", "m²": "m²", "lfm": "lfdm", "lfdm": "lfdm", "lfdm.": "lfdm", "m": "m"}


def hole_alle(pfad: str, params: dict, konto, max_seiten: int = 80) -> list:
    aus, seite = [], 0
    while seite < max_seiten:
        status, d, _ = lexware.anfrage("GET", pfad, konto, dict(params, page=seite))
        if status != 200:
            raise lexware.Abbruch(lexware.fehlertext(status, d, konto), 2)
        if not isinstance(d, dict) or "content" not in d:
            return d if isinstance(d, list) else []
        aus.extend(d["content"])
        if d.get("last", True):
            break
        seite += 1
    return aus


def name_von(k: dict) -> str:
    if k.get("company"):
        return k["company"].get("name") or ""
    p = k.get("person") or {}
    return " ".join(x for x in (p.get("firstName"), p.get("lastName")) if x)


def schluessel_name(n: str) -> str:
    n = RECHTSFORM.sub(" ", n.lower())
    return re.sub(r"[^a-z0-9äöüß]", "", n)


def tag(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s[:10]) if s else None


def befund(stufe: str, titel: str, text: str, beispiele: list[str] | None = None) -> dict:
    return {"stufe": stufe, "titel": titel, "text": text, "beispiele": (beispiele or [])[:8]}


def pruefen(konto, tage_alt: int) -> tuple[dict, list[dict]]:
    heute = dt.date.today()
    status, profil, _ = lexware.anfrage("GET", "/profile", konto)
    if status != 200:
        raise lexware.Abbruch(lexware.fehlertext(status, profil, konto), 2)
    befunde: list[dict] = []

    # Kontakte
    kontakte = hole_alle("/contacts", {"size": 250}, konto)
    kunden = [k for k in kontakte if "customer" in (k.get("roles") or {}) and not k.get("archived")]
    ohne = [k for k in kunden if not (k.get("addresses") or {}).get("billing")]
    mehr = [k for k in kunden if len((k.get("addresses") or {}).get("billing") or []) > 1]
    gruppen = defaultdict(list)
    for k in kunden:
        if name_von(k):
            gruppen[schluessel_name(name_von(k))].append(k)
    dubletten = [g for g in gruppen.values() if len(g) > 1]
    if mehr:
        befunde.append(befund(ROT, "Kunden mit mehreren Rechnungsadressen",
                              f"{len(mehr)} Kunden. Belege mit bloßer Kunden-ID lehnt Lexware hier ab (406), und über "
                              "die API lassen sich diese Kontakte nicht ändern. In Lexware auf eine Rechnungsadresse "
                              "bereinigen oder die Adresse in jedem Beleg ausgeschrieben mitgeben.",
                              [name_von(k) for k in mehr]))
    if ohne:
        befunde.append(befund(GELB, "Kunden ohne Rechnungsadresse",
                              f"{len(ohne)} Kunden. Ein Beleg an sie scheitert, bis eine Adresse da ist.",
                              [name_von(k) for k in ohne]))
    if dubletten:
        befunde.append(befund(GELB, "Mögliche Dubletten",
                              f"{len(dubletten)} Namen kommen mehrfach vor (Rechtsform und Schreibweise ignoriert). "
                              "Agenten finden dann mehrere Treffer und müssen nachfragen.",
                              [" = ".join(name_von(k) for k in g) for g in dubletten]))

    # Artikel
    artikel = hole_alle("/articles", {}, konto)
    ohne_nr = [a for a in artikel if not (a.get("articleNumber") or "").strip()]
    nummern = Counter((a.get("articleNumber") or "").strip() for a in artikel if (a.get("articleNumber") or "").strip())
    doppelt = [n for n, c in nummern.items() if c > 1]
    einheiten = defaultdict(set)
    for a in artikel:
        roh = (a.get("unitName") or "").strip()
        if roh:
            einheiten[EINHEIT.get(roh.lower().rstrip("."), roh)].add(roh)
    gemischt = {k: v for k, v in einheiten.items() if len(v) > 1}
    if artikel and len(ohne_nr) > len(artikel) / 2:
        befunde.append(befund(GELB, "Artikel ohne Artikelnummer",
                              f"{len(ohne_nr)} von {len(artikel)}. Mit Nummer findet die Artikelsuche in Lexware und "
                              "jeder Agent die Leistung sicher wieder.", [a.get("title", "") for a in ohne_nr]))
    if doppelt:
        befunde.append(befund(ROT, "Doppelte Artikelnummern",
                              f"{len(doppelt)} Nummern sind mehrfach vergeben. Lexware prüft das nicht.", doppelt))
    if gemischt:
        befunde.append(befund(GELB, "Uneinheitliche Einheiten",
                              "Dieselbe Einheit steht in mehreren Schreibweisen im Artikelstamm.",
                              [f"{k}: {', '.join(sorted(v))}" for k, v in gemischt.items()]))

    # Rechnungen
    entwuerfe = hole_alle("/voucherlist", {"voucherType": "invoice,quotation,creditnote,orderconfirmation",
                                           "voucherStatus": "draft", "size": 250}, konto)
    alte_entwuerfe = [v for v in entwuerfe if tag(v.get("voucherDate")) and (heute - tag(v["voucherDate"])).days > 30]
    if alte_entwuerfe:
        befunde.append(befund(GELB, "Alte Entwürfe",
                              f"{len(alte_entwuerfe)} Entwürfe sind älter als 30 Tage. Aufräumen geht nur in Lexware.",
                              [f"{v.get('voucherType')} {v.get('contactName', '')} vom {v.get('voucherDate', '')[:10]}"
                               for v in alte_entwuerfe]))
    offen = hole_alle("/voucherlist", {"voucherType": "invoice", "voucherStatus": "open", "size": 250}, konto)
    sehr_alt = [v for v in offen if tag(v.get("dueDate")) and (heute - tag(v["dueDate"])).days > tage_alt]
    if offen and len(sehr_alt) >= max(5, len(offen) // 4):
        befunde.append(befund(ROT, "Zahlungsabgleich fehlt vermutlich",
                              f"{len(sehr_alt)} von {len(offen)} offenen Rechnungen sind seit über {tage_alt} Tagen "
                              "fällig. Meist sind sie bezahlt, aber in Lexware nicht zugeordnet. Dann ist jede "
                              "Auswertung offener Posten falsch. Bankkonto in Lexware verbinden und Zahlungen zuordnen.",
                              [f"{v.get('voucherNumber')} {v.get('contactName', '')}" for v in sehr_alt]))
    elif sehr_alt:
        befunde.append(befund(GELB, "Sehr alte offene Rechnungen",
                              f"{len(sehr_alt)} offene Rechnungen sind seit über {tage_alt} Tagen fällig.",
                              [f"{v.get('voucherNumber')} {v.get('contactName', '')}" for v in sehr_alt]))
    ueberfaellig = [v for v in offen if v.get("voucherStatus") == "overdue"]

    # Angebote
    angebote = hole_alle("/voucherlist", {"voucherType": "quotation", "voucherStatus": "open", "size": 250}, konto)
    abgelaufen = [v for v in angebote if v.get("voucherStatus") == "overdue"]
    if angebote and len(abgelaufen) > len(angebote) / 2:
        befunde.append(befund(GELB, "Viele abgelaufene Angebote",
                              f"{len(abgelaufen)} von {len(angebote)} offenen Angeboten sind abgelaufen. In Lexware als "
                              "angenommen oder abgelehnt markieren, sonst stimmt keine Angebotsquote."))

    # Webhooks
    _, abos, _ = lexware.anfrage("GET", "/event-subscriptions", konto)
    abo_liste = (abos or {}).get("content", []) if isinstance(abos, dict) else (abos or [])

    zahlen = {
        "firma": profil.get("companyName"), "steuerart": profil.get("taxType"),
        "kleinunternehmer": profil.get("smallBusiness"), "kontakte": len(kontakte), "kunden": len(kunden),
        "artikel": len(artikel), "offene_rechnungen": len(offen), "davon_ueberfaellig": len(ueberfaellig),
        "offene_angebote": len(angebote), "entwuerfe": len(entwuerfe), "webhooks": len(abo_liste),
    }
    return zahlen, befunde


def bericht(z: dict, befunde: list[dict]) -> str:
    gesamt = ROT if any(b["stufe"] == ROT for b in befunde) else GELB if befunde else GRUEN
    zeilen = [
        f"# Lexware-Check: {z['firma']}",
        "",
        f"Stand {dt.datetime.now():%d.%m.%Y %H:%M} · nur gelesen, nichts geändert · Gesamt: {gesamt}",
        "",
        "| Bereich | Stand |",
        "| --- | --- |",
        f"| Konto | Steuerart {z['steuerart']}, Kleinunternehmer {'ja' if z['kleinunternehmer'] else 'nein'} |",
        f"| Kontakte | {z['kontakte']} gesamt, {z['kunden']} aktive Kunden |",
        f"| Artikel | {z['artikel']} |",
        f"| Offene Rechnungen | {z['offene_rechnungen']}, davon überfällig {z['davon_ueberfaellig']} |",
        f"| Offene Angebote | {z['offene_angebote']} |",
        f"| Entwürfe | {z['entwuerfe']} |",
        f"| Webhooks | {z['webhooks'] or 'keine (Automatisierungen fragen dann regelmäßig ab)'} |",
        "",
        "## Befunde",
        "",
    ]
    if not befunde:
        zeilen.append(f"{GRUEN} Keine Auffälligkeiten. Das Konto ist bereit für Automatisierung.")
    for b in sorted(befunde, key=lambda b: [ROT, GELB, GRUEN].index(b["stufe"])):
        zeilen += [f"### {b['stufe']} {b['titel']}", "", b["text"], ""]
        zeilen += [f"- {x}" for x in b["beispiele"]]
        if b["beispiele"]:
            zeilen.append("")
    return "\n".join(zeilen).rstrip() + "\n"


def main(argv: list[str]) -> int:
    konto = argv[argv.index("--konto") + 1] if "--konto" in argv else None
    tage = int(argv[argv.index("--tage-alt") + 1]) if "--tage-alt" in argv else 180
    try:
        z, b = pruefen(konto, tage)
    except lexware.Abbruch as e:
        print(str(e), file=sys.stderr)
        return e.code
    print(bericht(z, b), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
