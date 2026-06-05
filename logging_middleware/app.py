import os
import sys
import requests

BASE_URL = "http://4.224.186.213/evaluation-service"
ENV_FILE = ".env"

def load_env():
    
    if not os.path.exists(ENV_FILE):
        print(f"[CRITICAL] Configuration file '{ENV_FILE}' is missing.")
        sys.exit(1)
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

def update_env_file(key, value):
   
    lines = []
    key_exists = False
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            lines = f.readlines()
    
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_exists = True
            break
            
    if not key_exists:
        lines.append(f"\n{key}={value}\n")
        
    with open(ENV_FILE, "w") as f:
        f.writelines(lines)
    os.environ[key] = value

class AffordMedService:
    def __init__(self):
        load_env()
        self.email = os.getenv("USER_EMAIL")
        self.name = os.getenv("USER_NAME")
        self.roll_no = os.getenv("ROLL_NUMBER")
        self.access_code = os.getenv("ACCESS_CODE")
        
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.access_token = None

    def initialize_system(self):
       
        
        if not self.client_id or not self.client_secret:
            print("[INIT] Missing API credentials. Running registration sequence...")
            reg_url = f"{BASE_URL}/register"
            
            payload = {
                "email": self.email,
                "name": self.name,
                "rollNo": self.roll_no,
                "accessCode": self.access_code,
                "mobileNo": "6309128244",
                "githubUsername": "Neelima2025"
            }
            try:
                res = requests.post(reg_url, json=payload)
                if res.status_code in [200, 201]:
                    data = res.json()
                    self.client_id = data.get("clientID")
                    self.client_secret = data.get("clientSecret")
                    
                    update_env_file("CLIENT_ID", self.client_id)
                    update_env_file("CLIENT_SECRET", self.client_secret)
                    print("[SUCCESS] Registration completed successfully.")
                else:
                    print(f"[ERROR] Registration rejected by server ({res.status_code}): {res.text}")
                    return False
            except Exception as e:
                print(f"[EXCEP] Connection to target server failed: {e}")
                return False

        print("[AUTH] Exchanging keys for authorization session token...")
        auth_url = f"{BASE_URL}/auth"
        auth_payload = {
            "email": self.email,
            "name": self.name.lower() if self.name else "", 
            "rollNo": self.roll_no,
            "accessCode": self.access_code,
            "clientID": self.client_id,
            "clientSecret": self.client_secret
        }
        try:
            res = requests.post(auth_url, json=auth_payload)
            if res.status_code in [200, 201]:
                self.access_token = res.json().get("access_token")
                print("[SUCCESS] Access token acquired successfully.\n")
                return True
            else:
                print(f"[ERROR] Authorization handshake failed ({res.status_code}): {res.text}")
                return False
        except Exception as e:
            print(f"[EXCEP] Token assignment failed: {e}")
            return False

    def log(self, stack: str, level: str, package: str, message: str):
       
        if not self.access_token:
            print("[WARN] Post blocked: Session unauthorized.")
            return False
            
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "stack": stack.lower(),
            "level": level.lower(),
            "package": package.lower(),
            "message": str(message)
        }
        try:
            res = requests.post(f"{BASE_URL}/logs", json=payload, headers=headers)
            if res.status_code in [200, 201]:
                print(f"[SERVER LOG DATA ACCEPTED] ID: {res.json().get('logID')} | {res.json().get('message')}")
                return True
            else:
                print(f"[SERVER LOG ERROR] {res.status_code}: {res.text}")
                return False
        except Exception as e:
            print(f"[EXCEP] Telemetry logging dispatch broken down: {e}")
            return False

if __name__ == "__main__":
    service = AffordMedService()
    if service.initialize_system():
        print("=== Application Active ===")
        
        # Test Sample 1 (Shortened to 32 characters to satisfy server limits)
        service.log(
            stack="backend",
            level="info",
            package="route",
            message="Initialized route mapping hooks."
        )
        
        # Test Sample 2 (30 characters)
        service.log(
            stack="backend",
            level="error",
            package="handler",
            message="received string, expected bool"
        )
