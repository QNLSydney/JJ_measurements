#RT_yoko
# Alexis Jouan 05/09/2019
# Measure the Resistance R as a function of temperature

import time 
import requests
from functools import partial
import time
import numpy as np

from qcodes import Instrument
from qcodes.dataset.measurements import Measurement

import requests

import qcodes_measurements as qcm
from qcodes_measurements.tools.measure import _run_functions, _get_window

def RT_HT(station, voltage, stanford_gain_V, stanford_gain_I):

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-3
    station.yoko.voltage.inter_delay = 0.0001

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.BlueFors_LD.Four_K_temp)
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=(station.BlueFors_LD.Four_K_temp,))
    
    win = qcm.pyplot.PlotWindow(title="R(T)")
    win.resize(750,500)

    num_points = 0
    array_size = 1
    temp_array = np.full((1,), np.nan)
    r_array = np.full((1,), np.nan)


    plot1 = win.addPlot(title="RT 300K - 4K")
    plotdata = plot1.plot(setpoint_x=temp_array)

    plot1.left_axis.label = "Resistance"
    plot1.left_axis.units = "Ohms"
    plot1.bot_axis.label = "Temperature"
    plot1.bot_axis.units = "K"

    j=0

    T = station.BlueFors_LD.Four_K_temp()

    with meas.run() as datasaver:
        
        while T > 4.0:
            T = station.BlueFors_LD.Four_K_temp() 

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
                                (station.BlueFors_LD.Four_K_temp, T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))

            temp_array[num_points] = T
            r_array[num_points] = R_av
            plotdata.xData = temp_array
            plotdata.update(r_array)
            num_points += 1

            if num_points == array_size:
                array_size *= 2
                temp_array.resize(array_size)
                temp_array[array_size//2:] = np.nan
                r_array.resize(array_size)
                r_array[array_size//2:] = np.nan
            
            #print((T,R_av))
            time.sleep(300)
            j = j+1
            
    station.yoko.voltage(0)

def RT_HT_ithaco(station, voltage, stanford_gain_V, gain_ithaco):

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-3
    station.yoko.voltage.inter_delay = 0.0001

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.BlueFors_LD.Four_K_temp)
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=(station.BlueFors_LD.Four_K_temp,))
    
    win = qcm.pyplot.PlotWindow(title="R(T)")
    win.resize(750,500)

    num_points = 0
    array_size = 1
    temp_array = np.full((1,), np.nan)
    r_array = np.full((1,), np.nan)


    plot1 = win.addPlot(title="RT 300K - 4K")
    plotdata = plot1.plot(setpoint_x=temp_array, color=(0, 0, 255))

    plot1.left_axis.label = "Resistance"
    plot1.left_axis.units = "Ohms"
    plot1.bot_axis.label = "Temperature"
    plot1.bot_axis.units = "K"

    j=0

    T = station.BlueFors_LD.Four_K_temp()

    with meas.run() as datasaver:
        
        while T > 4.0:
            T = station.BlueFors_LD.Four_K_temp() 

            station.yoko.voltage(voltage)
            
            time.sleep(1)

            volt_p = station.dmm1.volt()/stanford_gain_V
            curr_p = -station.dmm2.volt()/gain_ithaco
            
            
            station.yoko.voltage(-voltage)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_V
            curr_m = -station.dmm2.volt()/gain_ithaco
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            R_av = V_av/I_av

            datasaver.add_result((station.yoko.voltage, voltage),
                                (station.BlueFors_LD.Four_K_temp, T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))

            temp_array[num_points] = T
            r_array[num_points] = R_av
            plotdata.xData = temp_array
            plotdata.update(r_array)
            num_points += 1

            if num_points == array_size:
                array_size *= 2
                temp_array.resize(array_size)
                temp_array[array_size//2:] = np.nan
                r_array.resize(array_size)
                r_array[array_size//2:] = np.nan
            
            #print((T,R_av))
            time.sleep(60)
            j = j+1
            
    station.yoko.voltage(0)

def RT_LT(station, voltage, stanford_gain_V, stanford_gain_I):
    R_I = 1e4

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-3
    station.yoko.voltage.inter_delay = 0.0001

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.BlueFors_LD.MC_temp)
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=(station.BlueFors_LD.MC_temp,))
    
    win = qcm.pyplot.PlotWindow(title="R(T)")
    win.resize(750,500)

    num_points = 0
    array_size = 1
    temp_array = np.full((1,), np.nan)
    r_array = np.full((1,), np.nan)


    plot1 = win.addPlot(title="RT  4K - 8mK")
    plotdata = plot1.plot(setpoint_x=temp_array)

    plot1.left_axis.label = "Resistance"
    plot1.left_axis.units = "Ohms"
    plot1.bot_axis.label = "Temperature"
    plot1.bot_axis.units = "K"

    j=0

    T =  station.BlueFors_LD.MC_temp()

    with meas.run() as datasaver:
        
        while T > 0.008:
            T =  station.BlueFors_LD.MC_temp()    

            station.yoko.voltage(voltage)
            
            time.sleep(1)

            volt_p = station.dmm1.volt()/stanford_gain_V
            curr_p = station.dmm2.volt()/(R_I*stanford_gain_I) #10kOhm resistor for current meas.
            
            time.sleep(1)
            
            station.yoko.voltage(-voltage)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_V
            curr_m = station.dmm2.volt()/(1e4*stanford_gain_I)
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            R_av = V_av/I_av

            datasaver.add_result((station.yoko.voltage, voltage),
                                ( station.BlueFors_LD.MC_temp, T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))

            temp_array[num_points] = T
            r_array[num_points] = R_av
            plotdata.xData = temp_array
            plotdata.update(r_array)
            num_points += 1

            if num_points == array_size:
                array_size *= 2
                temp_array.resize(array_size)
                temp_array[array_size//2:] = np.nan
                r_array.resize(array_size)
                r_array[array_size//2:] = np.nan
            
            
            #print((T,R_av))
            time.sleep(1)
            j = j+1
            
    station.yoko.voltage(0)


def RT_LT_ithaco(station, voltage, stanford_gain_V, gain_ithaco):

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-3
    station.yoko.voltage.inter_delay = 0.0001

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.BlueFors_LD.MC_temp)
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=(station.BlueFors_LD.MC_temp,))
    
    win = qcm.pyplot.PlotWindow(title="R(T)")
    win.resize(750,500)

    num_points = 0
    array_size = 1
    temp_array = np.full((1,), np.nan)
    r_array = np.full((1,), np.nan)


    plot1 = win.addPlot(title="RT  4K - 8mK")
    plotdata = plot1.plot(setpoint_x=temp_array, color=(0, 0, 255))

    plot1.left_axis.label = "Resistance"
    plot1.left_axis.units = "Ohms"
    plot1.bot_axis.label = "Temperature"
    plot1.bot_axis.units = "K"

    j=0

    T = station.BlueFors_LD.MC_temp()

    with meas.run() as datasaver:
        
        while T  >0.008:
            T = station.BlueFors_LD.MC_temp() 

            station.yoko.voltage(voltage)
            
            time.sleep(1)

            volt_p = station.dmm1.volt()/stanford_gain_V
            curr_p = -station.dmm2.volt()/gain_ithaco
            
            
            station.yoko.voltage(-voltage)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_V
            curr_m = -station.dmm2.volt()/gain_ithaco
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            R_av = V_av/I_av

            datasaver.add_result((station.yoko.voltage, voltage),
                                (station.BlueFors_LD.MC_temp, T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))

            temp_array[num_points] = T
            r_array[num_points] = R_av
            plotdata.xData = temp_array
            plotdata.update(r_array)
            num_points += 1

            if num_points == array_size:
                array_size *= 2
                temp_array.resize(array_size)
                temp_array[array_size//2:] = np.nan
                r_array.resize(array_size)
                r_array[array_size//2:] = np.nan
            
            #print((T,R_av))
            time.sleep(2)
            j = j+1
            
    station.yoko.voltage(0)