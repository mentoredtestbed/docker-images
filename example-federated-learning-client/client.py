import flwr as fl
import tensorflow as tf
import numpy as np
import time
import os
import psutil
import csv
from sklearn.metrics import f1_score, roc_auc_score
import yaml

# Environment Variables
CLIENT_ID = int(os.getenv("CLIENT_ID", -1))  # Unique ID for each client
TOTAL_CLIENTS = int(os.getenv("TOTAL_CLIENTS", 3))  # Total number of clients
FL_SERVER = os.getenv("FL_SERVER", "na-server")  # FL server address
LAYER_SIZE = int(os.getenv("LAYER_SIZE", 2**10))  # FL server address
NUM_SAMPLES = int(os.getenv("NUM_SAMPLES", -1))  # Sample size
REAL_CLIENT_ID = int(os.getenv("REAL_CLIENT_ID", -1))  # Real client ID
SLEEP_WAIT_SERVER_WARMUP = int(os.getenv("SLEEP_WAIT_SERVER_WARMUP", 90))  # Real client ID
IGNORE_WARMUP = os.getenv("IGNORE_WARMUP", "False") == "True"  # Ignore warmup rounds
RANDOM_DATA_BY_PARTITION = os.getenv("RANDOM_DATA_BY_PARTITION", "False") == "True"  # Ignore warmup rounds
FL_IFNAME = os.getenv("FL_IFNAME", "eth0")  # Network interface name


if not IGNORE_WARMUP:
    # Open /MENTORED_IP_LIST.yaml
    while not os.path.exists("/MENTORED_IP_LIST.yaml"):
        time.sleep(1)

    with open("/MENTORED_IP_LIST.yaml", "r") as f:
        ip_list = yaml.safe_load(f)

    # Get the IP address of the FL server
    FL_SERVER = [x[0] for x in ip_list[FL_SERVER][0] if x[2] == FL_IFNAME][0]
    FL_SERVER = f"{FL_SERVER}:8080"

# Create logs directory
log_dir = "/app/logs"
os.makedirs(log_dir, exist_ok=True)
client_log_file = os.path.join(log_dir, f"client_{REAL_CLIENT_ID}_metrics.csv")
resource_log_file = os.path.join(log_dir, f"client_{REAL_CLIENT_ID}_resource_usage.csv")

# Write header for client metrics CSV
with open(client_log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Time Since Start (s)", "Client ID", "Round", "Training Time (s)", "Evaluation Time (s)", "Total Time (s)", "Accuracy", "F1-Score", "AUC"])

# Write header for resource usage CSV
with open(resource_log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Client ID", "Round", "Phase", "CPU Usage (%)", "Memory Usage (MB)"])

# Load dataset
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# Select 1000 random samples
# idx = np.random.choice(len(x_test), 1000, replace=False)
# x_test, y_test = x_test[idx], y_test[idx]
x_test, y_test = x_test[:1000], y_test[:1000]

# idx = np.random.choice(len(x_train), 1000, replace=False)
# x_train, y_train = x_train[idx], y_train[idx]
x_train, y_train = x_train[:1000], y_train[:1000]

x_train, x_test = x_train / 255.0, x_test / 255.0

# Define a simple model
model = tf.keras.models.Sequential([
    tf.keras.layers.Flatten(input_shape=(28, 28)),
    tf.keras.layers.Dense(LAYER_SIZE, activation="relu"),
    tf.keras.layers.Dense(LAYER_SIZE, activation="relu"),
    tf.keras.layers.Dense(10, activation="softmax")
])

model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer="adam",
    metrics=["accuracy"]
)

class FLClient(fl.client.NumPyClient):
    round_num = 0  # Track round number

    def __init__(self):
        super().__init__()
        
        # Split the dataset among clients
        self.reload_train_data()
        
        self.last_duration_train = 0
        self.last_duration_eval = 0

    def get_parameters(self, config):
        return model.get_weights()

    def reload_train_data(self):
        if CLIENT_ID < 0:
            if NUM_SAMPLES <= 0:
                n_samples = len(x_train) // TOTAL_CLIENTS
            else:
                n_samples = NUM_SAMPLES
            
            if RANDOM_DATA_BY_PARTITION:
                total_partitions = len(x_train) // n_samples
                idx = np.random.choice(total_partitions, 1)[0]
                start_idx = idx * n_samples
                end_idx = start_idx + n_samples if idx < total_partitions - 1 else len(x_train)
                self.x_train_client = x_train[start_idx:end_idx]
                self.y_train_client = y_train[start_idx:end_idx]
            else:
                # Select NUM_SAMPLES random samples
                idx = np.random.choice(len(x_train), n_samples, replace=False)
                self.x_train_client = x_train[idx]
                self.y_train_client = y_train[idx]

    def fit(self, parameters, config):
        print(f"Client {REAL_CLIENT_ID} - Round {FLClient.round_num} - Training...")
        self.reload_train_data()
        
        start_train = time.time()
        model.set_weights(parameters)
        model.fit(self.x_train_client, self.y_train_client, epochs=1, batch_size=32, verbose=0)
        duration_train = time.time() - start_train
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        self.last_duration_train = duration_train

        # Log metrics
        FLClient.round_num += 1
        with open(resource_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([CLIENT_ID, FLClient.round_num, "Training", cpu_usage, memory_usage])

        print(f"Client {CLIENT_ID} - Round {FLClient.round_num} - Training Time: {duration_train:.2f}s, CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage:.2f}MB")
        return model.get_weights(), len(self.x_train_client), {}

    def evaluate(self, parameters, config):
        print(f"Client {REAL_CLIENT_ID} - Round {FLClient.round_num} - Evaluating...")
        start_eval = time.time()
        model.set_weights(parameters)
        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        y_pred = np.argmax(model.predict(x_test), axis=1)
        f1 = f1_score(y_test, y_pred, average='macro')
        auc = roc_auc_score(tf.keras.utils.to_categorical(y_test, 10), model.predict(x_test), multi_class='ovr')
        duration_eval = time.time() - start_eval
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

        total_time = self.last_duration_train + duration_eval
        self.last_duration_eval = duration_eval

        # Log metrics
        with open(client_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            # writer.writerow([CLIENT_ID, FLClient.round_num, self.last_duration_train, duration_eval, total_time, accuracy, f1, auc])
            writer.writerow([time.time(), time.time() - server_start_time, CLIENT_ID, FLClient.round_num, self.last_duration_train, duration_eval, total_time, accuracy, f1, auc])

        with open(resource_log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([CLIENT_ID, FLClient.round_num, "Evaluation", cpu_usage, memory_usage])

        print(f"Client {CLIENT_ID} - Round {FLClient.round_num} - Evaluation Time: {duration_eval:.2f}s, Accuracy: {accuracy:.4f}, F1-Score: {f1:.4f}, AUC: {auc:.4f}, CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage:.2f}MB")
        return loss, len(x_test), {"accuracy": accuracy, "f1_score": f1, "auc": auc}


# time.sleep(SLEEP_WAIT_SERVER_WARMUP)  # Wait for the server to start

server_start_time = time.time()
while True:
    # print("Starting FL Client...")
    # sleep_time = np.random.randint(1, 3)
    # time.sleep(sleep_time)
    # print(f"Client {CLIENT_ID} - Sleeping for {sleep_time} seconds...")
    try:
        fl.client.start_numpy_client(server_address=FL_SERVER, client=FLClient())
    except Exception as e:
        print(f"Client {CLIENT_ID} - Exception: {e}")
