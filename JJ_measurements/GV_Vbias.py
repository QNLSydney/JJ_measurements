# GV Vbias
# Alexis Jouan 13/10/2019
# Reading AC current and AC voltage with two lockins

import numpy as np
import time
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime

import qcodes_measurements as qcm
from qcodes_measurements.tools.measure import _run_functions, _get_window

def GV_yoko_up(station, voltages, amplitude, stanford_gain_V_ac, stanford_gain_I_ac):

    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'V_max = {voltages[-1]} V')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 1e-3
    station.yoko.voltage.inter_delay = 10e-3
    
    station.lockin_2.amplitude(amplitude)

    meas = Measurement()

    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.lockin_2.amplitude)

    meas.register_parameter(station.lockin_1.Y, setpoints=(station.yoko.voltage,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.yoko.voltage,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.yoko.voltage,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.yoko.voltage,))
    meas.register_custom_parameter("G_ac", unit="S", setpoints=(station.yoko.voltage,))
    meas.register_custom_parameter("I_dc", unit="A", setpoints=(station.yoko.voltage,))

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

            station.yoko.voltage(v)
            

        time.sleep(1)

        for v in voltages:

            station.yoko.voltage(v)

            
            time.sleep(9*time_constant)

            current_X_AC = station.lockin_2.X()/stanford_gain_I_ac
            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac

            current_Y_AC = station.lockin_2.Y()/stanford_gain_I_ac
            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac

            G_ac = current_X_AC/voltage_X_AC

            datasaver.add_result(("G_ac",G_ac),
                                (station.yoko.voltage, v),
                                (station.lockin_1.Y,current_Y_AC),
                                (station.lockin_2.Y,voltage_Y_AC),
                                (station.lockin_1.X,current_X_AC),
                                (station.lockin_2.X,voltage_X_AC))

        for v in volt_sweep_final:

            station.yoko.voltage(v)

        ID_exp = datasaver.run_id

    station.yoko.voltage(0)
    plot_by_id(ID_exp)

def GV_IV_up(station, voltages, amplitude, stanford_gain_V_ac, stanford_gain_I, stanford_gain_V):

    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'V_max = {voltages[-1]} V')

    int_time = 1 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    #station.dmm2.volt() 
    #station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #print(f'Stanford Gain V ={stanford_gain_V}') TO DO
    #print(f'Stanford Gain I ={stanford_gain_I}')
    print(f'Voltage Max V_max = {voltages[-1]}')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3
    #
    station.lockin_2.amplitude(amplitude)

    meas = Measurement()

    
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.dmm1.volt,))
    meas.register_custom_parameter("G_ac", unit="S", setpoints=(station.dmm1.volt,))
    meas.register_custom_parameter("I_dc", unit="A", setpoints=(station.dmm1.volt,))

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
            time.sleep(500e-3)

        time.sleep(10)

        for v in voltages:

            station.lockin_2.sine_outdc(v)

            v_dc = station.dmm1.volt()/stanford_gain_V

            v_i_dc = station.dmm2.volt()/stanford_gain_I

            i_dc = v_i_dc/R_I

            time.sleep(9*time_constant)

            current_X_AC = station.lockin_2.X()
            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac

            current_Y_AC = station.lockin_2.Y()
            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac

            G_ac = current_X_AC/voltage_X_AC

            datasaver.add_result(("G_ac",G_ac),
                                (station.dmm1.volt, v_dc),
                                (station.dmm2.volt, v_i_dc),
                                ("I_dc",i_dc),
                                (station.lockin_2.sine_outdc, v),
                                (station.lockin_1.Y,current_Y_AC),
                                (station.lockin_2.Y,voltage_Y_AC),
                                (station.lockin_1.X,current_X_AC),
                                (station.lockin_2.X,voltage_X_AC))

        for v in volt_sweep_final:

            station.lockin_2.sine_outdc(v)
            time.sleep(100e-3)


        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)

