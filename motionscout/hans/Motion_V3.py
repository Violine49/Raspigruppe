#!/usr/bin/python3.7
# Import required Python libraries
import time
import datetime
import RPi.GPIO as GPIO
#from paho.mqtt import client as mqtt_client
import paho.mqtt.client as mqtt
import random

broker = 'IOBroker'
port = 1883
topic = "SmartHome/Motion/PIR3"
# client ID über Zufallsgenerator erzeugen
client_id = f'python-mqtt-{random.randint(0, 1000)}' # f-String

client = mqtt.Client("Motion Test") #client_id
client.connect(broker)

# BCM GPIO-Referenen verwenden (anstelle der Pin-Nummern)
# und GPIO-Eingang definieren
GPIO.setmode(GPIO.BCM)
#       GPIO_PIR = 4  #PIN 7
GPIO_PIR = 17  #PIN 11
GPIO_LED = 5  #PIN 29
# Set GPIO_PIR als input
GPIO.setup(GPIO_PIR,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
# Set GPIO_LED als output 
GPIO.setup(GPIO_LED,GPIO.OUT)
Current_State  = 0
Previous_State = 0

# Variable zählt die Bewegungen
motion_count= 0
# Den Ruhezustand des PIR Sensors abwarten 
print ("Warten, bis PIR im Ruhezustand ist ...")
GPIO.output(GPIO_LED,not GPIO.input(GPIO_PIR))
# Schleife, bis PIR == 0 ist -  PIR braucht Zeit um sich zu formieren
while GPIO.input(GPIO_PIR) != 0:
    time.sleep(0.5)
GPIO.output(GPIO_LED,1)
print ("Bereit...")
print ("%s *** Warten auf Bewegung ***" % datetime.datetime.now())
#**********************************************************************************
try:
    while True :
        # Lese PIR Eingang
        Current_State = GPIO.input(GPIO_PIR)
        if Current_State==1:                   
            time.sleep(1)   #Signal muss mindestens eine Sekunde anliegen
            Current_State = GPIO.input(GPIO_PIR)  # nochmal abfragen
        if Current_State==1 and Previous_State==0:
            # PIR hat angesprochen
            start_time=time.time()
            GPIO.output(GPIO_LED,0)
            print ("%s *** Bewegung beginnt! ***" % datetime.datetime.now())
            motion_count+=1
            # alten Status speichern
            Previous_State=1
        elif Current_State==0 and Previous_State==1:
            # PIR Bewegungs-Erkennung beendet
            stop_time=time.time()
            GPIO.output(GPIO_LED,1)
            elapsed_time=int(stop_time-start_time)
            print ("%s *** Bewegung beendet! ***" % datetime.datetime.now(),sep='',end='')
            print (" Zeitdauer : " + str(elapsed_time) + " sec" + "  Anzahl Bewegungen " + str(motion_count))
            Previous_State=0
            result = client.publish(topic, motion_count)  #MQTT Broker benachrichtigen

except KeyboardInterrupt:
    # Programm beenden
    print ("Ende...")
    GPIO.cleanup()
