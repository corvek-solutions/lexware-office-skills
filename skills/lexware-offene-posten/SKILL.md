---
name: lexware-offene-posten
description: Offene und überfällige Rechnungen aus Lexware Office auf einen Blick, je Kunde oder gesamt, mit Tagen über Fälligkeit, Netto und Brutto, Zahlstand und dem nächsten Schritt bis zur Mahnung als Entwurf. Verwenden bei „wer schuldet uns Geld“, „welche Rechnungen sind offen“, „was ist bei Müller noch offen“, „überfällige Rechnungen“, „mach eine Zahlungserinnerung“, „Mahnung für RE-…“, „hat … schon bezahlt“, „Forderungen“, „Liquidität diese Woche“.
---

# Lexware Office: offene Posten und Mahnungen

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Lesen ist ungefährlich; Mahnungen entstehen immer als Entwurf.

## Offene Rechnungen lesen

```
lexware.py alle /voucherlist voucherType=invoice voucherStatus=open \
  --felder id,voucherNumber,voucherDate,dueDate,contactName,totalAmount,openAmount,voucherStatus
```

- `open` enthält die überfälligen schon (Lexware führt sie als `overdue`). Nur überfällige: `voucherStatus=overdue`
  (nicht mit anderen Status kombinierbar).
- Je Kunde: vorher die Kontakt-ID suchen und `contactId=<id>` anhängen.
- Tage über Fälligkeit = heute − `dueDate`. Sortiere absteigend, die ältesten zuerst.
- Abschlagsrechnungen haben eigene Belegart `downpaymentinvoice`; für den vollen Stand beide abfragen.

**Ausgabe** als Tabelle mit Summe:

| Rechnung | Kunde | fällig seit | offen (brutto) | offen (netto) | Lexware |
| --- | --- | ---: | ---: | ---: | --- |
| RE-2026-0412 | Muster Bau GmbH | 34 Tage | 4.165,00 € | 3.500,00 € | [öffnen](https://app.lexware.de/permalink/invoices/view/…) |

## Zwei Dinge, die man wissen muss

1. **`openAmount` ist brutto.** Netto je Rechnung anteilig: `openAmount × totalNetAmount ÷ totalGrossAmount` (die
   Beträge aus `get /invoices/<id>`). Nicht pauschal durch 1,19 teilen: Rechnungen mit 7 %, 0 % oder § 13b stimmen
   sonst nicht.
2. **„Offen“ ist nur so gut wie der Zahlungsabgleich in Lexware.** Die API kennt keine Bankumsätze. Ist das Bankkonto
   in Lexware nicht verbunden oder sind Zahlungen nicht zugeordnet, stehen bezahlte Rechnungen weiter als offen da.
   Viele offene Rechnungen, die älter als 180 Tage sind, sind fast immer ein Zeichen dafür. Dann sag das, statt
   Zahlen als Wahrheit zu melden. Der Skill `lexware-check` misst es.

## Zahlstand einer Rechnung

`lexware.py get /payments/<rechnungs-id>` liefert `paymentStatus` (`balanced` bezahlt, `openRevenue` offen),
`openAmount`, `paidDate` und `paymentItems` (Teilzahlungen, Gutschriften). Die API zeigt den Zahlstand nur; buchen
oder zuordnen geht nur in Lexware.

## Mahnstufen

| Stufe | Wann (Vorschlag) | Ton |
| --- | --- | --- |
| Zahlungserinnerung | ab 7 Tagen über Fälligkeit | freundlich, „vielleicht übersehen“, Rechnung als PDF dabei |
| 1. Mahnung | ab 21 Tagen | sachlich, neue Frist 10 Tage |
| 2. Mahnung | ab 35 Tagen | bestimmt, Verzugszinsen und Pauschale nennen, letzte Frist |

Rahmen, ohne Rechtsberatung: Verzug tritt spätestens 30 Tage nach Fälligkeit und Zugang ein (§ 286 Abs. 3 BGB; bei
Verbrauchern nur, wenn die Rechnung darauf hinweist). Verzugszinsen: Unternehmen 9 Prozentpunkte über dem
Basiszinssatz, Verbraucher 5 (§ 288 BGB). Den aktuellen Basiszinssatz nie aus dem Gedächtnis nehmen, sondern bei der
Deutschen Bundesbank nachsehen. Gegenüber Unternehmen ist eine Pauschale von 40 € möglich (§ 288 Abs. 5 BGB). Ob und
wie gemahnt wird, entscheidet der Mensch; viele Betriebe rufen erst an.

## Mahnung als Entwurf

```
lexware.py post /dunnings mahnung.json precedingSalesVoucherId=<rechnungs-id>
```

Lexware legt Mahnungen immer als Entwurf an. Körper wie ein Beleg: `voucherDate`, `address`, `lineItems` (z. B. eine
Position Mahngebühr, wenn gewollt), `totalPrice`, `taxConditions`, `title` („Zahlungserinnerung“ oder
„1. Mahnung“), `introduction` mit Rechnungsnummer, Datum, Betrag und neuer Frist. Danach den Link nennen; Versand
passiert in Lexware. Mahnungen erscheinen nicht in der Belegliste; die ID aus der Antwort merken.

Eine Zahlungserinnerung kann statt eines Lexware-Belegs auch eine kurze E-Mail sein. Dann den Text als Entwurf
vorbereiten und das PDF der Rechnung beilegen (`lexware.py pdf invoice <id> <datei>`). Gesendet wird nur nach Ja.

## Liquidität der nächsten Tage

Offene Rechnungen nach `dueDate` gruppieren (diese Woche, nächste Woche, später, überfällig) und daneben die offenen
Eingangsbelege (`voucherType=purchaseinvoice voucherStatus=open`). Das ergibt eine einfache Vorschau der erwarteten
Ein- und Auszahlungen. Den Kontostand liefert Lexware nicht; frag danach, wenn er gebraucht wird.
