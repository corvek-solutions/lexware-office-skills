<p align="center">
  <img src="assets/banner.png" alt="Agent Skills für Lexware Office, von Corvek Solutions" width="100%">
</p>

<p align="center">
  <b>Zehn Skills, mit denen KI-Agenten in Lexware Office arbeiten wie ein erfahrener Profi:<br>
  Entwurf zuerst, Summen nachgerechnet, Fehler verstanden, Direktlink dabei.</b>
</p>

<p align="center">
  <img alt="Lizenz MIT" src="https://img.shields.io/badge/Lizenz-MIT-0b0d10?style=flat-square">
  <img alt="10 Skills" src="https://img.shields.io/badge/Skills-10-0b0d10?style=flat-square">
  <img alt="Keine Abhängigkeiten" src="https://img.shields.io/badge/Abh%C3%A4ngigkeiten-keine-0b0d10?style=flat-square">
  <img alt="Python 3.9+" src="https://img.shields.io/badge/Python-3.9%2B-0b0d10?style=flat-square">
  <img alt="Lexware MCP oder Public API" src="https://img.shields.io/badge/Anschluss-Lexware%20MCP%20oder%20Public%20API-0b0d10?style=flat-square">
</p>

---

## Worum es geht

**Agent Skills** sind Anleitungen mit Werkzeugen, die ein KI-Agent genau dann lädt, wenn er sie braucht. Dieses Paket
bringt ihm Lexware Office bei. Nicht nur, welche Endpunkte es gibt, sondern wie man damit im echten Betrieb arbeitet:
was zuerst geprüft wird, was nie ohne Rückfrage passiert, warum Lexware eine Rechnung ablehnt und wie man es behebt.

Entstanden ist es aus Lexware-Automatisierungen, die wir für Betriebe in Bau, Sanierung und Gebäudebetrieb gebaut haben
und täglich betreiben: Angebote aus dem Postfach, Rechnungsfreigabe mit Eingangsbelegen, Kennzahlen-Cockpits,
Lesezugriff für KI-Agenten im Team. Dazu kommen die besten Ideen aus den öffentlichen Lexware-Projekten auf GitHub,
geprüft und neu geschrieben ([Quellen](CREDITS.md)).

## So sieht das aus

<p align="center"><img src="assets/screenshots/rechnung.png" alt="Rechnung aus einem Satz: Kontakt gefunden, Vorschau mit Netto, Umsatzsteuer und Brutto, Entwurf in Lexware mit Direktlink" width="100%"></p>

<table>
  <tr>
    <td width="50%"><img src="assets/screenshots/angebot.png" alt="Angebot aus dem PDF eines Nachunternehmers mit 15 Prozent Aufschlag"></td>
    <td width="50%"><img src="assets/screenshots/offene-posten.png" alt="Offene Posten mit Tagen über Fälligkeit, brutto und netto"></td>
  </tr>
  <tr>
    <td><b>Angebot aus dem PDF eines Nachunternehmers.</b> Positionen gelesen und gegen die PDF-Summe geprüft, Aufschlag je Position, Name des Nachunternehmers nirgends im Angebot.</td>
    <td><b>Wer schuldet uns Geld?</b> Offene Rechnungen nach Tagen über Fälligkeit, netto anteilig richtig gerechnet, Mahnung als Entwurf auf Zuruf.</td>
  </tr>
</table>

<p align="center"><img src="assets/screenshots/check.png" alt="Lexware-Check: Ampel-Bericht über Stammdaten, Zahlungsabgleich und Entwürfe" width="100%"></p>

<p align="center"><sub>Alle Daten in den Bildern sind erfunden.</sub></p>

## Die zehn Skills

