---
name: lexware-angebote
description: Angebote in Lexware Office erstellen und weiterführen, aus einem Satz, aus dem Artikelstamm oder aus dem PDF-Angebot eines Nachunternehmers mit Aufschlag (je Position eingerechnet oder als Handling Fee). Mit Projektkopf, Leistungsort, Rechnungsadressen-Prüfung, nachgerechneten Summen und dem Weg Angebot › Auftragsbestätigung › Rechnung. Verwenden bei „mach ein Angebot für …“, „Angebot aus dem PDF vom Nachunternehmer mit 15 % drauf“, „Angebot aus dem Leistungsverzeichnis“, „welche Angebote sind offen“, „Auftragsbestätigung zum Angebot AG-…“, „Angebotsquote“.
---

# Lexware Office: Angebote

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Es gelten die Regeln aus `lexware-grundlagen`. Der Körper eines
Angebots gleicht dem einer Rechnung (siehe `lexware-rechnungen`), mit drei Unterschieden: Endpunkt `/quotations`,
zusätzlich `expirationDate` (gültig bis), kein Leistungsdatum nötig.

## Drei Wege zum Angebot

**1. Aus einem Satz.** „Angebot an Muster Bau: 40 m² Fliesen verlegen à 48 €, Material 1.250 € pauschal.“ Ablauf wie
bei Rechnungen: zerlegen, Fehlendes in einer Nachricht fragen, Vorschau, Ja, Entwurf, zurücklesen, Link.

**2. Aus dem Artikelstamm.** Positionsnummern oder Stichworte gegen `/articles` suchen
(`lexware.py get /articles articleNumber=LV-01.02.001`). Titel, Langtext, Einheit und Preis aus dem Artikel in die
Position übernehmen. Wichtig: Auch mit Artikel-`id` übernimmt die API **nichts** von selbst; alle Felder mitschicken.

**3. Aus dem Angebot eines Nachunternehmers, mit Aufschlag.** Der häufigste Fall im Bau und im Gebäudebetrieb:
Ein Nachunternehmer schickt ein PDF, daraus wird das eigene Angebot an den Kunden.

1. PDF lesen: jede Position mit Nummer, Text, Menge, Einheit, Einzelpreis netto. Summe des PDFs notieren.
2. Eigene Summe der gelesenen Positionen gegen die Summe im PDF prüfen. Weicht sie ab, nicht weiterrechnen, sondern
   die Abweichung zeigen (meist eine überlesene Position oder ein Zuschlag).
3. Aufschlag nach Wahl des Menschen:

| Art | Rechnung | Wann |
| --- | --- | --- |
| **eingerechnet** | jeder Einzelpreis × (1 + Aufschlag), je Position kaufmännisch auf Cent gerundet | eigenes Angebot; der Kunde sieht nur den Endpreis |
| **Handling Fee** | Positionen unverändert, dazu eine Position „Handling Fee N %“ mit N % der Zwischensumme | Weiterberechnung mit offen ausgewiesener Gebühr |

4. Beim eingerechneten Aufschlag dürfen Name und Angebotsnummer des Nachunternehmers **nirgends** stehen: nicht in
   Positionen, nicht in Einleitung, nicht in der Bemerkung. Vor dem Senden danach suchen.
5. Rechnen mit `python3 beispiele/aufschlag.py positionen.json 15` (eingerechnet) oder `… 15 --fee` (Handling Fee):
   liefert die fertigen `lineItems` und auf stderr Einkauf, Aufschlag und Angebotssumme. Die beiden Arten ergeben
   wegen der Rundung je Position wenige Cent Unterschied; das ist richtig so.
6. Vorschau mit beiden Summen (Einkauf, Angebot) und dem Aufschlag in Euro. Nach dem Ja anlegen und zurücklesen:
   Rechnet Lexware die Summe anders (Rundung), beide Beträge nennen.

## Bewährte Form

```json
{
  "voucherDate": "2026-11-23T00:00:00.000+01:00",
  "expirationDate": "2026-12-23T00:00:00.000+01:00",
  "address": { "contactId": "3f2b…" },
  "lineItems": [
    { "type": "text", "name": "Objekt Hauptstraße 1, 60311 Frankfurt", "description": "Sanierung Bad 2. OG links" },
    { "type": "custom", "name": "Fliesen verlegen", "quantity": 40, "unitName": "m²",
      "unitPrice": { "currency": "EUR", "netAmount": 48.00, "taxRatePercentage": 19 }, "discountPercentage": 0 }
  ],
  "totalPrice": { "currency": "EUR" },
  "taxConditions": { "taxType": "net" },
  "title": "Angebot",
  "introduction": "Leistungsort: Hauptstraße 1, 60311 Frankfurt.\nGerne bieten wir Ihnen an:",
  "remark": "Wir freuen uns auf Ihren Auftrag.\nVorgang 2026-117"
}
```

- **`address` ist die Rechnungsanschrift, nicht der Leistungsort.** Bei Hausverwaltungen steht dort die Verwaltung,
  nicht das Objekt. Den Leistungsort deshalb als erste Textposition und in die Einleitung schreiben. Wer später
  Angebote auswertet, liest den Ort aus `introduction` oder der Textposition, nicht aus `address`.
- **Kennung in der Bemerkung** (z. B. „Vorgang 2026-117“): So findet eine Automatisierung das Angebot später wieder,
  und ein abgebrochener Versuch lässt sich prüfen, bevor neu angelegt wird.
- **Rechnungsadressen:** Hat der Kunde mehrere, Adresse ausgeschrieben mitgeben (siehe `lexware-kontakte`), sonst 406.
- **Datum:** `lexware.py datum` benutzen. Ein fest eingetragenes `+02:00` legt im Winter jedes Angebot auf den Vortag.
- **Nie `lineItems: []`:** legt einen nummerierten Entwurf mit 0 € an, der nur in der Oberfläche löschbar ist.
- **Optionale Positionen** (`optional: true`) und Alternativen blockieren später das Weiterführen zur Rechnung über die
  API. Nur setzen, wenn der Mensch es will, und dazusagen.

## Weiterführen

| Schritt | Aufruf | Voraussetzung |
| --- | --- | --- |
| Auftragsbestätigung | `lexware.py post /order-confirmations ab.json precedingSalesVoucherId=<angebot>` | Angebot festgeschrieben |
| Rechnung | `lexware.py post /invoices re.json precedingSalesVoucherId=<angebot oder ab>` | Vorgänger festgeschrieben, keine Entwürfe |

Positionen immer ausdrücklich mitschicken. Nicht beauftragte Positionen vorher mit dem Menschen klären und weglassen.

## Angebote lesen und auswerten

- Offene Angebote: `lexware.py alle /voucherlist voucherType=quotation voucherStatus=open --felder voucherNumber,voucherDate,contactName,totalAmount,voucherStatus`
  (`open` enthält auch abgelaufene, die Lexware als `overdue` führt; oft sind das zwei Drittel des offenen Bestands).
- Angenommen oder abgelehnt setzt der Mensch in Lexware; die API kann den Status nicht ändern.
- Angebotsquote: angenommen ÷ (angenommen + abgelehnt), Zeitraum über `voucherDateFrom`. Mehr im Skill
  `lexware-auswertungen`.
- PDF eines festgeschriebenen Angebots: `lexware.py pdf quotation <id> AG-0815.pdf`.
