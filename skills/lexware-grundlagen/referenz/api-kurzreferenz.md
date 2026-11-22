# Lexware Office API: Kurzreferenz

Stand November 2026. Quelle: https://developers.lexware.io/docs/ und Praxis. Alle Pfade unter
`https://api.lexware.io/v1`, Anmeldung `Authorization: Bearer <schlüssel>`, höchstens 2 Anfragen je Sekunde.

## Endpunkte

| Pfad | Methoden | Zweck, Besonderheiten |
| --- | --- | --- |
| `/profile` | GET | Firma, `taxType`, `smallBusiness`, Funktionen |
| `/contacts` | GET, POST | Suche `name`, `email` (ab 3 Zeichen), `number`, `customer`, `vendor`; bis 250 je Seite |
| `/contacts/{id}` | GET, PUT | PUT mit `version`, ersetzt den ganzen Datensatz; kein DELETE |
| `/articles` | GET, POST | Filter `articleNumber`, `gtin`, `type` |
| `/articles/{id}` | GET, PUT, DELETE | einziger Datensatz, der sich löschen lässt (neben Webhook-Abos) |
| `/invoices` | POST | `?finalize=true`, `?precedingSalesVoucherId=`; kein Listen-GET (dafür `/voucherlist`) |
| `/invoices/{id}` | GET | |
| `/invoices/{id}/file` | GET | PDF (`Accept: application/pdf`) oder XRechnung (`Accept: application/xml`); Entwurf: 409 |
| `/quotations`, `/order-confirmations`, `/delivery-notes`, `/credit-notes` | POST, GET `{id}`, GET `{id}/file` | wie Rechnungen |
| `/down-payment-invoices/{id}` | GET, GET `/file` | nur lesen |
| `/dunnings` | POST `?precedingSalesVoucherId=` | immer Entwurf; GET `{id}`, `/file`; nicht in der Belegliste |
| `/recurring-templates` | GET, GET `{id}` | nur lesen |
| `/voucherlist` | GET | Index aller Belege; `voucherType` und `voucherStatus` Pflicht |
| `/vouchers` | POST | Eingangs- und Ausgangsbelege der Buchhaltung |
| `/vouchers/{id}` | GET, PUT | PUT ohne `files` löscht die Dateien |
| `/vouchers/{id}/files` | POST | Datei an einen Beleg (multipart `file`) |
| `/files` | POST, GET `{id}` | Upload zur Belegerkennung (multipart `file`, `type=voucher`), Antwort 202 mit `voucherId` |
| `/payments/{id}` | GET | Zahlstand eines Belegs |
| `/payment-conditions`, `/posting-categories`, `/print-layouts`, `/countries` | GET | Listen ohne Seiten |
| `/event-subscriptions` | GET, POST, GET `{id}`, DELETE `{id}` | Webhooks |

## Werte

**taxType:** `net`, `gross`, `vatfree` (Kleinunternehmer), `intraCommunitySupply`, `constructionService13b`,
`externalService13b`, `thirdPartyCountryService`, `thirdPartyCountryDelivery`, `photovoltaicEquipment`.

**lineItems[].type:** `custom`, `service`, `material` (mit Artikel-`id`, Felder trotzdem mitschicken), `text`.

**shippingConditions.shippingType:** `service`, `serviceperiod`, `delivery`, `deliveryperiod`, `none`.

**voucherlist voucherType:** `invoice`, `quotation`, `orderconfirmation`, `deliverynote`, `creditnote`,
`downpaymentinvoice`, `salesinvoice`, `salescreditnote`, `purchaseinvoice`, `purchasecreditnote` (Komma-Liste oder
`any`). `invoice` (in Lexware geschrieben) und `salesinvoice` (Buchhaltungsbeleg) sind verschiedene Typen.

**voucherlist voucherStatus:** `draft`, `open`, `overdue` (nur allein), `paid`, `paidoff`, `voided`, `accepted`,
`rejected`, `unchecked`, `any`. Weitere Filter: `contactId`, `voucherNumber` (exakt), `voucherDateFrom`/`To`,
`createdDateFrom`/`To`, `updatedDateFrom`/`To` (nur Datum), `archived`, `sort`.

**vouchers type:** `salesinvoice`, `salescreditnote`, `purchaseinvoice`, `purchasecreditnote`; `voucherStatus` beim
Anlegen leer, `open` oder `unchecked`.

## Grenzen

| Was | Grenze |
| --- | --- |
| Anfragen | 2 je Sekunde, ein Kontingent für alles |
| Seitengröße | Standard 25, höchstens 250; Suchfenster 10.000 Treffer |
| Positionen je Beleg | 300 |
| `title` / `introduction`, `remark` / Positionsname | 25 / 2000 / 255 Zeichen (Doku) |
| Artikel-`title` | 100 Zeichen (im Betrieb erzwungen) |
| Belegdateien | PDF, JPG, PNG, XML; 5 MB |
| Währung | nur EUR |
| Schlüssel | höchstens 24 Monate gültig |

## Direktlinks

`https://app.lexware.de/permalink/<typ>/<view|edit>/<id>` für `contacts` (view), `invoices` (auch Abschläge),
`quotations`, `order-confirmations`, `delivery-notes`, `credit-notes`, `dunnings`, `vouchers`;
`recurring-templates` nur `edit`.

## Webhooks

Ereignisse `<art>.created|changed|deleted` für `article`, `contact`, `invoice`, `quotation`, `credit-note`,
`order-confirmation`, `delivery-note`, `down-payment-invoice`, `voucher`, `dunning`, `recurring-template`;
`<art>.status.changed` für die Belegarten außer Mahnung und Vorlage; `payment.changed`, `token.revoked`. Körper
`{organizationId, eventType, resourceId, eventDate}`, Signatur `X-Lxo-Signature` (RSA-SHA512, Base64), 5 Sekunden
Zeit, Wiederholung nach 10, 20, 40, 80, 160 Sekunden und dann zweistündlich.

## Offizieller MCP-Server

`https://mcp.lexware.de/mcp`, OAuth mit dem Lexware-Login, Tarif XL, 40 Werkzeuge (27 lesend, 13 schreibend),
2 Aufrufe je Sekunde, keine Datei-Uploads. Einrichtung je Client: https://developers.lexware.io/mcp/docs/