def GV_IV_yoko_up(station, voltages, amplitude, stanford_gain_V_ac, stanford_gain_I, stanford_gain_V):


    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'V_max = {voltages[-1]} V')

    int_time = 1 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    #station.dmm2.volt() 
    #station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #print(f'Stanford Gain V ={stanford_gain_V}') TO DO
    #print(f'Stanford Gain I ={stanford_gain_I}')
    print(f'Voltage Max V_max = {voltages[-1]}')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    station.yoko.voltage.step = 0.1e-6
    station.yoko.voltage.inter_delay = 5e-4
    #
    station.lockin_2.amplitude(amplitude)

    meas = Measurement()

    
    meas.register_parameter(station.yoko.voltage)
    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.dmm1.volt,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.dmm1.volt,))
    meas.register_custom_parameter("G_ac", unit="S", setpoints=(station.dmm1.volt,))
    meas.register_custom_parameter("I_dc", unit="A", setpoints=(station.dmm1.volt,))

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

            station.yoko.voltage(v)
            time.sleep(100e-3)

        time.sleep(10)

        for v in voltages:

            station.yoko.voltage(v)

            v_dc = station.dmm1.volt()/stanford_gain_V

            i_dc = -station.dmm2.volt()/stanford_gain_I #Using ithaco

            #i_dc = v_i_dc/R_I

            time.sleep(9*time_constant)

            current_X_AC = station.lockin_2.X()/stanford_gain_I
            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac

            current_Y_AC = station.lockin_2.Y()/stanford_gain_I
            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac

            G_ac = current_X_AC/voltage_X_AC

            datasaver.add_result(("G_ac",G_ac),
                                (station.dmm1.volt, v_dc),
                                (station.dmm2.volt, v_i_dc),
                                ("I_dc",i_dc),
                                (station.yoko.voltage, v),
                                (station.lockin_1.Y,current_Y_AC),
                                (station.lockin_2.Y,voltage_Y_AC),
                                (station.lockin_1.X,current_X_AC),
                                (station.lockin_2.X,voltage_X_AC))

        for v in volt_sweep_final:

            station.yoko.voltage(v)
            time.sleep(100e-3)


        ID_exp = datasaver.run_id

    station.yoko.voltage(0)
    plot_by_id(ID_exp)


