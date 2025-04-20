import flwr as fl
import time
import psutil
import csv
import os

# Create logs directory
log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)
server_log_file = os.path.join(log_dir, "server_metrics.csv")
TOTAL_ROUNDS = int(os.getenv("TOTAL_ROUNDS", 1))  # Unique ID for each client
MIN_CLIENTS = int(os.getenv("MIN_CLIENTS", 1))  # Total number of clients
# Write header for server metrics CSV
with open(server_log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Round", "Aggregation Time (s)", "CPU Usage (%)", "Time Since Start (s)"])

class ServerStrategy(fl.server.strategy.FedAvg):
    def __init__(self):
        super().__init__()
        self.start_time = None

    def aggregate_fit(self, rnd, results, failures):
        if self.start_time is None:
            self.start_time = time.time()

        agg_time_start = time.time()
        aggregated_result = super().aggregate_fit(rnd, results, failures)
        agg_time = time.time() - agg_time_start
        cpu_usage = psutil.cpu_percent()
        time_since_start = time.time() - self.start_time

        # Log metrics
        with open(server_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            # writer.writerow([rnd, agg_time, cpu_usage, time_since_start])
            writer.writerow([time.time(), rnd, agg_time, cpu_usage, time_since_start])

        print(f"Round {rnd} - Aggregation Time: {agg_time:.2f}s, CPU Usage: {cpu_usage}%, Time Since Start: {time_since_start:.2f}s")
        return aggregated_result

# Start the federated learning server

server_start_time = time.time()
strategy = ServerStrategy()
while True:
    try:
        print("Starting FL Server...")
        client_manager = fl.server.SimpleClientManager()
        server = fl.server.Server(client_manager=client_manager, strategy=strategy)
        # server.client_manager().wait_for(MIN_CLIENTS, timeout=900)
        fl.server.start_server(
            server=server,
            server_address="0.0.0.0:8080",
            config=fl.server.ServerConfig(num_rounds=TOTAL_ROUNDS),
            strategy=strategy
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        time.sleep(1)
        continue
    print(f"Total Server Execution Time: {time.time() - server_start_time} seconds")
