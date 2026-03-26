# LAMP Server Manager

Eine Python GUI-Anwendung zur Verwaltung von mehreren LAMP-Servern mit Docker Compose und vollständiger Datenbankverwaltung.

## Hauptfunktionen

### **Multi-Server Management**
- **Tab-System**: Verwalte mehrere LAMP-Server in Tabs
- **Server hinzufügen**: Neue Server über YAML-Datei-Import
- **Server löschen**: Mit Container- und Ordner-Management-Optionen
- **Konfliktprüfung**: Automatische Erkennung von Port- und Container-Konflikten

### **Server Steuerung**
- **Start/Stop**: Docker Compose Container steuern
- **Live-Status**: Automatische Status-Updates alle 5 Sekunden
- **Port-Konfiguration**: Automatische Erkennung aus docker-compose.yml
- **Quick-Access**: Direkter Zugriff auf Webserver, phpMyAdmin und Ordner

### **Datenbank Management**
- **Datenbank-Übersicht**: Mit Größe und Tabellenanzahl
- **Erstellen/Löschen**: Datenbanken mit UTF8MB4 Support
- **Benutzer-Verwaltung**: Vollständige MySQL/MariaDB Benutzer-Verwaltung
- **Rechte-Management**: Detaillierte Berechtigungen (SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX, ALL PRIVILEGES)

### **Mehrsprachigkeit**
- **Deutsch/Englisch**: Vollständige Lokalisierung
- **Sprachwechsel**: Laufender Wechsel ohne Neustart
- **Erweiterbar**: Einfache Hinzufügung neuer Sprachen

### **Dateizugriff**
- **Log-Ordner**: Direkter Zugriff auf Apache-Logs
- **Datenbank-Ordner**: Zugriff auf MySQL/MariaDB Daten
- **WWW-Ordner**: Schneller Zugriff auf Web-Root
- **Browser-Integration**: Automatisches Öffnen von URLs

## Installation

### 1. Voraussetzungen
- Python 3.7+ installiert
- Docker und Docker Compose installiert
- LAMP-Server Projekt mit docker-compose.yml

### 2. Tkinter installieren (falls nicht vorhanden)
Falls Tkinter nicht installiert ist:
```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3-tk -y

# Überprüfen
python3 -m tkinter
```

### 3. Docker-Berechtigungen einrichten
Füge deinen Benutzer zur Docker-Gruppe hinzu:
```bash
# Benutzer zur Docker-Gruppe hinzufügen
sudo usermod -aG docker $USER

# Wichtig: Abmelden und neu anmelden ODER
newgrp docker
```

### 4. Python-Abhängigkeiten installieren
```bash
# Virtuelle Umgebung erstellen (empfohlen)
python3 -m venv .venv
source .venv/bin/activate

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Verwendung

Starte die Anwendung:
```bash
python lamp_manager.py
```

### Server Steuerung
- **Server Starten**: Startet alle Docker-Container im Hintergrund (`docker-compose up -d`)
- **Server Stoppen**: Stoppt alle Container (`docker-compose down`)

### Datenbank Verwaltung
- **Datenbanken Aktualisieren**: Lädt alle Datenbanken neu
- **Neue Datenbank**: Erstellt eine neue Datenbank
- **Datenbank Löschen**: Löscht die ausgewählte Datenbank
- **Benutzer Verwalten**: Öffnet Benutzer-Verwaltungsfenster

### Benutzer Verwaltung
- **Neuer Benutzer**: Erstellt neuen Benutzer mit:
  - Multi-Selection für Datenbanken (Strg+Klick für Mehrfachauswahl)
  - Detaillierte Rechte-Setzung (SELECT, INSERT, UPDATE, DELETE, etc.)
  - Flexible Host-Angabe
- **Benutzer Aktualisieren**: Lädt Benutzerliste neu
- **Benutzer Löschen**: Löscht ausgewählten Benutzer

## Konfiguration

### **Automatische Konfiguration**
Die Anwendung liest automatisch die Konfiguration aus deinen `docker-compose.yml` Dateien:
- **Datenbank-Port**: Aus Port-Mapping (z.B. 3306:3306)
- **Webserver-Port**: Aus Apache/Nginx Port-Mapping  
- **phpMyAdmin-Port**: Aus phpMyAdmin Konfiguration
- **Zugangsdaten**: Aus Environment-Variablen (MYSQL_ROOT_PASSWORD, etc.)
- **Container-Namen**: Für Status-Prüfung und Konflikterkennung

### **Multi-Server Setup**
Jeder Server wird über seine eigene `docker-compose.yml` verwaltet:
- **Server hinzufügen**: `+` Tab → YAML-Datei auswählen
- **Server-Name**: Frei wählbar (z.B. "Projekt A", "Testing")
- **Konfiguration**: Automatische Extraktion aus YAML
- **Speicherung**: In `lamp_config.json`

### **Verzeichnisstruktur**
Die Anwendung erwartet folgende Ordnerstruktur pro Server:
```
dein-projekt/
├── docker-compose.yml    # Docker Konfiguration
├── www/                  # Web-Root (Apache/PHP)
├── logs/                 # Apache Logs
├── db/                   # MySQL/MariaDB Daten
└── lamp_manager.py       # GUI Anwendung
```

### **Manuelle Anpassung**
Pfad zur Konfigurationsdatei (wird automatisch erstellt):
```python
# lamp_config.json enthält:
{
  "servers": {
    "server_0": {
      "name": "LAMP Server 1",
      "compose_path": "/pfad/zur/docker-compose.yml"
    }
  },
  "language": "de"
}
```

## Erweiterte Funktionen

### **Server-Management**
- **Starten**: `docker-compose start` oder `docker-compose up -d`
- **Stoppen**: `docker-compose stop` oder `docker-compose down`
- **Status-Prüfung**: Container-Status alle 5 Sekunden
- **Automatische Wiederherstellung**: Fehlerbehandlung und Neustart

### **Benutzer-Verwaltung**
- **Benutzer erstellen**: Mit Passwort, Host und Datenbank-Rechten
- **Benutzer bearbeiten**: Passwort ändern, Rechte anpassen
- **Benutzer löschen**: Mit Sicherheitsabfrage
- **Rechte-Verwaltung**: Granulare Berechtigungen pro Datenbank

### **Web-Integration**
- **Browser-Öffnung**: Automatisch URLs öffnen
- **phpMyAdmin**: Direkter Zugriff auf Datenbank-Webinterface
- **Webserver**: Schneller Zugriff auf Apache/Nginx

### **Datenbank-Informationen**
- **Größe**: MB-Angabe pro Datenbank
- **Tabellen**: Anzahl der Tabellen pro Datenbank  
- **Benutzer**: Zugeordnete Benutzer mit Rechten
- **Live-Updates**: Automatische Aktualisierung bei Server-Start

## Troubleshooting

### **Häufige Probleme**

#### Docker Permission denied
```bash
# Prüfen ob Benutzer in Docker-Gruppe
groups $USER | grep docker

