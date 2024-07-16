import paho.mqtt.client as mqtt
from chatter3 import *
import json

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("lunar_gate")

class Message:
    def __init__(self,text):
        self.text=text
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global greeting_now
    print(greeting_now)
    if not greeting_now:
        greeting_now=True
        resp=json.loads(msg.payload.decode())
        thread = create_thread(Message(f"{resp['username']} has just scanned their access card to enter the hackerspace, please welcome them."))
        response = run_thread(thread)
        speak(response)
        greeting_now=False

greeting_now=False
    
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.0.6", 1883, 60)

pygame.mixer.init()

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
mqttc.loop_forever()
