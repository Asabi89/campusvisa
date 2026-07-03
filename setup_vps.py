import paramiko
import time
import sys

def run_cmd(ssh, cmd):
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    
    # Wait for the command to finish
    exit_status = stdout.channel.recv_exit_status()
    
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    
    if out:
        print(f"STDOUT:\n{out}")
    if err:
        print(f"STDERR:\n{err}")
    
    return exit_status

def setup_vps():
    host = "185.245.182.179"
    user = "root"
    password = "Alabimi89@"

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    print("Connecting to VPS...")
    try:
        ssh.connect(host, username=user, password=password, timeout=10)
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    print("Connected successfully.")
    
    # Install Docker and Nginx if not installed
    print("Updating packages and installing dependencies...")
    run_cmd(ssh, "apt-get update && apt-get install -y git curl nginx certbot python3-certbot-nginx")
    run_cmd(ssh, "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh")
    run_cmd(ssh, "apt-get install -y docker-compose-plugin")
    # For older ubuntu: run_cmd(ssh, "apt-get install -y docker-compose")

    # Clone the repository
    # Note: the repository needs to be public, or use a deploy key, or use HTTPS with token.
    # We will assume it's public for now, or just create a placeholder directory and pull.
    run_cmd(ssh, "rm -rf /root/campusvisa")
    run_cmd(ssh, "git clone https://github.com/Asabi89/campusvisa.git /root/campusvisa")

    # Write .env file
    env_content = """SECRET_KEY=django-insecure-production-key-campusvisa-2026
DEBUG=False
ALLOWED_HOSTS=nextstepc.com,www.nextstepc.com,visa.nextstepc.com,185.245.182.179

# Database (using sqlite for now as requested by missing instructions, can switch to postgres)
# DB_NAME=campusvisa
# DB_USER=campusvisa_user
# DB_PASSWORD=your-db-password

# Redis
REDIS_URL=redis://redis:6379/0

# Email (SMTP) - use Gmail App Passwords or Brevo/SendGrid
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=selinaonio@gmail.com
EMAIL_HOST_PASSWORD=lwxn wiow zaxf ovcx
DEFAULT_FROM_EMAIL=CampusVisa <no-reply@nextstepc.com>
"""
    run_cmd(ssh, f"echo '{env_content}' > /root/campusvisa/.env")

    # Start docker containers
    run_cmd(ssh, "cd /root/campusvisa && docker-compose up -d --build")

    # Setup Nginx Configuration
    nginx_conf = """
server {
    listen 80;
    server_name nextstepc.com www.nextstepc.com visa.nextstepc.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Serve Django static files directly via Nginx for performance
    location /static/ {
        alias /root/campusvisa/static/;
    }

    # Serve Django media files
    location /media/ {
        alias /root/campusvisa/media/;
    }
}
"""
    # Write nginx conf
    run_cmd(ssh, f"echo '{nginx_conf}' > /etc/nginx/sites-available/campusvisa")
    run_cmd(ssh, "ln -sf /etc/nginx/sites-available/campusvisa /etc/nginx/sites-enabled/")
    run_cmd(ssh, "rm -f /etc/nginx/sites-enabled/default")
    run_cmd(ssh, "systemctl restart nginx")

    print("Setup complete! Once domain DNS is updated to point to this IP, we can run Certbot.")
    ssh.close()

if __name__ == "__main__":
    setup_vps()
