#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Proxy Server with Channel Sponsorship
Supports both SOCKS5 and MTProto protocols
Designed for Railway.app deployment
"""

import os
import sys
import json
import time
import socket
import struct
import select
import threading
import logging
import argparse
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class TelegramProxyServer:
    def __init__(self, host='0.0.0.0', socks_port=1080, mtproto_port=443, 
                 sponsor_channel=None, proxy_secret=None):
        self.host = host
        self.socks_port = socks_port
        self.mtproto_port = mtproto_port
        self.sponsor_channel = sponsor_channel or os.getenv('SPONSOR_CHANNEL', '@your_channel')
        self.proxy_secret = proxy_secret or os.getenv('PROXY_SECRET', self.generate_secret())
        self.running = False
        self.connections = []
        
    def generate_secret(self):
        """Generate a random 32-character hex secret"""
        import secrets
        return secrets.token_hex(16)
    
    def start_socks5_server(self):
        """Start SOCKS5 proxy server"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.socks_port))
            server_socket.listen(5)
            logger.info(f"SOCKS5 server listening on {self.host}:{self.socks_port}")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    logger.info(f"SOCKS5 connection from {addr}")
                    thread = threading.Thread(
                        target=self.handle_socks5_client,
                        args=(client_socket,)
                    )
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"SOCKS5 server error: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start SOCKS5 server: {e}")
    
    def handle_socks5_client(self, client_socket):
        """Handle SOCKS5 client connection"""
        try:
            # SOCKS5 greeting (VER, NMETHODS, METHODS)
            data = client_socket.recv(262)
            if not data or len(data) < 2 or data[0] != 0x05: # SOCKS5 version
                logger.warning(f"Invalid SOCKS5 greeting from {client_socket.getpeername()}: {data.hex()}")
                client_socket.close()
                return
            
            nmethods = data[1]
            methods = data[2:2+nmethods]

            # Check for NO AUTHENTICATION REQUIRED (0x00)
            if 0x00 not in methods:
                logger.warning(f"No supported SOCKS5 authentication method from {client_socket.getpeername()}. Methods: {methods.hex()}")
                client_socket.send(b'\x05\xFF') # No acceptable methods
                client_socket.close()
                return
            
            # Send NO AUTHENTICATION REQUIRED (VER, METHOD)
            client_socket.send(b'\x05\x00')
            
            # Receive connection request (VER, CMD, RSV, ATYP, DST.ADDR, DST.PORT)
            data = client_socket.recv(4)
            if not data or len(data) < 4 or data[0] != 0x05 or data[2] != 0x00: # SOCKS5 version, RSV
                logger.warning(f"Invalid SOCKS5 request header from {client_socket.getpeername()}: {data.hex()}")
                client_socket.close()
                return
            
            cmd = data[1]
            if cmd != 0x01: # Only CONNECT command is supported
                logger.warning(f"Unsupported SOCKS5 command {cmd} from {client_socket.getpeername()}")
                client_socket.send(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00') # Command not supported
                client_socket.close()
                return

            # Parse address
            addr_type = data[3]
            addr = None
            port = None

            if addr_type == 0x01:  # IPv4
                addr_data = client_socket.recv(6)
                if len(addr_data) < 6:
                    logger.warning(f"Incomplete IPv4 address data from {client_socket.getpeername()}")
                    client_socket.close()
                    return
                addr = socket.inet_ntoa(addr_data[:4])
                port = struct.unpack('>H', addr_data[4:6])[0]
            elif addr_type == 0x03:  # Domain name
                addr_len_byte = client_socket.recv(1)
                if not addr_len_byte:
                    logger.warning(f"Missing domain length byte from {client_socket.getpeername()}")
                    client_socket.close()
                    return
                addr_len = addr_len_byte[0]
                addr_data = client_socket.recv(addr_len + 2)
                if len(addr_data) < addr_len + 2:
                    logger.warning(f"Incomplete domain name data from {client_socket.getpeername()}")
                    client_socket.close()
                    return
                addr = addr_data[:addr_len].decode('utf-8')
                port = struct.unpack('>H', addr_data[addr_len:addr_len+2])[0]
            else:
                logger.warning(f"Unsupported SOCKS5 address type {addr_type} from {client_socket.getpeername()}")
                client_socket.send(b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00') # Address type not supported
                client_socket.close()
                return
            
            logger.info(f"SOCKS5 connecting to target: {addr}:{port}")
            # Connect to target server
            try:
                target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                target_socket.connect((addr, port))
                
                # Send success response (VER, REP, RSV, ATYP, BND.ADDR, BND.PORT)
                client_socket.send(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00') # Success, BND.ADDR and BND.PORT are 0.0.0.0:0
                
                # Log connection for sponsorship tracking
                self.log_connection(client_socket.getpeername(), addr, port)
                
                # Relay data between client and target
                self.relay_data(client_socket, target_socket)
                
            except Exception as e:
                logger.error(f"Failed to connect to {addr}:{port} - {e}")
                client_socket.send(b'\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00') # General SOCKS server failure
                client_socket.close()
                
        except Exception as e:
            logger.error(f"SOCKS5 client handler error for {client_socket.getpeername()}: {e}")
        finally:
            try:
                client_socket.close()
            except Exception as e:
                logger.error(f"Error closing SOCKS5 client socket: {e}")
    
    def start_mtproto_server(self):
        """Start MTProto proxy server (simplified implementation)"""
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.mtproto_port))
            server_socket.listen(5)
            logger.info(f"MTProto server listening on {self.host}:{self.mtproto_port}")
            
            while self.running:
                try:
                    client_socket, addr = server_socket.accept()
                    logger.info(f"MTProto connection from {addr}")
                    thread = threading.Thread(
                        target=self.handle_mtproto_client,
                        args=(client_socket,)
                    )
                    thread.daemon = True
                    thread.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"MTProto server error: {e}")
                        
        except Exception as e:
            logger.error(f"Failed to start MTProto server: {e}")
    
    def handle_mtproto_client(self, client_socket):
        """Handle MTProto client connection with channel sponsorship"""
        try:
            # Simplified MTProto handshake
            # In a real implementation, this would handle the full MTProto protocol
            
            # Log connection for sponsorship
            self.log_connection(client_socket.getpeername(), "telegram", 443, protocol="MTProto")
            
            # For now, we'll implement a basic relay to Telegram servers
            # In production, this would include proper MTProto encryption and channel injection
            
            # Connect to Telegram server
            telegram_servers = [
                "149.154.175.50",  # DC2
                "149.154.167.51",  # DC4
                "91.108.56.130",   # DC5
            ]
            
            for server in telegram_servers:
                try:
                    target_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    target_socket.connect((server, 443))
                    
                    # Inject channel sponsorship information
                    self.inject_channel_sponsorship(client_socket)
                    
                    # Relay data
                    self.relay_data(client_socket, target_socket)
                    break
                    
                except Exception as e:
                    logger.error(f"Failed to connect to Telegram server {server}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"MTProto client error: {e}")
        finally:
            client_socket.close()
    
    def inject_channel_sponsorship(self, client_socket):
        """Inject channel sponsorship information into the connection"""
        try:
            # This is a simplified implementation
            # In a real MTProto proxy, this would be integrated into the protocol flow
            sponsorship_data = {
                "sponsored_channel": self.sponsor_channel,
                "proxy_id": self.proxy_secret[:8],
                "timestamp": int(time.time())
            }
            logger.info(f"Injecting sponsorship for channel: {self.sponsor_channel}")
            
            # In a real implementation, this would be encoded in MTProto format
            # and sent at the appropriate time in the protocol handshake
            
        except Exception as e:
            logger.error(f"Failed to inject sponsorship: {e}")
    
    def relay_data(self, client_socket, target_socket):
        """Relay data between client and target sockets"""
        try:
            sockets = [client_socket, target_socket]
            while True:
                ready, _, _ = select.select(sockets, [], [], 60)
                if not ready:
                    break
                    
                for sock in ready:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return
                            
                        if sock is client_socket:
                            target_socket.send(data)
                        else:
                            client_socket.send(data)
                            
                    except Exception as e:
                        logger.error(f"Relay error: {e}")
                        return
                        
        except Exception as e:
            logger.error(f"Relay data error: {e}")
        finally:
            try:
                client_socket.close()
                target_socket.close()
            except:
                pass
    
    def log_connection(self, client_addr, target_addr, target_port, protocol="SOCKS5"):
        """Log connection for analytics and sponsorship tracking"""
        connection_info = {
            "timestamp": time.time(),
            "client_ip": client_addr[0],
            "client_port": client_addr[1],
            "target_addr": target_addr,
            "target_port": target_port,
            "protocol": protocol,
            "sponsor_channel": self.sponsor_channel
        }
        self.connections.append(connection_info)
        logger.info(f"Connection logged: {protocol} {client_addr} -> {target_addr}:{target_port}")
    
    def start(self):
        """Start both proxy servers"""
        self.running = True
        
        # Start SOCKS5 server in a separate thread
        socks5_thread = threading.Thread(target=self.start_socks5_server)
        socks5_thread.daemon = True
        socks5_thread.start()
        
        # Start MTProto server in a separate thread
        mtproto_thread = threading.Thread(target=self.start_mtproto_server)
        mtproto_thread.daemon = True
        mtproto_thread.start()
        
        logger.info("Telegram Proxy Server started successfully")
        logger.info(f"SOCKS5 Proxy: {self.host}:{self.socks_port}")
        logger.info(f"MTProto Proxy: {self.host}:{self.mtproto_port}")
        logger.info(f"Sponsor Channel: {self.sponsor_channel}")
        logger.info(f"Proxy Secret: {self.proxy_secret}")
    
    def stop(self):
        """Stop the proxy server"""
        self.running = False
        logger.info("Telegram Proxy Server stopped")
    
    def get_stats(self):
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "sponsor_channel": self.sponsor_channel,
            "proxy_secret": self.proxy_secret,
            "recent_connections": self.connections[-10:] if self.connections else []
        }

