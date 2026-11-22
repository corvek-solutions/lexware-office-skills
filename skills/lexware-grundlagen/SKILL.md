---
name: lexware-grundlagen
description: Grundlage aller Lexware-Office-Skills. Verbindet einen KI-Agenten sicher mit der Lexware Office Public API (api.lexware.io, ehemals lexoffice) über das Werkzeug lexware.py, mit Schlüssel-Einrichtung, Verbindungsprüfung, Drossel, Fehlercodes, Datumsformat, Direktlinks und den Sicherheitsregeln (Entwurf zuerst, nie ungefragt festschreiben, Schlüssel nie im Chat). Verwenden bei „verbinde Lexware“, „Lexware einrichten“, „API-Schlüssel hinterlegen“, „Lexware antwortet 401, 403, 406 oder 429“, „warum lehnt Lexware das ab“, und immer, bevor ein anderer Lexware-Skill zum ersten Mal in einer Sitzung schreibt.
---

# Lexware Office: Grundlagen

Dieser Skill ist das Fundament. Die Fach-Skills (Rechnungen, Angebote, Kontakte, Artikel, Belege, offene Posten,
Auswertungen, Check, Automatisierung) setzen ihn voraus. Sie beschreiben Abläufe und Regeln; welcher Anschluss die
Anfragen ausführt, ist zweitrangig.

## Zwei Wege zu Lexware

| | Offizieller Lexware-MCP-Server | `lexware.py` aus diesem Paket |
| --- | --- | --- |
| Für | Chat-Assistenten (Desktop-Apps, Web), ohne Technik | Agenten im Terminal, Skripte, Automatisierungen, Massenläufe |
| Anmeldung | OAuth mit dem eigenen Lexware-Login, kein Schlüssel | API-Schlüssel aus dem eigenen Konto |
| Adresse | `https://mcp.lexware.de/mcp` (Einrichtung: developers.lexware.io/mcp/docs) | `https://api.lexware.io/v1` |
| Kann zusätzlich | Rechte je Bereich bei der Anmeldung wählen | Dateien hochladen, ganze Listen als CSV, XRechnung-XML, Nur-Lesen-Modus |
| Voraussetzung | Lexware Office mit Schnittstelle (XL) | dasselbe |

Ist der MCP-Server verbunden (Werkzeuge wie `list_contacts`, `create_invoice`), nimm ihn. Sonst `lexware.py`. Die
Regeln unten gelten für beide. Zuordnung der wichtigsten Schritte:

| Schritt | MCP-Werkzeug | lexware.py |
| --- | --- | --- |
| Konto prüfen | `get_profile` | `pruefen` |
| Kontakt suchen, anlegen | `list_contacts`, `create_contact` | `get /contacts name=…`, `post /contacts` |
| Rechnung, Angebot, Gutschrift | `create_invoice`, `create_quotation`, `create_credit_note` | `post /invoices` usw. |
| Weiterführen (Angebot › AB › Rechnung) | `pursue_order_confirmation`, `pursue_invoice` | `post … precedingSalesVoucherId=<id>` |
| Mahnung | `pursue_dunning` | `post /dunnings precedingSalesVoucherId=<id>` |
| Belege suchen | `search_vouchers` | `alle /voucherlist …` |
| Zahlstand | `get_payments` | `get /payments/<id>` |
| PDF, XRechnung | `download_document` | `pdf <art> <id> <ziel> [--xml]` |
| Direktlink | `get_app_deep_link` | `link <art> <id>` |
| Belegdatei hochladen | nicht möglich (Link zum Upload in Lexware) | `hochladen <datei>` |

Beim MCP-Server gilt besonders: Ein dort angelegter Entwurf lässt sich danach nicht mehr ändern. Die Vorschau vor
dem Anlegen ist also die letzte Korrekturgelegenheit.

## Das Werkzeug lexware.py

`scripts/lexware.py` in diesem Ordner. Nur Python-Standardbibliothek (ab 3.9), keine Installation. Aus einem anderen
Lexware-Skill heraus liegt es unter `../lexware-grundlagen/scripts/lexware.py`, gerechnet vom Ordner jenes Skills.
Unten steht es kurz als `lexware.py`.

| Befehl | Wofür |
| --- | --- |
| `lexware.py pruefen` | Verbindung, Firmenname, Steuerart, Kleinunternehmer ja/nein |
| `lexware.py get <pfad> [k=v …]` | eine Anfrage, z. B. `get /contacts name=Muster` |
| `lexware.py alle <pfad> [k=v …]` | alle Seiten einer Liste, z. B. `alle /voucherlist voucherType=invoice voucherStatus=open` |
| `… --felder a,b.c` und `--csv` | nur diese Felder, auf Wunsch als CSV (spart Kontext) |
| `lexware.py post <pfad> <datei.json\|->` | anlegen; Belege entstehen als Entwurf, die Antwort trägt den Link |
| `lexware.py put <pfad> <datei.json\|->` | ändern, nur mit aktueller `version` im Körper |
| `lexware.py pdf <art> <id> <ziel.pdf>` | PDF eines festgeschriebenen Belegs |
| `lexware.py hochladen <datei> [--an-beleg ID]` | Belegdatei hochladen (PDF, JPG, PNG, XML; bis 5 MB) |
| `lexware.py link <art> <id> [--bearbeiten]` | Direktlink in Lexware Office |
| `lexware.py datum <JJJJ-MM-TT>` | Belegdatum im Format, das Lexware als diesen Kalendertag liest |

