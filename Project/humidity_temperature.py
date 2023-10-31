import time
import Freenove_DHT as DHT
##import Adafruit_DHT

DHTPin = 17

class HumidityTemperature :
    '''
    DHTPin = 17
    dht_sensor = Adafrut_DHT.DHT11
    humidity, temperature = Adafruit_DHT.read_retry(dht_sensor, DHTPin)

    gpio = 0
    dht = 0

    def __init__(self, gpio) :
        self.gpio = gpio
        self.dht = DHT.DHT(self.gpio)
        
    def getHumAndTemp(self):
        data = dict()
        chk = self.dht.readDHT11()
        
        if (chk is self.dht.DHTLIB_OK):
            time.sleep(0.1)
            '''
    def getHumAndTemp():
        data = dict()
        data['humidity'] = 55
        data['temperature'] = 21
        return data
