---
name: lexware-automatisierung
description: Lexware Office in Automatisierungen einbinden, die im Betrieb halten (n8n, Make, eigene Dienste, Agenten). Webhooks mit Signaturprüfung, Abfrage als Rückfall, Wiederholung ohne Dubletten über Kennungen, Testbetrieb und Notaus, Fehler als verständlicher Satz an den Auslöser. Verwenden bei „Lexware soll Bescheid geben, wenn …“, „Webhook einrichten“, „n8n mit Lexware“, „automatisch eine Rechnung, wenn …“, „Angebote aus dem Postfach automatisch nach Lexware“, „Lexware-Automatisierung ist doppelt gelaufen“, „Signatur prüfen“.
---

# Lexware Office: Automatisierung

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`; Beispiel zur Signaturprüfung in `beispiele/`. Diese Regeln
kommen aus Strecken, die täglich echte Angebote, Rechnungen und Eingangsbelege durch Lexware schieben.

## 1. Ereignisse: Webhooks

```
lexware.py post /event-subscriptions - <<< '{"eventType": "invoice.status.changed", "callbackUrl": "https://example.de/lexware"}'
lexware.py get /event-subscriptions
lexware.py loeschen /event-subscriptions/<id> --ja
```

- **Ereignisse:** `<art>.created`, `.changed`, `.deleted` für `article`, `contact`, `invoice`, `quotation`,
  `credit-note`, `order-confirmation`, `delivery-note`, `down-payment-invoice`, `voucher`; dazu `.status.changed` für
  alle Belegarten; `dunning` und `recurring-template` ohne Statusereignis; außerdem `payment.changed` und
  `token.revoked`.
- **Inhalt:** nur `organizationId`, `eventType`, `resourceId`, `eventDate`. Was gilt, liest der Empfänger danach
  selbst bei Lexware. So ändert auch eine wiederholte oder vertauschte Meldung nichts Falsches.
- **Signatur prüfen, immer:** Kopf `X-Lxo-Signature`, RSA-SHA512 über den Körper, Base64. Öffentlicher Schlüssel:
  https://developers.lexware.io/webhookSignature/public/public_key.pub. Ohne gültige Signatur nichts annehmen.
  Beispiel ohne Abhängigkeiten: [beispiele/webhook-pruefen.mjs](beispiele/webhook-pruefen.mjs).
- **Adresse:** HTTPS mit gültigem Zertifikat. Lexware prüft sie beim Einrichten mit `HEAD`; antwortet sie darauf
  nicht mit 2xx, scheitert das Abo (406). Gleiches Ereignis an dieselbe Adresse zweimal: 409.
- **Zustellung:** 5 Sekunden Zeit. Also sofort mit 2xx antworten und die Arbeit danach erledigen. Bei 401, 403, 429
  und 5xx wiederholt Lexware nach 10, 20, 40, 80, 160 Sekunden, danach alle zwei Stunden. 404 oder DNS-Fehler lassen
  das Abo nach den Wiederholungen verschwinden, 410 sofort.
- Wird der API-Schlüssel ungültig, sind alle Abos weg (`token.revoked`). Nach einem Schlüsselwechsel neu einrichten.
- Abos lassen sich nicht ändern, nur löschen und neu anlegen.

## 2. Sparsam abfragen: Webhooks zuerst, Abfrage als Sicherheitsnetz

Lexware sieht die Zahl der Aufrufe je Konto, und alle Dienste mit demselben Schlüssel teilen sich die Grenze von
2 Anfragen je Sekunde. Ein Takt, der immer wieder dasselbe fragt, kostet beides, ohne etwas Neues zu liefern.

- **Webhooks zuerst.** Was sofort passieren soll, hängt an einem Ereignis (Abschnitt 1), nicht an einem Takt.
- **Abfrage nur als Sicherheitsnetz,** ein- bis zweimal am Tag, falls ein Ereignis verloren ging: eine einzige
  `voucherlist` für alle gebrauchten Arten (`voucherType=invoice,creditnote,quotation`), `voucherStatus=any`,
  `updatedDateFrom=<letzter Erfolg minus ein Tag>` (nur Datum). Ohne Webhooks höchstens alle 10 bis 15 Minuten und
  ebenso nur nach Geändertem fragen.
- **Einzelbeleg nur bei neuer `updatedDate`,** und die Zeit bei jedem Lauf speichern, auch wenn sich an den eigenen
  Feldern nichts geändert hat. Sonst gilt ein Beleg, an dem Lexware nur Felder ändert, die man nicht speichert, bei
  jedem Lauf wieder als geändert und wird endlos neu geholt.
- **Vollständige Listen höchstens einmal am Tag,** damit in Lexware gelöschte Belege auffallen, ohne dabei die
  Einzelbelege neu zu laden.
- **Ein Abgleich je Konto,** nicht je Dienst. Mehrere Dienste lesen aus einem gemeinsamen Zwischenspeicher, und eine
  Testumgebung mit dem echten Schlüssel läuft nie im selben Takt mit.
- **Mitzählen:** Aufrufe je Lauf ins eigene Protokoll schreiben. Dann fällt ein Ausreißer auf, bevor Lexware ihn meldet.

## 3. Nichts doppelt anlegen

- **Kennung in die Bemerkung:** jeder automatisch angelegte Beleg trägt in `remark` eine Kennung aus dem
  auslösenden System, z. B. `Vorgang 2026-117` oder `Freigabe rf-42`.
- **Vor dem Anlegen nachsehen:** Gibt es zu dieser Kennung schon einen Beleg dieser Art (nicht storniert), zeigt der
  Auftrag auf ihn statt neu anzulegen.
- **Schreiben nie automatisch wiederholen.** Bricht ein POST ab (Zeitüberschreitung, 504, Neustart), kann er
  angekommen sein. Der nächste Versuch sucht zuerst über die Belegliste (Kunde, Tag) und die Kennung.
- **Je Auftrag ein Schlüssel** (z. B. `angebot:<vorgang>`); ein zweiter Klick oder eine zweite Mail liefert den
  vorhandenen Auftrag zurück.

## 4. Testbetrieb und Notaus

- Drei Stellungen: **aus** (nichts schreibt), **test** (Belege nur an einen festen Testkunden), **an**. Die Stellung
  beim Auslösen **und** beim Ausführen prüfen.
- Eingangsbelege nie im Testbetrieb auf dem echten Konto: Sie lassen sich nicht spurlos löschen.
- Jeder Test auf dem echten Konto verbraucht Belegnummern und hinterlässt Entwürfe, die nur in der Oberfläche
  verschwinden. Testspuren deshalb auflisten und dem Menschen zum Löschen geben.
- Ein Notaus (Umgebungsvariable oder Schalter), der bei jeder Anfrage gelesen wird, nicht nur beim Start.
- Nur die Wege freischalten, die die Strecke braucht (feste Liste je Methode); `finalize` in Automatisierungen
  gar nicht erst bauen.

## 5. Fehler an den Auslöser

Jeder Fehler geht als **ein verständlicher Satz mit Weg nach vorn** an die Person, die ausgelöst hat, und eine Kopie
an den Betreuer. Nie still scheitern, nie die rohe Meldung von Lexware durchreichen.

| Lexware sagt | Satz an den Auslöser |
| --- | --- |
| 406, „exactly one billing address, but 2 …“ | „Der Kunde hat in Lexware zwei Rechnungsadressen. Ich habe die erste genommen und ‚Bitte prüfen‘ in den Entwurf geschrieben.“ oder „Bitte in Lexware eine Rechnungsadresse festlegen.“ |
| 406 mit `details[].field` | „Lexware lehnt das Feld <Feld> ab: <Grund>. Ich habe …“ |
| 401 | „Lexware lässt die Automatisierung gerade nicht hinein. Der Schlüssel ist abgelaufen oder falsch; Betreuer ist informiert.“ |
| 429 nach mehreren Pausen | „Lexware ist gerade ausgelastet. Der Auftrag läuft in ein paar Minuten von selbst weiter.“ |
| Abgleich steht länger als zwei Stunden | einmal melden, nicht bei jedem Lauf; ein Erfolg hebt die Meldung auf |

## 6. n8n

- **HTTP Request**: Authentifizierung „Header Auth“ mit `Authorization: Bearer <Schlüssel>`, Schlüssel nur in den
  Zugangsdaten von n8n.
- **Tempo:** Batching auf 1 Element je 600 ms, wenn ein Knoten viele Aufrufe macht.
- **Fehler:** „Retry on Fail“ wiederholt alle Fehler, auch 406 und abgebrochene POSTs. Besser: „Continue (using error
  output)“ und dahinter nach Status verzweigen; nur 429 nach Pause wiederholen.
- **Webhook-Signatur** im Code-Knoten mit `crypto.verify('RSA-SHA512', …)` (eingebaute Module freischalten:
  `NODE_FUNCTION_ALLOW_BUILTIN=crypto`), Körper dafür roh empfangen.
- **Datum** im Code-Knoten mit Berliner Versatz des jeweiligen Tages bauen, nie fest `+02:00`.

## 7. Für Teams: eine Brücke statt geteilter Schlüssel

Sollen mehrere Personen per Chat auf Lexware zugreifen, mit jeweils eigenen Rechten, ist eine eigene Brücke der
saubere Weg (MCP-Server mit Anmeldung je Person, Schlüssel je Person, nur freigegebene Werkzeuge, Protokoll ohne
Inhalte). Aufbau und Lehren: [docs/team-bruecke.md](../../docs/team-bruecke.md). Für die meisten Fälle reicht heute
der offizielle Lexware-MCP-Server mit der eigenen Anmeldung jeder Person.
