# MyLog Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/LL0rd/homeassistant-mylog.svg)](https://github.com/LL0rd/homeassistant-mylog/releases)
[![License](https://img.shields.io/github/license/LL0rd/homeassistant-mylog.svg)](LICENSE)

A Home Assistant integration for [MyLog](https://mylog.zip) - send log entries directly from your smart home automations.

## Features

- Easy GUI-based configuration
- Send log entries via Home Assistant services
- Support for all MyLog entry fields (title, content, severity, tags, location, etc.)
- Batch logging support for multiple entries
- English and German translations

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add `https://github.com/LL0rd/homeassistant-mylog` as an Integration
6. Click "Install"
7. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Copy the `custom_components/mylog` folder to your Home Assistant `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services** → **Add Integration**
2. Search for "MyLog"
3. Enter your API key (obtain one from [mylog.zip](https://mylog.zip) under Settings → API Keys)
4. Click Submit

## Services

### mylog.send_log

Send a single log entry to MyLog.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Log entry title (max 500 chars) |
| `content` | string | No | Log entry content/message |
| `type_name` | string | No | Name of the log type |
| `type_id` | integer | No | ID of the log type |
| `severity` | string | No | `info`, `low`, `medium`, `high`, `critical` (default: `info`) |
| `priority` | integer | No | Priority 0-100 (default: 0) |
| `status` | string | No | `draft`, `active`, `archived` (default: `active`) |
| `tags` | list | No | List of tags |
| `location_name` | string | No | Location name |
| `location_lat` | float | No | Latitude (-90 to 90) |
| `location_lng` | float | No | Longitude (-180 to 180) |
| `occurred_at` | string | No | ISO 8601 datetime |
| `is_favourite` | boolean | No | Mark as favourite |
| `is_starred` | boolean | No | Mark as starred |
| `is_pinned` | boolean | No | Mark as pinned |
| `is_public` | boolean | No | Make entry public |
| `external_ref_id` | string | No | External reference ID |

### mylog.send_batch

Send multiple log entries in a single request (max 100 entries).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `entries` | list | Yes | List of log entry objects |

## Example Automations

### Log Motion Detection

```yaml
automation:
  - alias: "Log Motion Detection"
    trigger:
      - platform: state
        entity_id: binary_sensor.living_room_motion
        to: "on"
    action:
      - service: mylog.send_log
        data:
          title: "Motion Detected"
          content: "Motion detected in {{ trigger.to_state.attributes.friendly_name }}"
          type_name: "Home Assistant"
          severity: "info"
          tags:
            - motion
            - security
          location_name: "Living Room"
```

### Log Temperature Alert

```yaml
automation:
  - alias: "Log Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.outdoor_temperature
        above: 35
    action:
      - service: mylog.send_log
        data:
          title: "High Temperature Alert"
          content: "Outdoor temperature is {{ states('sensor.outdoor_temperature') }}°C"
          severity: "high"
          tags:
            - temperature
            - alert
```

### Log Home Assistant Start

```yaml
automation:
  - alias: "Log HA Start"
    trigger:
      - platform: homeassistant
        event: start
    action:
      - service: mylog.send_log
        data:
          title: "Home Assistant Started"
          content: "Home Assistant has been restarted"
          severity: "info"
          tags:
            - system
```

## Requirements

- Home Assistant 2024.1.0 or newer
- A MyLog account with an API key

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues, please [open an issue](https://github.com/LL0rd/homeassistant-mylog/issues) on GitHub.
