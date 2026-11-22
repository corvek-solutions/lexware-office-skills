#!/usr/bin/env python3
"""lexware.py · Werkzeug für die Lexware Office Public API (api.lexware.io).

Nur Python-Standardbibliothek, ab Python 3.9. Teil der Lexware Office Skills von Corvek Solutions (MIT-Lizenz).

Die Regeln aus dem Produktivbetrieb sind fest eingebaut:
  * Drossel auf 1,8 Anfragen je Sekunde, auch über mehrere Aufrufe hintereinander (Lexware erlaubt 2).
  * 429 (zu viele Anfragen) wartet und wiederholt; 406 (Prüffehler) wird nie wiederholt, das schuldige Feld steht da.
  * Schreiben (POST, PUT) wird nie blind wiederholt: Es könnte angekommen sein. Erst nachsehen, dann neu senden.
  * Festschreiben (finalize=true) ist gesperrt, solange nicht ausdrücklich --festschreiben dabeisteht.
  * LEXWARE_NUR_LESEN=1 sperrt jedes Schreiben.
  * Der Schlüssel wird nie ausgegeben.

Schlüssel (der erste Fund gilt):
  1. Umgebungsvariable LEXWARE_API_KEY (mit --konto NAME: LEXWARE_API_KEY_NAME)
  2. Datei ~/.config/lexware/api-key (mit --konto NAME: ~/.config/lexware/NAME.key), Rechte 600
  3. macOS-Schlüsselbund, Dienst „lexware-api-key“ (mit --konto NAME: „lexware-api-key-NAME“)

Befehle:
  pruefen                                  Verbindung und Konto prüfen (Profil, Steuerart, Kleinunternehmer)
  get    <pfad> [k=v ...]                  eine Anfrage, z. B.  get /contacts name=Muster
  alle   <pfad> [k=v ...]                  alle Seiten einer Liste, z. B.  alle /voucherlist voucherType=invoice voucherStatus=open
  post   <pfad> <datei.json|-> [k=v ...]   anlegen (Belege als Entwurf), z. B.  post /invoices entwurf.json
  put    <pfad> <datei.json|->             ändern (mit aktueller version im Körper)
  loeschen <pfad> --ja                     nur Artikel und Ereignis-Abos
  pdf    <art> <id> <ziel.pdf> [--xml]     PDF eines festgeschriebenen Belegs holen (--xml: XRechnung als XML)
  hochladen <datei> [--an-beleg ID]        Beleg (PDF, JPG, PNG, XML) hochladen, ohne ID zur Belegerfassung
  link   <art> <id> [--bearbeiten]         Direktlink in Lexware Office
  datum  <JJJJ-MM-TT>                      Belegdatum mit dem Berliner Versatz dieses Tages

Optionen für get und alle:  --felder a,b.c   nur diese Felder   --csv   als CSV   --max-seiten N
Belegarten für pdf und link: invoice, quotation, order-confirmation, credit-note, down-payment-invoice,
delivery-note, dunning, voucher (oder die Pfade: invoices, quotations, …)
"""
from __future__ import annotations

import csv
import io
import json
import mimetypes
import os
import pathlib
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

BASIS = "https://api.lexware.io/v1"
APP = "https://app.lexware.de/permalink"
ABSTAND = 1 / 1.8                 # Sekunden zwischen zwei Anfragen
VERSUCHE_429 = 5
VERSUCHE_STOERUNG = 3             # nur beim Lesen
ZEIT = 60
DATEI_MAX = 5 * 1024 * 1024       # Lexware nimmt Belegdateien bis 5 MB
STAND = pathlib.Path(os.environ.get("XDG_CACHE_HOME", pathlib.Path.home() / ".cache")) / "lexware" / "letzte-anfrage"

ARTEN = {
    "invoice": "invoices", "quotation": "quotations", "order-confirmation": "order-confirmations",
    "orderconfirmation": "order-confirmations", "credit-note": "credit-notes", "creditnote": "credit-notes",
    "down-payment-invoice": "down-payment-invoices", "downpaymentinvoice": "down-payment-invoices",
    "delivery-note": "delivery-notes", "deliverynote": "delivery-notes", "dunning": "dunnings", "voucher": "vouchers",
}
LOESCHBAR = [re.compile(r"^/articles/[0-9a-f-]{36}$"), re.compile(r"^/event-subscriptions/[0-9a-f-]{36}$")]


class Abbruch(Exception):
    def __init__(self, text: str, code: int = 1):
        super().__init__(text)
        self.code = code


