# Hikvision Doorbell Two-Way Audio - Home Assistant Integration

Custom Home Assistant integration for two-way audio communication with Hikvision doorbells using WebRTC.

## Features

- 🎥 Camera entity with RTSP video stream
- 🎤 **WebRTC-based two-way audio** via custom Lovelace card
- 📢 Service to send pre-recorded audio files to doorbell
- 🚀 Real-time, low-latency audio streaming
- 🎨 Beautiful custom UI card with visual feedback
- 🔒 Local network only (no external servers required)
- 🌐 Works with Home Assistant Container, Core, Supervised, and OS

## Prerequisites

You need the **Hikvision Doorbell Server** running and accessible from Home Assistant:

Repository: https://github.com/acardace/hikvision-doorbell-server

### Quick Start (Docker/Podman)

```bash
# Create config.yaml
cat > config.yaml <<EOF
doorbell:
  host: "192.168.1.100"
  username: "admin"
  password: "your_password"
server:
  host: "0.0.0.0"
  port: 8080
EOF

# Run server
docker run -d \
  --name hikvision-doorbell-server \
  -p 8080:8080 \
  -v $(pwd)/config.yaml:/app/config.yaml:ro \
  ghcr.io/acardace/hikvision-doorbell-server:latest
```

### Kubernetes Deployment

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: doorbell-config
data:
  config.yaml: |
    doorbell:
      host: "192.168.1.100"
      username: "admin"
      password: "your_password"
    server:
      host: "0.0.0.0"
      port: 8080
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hikvision-doorbell-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hikvision-doorbell
  template:
    metadata:
      labels:
        app: hikvision-doorbell
    spec:
      containers:
      - name: server
        image: ghcr.io/acardace/hikvision-doorbell-server:latest
        ports:
        - containerPort: 8080
        volumeMounts:
        - name: config
          mountPath: /app/config.yaml
          subPath: config.yaml
      volumes:
      - name: config
        configMap:
          name: doorbell-config
---
apiVersion: v1
kind: Service
metadata:
  name: hikvision-doorbell-server
spec:
  selector:
    app: hikvision-doorbell
  ports:
  - port: 8080
    targetPort: 8080
```

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Hikvision Doorbell" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/hikvision_doorbell` directory to your Home Assistant `config/custom_components/` directory
2. Copy the `www/hikvision-doorbell-card.js` file to your `config/www/` directory
3. Restart Home Assistant
4. Add Lovelace resource (see Custom Card section)

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Hikvision Doorbell"
4. Enter your configuration:
   - **Server URL**: URL to the server (e.g., `http://192.168.1.50:8080` or `http://hikvision-doorbell-server:8080`)
   - **RTSP URL** (optional): Your doorbell's RTSP stream URL (e.g., `rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101`)
5. Click Submit

## Usage

### Custom Lovelace Card (WebRTC Two-Way Audio)

The integration includes a custom Lovelace card for real-time two-way audio communication.

#### Setup

1. **Add Resource** (only needed for manual installation):
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click "Add Resource"
   - URL: `/hacsfiles/hikvision_doorbell/hikvision-doorbell-card.js`
   - Resource type: **JavaScript Module**

2. **Add Card to Dashboard**:

   ```yaml
   type: custom:hikvision-doorbell-card
   entity: camera.hikvision_doorbell
   name: Front Door
   ```

#### How to Use

1. Click "Start Talking" button
2. Allow microphone access when prompted
3. Wait for WebRTC connection (usually < 2 seconds)
4. Speak through your microphone - you'll hear doorbell audio too
5. Click "Stop Talking" when done

**Browser Requirements**: Chrome 90+, Firefox 88+, Safari 14.1+, or mobile browsers with WebRTC support.

### Send Audio File Service

Send a pre-recorded audio file to the doorbell speaker (any format - MP3, WAV, OGG, etc.):

```yaml
service: hikvision_doorbell.send_file
target:
  entity_id: camera.hikvision_doorbell
data:
  audio_file: /config/doorbell_message.mp3
```

**Note**: The server automatically converts audio to G.711 µ-law format required by the doorbell.

### Example Automation

Play a welcome message when someone presses the doorbell:

```yaml
automation:
  - alias: "Doorbell Pressed - Play Welcome"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell_button
        to: "on"
    action:
      - service: hikvision_doorbell.send_file
        target:
          entity_id: camera.hikvision_doorbell
        data:
          audio_file: /config/sounds/welcome.mp3
```

### Dashboard Examples

#### Simple Two-Way Audio Card

```yaml
type: custom:hikvision-doorbell-card
entity: camera.hikvision_doorbell
```

#### Combined Video + Audio Card

```yaml
type: vertical-stack
cards:
  - type: picture-entity
    entity: camera.hikvision_doorbell
    camera_view: live
  - type: custom:hikvision-doorbell-card
    entity: camera.hikvision_doorbell
    name: Talk to Visitor
```

#### Grid Layout

```yaml
type: grid
columns: 2
cards:
  - type: picture-entity
    entity: camera.hikvision_doorbell
    camera_view: live
  - type: custom:hikvision-doorbell-card
    entity: camera.hikvision_doorbell
  - type: button
    name: Play Welcome
    tap_action:
      action: call-service
      service: hikvision_doorbell.send_file
      service_data:
        entity_id: camera.hikvision_doorbell
        audio_file: /config/sounds/welcome.mp3
  - type: button
    name: Play Away Message
    tap_action:
      action: call-service
      service: hikvision_doorbell.send_file
      service_data:
        entity_id: camera.hikvision_doorbell
        audio_file: /config/sounds/away.mp3
```

## Advanced Usage

### CLI Tool

The server includes a CLI tool for testing:

```bash
# Send audio file
./doorbell-cli send -f message.mp3 -s http://192.168.1.50:8080

# Two-way audio from terminal
./doorbell-cli speak -s http://192.168.1.50:8080
```

### Audio Conversion (Optional)

While the server handles conversion automatically, you can pre-convert files for faster playback:

```bash
ffmpeg -i input.mp3 -ar 8000 -ac 1 -f mulaw output.raw
```

## Troubleshooting

### Cannot connect to server

- Verify server is running: `curl http://SERVER_URL/healthz`
- Check the server URL in integration configuration
- Ensure firewall rules allow access to port 8080
- Check server logs: `docker logs hikvision-doorbell-server`

### WebRTC card not connecting

- Ensure browser supports WebRTC (Chrome 90+, Firefox 88+, Safari 14.1+)
- Check browser console for errors (F12 → Console)
- Verify microphone permission was granted
- Ensure server URL is accessible from your device
- Try reloading the page
- Check that you're using HTTPS (required for mic access, except on localhost)

### No audio from doorbell

- Check device audio output settings
- Ensure browser audio isn't muted
- Verify RTSP stream works (test with VLC)
- Check server logs for errors

### File upload fails

- Ensure file path is accessible to Home Assistant
- Check file format is supported (MP3, WAV, OGG, FLAC, etc.)
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

MIT License - see individual repositories for details.
