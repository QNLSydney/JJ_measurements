# IV Ibias
import numpy as np

def IV_up(station, meas):

	stanford_gain_1 = 1e3
	stanford_gain_2 = 1e3

	station.dmm1.volt()
	station.dmm1.NPLC(1)

	station.dmm2.volt()
	station.dmm2.NPLC(1)

	station.yoko.output('off')
	station.yoko.source_mode("VOLT")
	station.yoko.output('on')

	station.yoko.voltage.step = 5e-3
	station.yoko.voltage.inter_delay = 10e-3

	meas.register_parameter(station.yoko.voltage)
	meas.register_parameter(station.dmm2.volt)
	meas.register_custom_parameter("Current")
	meas.register_parameter(station.dmm1.volt, setpoints=("Current",))


	voltages =np.linspace(-50e-3,50e-3,101)

	with meas.run() as datasaver:
	    for v in voltages:
	        station.yoko.voltage(v)

	        
	        voltage_meas = station.dmm1.volt()/stanford_gain_1
	        current_meas = station.dmm2.volt()/(1e4*stanford_gain_2)

	        datasaver.add_result((station.yoko.voltage,v),
	                            (station.dmm2.volt,station.dmm2.volt()),
	                            ("Current",current_meas),
	                            (station.dmm1.volt,voltage_meas))

	station.yoko.voltage(0)