# Wunschliste für Home Assistant

> **Hinweis:** Dieses Projekt wurde mit KI (Claude von Anthropic) erstellt und von mir für den Privatgebrauch getestet. Nutzung auf eigene Verantwortung.

Eine Geschenkliste (z. B. zur Geburt) als eigener Menüpunkt in Home Assistant. Familie und Freunde sehen die Liste auf einer öffentlichen Seite ohne Login, bearbeitet wird nur in Home Assistant.

Die Daten liegen ausschließlich in Home Assistant (`/config/.storage/wunschliste`) und sind Teil jeder HA-Sicherung. In diesem Repository liegt nur das Programm, keine Liste.

## Funktionen

- **Bearbeiten in HA:** Wünsche hinzufügen, ändern, löschen, als vergeben markieren (mit Namen) und wieder freigeben
- **Öffentliche Seite** unter `https://<deine-ha-adresse>/geschenkliste`. Dort kann man einen freien Wunsch mit „Ich schenke das“ und seinem Namen selbst als vergeben markieren und auf demselben Gerät mit „Doch nicht“ wieder freigeben. Die Seite zeigt nur „Schon vergeben“, nie, wer etwas schenkt
- **Events für Automationen:** `wunschliste_vergeben` und `wunschliste_freigegeben` mit `wunsch` und `von`, z. B. für eine Push-Nachricht
- Preisklassen (unter 20 €, 20–50 €, 50–100 €, über 100 €) und „Zeit statt Geld“ für Wünsche mit Preis 0
- Überschrift, Termin, Kleidergrößen und Hinweistexte unter „Texte und Termin“
- Import und Export der Liste als JSON-Datei
- Änderungen erscheinen sofort auf allen offenen Geräten

## Installation über HACS

1. HACS → ⋮ → *Benutzerdefinierte Repositories* → `https://github.com/ngehlich/ha-wunschliste`, Typ *Integration*
2. „Wunschliste“ herunterladen und Home Assistant neu starten
3. *Einstellungen → Geräte & Dienste → Integration hinzufügen → Wunschliste*

Danach erscheint „Wunschliste“ in der Seitenleiste. Oben steht der öffentliche Link zum Kopieren.

Damit andere die Seite öffnen können, muss Home Assistant von außen erreichbar sein, z. B. über Nabu Casa oder eine eigene Domain.

## Was ist öffentlich?

Ohne Login erreichbar sind nur:

- `/geschenkliste`: die Seite
- `/api/wunschliste/liste`: Überschrift, Texte, Termin und die Wünsche (Name, Hinweis, Preis, Thema, Shop, Link, vergeben ja/nein)
- `/api/wunschliste/vergeben`: einen freien Wunsch mit Namen markieren. Bei „Zeit statt Geld“ können mehrere zusagen, die Idee bleibt frei
- `/api/wunschliste/freigeben`: eine eigene Markierung aufheben, nur mit dem Schlüssel, den der Browser beim Markieren bekommen hat

Beide Aktionen sind auf 20 pro Adresse in 10 Minuten begrenzt.

Wer etwas schenkt, steht nur im Bearbeiten-Menü (selbst eingetragene Namen mit „(selbst)“). Wünsche anlegen, ändern und fremde Markierungen aufheben geht nur mit HA-Login.

## Updates und neue Versionen

HACS bietet nur veröffentlichte Releases als Update an.

1. `version` in `custom_components/wunschliste/manifest.json` und `VERSION` in `__init__.py` hochzählen
2. Abschnitt `## <version>` in `CHANGELOG.md` ergänzen
3. Auf `main` mergen – der Workflow „Release“ legt Tag und GitHub-Release `v<version>` automatisch an

## Lizenz

GPL-3.0, siehe [LICENSE](LICENSE).
