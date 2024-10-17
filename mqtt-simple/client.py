#!/usr/bin/env python3
import os
import time
import random
import paho.mqtt.client as mqtt

# Callback when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:  # Successful connection
        if mqtt_mode == "sub":
            client.subscribe("test/topic", qos=0)
            print("Subscribed to test/topic")
    else:
        print(f"Connection failed with result code {rc}")

# Callback when a message is published
def on_publish(client, userdata, mid):
    print(f"Message {mid} published")

# Callback when a message is received
def on_message(client, userdata, message):
    print(f"Received message: '{message.payload.decode()}' on topic: '{message.topic}'")

# Callback when the client disconnects
def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")

# Get environment variables
# If there's an argment use it as the broker address
if len(os.sys.argv) > 1:
    mqtt_broker = os.sys.argv[1]
else:
    mqtt_broker = os.getenv('MQTT_BROKER', 'localhost')

mqtt_port = int(os.getenv('MQTT_PORT', 1883))
mqtt_mode = os.getenv('MQTT_MODE', 'pub')  # "pub" for publisher, "sub" for subscriber
# Use hostname as MQTT client ID if not provided
# if MQTT_CLIENT_ID is set
hostname = os.getenv('HOSTNAME')
if os.environ.get('MQTT_CLIENT_ID') is None:
    mqtt_client_id = hostname
else:
    mqtt_client_id = os.getenv('MQTT_CLIENT_ID', 'mqtt_random_data_sender')

sleep_time_in_seconds = float(os.getenv("SLEEP_TIME", 1.0))

# Initialize the MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, mqtt_client_id)

# Set callback functions
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.on_disconnect = on_disconnect

# Connect to the MQTT broker
client.connect(mqtt_broker, mqtt_port, 60)

# Publisher mode
if mqtt_mode == "pub":
    client.loop_start()  # Start the loop in a background thread
    try:
        while True:
            random_data = random.randint(1, 100)
            client.publish("test/topic", payload=random_data, qos=0)
            print(f"Sent data: {random_data}")
            time.sleep(sleep_time_in_seconds)
    except KeyboardInterrupt:
        print("Publisher stopped by user")
    finally:
        client.loop_stop()
        client.disconnect()

# Subscriber mode
elif mqtt_mode == "sub":
    client.loop_forever()  # Block and wait for messages
