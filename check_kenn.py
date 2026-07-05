import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("185.245.182.179", username="root", password="Alabimi89@")

print("--- KENN WEB LOGS ---")
stdin, stdout, stderr = ssh.exec_command("docker logs --tail=50 kenn-web-1")
print(stdout.read().decode())
print(stderr.read().decode())

print("--- CAMPUSVISA CELERY LOGS ---")
stdin, stdout, stderr = ssh.exec_command("docker logs --tail=50 campusvisa_celery")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()
