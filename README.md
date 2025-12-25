# Home Assistant Integration für Ikea Obegraensad

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant Integration für die Ikea Obegraensad LED Matrix Uhr.

## Features

- **Display Ein/Aus**: Steuere das Display über Home Assistant
- **Automatisierungen**: Nutze das Display in HA-Automatisierungen
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

Nach der Installation erscheint ein Switch mit dem Namen "Display" in Home Assistant. Dieser kann zum Ein- und Ausschalten des Displays verwendet werden.

### Automatisierung Beispiel

```yaml
automation:
  - alias: "Wohnzimmer Licht an → Display an"
    trigger:
      - platform: state
        entity_id: light.wohnzimmer
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_display
```

## API-Voraussetzungen

Das Arduino-Gerät muss folgende API-Endpoints unterstützen:

- `GET /api/status` - Gibt JSON mit `displayEnabled` zurück
- `GET /api/setDisplay?enabled=true|false` - Setzt Display Ein/Aus

## Voraussetzungen

- Home Assistant 2023.1.0 oder höher
- Ikea Obegraensad Gerät mit Firmware, die `/api/setDisplay` unterstützt

## Bekannte Probleme / Einschränkungen

- Die Integration nutzt Polling (alle 30 Sekunden) für Status-Updates
- Display-Steuerung funktioniert parallel zur MQTT-Präsenz-Integration

## Unterstützung

Bei Problemen bitte ein Issue auf GitHub erstellen.
