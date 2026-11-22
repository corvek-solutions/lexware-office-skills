---
name: lexware-rechnungen
description: Rechnungen und Gutschriften in Lexware Office aus einem Satz erstellen, als Entwurf mit Vorschau, nachgerechneten Summen und Direktlink. Kennt Kleinunternehmer (§ 19 UStG), Bauleistungen (§ 13b UStG), Leistungszeitraum, Rechnungsadressen, Rechnung aus Angebot oder Auftragsbestätigung und das PDF nach dem Festschreiben. Verwenden bei „schreib eine Rechnung an …“, „stell Müller 8 Stunden Beratung in Rechnung“, „Rechnung aus dem Angebot AG-…“, „Gutschrift für …“, „Rechnung für Oktober“, „mach die Rechnung fertig“, „PDF der Rechnung RE-…“.
---

# Lexware Office: Rechnungen

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Grundregeln aus `lexware-grundlagen` gelten: Vorschau zuerst,
Entwurf statt Festschreiben, zurücklesen, nie raten.

## Ablauf: Rechnung aus einem Satz

**Beispiel:** „Schreib der Muster Bau GmbH eine Rechnung über 12 Stunden Bauleitung à 85 € für Oktober.“

1. **Zerlegen:** Empfänger (Muster Bau GmbH), Positionen (12 Std. Bauleitung, 85,00 € netto je Std.), Leistungszeitraum
   (01.10. bis 31.10.), Rechnungsdatum (heute). Netto oder brutto gemeint? Im Geschäftsverkehr ist ein Preis ohne
   Zusatz netto; im Zweifel fragen.
2. **Was fehlt, in einer Nachricht fragen:** Menge, Preis, Steuersatz, Leistungsdatum, abweichende Adresse. Preise
   nie erfinden. Kennt der Artikelstamm die Leistung (`get /articles`), den Preis als Vorschlag nennen.
3. **Profil** (einmal je Sitzung, `lexware.py pruefen`): Kleinunternehmer heißt `taxType: "vatfree"` und 0 % in jeder
   Position.
4. **Kontakt** mit Skill `lexware-kontakte` finden. Genau ein Treffer, nicht archiviert. Rechnungsadressen zählen:
   eine heißt `contactId` reicht, mehrere heißt Mensch wählt, Adresse ausgeschrieben mitgeben.
5. **Vorschau zeigen**, Summen im Code gerechnet, je Position auf Cent gerundet:

   | Pos. | Leistung | Menge | Einheit | Einzel netto | Gesamt netto |
   | --- | --- | ---: | --- | ---: | ---: |
   | 1 | Bauleitung Oktober 2026 | 12 | Std. | 85,00 € | 1.020,00 € |
   | | | | | **Netto** | **1.020,00 €** |
   | | | | | USt 19 % | 193,80 € |
   | | | | | **Brutto** | **1.213,80 €** |

   Dazu Empfänger mit Adresse, Rechnungsdatum, Leistungszeitraum, Zahlungsziel. Frage: „Als Entwurf anlegen?“
6. **Anlegen** nach dem Ja: `lexware.py post /invoices rechnung.json`. Die Antwort trägt `id` und den Link zum
   Bearbeiten.
7. **Zurücklesen:** `lexware.py get /invoices/<id> --felder voucherStatus,totalPrice.totalNetAmount,totalPrice.totalGrossAmount,address.name`.
   Weicht die Summe ab (Rundung), mit beiden Beträgen und Link melden.
8. **Abschluss:** „Der Entwurf liegt in Lexware: <Link>. Dort prüfen, festschreiben und versenden.“

## Der Körper

```json
{
  "voucherDate": "2026-11-03T00:00:00.000+01:00",
  "address": { "contactId": "3f2b…" },
  "lineItems": [
    { "type": "custom", "name": "Bauleitung Oktober 2026", "description": "Koordination der Gewerke, Baustellentermine",
      "quantity": 12, "unitName": "Std.",
      "unitPrice": { "currency": "EUR", "netAmount": 85.00, "taxRatePercentage": 19 },
      "discountPercentage": 0 }
  ],
  "totalPrice": { "currency": "EUR" },
  "taxConditions": { "taxType": "net" },
  "shippingConditions": { "shippingType": "serviceperiod",
                          "shippingDate": "2026-10-01T00:00:00.000+02:00",
                          "shippingEndDate": "2026-10-31T00:00:00.000+01:00" },
  "title": "Rechnung",
  "introduction": "Für unsere Leistungen im Oktober stellen wir Ihnen in Rechnung:",
  "remark": "Vielen Dank für die gute Zusammenarbeit."
}
```

