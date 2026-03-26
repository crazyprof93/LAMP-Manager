#!/bin/bash

# LAMP Manager Starter Script
# Dieses Skript startet den LAMP Manager mit der korrekten Python-Umgebung

echo "LAMP Manager wird gestartet..."

# Zum Projektverzeichnis wechseln
cd "$(dirname "$0")"

# Prüfen ob virtuelle Umgebung existiert
if [ ! -d ".venv" ]; then
    echo "Virtuelle Umgebung nicht gefunden!"
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv .venv
    echo "Virtuelle Umgebung erstellt"
fi

# Virtuelle Umgebung aktivieren
echo "Aktiviere virtuelle Umgebung..."
source .venv/bin/activate

# Abhängigkeiten prüfen und installieren
echo "Pruefe Abhaengigkeiten..."
pip install -r requirements.txt > /dev/null 2>&1

# Tkinter prüfen und installieren
echo "Pruefe Tkinter..."
python3 -c "import tkinter; print('Tkinter OK')" 2>/dev/null || {
    echo "Tkinter nicht installiert!"
    echo "Installiere Tkinter..."
    sudo apt update && sudo apt install python3-tk -y
}

# Docker-Berechtigungen prüfen und setzen
echo "Pruefe Docker-Berechtigungen..."
if ! groups $USER | grep -q docker; then
    echo "Du bist nicht in der Docker-Gruppe!"
    echo "Fuehre Docker-Berechtigungseinrichtung durch..."
    
    # Benutzer zur Docker-Gruppe hinzufügen
    echo "Fuege Benutzer '$USER' zur Docker-Gruppe hinzu..."
    sudo usermod -aG docker $USER
    
    echo ""
    echo "WICHTIG: Die Docker-Berechtigungen benoetigen einen Neustart!"
    echo ""
    echo "Naechste Schritte:"
    echo "   1. Abmelden (Logout)"
    echo "   2. Neu anmelden (Login)"
    echo "   3. Dieses Skript erneut ausfuehren: ./start_lamp_manager.sh"
    echo ""
    echo "Nach dem Neustart wird der LAMP Manager automatisch gestartet!"
    echo ""
    echo "Anwendung wird jetzt beendet. Bitte neu anmelden und erneut starten."
    
    # Beenden ohne Anwendung zu starten
    deactivate
    exit 0
fi

# Wenn wir hier sind, sind alle Berechtigungen OK
echo "Docker-Berechtigungen OK!"
echo "Alle Voraussetzungen erfuellt!"
echo ""

# Anwendung starten
echo "Starte LAMP Manager..."
echo "Pfad: $(pwd)"
echo "Python: $(which python)"
echo ""

python lamp_manager.py

# Deaktivieren der virtuellen Umgebung beim Beenden
deactivate
