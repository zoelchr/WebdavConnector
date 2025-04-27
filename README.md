WebDAV Connector - Version 2.3
===============================

Beschreibung:
-------------
Mit diesem Tool kannst du unter Windows bequem WebDAV-Verbindungen verwalten:
- Beliebig viele Verbindungen speichern
- Verbindungen aktivieren oder deaktivieren
- Verbindungen löschen
- Alle aktiven Laufwerke auf einmal trennen
- Login/Passwort optional verwenden (wird pro Verbindung gespeichert)
- Nur freie Laufwerksbuchstaben werden angeboten
- Nur freie Pfade werden angeboten

Installation:
-------------
1. Python 3 installieren (https://www.python.org/)
2. Zusatzmodul 'python-dotenv' installieren:
   > pip install python-dotenv

Starten:
--------
- Skript 'webdav_connector.py' ausführen:
   > python webdav_connector.py

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
- Passwortabfragen zeigen klar an, zu welcher Verbindung sie gehören.

Stand:
------
Version 2.3 (April 2025)