- Jedes Datum mit `lexware.py datum JJJJ-MM-TT` bauen (der Versatz wechselt mit der Sommerzeit, siehe oben).
- `lineItems[].type`: `custom` (freie Position), `service` oder `material` (mit Artikel-`id`, aber alle Felder
  trotzdem selbst mitschicken), `text` (nur Text, z. B. als Kopfzeile „Objekt Hauptstraße 1“).
- `name` laut Doku bis 255 Zeichen; lange Texte trotzdem in `description`, das liest sich im PDF besser. Höchstens
  300 Positionen, nur Euro. `title` bis 25 Zeichen, `introduction` und `remark` bis 2000.
- Leistungsdatum gehört auf jede Rechnung: `shippingType` `service` (ein Tag) oder `serviceperiod` (Zeitraum), bei
  Waren `delivery` oder `deliveryperiod`, jeweils mit `shippingDate` (und `shippingEndDate`).
- Ohne `paymentConditions` gilt das Zahlungsziel aus den Lexware-Einstellungen; das ist meist gewollt.
- Brutto-Konten (`steuerart: gross`): `grossAmount` statt `netAmount`, `taxType: "gross"`.

## Sonderfälle

| Fall | So |
| --- | --- |
| Kleinunternehmer | `taxType: "vatfree"`, `taxRatePercentage: 0`; im Entwurf prüfen, dass der Hinweis auf § 19 UStG im Beleg steht |
| Bauleistung an Bauunternehmer (§ 13b UStG) | `taxType: "constructionService13b"`, 0 %; der Kontakt braucht `company.allowTaxFreeInvoices: true`; ob § 13b greift, entscheidet der Mensch, nicht der Agent |
| Lieferung oder Leistung ins EU-Ausland | `intraCommunitySupply` bzw. `thirdPartyCountryService`, `thirdPartyCountryDelivery`; USt-ID des Kunden muss im Kontakt stehen |
| Rechnung aus Angebot oder Auftragsbestätigung | `lexware.py post /invoices rechnung.json precedingSalesVoucherId=<id>`; der Vorgänger muss festgeschrieben sein. Angebote mit optionalen oder alternativen Positionen lehnt Lexware als Vorgänger ab (406). Positionen ausdrücklich mitschicken |
| Gutschrift | `lexware.py post /credit-notes gutschrift.json precedingSalesVoucherId=<rechnung>`, Beträge positiv. Eine Gutschrift zu einer Rechnung gilt sofort als ausgeglichen und mindert den offenen Betrag der Rechnung; die Rechnung darf kein Entwurf sein |
| Abschlags- und Schlussrechnungen | über die API nur lesbar (`/down-payment-invoices/{id}`, Schlussrechnung erkennbar an `closingInvoice`); angelegt werden sie in Lexware. Bei Teilrechnungen im Bau ist kumuliert mit Abzugszeile üblich: dann ist die Summe aller Rechnungen eines Angebots der abgerechnete Stand |
| XRechnung (öffentliche Auftraggeber) | `taxType: "net"`, der Kontakt trägt Leitweg-ID (`buyerReference`) und Lieferantennummer beim Kunden (`vendorNumberAtCustomer`); jede Position mit Menge, Einheit, Name. Das XML: `lexware.py pdf invoice <id> rechnung.xml --xml`. Das PDF einer XRechnung ist nur eine Ansicht, keine E-Rechnung |
| ZUGFeRD | stellt Lexware selbst ein (Profil EN16931, nur lesbar); vor dem Festschreiben in Lexware prüfen |

## Festschreiben und PDF

- Empfohlen: der Mensch schreibt in Lexware fest (Link). Ein vorhandener Entwurf lässt sich über die API weder
  festschreiben noch ändern noch löschen; Status (storniert, bezahlt) setzt die API nie.
- Jede über die API angelegte Rechnung verbraucht eine Nummer, auch als Entwurf. Deshalb nie „zum Ausprobieren“
  anlegen, sondern erst nach dem Ja zur Vorschau.
- Will der Mensch es direkt („ja, gleich festschreiben“), nach der Vorschau mit
  `lexware.py post /invoices rechnung.json finalize=true --festschreiben`. Danach ist die Nummer vergeben, die Rechnung
  nicht mehr löschbar, Korrektur nur per Gutschrift oder Storno in Lexware.
- PDF: `lexware.py pdf invoice <id> RE-2026-0042.pdf`. Ein Entwurf hat kein PDF (409).
- Vorsicht in der Oberfläche: Der Druckdialog steht auf „Fertigstellen und drucken“; wer nur ansehen will, wählt
  „Als Entwurf drucken“.

## Nicht tun

- Keine Rechnung ohne Vorschau und Ja.
- Kein `lineItems: []`: Lexware legt dann einen Entwurf mit 0 € an, der nur in der Oberfläche löschbar ist.
- Keine Steuerberatung. Steuerart und Steuersatz bei Unklarheit beim Menschen klären, nicht festlegen.