# --------------------------------------------------------------------------------------------- Schlüssel und Adresse
def schluessel(konto: str | None) -> str:
    name = f"LEXWARE_API_KEY_{konto.upper().replace('-', '_')}" if konto else "LEXWARE_API_KEY"
    if os.environ.get(name, "").strip():
        return os.environ[name].strip()
    datei = pathlib.Path.home() / ".config" / "lexware" / (f"{konto}.key" if konto else "api-key")
    if datei.exists():
        if os.name == "posix" and datei.stat().st_mode & 0o077:
            print(f"Hinweis: {datei} ist für andere lesbar. Besser: chmod 600 {datei}", file=sys.stderr)
        k = datei.read_text().strip()
        if k:
            return k
    if sys.platform == "darwin":
        dienst = f"lexware-api-key-{konto}" if konto else "lexware-api-key"
        try:
            k = subprocess.run(["security", "find-generic-password", "-s", dienst, "-w"],
                               capture_output=True, text=True, check=True).stdout.strip()
            if k:
                return k
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    raise Abbruch(
        "Kein Lexware-Schlüssel gefunden. In Lexware Office unter Erweiterungen › Public API einen Schlüssel erzeugen "
        f"und als {name} setzen oder in {datei} ablegen (chmod 600). Siehe skills/lexware-grundlagen/SKILL.md.")


def basis() -> str:
    """Immer Lexware. Nur für Tests mit einer Attrappe auf diesem Rechner lässt sich die Adresse umstellen."""
    b = os.environ.get("LEXWARE_BASIS", "").strip().rstrip("/")
    if b and re.match(r"^http://(127\.0\.0\.1|localhost)(:\d+)?(/|$)", b):
        return b
    return BASIS


def nur_lesen() -> bool:
    return os.environ.get("LEXWARE_NUR_LESEN", "").strip().lower() in ("1", "ja", "true", "yes")


# --------------------------------------------------------------------------------------------- Drossel
def warten_auf_platz() -> None:
    """Höchstens 1,8 Anfragen je Sekunde, auch wenn das Werkzeug viele Male hintereinander startet."""
    try:
        STAND.parent.mkdir(parents=True, exist_ok=True)
        import fcntl  # nur Unix; unter Windows gilt die Drossel nur innerhalb eines Aufrufs
        with open(STAND, "a+") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            f.seek(0)
            try:
                letzte = float(f.read().strip() or 0)
            except ValueError:
                letzte = 0.0
            warte = letzte + ABSTAND - time.time()
            if warte > 0:
                time.sleep(min(warte, ABSTAND))
            f.seek(0)
            f.truncate()
            f.write(str(time.time()))
    except (ImportError, OSError):
        _warten_im_prozess()


_letzte = 0.0


def _warten_im_prozess() -> None:
    global _letzte
    warte = _letzte + ABSTAND - time.monotonic()
    if warte > 0:
        time.sleep(warte)
    _letzte = time.monotonic()


