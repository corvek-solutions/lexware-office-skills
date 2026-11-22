---
name: lexware-artikel
description: Artikelstamm in Lexware Office aufbauen und pflegen, vom einzelnen Artikel bis zum Import ganzer Leistungsverzeichnisse (LV, Preislisten, Excel) mit Protokoll und vollständigem Rückbau. Kennt die Grenzen der API (Titel 100 Zeichen, Einheiten als freier Text, Artikelnummer nicht eindeutig geprüft, Prozent-Positionen). Verwenden bei „leg den Artikel an“, „importiere die Preisliste“, „Leistungsverzeichnis nach Lexware“, „Artikelstamm aufräumen“, „welche Artikel haben keine Nummer“, „ändere den Preis von …“.
---

# Lexware Office: Artikel

Werkzeug: `../lexware-grundlagen/scripts/lexware.py`. Artikel sind der einzige Bereich, in dem die API auch löschen
kann. Deshalb taugt er für große Importe mit sauberem Rückweg.

## Lesen

- Alle: `lexware.py alle /articles --felder id,articleNumber,title,unitName,price.netPrice,type`
  (Seitengröße fest 25; `size` mitzuschicken ergibt 406).
- Gezielt: `lexware.py get /articles articleNumber=LV-01.02.001`, auch `gtin=…`, `type=SERVICE|PRODUCT`.

## Anlegen

```json
{
  "title": "Bodenbelag demontieren",
  "description": "Losen Bodenbelag aufnehmen, Kleberreste entfernen, Material entsorgungsgerecht bereitstellen.",
  "type": "SERVICE",
  "articleNumber": "LV-01.02.001",
  "unitName": "m²",
  "price": { "netPrice": 12.40, "leadingPrice": "NET", "taxRate": 19 }
}
```

Pflicht sind `title`, `type`, `unitName`, `price`. Aus der Praxis:

| Befund | Folge |
| --- | --- |
| `title` höchstens 100 Zeichen (die API erzwingt es, die Doku nennt es nicht) | längere Titel kürzen, Rest in `description` |
| `description` verträgt lange Texte (über 500 Zeichen geprüft) | Langtexte aus dem LV gehören dorthin |
| `unitName` ist freier Text; unbekannte Einheiten legt Lexware still an | vorher normalisieren, sonst stehen `St`, `Stk` und `Stück` nebeneinander |
| `articleNumber` ist optional und **nicht** eindeutig geprüft | vorher selbst gegen den Bestand prüfen |
| `taxRate` nimmt 0, 7, 19 | |
| `type` ist `SERVICE` oder `PRODUCT`; die CSV-Importvorlage von Lexware hat dafür keine Spalte | wer den Typ steuern will, nimmt die API |
| Die Artikelsuche in Lexware trifft auf die Artikelnummer | Positionsnummer in `articleNumber`, nicht in den Titel schreiben |

## Großer Import mit Rückweg

1. **Quelle lesen** (PDF-Leistungsverzeichnis, Excel, CSV) und in eine JSON-Liste im Format oben bringen. Einheiten
   normalisieren, Titel über 100 Zeichen teilen, Dubletten gegen den Bestand und in sich prüfen.
2. **Bestand sichern:** `lexware.py alle /articles > artikel-vorher.json`.
3. **Probe mit fünf Artikeln**, zurücklesen, in Lexware ansehen lassen. Erst nach dem Ja weiter.
4. **Import** Artikel für Artikel mit `lexware.py post /articles <datei>` und ein **Protokoll** führen: je Artikel
   Nummer, HTTP-Status, vergebene `id`. Bei Abbruch dort weitermachen, wo das Protokoll endet.
5. **Rückbau** bei Bedarf: jede `id` aus dem Protokoll mit `lexware.py loeschen /articles/<id> --ja` (Antwort 204).
   Danach ist der Stamm wieder wie vorher; zum Beleg mit `artikel-vorher.json` vergleichen.

Bewährt: rund 530 Artikel in einem Lauf, durch die Drossel ohne einen einzigen 429.

## Prozent-Positionen: nicht als Artikel

Zuschläge wie „Regiekosten 13 %“ oder „Baustelleneinrichtung 1 %“ sind keine Leistung mit Euro-Preis, sondern eine
Rechenregel auf die Summe. Als Artikel mit Preis 13,00 € und Einheit „%“ rechnet Lexware im Beleg `Menge × 13,00 €`,
also falsch. Optionen, dem Menschen vorlegen:

- draußen lassen und im Beleg als eigene Position mit dem ausgerechneten Betrag setzen (empfohlen);
- mit Preis 0,00 € anlegen, Satz nur im Text, damit sie in der Suche auftaucht.

## Artikel in Belegen

Ein Artikel im Beleg (`lineItems[].id` = Artikel-ID, `type` = `service` oder `material`) übernimmt über die API
**keine** Werte automatisch, anders als in der Oberfläche. Name, Beschreibung, Einheit und Preis immer selbst
mitschicken. Abweichende Werte im Beleg ändern den Artikel nicht.
