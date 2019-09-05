def init():

	import time
	import numpy as np
	import scipy
	import matplotlib.pyplot as plt

	import MDAC

	import qcodes as qc
	from qcodes import ChannelList, Parameter
	from qcodes.dataset.measurements import Measurement
	from qcodes.dataset.plotting import plot_by_id
	from qcodes.dataset.data_set import load_by_id, load_by_counter
	from qcodes.dataset.experiment_container import new_experiment, load_experiment_by_name

	from qdev_wrappers.station_configurator import StationConfigurator

	import qcodes_measurements as qcm
	from qcodes_measurements.plot.plot_tools import *

	# Log all output
	from IPython import get_ipython
	ip = get_ipython()
	ip.magic("logstop")
	ip.magic("logstart -o -t iPython_Logs\\console_log.py rotate")

	# Close any instruments that may already be open
	instruments = list(qc.Instrument._all_instruments.keys())
	for instrument in instruments:
	    instr = qc.Instrument._all_instruments.pop(instrument)
	    instr = instr()
	    instr.close()
	del instruments

	exp_name = 'JJ_DC_meas'
	sample_name = 'Anod_JJ_B'

	try:
	    exp = load_experiment_by_name(exp_name, sample=sample_name)
	    print('Experiment loaded. Last ID no:', exp.last_counter)
	except ValueError:
	    exp = new_experiment(exp_name, sample_name)
	    print('Starting new experiment.')

	scfg = StationConfigurator()

	#lockin_1 = scfg.load_instrument('sr860_1')
	#lockin_2 = scfg.load_instrument('sr860_2')
	yoko = scfg.load_instrument('yoko')
	#mag = scfg.load_instrument('Oxford')
	dmm1 = scfg.load_instrument('agilent_1')
	dmm2 = scfg.load_instrument('agilent_2')
	#mdac = MDAC.MDAC('mdac_8', 'ASRL9::INSTR')