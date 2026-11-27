---
name: lexware-auswertungen
description: Kennzahlen aus Lexware Office auswerten, ohne Excel-Export von Hand. Umsatz je Monat, Quartal, Kunde und Jahr (netto, Gutschriften abgezogen), Angebotsquote und offene Angebotssumme, Top-Kunden, Vergleich zum Vorjahr, Export als CSV oder Tabelle, mit lokalem Zwischenspeicher für schnelle Wiederholung. Verwenden bei „wie viel Umsatz hatten wir im Oktober“, „Umsatz nach Kunden“, „Monatsüberblick“, „wie läuft das Jahr“, „Angebotsquote“, „Top 10 Kunden“, „Vergleich zum Vorjahr“, „exportiere die Rechnungen“.
---

# Lexware Office: Auswertungen

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Auswertungen lesen nur. Setze für diese Arbeit
`LEXWARE_NUR_LESEN=1`, dann kann nichts schiefgehen.

## Datengrundlage

Die Belegliste liefert je Beleg Nummer, Datum, Kunde, Status und `totalAmount` (brutto). Das Netto steht nur im
Einzelbeleg. Daraus folgt der Ablauf:

1. **Liste holen** je Belegart, ab Jahresbeginn des Vorjahres:
   `lexware.py alle /voucherlist voucherType=invoice voucherStatus=any voucherDateFrom=2025-01-01 --felder id,voucherNumber,voucherDate,contactName,totalAmount,voucherStatus,updatedDate`
   und dasselbe mit `voucherType=creditnote` (wird abgezogen).
2. **Nicht zählen:** `draft` (Entwurf) und `voided` (storniert).
3. **Netto je Beleg** aus `lexware.py get /invoices/<id> --felder totalPrice.totalNetAmount`. Bei zwei Anfragen je
   Sekunde dauern 500 Rechnungen gut vier Minuten. Deshalb:
4. **Zwischenspeicher:** Ergebnis als JSON-Datei ablegen (id, Datum, Kunde, netto, brutto, Status, `updatedDate`).
   Beim nächsten Mal nur Belege nachladen, deren `updatedDate` sich geändert hat oder die neu sind (die neue Zeit
   immer mitspeichern, auch wenn die eigenen Felder gleich bleiben), und Belege
   entfernen, die in der Liste fehlen (in Lexware gelöscht). Für den Abgleich nur geänderter Belege nimmt
   `updatedDateFrom` ein Datum ohne Uhrzeit; einen Tag Überlappung einplanen.

Sag immer dazu, auf welchem Stand die Zahlen sind („Lexware, Stand heute 14:20“).

## Kennzahlen

| Kennzahl | Rechnung |
| --- | --- |
| Umsatz netto | Σ Rechnungen netto − Σ Gutschriften netto, nach `voucherDate` (Rechnungsdatum) |
| Umsatz je Kunde | dasselbe gruppiert nach `contactName`; Top 10 mit Anteil in Prozent |
| Vorjahresvergleich | gleicher Zeitraum im Vorjahr, Abweichung in Euro und Prozent |
| Angebotsquote | angenommen ÷ (angenommen + abgelehnt) im Zeitraum, aus `voucherType=quotation` |
| offene Angebotssumme | Σ offener Angebote (brutto aus der Liste; netto über Einzelbeleg) |
| Durchschnittlicher Rechnungsbetrag | Umsatz netto ÷ Anzahl Rechnungen |

Abgrenzung, die man nennen sollte: Das ist Umsatz nach Rechnungsdatum, nicht nach Zahlungseingang. Für die
Einnahmen-Überschuss-Rechnung zählt der Zahlungseingang; das kann Lexware selbst auswerten, die API liefert dafür
keine Bankdaten.

Bei Teilrechnungen im Bau (kumuliert mit Abzugszeile) ist die Nettosumme aller Rechnungen eines Auftrags der
abgerechnete Stand. Nicht jede Teilrechnung hängt in Lexware am Angebot; Zuordnung dann über Bestellnummer oder
Kennung in der Bemerkung.

## Ausgabe

- Kurz zuerst: eine Zeile mit der Antwort („Oktober 2026: 48.210 € netto, 12 % über Oktober 2025“), dann die
  Tabelle.
- Beträge mit Tausenderpunkt und Komma, Euro-Zeichen hinten.
- Auf Wunsch CSV (`--csv`, Trennzeichen Semikolon, öffnet direkt in Excel) oder ein Diagramm, wenn die Umgebung
  eins zeichnen kann.
- Für Monatsberichte: Umsatz, offene Posten (Skill `lexware-offene-posten`), offene Angebote, drei auffällige
  Punkte (größter neuer Kunde, ältester offener Posten, auffällige Abweichung zum Vorjahr).
