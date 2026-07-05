import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect("185.245.182.179", username="root", password="Alabimi89@")

# We need to run certbot to install SSL for the domains
# Command: sudo certbot --nginx -d nextstepc.com -d www.nextstepc.com -d visa.nextstepc.com -d staff.nextstepc.com -d admin.nextstepc.com

print("--- RUNNING CERTBOT ---")
cmd = "certbot --nginx -d nextstepc.com -d www.nextstepc.com -d visa.nextstepc.com -d staff.nextstepc.com -d admin.nextstepc.com --non-interactive --agree-tos --redirect -m admin@nextstepc.com --expand"
stdin, stdout, stderr = ssh.exec_command(cmd)

print("STDOUT:")
for line in stdout:
    print(line.strip())

print("STDERR:")
for line in stderr:
    print(line.strip())

ssh.close()
