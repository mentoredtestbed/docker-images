#!/usr/bin/env python3
import argparse
import os
import time
import random
import logging
import paho.mqtt.client as mqtt

def setup_loggers(main_log_file, mqtt_log_file):
    # Ensure the log directories exist
    os.makedirs(os.path.dirname(main_log_file), exist_ok=True)

    # Configure the main application logger
    main_logger = logging.getLogger("main")
    main_logger.setLevel(logging.INFO)
    main_handler = logging.FileHandler(main_log_file)
    main_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S'))
    main_logger.addHandler(main_handler)

    # Configure the MQTT logger
    mqtt_logger = logging.getLogger("mqtt")
    mqtt_logger.setLevel(logging.INFO)
    mqtt_handler = logging.FileHandler(mqtt_log_file)
    mqtt_handler.setFormatter(logging.Formatter("%(message)s"))
    mqtt_logger.addHandler(mqtt_handler)

    # Add a CSV header to the MQTT log file if it's empty
    if not os.path.exists(mqtt_log_file) or os.stat(mqtt_log_file).st_size == 0:
        with open(mqtt_log_file, 'w') as f:
            f.write("time,topic,message,action\n")

    return main_logger, mqtt_logger

def main_loop(mqtt_config, sleep_time_min, sleep_time_max, static_behavior, main_logger, mqtt_logger):
    def on_connect(client, userdata, flags, rc):
        message = f"Connected with result code {rc}"
        print(message)
        main_logger.info(message)
        if rc == 0:  # Successful connection
            if mqtt_config["MQTT_MODE"] == "sub":
                mqtt_topic = mqtt_config["MQTT_TOPIC"]
                client.subscribe(mqtt_topic, qos=mqtt_config["MQTT_QOS"])
                main_logger.info(f"Subscribed to {mqtt_topic}")
        else:
            main_logger.error(f"Connection failed with result code {rc}")

    def on_publish(client, userdata, mid):
        main_logger.info(f"Message {mid} published")
        # TODO: Fix this so that it logs the correct data
        # mqtt_logger.info(f"{time.time()},{mqtt_config['MQTT_TOPIC']},{userdata},published")

    def on_message(client, userdata, message):
        main_logger.info(f"Received message: '{message.payload.decode()}' on topic: '{message.topic}'")
        mqtt_logger.info(f"{time.time()},{message.topic},{message.payload.decode()},received")

    def on_disconnect(client, userdata, rc):
        main_logger.info(f"Disconnected with result code {rc}")

    # Initialize the MQTT client
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, mqtt_client_id)

    # Set callback functions
    client.on_connect = on_connect
    client.on_publish = on_publish
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the MQTT broker
    main_logger.info(f"Connecting to {mqtt_config['MQTT_BROKER']}:{mqtt_config['MQTT_PORT']}")
    client.connect(mqtt_config["MQTT_BROKER"], mqtt_config["MQTT_PORT"], 60)

    if mqtt_config["MQTT_MODE"] == "pub":
        client.loop_start()  # Start the loop in a background thread
        try:
            while True:
                random_data = random.randint(100000, 999999)
                client.userdata=random_data
                mqtt_logger.info(f"{time.time()},{mqtt_config['MQTT_TOPIC']},{random_data},published")
                client.publish(mqtt_config["MQTT_TOPIC"], payload=random_data, qos=mqtt_config["MQTT_QOS"])
                main_logger.info(f"Sent data: {random_data}")
                sleep_time_in_seconds = sleep_time_max if static_behavior else random.uniform(sleep_time_min, sleep_time_max)
                time.sleep(sleep_time_in_seconds)
        except KeyboardInterrupt:
            main_logger.info("Publisher stopped by user")
        finally:
            client.loop_stop()
            client.disconnect()

    elif mqtt_config["MQTT_MODE"] == "sub":
        client.loop_forever()  # Block and wait for messages

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-smin", "--sleep_time_min", help="Minimum sleep time", default=0.1, type=float)
    parser.add_argument("-smax", "--sleep_time_max", help="Maximum sleep time", default=0.5, type=float)
    parser.add_argument("-ip", "--server_ip", help="Server IP", default=None, type=str)
    parser.add_argument("-p", "--port", help="Server port", default=1883, type=int)
    parser.add_argument("-t", "--topic", help="MQTT topic", default=None, type=str)
    parser.add_argument("-m", "--mode", help="MQTT mode (pub/sub)", default=None, type=str)
    parser.add_argument("-c", "--client_id", help="MQTT client ID", default=None, type=str)
    parser.add_argument("-q", "--qos", help="MQTT QoS", default=0, type=int)
    parser.add_argument("-o", "--output", help="Output log file", default="mqtt_client_log.txt", type=str)
    parser.add_argument('--static_behavior', action='store_true', help='Static behavior (no randomization)')
    args = parser.parse_args()

    main_log_file = args.output
    # Replace the extension, whatever it is, with .csv
    mqtt_log_file = os.path.splitext(main_log_file)[0] + ".csv"

    main_logger, mqtt_logger = setup_loggers(main_log_file, mqtt_log_file)

    sleep_time_min = args.sleep_time_min
    sleep_time_max = args.sleep_time_max
    static_behavior = args.static_behavior

    mqtt_broker = args.server_ip or os.getenv('MQTT_BROKER', 'localhost')
    mqtt_client_id = args.client_id or os.getenv('MQTT_CLIENT_ID') or os.getenv('HOSTNAME')
    mqtt_topic = args.topic or os.getenv('MQTT_TOPIC', 'mentored/topic')
    mqtt_mode = args.mode or os.getenv('MQTT_MODE', 'pub')
    mqtt_qos = args.qos or os.getenv('MQTT_QOS', 0)

    mqtt_config = {
        "MQTT_BROKER": mqtt_broker,
        "MQTT_PORT": args.port,
        "MQTT_TOPIC": mqtt_topic,
        "MQTT_MODE": mqtt_mode,
        "MQTT_CLIENT_ID": mqtt_client_id,
        "MQTT_QOS": int(mqtt_qos)
    }

    main_logger.info(f"Starting client with broker: {mqtt_broker}:{args.port}, mode: {mqtt_mode}, topic: {mqtt_topic}, QoS: {mqtt_qos}")
    main_loop(mqtt_config, sleep_time_min, sleep_time_max, static_behavior, main_logger, mqtt_logger)
