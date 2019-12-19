# IV_Ibias
# Alexis Jouan 05/09/2019
# IV Ibias using a 1 MOhm resistor for current bias and 10kOhm to read the current

import numpy as np
from qcodes.dataset.measurements import Measurement
from qcodes.dataset.plotting import plot_by_id
from datetime import datetime

def IV_up(station, voltages, stanford_gain_V, stanford_gain_I):
	now = datetime.now()
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print(dt_string)	

	R_polar = 1e6 #Value of the resistance used to induce a current
	R_I = 1e4 #The value of the resistor used to measure the current

	print(f'Stanford Gain V ={stanford_gain_V}')
	print(f'Stanford Gain I ={stanford_gain_I}')
	print(f'Current Max I_max = {voltages[-1]/R_polar}')

	int_time = 1 #Integration time of the dmm's

	station.dmm1.volt()
	station.dmm1.NPLC(int_time)

	station.dmm2.volt()
	station.dmm2.NPLC(int_time)

	print(f'Integration time = {int_time*0.02} s')

	station.yoko.output('off') 
	station.yoko.source_mode("VOLT") 
	station.yoko.output('on')

	station.yoko.voltage.step = 1e-3
	station.yoko.voltage.inter_delay = 1e-3

	meas = Measurement()

	meas.register_parameter(station.yoko.voltage)
	meas.register_parameter(station.dmm2.volt)
	meas.register_custom_parameter("Current", unit="A")
	meas.register_parameter(station.dmm1.volt, setpoints=("Current",))

	with meas.run() as datasaver:

	    ID_exp = datasaver.run_id

	    for v in voltages:

	        station.yoko.voltage(v)

	        voltage_meas = station.dmm1.volt()/stanford_gain_V
	        current_meas = station.dmm2.volt()/(R_I*stanford_gain_I)

	        datasaver.add_result((station.yoko.voltage,v),
	                            (station.dmm2.volt,station.dmm2.volt()),
	                            ("Current",current_meas),
                                (station.dmm1.volt,voltage_meas))

	station.yoko.voltage(0)
	plot_by_id(ID_exp)


def IV_gate_sweep(station, voltages, v_gates, stanford_gain_V, stanford_gain_I):

	now = datetime.now()
	# dd/mm/YY H:M:S
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	print(dt_string)	

	R_polar = 1e6 #Value of the resistance used to induce a current
	R_I = 1e4 #The value of the resistor used to measure the current

	print(f'Stanford Gain V ={stanford_gain_V}')
	print(f'Stanford Gain I ={stanford_gain_I}')
	print(f'Current Max I_max = {voltages[-1]/R_polar}')

	int_time = 1 #Integration time of the dmm's

	station.dmm1.volt()
	station.dmm1.NPLC(int_time)

	station.dmm2.volt()
	station.dmm2.NPLC(int_time)

	print(f'Integration time = {int_time*0.02} s')

	print(f'v_gate from {v_gates[0]}V to {v_gates[-1]}V with {len(v_gates)} points')

	station.yoko.output('off') 
	station.yoko.source_mode("VOLT") 
	station.yoko.output('on')

	station.yoko.voltage.step = 1e-3
	station.yoko.voltage.inter_delay = 1e-3

	meas = Measurement()

	meas.register_parameter(station.mdac_8.ch01.voltage)
	meas.register_parameter(station.yoko.voltage)
	meas.register_parameter(station.dmm2.volt)
	meas.register_custom_parameter("Current", unit="A")
	meas.register_parameter(station.dmm1.volt, setpoints=("Current",station.mdac_8.ch01.voltage))

	with meas.run() as datasaver:

	    ID_exp = datasaver.run_id
	    for i, v_g in enumerate(v_gates):
	    	print(f'v_g = {v_g}V')

	    	station.mdac_8.ch01.ramp(v_g, 0.01)
	    	station.mdac_8.ch02.ramp(v_g, 0.01)
	    	station.mdac_8.ch01.block()
	    	station.mdac_8.ch02.block()
	    	for v in voltages:

	       		station.yoko.voltage(v)

	        	voltage_meas = station.dmm1.volt()/stanford_gain_V
	        	current_meas = station.dmm2.volt()/(R_I*stanford_gain_I)

	        	datasaver.add_result((station.yoko.voltage,v),
	        					(station.mdac_8.ch01.voltage, v_g),
	                            (station.dmm2.volt,station.dmm2.volt()),
	                            ("Current",current_meas),
                                (station.dmm1.volt,voltage_meas))

	station.yoko.voltage(0)
	plot_by_id(ID_exp)