# Fallstricke aus dem Produktivbetrieb

Was beim Bau und Betrieb von Lexware-Automatisierungen in Bau, Sanierung und Gebäudebetrieb tatsächlich aufgefallen
ist: Angebotsstrecken aus dem Postfach, Lesezugriff für KI-Agenten im Team, Rechnungsfreigabe mit Eingangsbelegen,
Kennzahlen-Cockpits, Artikelimporte mit über 500 Positionen.

| Zeichen | Herkunft |
| --- | --- |
| ✅ | im Betrieb selbst ausgeführt und das Ergebnis gesehen |
| 📄 | laut offizieller Doku (developers.lexware.io), dort nachlesbar |

**Oberfläche und API verhalten sich nicht immer gleich.** Nie vom Verhalten in Lexware auf das Verhalten der API
schließen.

## Zugang

1. ✅ **401 nach dem Einrichten ist fast immer ein abgeschnittener Schlüssel.** Ein um ein Zeichen gekürzt
   gespeicherter Schlüssel sah tagelang wie ein widerrufener aus. Erst die Länge prüfen, dann neu erzeugen.
2. 📄 Mehrere Schlüssel je Benutzer, Rechte beim Anlegen wählbar, nachträglich nicht änderbar, gültig höchstens
   24 Monate. Ein Schlüssel kann nie mehr als sein Benutzer.
3. 📄 Die Schnittstelle braucht den Tarif mit Public API (XL). 402 heißt: Vertrag.
4. ✅ Basisadresse `https://api.lexware.io/v1`. Der alte Host `api.lexoffice.io` war nur übergangsweise da; nicht
   mehr verwenden.

## Tempo und Fehler

5. ✅ **Höchstens 2 Anfragen je Sekunde**, über alle Endpunkte zusammen. Eine harte Drossel auf 1,8 je Sekunde hat
   531 Schreibvorgänge am Stück ohne einen einzigen 429 getragen. 📄 Wer dauerhaft drüber liegt, kann gesperrt werden.
6. ✅ **429 und 406 sind verschiedene Welten.** 429 heißt warten und wiederholen. 406 heißt „deine Angaben sind
   falsch“ und wird nie wiederholt; das Feld steht in `details[]`, etwa
   `{"violation": "SIZE", "field": "title", "message": "Größe muss zwischen 1 und 100 sein"}`. Wer 406 wie 429
   behandelt, wiederholt sinnlos und sieht die Ursache nie.
7. ✅ Bei Überlast kommt auch ein Rumpf `{"message": "Rate limit exceeded"}`.
8. 📄 Zwei Fehlerformate: `IssueList` (Kontakte, Dateien, Eingangsbelege) und `details[]` (alles andere).
9. 📄 504 nach 30 Sekunden kann trotzdem angekommen sein. Schreiben nie blind wiederholen.

## Datum

10. ✅ **`voucherDate` ist ein Kalendertag in deutscher Zeit.** `2026-11-12T00:00:00.000+02:00` ist in Berlin der
    11.11., 23 Uhr, und Lexware speichert den 11.11. Eine Strecke mit fest eingetragenem `+02:00` hat nach der
    Zeitumstellung jedes Angebot auf den Vortag datiert, Ablaufdatum ebenso. Immer den Versatz des jeweiligen Tages
    nehmen.
11. ✅ `updatedDateFrom` nimmt nur ein Datum. Mit Uhrzeit kommt 400.
12. 📄 Zeitstempel exakt `yyyy-MM-ddTHH:mm:ss.SSSXXX`, drei Nachkommastellen, sonst 406.

## Kontakte und Adressen

13. ✅ **Ein Beleg mit bloßer `contactId` braucht beim Kunden genau eine Rechnungsadresse.** Sonst 406 „Referenced
    contact needs to have exactly one billing address, but 2 addresses were found“ (oder 0). Ein Angebot ist daran an
    einem Tag fünfmal gescheitert.
14. ✅ **Mit ausgeschriebener Adresse im Beleg geht es trotzdem:** `address: { contactId, name, street, zip, city,
    countryCode }` wird angenommen, der Kunde bleibt verknüpft.
15. 📄 Kontakte mit mehreren Adressen, Ansprechpartnern oder mehreren E-Mails je Art lassen sich über die API nicht
    ändern. Bereinigen nur in Lexware.
16. ✅ Die Kundennummer steht in `roles.customer.number`.
17. 📄 Suche nach Name und E-Mail ab drei Zeichen, Teiltreffer; `&`, `<`, `>` müssen HTML-kodiert sein, `_` und `%`
    sind Platzhalter. Sonst kommt still kein Treffer.
18. ✅ **`address` im Angebot ist die Rechnungsanschrift, nicht der Leistungsort.** Bei Hausverwaltungen steht dort
    die Verwaltung. Wer daraus den Ort für die Auftragsliste zieht, trägt systematisch die falsche Adresse ein. Der
    Leistungsort stand bei 43 von 44 geprüften Angeboten in der Einleitung, in freier Form; das muss ein Modell
    lesen, eine Regex trifft es nicht.

## Belege

19. ✅ **Leere Positionsliste wird angenommen.** `lineItems: []` legt einen Entwurf mit 0 € und echter Nummer an,
    löschbar nur in der Oberfläche. Für Proben nie eine leere Liste.
20. 📄 Jede über die API angelegte Rechnung verbraucht eine Nummer, auch als Entwurf. Entwürfe lassen sich über die
    API weder ändern noch löschen noch nachträglich festschreiben.
