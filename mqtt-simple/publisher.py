#!/usr/bin/env python3
import os
import time
import random
import paho.mqtt.client as mqtt

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

# Callback when a message is published
def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# Get environment variables for broker and port
mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')
mqtt_port = int(os.getenv('MQTT_PORT', 1883))
# Client id default to hostname
if os.getenv("MQTT_CLIENT_ID") is None:
    mqtt_client_id = os.getenv("HOSTNAME", "mqtt_random_data_sender")
sleep_time_in_seconds = float(os.getenv("SLEEP_TIME", 1.0))  # Default to 1000 ms

# Initialize the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, mqtt_client_id)

# Set the callback functions
client.on_connect = on_connect
client.on_publish = on_publish

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Start the loop in a background thread to process the network traffic
client.loop_start()

# Publish random data continuously every 5 seconds
try:
    while True:
        random_data = random.randint(1, 100)
        client.publish("test/topic", payload=random_data, qos=0)
        print(f"Sent data: {random_data}")
        time.sleep(sleep_time_in_seconds)
except KeyboardInterrupt:
    print("Stopped by user")

# Stop the loop and disconnect cleanly
client.loop_stop()
client.disconnect()