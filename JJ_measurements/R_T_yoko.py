# Measure the Resistance R as a function of temperature
import time 
import requests
from functools import partial
import time
import numpy as np

from qcodes import Instrument
from qcodes.dataset.measurements import Measurement

import qcodes_measurements as qcm
from qcodes_measurements.tools.measure import _run_functions, _get_window

class FridgeTemps(Instrument):
    def __init__(self, fridge, url):
        super().__init__(fridge)
        self.url = url
        
        params = requests.get(url)
        if params.status_code != 200:
            raise RuntimeError("Unable to query fridge")
        params = set(params.json().keys())
        params.remove("Time")
        params = tuple(params)
        self.params = params
        
        for param in params:
            self.add_parameter(f"{param}_temp",
                               unit="K",
                               label=f"{param}",
                               get_cmd=partial(self.get_param, param),
                               snapshot_get=False)
        
    def get_param(self, param):
        temps = requests.get(self.url)
        if temps.status_code != 200:
            raise RuntimeError("Unable to query fridge")
        temps = temps.json()
        return temps[param]
try:
    T = ft.Four_K_temp()
    print('Four K temp :', T)
except NameError:
    ft = FridgeTemps("BlueFors_LD", 
     "https://qphys1114.research.ext.sydney.edu.au/therm_flask/BlueFors_LD/data/?current")
    print('Loading Temperature Data')


def RT_yoko(station, meas, voltage, stanford_gain_V, stanford_gain_I):

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-6
    station.yoko.voltage.inter_delay = 0.0001

    meas.register_parameter(station.yoko.voltage)
    meas.register_custom_parameter("Temperature", unit = "K")
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=("Temperature",))
    
    j=0

    T = ft.Four_K_temp()

    with meas.run() as datasaver:
        
        while T > 4.0:
            T = ft.Four_K_temp()    

            station.yoko.voltage(voltage)
            
            time.sleep(1)

            volt_p = station.dmm1.volt()/stanford_gain_V
            curr_p = station.dmm2.volt()/(1e4*stanford_gain_I) #10kOhm resistor for current meas.
            
            time.sleep(1)
            
            station.yoko.voltage(-voltage)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_V
            curr_m = station.dmm2.volt()/(1e4*stanford_gain_I)
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            R_av = V_av/I_av

            datasaver.add_result((station.yoko.voltage, voltage),
                                ("Temperature", T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))
            
            print((T,R_av))
            time.sleep(300)
            j = j+1
            
    station.yoko.voltage(0)