import RPi.GPIO as GPIO
import time
import DHT11 as DHT
DHTPin = 17     #define the pin of DHT11

def loop():
    dht = DHT.DHT(DHTPin)   #create a DHT class object
    counts = 0 # Measurement counts
    while(True):
        counts += 1
        print("Measurement counts: ", counts)
        for i in range(0,15):            
            chk = dht.readDHT11()     #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
            if (chk is dht.DHTLIB_OK):      #read DHT11 and get a return value. Then determine whether data read is normal according to the return value.
                print("DHT11,OK!")
                break
            time.sleep(0.1)
        print("Humidity : %.2f, \t Temperature : %.2f \n"%(dht.humidity,dht.temperature))
        if(dht.temperature > 24):
            print("The current temperature is %.2f . Would you like to turn on the fan?"(dht.temperature))
        else:
            print("Testing")
        time.sleep(2)       
        
if __name__ == '__main__':
    print ('Program is starting ... ')
    try:
        loop()
    except KeyboardInterrupt:
        GPIO.cleanup()
        exit()
        
        #If the current temperature is greater than 24, send an email to the user with this message
        #“The current temperature is ***. Would you like to turn on the fan?”
        #If the user replies YES, then turn on the fan. Otherwise, do nothing.
        #The fan status should be presented on the dashboard
        