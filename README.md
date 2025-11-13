# Hikvision Doorbell Integration

Home Assistant custom integration providing native WebRTC two-way audio support for Hikvision doorbells with low latency.

## Features

- **Native WebRTC two-way audio** - Real-time, low-latency bidirectional audio communication
- **Play audio files** - Send pre-recorded messages to the doorbell speaker
- **Abort operations** - Stop active audio sessions on demand

## Requirements

- [hikvision-doorbell-server](https://github.com/acardace/hikvision-doorbell-server) running and accessible from Home Assistant
- [Frigate](https://frigate.video/) with go2rtc configured for camera streaming
- [Hikvision Doorbell Card](https://github.com/acardace/hikvision-doorbell-card) for WebRTC two-way audio UI
- Hikvision doorbell compatible with ISAPI two-way audio
- Home Assistant accessible via HTTPS (required for browser microphone access)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS:
   - Go to HACS → Integrations
   - Click the three dots menu → Custom repositories
   - Add `https://github.com/acardace/hikvision-doorbell-integration`
   - Category: Integration
2. Click Install
3. Restart Home Assistant
4. Add the integration:
   - Go to Settings → Devices & Services → Add Integration
   - Search for "Hikvision Doorbell Two-Way Audio"
   - Configure the integration:
     - **Server URL**: `https://doorbell-server.example.com`
     - **Frigate URL**: `https://frigate.example.com`
     - **Camera Name**: The camera name as configured in Frigate (e.g., `doorbell`)

### Manual

1. Copy the `custom_components/hikvision_doorbell` directory to your Home Assistant `custom_components` folder
2. Restart Home Assistant
3. Add the integration:
   - Go to Settings → Devices & Services → Add Integration
   - Search for "Hikvision Doorbell Two-Way Audio"
   - Configure the integration:
     - **Server URL**: `https://doorbell-server.example.com`
     - **Frigate URL**: `https://frigate.example.com`
     - **Camera Name**: The camera name as configured in Frigate (e.g., `doorbell`)

## Custom Lovelace Card

For WebRTC two-way audio with a custom UI, install the [Hikvision Doorbell Card](https://github.com/acardace/hikvision-doorbell-card).

## Services

### `hikvision_doorbell.play_file`

Play an audio file through the doorbell speaker.

**Parameters:**
- `entity_id`: The doorbell camera entity
- `audio_file`: Path to the audio file (e.g., `/config/media/chime.wav`)

WAV files are sent directly without conversion. Other formats (MP3, OGG, etc.) are automatically converted to G.711 µ-law using ffmpeg.

**Example:**
```yaml
service: hikvision_doorbell.play_file
data:
  entity_id: camera.doorbell
  audio_file: /config/media/doorbell_chime.mp3
```

### `hikvision_doorbell.abort`

Stop all active operations (play-file and WebRTC sessions) and release audio channels.

**Parameters:**
- `entity_id`: The doorbell camera entity

**Example:**
```yaml
service: hikvision_doorbell.abort
data:
  entity_id: camera.doorbell
```

## Example Automation

Play a welcome message when someone presses the doorbell:

```yaml
automation:
  - alias: "Doorbell - Play Welcome Message"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell_button
        to: "on"
    action:
      - service: hikvision_doorbell.play_file
        data:
          entity_id: camera.hikvision_doorbell
          audio_file: /config/sounds/welcome.wav
```

## Troubleshooting

### WebRTC card not connecting

- Verify microphone permission was granted
- Ensure server URL is accessible from your device
- Check that you're using HTTPS (required for mic access, except on localhost)

### File upload fails

- Ensure file path is accessible to Home Assistant
- Verify server has ffmpeg installed (included in Docker image)
- Check server logs for conversion errors

### ICE connection timeout

- This usually means WebRTC can't establish a connection
- Ensure both Home Assistant and the server are on the same network/VPN
- Check firewall isn't blocking UDP traffic
- The system is designed for local networks only (no STUN/TURN servers)

## Architecture

```
┌─────────────┐         ┌──────────────────┐         ┌─────────────┐
│   Browser   │  WebRTC │  Doorbell Server │  ISAPI  │   Doorbell  │
│  (Lovelace) │◄───────►│   (Go/WebRTC)    │◄───────►│  (Hikvision)│
└─────────────┘         └──────────────────┘         └─────────────┘
                                │
                        ┌───────┴────────┐
                        │  Home Assistant│
                        │   (Services)   │
                        └────────────────┘
```

- **Browser ↔ Server**: WebRTC for real-time bidirectional audio
- **Home Assistant → Server**: HTTP REST API for file uploads
- **Server ↔ Doorbell**: Hikvision ISAPI for audio channel control

## Technical Details

- **Audio Codec**: G.711 µ-law (PCMU) - 8000Hz, mono
- **WebRTC**: Local network only (no external ICE servers)
- **Protocol**: ISAPI over HTTP Digest Authentication
- **Streaming**: RTP over HTTP for doorbell audio channels

## Support

For issues and feature requests:
- **Integration**: https://github.com/acardace/hikvision-doorbell-integration/issues
- **Server**: https://github.com/acardace/hikvision-doorbell-server/issues

## License

Apache License 2.0
