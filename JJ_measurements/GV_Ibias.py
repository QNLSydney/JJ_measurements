# GV Ibias
# Alexis Jouan 17/10/2019
# Reading AC current and AC voltage with two lockins

import numpy as np
import time
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime

import qcodes_measurements as qcm
from qcodes_measurements.tools.measure import _run_functions, _get_window

def GV_up(station, voltages, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Current Max I_max = {voltages[-1]/R_polar} A')

    int_time = 1 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_1.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("I_dc_polar", unit="A")

    meas.register_parameter(station.dmm1.volt, setpoints=("I_dc_polar",))
    meas.register_parameter(station.dmm2.volt, setpoints=("I_dc_polar",))
    meas.register_parameter(station.lockin_1.Y, setpoints=("I_dc_polar",))
    meas.register_parameter(station.lockin_2.Y, setpoints=("I_dc_polar",))
    meas.register_parameter(station.lockin_1.X, setpoints=("I_dc_polar",))
    meas.register_parameter(station.lockin_2.X, setpoints=("I_dc_polar",))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=("I_dc_polar",))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=("I_dc_polar",))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=("I_dc_polar",))

    print(f'Frequency Lockin : {station.lockin_1.frequency()} Hz')

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude*1e3} mV')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')
   

    v_init = voltages[0]
    v_final = voltages[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_final = np.linspace(v_final, 0.0, L)


    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)

        time.sleep(3)

        for v in voltages:

            station.lockin_2.sine_outdc(v)

            I_dc_polar = v/R_polar

            v_dc = station.dmm1.volt()/stanford_gain_V
            v_i_dc = station.dmm2.volt()/stanford_gain_I

            I_dc = v_i_dc/R_I

            R_dc = v_dc/I_dc

            time.sleep(9*time_constant)

            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
            current_X_AC = station.lockin_2.X()

            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
            current_Y_AC = station.lockin_2.Y()

            R_ac = voltage_X_AC/current_X_AC

            datasaver.add_result(("I_dc_polar", I_dc_polar),
                                ("I_dc", I_dc),
                                ("R_ac",R_ac),
                                ("R_dc", R_dc),
                                (station.dmm1.volt, v_dc),
                                (station.dmm2.volt, v_i_dc),
                                (station.lockin_2.amplitude, amplitude),
                                (station.lockin_2.sine_outdc, v),
                                (station.lockin_2.Y,current_Y_AC),
                                (station.lockin_1.Y,voltage_Y_AC),
                                (station.lockin_2.X,current_X_AC),
                                (station.lockin_1.X,voltage_X_AC))

        for v in volt_sweep_final:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)

        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)


def GV_2D(station, voltages, v_gates, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Current Max I_max = {voltages[-1]/R_polar} A')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_1.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("I_dc_polar", unit="A")
    meas.register_parameter(station.mdac_8.ch01.voltage)

    meas.register_parameter(station.dmm1.volt, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_parameter(station.dmm2.volt, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_1.Y, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_2.Y, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_1.X, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_2.X, setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=("I_dc_polar",station.mdac_8.ch01.voltage))

    print(f'Frequency Lockin : {station.lockin_1.frequency()} Hz')

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude*1e3} mV')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')
   
    #Preparing the measurement :
    
    v_init = voltages[0]
    v_final = voltages[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_back = np.linspace(v_final, v_init, 2*L)

    M = len(voltages)
    N = len(v_gates)

    R_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    currents = voltages*1e3 

    plot1 = win.addPlot(title = "R_ac(I_dc, V_g)")
    plot1.plot(setpoint_x = currents, setpoint_y = v_gates)
    plot1.left_axis.label = "V_g"
    plot1.left_axis.units = "V"
    plot1.bot_axis.label = "I_dc"
    plot1.bot_axis.units = "nA"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)

        for i, v_g in enumerate(v_gates):

            station.mdac_8.ch01.ramp(v_g, 0.01)
            station.mdac_8.ch02.ramp(v_g, 0.01)
            station.mdac_8.ch03.ramp(v_g, 0.01)
            station.mdac_8.ch01.block()
            station.mdac_8.ch02.block()
            station.mdac_8.ch03.block()

            print(f'V_g = {v_g} V')

            for j, v in enumerate(voltages):

                station.lockin_2.sine_outdc(v)

                I_dc_polar = v/R_polar

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                R_ac = voltage_X_AC/current_X_AC

                R_ac_plot[j, i] = R_ac

                plot1.traces[0].update(R_ac_plot)


                datasaver.add_result(("I_dc_polar", I_dc_polar),
                                    (station.mdac_8.ch01.voltage, v_g),
                                    ("I_dc", I_dc),
                                    ("R_ac",R_ac),
                                    ("R_dc", R_dc),
                                    (station.dmm1.volt, v_dc),
                                    (station.dmm2.volt, v_i_dc),
                                    (station.lockin_2.amplitude, amplitude),
                                    (station.lockin_2.sine_outdc, v),
                                    (station.lockin_2.Y,current_Y_AC),
                                    (station.lockin_1.Y,voltage_Y_AC),
                                    (station.lockin_2.X,current_X_AC),
                                    (station.lockin_1.X,voltage_X_AC))

            for v in volt_sweep_back:

                station.lockin_2.sine_outdc(v)
                time.sleep(100e-3)

            time.sleep(3)

        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)
    win.export('figures/Rac_2D_plot_ID_exp_'+str(ID_exp)+'.png')