# --------------------------------------------------------------------------------------------- Anfrage
def anfrage(methode: str, pfad: str, konto: str | None = None, params: dict | None = None, koerper=None,
            datei: tuple[str, bytes, str] | None = None, felder: dict | None = None,
            accept: str = "application/json") -> tuple[int, object, dict]:
    """Eine Anfrage an Lexware. Gibt (Status, Daten, Kopfzeilen) zurück oder bricht mit klarem Satz ab."""
    schreibt = methode in ("POST", "PUT", "DELETE")
    if schreibt and nur_lesen():
        raise Abbruch("LEXWARE_NUR_LESEN ist gesetzt: Schreiben ist gesperrt.", 3)
    q = urllib.parse.urlencode({k: v for k, v in (params or {}).items() if v not in (None, "")})
    url = f"{basis()}{pfad}{'?' + q if q else ''}"
    kopf = {"Authorization": f"Bearer {schluessel(konto)}", "Accept": accept}
    daten = None
    if datei is not None:
        grenze = uuid.uuid4().hex
        teile = []
        for k, v in (felder or {}).items():
            teile.append(f'--{grenze}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
        name, inhalt, typ = datei
        teile.append(f'--{grenze}\r\nContent-Disposition: form-data; name="file"; filename="{name}"\r\n'
                     f"Content-Type: {typ}\r\n\r\n".encode() + inhalt + b"\r\n")
        teile.append(f"--{grenze}--\r\n".encode())
        daten = b"".join(teile)
        kopf["Content-Type"] = f"multipart/form-data; boundary={grenze}"
    elif koerper is not None:
        daten = json.dumps(koerper, ensure_ascii=False).encode()
        kopf["Content-Type"] = "application/json"

    drossel = stoerung = 0
    while True:
        warten_auf_platz()
        req = urllib.request.Request(url, data=daten, method=methode, headers=kopf)
        try:
            with urllib.request.urlopen(req, timeout=ZEIT) as a:
                roh = a.read()
                return a.status, _lesen(roh, a.headers.get("Content-Type", "")), dict(a.headers)
        except urllib.error.HTTPError as e:
            roh = e.read()
            if e.code == 429 and drossel < VERSUCHE_429:
                nach = e.headers.get("Retry-After")
                pause = min(float(nach), 60) if nach and nach.replace(".", "", 1).isdigit() else 2 ** drossel
                drossel += 1
                print(f"Lexware drosselt (429), warte {pause:.0f} s ({drossel}/{VERSUCHE_429}) …", file=sys.stderr)
                time.sleep(pause)
                continue
            if e.code in (500, 502, 503, 504) and not schreibt and stoerung < VERSUCHE_STOERUNG:
                stoerung += 1
                time.sleep(2 ** stoerung)
                continue
            return e.code, _lesen(roh, e.headers.get("Content-Type", "")), dict(e.headers)
        except (urllib.error.URLError, TimeoutError) as e:
            if schreibt:
                raise Abbruch(
                    f"Verbindung brach beim Schreiben ab ({e}). Der Beleg kann trotzdem angekommen sein: erst in der "
                    "Belegliste nachsehen (lexware.py get /voucherlist …), dann neu senden.", 4)
            if stoerung < VERSUCHE_STOERUNG:
                stoerung += 1
                time.sleep(2 ** stoerung)
                continue
            raise Abbruch(f"Lexware ist nicht erreichbar: {e}", 4)


def _lesen(roh: bytes, typ: str):
    if not roh:
        return None
    if "json" in typ or roh[:1] in (b"{", b"["):
        try:
            return json.loads(roh)
        except ValueError:
            pass
    if typ.startswith("application/pdf") or roh[:5] == b"%PDF-" or "xml" in typ:
        return roh
    return {"rohtext": roh.decode("utf-8", "replace")[:600]}


def fehlertext(status: int, daten, konto: str | None) -> str:
    """Übersetzt Fehler von Lexware in einen Satz mit dem Weg nach vorn."""
    if status == 401:
        try:
            laenge = len(schluessel(konto))
        except Abbruch:
            laenge = 0
        return (f"401: Lexware kennt den Schlüssel nicht (geladen: {laenge} Zeichen). Häufigste Ursache: beim Kopieren "
                "fehlt ein Zeichen. Erst die Länge prüfen, dann den Schlüssel in Lexware ansehen oder neu erzeugen.")
    if status == 402:
        return "402: Der Tarif dieses Lexware-Kontos enthält die Public API nicht."
    if status == 403:
        return ("403: Der Schlüssel darf das nicht. Er ist auf die beim Anlegen gewählten Bereiche und die Rechte "
                "seines Benutzers begrenzt. Für mehr Rechte einen neuen Schlüssel anlegen.")
    if status == 404:
        return "404: Nicht gefunden. Kennung und Belegart prüfen (eine Rechnungs-ID ist kein Angebot)."
    if status in (400, 406, 409, 415, 422):
        art = {400: "Anfrage falsch aufgebaut", 406: "Lexware lehnt die Angaben ab (Prüffehler)",
               409: "Konflikt: der Datensatz wurde inzwischen geändert (version neu lesen)",
               415: "Dateityp oder Content-Type passt nicht", 422: "Angaben sind so nicht verarbeitbar"}[status]
        zeilen = [f"{status}: {art}. Nicht einfach wiederholen, erst korrigieren."]
        if isinstance(daten, dict):
            for d in daten.get("details") or daten.get("IssueList") or []:
                if isinstance(d, dict):
                    feld = d.get("field") or d.get("source") or "?"
                    grund = d.get("violation") or d.get("i18nKey") or d.get("type") or ""
                    text = d.get("message") or ""
                    zeilen.append(f"  Feld {feld}: {grund} {text}".rstrip())
            if daten.get("message") and len(zeilen) == 1:
                zeilen.append(f"  {daten['message']}")
        return "\n".join(zeilen)
    if status == 429:
        return "429: Lexware drosselt auch nach mehreren Pausen noch. In einer Minute erneut versuchen."
    return f"{status}: Lexware meldet einen Fehler. In einer Minute erneut versuchen."


# --------------------------------------------------------------------------------------------- Hilfen
def parameter(args: list[str]) -> dict:
    p = {}
    for a in args:
        if "=" not in a:
            raise Abbruch(f"Parameter „{a}“ bitte als name=wert angeben.", 2)
        k, v = a.split("=", 1)
        p[k] = v
    return p


def suche_vorbereiten(pfad: str, params: dict) -> dict:
    """Regeln der Listen-Endpunkte, bevor etwas hinausgeht."""
    p = dict(params)
    if pfad.startswith("/contacts"):
        for k in ("name", "email"):
            if k in p:
                # Lexware: & < > als HTML kodieren; _ und % sind Platzhalter und werden mit \ geschützt
                p[k] = (p[k].replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%")
                        .replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        if "name" in p and len(p["name"]) < 3:
            raise Abbruch("Die Namenssuche braucht mindestens drei Zeichen.", 2)
    if pfad.startswith("/voucherlist"):
        if not p.get("voucherType") or not p.get("voucherStatus"):
            raise Abbruch("Die Belegliste braucht voucherType und voucherStatus, z. B. voucherType=invoice "
                          "voucherStatus=open (alle Status: voucherStatus=any).", 2)
        if "overdue" in p["voucherStatus"].split(",") and "," in p["voucherStatus"]:
            raise Abbruch("voucherStatus=overdue lässt sich nicht mit anderen Status kombinieren. "
                          "Hinweis: open enthält überfällige Belege schon.", 2)
    return p


def json_lesen(quelle: str):
    text = sys.stdin.read() if quelle == "-" else pathlib.Path(quelle).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except ValueError as e:
        raise Abbruch(f"Kein gültiges JSON in {quelle}: {e}", 2)


def feld(d, pfad: str):
    for teil in pfad.split("."):
        if isinstance(d, list):
            d = d[0] if d else None
        if not isinstance(d, dict):
            return None
        d = d.get(teil)
    return d


def ausgeben(daten, felder: str | None = None, als_csv: bool = False) -> None:
    liste = daten.get("content") if isinstance(daten, dict) and isinstance(daten.get("content"), list) else daten
    if felder:
        namen = [f.strip() for f in felder.split(",") if f.strip()]
        zeilen = liste if isinstance(liste, list) else [liste]
        zeilen = [{n: feld(z, n) for n in namen} for z in zeilen]
        if als_csv:
            out = io.StringIO()
            w = csv.DictWriter(out, fieldnames=namen, delimiter=";")
            w.writeheader()
            w.writerows(zeilen)
            print(out.getvalue(), end="")
            return
        liste = zeilen if isinstance(liste, list) else zeilen[0]
        daten = liste
    print(json.dumps(daten, indent=2, ensure_ascii=False))


def art_pfad(art: str) -> str:
    a = art.strip().lower().strip("/")
    if a in ARTEN.values():
        return a
    if a in ARTEN:
        return ARTEN[a]
    raise Abbruch(f"Unbekannte Belegart „{art}“. Möglich: {', '.join(sorted(set(ARTEN)))}", 2)


def ok_oder_abbruch(status: int, daten, konto: str | None) -> None:
    if not 200 <= status < 300:
        raise Abbruch(fehlertext(status, daten, konto), 2)


def belegdatum(tag: str) -> str:
    """Lexware liest voucherDate als Kalendertag. Mitternacht mit dem Berliner Versatz genau dieses Tages."""
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
        zone = ZoneInfo("Europe/Berlin")
    except Exception:  # ohne Zeitzonendaten: Sommerzeit grob nach EU-Regel
        zone = None
    t = datetime.strptime(tag, "%Y-%m-%d")
    if zone is not None:
        versatz = t.replace(tzinfo=zone).utcoffset()
        minuten = int(versatz.total_seconds() // 60)
    else:
        minuten = 120 if 4 <= t.month <= 9 else 60
    return f"{tag}T00:00:00.000{'+' if minuten >= 0 else '-'}{abs(minuten) // 60:02d}:{abs(minuten) % 60:02d}"


# --------------------------------------------------------------------------------------------- Befehle
def befehl_pruefen(konto):
    status, d, _ = anfrage("GET", "/profile", konto)
    ok_oder_abbruch(status, d, konto)
    info = {
        "verbunden": True,
        "firma": d.get("companyName"),
        "steuerart": d.get("taxType"),
        "kleinunternehmer": d.get("smallBusiness"),
        "funktionen": d.get("businessFeatures") or d.get("subscriptionFeatures"),
        "nur_lesen_modus": nur_lesen(),
    }
    print(json.dumps(info, indent=2, ensure_ascii=False))


def befehl_alle(pfad, params, konto, felder, als_csv, max_seiten):
    params = dict(params)
    seite = int(params.pop("page", 0))
    alles = []
    if pfad.startswith("/voucherlist") and "size" not in params:
        params["size"] = 250          # die Belegliste nimmt 250 je Seite; /articles nicht (dort 406 bei size)
    for _ in range(max_seiten):
        status, d, _ = anfrage("GET", pfad, konto, dict(params, page=seite))
        ok_oder_abbruch(status, d, konto)
        if not isinstance(d, dict) or "content" not in d:
            ausgeben(d, felder, als_csv)
            return
        alles.extend(d["content"])
        print(f"  Seite {seite + 1}/{d.get('totalPages', '?')}: {len(alles)} Einträge", file=sys.stderr)
        if d.get("last", True) or seite + 1 >= d.get("totalPages", 0):
            break
        seite += 1
    else:
        print(f"Hinweis: nach {max_seiten} Seiten abgebrochen (--max-seiten).", file=sys.stderr)
    ausgeben(alles, felder, als_csv)


def befehl_post(pfad, koerper, params, konto, festschreiben):
    if str(params.get("finalize", "")).lower() == "true" and not festschreiben:
        raise Abbruch("finalize=true schreibt den Beleg endgültig fest (Nummer, kein Löschen mehr). Gesperrt. "
                      "Nur nach ausdrücklicher Zustimmung mit --festschreiben senden.", 3)
    status, d, _ = anfrage("POST", pfad, konto, params, koerper)
    ok_oder_abbruch(status, d, konto)
    art = pfad.strip("/").split("/")[0]
    if isinstance(d, dict) and d.get("id") and art in ARTEN.values():
        d["link"] = f"{APP}/{art}/{'view' if params.get('finalize') == 'true' else 'edit'}/{d['id']}"
    print(json.dumps(d, indent=2, ensure_ascii=False))


def befehl_put(pfad, koerper, konto):
    if isinstance(koerper, dict) and "version" not in koerper:
        raise Abbruch("PUT braucht die aktuelle version im Körper (vorher per get lesen). Sonst lehnt Lexware ab.", 2)
    status, d, _ = anfrage("PUT", pfad, konto, None, koerper)
    ok_oder_abbruch(status, d, konto)
    print(json.dumps(d, indent=2, ensure_ascii=False))


def befehl_loeschen(pfad, konto, ja):
    if not any(r.match(pfad) for r in LOESCHBAR):
        raise Abbruch("Löschen ist hier nur für Artikel und Ereignis-Abos vorgesehen. Belege löscht man in Lexware.", 3)
    if not ja:
        raise Abbruch("Löschen nur mit --ja.", 3)
    status, d, _ = anfrage("DELETE", pfad, konto)
    if status not in (200, 204, 404):
        raise Abbruch(fehlertext(status, d, konto), 2)
    print(json.dumps({"geloescht": pfad, "status": status}, ensure_ascii=False))


def befehl_pdf(art, beleg_id, ziel, konto, xml=False):
    pfad = art_pfad(art)
    if xml:
        status, d, _ = anfrage("GET", f"/{pfad}/{beleg_id}/file", konto, accept="application/xml")
        ok_oder_abbruch(status, d, konto)
        roh = d if isinstance(d, bytes) else (d.get("rohtext", "") if isinstance(d, dict) else str(d)).encode()
        if b"<" not in roh[:200]:
            raise Abbruch("Lexware lieferte kein XML. Nur Rechnungen an Kontakte mit Leitweg-ID sind XRechnungen.", 2)
        pathlib.Path(ziel).write_bytes(roh)
        print(json.dumps({"datei": str(ziel), "bytes": len(roh)}, ensure_ascii=False))
        return
    status, d, _ = anfrage("GET", f"/{pfad}/{beleg_id}/file", konto, accept="application/pdf")
    if status == 409:
        raise Abbruch("409: Der Beleg ist ein Entwurf. Ein PDF gibt es erst nach dem Festschreiben in Lexware.", 2)
    if status == 200 and isinstance(d, bytes):
        pdf = d
    else:
        # älterer Weg: Dokument erzeugen lassen, dann die Datei holen (nur festgeschriebene Belege)
        status, d, _ = anfrage("GET", f"/{pfad}/{beleg_id}/document", konto)
        ok_oder_abbruch(status, d, konto)
        status, pdf, _ = anfrage("GET", f"/files/{d['documentFileId']}", konto, accept="application/pdf")
        ok_oder_abbruch(status, pdf, konto)
    if not isinstance(pdf, bytes) or pdf[:5] != b"%PDF-":
        raise Abbruch("Lexware lieferte kein PDF. Entwürfe haben noch kein PDF, erst nach dem Festschreiben.", 2)
    pathlib.Path(ziel).write_bytes(pdf)
    print(json.dumps({"datei": str(ziel), "bytes": len(pdf)}, ensure_ascii=False))


def befehl_hochladen(datei, konto, an_beleg):
    p = pathlib.Path(datei)
    inhalt = p.read_bytes()
    if len(inhalt) > DATEI_MAX:
        raise Abbruch(f"{p.name} ist {len(inhalt) / 1048576:.1f} MB groß. Lexware nimmt Belegdateien bis 5 MB.", 2)
    typ = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
    if typ not in ("application/pdf", "image/jpeg", "image/png", "application/xml", "text/xml"):
        raise Abbruch(f"Dateityp {typ} nimmt Lexware als Beleg nicht an (PDF, JPG, PNG, XML für E-Rechnungen).", 2)
    if an_beleg:
        status, d, _ = anfrage("POST", f"/vouchers/{an_beleg}/files", konto, datei=(p.name, inhalt, typ))
    else:
        status, d, _ = anfrage("POST", "/files", konto, datei=(p.name, inhalt, typ), felder={"type": "voucher"})
    ok_oder_abbruch(status, d, konto)
    print(json.dumps(d, indent=2, ensure_ascii=False))


def befehl_link(art, beleg_id, bearbeiten):
    print(f"{APP}/{art_pfad(art)}/{'edit' if bearbeiten else 'view'}/{beleg_id}")


def main(argv: list[str]) -> int:
    args = list(argv)
    def schalter(name: str) -> bool:
        if name in args:
            args.remove(name)
            return True
        return False
    def wert(name: str, vorgabe=None):
        if name in args:
            i = args.index(name)
            if i + 1 >= len(args):
                raise Abbruch(f"{name} braucht einen Wert.", 2)
            v = args[i + 1]
            del args[i:i + 2]
            return v
        return vorgabe

    try:
        konto = wert("--konto")
        felder = wert("--felder")
        max_seiten = int(wert("--max-seiten", 40))
        an_beleg = wert("--an-beleg")
        als_csv, festschreiben, ja = schalter("--csv"), schalter("--festschreiben"), schalter("--ja")
        bearbeiten, xml = schalter("--bearbeiten"), schalter("--xml")
        if not args or args[0] in ("-h", "--help", "hilfe"):
            print(__doc__)
            return 0
        befehl, rest = args[0], args[1:]
        if befehl == "pruefen":
            befehl_pruefen(konto)
        elif befehl == "get" and rest:
            status, d, _ = anfrage("GET", rest[0], konto, suche_vorbereiten(rest[0], parameter(rest[1:])))
            ok_oder_abbruch(status, d, konto)
            ausgeben(d, felder, als_csv)
        elif befehl == "alle" and rest:
            befehl_alle(rest[0], suche_vorbereiten(rest[0], parameter(rest[1:])), konto, felder, als_csv, max_seiten)
        elif befehl == "post" and len(rest) >= 2:
            befehl_post(rest[0], json_lesen(rest[1]), parameter(rest[2:]), konto, festschreiben)
        elif befehl == "put" and len(rest) == 2:
            befehl_put(rest[0], json_lesen(rest[1]), konto)
        elif befehl == "loeschen" and len(rest) == 1:
            befehl_loeschen(rest[0], konto, ja)
        elif befehl == "pdf" and len(rest) == 3:
            befehl_pdf(rest[0], rest[1], rest[2], konto, xml)
        elif befehl == "hochladen" and len(rest) == 1:
            befehl_hochladen(rest[0], konto, an_beleg)
        elif befehl == "link" and len(rest) == 2:
            befehl_link(rest[0], rest[1], bearbeiten)
        elif befehl == "datum" and len(rest) == 1:
            print(belegdatum(rest[0]))
        else:
            print(__doc__, file=sys.stderr)
            return 2
        return 0
    except Abbruch as e:
        print(str(e), file=sys.stderr)
        return e.code
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
