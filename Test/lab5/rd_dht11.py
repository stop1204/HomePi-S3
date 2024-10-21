import time
import board
import adafruit_dht

# init sensor, use GPIO 26
dht_device = adafruit_dht.DHT11(board.D26)

try:
    while True:
        # read temp&humidity
        temperature = dht_device.temperature
        humidity = dht_device.humidity

        if humidity is not None and temperature is not None:
            print(time.strftime('%d/%m/%y')+" "+time.strftime('%H:%M')+"\tTemp={0:0.1f}C Humidity={1:0.1f}%".format(temperature, humidity))
        #print("Temperature: %d C" % result.temperature)
        #print("Humidity: %d %%" % result.humidity)
        else:
            print("Failed to retrieve data from sensor")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped by User")
except RuntimeError as error:
    # process error
    print(f"RuntimeError: {error.args[0]}")
    time.sleep(2)