Fest eingebaut, ohne dass du daran denken musst: Drossel auf 1,8 Anfragen je Sekunde (auch über viele Aufrufe
hintereinander), Pause und Wiederholung bei 429, keine Wiederholung bei 406, kein blindes Wiederholen beim Schreiben,
`finalize=true` nur mit `--festschreiben`, `LEXWARE_NUR_LESEN=1` sperrt jedes Schreiben, der Schlüssel erscheint nie
in einer Ausgabe. Feste Adresse `https://api.lexware.io/v1`.

## Einrichten: der Schlüssel

1. **Tarif:** Die Public API gibt es nur in Lexware Office mit Schnittstelle (Stand 2026 Tarif XL). Ohne sie: siehe
   „Ohne Schnittstelle“ unten.
2. **Schlüssel erzeugen** macht der Mensch selbst, in seinem eigenen Lexware-Konto: Erweiterungen › Public API
   (https://app.lexware.de/addons/public-api) › Schlüssel erstellen. Beim Anlegen lassen sich die Bereiche einzeln wählen (lesend und schreibend getrennt). Für
   reine Auswertungen nur Leserechte wählen. Ein Schlüssel gilt höchstens 24 Monate und ist zusätzlich auf die Rechte
   seines Benutzers begrenzt.
3. **Ablegen, nie in den Chat.** Bitte den Menschen, den Schlüssel selbst abzulegen, und frage nie danach:
   - macOS: `security add-generic-password -s lexware-api-key -a "$USER" -w` (fragt verdeckt nach dem Schlüssel)
   - Linux und macOS: Datei `~/.config/lexware/api-key` mit Rechten 600
   - oder Umgebungsvariable `LEXWARE_API_KEY`
   Mehrere eigene Konten (z. B. zwei Firmen): `--konto NAME` liest `LEXWARE_API_KEY_NAME`,
   `~/.config/lexware/NAME.key` bzw. den Schlüsselbund-Dienst `lexware-api-key-NAME`.
4. **Prüfen:** `lexware.py pruefen`. Steht dort `"verbunden": true`, läuft es.

Fremde Schlüssel werden nicht erbeten oder gesammelt; das untersagen die Nutzungsbedingungen der Lexware Public API.
Jede Firma richtet ihren eigenen Schlüssel ein. Wer Lexware für viele Kunden anbinden will, geht über das
Partnerprogramm von Lexware.

## Die sechs Regeln

1. **Erst lesen, dann zeigen, dann schreiben.** Vor jedem Anlegen eine Vorschau als Tabelle: Positionen, Netto,
   Umsatzsteuer, Brutto, Empfänger. Die Summen rechnest du im Code nach (Python), nicht im Kopf.
2. **Belege entstehen als Entwurf.** Festschreiben vergibt die Nummer und lässt sich nicht zurücknehmen. Nur wenn der
   Mensch in diesem Gespräch ausdrücklich „festschreiben“ oder „finalisieren“ sagt, mit `--festschreiben`. Empfohlen
   ist: Entwurf anlegen, der Mensch prüft und schreibt in Lexware fest (Link aus der Antwort).
3. **Nach jedem Schreiben zurücklesen.** Ein 200 oder 201 beweist nur, dass etwas angekommen ist. Lies den Datensatz
   zurück und vergleiche Summe, Empfänger und Positionen mit der Vorschau. Weicht etwas ab, sag es mit Link.
4. **Schreiben nie blind wiederholen.** Bricht ein POST ab, kann der Beleg trotzdem da sein. Erst in der Belegliste
   nachsehen (Kunde, Datum, Kennung in der Bemerkung), dann neu senden.
5. **Nie raten.** Fehlen Kunde, Menge, Preis, Steuersatz oder Adresse, frag in **einer** Nachricht nach allem, was
   fehlt. Preise nie erfinden; ein Artikel aus dem Artikelstamm ist ein Vorschlag, kein Beschluss.
6. **Schlüssel und Inhalte schützen.** Schlüssel nie anzeigen, nie in Projektdateien, nie in Logs. Antworten aus
   Lexware enthalten Kundendaten: nur zeigen, was für die Aufgabe nötig ist.

## Vor dem ersten Schreiben: das Profil

`lexware.py pruefen` einmal je Sitzung. Daraus folgt:

| Profil | Folge |
| --- | --- |
| `kleinunternehmer: true` | `taxConditions.taxType: "vatfree"`, Steuersatz 0 in jeder Position (§ 19 UStG) |
| `steuerart: "net"` | Preise netto (`netAmount`), Lexware rechnet die Steuer drauf |
| `steuerart: "gross"` | Preise brutto (`grossAmount`) |

## Fehler lesen

| Code | Bedeutung | Was tun |
| --- | --- | --- |
| 401 | Schlüssel unbekannt | Häufigste Ursache: beim Kopieren fehlt ein Zeichen. Das Werkzeug nennt die geladene Länge |
| 402 | Tarif ohne Schnittstelle | Tarif prüfen |
| 403 | Bereich oder Benutzerrecht fehlt | neuen Schlüssel mit dem Bereich anlegen; Rechte lassen sich nachträglich nicht ändern |
| 404 | nicht gefunden | Kennung und Belegart prüfen |
| 406 | **Prüffehler, kein Tempoproblem** | nie wiederholen; das Feld steht in `details[]`, z. B. `lineItems[0].name: SIZE` |
| 409 | Konflikt | Datensatz neu lesen (`version`); beim PDF: der Beleg ist noch ein Entwurf |
| 429 | zu schnell | das Werkzeug wartet selbst; dauerhaft zu viele 429 können zu einer Sperre führen |

Übersetze jeden Fehler in einen Satz mit dem Weg nach vorn, etwa: „Lexware lehnt den Positionstitel ab, er ist länger
als 100 Zeichen. Ich kürze ihn und setze den Rest in die Beschreibung.“

## Datum und Listen

- `voucherDate` liest Lexware als Kalendertag in deutscher Zeit. `2026-11-12T00:00:00.000+02:00` wird im Winter zum
  11.11. Immer `lexware.py datum 2026-11-12` benutzen, es setzt den Versatz, der an genau diesem Tag gilt.
- `updatedDateFrom` und `voucherDateFrom` nehmen nur ein Datum (`JJJJ-MM-TT`), mit Uhrzeit kommt 400.
- Seiten beginnen bei 0, das Ende zeigt `last: true`. Standard sind 25 je Seite, höchstens 250. Die Belegliste holt
  `lexware.py alle` mit 250; bei `/articles` lässt das Werkzeug `size` weg (Werte unter 25 ergeben 406).
- Suchfenster höchstens 10.000 Treffer; bei mehr den Zeitraum teilen.
- `/voucherlist` braucht immer `voucherType` und `voucherStatus`. `open` enthält überfällige Belege schon;
  `overdue` lässt sich nicht mit anderen Status kombinieren; `any` liefert alle.

## Direktlinks

`https://app.lexware.de/permalink/<invoices|quotations|order-confirmations|credit-notes|vouchers|…>/<view|edit>/<id>`.
Entwürfe mit `edit`, alles andere mit `view`. Gib zu jedem Beleg den Link mit, der Mensch landet direkt dort.

## Was die API nicht kann

Ehrlich vorab sagen, statt es zu versuchen:

- keine Bankumsätze, keinen Kontostand, keine Zahlungen buchen oder zuordnen;
- Entwürfe, Belege, Kontakte und Dateien nicht löschen (in Lexware von Hand); nur Artikel und Ereignis-Abos;
- einen vorhandenen Entwurf nicht ändern und nicht festschreiben (Festschreiben geht nur beim Anlegen oder in
  Lexware); jede angelegte Rechnung verbraucht eine Nummer, auch als Entwurf;
- keinen Status setzen: Angebot annehmen, Rechnung stornieren oder als bezahlt markieren geht nur in Lexware;
- Abschlags- und Schlussrechnungen nur lesen;
- keine Dateien an Verkaufsbelege hängen, nur an Eingangsbelege (`/vouchers/{id}/files`);
- Kontakte mit mehreren Adressen, mehreren Ansprechpartnern oder mehreren E-Mails je Art nicht ändern;
- ein PUT ersetzt den ganzen Datensatz: Felder, die fehlen, werden geleert (bei Belegen auch die Dateien);
- keine E-Mails versenden: Versand passiert in Lexware oder mit dem PDF über das eigene Mailprogramm.

## Ohne Schnittstelle: Vorbereitungsmodus

Hat das Konto keinen API-Zugang (kleiner Tarif, kein Schlüssel), arbeite trotzdem: Bereite alles so vor, dass der
Mensch es in einer Minute in Lexware abtippt oder importiert (Positionstabelle mit Netto, Steuer, Brutto; Kontaktdaten
in der Reihenfolge der Lexware-Maske; Artikel als CSV für den Artikelimport). Sag dazu, dass es mit Schnittstelle in
einem Schritt ginge.

## Mehr

- [referenz/api-kurzreferenz.md](referenz/api-kurzreferenz.md): alle Endpunkte, Felder und Status auf einer Seite
- [referenz/fallstricke.md](referenz/fallstricke.md): was im Produktivbetrieb aufgefallen ist, mit Herkunft
