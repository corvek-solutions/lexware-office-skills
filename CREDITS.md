# Quellen und Dank

Alle Texte und der gesamte Code in diesem Repository sind neu geschrieben. Die folgenden öffentlichen Projekte haben
wir vorher gelesen und geprüft (Herkunft, Lizenz, Netzwerkziele, Skripte). Ideen, die wir übernommen haben, stehen
dabei. Danke an alle, die ihr Wissen offen teilen.

| Projekt | Lizenz | Übernommene Ideen |
| --- | --- | --- |
| [Ultra-Smashed/lexware-skill](https://github.com/Ultra-Smashed/lexware-skill) | MIT | „Erst zeigen, dann schreiben“ mit Summentabelle; fehlende Angaben in einer Nachricht erfragen; Vorbereitungsmodus ohne Schnittstelle; Mahnstufen |
| [jan-nikolov/lexware-office-axi](https://github.com/jan-nikolov/lexware-office-axi) | MIT | Stufen Lesen, Schreiben, Festschreiben; Schreiben nach Abbruch nicht blind wiederholen; HTML-Kodierung in der Suche; PDF von Entwürfen (409) |
| [HybridAIOne/hybridclaw](https://github.com/HybridAIOne/hybridclaw) | MIT | Schreiben nur mit ausdrücklicher Freigabe; Schlüssel nie in den Chat |
| [ilyafedotov-ops/german-business-skills](https://github.com/ilyafedotov-ops/german-business-skills) | MIT | Hinweis auf „Als Entwurf drucken“; Schlüssel erst ab Tarif XL |
| grundwerk/lexoffice-accounting-skill | ohne klare Lizenz | nur Fakten: Kategorien nach Namen auflösen; Dubletten über Nummer und Belegdatum; nach jedem Schreiben zurücklesen |
| Miragon/miranum-skills | ohne Lizenz | nur Fakten: § 13b braucht `allowTaxFreeInvoices` am Kontakt; Textposition als Projektkopf |

Bewusst **nicht** übernommen: Anmeldung in der Weboberfläche mit Passwort und Umgehung der Bot-Erkennung, interne
undokumentierte Endpunkte, Massenlöschungen, Steuer- und Lohnberatung, Anbieter-Laufzeitumgebungen mit fremder
Schlüsselverwahrung, Werbe-Fußzeilen und Herstellermarken in Buchhaltungsdaten.

Fakten zur API stammen aus der offiziellen Dokumentation unter https://developers.lexware.io, Praxisbefunde aus
eigenen Projekten (Zeichen ✅ in [fallstricke.md](skills/lexware-grundlagen/referenz/fallstricke.md)).

## Marken

Lexware und Lexware Office sind Marken der Haufe-Lexware GmbH & Co. KG bzw. der Haufe Group. Dieses Projekt ist
unabhängig und wird von Lexware weder betrieben noch unterstützt oder geprüft. Der Name wird nur verwendet, um zu
beschreiben, womit die Skills zusammenarbeiten.
