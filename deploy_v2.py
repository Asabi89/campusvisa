import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("185.245.182.179", username="root", password="Alabimi89@")

print("--- PULLING, MIGRATING AND RESTARTING ---")
stdin, stdout, stderr = ssh.exec_command("cd /opt/campusvisa && git pull origin main && docker compose exec -T web python manage.py migrate && docker compose exec -T web python populate_pricing.py && docker compose restart web")
exit_status = stdout.channel.recv_exit_status()
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
