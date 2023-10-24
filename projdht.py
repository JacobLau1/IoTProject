#Will need to run sudo pip3 install Adafruit_DHT on the rpi to run this code properly
import Adafruit_DHT
import time
sensor = Adafruit_DHT.DHT11

# DHT pin connects to GPIO 17
sensor_pin = 17

while True:
    humidity, temperature = Adafruit_DHT.read_retry(sensor, sensor_pin)  # Use read_retry to retry in case of failure
    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}ºC, Humidity={1:0.1f}%".format(temperature, humidity))
        if(temperature > 24):
            print("send email")
    else:
        print("Error with the DHT11. Make sure the wiring has been done properly.")
    time.sleep(3)