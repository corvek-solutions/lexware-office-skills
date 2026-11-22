# Installation im Detail

Die Skills folgen dem offenen Format **Agent Skills** (ein Ordner je Skill mit `SKILL.md`). Sie laufen überall, wo
dieses Format gelesen wird. Alle zehn Skills gehören zusammen; `lexware-grundlagen` ist Pflicht.

## Claude Code

Als Plugin, mit Updates:

```
/plugin marketplace add corvek-solutions/lexware-office-skills
/plugin install lexware-office@corvek
```

Oder als Ordner, für alle Projekte:

```
git clone https://github.com/corvek-solutions/lexware-office-skills.git
cp -R lexware-office-skills/skills/* ~/.claude/skills/
```

Nur für ein Projekt: in `.claude/skills/` des Projekts kopieren.

## Claude Desktop und claude.ai

Je Skill ein ZIP in den Einstellungen unter Skills hochladen. Die fertigen ZIPs liegen unter
[Releases](https://github.com/corvek-solutions/lexware-office-skills/releases). Für den Zugriff auf Lexware den
offiziellen Lexware-MCP-Server als Konnektor verbinden (Anleitung: https://developers.lexware.io/mcp/docs/). Mit dem
Konnektor brauchen die Skills `lexware.py` nicht; sie nutzen dann die MCP-Werkzeuge.

## OpenAI Codex, Cursor und andere

Den Inhalt von `skills/` dorthin kopieren, wo das jeweilige Werkzeug Agent Skills sucht (siehe dessen Doku), oder
die `SKILL.md` als Regeln beziehungsweise Projektanweisungen einbinden. `lexware.py` läuft in jedem Terminal mit Python 3.9+.

## Schlüssel hinterlegen

Siehe [lexware-grundlagen](../skills/lexware-grundlagen/SKILL.md#einrichten-der-schlüssel). Danach:

```
python3 skills/lexware-grundlagen/scripts/lexware.py pruefen
```

## Tests

```
python3 -m unittest discover -s tests -v
node --test tests/*.mjs
```

Ohne Lexware-Konto: Die Tests laufen gegen eine Attrappe auf `127.0.0.1`.
