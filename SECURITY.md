# Sicherheit

## Wie die Skills geschützt sind

- **Kein Schlüssel im Chat.** Der API-Schlüssel liegt im Schlüsselbund, in einer Datei mit Rechten 600 oder in einer
  Umgebungsvariable. Die Skills fragen nie danach, das Werkzeug gibt ihn nie aus (Test vorhanden).
- **Feste Adresse.** `lexware.py` spricht nur mit `https://api.lexware.io/v1`. Umstellen lässt sich die Adresse nur
  auf `127.0.0.1` oder `localhost`, für Tests mit einer Attrappe.
- **Keine Abhängigkeiten.** Python-Standardbibliothek und Node-Bordmittel. Nichts wird nachgeladen, keine
  Telemetrie, keine Installationsskripte, keine Hooks, keine mitgelieferten Einstellungen.
- **Entwurf zuerst.** `finalize=true` geht nur mit dem Schalter `--festschreiben`; `LEXWARE_NUR_LESEN=1` sperrt jedes
  Schreiben; Löschen nur für Artikel und Webhook-Abos und nur mit `--ja`.
- **Kein blindes Wiederholen.** Bricht ein Schreibvorgang ab, meldet das Werkzeug das, statt erneut zu senden.
- **Webhooks nur mit Signatur.** Das Beispiel prüft RSA-SHA512 gegen den öffentlichen Schlüssel von Lexware und
  nimmt höchstens 4 KB an.
- **Rechte klein halten.** Für Auswertungen einen Schlüssel nur mit Leserechten anlegen.

## Lücke gefunden?

Bitte nicht als öffentliches Issue, sondern über die Sicherheitsmeldung von GitHub (Reiter „Security“ ›
„Report a vulnerability“) oder per Mail an lennart.duerr@corvek.de. Wir melden uns innerhalb von zwei Werktagen.
