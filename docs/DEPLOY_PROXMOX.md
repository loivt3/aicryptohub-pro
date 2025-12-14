# Deploy AI Crypto Hub trên Proxmox VE

Hướng dẫn chi tiết deploy Microservices SaaS lên Proxmox VE với Docker.

---

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Tạo LXC Container](#2-tạo-lxc-container)
3. [Cài đặt Docker](#3-cài-đặt-docker)
4. [Clone và Deploy](#4-clone-và-deploy)
5. [Cấu hình SSL (Let's Encrypt)](#5-cấu-hình-ssl-lets-encrypt)
6. [Cấu hình Domain](#6-cấu-hình-domain)
7. [Monitoring & Maintenance](#7-monitoring--maintenance)

---

## 1. Yêu cầu hệ thống

### Proxmox VE
- Proxmox VE 7.x hoặc 8.x
- Đủ resources cho container/VM

### Container/VM Specs (Recommended)
| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 2GB | 4GB |
| Disk | 20GB | 40GB SSD |
| Network | 1 Gbps | 1 Gbps |

---

## 2. Tạo LXC Container

### Option A: LXC Container (Lightweight - Recommended)

#### 2.1 Tải template Ubuntu
```bash
# SSH vào Proxmox host
ssh root@<proxmox-ip>

# Tải Ubuntu 22.04 template
pveam update
pveam download local ubuntu-22.04-standard_22.04-1_amd64.tar.zst
```

#### 2.2 Tạo container
```bash
# Tạo LXC container
pct create 200 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \
  --hostname aicryptohub \
  --cores 4 \
  --memory 4096 \
  --swap 1024 \
  --rootfs local-lvm:40 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --unprivileged 1 \
  --features nesting=1 \
  --start 1
```

> [!IMPORTANT]
> **nesting=1** là bắt buộc để chạy Docker trong LXC

#### 2.3 Vào container
```bash
pct enter 200
```

### Option B: VM (Full isolation)

Nếu cần isolation cao hơn, tạo VM Ubuntu 22.04 thông qua Proxmox Web UI:
1. Upload ISO Ubuntu 22.04 Server
2. Create VM với 4 cores, 4GB RAM, 40GB disk
3. Install Ubuntu Server

---

## 3. Cài đặt Docker

### 3.1 Update hệ thống
```bash
apt update && apt upgrade -y
```

### 3.2 Cài đặt Docker
```bash
# Cài đặt dependencies
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# Thêm Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Thêm Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Cài đặt Docker
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify
docker --version
docker compose version
```

### 3.3 Cấu hình Docker (Optional)
```bash
# Thêm user vào docker group (nếu không dùng root)
usermod -aG docker $USER

# Enable Docker service
systemctl enable docker
systemctl start docker
```

---

## 4. Clone và Deploy

### 4.1 Clone repository
```bash
# Cài đặt git
apt install -y git

# Clone repo (hoặc copy từ local)
cd /opt
git clone https://github.com/your-username/aicryptohub-pro.git
cd aicryptohub-pro
```

### 4.2 Cấu hình Environment

```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit với credentials thực
nano backend/.env
```

**Nội dung `.env`:**
```env
# Database - Supabase
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT].supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Redis (local)
REDIS_URL=redis://redis:6379

# AI Providers
GEMINI_API_KEY=your-gemini-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key

# External APIs
COINGECKO_API_KEY=your-coingecko-api-key

# JWT Secret (generate: openssl rand -hex 32)
JWT_SECRET_KEY=your-super-secret-jwt-key-here

# App
DEBUG=false
```

### 4.3 Cấu hình Frontend

```bash
# Tạo file .env cho frontend
cat > frontend/.env << 'EOF'
NUXT_PUBLIC_API_BASE=https://api.aicryptohub.io/api/v1
EOF
```

### 4.4 Build và Deploy

```bash
cd /opt/aicryptohub-pro/infrastructure

# Build images
docker compose build

# Start services
docker compose up -d

# Kiểm tra status
docker compose ps
```

**Output mong đợi:**
```
NAME                    STATUS              PORTS
aicryptohub-api         Up (healthy)        8000
aicryptohub-web         Up (healthy)        3000
aicryptohub-redis       Up (healthy)        6379
aicryptohub-nginx       Up (healthy)        80, 443
```

### 4.5 Kiểm tra logs
```bash
# Xem tất cả logs
docker compose logs -f

# Xem log từng service
docker compose logs -f backend
docker compose logs -f frontend
```

---

## 5. Cấu hình SSL (Let's Encrypt)

### 5.1 Cài đặt Certbot
```bash
apt install -y certbot
```

### 5.2 Tạo SSL certificate
```bash
# Stop nginx tạm thời
docker compose stop nginx

# Request certificate
certbot certonly --standalone \
  -d aicryptohub.io \
  -d www.aicryptohub.io \
  -d api.aicryptohub.io \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Start nginx lại
docker compose start nginx
```

### 5.3 Copy certificates vào project
```bash
# Tạo thư mục SSL
mkdir -p /opt/aicryptohub-pro/infrastructure/nginx/ssl

# Copy certificates
cp /etc/letsencrypt/live/aicryptohub.io/fullchain.pem \
   /opt/aicryptohub-pro/infrastructure/nginx/ssl/

cp /etc/letsencrypt/live/aicryptohub.io/privkey.pem \
   /opt/aicryptohub-pro/infrastructure/nginx/ssl/

# Set permissions
chmod 600 /opt/aicryptohub-pro/infrastructure/nginx/ssl/*.pem
```

### 5.4 Cập nhật nginx config

Sửa `infrastructure/nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name aicryptohub.io www.aicryptohub.io;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # ... rest of config
}
```

### 5.5 Restart nginx
```bash
docker compose restart nginx
```

### 5.6 Auto-renew SSL
```bash
# Thêm cron job
crontab -e

# Thêm dòng này:
0 3 * * * certbot renew --quiet && cp /etc/letsencrypt/live/aicryptohub.io/*.pem /opt/aicryptohub-pro/infrastructure/nginx/ssl/ && docker compose -f /opt/aicryptohub-pro/infrastructure/docker-compose.yml restart nginx
```

---

## 6. Cấu hình Domain

### 6.1 DNS Records

Thêm các DNS records tại domain registrar (Cloudflare, GoDaddy, etc.):

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | `<container-ip>` | 300 |
| A | www | `<container-ip>` | 300 |
| A | api | `<container-ip>` | 300 |
| CNAME | www | aicryptohub.io | Auto |

### 6.2 Lấy IP của container
```bash
# Từ Proxmox host
pct exec 200 -- ip addr show eth0 | grep inet
```

### 6.3 Port Forwarding (nếu cần)

Nếu Proxmox server sau NAT, cấu hình port forwarding trên router:

| External Port | Internal IP | Internal Port |
|---------------|-------------|---------------|
| 80 | `<container-ip>` | 80 |
| 443 | `<container-ip>` | 443 |

---

## 7. Monitoring & Maintenance

### 7.1 Xem resource usage
```bash
# Docker stats
docker stats

# Container resource
docker compose top
```

### 7.2 Backup data
```bash
# Backup script
cat > /opt/backup-aicryptohub.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/opt/backups

mkdir -p $BACKUP_DIR

# Backup Redis data
docker compose -f /opt/aicryptohub-pro/infrastructure/docker-compose.yml \
  exec redis redis-cli BGSAVE

# Backup .env files
tar -czf $BACKUP_DIR/env_$DATE.tar.gz \
  /opt/aicryptohub-pro/backend/.env \
  /opt/aicryptohub-pro/frontend/.env

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -type f -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/backup-aicryptohub.sh

# Thêm cron job
crontab -e
# 0 2 * * * /opt/backup-aicryptohub.sh
```

### 7.3 Update deployment
```bash
cd /opt/aicryptohub-pro

# Pull latest code
git pull origin main

# Rebuild và restart
docker compose -f infrastructure/docker-compose.yml build
docker compose -f infrastructure/docker-compose.yml up -d

# Cleanup old images
docker image prune -f
```

### 7.4 Logs rotation
```bash
# Cấu hình Docker log rotation
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker
```

### 7.5 Health check
```bash
# Check API health
curl -s http://localhost:8000/health | jq

# Check frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

---

## Troubleshooting

### Container không start
```bash
# Xem logs
docker compose logs backend

# Kiểm tra .env
cat backend/.env
```

### Database connection failed
```bash
# Test từ container
docker compose exec backend python -c "
from app.services.database import get_db_service
db = get_db_service()
print('Connection:', db.test_connection())
"
```

### Port already in use
```bash
# Tìm process đang dùng port
lsof -i :80
lsof -i :443

# Kill process
kill -9 <PID>
```

### SSL certificate expired
```bash
certbot renew --force-renewal
# Copy lại certificates
```

---

## Quick Commands Cheatsheet

```bash
# Start all
docker compose -f /opt/aicryptohub-pro/infrastructure/docker-compose.yml up -d

# Stop all
docker compose -f /opt/aicryptohub-pro/infrastructure/docker-compose.yml down

# Restart specific service
docker compose restart backend

# View logs
docker compose logs -f --tail=100

# Enter container shell
docker compose exec backend bash
docker compose exec frontend sh

# Rebuild without cache
docker compose build --no-cache

# Cleanup
docker system prune -af
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Proxmox VE Host                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              LXC Container (ID: 200)                  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │              Docker Compose                     │  │  │
│  │  │  ┌─────────┐ ┌─────────┐ ┌─────────┐           │  │  │
│  │  │  │  Nginx  │ │Frontend │ │ Backend │           │  │  │
│  │  │  │  :80    │ │ :3000   │ │ :8000   │           │  │  │
│  │  │  │  :443   │ │ Nuxt.js │ │ FastAPI │           │  │  │
│  │  │  └────┬────┘ └────┬────┘ └────┬────┘           │  │  │
│  │  │       │           │           │                 │  │  │
│  │  │       └───────────┴───────────┘                 │  │  │
│  │  │                   │                             │  │  │
│  │  │              ┌────┴────┐                        │  │  │
│  │  │              │  Redis  │                        │  │  │
│  │  │              │  :6379  │                        │  │  │
│  │  │              └─────────┘                        │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                            │                                  │
│                            ▼                                  │
│                    ┌───────────────┐                          │
│                    │   Internet    │                          │
│                    │ aicryptohub.io│                          │
│                    └───────────────┘                          │
└─────────────────────────────────────────────────────────────┘

External:
┌─────────────────┐
│    Supabase     │
│   PostgreSQL    │
└─────────────────┘
```