# Falls nicht vorhanden:
sudo usermod -aG docker $USER
# Wichtig: Abmelden und neu anmelden!
```

#### Tkinter nicht gefunden
```bash
# Installieren (Debian/Ubuntu)
sudo apt update && sudo apt install python3-tk -y

# Testen
python3 -c "import tkinter; print('Tkinter OK')"
```

#### Datenbankverbindung fehlgeschlagen
1. **Server starten**: Klicke auf "Server Starten"
2. **Port prüfen**: `docker ps` sollte Port 3306 zeigen
3. **Konfiguration prüfen**: Terminal zeigt geladene Konfiguration an
4. **Warten**: MariaDB braucht manchmal 30-60 Sekunden zum Starten

#### Container-Konflikte
- **Fehlermeldung**: "Port already in use" oder "Container name exists"
- **Lösung**: Andere Ports in docker-compose.yml verwenden
- **Automatische Prüfung**: Anwendung warnt vor Konflikten beim Hinzufügen

#### YAML-Datei Fehler
- **Validierung**: Anwendung prüft YAML-Syntax automatisch
- **Required**: `services` Sektion muss vorhanden sein
- **Ports**: Korrekte Port-Mapping Syntax `host:container`

### **Debugging**

#### Logs anzeigen
```bash
# Docker Logs
docker-compose logs

# Spezifischer Service
docker-compose logs web
docker-compose logs db
```

#### Konfiguration prüfen
```bash
# Docker Compose Konfiguration
docker-compose config

# Container Status
docker ps -a
```

#### Netzwerkprobleme
```bash
# Port belegt?
netstat -tulpn | grep :8080

# Container Netzwerke
docker network ls
```

### **Wichtige Hinweise**

#### Sicherheit
- Die Anwendung verbindet sich als Root-Benutzer zur Datenbank
- Passwörter werden im Klartext in der GUI angezeigt
- Verwende die Anwendung nur in einer sicheren Umgebung

#### Performance
- Status-Updates alle 5 Sekunden (kann CPU-Last erzeugen)
- Große Datenbanken brauchen länger für Tabellen-Zählung
- Multi-Server-Management erhöht Speicherverbrauch

#### Kompatibilität
- **Python**: 3.7+ erforderlich
- **Docker**: Compose v2+ empfohlen
- **Datenbank**: MySQL 5.7+ / MariaDB 10.3+
- **OS**: Linux (getestet auf Ubuntu/Debian)

## **Projektstruktur**

```
LAMP-Manager/
├── lamp_manager.py          # Hauptanwendung (GUI)
├── requirements.txt         # Python-Abhängigkeiten
├── docker-compose.yml       # Docker Konfiguration
├── Dockerfile              # Apache/PHP Image
├── lamp_config.json        # Server-Konfiguration (auto)
├── start_lamp_manager.sh   # Startskript
├── languages/              # Sprachdateien
│   ├── de.json            # Deutsch
│   └── en.json            # Englisch
├── www/                   # Web-Root (Apache)
├── logs/                  # Apache Logs
├── db/                    # MySQL/MariaDB Daten
└── README.md              # Diese Datei
```

## **Schnellstart**

```bash
# 1. Repository klonen/entpacken
cd LAMP-Manager

# 2. Python-Umgebung einrichten
python3 -m venv .venv
source .venv/bin/activate

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Docker-Berechtigungen (falls nötig)
sudo usermod -aG docker $USER
newgrp docker

# 5. Anwendung starten
python lamp_manager.py
```

## **Lizenz**

Dieses Projekt ist Open Source. Feel free to use, modify and distribute.

## **Beitragen**

Issues und Pull Requests sind willkommen!

---

**Version**: 2.0+  
**Letzte Aktualisierung**: 2025  
**Entwickelt mit**: Python 3, Tkinter, Docker, MySQL Connector
