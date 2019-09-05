# Measure the Resistance R as a function of temperature

stanford_gain = 1

dmm1.NPLC(10)
#dmm2.NPLC(10)

yoko.current.step = 5e-9
yoko.current.inter_delay = 10e-3

meas = Measurement()

meas.register_parameter(yoko.current)
meas.register_custom_parameter("Temperature")
meas.register_custom_parameter("Counter")
meas.register_custom_parameter("Resistance")
meas.register_parameter(dmm1.volt, setpoints=("Temperature",))
#meas.register_parameter(dmm2.volt, setpoints=("Temperature",))

yoko.output('off')
yoko.source_mode("CURR")
yoko.output('on')

j=0

current = 1.0e-6

T = ft()

with meas.run() as datasaver:
    
    while T[1]>3:
        
        T = ft()
        
        yoko.current(current)
        
        time.sleep(1)

        volt_p = dmm1.volt()/stanford_gain
        
        time.sleep(1)
        
        yoko.current(-current)
        
        time.sleep(1)
        
        volt_m = dmm1.volt()/stanford_gain
        
        V_av = (volt_p - volt_m)/2
        
        R_av = V_av/current

        datasaver.add_result((yoko.current,current),
                            ("Temperature",T),
                            ("Counter",j),
                             ("Resistance",R_av),
                            (dmm1.volt,V_av))
        
        print((T[1],R_av))
        time.sleep(300)
        j = j+1
        
yoko.current(0)