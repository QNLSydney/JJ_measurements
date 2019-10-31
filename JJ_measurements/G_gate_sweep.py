#G_gate_sweep
#Alexis Jouan 31/10/2019
#Lockin measurement of the resistance of the device as a function of gate voltage

import numpy as np
import time
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime

import qcodes_measurements as qcm
from qcodes_measurements.tools.measure import _run_functions, _get_window

def G_up(station, v_gates, v_polar, amplitude, stanford_gain_V_ac):
    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    #print date and time of the measurement

    #Start the measurement

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_parameter(station.mdac_8.ch01.voltage)

    meas.register_parameter(station.lockin_1.Y, setpoints=(station.mdac_8.ch01.voltage,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.mdac_8.ch01.voltage,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.mdac_8.ch01.voltage,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.mdac_8.ch01.voltage,))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=(station.mdac_8.ch01.voltage,))

    #Prepare the live plot
    win = qcm.pyplot.PlotWindow(title="Gate Sweep 1D")
    win.resize(600,400)

    plot = win.addPlot(title ="R_ac(V_g)")
    plot.update_axes(station.mdac_8.ch01.voltage, station.lockin_1.X)

    R_ac_all = np.full(len(v_gates), np.nan)


    #Print the main lockin settings
    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
   
    time_constant = station.lockin_2.time_constant()
    print(f'Integration time lockins {time_constant} s')

    print(f'Frequency Lockin : {station.lockin_2.frequency()} Hz')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')

    #Initialisation of the lockin

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude/1e-3} mV')

    station.lockin_2.sine_outdc(v_polar)
    print(f'V_dc polarization : {v_polar/1e-3} mV')


    with meas.run() as datasaver:

        for i, v_g in enumerate(v_gates):

            station.mdac_8.ch01.ramp(v_g, 0.01)
            station.mdac_8.ch02.ramp(v_g, 0.01)
            station.mdac_8.ch03.ramp(v_g, 0.01)
            station.mdac_8.ch01.block()
            station.mdac_8.ch02.block()
            station.mdac_8.ch03.block()

            print(v_g)

            time.sleep(5*time_constant)

            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
            current_X_AC = station.lockin_2.X()

            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
            current_Y_AC = station.lockin_2.Y()

            R_ac = voltage_X_AC/current_X_AC

            R_ac_all[i] = R_ac

            trace = plot.plot(setpoint_x = v_gates, pen = (0, 0, 255), name = "R_ac")
            trace.update(R_ac_all)

            datasaver.add_result(("R_ac",R_ac),
                                (station.lockin_2.amplitude, amplitude),
                                (station.lockin_2.sine_outdc, v_polar),
                                (station.mdac_8.ch01.voltage, v_g),
                                (station.lockin_2.Y,current_Y_AC),
                                (station.lockin_1.Y,voltage_Y_AC),
                                (station.lockin_2.X,current_X_AC),
                                (station.lockin_1.X,voltage_X_AC))


        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    station.lockin_2.amplitude(0)

    win.export('figures/Rac_Gate_sweep_1D_ID_exp_'+str(ID_exp)+'.png')

    plot_by_id(ID_exp)