# Flask web interface
app = Flask(__name__)
CORS(app)

# Global proxy server instance
proxy_server = None

@app.route('/')
def index():
    """Main dashboard"""
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Telegram Proxy Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #0088cc; text-align: center; }
        .info-box { background: #e7f3ff; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .config-box { background: #f0f8f0; padding: 20px; border-radius: 5px; margin: 20px 0; }
        .stats-box { background: #fff3cd; padding: 20px; border-radius: 5px; margin: 20px 0; }
        code { background: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
        .btn { background: #0088cc; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #006699; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Telegram Proxy Server</h1>
        
        <div class="info-box">
            <h3>📡 Server Information</h3>
            <p><strong>Status:</strong> <span style="color: green;">● Active</span></p>
            <p><strong>SOCKS5 Port:</strong> {{ stats.socks_port or 1080 }}</p>
            <p><strong>MTProto Port:</strong> {{ stats.mtproto_port or 443 }}</p>
            <p><strong>Sponsor Channel:</strong> {{ stats.sponsor_channel }}</p>
        </div>
        
        <div class="config-box">
            <h3>⚙️ Proxy Configuration</h3>
            <p><strong>SOCKS5 Proxy URL:</strong></p>
            <code>socks5://{{ request.host.split(':')[0] }}:1080</code>
            
            <p><strong>MTProto Proxy URL:</strong></p>
            <code>tg://proxy?server={{ request.host.split(':')[0] }}&port=443&secret={{ stats.proxy_secret }}</code>
            
            <p><strong>Proxy Secret:</strong></p>
            <code>{{ stats.proxy_secret }}</code>
        </div>
        
        <div class="stats-box">
            <h3>📊 Statistics</h3>
            <p><strong>Total Connections:</strong> {{ stats.total_connections }}</p>
            <p><strong>Marketing Channel:</strong> {{ stats.sponsor_channel }}</p>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="btn" onclick="window.location.reload()">🔄 Refresh Stats</button>
            <button class="btn" onclick="window.open('/api/stats', '_blank')">📈 View API</button>
        </div>
    </div>
</body>
</html>
    """, stats=proxy_server.get_stats() if proxy_server else {})

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    if proxy_server:
        return jsonify(proxy_server.get_stats())
    return jsonify({"error": "Proxy server not running"})

@app.route('/api/config')
def api_config():
    """API endpoint for configuration"""
    if proxy_server:
        stats = proxy_server.get_stats()
        return jsonify({
            "socks5_url": f"socks5://{request.host.split(':')[0]}:1080",
            "mtproto_url": f"tg://proxy?server={request.host.split(':')[0]}&port=443&secret={stats['proxy_secret']}",
            "sponsor_channel": stats['sponsor_channel'],
            "proxy_secret": stats['proxy_secret']
        })
    return jsonify({"error": "Proxy server not running"})

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "service": "telegram-proxy"})

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Telegram Proxy Server with Channel Sponsorship')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--web-port', type=int, default=int(os.getenv('PORT', 5000)), help='Web interface port')
    parser.add_argument('--socks-port', type=int, default=1080, help='SOCKS5 proxy port')
    parser.add_argument('--mtproto-port', type=int, default=443, help='MTProto proxy port')
    parser.add_argument('--sponsor-channel', default=os.getenv('SPONSOR_CHANNEL', '@your_channel'), help='Sponsor channel')
    parser.add_argument('--proxy-secret', default=os.getenv('PROXY_SECRET'), help='Proxy secret')
    
    args = parser.parse_args()
    
    # Initialize proxy server
    global proxy_server
    proxy_server = TelegramProxyServer(
        host=args.host,
        socks_port=args.socks_port,
        mtproto_port=args.mtproto_port,
        sponsor_channel=args.sponsor_channel,
        proxy_secret=args.proxy_secret
    )
    
    # Start proxy server
    proxy_server.start()
    
    # Start web interface
    logger.info(f"Starting web interface on {args.host}:{args.web_port}")
    app.run(host=args.host, port=args.web_port, debug=False)

if __name__ == '__main__':
    main())
