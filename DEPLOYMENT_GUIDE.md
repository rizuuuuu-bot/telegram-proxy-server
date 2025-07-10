# 🚀 Complete Deployment Guide for Telegram Proxy Server

## Table of Contents
1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Railway.app Deployment](#railwayapp-deployment)
3. [Environment Configuration](#environment-configuration)
4. [Testing and Verification](#testing-and-verification)
5. [Channel Sponsorship Setup](#channel-sponsorship-setup)
6. [User Distribution](#user-distribution)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Pre-Deployment Checklist

### 1. Telegram Channel Preparation
Before deploying your proxy server, ensure you have:

- **Created your Telegram channel** for marketing purposes
- **Made the channel public** (users must be able to find it)
- **Noted the exact channel username** (including the @ symbol)
- **Added initial content** to make the channel attractive to new subscribers

### 2. GitHub Repository Setup
- Fork or create a new repository from this codebase
- Ensure all files are committed and pushed to your main branch
- Verify that sensitive information is not included in the repository

### 3. Railway.app Account
- Create a free account at [Railway.app](https://railway.app)
- Connect your GitHub account to Railway
- Verify your account if required for deployment

## Railway.app Deployment

### Method 1: One-Click Deploy (Recommended)

1. **Click the Deploy Button**
   ```
   [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
   ```

2. **Configure Repository**
   - Select "Deploy from GitHub repo"
   - Choose your forked repository
   - Select the main branch

3. **Set Environment Variables**
   - `SPONSOR_CHANNEL`: Your channel username (e.g., `@my_marketing_channel`)
   - Railway will automatically set `PORT` for the web interface

4. **Deploy**
   - Click "Deploy" and wait for the build process to complete
   - Railway will provide you with a public URL

### Method 2: Manual Deployment

1. **Login to Railway**
   ```bash
   # Install Railway CLI (optional)
   npm install -g @railway/cli
   railway login
   ```

2. **Create New Project**
   - Go to Railway dashboard
   - Click "New Project"
   - Select "Deploy from GitHub repo"

3. **Configure Build Settings**
   - Railway will automatically detect the Dockerfile
   - Build command: `docker build .`
   - Start command: `python app.py`

4. **Set Environment Variables**
   - Navigate to project settings
   - Add environment variables:
     ```
     SPONSOR_CHANNEL=@your_channel_name
     ```

5. **Deploy**
   - Push changes to trigger automatic deployment
   - Monitor build logs for any issues

## Environment Configuration

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `SPONSOR_CHANNEL` | Your Telegram channel username | `@my_channel` | ✅ Yes |

### Optional Variables

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `PORT` | Web interface port | `5000` | Set by Railway |
| `PROXY_SECRET` | Custom proxy secret | Auto-generated | 32-char hex |
| `SOCKS_PORT` | SOCKS5 proxy port | `1080` | Internal use |
| `MTPROTO_PORT` | MTProto proxy port | `443` | Internal use |

### Setting Environment Variables in Railway

1. **Via Dashboard**:
   - Go to your project dashboard
   - Click on "Variables" tab
   - Add new variable: `SPONSOR_CHANNEL` = `@your_channel`
   - Click "Add" and redeploy

2. **Via CLI**:
   ```bash
   railway variables set SPONSOR_CHANNEL=@your_channel
   ```

## Testing and Verification

### 1. Health Check
After deployment, verify your server is running:
```bash
curl https://your-app.railway.app/health
```
Expected response:
```json
{"status": "healthy", "service": "telegram-proxy"}
```

### 2. Web Dashboard Access
Visit your Railway app URL to access the web dashboard:
- URL: `https://your-app.railway.app`
- Check server status, proxy URLs, and statistics

### 3. API Endpoints Testing
Test the API endpoints:
```bash
# Get statistics
curl https://your-app.railway.app/api/stats

# Get configuration
curl https://your-app.railway.app/api/config
```

### 4. SOCKS5 Proxy Testing
Test SOCKS5 functionality:
```bash
curl --socks5 your-app.railway.app:1080 http://httpbin.org/ip
```

### 5. MTProto Proxy Testing
1. Copy the MTProto URL from your dashboard
2. Open Telegram on your device
3. Click the proxy link to add it
4. Verify connection in Telegram settings

## Channel Sponsorship Setup

### 1. Official MTProto Registration
For full MTProto sponsorship features:

1. **Contact @MTProxybot** on Telegram
2. **Send command**: `/newproxy`
3. **Provide your server details**:
   - Server: `your-app.railway.app`
   - Port: `443`
   - Secret: (from your dashboard)
4. **Receive proxy tag** for enhanced sponsorship
5. **Update environment variables** with the received tag

### 2. Channel Promotion Strategy
Your sponsored channel will appear to users when they:
- Connect through your SOCKS5 proxy
- Use your MTProto proxy link
- Access Telegram through your server

### 3. Content Strategy
Optimize your channel for new subscribers:
- **Welcome message** explaining the proxy service
- **Regular valuable content** to retain subscribers
- **Clear channel description** and purpose
- **Engaging posts** to encourage interaction

## User Distribution

### 1. Proxy URL Generation
Your dashboard provides ready-to-share URLs:

**SOCKS5 Configuration**:
```
Server: your-app.railway.app
Port: 1080
Type: SOCKS5
```

**MTProto Link**:
```
tg://proxy?server=your-app.railway.app&port=443&secret=YOUR_SECRET
```

### 2. Distribution Channels
Share your proxy through:
- **Social media platforms**
- **Telegram groups and channels**
- **Forums and communities**
- **Direct messaging**
- **QR codes** for mobile users

### 3. User Instructions
Provide clear setup instructions:

**For Android/iOS**:
1. Open Telegram
2. Go to Settings → Data and Storage
3. Tap "Proxy Settings"
4. Add new proxy with provided details

**For Desktop**:
1. Open Telegram Desktop
2. Go to Settings → Advanced → Connection Type
3. Select "Use custom proxy"
4. Enter proxy details

## Monitoring and Maintenance

### 1. Railway Dashboard Monitoring
Monitor your deployment through Railway dashboard:
- **Build logs**: Check for deployment issues
- **Application logs**: Monitor runtime errors
- **Metrics**: Track CPU, memory, and network usage
- **Deployments**: View deployment history

### 2. Application Monitoring
Use the built-in web dashboard to monitor:
- **Connection statistics**: Total and recent connections
- **Server status**: Health and uptime
- **Proxy configuration**: Current settings and URLs
- **Channel performance**: Sponsorship effectiveness

### 3. Log Analysis
Monitor application logs for:
- Connection patterns and usage
- Error rates and types
- Performance bottlenecks
- Security incidents

### 4. Regular Maintenance Tasks

**Weekly**:
- Check server health and performance
- Review connection statistics
- Update channel content
- Monitor user feedback

**Monthly**:
- Review and update proxy secrets if needed
- Analyze usage patterns
- Optimize server configuration
- Update dependencies if required

## Troubleshooting

### Common Deployment Issues

**1. Build Failures**
```
Error: Failed to build Docker image
```
**Solution**:
- Check Dockerfile syntax
- Verify all required files are in repository
- Review build logs for specific errors
- Ensure requirements.txt is correct

**2. Environment Variable Issues**
```
Error: SPONSOR_CHANNEL not set
```
**Solution**:
- Verify environment variables in Railway dashboard
- Ensure variable names are correct
- Redeploy after setting variables

**3. Port Binding Issues**
```
Error: Permission denied binding to port 443
```
**Solution**:
- Railway handles port binding automatically
- Ensure your app listens on 0.0.0.0
- Use PORT environment variable for web interface

### Runtime Issues

**1. Proxy Connection Failures**
**Symptoms**: Users cannot connect through proxy
**Solutions**:
- Check server health endpoint
- Verify proxy ports are accessible
- Review application logs for errors
- Test proxy functionality manually

**2. Channel Sponsorship Not Working**
**Symptoms**: Sponsored channel not appearing
**Solutions**:
- Verify channel username is correct
- Ensure channel is public
- Check MTProto implementation
- Contact @MTProxybot for official registration

**3. High Resource Usage**
**Symptoms**: Server running slowly or crashing
**Solutions**:
- Monitor connection limits
- Implement rate limiting
- Upgrade Railway plan if needed
- Optimize connection handling

### Performance Optimization

**1. Connection Limits**
- Monitor concurrent connections
- Implement connection pooling
- Set appropriate timeouts
- Use connection rate limiting

**2. Resource Management**
- Monitor memory usage
- Optimize logging levels
- Clean up inactive connections
- Use efficient data structures

**3. Scaling Considerations**
- Monitor user growth
- Plan for traffic spikes
- Consider load balancing
- Implement caching where appropriate

### Getting Help

**1. Railway Support**
- Check Railway documentation
- Use Railway community Discord
- Submit support tickets for platform issues

**2. Application Support**
- Review application logs
- Check GitHub issues
- Create detailed bug reports
- Test in local environment first

**3. Telegram Proxy Support**
- Consult Telegram proxy documentation
- Join proxy-related communities
- Test with official Telegram clients
- Verify compliance with Telegram ToS

---

## Success Metrics

Track your proxy server success with these metrics:

### Technical Metrics
- **Uptime**: Target 99.9% availability
- **Response time**: Web dashboard < 2 seconds
- **Connection success rate**: > 95%
- **Error rate**: < 1%

### Business Metrics
- **Channel subscribers**: Track growth from proxy users
- **User retention**: Monitor repeat proxy usage
- **Geographic distribution**: Understand user locations
- **Usage patterns**: Peak times and connection duration

### Optimization Goals
- **Minimize latency**: Optimize proxy performance
- **Maximize reliability**: Ensure consistent service
- **Improve user experience**: Simplify setup process
- **Grow channel audience**: Effective sponsorship strategy

By following this comprehensive deployment guide, you'll have a fully functional Telegram proxy server with channel sponsorship capabilities running on Railway.app, ready to serve users and grow your Telegram community.