<table>
  <tr><th align="left" width="210">Skill</th><th align="left">Was er kann</th><th align="left" width="230">Sag zum Beispiel</th></tr>
  <tr><td><img src="assets/icons/lexware-grundlagen.svg" width="36" height="36" alt=""><br><a href="skills/lexware-grundlagen/SKILL.md"><b>Grundlagen</b></a><br><sub><code>lexware-grundlagen</code></sub></td><td>Anschluss über den offiziellen Lexware-MCP-Server oder die Public API, Schlüssel sicher ablegen, Fehler lesen, die sechs Regeln. Pflicht für alle anderen</td><td>„Verbinde Lexware“ · „Warum kommt 406?“</td></tr>
  <tr><td><img src="assets/icons/lexware-rechnungen.svg" width="36" height="36" alt=""><br><a href="skills/lexware-rechnungen/SKILL.md"><b>Rechnungen</b></a><br><sub><code>lexware-rechnungen</code></sub></td><td>Rechnung aus einem Satz, Gutschrift, Rechnung aus Angebot, Kleinunternehmer, §&nbsp;13b, XRechnung, PDF</td><td>„Schreib Muster Bau 12 Stunden Bauleitung à 85 € in Rechnung“</td></tr>
  <tr><td><img src="assets/icons/lexware-angebote.svg" width="36" height="36" alt=""><br><a href="skills/lexware-angebote/SKILL.md"><b>Angebote</b></a><br><sub><code>lexware-angebote</code></sub></td><td>Angebot aus Satz, Artikelstamm oder Nachunternehmer-PDF mit Aufschlag oder Handling Fee, weiterführen zu Auftragsbestätigung und Rechnung</td><td>„Mach aus dem PDF ein Angebot, 15&nbsp;% drauf“</td></tr>
  <tr><td><img src="assets/icons/lexware-kontakte.svg" width="36" height="36" alt=""><br><a href="skills/lexware-kontakte/SKILL.md"><b>Kontakte</b></a><br><sub><code>lexware-kontakte</code></sub></td><td>Kunden und Lieferanten finden und anlegen ohne Dubletten, Rechnungsadressen prüfen, sauber ändern</td><td>„Gibt es Müller & Söhne schon?“</td></tr>
  <tr><td><img src="assets/icons/lexware-artikel.svg" width="36" height="36" alt=""><br><a href="skills/lexware-artikel/SKILL.md"><b>Artikel</b></a><br><sub><code>lexware-artikel</code></sub></td><td>Artikelstamm pflegen, Leistungsverzeichnisse und Preislisten importieren, mit Protokoll und Rückbau</td><td>„Importier das Leistungsverzeichnis“</td></tr>
  <tr><td><img src="assets/icons/lexware-belege.svg" width="36" height="36" alt=""><br><a href="skills/lexware-belege/SKILL.md"><b>Belege</b></a><br><sub><code>lexware-belege</code></sub></td><td>Eingangsrechnungen und Quittungen zur Belegerkennung hochladen oder fertig buchen, Kategorie nach Namen, Dublettenprüfung</td><td>„Ab damit in Lexware“</td></tr>
  <tr><td><img src="assets/icons/lexware-offene-posten.svg" width="36" height="36" alt=""><br><a href="skills/lexware-offene-posten/SKILL.md"><b>Offene Posten</b></a><br><sub><code>lexware-offene-posten</code></sub></td><td>Offene und überfällige Rechnungen, Zahlstand, Mahnstufen, Mahnung als Entwurf, Liquiditätsvorschau</td><td>„Wer schuldet uns Geld?“</td></tr>
  <tr><td><img src="assets/icons/lexware-auswertungen.svg" width="36" height="36" alt=""><br><a href="skills/lexware-auswertungen/SKILL.md"><b>Auswertungen</b></a><br><sub><code>lexware-auswertungen</code></sub></td><td>Umsatz je Monat und Kunde, Vorjahresvergleich, Angebotsquote, CSV-Export, mit Zwischenspeicher</td><td>„Wie lief der Oktober?“</td></tr>
  <tr><td><img src="assets/icons/lexware-check.svg" width="36" height="36" alt=""><br><a href="skills/lexware-check/SKILL.md"><b>Check</b></a><br><sub><code>lexware-check</code></sub></td><td>Gesundheitscheck des Kontos als Ampel-Bericht: Adressen, Dubletten, Artikel, Entwürfe, Zahlungsabgleich</td><td>„Ist unser Lexware bereit für Automatisierung?“</td></tr>
  <tr><td><img src="assets/icons/lexware-automatisierung.svg" width="36" height="36" alt=""><br><a href="skills/lexware-automatisierung/SKILL.md"><b>Automatisierung</b></a><br><sub><code>lexware-automatisierung</code></sub></td><td>Webhooks mit Signaturprüfung, Abfrage als Rückfall, nichts doppelt anlegen, Testbetrieb, n8n</td><td>„Sag Bescheid, wenn eine Rechnung bezahlt ist“</td></tr>
</table>

## In zwei Minuten startklar

**1. Installieren**

In Claude Code als Plugin:

```
/plugin marketplace add corvek-solutions/lexware-office-skills
/plugin install lexware-office@corvek
```

Oder als Ordner, für jedes Werkzeug, das Agent Skills liest:

```
git clone https://github.com/corvek-solutions/lexware-office-skills.git
cp -R lexware-office-skills/skills/* ~/.claude/skills/
```

Desktop-Apps, Web und weitere Werkzeuge: [docs/installation.md](docs/installation.md).

**2. Lexware verbinden**, ein Weg genügt:

