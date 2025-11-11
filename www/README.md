# Hikvision Doorbell WebRTC Card

A custom Lovelace card for two-way audio communication with Hikvision doorbells using WebRTC.

## Features

- 🎤 **Two-way audio**: Speak to and hear from your doorbell in real-time
- 🌐 **WebRTC-based**: Low latency, peer-to-peer audio streaming
- 🎨 **Beautiful UI**: Clean, modern interface with visual feedback
- 🔒 **Local network**: No external servers required (works over LAN/VPN)
- 📱 **Mobile friendly**: Works on both desktop and mobile browsers

## Installation

### Via HACS (Recommended)

When this integration is added to HACS, the card will be automatically installed.

### Manual Installation

1. Copy `hikvision-doorbell-card.js` to your `www` folder (create if it doesn't exist)
2. Add the following to your Lovelace resources:

   **Using UI:**
   - Go to Settings → Dashboards → Resources
   - Click "Add Resource"
   - URL: `/hacsfiles/hikvision_doorbell/hikvision-doorbell-card.js`
   - Resource type: JavaScript Module

   **Using YAML:**
   ```yaml
   resources:
     - url: /hacsfiles/hikvision_doorbell/hikvision-doorbell-card.js
       type: module
   ```

## Configuration

### Minimal Configuration

```yaml
type: custom:hikvision-doorbell-card
entity: camera.doorbell
```

### Full Configuration

```yaml
type: custom:hikvision-doorbell-card
entity: camera.doorbell
name: Front Door
```

### Configuration Options

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `type` | string | **Yes** | - | Must be `custom:hikvision-doorbell-card` |
| `entity` | string | **Yes** | - | Camera entity ID |
| `name` | string | No | Entity name | Display name for the card |

## Usage

1. **Click "Start Talking"** - The card will request microphone permission
2. **Allow microphone access** - Your browser will prompt for permission
3. **Wait for connection** - The card will establish a WebRTC connection
4. **Speak** - Once connected, you can speak through your doorbell
5. **Listen** - You'll also hear audio from the doorbell
6. **Click "Stop Talking"** - Ends the audio session

## Browser Compatibility

This card requires a modern browser with WebRTC support:

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14.1+
- ✅ Mobile browsers (iOS Safari 14.1+, Chrome Mobile)

**Note:** HTTPS is required for microphone access (except on localhost).

## Troubleshooting

### Microphone permission denied
- Check your browser's site permissions
- Ensure you're using HTTPS (required for getUserMedia API)
- Try reloading the page and allowing permission again

### Connection timeout
- Verify the server URL in the camera entity attributes
- Check that the doorbell server is running and accessible
- Ensure your network allows WebRTC connections (no restrictive firewalls)
- Check browser console for detailed error messages

### No audio from doorbell
- Check your device's audio output settings
- Ensure audio isn't muted in your browser
- Try restarting the audio session

### Audio quality issues
- Check your network connection
- Reduce distance from Wi-Fi router
- Close other bandwidth-intensive applications

## Advanced

### Server URL Override

The card automatically reads the server URL from the camera entity's `server_url` attribute. To manually override:

```javascript
// Not currently supported - server URL is always read from entity attributes
```

### Customizing Styles

The card uses Home Assistant's CSS variables. You can customize colors by overriding:

```yaml
type: custom:hikvision-doorbell-card
entity: camera.doorbell
card_mod:
  style: |
    .talk-button {
      background-color: #00a8e1 !important;
    }
```

## Development

To modify the card:

1. Edit `hikvision-doorbell-card.js`
2. Clear browser cache or add `?v=X` to the resource URL
3. Reload Lovelace

## Support

For issues, feature requests, or contributions, visit:
https://github.com/acardace/hikvision-doorbell-integration

## License

This card is part of the Hikvision Doorbell Integration.