def GV_B(station, voltages, field_range_Y, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Current Max I_max = {voltages[-1]/R_polar} A')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_1.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("I_dc_polar", unit="A")
    meas.register_parameter(station.mag.y_measured)

    meas.register_parameter(station.dmm1.volt, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_parameter(station.dmm2.volt, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_parameter(station.lockin_1.Y, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_parameter(station.lockin_2.Y, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_parameter(station.lockin_1.X, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_parameter(station.lockin_2.X, setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=("I_dc_polar", station.mag.y_measured))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=("I_dc_polar", station.mag.y_measured))

    print(f'Frequency Lockin : {station.lockin_1.frequency()} Hz')

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude*1e3} mV')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')
   
    #Preparing the measurement :
    
    v_init = voltages[0]
    v_final = voltages[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_back = np.linspace(v_final, v_init, 2*L)

    M = len(voltages)
    N = len(field_range_Y)

    R_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    currents = voltages*1e3 

    plot1 = win.addPlot(title = "R_ac(I_dc, V_g)")
    plot1.plot(setpoint_x = currents, setpoint_y = field_range_Y)
    plot1.left_axis.label = "V_g"
    plot1.left_axis.units = "V"
    plot1.bot_axis.label = "I_dc"
    plot1.bot_axis.units = "nA"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)

        for i, b in enumerate(field_range_Y):

            station.mag.y_target(b)
            station.mag.ramp('simul')

            time.sleep(2)

            l_y = station.mag.y_measured()

            print(l_y)


            for j, v in enumerate(voltages):

                station.lockin_2.sine_outdc(v)

                I_dc_polar = v/R_polar

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc_polar

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                R_ac = voltage_X_AC/current_X_AC

                R_ac_plot[j, i] = R_ac

                plot1.traces[0].update(R_ac_plot)


                datasaver.add_result(("I_dc_polar", I_dc_polar),
                                    (station.mag.y_measured, b),
                                    ("I_dc", I_dc),
                                    ("R_ac",R_ac),
                                    ("R_dc", R_dc),
                                    (station.dmm1.volt, v_dc),
                                    (station.dmm2.volt, v_i_dc),
                                    (station.lockin_2.amplitude, amplitude),
                                    (station.lockin_2.sine_outdc, v),
                                    (station.lockin_2.Y,current_Y_AC),
                                    (station.lockin_1.Y,voltage_Y_AC),
                                    (station.lockin_2.X,current_X_AC),
                                    (station.lockin_1.X,voltage_X_AC))

            for v in volt_sweep_back:

                station.lockin_2.sine_outdc(v)
                time.sleep(100e-3)

            time.sleep(3)

        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)
    win.export('figures/Rac_B_plot_ID_exp_'+str(ID_exp)+'.png')

def GV_B_yoko(station, voltages, currents_B, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Current Max I_max = {voltages[-1]/R_polar} A')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_1.time_constant()

    print(f'Integration time lockins {time_constant} s')

    station.yoko.output('off')
    station.yoko.source_mode("CURR")
    station.yoko.output('on')

    station.yoko.current.step = 1e-6
    station.yoko.current.inter_delay = 1e-3


    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("I_dc_polar", unit="A")
    meas.register_parameter(station.yoko.current)

    meas.register_parameter(station.dmm1.volt, setpoints=("I_dc_polar", station.yoko.current))
    meas.register_parameter(station.dmm2.volt, setpoints=("I_dc_polar", station.yoko.current))
    meas.register_parameter(station.lockin_1.Y, setpoints=("I_dc_polar", station.yoko.current))
    meas.register_parameter(station.lockin_2.Y, setpoints=("I_dc_polar", station.yoko.current))
    meas.register_parameter(station.lockin_1.X, setpoints=("I_dc_polar",station.yoko.current))
    meas.register_parameter(station.lockin_2.X, setpoints=("I_dc_polar", station.yoko.current))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=("I_dc_polar", station.yoko.current))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=("I_dc_polar", station.yoko.current))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=("I_dc_polar", station.yoko.current))

    print(f'Frequency Lockin : {station.lockin_1.frequency()} Hz')

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude*1e3} mV')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')
    
   
    #Preparing the measurement :
    
    v_init = voltages[0]
    v_final = voltages[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_back = np.linspace(v_final, v_init, 2*L)

    M = len(voltages)
    N = len(currents_B)

    R_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    currents = voltages*1e3 

    plot1 = win.addPlot(title = "R_ac(I_dc, V_g)")
    plot1.plot(setpoint_x = currents, setpoint_y = currents_B)
    plot1.left_axis.label = "I"
    plot1.left_axis.units = "A"
    plot1.bot_axis.label = "I_dc"
    plot1.bot_axis.units = "nA"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)

        for i, I in enumerate(currents_B):

            station.yoko.current(I)

            print(I)


            for j, v in enumerate(voltages):

                station.lockin_2.sine_outdc(v)

                I_dc_polar = v/R_polar

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc_polar

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                R_ac = voltage_X_AC/current_X_AC

                R_ac_plot[j, i] = R_ac

                plot1.traces[0].update(R_ac_plot)


                datasaver.add_result(("I_dc_polar", I_dc_polar),
                                    (station.yoko.current, I),
                                    ("I_dc", I_dc),
                                    ("R_ac",R_ac),
                                    ("R_dc", R_dc),
                                    (station.dmm1.volt, v_dc),
                                    (station.dmm2.volt, v_i_dc),
                                    (station.lockin_2.amplitude, amplitude),
                                    (station.lockin_2.sine_outdc, v),
                                    (station.lockin_2.Y,current_Y_AC),
                                    (station.lockin_1.Y,voltage_Y_AC),
                                    (station.lockin_2.X,current_X_AC),
                                    (station.lockin_1.X,voltage_X_AC))

            for v in volt_sweep_back:

                station.lockin_2.sine_outdc(v)
                time.sleep(100e-3)

            time.sleep(3)

        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)
    win.export('figures/Rac_B_yoko_plot_ID_exp_'+str(ID_exp)+'.png')