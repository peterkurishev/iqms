# 🌐 Internet Quality Monitoring System

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/github/license/peterkurishev/iqms)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![Systemd](https://img.shields.io/badge/systemd-supported-green.svg)

Distributed system for real-time internet performance monitoring with lightweight agents and centralized analytics.

## 📌 Key Features

| Feature | Description |
|---------|-------------|
| 📊 **Comprehensive Metrics** | Latency, jitter, packet loss, speeds, DNS times, WiFi strength |
| 🤖 **Smart Agents** | Auto-start, self-healing, cross-platform (Linux/Win/macOS) |
| 🗄️ **Centralized Storage** | TimescaleDB for time-series data with REST API |
| 🔐 **Security** | API key auth, HTTPS encryption, isolated execution |
| 📈 **Visualization** | Built-in Grafana dashboards |

## 🛠️ Installation

### Server Deployment (Docker)

```bash
git clone https://github.com/yourusername/internet-monitor.git
cd internet-monitor/server

# Configure environment
cp .env.example .env
nano .env  # Edit your settings

# Deploy
docker-compose up -d

# Agent setup

```bash
# Linux systemd service
sudo ./install-agent.sh --api-url YOUR_SERVER_URL --api-key YOUR_AGENT_KEY
```
# 🖥️ Architecture

```
graph LR
    A[Agents] -->|HTTPS| B[API Server]
    B --> C[(TimescaleDB)]
    C --> D[Grafana]
    C --> E[Alert Manager]
    F[Test Servers] --> A
```
