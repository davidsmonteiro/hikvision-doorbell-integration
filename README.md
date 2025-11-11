# Hikvision Doorbell Two-Way Audio - Home Assistant Integration

Custom Home Assistant integration for two-way audio communication with Hikvision doorbells.

## Features

- Camera entity with RTSP video stream
- Three service calls for two-way audio:
  - `start_2way` - Start two-way audio session
  - `stop_2way` - Stop two-way audio session
  - `send_file` - Send pre-recorded audio file to doorbell
- Easy configuration via UI
- Works with Home Assistant Container, Core, and Supervised

## Prerequisites

You need the **Hikvision Doorbell Middleware** running and accessible from Home Assistant:

- For Home Assistant OS/Supervised: Install the [Hikvision Doorbell Addon](https://github.com/acardace/hikvision-doorbell-homeassistant)
- For Home Assistant Container/Core: Run the middleware yourself (see below)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "Hikvision Doorbell" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/hikvision_doorbell` directory to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Running the Middleware (For Container/Core users)

If you're using Home Assistant Container or Core, you need to run the middleware separately.

### Using Docker/Podman:

```bash
docker run -d \
  --name hikvision-doorbell-middleware \
  -p 8080:8080 \
  -e DOORBELL_HOST='192.168.1.100' \
  -e DOORBELL_USERNAME='admin' \
  -e DOORBELL_PASSWORD='your_password' \
  ghcr.io/acardace/hikvision-doorbell-amd64:latest
```

### Using Kubernetes:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hikvision-doorbell-middleware
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
      - name: middleware
        image: ghcr.io/acardace/hikvision-doorbell-amd64:latest
        ports:
        - containerPort: 8080
        env:
        - name: DOORBELL_HOST
          value: "192.168.1.100"
        - name: DOORBELL_USERNAME
          value: "admin"
        - name: DOORBELL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: doorbell-secret
              key: password
---
apiVersion: v1
kind: Service
metadata:
  name: hikvision-doorbell-middleware
spec:
  selector:
    app: hikvision-doorbell
  ports:
  - port: 8080
    targetPort: 8080
```

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Hikvision Doorbell"
4. Enter your configuration:
   - **Middleware URL**: URL to the middleware (e.g., `http://localhost:8080` or `http://hikvision-doorbell-middleware:8080`)
   - **RTSP URL** (optional): Your doorbell's RTSP stream URL (e.g., `rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101`)
5. Click Submit

## Usage

### Services

#### Start Two-Way Audio Session

```yaml
service: hikvision_doorbell.start_2way
target:
  entity_id: camera.hikvision_doorbell
```

#### Stop Two-Way Audio Session

```yaml
service: hikvision_doorbell.stop_2way
target:
  entity_id: camera.hikvision_doorbell
```

#### Send Audio File

```yaml
service: hikvision_doorbell.send_file
target:
  entity_id: camera.hikvision_doorbell
data:
  audio_file: /config/doorbell_message.raw
```

**Note**: Audio file must be in G.711 µ-law format (8000Hz, mono). You can convert files using ffmpeg:

```bash
ffmpeg -i input.mp3 -ar 8000 -ac 1 -f mulaw output.raw
```

### Example Automation

```yaml
automation:
  - alias: "Doorbell Pressed - Play Message"
    trigger:
      - platform: state
        entity_id: binary_sensor.doorbell_button
        to: "on"
    action:
      - service: hikvision_doorbell.start_2way
        target:
          entity_id: camera.hikvision_doorbell
      - delay:
          seconds: 1
      - service: hikvision_doorbell.send_file
        target:
          entity_id: camera.hikvision_doorbell
        data:
          audio_file: /config/welcome_message.raw
      - delay:
          seconds: 5
      - service: hikvision_doorbell.stop_2way
        target:
          entity_id: camera.hikvision_doorbell
```

### Dashboard Card

```yaml
type: picture-glance
title: Front Door
camera_image: camera.hikvision_doorbell
entities:
  - entity: camera.hikvision_doorbell
tap_action:
  action: call-service
  service: hikvision_doorbell.start_2way
  service_data:
    entity_id: camera.hikvision_doorbell
hold_action:
  action: call-service
  service: hikvision_doorbell.stop_2way
  service_data:
    entity_id: camera.hikvision_doorbell
```

## Troubleshooting

### Cannot connect to middleware

- Verify middleware is running and accessible
- Check the middleware URL in the integration configuration
- Ensure firewall rules allow access to port 8080

### Audio not playing

- Ensure you called `start_2way` before sending audio
- Verify audio file is in correct format (G.711 µ-law, 8000Hz, mono)
- Check middleware logs for errors
- Call `stop_2way` when done to free up the channel

### Session already active error

- Call `stop_2way` to close any existing session
- Restart the middleware if the session is stuck

## Support

For issues and feature requests:
- Integration: https://github.com/acardace/hikvision-doorbell-integration/issues
- Middleware: https://github.com/acardace/hikvision-doorbell-homeassistant/issues
