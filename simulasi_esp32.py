"""Simulator ESP32: publish sensor DHT22 + subscribe perintah kontrol & notifikasi."""
import paho.mqtt.client as mqtt
import json, time, random
from datetime import datetime

BROKER = "localhost"
TOPIC_SENSOR = "iot/sensor"
TOPIC_KONTROL = "iot/kontrol"
TOPIC_NOTIF = "iot/notifikasi"

# Kompatibel paho-mqtt v2 (CallbackAPIVersion) maupun v1
try:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="ESP32-Simulator")
except AttributeError:
    client = mqtt.Client("ESP32-Simulator")

lamp = "off"

def on_connect(client, userdata, *args):
    client.subscribe([(TOPIC_KONTROL, 0), (TOPIC_NOTIF, 0)])
    print("✓ Terhubung ke broker, subscribe iot/kontrol & iot/notifikasi")

def on_message(client, userdata, msg):
    global lamp
    try:
        data = json.loads(msg.payload.decode())
    except ValueError:
        return
    if msg.topic == TOPIC_KONTROL:
        if data.get("device") == "lamp":
            lamp = data.get("action", lamp)
        print(f"← KONTROL diterima: {data} | LED sekarang: {lamp.upper()}")
    else:
        print(f"⚠ NOTIFIKASI: {data.get('message')}")

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.loop_start()

print("ESP32 Simulator berjalan... Ctrl+C untuk stop")
try:
    while True:
        data = {
            "suhu": round(random.uniform(25, 34), 1),   # sampai 34 agar threshold bisa terpicu
            "kelembaban": round(random.uniform(55, 80), 1),
            "timestamp": datetime.now().isoformat(),
        }
        client.publish(TOPIC_SENSOR, json.dumps(data))
        print(f"→ Publish: {data}")
        time.sleep(3)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()
