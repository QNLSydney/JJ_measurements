# IV Ibias

stanford_gain_1 = 1
stanford_gain_2 = 1e3

dmm1.volt()
dmm1.NPLC(1)

dmm2.volt()
dmm2.NPLC(1)

yoko.output('off')
yoko.source_mode("VOLT")
yoko.output('on')


yoko.voltage.step = 5e-3
yoko.voltage.inter_delay = 10e-3

meas = Measurement()

meas.register_parameter(yoko.voltage)
meas.register_parameter(dmm2.volt)
meas.register_parameter(dmm1.volt, setpoints=(dmm2.volt,))


voltages =np.linspace(-50e-3,50e-3,101)

with meas.run() as datasaver:
    for v in voltages:
        yoko.voltage(v)

        
        voltage_meas = dmm1.volt()/stanford_gain_1
        current_meas = dmm2.volt()/(1e4*stanford_gain_2)

        datasaver.add_result((yoko.voltage,v),
                            (dmm2.volt,current_meas),
                            (dmm1.volt,voltage_meas))

yoko.voltage(0)