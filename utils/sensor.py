import time
import numpy as np
import Adafruit_ADS1x15
import RPi.GPIO as GPIO

GAIN = 1
adc = Adafruit_ADS1x15.ADS1115()

class Sensor:

    def read(self):
        dato = []
        i = 1
        while i <= 100:
            values0 = adc.read_adc(0, gain=GAIN)
            dato.append(values0)
            i += 1
        
        desv = np.std(dato)        
        dato = []
        return round(0.002103*desv,2)