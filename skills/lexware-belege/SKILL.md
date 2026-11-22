---
name: lexware-belege
description: Eingangsbelege und Quittungen nach Lexware Office bringen, als Datei zur Belegerkennung (sicherer Standard) oder als fertig gebuchter Beleg mit Kategorie, Lieferant und Steuer. Mit Dublettenprüfung, Kategorien nach Namen statt fester Kennungen und nachgerechneten Summen. Verwenden bei „lade die Rechnung hoch“, „ab damit in Lexware“, „Belege aus dem Ordner nach Lexware“, „buche die Hetzner-Rechnung“, „E-Rechnung hochladen“, „welche Belege fehlen“, „Belegerfassung“.
---

# Lexware Office: Belege

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Eingangsbelege sind Buchhaltung: Was einmal gebucht ist, lässt
sich über die API weder löschen noch ohne Weiteres zurücknehmen. Deshalb gibt es zwei Wege, und der erste ist der
Standard.

## Weg 1 (Standard): Datei zur Belegerkennung

```
lexware.py hochladen rechnung-hetzner-2026-11.pdf
```

- PDF, JPG, PNG oder XML (XRechnung), höchstens 5 MB. Das Werkzeug prüft beides vorher.
- Lexware legt daraus selbst einen Beleg an, liest ihn aus und stellt ihn unter „Zu prüfen“. Der Mensch prüft dort
  Betrag, Kategorie und Lieferant und bucht. Die Antwort enthält `id` (Datei) und `voucherId` (Beleg).
- Gleiche Datei zweimal: Lexware erkennt sie und gibt die vorhandenen Kennungen zurück, es entsteht keine Dublette.
- XML, das keine gültige XRechnung ist, lehnt Lexware ab (`invalid_xrechnung`).
- Viele Dateien: nacheinander, die Drossel regelt das Tempo. Danach eine Liste: Datei, Beleg-ID, Ergebnis.

## Weg 2: fertig gebuchter Beleg

Nur wenn der Mensch es so will und alle Angaben eindeutig sind (Nummer, Datum, Lieferant, Netto, Steuer, Kategorie).

1. **Kategorie nach Namen auflösen**, nie eine Kennung fest einbauen:
   `lexware.py get /posting-categories --felder id,name,type` und nach Namen wählen (z. B. „Fremdleistungen“,
   „Internet und Telefon“). Im Zweifel den Menschen wählen lassen.
2. **Dublette prüfen:** `lexware.py get /voucherlist voucherType=purchaseinvoice voucherStatus=any voucherNumber=<nr>`
   und das Belegdatum vergleichen. Gleiche Nummer und gleiches Datum heißt: schon da. (Nummer und Betrag allein sind
   kein sicheres Merkmal.)
3. **Körper bauen und Summen prüfen** (auf den Cent; Steuer je Steuersatz summiert):

```json
{
  "type": "purchaseinvoice",
  "voucherStatus": "open",
  "voucherNumber": "R-2026-11-0042",
  "voucherDate": "2026-11-03",
  "shippingDate": "2026-11-03",
  "dueDate": "2026-11-17",
  "totalGrossAmount": 119.00,
  "totalTaxAmount": 19.00,
  "taxType": "net",
  "useCollectiveContact": true,
  "voucherItems": [ { "amount": 100.00, "taxAmount": 19.00, "taxRatePercent": 19, "categoryId": "<aus Schritt 1>" } ],
  "remark": "Server November 2026 · Kennung beleg-2026-11-0042"
}
```

4. Vorschau zeigen, nach dem Ja `lexware.py post /vouchers beleg.json`, dann die Datei dazu:
   `lexware.py hochladen rechnung.pdf --an-beleg <id>`, dann zurücklesen.

Hinweise:

- `voucherStatus: "open"` heißt gebucht. Prüfen lassen will man über Weg 1.
- `useCollectiveContact: true` bucht auf den Sammellieferanten; mit Lieferant stattdessen `"contactId": "<id>"`.
- `taxType: "gross"`: `amount` ist dann brutto.
- Beim späteren Ändern (`put /vouchers/<id>`) immer das `files`-Feld mitschicken: Ein PUT ersetzt den ganzen Beleg,
  fehlende Dateien gehen verloren.
- Belege, die mit einer Bankbuchung verknüpft oder festgeschrieben sind, lehnt Lexware beim Ändern ab.
- Bewirtung, Reisekosten, Reverse Charge (§ 13b als Empfänger): Kategorie und Steuer mit dem Menschen oder der
  Steuerberatung klären, nicht selbst festlegen.

## Nie auf dem echten Konto testen

Ein Eingangsbeleg lässt sich über die API nicht löschen und hinterlässt Spuren in der Buchhaltung. Proben nur in einem
eigenen Testkonto. Auf dem echten Konto gilt: Weg 1, oder Weg 2 erst nach Vorschau und Ja.

## Welche Belege fehlen?

Für einen Abgleich (z. B. Kontoauszug gegen Lexware) die Eingangsbelege eines Zeitraums lesen:
`lexware.py alle /voucherlist voucherType=purchaseinvoice voucherStatus=any voucherDateFrom=2026-11-01 voucherDateTo=2026-11-30 --felder voucherNumber,voucherDate,contactName,totalAmount,voucherStatus --csv`
und gegen die Liste des Menschen halten. Bankumsätze selbst liefert die API nicht.
