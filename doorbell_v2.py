# Added code related to MQTT in case want to integrate it 
# in the future, but for now only using RF
import paho.mqtt.client as mqtt 
import paho.mqtt.publish as publish 
import picamera 
import argparse 
import signal 
import sys 
import glob
import os
import time 
from datetime import datetime
import logging 
from rpi_rf import RFDevice 
import telepot

rfdevice = None 
### camera 
camera = picamera.PiCamera() 
camera.vflip=True 
#

def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    print('Got command %s' % command)

    if command == '/news':
        bot.sendMessage(chat_id, 'Here are some news...')
    elif command == '/showmehome':
        print('Taking photo') 
        camera.capture('image.jpg') 
        file_name = 'image_showmehome_' + str(datetime.now()) + '.jpg' 
        camera.capture(file_name)  # time-stamped image 
        with open('image.jpg', "rb") as imageFile: 
            myFile = imageFile.read() 
        bot.sendPhoto(chat_id, open('image.jpg', "rb"))
        bot.sendMessage(chat_id, str(datetime.now()))
        print(file_name + ' image saved and sent') 
    elif command == '/lastdoorbell':
        list_of_files = glob.glob('/var/www/html/images/image_doorbell_*')
        latest_file = max(list_of_files, key=os.path.getctime)
        bot.sendPhoto(chat_id, open(latest_file, "rb"))
        bot.sendMessage(chat_id, latest_file)

### telepot
bot = telepot.Bot('XXX')
bot.message_loop(handle)
print('Telepot listening...')

def post_image(): 
    # chat_id = response['message']['chat']['id']
    print('Taking photo') 
    camera.capture('image.jpg') 
    file_name = 'image_doorbell_' + str(datetime.now()) + '.jpg' 
    camera.capture(file_name)  # time-stamped image 
    with open('image.jpg', "rb") as imageFile: 
        myFile = imageFile.read() 
    #    data = bytearray(myFile) 
#    client.publish('dev/camera', data, mqttQos, mqttRetained)  # 
#    client.publish('dev/test', 'Capture!') 
    print(file_name + ' image published') 

### MQTT 
# broker = '192.168.0.100' 
# topic ='dev/test' 
# mqttQos = 0 
# mqttRetained = False 

# def on_connect(client, userdata, flags, rc): 
#    print("Connected with result code "+str(rc)) 
#    client.subscribe(topic) 
# # The callback for when a PUBLISH message is received from the server.

# def on_message(client, userdata, msg): 
#    payload = str(msg.payload.decode('ascii'))  # decode the binary string 
#    print(msg.topic + " " + payload) 
#    process_trigger(payload) 

# def process_trigger(payload): 
#    if payload == 'ON': 
#        print('ON triggered') 
#        post_image() 

#client = mqtt.Client() 
#client.on_connect = on_connect    # call these on connect and on message 
#client.on_message = on_message 
#client.username_pw_set(username='user',password='pass')  # need this 
#print("Connecting to broker...")
#client.connect(broker) 
#client.loop_forever()    #  don't get past this 
#client.loop_start()    #  run in background and free up main thread 

### RF 

def exithandler(signal, frame): 
   rfdevice.cleanup() 
   sys.exit(0) 
logging.basicConfig(level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S', 
                   format='%(asctime)-15s - [%(levelname)s] %(module)s: %(message)s', ) 
parser = argparse.ArgumentParser(description='Receives a decimal code via a 433/315MHz GPIO device') 
parser.add_argument('-g', dest='gpio', type=int, default=27, 
                   help="GPIO pin (Default: 27)") 
args = parser.parse_args() 
signal.signal(signal.SIGINT, exithandler) 
rfdevice = RFDevice(args.gpio) 
rfdevice.enable_rx() 
timestamp = None 
logging.info("Listening for codes on GPIO " + str(args.gpio)) 
code_of_interest = '36864' 
code_of_interest2 = '32768' 
code_of_interest3 = '73728'

while True: 
   if rfdevice.rx_code_timestamp != timestamp: 
       timestamp = rfdevice.rx_code_timestamp 
       print(str(rfdevice.rx_code)) 
       if str(rfdevice.rx_code) == code_of_interest or str(rfdevice.rx_code) == code_of_interest2 or str(rfdevice.rx_code) == code_of_interest3: 
           post_image() 
           time.sleep(1)  # prevent registering multiple times 
   time.sleep(0.01) 
rfdevice.cleanup() 
