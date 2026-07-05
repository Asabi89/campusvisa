import paramiko
import json
import time

def run_cmd(ssh, cmd, fail_ok=False):
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    exit_status = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if out: print(f"STDOUT:\n{out}")
    if err: print(f"STDERR:\n{err}")
    if exit_status != 0 and not fail_ok:
        print(f"Command failed with exit status {exit_status}")
    return out

def fix_vps():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("185.245.182.179", username="root", password="Alabimi89@")
    
    # 1. Restart KENN project
    print("\n--- RESTARTING KENN PROJECT ---")
    inspect_out = run_cmd(ssh, "docker inspect kenn-web-1", fail_ok=True)
    if inspect_out and not inspect_out.startswith("[]"):
        try:
            data = json.loads(inspect_out)
            kenn_dir = data[0]['Config']['Labels'].get('com.docker.compose.project.working_dir')
            if kenn_dir:
                print(f"Found kenn project at {kenn_dir}")
                run_cmd(ssh, f"cd {kenn_dir} && docker compose restart")
            else:
                print("Could not determine kenn project dir from labels, restarting containers directly.")
                run_cmd(ssh, "docker restart kenn-web-1 kenn-celery_worker-1 kenn-celery_beat-1")
        except Exception as e:
            print(f"Error parsing docker inspect: {e}")
            run_cmd(ssh, "docker restart kenn-web-1 kenn-celery_worker-1 kenn-celery_beat-1")
    else:
        print("kenn-web-1 container not found.")

    # 2. Fix CAMPUSVISA
    print("\n--- FIXING CAMPUSVISA PROJECT ---")
    # Stop existing campusvisa containers if they exist
    run_cmd(ssh, "cd /root/campusvisa && docker compose down", fail_ok=True)
    
    # Move directory
    run_cmd(ssh, "mv /root/campusvisa /opt/campusvisa", fail_ok=True)
    
    # Update nginx config
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
        alias /opt/campusvisa/static/;
    }

    # Serve Django media files
    location /media/ {
        alias /opt/campusvisa/media/;
    }
}
"""
    run_cmd(ssh, f"echo '{nginx_conf}' > /etc/nginx/sites-available/campusvisa")
    run_cmd(ssh, "systemctl restart nginx")
    
    # Build and start campusvisa containers
    run_cmd(ssh, "cd /opt/campusvisa && docker compose up -d --build")
    
    # Run migrations and collectstatic just in case
    run_cmd(ssh, "cd /opt/campusvisa && docker compose exec -T web python manage.py collectstatic --noinput", fail_ok=True)
    
    ssh.close()
    print("VPS fix script completed!")

if __name__ == "__main__":
    fix_vps()