21. 📄 **Eine Artikel-Referenz in einer Position übernimmt nichts.** Anders als in der Oberfläche, wo Kurztext,
    Langtext, Einheit, Preis und Steuersatz automatisch einfließen, müssen über die API alle Felder mitgeschickt
    werden.
22. ✅ **`voucherStatus=open` enthält die überfälligen.** `overdue` ist ein Unterfall von offen. Von 70 offenen
    Angeboten trugen 49 den Status `overdue`; wer nur `open` als Wert erwartet, übersieht zwei Drittel.
23. ✅ `size=250` funktioniert in der Belegliste und holt den offenen Bestand in einem Aufruf. Standard sind 25.
24. ✅ `totalPrice` liefert `totalNetAmount`, `totalGrossAmount`, `totalTaxAmount`. Die Belegliste kennt nur
    `totalAmount` und `openAmount`, beide brutto. Netto offen je Beleg anteilig aus Netto ÷ Brutto, nicht pauschal
    ÷ 1,19.
25. ✅ **„Offen“ hängt am Zahlungsabgleich.** Ohne verbundenes Bankkonto bleibt `openAmount` stehen, auch wenn
    längst bezahlt ist. In einem Konto war das Feld deshalb für Auswertungen wertlos.
26. ✅ Teilrechnungen im Bau werden oft kumuliert mit Abzugszeile gestellt. Nicht jede hängt in Lexware am Angebot;
    die Zuordnung braucht dann Bestellnummer oder eine Kennung in der Bemerkung.
27. 📄 Dateien gibt es nur an Eingangsbelegen (`/vouchers/{id}/files`), nicht an Rechnungen oder Angeboten. Was zum
    Versand dazugehört, hängt der Mensch in Lexware an.
28. 📄 Ein Eingangsbeleg lässt sich über die API nicht löschen. Deshalb nie auf dem echten Konto testen.
29. 📄 Optionale oder alternative Positionen in einem Angebot verhindern das Weiterführen zur Rechnung per API.

## Artikel

30. ✅ **`title` höchstens 100 Zeichen**, obwohl die Doku kein Limit nennt. Drei Positionen mit 101 Zeichen kamen mit
    406 zurück. `description` verträgt lange Texte.
31. ✅ `unitName` ist freier Text; unbekannte Einheiten legt Lexware still an. Vorher normalisieren.
32. ✅ `articleNumber` ist optional und wird nicht auf Eindeutigkeit geprüft.
33. ✅ **`DELETE /articles/{id}` ist der Rückwärtsgang.** 5 Artikel angelegt und gelöscht: Stamm danach identisch.
    Damit sind große Importe mit Protokoll vollständig rückbaubar.
34. ✅ Die CSV-Importvorlage von Lexware hat keine Spalte für den Typ (Leistung oder Produkt); die API schon.
35. ✅ Prozent-Positionen aus Leistungsverzeichnissen (Zuschläge) rechnen als Artikel falsch (`Menge × 13,00 €` statt
    13 %). Nicht als Artikel anlegen.

## Webhooks und Betrieb

36. 📄 Webhooks tragen nur Kennungen. Signatur `X-Lxo-Signature`, RSA-SHA512. Lexware prüft die Adresse beim
    Einrichten mit `HEAD`; ein Proxy, der `HEAD` ablehnt, verhindert das Abo.
37. ✅ Eine Brücke für KI-Agenten mit Anmeldung über Microsoft Entra starb nach gut einer Stunde, weil beim
    Anmelden `offline_access` fehlte: kein Refresh-Token, also keine Verlängerung. Mit dem Bereich hält die Verbindung
    wochenlang.
38. ✅ Chat-Assistenten laden die Werkzeugliste eines Konnektors nur beim Verbinden. Neue oder umbenannte Werkzeuge
    brauchen ein Trennen und Neuverbinden je Person.
39. ✅ Fehler aus Lexware an den Auslöser zurückgeben, in einem Satz mit Weg nach vorn. Eine Strecke, die bei 406
    still scheiterte, endete in einem Notfallanruf. Seitdem antwortet jeder Fehler dem Absender mit Grund und nächstem
    Schritt.
40. ✅ Ein Abgleich, der die neue `updatedDate` nur speicherte, wenn sich auch die eigenen Felder änderten, holte
    Angebote bei jedem Lauf neu: Lexware ändert die Zeit eines Angebots auch bei Dingen, die ein Dashboard nicht
    speichert. Zusammen mit kompletten Listen alle 10 Minuten und einer Testumgebung im selben Takt entstand ein
    Vielfaches der nötigen Aufrufe, obwohl sich nur wenige Belege am Tag änderten. Die Zeit immer speichern, nur
    Geändertes abfragen, Test nicht im Takt (siehe `lexware-automatisierung`, Abschnitt 2).
41. ✅ `voucherType` in der `voucherlist` nimmt mehrere Arten mit Komma, auch zusammen mit `purchaseinvoice` und
    `updatedDateFrom`. Jeder Eintrag trägt seine Art in `voucherType`, die Felder sind dieselben wie in der Liste einer
    einzelnen Art (Rechnungen mit `dueDate` und `openAmount`).
42. ✅ Eine Zahlung ändert die `updatedDate` der Rechnung. Eine Abfrage nur nach Geändertem sieht bezahlte
    Rechnungen also am selben Tag.
