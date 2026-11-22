---
name: lexware-check
description: Gesundheitscheck eines Lexware-Office-Kontos in zwei Minuten, nur lesend, als Ampel-Bericht. Findet, was Automatisierungen und KI-Agenten scheitern lässt, bevor es passiert, Kunden mit mehreren oder ohne Rechnungsadresse, Dubletten, Artikel ohne Nummer, doppelte Artikelnummern, uneinheitliche Einheiten, alte Entwürfe, fehlenden Zahlungsabgleich, abgelaufene Angebote, fehlende Webhooks. Verwenden bei „prüf unser Lexware“, „ist Lexware bereit für Automatisierung“, „Lexware-Check“, „Datenqualität in Lexware“, „warum klappt die Rechnung über die API nicht“, „startklar für das neue Jahr“, vor jedem neuen Automatisierungsprojekt.
---

# Lexware Office: Check

Ein Lexware-Konto ist erst dann bereit für Automatisierung, wenn die Stammdaten sauber sind. Dieser Check misst das,
ohne etwas zu ändern.

## Ablauf

1. `python3 scripts/check.py > lexware-check.md` (im Ordner dieses Skills; `--konto NAME` für ein weiteres eigenes
   Konto, `--tage-alt 180` für die Grenze „sehr alt“). Das Skript setzt selbst den Nur-Lesen-Modus.
2. Bericht zeigen: oben die Gesamtampel und die Zahlen, darunter die Befunde, rot zuerst.
3. Zu jedem roten und gelben Befund einen konkreten nächsten Schritt nennen, mit Ort in Lexware.

Beim offiziellen Lexware-MCP-Server ohne `lexware.py`: dieselben Prüfungen über `list_contacts`, `list_articles` und
`search_vouchers`, Bericht in derselben Form.

## Was geprüft wird, und warum

| Prüfung | Ampel | Warum es zählt |
| --- | --- | --- |
| Kunden mit mehreren Rechnungsadressen | rot | Belege mit bloßer Kunden-ID lehnt Lexware ab; diese Kontakte sind über die API nicht änderbar |
| Kunden ohne Rechnungsadresse | gelb | jeder Beleg an sie scheitert |
| Dubletten (Name ohne Rechtsform) | gelb | Agenten finden mehrere Treffer und müssen raten oder fragen |
| Doppelte Artikelnummern | rot | Lexware prüft Eindeutigkeit nicht; die Artikelsuche trifft dann das Falsche |
| Artikel ohne Nummer (mehr als die Hälfte) | gelb | ohne Nummer keine sichere Zuordnung aus Leistungsverzeichnissen |
| Einheiten in mehreren Schreibweisen | gelb | „St“, „Stk“, „Stück“ nebeneinander machen Auswertungen und Belege uneinheitlich |
| Entwürfe älter als 30 Tage | gelb | Altlasten, über die API nicht löschbar |
| Viele sehr alte offene Rechnungen | rot | fast immer fehlender Zahlungsabgleich; dann ist jede Auswertung offener Posten falsch |
| Mehr als die Hälfte der offenen Angebote abgelaufen | gelb | ohne „angenommen“ und „abgelehnt“ stimmt keine Angebotsquote |
| Keine Webhooks | Hinweis | Automatisierungen müssen dann regelmäßig abfragen statt sofort zu reagieren |

## Startklar für Automatisierung: was nur in Lexware selbst geht

Der Check liest über die API. Diese Punkte prüft der Mensch in Lexware, der Agent fragt sie als Liste ab:

- Tarif mit Schnittstelle (XL) und eigener Schlüssel je Automatisierung, Ablaufdatum notiert (höchstens 24 Monate).
- Nummernkreise für das neue Jahr (Präfix, Startwert) für Angebot, Auftragsbestätigung, Rechnung.
- E-Rechnung eingeschaltet; Leitweg-ID bei öffentlichen Auftraggebern.
- Firmendaten, Bank, Logo, Fußzeile, Textbausteine und Mailvorlagen.
- Bankkonto verbunden und Zahlungen zugeordnet (sonst stimmt „offen“ nicht).
- Buchungskategorien, die Automatisierungen nutzen sollen (z. B. Fremdleistungen).
- Benutzer je Person, Rollen ohne Finanzsicht für Mitarbeitende, die sie nicht brauchen.

Bewährte Reihenfolge vor dem Start einer Automatisierung: Schlüssel setzen › Check › Stammdaten bereinigen › ein
Testkontakt › eine Probe als Entwurf › in Lexware ansehen und festschreiben › erst dann echte Kunden.
