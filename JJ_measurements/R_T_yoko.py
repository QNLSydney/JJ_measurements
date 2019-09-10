# Measure the Resistance R as a function of temperature
import time 

def RT_yoko(station, meas, ft):
    stanford_gain_1 = 1e2
    stanford_gain_2 = 1e3

    station.dmm1.NPLC(10)
    station.dmm2.NPLC(10)

    station.yoko.output('off')
    station.yoko.source_mode("VOLT")
    station.yoko.output('on')

    station.yoko.voltage.step = 10e-3
    station.yoko.voltage.inter_delay = 0.0001

    meas.register_parameter(station.yoko.voltage)
    meas.register_custom_parameter("Temperature", unit = "K")
    meas.register_custom_parameter("Counter")
    meas.register_custom_parameter("Current", unit = "A")
    meas.register_parameter(station.dmm1.volt)
    meas.register_parameter(station.dmm2.volt)
    meas.register_custom_parameter("Resistance", unit = "Ohms", setpoints=("Temperature",))
    
    j=0

    voltage = 500.0e-3

    T = ft.MC_temp()

    with meas.run() as datasaver:
        
        while T < 1:


            if T<90:
                T = ft.MC_temp()
            else:
                T = ft.Four_K_temp()    
                      
            
            station.yoko.voltage(voltage)
            
            time.sleep(1)

            volt_p = station.dmm1.volt()/stanford_gain_1
            curr_p = station.dmm2.volt()/(1e4*stanford_gain_2) #10kOhm resistor for current meas.
            
            time.sleep(1)
            
            station.yoko.voltage(-voltage)
            
            time.sleep(1)
            
            volt_m = station.dmm1.volt()/stanford_gain_1
            curr_m = station.dmm2.volt()/(1e4*stanford_gain_2)
            
            V_av = (volt_p - volt_m)/2
            I_av = (curr_p - curr_m)/2
            R_av = V_av/I_av

            datasaver.add_result((station.yoko.voltage, voltage),
                                ("Temperature", T),
                                ("Counter", j),
                                 ("Resistance", R_av),
                                (station.dmm1.volt,V_av),
                                ("Current", I_av))
            
            print((T,R_av))
            time.sleep(150)
            j = j+1
            
    station.yoko.voltage(0)