def GV_2D(station, voltages, v_gates, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Voltage Max V_max = {voltages[-1]} V')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("V_dc_polar", unit="V")
    meas.register_parameter(station.mdac_8.ch01.voltage)

    meas.register_parameter(station.dmm1.volt)
    
    meas.register_parameter(station.dmm2.volt, setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("G_ac", unit="S",setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=(station.dmm1.volt, station.mdac_8.ch01.voltage))

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

    G_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    voltages_live = voltages*1e6 

    plot1 = win.addPlot(title = "G_ac(V_dc, V_g)")
    plot1.plot(setpoint_x = voltages_live, setpoint_y = v_gates)
    plot1.left_axis.label = "V_g"
    plot1.left_axis.units = "V"
    plot1.bot_axis.label = "V_dc_polar"
    plot1.bot_axis.units = "uV"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(200e-3)

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

                v_dc_polar = v

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                G_ac = current_X_AC/voltage_X_AC

                G_ac_plot[j, i] = G_ac

                plot1.traces[0].update(G_ac_plot)


                datasaver.add_result(("V_dc_polar", v_dc_polar),
                                    (station.mdac_8.ch01.voltage, v_g),
                                    ("I_dc", I_dc),
                                    ("G_ac",G_ac),
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
    win.export('figures/Gac_2D_plot_ID_exp_'+str(ID_exp)+'.png')


def GV_B(station, voltages, field_rang_Y, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Voltage Max V_max = {voltages[-1]} V')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("V_dc_polar", unit="V")
    meas.register_parameter(station.mag.y_measured)

    meas.register_parameter(station.dmm1.volt)
    
    meas.register_parameter(station.dmm2.volt, setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_custom_parameter("G_ac", unit="S",setpoints=(station.dmm1.volt, station.mag.y_measured))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=(station.dmm1.volt, station.mag.y_measured))

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
    N = len(field_rang_Y)

    G_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    voltages_live = voltages*1e6 

    plot1 = win.addPlot(title = "G_ac(V_dc, V_g)")
    plot1.plot(setpoint_x = voltages_live, setpoint_y = field_rang_Y)
    plot1.left_axis.label = "V_g"
    plot1.left_axis.units = "V"
    plot1.bot_axis.label = "V_dc_polar"
    plot1.bot_axis.units = "uV"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(200e-3)

        for i, b in enumerate(field_rang_Y):
            station.mag.y_target(b)
            station.mag.ramp('simul')

            while abs(station.mag.y_measured()-b)>0.001:
                time.sleep(2)
            time.sleep(5)

            l_y = station.mag.y_measured()

            print(l_y)

            for j, v in enumerate(voltages):

                station.lockin_2.sine_outdc(v)

                v_dc_polar = v

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                G_ac = current_X_AC/voltage_X_AC

                G_ac_plot[j, i] = G_ac

                plot1.traces[0].update(G_ac_plot)


                datasaver.add_result(("V_dc_polar", v_dc_polar),
                                    (station.mag.y_measured, l_y),
                                    ("I_dc", I_dc),
                                    ("G_ac",G_ac),
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
    win.export('figures/Gac_B_plot_ID_exp_'+str(ID_exp)+'.png')


def GV_B_yoko(station, voltages, currents, amplitude, stanford_gain_V_ac, stanford_gain_V, stanford_gain_I):
    
    #Before using this code change these values according to your own setup :
    
    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'Voltage Max V_max = {voltages[-1]} V')

    int_time = 10 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_2.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #station.yoko.output('off')
    #station.yoko.source_mode("VOLT")
    #station.yoko.output('on')

    #station.yoko.voltage.step = 5e-3
    #station.yoko.voltage.inter_delay = 10e-3

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_custom_parameter("V_dc_polar", unit="V")
    meas.register_parameter(station.yoko.current)

    meas.register_parameter(station.dmm1.volt)
    
    meas.register_parameter(station.dmm2.volt, setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_custom_parameter("I_dc", unit="A",setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_custom_parameter("G_ac", unit="S",setpoints=(station.dmm1.volt, station.yoko.current))
    meas.register_custom_parameter("R_dc", unit="Ohm",setpoints=(station.dmm1.volt, station.yoko.current))

    print(f'Frequency Lockin : {station.lockin_1.frequency()} Hz')

    station.lockin_2.amplitude(amplitude)

    print(f'V_ac polarization : {amplitude*1e3} mV')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')

    station.yoko.current.step = 1e-6
    station.yoko.current.inter_delay = 1e-3
   
    #Preparing the measurement :
    
    v_init = voltages[0]
    v_final = voltages[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_back = np.linspace(v_final, v_init, 2*L)

    M = len(voltages)
    N = len(currents)

    G_ac_plot = np.full((M,N), 0.0)

    win = qcm.pyplot.PlotWindow(title="JJ dev. A")
    win.resize(500,750)

    voltages_live = voltages*1e6 

    plot1 = win.addPlot(title = "G_ac(V_dc, V_g)")
    plot1.plot(setpoint_x = voltages_live, setpoint_y = field_rang_Y)
    plot1.left_axis.label = "V_g"
    plot1.left_axis.units = "V"
    plot1.bot_axis.label = "V_dc_polar"
    plot1.bot_axis.units = "uV"

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)
            time.sleep(200e-3)

        for i, I in enumerate(currents):
            station.yoko.current(I)

            print(I)

            for j, v in enumerate(voltages):

                station.lockin_2.sine_outdc(v)

                v_dc_polar = v

                v_dc = station.dmm1.volt()/stanford_gain_V
                v_i_dc = station.dmm2.volt()/stanford_gain_I

                I_dc = v_i_dc/R_I

                R_dc = v_dc/I_dc

                time.sleep(9*time_constant)

                voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
                current_X_AC = station.lockin_2.X()

                voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
                current_Y_AC = station.lockin_2.Y()

                G_ac = current_X_AC/voltage_X_AC

                G_ac_plot[j, i] = G_ac

                plot1.traces[0].update(G_ac_plot)


                datasaver.add_result(("V_dc_polar", v_dc_polar),
                                    (station.yoko.current, I),
                                    ("I_dc", I_dc),
                                    ("G_ac",G_ac),
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
    win.export('figures/Gac_B_plot_ID_exp_'+str(ID_exp)+'.png')