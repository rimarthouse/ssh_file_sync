import os
import paramiko
import json
from datetime import datetime

# Path to options.json
CONFIG_FILE = "/data/options.json"

# Load configuration from options.json
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return json.load(file)

config = load_config()

REMOTE_HOST = config['remote_host']
REMOTE_PORT = config.get('remote_port', 22)
USERNAME = config['username']
PASSWORD = config['password']
REMOTE_DIR = config['remote_dir']
LOCAL_DIR = config['local_dir']

# Connect to the remote server via SSH
def connect_ssh():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(REMOTE_HOST, port=REMOTE_PORT, username=USERNAME, password=PASSWORD)
    return ssh

# Check the creation date of a file
def get_file_creation_date(sftp, file_path):
    stat = sftp.stat(file_path)
    return datetime.fromtimestamp(stat.st_mtime)

# Synchronize files from remote to local
def sync_files():
    ssh = connect_ssh()
    sftp = ssh.open_sftp()

    try:
        remote_files = sftp.listdir_attr(REMOTE_DIR)

        for remote_file in remote_files:
            remote_file_path = os.path.join(REMOTE_DIR, remote_file.filename)
            local_file_path = os.path.join(LOCAL_DIR, remote_file.filename)

            if not os.path.exists(LOCAL_DIR):
                os.makedirs(LOCAL_DIR)

            if os.path.exists(local_file_path):
                local_file_time = datetime.fromtimestamp(os.path.getmtime(local_file_path))
                remote_file_time = get_file_creation_date(sftp, remote_file_path)

                if remote_file_time > local_file_time:
                    print(f"Newer file detected: {remote_file.filename}, downloading...")
                    sftp.get(remote_file_path, local_file_path)
            else:
                print(f"File not found locally: {remote_file.filename}, downloading...")
                sftp.get(remote_file_path, local_file_path)

    finally:
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    try:
        print("Starting sync...")
        sync_files()
        print("Sync completed.")
    except Exception as e:
        print(f"Error: {e}")