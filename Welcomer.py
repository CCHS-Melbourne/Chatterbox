import paho.mqtt.client as mqtt
from Chatter_for_PI_Zero_2W import *
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
    global last_time
    resp=json.loads(msg.payload.decode())
    print(resp)
    if resp['time']>last_time+20:
        thread = create_thread(Message(f"{resp['username']} has just scanned their access card to enter the Connected Community Hackerspace, please welcome them."))
        response = run_thread(thread)
        speak(response)
        last_time=resp['time']
        


last_time=0
    
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
