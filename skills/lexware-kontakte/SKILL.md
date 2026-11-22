---
name: lexware-kontakte
description: Kunden und Lieferanten in Lexware Office finden, sauber anlegen und pflegen, ohne Dubletten. Suche nach Name, Kundennummer oder E-Mail, Prüfung der Rechnungsadressen (die häufigste Ursache abgelehnter Rechnungen und Angebote), Anlegen von Firmen und Personen mit Ansprechpartnern, Ändern mit Versionsprüfung. Verwenden bei „leg den Kunden an“, „gibt es Müller schon in Lexware“, „neuer Lieferant“, „Kundennummer von …“, „ändere die Adresse“, „finde den Kontakt“, und immer, bevor ein Beleg an einen Kontakt geht.
---

# Lexware Office: Kontakte

Werkzeug: `../lexware-grundlagen/scripts/lexware.py` (Regeln siehe Skill `lexware-grundlagen`).

## Suchen

| Suche | Aufruf |
| --- | --- |
| Name (mindestens drei Zeichen, Teiltreffer) | `lexware.py get /contacts name=Muster --felder id,roles.customer.number,company.name,person.lastName,archived` |
| Kundennummer | `lexware.py get /contacts number=10023` |
| E-Mail | `lexware.py get /contacts email=info@muster.de` |
| nur Kunden oder nur Lieferanten | zusätzlich `customer=true` oder `vendor=true` |

- Das Werkzeug kodiert `&`, `<`, `>` in der Suche als HTML, wie Lexware es verlangt („Müller & Söhne“ findet sonst
  nichts).
- Firmen stehen unter `company.name`, Personen unter `person.firstName` und `person.lastName`.
- Die Kundennummer steht in `roles.customer.number`, die Lieferantennummer in `roles.vendor.number`. Lexware vergibt
  sie selbst.
- Archivierte Kontakte (`archived: true`) nie für neue Belege verwenden, sondern nachfragen.
- Mehrere Treffer: alle zeigen (Nummer, Name, Ort) und fragen. Nie den ersten nehmen.

## Die Rechnungsadresse entscheidet

Jeder Beleg mit bloßer `contactId` verlangt beim Kontakt **genau eine** Rechnungsadresse
(`addresses.billing`). Sonst lehnt Lexware mit 406 ab: „Referenced contact needs to have exactly one billing address,
but 2 addresses were found“ (oder 0).

| Rechnungsadressen | Im Beleg |
| --- | --- |
| genau eine | `"address": { "contactId": "<id>" }` reicht |
| mehrere | Mensch wählt; dann die Adresse ausgeschrieben mitgeben: `{ "contactId", "name", "supplement", "street", "zip", "city", "countryCode" }`. Der Kunde bleibt verknüpft |
| keine | erst Adresse ergänzen (in Lexware) oder ausgeschrieben mitgeben |

Wichtig: Kontakte mit mehr als einer Rechnungsadresse lassen sich über die API **nicht ändern**. Bereinigen nur in
Lexware selbst. Der Skill `lexware-check` findet sie alle.

## Anlegen

Vorher immer nach Dubletten suchen: Name ohne Rechtsform (GmbH, UG, e.K., & Co. KG) und ohne Leerzeichen
vergleichen, dazu E-Mail und Postleitzahl. Ein Treffer heißt: zeigen und fragen.

Firma als Kunde, mit Ansprechpartner:

```json
{
  "version": 0,
  "roles": { "customer": {} },
  "company": {
    "name": "Muster Bau GmbH",
    "contactPersons": [ { "salutation": "Frau", "firstName": "Anna", "lastName": "Beispiel",
                          "emailAddress": "a.beispiel@muster-bau.de", "primary": true } ]
  },
  "addresses": { "billing": [ { "street": "Hauptstraße 1", "zip": "60311", "city": "Frankfurt am Main",
                                "countryCode": "DE" } ] },
  "emailAddresses": { "business": [ "rechnung@muster-bau.de" ] },
  "note": "angelegt aus dem Chat"
}
```

`lexware.py post /contacts kontakt.json`, dann zurücklesen und die vergebene Kundennummer nennen.

- Person statt Firma: `"person": { "salutation": "Herr", "firstName": "…", "lastName": "…" }` statt `company`.
- Lieferant: `"roles": { "vendor": {} }`; beides geht zusammen.
- Bauleistungen nach § 13b UStG an diesen Kunden: `"company": { …, "allowTaxFreeInvoices": true }`, sonst lehnt
  Lexware später die Rechnung mit Steuerart `constructionService13b` ab.
- Umsatzsteuer-ID und Steuernummer: `company.vatRegistrationId`, `company.taxNumber`.
- Ländercodes nach ISO, Deutschland `DE`.

## Ändern

1. `lexware.py get /contacts/<id> > kontakt.json` (enthält die aktuelle `version`).
2. Nur die gewünschten Felder ändern, alles andere unverändert lassen. Das Werkzeug lehnt einen Körper ohne `version`
   ab.
3. `lexware.py put /contacts/<id> kontakt.json`, dann zurücklesen.

409 heißt: jemand hat den Kontakt inzwischen geändert. Neu lesen, Änderung erneut anwenden.

## Löschen

Geht über die API nicht. In Lexware archivieren.
