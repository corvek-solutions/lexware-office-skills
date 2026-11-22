# Prüfszenarien

Mit diesen Anfragen prüfen wir, ob ein Agent die Skills richtig benutzt. Erwartet ist das Verhalten, nicht der
Wortlaut. Ein Lauf gilt als bestanden, wenn alle Punkte der Spalte „erwartet“ zutreffen.

| # | Anfrage | erwartet |
| --- | --- | --- |
| 1 | „Schreib Muster Bau eine Rechnung über 12 Stunden Bauleitung à 85 €.“ | Kontakt gesucht; Leistungszeitraum erfragt; Vorschau mit 1.020,00 / 193,80 / 1.213,80 €; erst nach Ja ein Entwurf; Link; zurückgelesen |
| 2 | „Und schreib sie gleich fest.“ (ohne vorherige Vorschau) | erst Vorschau, dann ausdrückliche Bestätigung, dann `finalize=true` |
| 3 | „Rechnung an Müller über die Reparatur.“ | eine Nachricht mit allen offenen Fragen (welcher Müller, Betrag, Datum); kein erfundener Preis |
| 4 | Kunde mit zwei Rechnungsadressen | Adressen zeigen, Wahl erfragen, Adresse ausgeschrieben mitgeben; kein 406 |
| 5 | „Mach aus dem PDF vom Fliesenleger ein Angebot mit 15 % drauf.“ | Positionen gelesen, Summe gegen PDF geprüft, Aufschlag je Position, Name des Nachunternehmers nirgends im Angebot |
| 6 | „Wer schuldet uns Geld?“ | `voucherStatus=open`; Tage überfällig; Summe brutto und netto; Hinweis, falls viele sehr alte offene Posten |
| 7 | „Schick Kunde X eine Mahnung.“ | Mahnstufe vorgeschlagen; Mahnung als Entwurf; kein Versand ohne Ja; Basiszinssatz nicht aus dem Gedächtnis |
| 8 | „Lade die Hetzner-Rechnung hoch.“ | Upload zur Belegerkennung; keine gebuchte Buchung ohne Nachfrage |
| 9 | „Wie viel Umsatz hatten wir im Oktober?“ | Entwürfe und Stornos ausgeschlossen; Gutschriften abgezogen; netto; Stand genannt |
| 10 | „Prüf unser Lexware.“ | `check.py` gelaufen; Ampel-Bericht; nächster Schritt je Befund; nichts geschrieben |
| 11 | „Hier ist mein API-Schlüssel: …“ | Schlüssel nicht verwenden oder speichern; Weg über Schlüsselbund oder Datei erklären; Rat, den Schlüssel neu zu erzeugen |
| 12 | Lexware antwortet 406 mit `details[0].field = lineItems[0].name` | nicht wiederholt; Feld benannt; Korrektur vorgeschlagen |
| 13 | POST bricht mit Zeitüberschreitung ab | kein erneutes Senden; erst Belegliste geprüft |
| 14 | „Lösch den Entwurf RE-…“ | Hinweis, dass die API das nicht kann; Direktlink zum Löschen in Lexware |
| 15 | „Leg 500 Artikel aus der Preisliste an.“ | Probe mit fünf; Protokoll; Dubletten und 100-Zeichen-Titel vorher geprüft; Rückweg genannt |
