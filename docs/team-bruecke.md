# Lexware für ganze Teams: die Brücke

Wenn mehrere Personen im Chat auf Lexware zugreifen sollen, jede mit ihren eigenen Rechten, gibt es zwei Wege.

## Weg 1: der offizielle Lexware-MCP-Server

Seit November 2026 bietet Lexware einen eigenen MCP-Server an (`https://mcp.lexware.de/mcp`). Jede Person meldet sich
mit ihrem eigenen Lexware-Login an und gibt die Bereiche frei. Für die meisten Teams ist das der richtige Start: kein
Schlüssel, keine eigene Infrastruktur, Rechte wie in Lexware. Die Skills in diesem Repository arbeiten damit
zusammen (Zuordnung der Werkzeuge im Skill `lexware-grundlagen`).

## Weg 2: eine eigene Brücke

Eine eigene Brücke lohnt sich, wenn Lexware nur ein Teil des Ablaufs ist: wenn derselbe Chat auch ablegen,
Excel-Listen pflegen, Mails entwerfen und Aufträge auslösen soll, mit einer Anmeldung über das Firmenkonto
(Microsoft 365) statt einzelner Logins, und mit Regeln, die Lexware allein nicht kennt.

```
Chat-Assistent der Person ──OAuth (Firmenkonto, z. B. Microsoft Entra)──► Brücke (MCP-Server, nur freigegebene Werkzeuge)
                                                                            │ erkennt die Person am Token
                                                                            ▼
                                                    Lexware Public API mit dem Schlüssel genau dieser Person
                                                    Microsoft 365 mit den Rechten genau dieser Person (On-Behalf-Of)
```

### Bauregeln, die sich bewährt haben

1. **Schlüssel je Person**, mit nur den Bereichen, die sie braucht. Fehlt einer, antwortet die Brücke „für dich
   noch nicht eingerichtet“. Dann sieht niemand im Chat mehr als in seiner Lexware-Oberfläche.
2. **Lesewerkzeuge im Code nur mit GET.** Was nicht gebaut ist, kann kein Modell auslösen. Schreibende Werkzeuge
   einzeln, mit Bestätigung im Chat, Festschreiben gar nicht.
3. **Zugang nur für eine Gruppe** im Firmenkonto (Zuweisung erforderlich), die Brücke prüft Aussteller, Zielgruppe
   und Gruppe im Token zusätzlich.
4. **Refresh-Token sichern:** Beim Anmelden `offline_access` mit anfragen. Ohne ihn stirbt jede Verbindung nach gut
   einer Stunde, und die Nutzer sehen nur „Erneut verbinden“.
5. **Werkzeugliste stabil halten:** Chat-Assistenten laden sie nur beim Verbinden. Neue Werkzeuge heißt: jede Person
   trennt und verbindet neu.
6. **Protokoll ohne Inhalte:** wer, wann, welches Werkzeug, welches Ziel; nie Beträge, Namen oder Antworten.
   90 Tage aufbewahren.
7. **Bremse je Person** (z. B. 60 Aufrufe je Minute) zusätzlich zur Drossel von Lexware (2 je Sekunde je Schlüssel).
8. **Fehler als Satz** mit Weg nach vorn, nie die rohe Meldung von Lexware.
9. **Eigener, gehärteter Server** (Dienstnutzer, nur Lesen außer Protokoll, Geheimnisse nur auf dem Server, nie im
   Repository).

### Was es im Betrieb leistet

Fragen wie „Welche Rechnungen bei Kunde X sind noch offen?“, „Was haben wir dem Kunden für das Objekt in der
Hauptstraße angeboten?“ oder „Leg das Angebot vom Nachunternehmer als Entwurf mit 15 % an“ beantwortet der Chat aus
Lexware, mit Belegnummer und Direktlink, und jede Person sieht dabei nur, was sie sehen darf.

Eine solche Brücke bauen wir individuell für den jeweiligen Betrieb: [corvek.de](https://corvek.de).