- **Offizieller Lexware-MCP-Server** für Chat-Assistenten: als Konnektor `https://mcp.lexware.de/mcp` hinzufügen und mit
  dem eigenen Lexware-Login anmelden ([Anleitung von Lexware](https://developers.lexware.io/mcp/docs/)).
- **Public API** für Agenten im Terminal und Automatisierungen: In Lexware unter Erweiterungen › Public API einen
  Schlüssel erzeugen, selbst ablegen (nie in den Chat), dann prüfen:

  ```
  # macOS: Schlüssel verdeckt in den Schlüsselbund, dann Verbindung prüfen
  security add-generic-password -s lexware-api-key -a "$USER" -w
  python3 skills/lexware-grundlagen/scripts/lexware.py pruefen
  ```

Beides braucht Lexware Office mit Schnittstelle (Tarif XL).

**3. Loslegen.** Am besten mit: *„Prüf unser Lexware.“*

## Sicherheit ist eingebaut, nicht angehängt

- **Entwurf zuerst.** Belege entstehen als Entwurf. Festschreiben nur, wenn der Mensch es ausdrücklich sagt; das
  Werkzeug sperrt `finalize=true` ohne den Schalter `--festschreiben`.
- **Erst zeigen, dann schreiben.** Vor jedem Anlegen eine Vorschau mit nachgerechneten Summen, danach zurücklesen und
  vergleichen.
- **Kein Schlüssel im Chat.** Schlüsselbund, Datei mit Rechten 600 oder Umgebungsvariable; nie in einer Ausgabe.
- **Nichts doppelt.** Abgebrochenes Schreiben wird nie blind wiederholt, sondern erst nachgesehen.
- **Nur-Lesen-Modus** mit `LEXWARE_NUR_LESEN=1`, für Auswertungen und den Check automatisch.
- **Keine Abhängigkeiten, keine Telemetrie, keine Hooks, keine mitgelieferten Einstellungen.** Feste Adresse
  `api.lexware.io`. Details in [SECURITY.md](SECURITY.md).

## Aus der Praxis

Fünf von [42 Befunden](skills/lexware-grundlagen/referenz/fallstricke.md), 29 davon im Betrieb selbst geprüft:

1. **429 und 406 sind verschiedene Welten.** 429 heißt warten. 406 heißt „deine Angaben sind falsch“ und wird nie
   wiederholt; das Feld steht in `details[]`.
2. **Ein Beleg an einen Kunden mit zwei Rechnungsadressen scheitert**, außer die Adresse steht ausgeschrieben im Beleg.
3. **`voucherDate` ist ein Kalendertag in deutscher Zeit.** Ein fest eingetragenes `+02:00` datiert im Winter jedes
   Angebot auf den Vortag.
4. **„Offen“ ist nur so gut wie der Zahlungsabgleich.** Ohne verbundenes Bankkonto stehen bezahlte Rechnungen weiter
   als offen da.
5. **Eine Artikel-Referenz übernimmt über die API nichts**, anders als in der Oberfläche. Alle Felder mitschicken.

## Offizieller MCP-Server und Skills: zwei Hälften

Seit November 2026 bietet Lexware einen eigenen MCP-Server mit 40 Werkzeugen. Der Server liefert die **Hände**: Kontakte
lesen, Rechnungen anlegen, Dokumente laden. Diese Skills liefern das **Urteil**: welche Schritte in welcher
Reihenfolge, was vorher geprüft wird, was nie ohne Rückfrage passiert, wie ein Fehler in einen verständlichen Satz
wird. Jeder Skill nennt für seine Schritte das passende MCP-Werkzeug und die Entsprechung in `lexware.py`. Dazu kommt,
was der MCP-Server nicht abdeckt: Belegdateien hochladen, Massenimporte, CSV-Auswertungen, Webhooks.

## Für Betriebe und Teams

Die Skills sind frei verfügbar und funktionieren für sich. Wenn Lexware in einen größeren Ablauf gehört, bauen wir
die individuelle Lösung dazu: Angebotsstrecken aus dem Postfach, Rechnungsfreigabe mit Eingangsbelegen, eine
[Brücke für ganze Teams](docs/team-bruecke.md) mit Rechten je Person, Cockpits mit Kennzahlen aus Lexware und die
Bereinigung der Stammdaten vorher.

**Corvek Solutions** · individuelle Softwarelösungen und Automatisierungen mit KI ·
[corvek.de](https://corvek.de) · [Termin vereinbaren](https://corvek.de/termin-2)

## Mitmachen

Fehler gefunden, Befund aus dem eigenen Betrieb, neue Idee? Issues und Pull Requests sind willkommen. Neue Befunde
bitte mit Herkunft (selbst geprüft oder Doku-Link). Tests ohne Lexware-Konto:

```
python3 -m unittest discover -s tests -v
node --test tests/*.mjs
```

Prüfszenarien für Agenten: [evals/szenarien.md](evals/szenarien.md).

## Lizenz und Marken

MIT, siehe [LICENSE](LICENSE). Icons auf Grundlage von [Lucide](https://lucide.dev) (ISC, [Lizenz](assets/icons/LICENSE-lucide.txt)).

Lexware und Lexware Office sind Marken der Haufe-Lexware GmbH & Co. KG bzw. der Haufe Group. Dieses Projekt ist
unabhängig und wird von Lexware weder betrieben noch unterstützt oder geprüft.
