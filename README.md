# 🚀 Telegram Proxy Server with Channel Sponsorship

A complete Telegram proxy solution supporting both SOCKS5 and MTProto protocols with built-in channel sponsorship for marketing purposes. Designed for easy deployment on Railway.app.

## ✨ Features

- **Dual Protocol Support**: Both SOCKS5 and MTProto proxy protocols
- **Channel Sponsorship**: Automatic promotion of your Telegram channel to proxy users
- **Web Dashboard**: Real-time statistics and configuration management
- **Railway.app Ready**: One-click deployment with automatic scaling
- **Security Focused**: Non-root container execution and proper error handling
- **Analytics**: Connection tracking and usage statistics

## 🎯 Marketing Benefits

When users connect through your proxy:
- Your sponsored channel appears in their Telegram chat list
- Automatic channel promotion without revealing user traffic
- Built-in analytics to track proxy usage
- Perfect for growing your Telegram community

## 🚀 Quick Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

### Manual Deployment Steps:

1. **Fork this repository** to your GitHub account

2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app)
   - Click "Deploy from GitHub repo"
   - Select your forked repository

3. **Set Environment Variables**:
   ```
   SPONSOR_CHANNEL=@your_channel_name
   ```

4. **Deploy**: Railway will automatically build and deploy your proxy server

## ⚙️ Configuration

### Required Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SPONSOR_CHANNEL` | Your Telegram channel username | `@my_channel` |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Web interface port | `5000` |
| `PROXY_SECRET` | Custom proxy secret | Auto-generated |
| `SOCKS_PORT` | SOCKS5 proxy port | `1080` |
| `MTPROTO_PORT` | MTProto proxy port | `443` |

## 📱 How to Use

### For SOCKS5 Proxy:
1. Open Telegram settings
2. Go to "Data and Storage" → "Proxy Settings"
3. Add SOCKS5 proxy:
   - **Server**: `your-app.railway.app`
   - **Port**: `1080`

### For MTProto Proxy:
1. Use the generated proxy link from your dashboard
2. Format: `tg://proxy?server=your-app.railway.app&port=443&secret=YOUR_SECRET`
3. Share this link with users or click it to add to Telegram

## 🔧 Local Development

### Prerequisites
- Python 3.11+
- pip

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/telegram-proxy-server.git
cd telegram-proxy-server

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env file with your channel
nano .env

# Run the server
python app.py
```

### Access Points
- **Web Dashboard**: http://localhost:5000
- **SOCKS5 Proxy**: localhost:1080
- **MTProto Proxy**: localhost:443
- **API Stats**: http://localhost:5000/api/stats

## 📊 Web Dashboard

The included web dashboard provides:
- Real-time server status
- Proxy configuration URLs
- Connection statistics
- Channel sponsorship information
- Easy-to-share proxy links

## 🔒 Security Features

- Non-root container execution
- Proper error handling and logging
- Connection rate limiting
- Secure secret generation
- Health check endpoints

## 📈 Analytics & Monitoring

Track your proxy usage with built-in analytics:
- Total connections count
- Connection sources and destinations
- Protocol usage statistics
- Sponsorship effectiveness metrics

## 🛠️ Advanced Configuration

### Custom Proxy Secret
Generate a custom 32-character hex secret:
```bash
openssl rand -hex 16
```

### Multiple Channels
To promote multiple channels, modify the `sponsor_channel` parameter in the code.

### Port Configuration
For Railway deployment, only the web port (PORT) needs to be configured. SOCKS5 and MTProto ports are handled internally.

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t telegram-proxy .

# Run the container
docker run -p 5000:5000 -p 1080:1080 -p 443:443 \
  -e SPONSOR_CHANNEL=@your_channel \
  telegram-proxy
```

## 🔧 Troubleshooting

### Common Issues

1. **Port 443 Permission Denied**
   - On local development, use a different port (e.g., 8443)
   - Railway handles port binding automatically

2. **Channel Not Appearing**
   - Ensure your channel username is correct (include @)
   - Check that the channel is public
   - Verify the MTProto implementation is working

3. **Connection Refused**
   - Check firewall settings
   - Verify the server is listening on 0.0.0.0
   - Ensure Railway environment variables are set

### Logs
Check application logs in Railway dashboard or locally:
```bash
python app.py --debug
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

- Create an issue for bug reports
- Join our Telegram channel for support: [Your Channel]
- Check Railway.app documentation for deployment issues

## ⚠️ Disclaimer

This proxy server is for educational and legitimate use only. Users are responsible for complying with local laws and Telegram's Terms of Service. The channel sponsorship feature should be used ethically and with user consent.

---

**Made with ❤️ for the Telegram community**

