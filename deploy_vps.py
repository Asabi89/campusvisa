import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("185.245.182.179", username="root", password="Alabimi89@")

print("--- UPDATING NGINX & DEPLOYING ---")
# 1. Update Nginx to include staff.nextstepc.com and admin.nextstepc.com
nginx_cmd = "sed -i 's/server_name nextstepc.com www.nextstepc.com visa.nextstepc.com staff.nextstepc.com;/server_name nextstepc.com www.nextstepc.com visa.nextstepc.com staff.nextstepc.com admin.nextstepc.com;/g' /etc/nginx/sites-available/campusvisa && systemctl reload nginx"
stdin, stdout, stderr = ssh.exec_command(nginx_cmd)
stdout.channel.recv_exit_status()

# 2. Pull changes and restart Docker
cmd = "cd /opt/campusvisa && git pull && docker compose restart web"
stdin, stdout, stderr = ssh.exec_command(cmd)

print("STDOUT:")
for line in stdout:
    print(line.strip())

print("STDERR:")
for line in stderr:
    print(line.strip())

ssh.close()
