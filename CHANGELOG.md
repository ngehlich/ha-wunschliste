# Änderungen

## 1.1.0

- Gäste können auf der öffentlichen Seite einen freien Wunsch mit „Ich schenke das“ und ihrem Namen selbst als vergeben markieren. Andere sehen nur „Schon vergeben“.
- Mit „Doch nicht“ lässt sich die eigene Markierung auf demselben Gerät wieder aufheben.
- Im Bearbeiten-Menü sind selbst eingetragene Namen mit „(selbst)“ gekennzeichnet.
- Neue Events `wunschliste_vergeben` und `wunschliste_freigegeben` für Automationen.
- Der Standard-Hinweistext erklärt das Markieren. Wer den alten Text nie geändert hat, bekommt den neuen automatisch.

## 1.0.0

Erste veröffentlichte Version.

- Menüpunkt „Wunschliste“ zum Hinzufügen, Ändern, Löschen und Vergeben von Wünschen
- Öffentliche Nur-Lese-Seite ohne Login unter `/geschenkliste`, ohne Namen der Schenkenden
- Preisklassen, „Zeit statt Geld“, Filter, Countdown zum Termin
- Import und Export als JSON-Datei
- Live-Aktualisierung zwischen mehreren offenen Geräten
