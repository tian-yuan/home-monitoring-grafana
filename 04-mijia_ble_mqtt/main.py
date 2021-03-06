#!/usr/bin/env python3

"""MiJia GATT to MQTT"""

import re
import time
import random

import paho.mqtt.client as mqtt

MQTT_TOPIC_HUMIDITY = 'home/mijia/humidity'
MQTT_TOPIC_TEMPERATURE = 'home/mijia/temperature'
MQTT_TOPIC_BATTERY = 'home/mijia/battery'
MQTT_TOPIC_STATE = 'home/mijia/status'

MQTT_PUBLISH_DELAY = 5
MQTT_CLIENT_ID = 'mijia'

#MQTT_SERVER = 'localhost'
MQTT_SERVER = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'

battery = None
temperature = None
humidity = None


def on_connect(client, userdata, flags, rc):
    client.publish(MQTT_TOPIC_STATE, 'connected', 1, True)


def main():
    mqttc = mqtt.Client(MQTT_CLIENT_ID)
    mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqttc.will_set(MQTT_TOPIC_STATE, 'disconnected', 1, True)
    mqttc.on_connect = on_connect

    mqttc.connect(MQTT_SERVER, 1883, 60)
    mqttc.loop_start()

    last_msg_time = time.time()
    reset_variables()

    while True:
        if battery is not None and temperature is not None and humidity is not None:
            delay_gap = time.time() - last_msg_time
            if delay_gap < MQTT_PUBLISH_DELAY:
                time.sleep(MQTT_PUBLISH_DELAY - delay_gap)

            publish_sensor_data(mqttc)
            last_msg_time = time.time()
            reset_variables()


def reset_variables():
    global battery
    global temperature
    global humidity

    battery = None
    temperature = None
    humidity = None
    battery = 90 + random.random()
    temperature = 37 + random.random()
    humidity = 30 + random.random()


def fetch_battery_level(dev):
    global battery

    battery_service = dev.getServiceByUUID(MIJIA_BATTERY_SERVICE_UUID)
    battery_characteristic = battery_service.getCharacteristics(MIJIA_BATTERY_CHARACTERISTIC_UUID)[0]
    battery = ord(battery_characteristic.read())


def fetch_sensor_data(temp_hum):
    global temperature
    global humidity

    pattern = re.compile('T=([\d.-]+) H=([\d.-]+)')
    match = re.match(pattern, temp_hum)
    if match:
        temperature = match.group(1)
        humidity = match.group(2)


def publish_sensor_data(mqttc):
    print('publish data to mqtt server.')
    mqttc.publish(MQTT_TOPIC_TEMPERATURE, temperature, 1, True)
    mqttc.publish(MQTT_TOPIC_HUMIDITY, humidity, 1, True)
    mqttc.publish(MQTT_TOPIC_BATTERY, battery, 1, True)


if __name__ == '__main__':
    print('Starting MiJia GATT client')
    main()
