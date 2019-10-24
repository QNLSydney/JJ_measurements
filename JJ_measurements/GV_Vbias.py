# GV Vbias
# Reading AC current and AC voltage with two lockins

import numpy as np
import time
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime


def GV_up(station, voltages, amplitude, stanford_gain_V_ac, stanford_gain_I, stanford_gain_V):

    R_I = 1e4 #value of the resistor used to measure the current

    now = datetime.now()
    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)    

    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
    print(f'Stanford Gain I_DC ={stanford_gain_I}')
    print(f'Stanford Gain V_DC ={stanford_gain_V}')
    print(f'V_max = {voltages[-1]} V')


    

    print(f'Integration time DC = {int_time*0.02} s')

    time_constant = station.lockin_1.time_constant()

    print(f'Integration time lockins {time_constant} s')

    #print(f'Stanford Gain V ={stanford_gain_V}') TO DO
    #print(f'Stanford Gain I ={stanford_gain_I}')
    print(f'Voltage Max V_max = {voltages[-1]}')

    int_time = 1 #Integration time of the dmm's

    station.dmm1.volt()
    station.dmm1.NPLC(int_time)

    station.dmm2.volt() 
    station.dmm2.NPLC(int_time)

    #station.dmm2.volt() 
    #station.dmm2.NPLC(int_time)

    print(f'Integration time = {int_time*0.02} s')

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
    meas.register_parameter(station.dmm1.volt, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_parameter(station.dmm2.volt, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_parameter(station.lockin_1.Y, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.lockin_2.sine_outdc,))
    meas.register_custom_parameter("G", unit="S", setpoints=(station.lockin_2.sine_outdc,))

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

            v_dc = station.dmm1.volt()/stanford_gain_V

            i_dc = station.dmm2.volt()/stanford_gain_I

            time.sleep(5*time_constant)

            current_X_AC = station.lockin_2.X()/stanford_gain_V_ac
            voltage_X_AC = station.lockin_1.X()

            current_Y_AC = station.lockin_2.Y()/stanford_gain_V_ac
            voltage_Y_AC = station.lockin_1.Y()

            G_ac = current_X_AC/voltage_X_AC

            datasaver.add_result(("G",G_ac),
                                (station.dmm1.volt, v_dc),
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
