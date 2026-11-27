# Änderungen

## 1.0.1 · 27.11.2026

- `lexware-automatisierung`: Abschnitt 2 neu, „Sparsam abfragen“. Webhooks zuerst, Abfrage nur als Sicherheitsnetz
  ein- bis zweimal am Tag, eine Anfrage für alle Arten, Einzelbelege nur bei neuer `updatedDate`, ein Abgleich je
  Konto, Testumgebung nicht im Takt, Aufrufe mitzählen.
- `lexware-auswertungen`: die neue `updatedDate` immer mitspeichern.
- Drei neue Befunde (40 bis 42), alle im Betrieb geprüft.

## 1.0.0 · 22.11.2026

- Zehn Skills: Grundlagen, Rechnungen, Angebote, Kontakte, Artikel, Belege, offene Posten, Auswertungen, Check,
  Automatisierung.
- `lexware.py`: Werkzeug ohne Abhängigkeiten mit Drossel, 429-Pause, 406-Felderklärung, Festschreib-Sperre,
  Nur-Lesen-Modus, CSV-Ausgabe, PDF und XRechnung, Belegupload, Datumsformat mit Berliner Versatz.
- `check.py`: Gesundheitscheck eines Kontos als Ampel-Bericht.
- `aufschlag.py`: Nachunternehmer-Positionen mit Aufschlag oder Handling Fee.
- `webhook-pruefen.mjs`: Webhook-Empfänger mit Signaturprüfung.
- Anschluss wahlweise über den offiziellen Lexware-MCP-Server oder die Public API.
- 39 Befunde mit Herkunft, davon 26 im Betrieb geprüft; Tests gegen eine Lexware-Attrappe.
