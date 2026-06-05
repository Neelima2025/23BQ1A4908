import os
import sys
import requests


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
try:
    from logging_middleware.app import AffordMedService
except ImportError:
    print("[WARN] Logging middleware module could not be imported automatically.")
    AffordMedService = None

BASE_URL = "http://4.224.186.213/evaluation-service"

ENV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))

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

class MaintenanceScheduler:
    def __init__(self):
        load_env()
       
        self.logger = AffordMedService() if AffordMedService else None
        if self.logger:
            self.logger.initialize_system()

    def get_headers(self):
        
        if self.logger and self.logger.access_token:
            return {
                "Authorization": f"Bearer {self.logger.access_token}",
                "Content-Type": "application/json"
            }
        return {}

    def fetch_depots(self):
      
        try:
            res = requests.get(f"{BASE_URL}/depots", headers=self.get_headers())
            if res.status_code == 200:
                return res.json().get("depots", [])
            print(f"[ERROR] Failed to fetch depots. Status: {res.status_code}")
            return []
        except Exception as e:
            print(f"[EXCEP] Depot fetch breakdown: {e}")
            return []

    def fetch_vehicles(self):
        
        try:
            res = requests.get(f"{BASE_URL}/vehicles", headers=self.get_headers())
            if res.status_code == 200:
                return res.json().get("vehicles", [])
            print(f"[ERROR] Failed to fetch vehicles. Status: {res.status_code}")
            return []
        except Exception as e:
            print(f"[EXCEP] Vehicle fetch breakdown: {e}")
            return []

    def optimize_knapsack(self, tasks, max_hours):
        
        n = len(tasks)
        dp = [[0 for _ in range(max_hours + 1)] for _ in range(n + 1)]

        for i in range(1, n + 1):
            task = tasks[i - 1]
            duration = task["Duration"]
            impact = task["Impact"]
            
            for w in range(max_hours + 1):
                if duration <= w:
                    dp[i][w] = max(impact + dp[i - 1][w - duration], dp[i - 1][w])
                else:
                    dp[i][w] = dp[i - 1][w]

        selected_tasks = []
        w = max_hours
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                selected_tasks.append(tasks[i - 1])
                w -= tasks[i - 1]["Duration"]

        return dp[n][max_hours], selected_tasks

    def execute_pipeline(self):
        print("\n=== Initiating Vehicle Maintenance Scheduling Optimization ===")
        
        depots = self.fetch_depots()
        vehicles = self.fetch_vehicles()

        if not depots or not vehicles:
            print("[CRITICAL] Input telemetry datasets empty. Terminating pipeline execution loop.")
            return

        if self.logger:
            self.logger.log("backend", "info", "route", "Successfully fetched configuration maps.")

        for depot in depots:
            depot_id = depot["ID"]
            max_capacity = depot["MechanicHours"]
            
            print(f"\nOptimizing Scheduler for Depot ID: {depot_id} (Capacity: {max_capacity} Hours)")
            
            max_impact, chosen_vehicles = self.optimize_knapsack(vehicles, max_capacity)
            total_duration = sum(v["Duration"] for v in chosen_vehicles)

            print(f" -> Maximum Achieved Operational Impact: {max_impact}")
            print(f" -> Allocated Workload Duration: {total_duration}/{max_capacity} hours")
            print(" -> Selected Task IDs:")
            for v in chosen_vehicles:
                print(f"    * Task: {v['TaskID']} | Duration: {v['Duration']} hrs | Impact Score: {v['Impact']}")

            if self.logger:
                msg = f"Depot {depot_id} optimized. Max impact: {max_impact}"
                self.logger.log("backend", "info", "controller", msg[:48])

if __name__ == "__main__":
    scheduler = MaintenanceScheduler()
    scheduler.execute_pipeline()
