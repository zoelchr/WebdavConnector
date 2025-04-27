WebDAV Connector - Version 1.0
===============================

Beschreibung:
-------------
Mit diesem Tool kannst du unter Windows bequem WebDAV-Verbindungen verwalten:
- Beliebig viele Verbindungen speichern
- Verbindungen aktivieren oder deaktivieren
- Verbindungen löschen
- Alle aktiven Laufwerke auf einmal trennen
- Login/Passwort optional verwenden (wird pro Verbindung gespeichert)

Installation:
-------------
1. **Python 3 installieren** (optional, nur wenn du das Skript direkt ausführen möchtest): [Python Download](https://www.python.org/)
2. **Zusatzmodul 'python-dotenv' installieren** (optional, nur wenn du das Skript direkt ausführen möchtest):
   > pip install python-dotenv

Starten:
--------
Um das Tool ohne Installation von Python zu nutzen:
1. Kopiere das gesamte Verzeichnis `./dist/v1.0` an einen lokalen Ort auf deinem Rechner.
2. Passe die Datei `pfade.env` an deine Bedürfnisse an.
3. Starte das Programm über die Datei:
   > .\webdav_connector.exe

Dateien:
--------
- webdav_connector.py  --> Haupt-Programmdatei
- pfade.env             --> Definierte WebDAV-Pfade (Name=Pfad)
- icon.ico              --> Icon für das Fenster (optional)
- history.json          --> Automatisch erstellte Verbindungsverlaufdatei

Besonderheiten:
---------------
- Beim Erstellen neuer Verbindungen kann gewählt werden, ob ein Login/Passwort benötigt wird.
- Die Einstellung (Login erforderlich: Ja/Nein) wird gespeichert.

Stand:
------
Version 1.0 (April 2025)
