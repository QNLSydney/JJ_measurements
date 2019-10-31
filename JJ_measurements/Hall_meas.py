# Hall_meas
# Alexis Jouan 31/10/2019
# Hall measurement

import numpy as np
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime

def Hall(V_polar, field_range_Y, stanford_gain_1, stanford_gain_2):

    R_polar = 1e6

    print(f'I_polar = {V_polar/R_polar}')

    R_I = 1e4

    # dmm1 is voltage
    station.dmm1.NPLC(100)

    # dmm2 is current
    station.dmm2.NPLC(10)
    
    station.yoko.voltage.step = 1e-4
    station.yoko.voltage.inter_delay = 0.0001

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.mag.y_target)
    meas.register_parameter(station.mag.y_measured)
    meas.register_parameter(station.dmm1.volt, setpoints = (station.mag.y_target,))
    meas.register_parameter(station.dmm2.volt, setpoints = (station.mag.y_target,))
    meas.register_custom_parameter("R_h", unit = "Ohms", setpoints = (station.mag.y_target,))
    meas.register_custom_parameter("R_xx", unit = "Ohms", setpoints = (station.mag.y_target,))

    with meas.run() as datasaver:
            
        for b in field_range_Y:

            station.mag.y_target(b)
            station.mag.ramp('simul')

            while abs(station.mag.y_measured()-b)>0.001:
                time.sleep(2)
            
            time.sleep(5)

            l_y = station.mag.y_measured()
            
            print(l_y)
            
            station.yoko.voltage(-V_polar)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_1
            curr_m = station.dmm2.volt()/(R_I*stanford_gain_2)
            
            time.sleep(1)
            
            yoko.voltage(V_polar)
            
            time.sleep(1)
            
            volt_p = station.dmm1.volt()/stanford_gain_1
            curr_p = station.dmm2.volt()/(R_I*stanford_gain_2)
            
            time.sleep(1)
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            
            R_av = V_av/I_av
            
            print(R_av)
            
            datasaver.add_result((station.yoko.voltage, station.yoko.voltage()),
                                 (station.dmm2.volt, station.dmm2.volt()),
                                 (station.dmm1.volt, station.dmm1.volt()),
                                 (station.mag.y_measured, l_y),
                                 (station.mag.y_target, b),
                                 ("R_h", R_av))
            station.yoko.voltage(0)
            
    print('Done')    