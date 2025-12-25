# Home Assistant Integration für Ikea Obegraensad

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant Integration für die Ikea Obegraensad LED Matrix Uhr.

## Features

- **Display Ein/Aus**: Steuere das Display über Home Assistant
- **Effekte-Steuerung**: Wähle zwischen verschiedenen LED-Matrix-Effekten (Snake, Clock, Rain, etc.)
- **Helligkeit**: Steuere die Helligkeit des Displays (0-255)
- **Auto-Brightness**: Automatische Helligkeitsanpassung basierend auf Umgebungslicht
- **Zeitzone**: Konfiguriere die Zeitzone für die Uhr
- **Sensoren**: Zeigt aktuelle Zeit, Effekt, Helligkeit, IP-Adresse und Sensorwerte
- **Präsenz-Status**: Zeigt den aktuellen Präsenzstatus an
- **Geräte-Seite**: Vollständige Geräte-Seite mit Device Info und Diagnostics
- **Diagnostics**: Detaillierte Diagnose-Informationen direkt in Home Assistant
- **Automatisierungen**: Nutze alle Entities in HA-Automatisierungen
- **mDNS Discovery**: Automatische Erkennung von Geräten im Netzwerk
- **Parallel zu MQTT**: Funktioniert parallel zur bestehenden MQTT-Präsenz-Integration

## Installation

### Über HACS (Empfohlen)

1. HACS öffnen
2. Integrations → Drei-Punkte-Menü → "Custom repositories"
3. Repository URL: `https://github.com/Abrechen2/ikea-obegraensad-homeassistant`
4. Kategorie: "Integration"
5. "Add" klicken
6. Integration installieren
7. Home Assistant neu starten

### Manuelle Installation

1. Kopiere den `custom_components/ikea_obegraensad/` Ordner in dein `config/custom_components/` Verzeichnis
2. Home Assistant neu starten
3. Gehe zu Settings → Devices & Services → "+" → "Ikea Obegraensad"

## Konfiguration

1. Öffne Home Assistant
2. Gehe zu Settings → Devices & Services
3. Klicke auf "+ ADD INTEGRATION"
4. Suche nach "Ikea Obegraensad"
5. Gib die IP-Adresse deines Geräts ein (z.B. `192.168.1.100`)
6. Optional: Port anpassen (Standard: 80)
7. Optional: Name vergeben

## Verwendung

Nach der Installation werden folgende Entities in Home Assistant erstellt und automatisch unter einem Device gruppiert:

### Entities

- **Switch: Display** - Ein/Aus-Schalter für das Display
- **Switch: Auto Brightness** - Ein/Aus-Schalter für die automatische Helligkeitsanpassung
- **Select: Effect** - Auswahl des aktuellen Effekts (Snake, Clock, Rain, etc.)
- **Select: Timezone** - Auswahl der Zeitzone
- **Light: Brightness** - Steuerung der Helligkeit (kann auch als Light-Entity verwendet werden)
- **Sensor: Time** - Aktuelle Uhrzeit
- **Sensor: Current Effect** - Aktuell aktiver Effekt
- **Sensor: Brightness** - Aktuelle Helligkeit
- **Sensor: Sensor Value** - Wert des Umgebungslichtsensors
- **Sensor: IP Address** - IP-Adresse des Geräts
- **Binary Sensor: Presence** - Präsenzstatus
- **Binary Sensor: Display Status** - Status des Displays

### Geräte-Seite

Jedes konfigurierte Gerät erhält eine vollständige Geräte-Seite in Home Assistant mit:

- **Geräte-Info**: Name, Hersteller (IKEA), Modell (Obegraensad), Firmware-Version und Link zum Web-Interface
- **Diagnose-Karte**: Vollständiger Status-JSON von `/api/status`, Config-Entry-Informationen und Coordinator-Status
- **Alle Entities**: Alle Switches, Selects, Lights und Sensoren sind unter dem Device gruppiert
- **Aktivitäts-Log**: Automatisch generiertes Log aller Entity-Änderungen

Die Geräte-Seite kann über **Einstellungen → Geräte & Dienste → [Gerät]** aufgerufen werden.

### Service: Auto-Brightness konfigurieren

Der Service `ikea_obegraensad.configure_auto_brightness` erlaubt die erweiterte Konfiguration der Auto-Brightness-Funktion:

```yaml
service: ikea_obegraensad.configure_auto_brightness
data:
  entity_id: switch.ikea_clock_auto_brightness
  enabled: true
  min: 50        # Minimale Helligkeit (0-1023)
  max: 800       # Maximale Helligkeit (0-1023)
  sensor_min: 100 # Minimaler Sensorwert (0-1024)
  sensor_max: 900 # Maximaler Sensorwert (0-1024)
```

### Automatisierung Beispiele

```yaml
automation:
  # Wohnzimmer Licht an → Display an
  - alias: "Wohnzimmer Licht an → Display an"
    trigger:
      - platform: state
        entity_id: light.wohnzimmer
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_display

  # Automatische Helligkeit bei Sonnenuntergang aktivieren
  - alias: "Auto-Brightness bei Sonnenuntergang"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_auto_brightness

  # Effekt bei bestimmter Zeit wechseln
  - alias: "Abends Clock-Effekt aktivieren"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.ikea_clock_effect
        data:
          option: "clock"
```

## API-Voraussetzungen

Das Arduino-Gerät muss folgende API-Endpoints unterstützen:

- `GET /api/status` - Gibt JSON mit Status-Daten zurück
  - Erwartete Felder: `displayEnabled`, `brightness`, `currentEffect`, `time`, `presence`, `sensorValue`, `ipAddress`, `autoBrightnessEnabled`, `autoBrightnessMin`, `autoBrightnessMax`, `autoBrightnessSensorMin`, `autoBrightnessSensorMax`, `timezone`
- `GET /api/setDisplay?enabled=true|false` - Setzt Display Ein/Aus
- `GET /api/setBrightness?b=0-1023` - Setzt Helligkeit
- `GET /effect/{effect_name}` - Wechselt den Effekt
- `GET /api/setAutoBrightness?enabled=true|false&min=0-1023&max=0-1023&sensorMin=0-1024&sensorMax=0-1024` - Konfiguriert Auto-Brightness
- `GET /api/setTimezone?tz=Europe/Berlin` - Setzt Zeitzone

## Voraussetzungen

- Home Assistant 2023.1.0 oder höher
- Ikea Obegraensad Gerät mit Firmware, die `/api/setDisplay` unterstützt

## Bekannte Probleme / Einschränkungen

- Die Integration nutzt Polling (alle 30 Sekunden) für Status-Updates
- Display-Steuerung funktioniert parallel zur MQTT-Präsenz-Integration
- Zeitzone-Select zeigt nur die wichtigsten Zeitzonen (ca. 25)

## Unterstützung

Bei Problemen bitte ein Issue auf GitHub erstellen.
