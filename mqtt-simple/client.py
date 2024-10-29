#!/usr/bin/env python3
import argparse
import os
import time
import random
import logging
import paho.mqtt.client as mqtt

def setup_logger(log_file):
    # Make sure the path to that log file exists
    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def main_loop(mqtt_config, sleep_time_min, sleep_time_max, static_behavior):
    # Callback when the client connects to the broker
    def on_connect(client, userdata, flags, rc):
        message = f"Connected with result code {rc}"
        print(message)
        logging.info(message)
        if rc == 0:  # Successful connection
            if mqtt_config["MQTT_MODE"] == "sub":
                mqtt_topic = mqtt_config["MQTT_TOPIC"]
                client.subscribe(mqtt_topic, qos=0)
                logging.info(f"Subscribed to {mqtt_topic}")
        else:
            logging.error(f"Connection failed with result code {rc}")

    # Callback when a message is published
    def on_publish(client, userdata, mid):
        logging.info(f"Message {mid} published")

    # Callback when a message is received
    def on_message(client, userdata, message):
        logging.info(f"Received message: '{message.payload.decode()}' on topic: '{message.topic}'")

    # Callback when the client disconnects
    def on_disconnect(client, userdata, rc):
        logging.info(f"Disconnected with result code {rc}")

    # Initialize the MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, mqtt_client_id)

    # Set callback functions
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    logging.info(f"Connecting to {mqtt_config['MQTT_BROKER']}:{mqtt_config['MQTT_PORT']}")
    client.connect(mqtt_config["MQTT_BROKER"], mqtt_config["MQTT_PORT"], 60)

    # Publisher mode
    if mqtt_config["MQTT_MODE"] == "pub":
        client.loop_start()  # Start the loop in a background thread
        try:
            while True:
                random_data = random.randint(1, 100)
                client.publish(mqtt_config["MQTT_TOPIC"], payload=random_data, qos=0)
                logging.info(f"Sent data: {random_data}")
                sleep_time_in_seconds = sleep_time_max if static_behavior else random.uniform(sleep_time_min, sleep_time_max)
                time.sleep(sleep_time_in_seconds)
        except KeyboardInterrupt:
            logging.info("Publisher stopped by user")
        finally:
            client.loop_stop()
            client.disconnect()

    # Subscriber mode
    elif mqtt_config["MQTT_MODE"] == "sub":
        client.loop_forever()  # Block and wait for messages

if __name__ == "__main__":

    args = argparse.ArgumentParser()
    args.add_argument("-smin", "--sleep_time_min", help="Minimum sleep time", default=0.1, type=float)
    args.add_argument("-smax", "--sleep_time_max", help="Maximum sleep time", default=0.5, type=float)
    args.add_argument("-ip", "--server_ip", help="Server IP", default=None, type=str)
    args.add_argument("-p", "--port", help="Server port", default=1883, type=int)
    args.add_argument("-t", "--topic", help="MQTT topic", default=None, type=str)
    args.add_argument("-m", "--mode", help="MQTT mode (pub/sub)", default=None, type=str)
    args.add_argument("-c", "--client_id", help="MQTT client ID", default=None, type=str)
    args.add_argument("-o", "--output", help="Output log file", default="mqtt_client_log.txt", type=str)
    args.add_argument('--static_behavior', action='store_true', help='Static behavior (no randomization)')
    args = args.parse_args()

    setup_logger(args.output)

    sleep_time_min = args.sleep_time_min
    sleep_time_max = args.sleep_time_max
    static_behavior = args.static_behavior

    # Also allow environment variables
    mqtt_broker = args.server_ip or os.getenv('MQTT_BROKER', 'localhost')
    mqtt_client_id = args.client_id or os.getenv('MQTT_CLIENT_ID') or os.getenv('HOSTNAME')
    mqtt_topic = args.topic or os.getenv('MQTT_TOPIC', 'mentored/topic')
    mqtt_mode = args.mode or os.getenv('MQTT_MODE', 'pub')

    mqtt_config = {
        "MQTT_BROKER": mqtt_broker,
        "MQTT_PORT": args.port,
        "MQTT_TOPIC": mqtt_topic,
        "MQTT_MODE": mqtt_mode,
        "MQTT_CLIENT_ID": mqtt_client_id
    }

    logging.info(f"Starting client with broker: {mqtt_broker}:{args.port}, mode: {mqtt_mode}, topic: {mqtt_topic}")
    main_loop(mqtt_config, sleep_time_min, sleep_time_max, static_behavior)
