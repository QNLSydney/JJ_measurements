# GV Ibias
# Reading AC current and AC voltage with two lockins

import numpy as np
import time
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime


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

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude*1e3} mV')

    v_init = voltages[0]
    v_final = voltage[-1]
    L = int(len(voltages)/2)
    volt_sweep_init = np.linspace(0.0, v_init, L)
    volt_sweep_final = np.linspace(v_final, 0.0, L)

    with meas.run() as datasaver:

        for v in volt_sweep_init:

            station.lockin_2.sine_outdc(v)

        for v in voltages:

            station.lockin_2.sine_outdc(v)

            I_dc_polar = v/R_polar

            v_dc = station.dmm1.volt()/stanford_gain_V
            v_i_dc = station.dmm2.volt()/stanford_gain_I

            I_dc = v_i_dc/R_I

            R_dc = v_dc/I_dc

            time.sleep(5*time_constant)

            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
            current_X_AC = station.lockin_2.X()/R_I

            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
            current_Y_AC = station.lockin_2.Y()/R_I

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

        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)
    plot_by_id(ID_exp)
