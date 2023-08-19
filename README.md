# DHT22_sensor_MQTT_picoW_V4
Python script to use a Pi Pico W as a base for a DHT22 environmental sensor that uses MQTT. Meant to be used with Home Assistant.

# Hardware Installation:
You'll need a Raspberry Pi Pico W and a DHT22 sensor. (I recommend getting the ones that are on their own little board module with three pins coming out of it, rather than the naked sensor that has 4 pins, as that will require you to add a resistor.) The Pico is about $6 and the DHT22 is about $5 if you get each in multi-packs. 

The DHT22 sensor module will have three pins; ground, power, and data in the middle.
Most DHT22 modules come with connecting wires for each one, so the most convenient way is to solder headers on the three pads you'll be using on the Pico and just use the connecting wires. That way you can swap out the sensor or Pico easier if one of them fails in the future.
Solder or connect via headers the following way:
  - Power goes to pin 36 (3.3 volts)
  - Ground goes to pin 38 (You can use any ground, that one just happens to be nearby the other pins you are using)
  - Data goes to pin 34 (GPIO pin 28)

For power on the sensor, you can use either pin 40 to give it 5 volts or pin 36 for 3.3 volts. The DHT22 module can take either, but if you're running a *really* long wire from the Pico to the sensor for some reason, it will need a bit more juice to work, so use the 5 volt pin in that case.
You can use any GPIO pin you want, you'll just have to change the line of the script where it says sensor = dht.DHT22(Pin(28)) to be whatever pin you are using.
The Pico needs a tiny amount of power. I was able to power one of my sensors using an ancient 0.5A phone charger I have.

# Software Installation:
1. Use Thonny and connect Pico W to your PC
2. Install MicroPython on the Pico
    Run->Configure Interpreter
    Interpreter Tab:
	    Select "MicroPython (Raspberry Pi Pico)"
	    Click "link" that says "Install or update MicroPython"

3. Install micropython-umqtt.simple
    once MicroPython is installed;
    tools->Manage Packages
    search "umqtt simple" in search field
    Click "link" that says "micropython-umqtt.simple"
    follow install instructions

4. Add DHT22_sensor_MQTT_picoW_V4.py to Pico as main.py

# Variables in the script you'll want to change:
- mqtt_update_frequency = 10, transmits data every 10 seconds. Probably excessive, but at least you know within 10 seconds if your sensor dies. If you increase this make sure you change the line when the script intializes the MQTT connection and change keepalive=60 to a number that's about twice the value of mqtt_update_frequency so MQTT doesn't kill the connection.
- mqtt_reset_frequency = 360, Kills and restarts MQTT connection after this many transmissions, just in case your MQTT connections dies for some reason, you'll get a new one every 3600 seconds.
- wifi_ssid = '', change this to the name of your wireless network
- wifi_password = '', change this to the password of your wireless network
- wifi_staticip = '192.168.1.xxx', change this to the ip address on your network you want the sensor to have. I *think* changing it to a string of zero length "" will make it connect with a DHCP address given to it by your router. (Haven't bothered to test this, I like everything to have a static IP if possible.)
- MQTT_BROKER_HOST = "192.168.1.xxx", change to the ip address of the machine hosting Home Assitant.
- MQTT_BROKER_PORT = 1883, default MQTT port. Shouldn't need to change this,
- MQTT_TOPIC = "room/dht22", your MQTT topic.
- MQTT_USERNAME = "", change to the MQTT user account username on Home Assitant
- MQTT_PASSWORD = "", change to the MQTT user account password on Home Assitant
- mqtt_client_id = "room", change this so anything, as long as it's unique from any of your other sensors

# NOTE:
Home Assistant does this very annoying thing, which is possibly a bug, where it will not log temperature or humidity data if the value is the same as the last time data from that sensor was received. MQTT can receive new data, but home assistant does NOT update it's "last received" timestamp. From my testing, it logs the temperature data less and less often over several hours before stopping temperature updates altogether. 

A solution that works is the "updateflip" variable in the script, which adds a digit in the 0.01 place for temperature. Example; this will make a room which is actually 25.6c transmit as flip flopping between 26.61 and 26.60. This *guarantees* that the temperature will be logged with Home Assistant every single update, at the price of being artificially inaccurate by 0.01c with every other temperature update.

This does not seem to be an issue with the humidity readings. I'm pretty sure this is because while the DHT22 temperature values are ±0.5°C accuracy, the humidity values are 2-5% accuracy, and so are changing quite a bit naturally already.
