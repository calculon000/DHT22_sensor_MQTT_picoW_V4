#DHT22_sensor_MQTT_picoW_V4 by Jamison 'Calculon000' Ward

from machine import Pin
from machine import WDT
from time import sleep
import network
import dht
from umqtt.simple import MQTTClient

#loop time settings
# the DHT22 returns at most one measurement every 2s
mqtt_update_frequency = 10 
mqtt_reset_frequency = 360 
#This is just watchdog timer stuff that resets the pi if the script freezes. You shouldn't need to adjust this even if you change the other timer variables.
WDT_timeout = 5000
WDT_feed_delay = float(WDT_timeout / 2000)
WDT_loops = float(mqtt_update_frequency/WDT_feed_delay)
updateflip=0

wdt = WDT(timeout=WDT_timeout) #timeout to restart pico if program freezes

led = Pin("LED", Pin.OUT)
led.off()

# DHT22 sensor settings
sensor = dht.DHT22(Pin(28))

# wlan settings
wifi_ssid = ''
wifi_password = ''
wifi_staticip = '192.168.1.xxx'

# MQTT broker settings
MQTT_BROKER_HOST = "192.168.1.xxx"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "room/dht22"
MQTT_USERNAME = "mqtt"
MQTT_PASSWORD = ""
mqtt_client_id = "room"

def WDT_sleep():
    for i in range(WDT_loops):
        wdt.feed()
        sleep(WDT_feed_delay)
    wdt.feed()

def blink(numblinks,speed=0.1):
    for i in range(numblinks*2):
        led.toggle()
        sleep(speed)
    #return

def wifi_connect(wifi_ssid,wifi_password,wifi_staticip):
    good_connection= False
    while good_connection == False:
        wlan = network.WLAN(network.STA_IF)
        wlan.ifconfig((wifi_staticip, '255.255.255.0', '192.168.1.254', '8.8.8.8'))
        wlan.active(True)
        wlan.connect(wifi_ssid, wifi_password)
        for ct in range(5):
            if wlan.isconnected() == True:
                good_connection= True
            else:
                print('waiting for connection...')
                wdt.feed()
                sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'WiFi Connected on {ip}')
    #return ip

# Connect to WiFi
try:
    wifi_connect(wifi_ssid,wifi_password,wifi_staticip)
except OSError as error:
    print(f'Wifi Error {error}')

try:
    while True:        
        # Initialize our MQTTClient and connect to the MQTT server
        mqtt_client = MQTTClient(
            client_id=mqtt_client_id,
            server=MQTT_BROKER_HOST,
            port=MQTT_BROKER_PORT,
            keepalive=60,
            user=MQTT_USERNAME,
            password=MQTT_PASSWORD)
        mqtt_client.connect()
        wdt.feed()
        blink(1,1)

        for i in range(mqtt_reset_frequency):
            sensor.measure()     # Recovers measurements from the sensor
            temperature=round(float(sensor.temperature()),1)
            print(f"Temperature : {temperature}{updateflip}°C")
            mqtt_client.publish(MQTT_TOPIC + "/temperature", f"{temperature}{updateflip}")
            updateflip+=1
            updateflip%=2
            humidity=sensor.humidity()
            print(f"Humidity    : {humidity}%")
            mqtt_client.publish(MQTT_TOPIC + "/humidity", f"{humidity}")
            blink(1,0.05)
            WDT_sleep()     
        mqtt_client.disconnect()
        WDT_sleep()
except Exception as e:
    print(f'MQTT Error: {e}')
