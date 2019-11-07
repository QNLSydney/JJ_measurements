def G_up_B(station, field_max, v_polar, amplitude, stanford_gain_V_ac):

    #Before using this code change these values according to your own setup :
    
    R_polar = 1e6 #value of the polarization resistor

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")    # dd/mm/YY H:M:S
    print(dt_string)    #print date and time of the measurement

    #Start the measurement

    meas = Measurement()

    meas.register_parameter(station.lockin_2.amplitude)
    meas.register_parameter(station.lockin_2.sine_outdc)
    meas.register_parameter(station.mag.y_measured)

    meas.register_parameter(station.lockin_1.Y, setpoints=(station.mag.y_measured,))
    meas.register_parameter(station.lockin_2.Y, setpoints=(station.mag.y_measured,))
    meas.register_parameter(station.lockin_1.X, setpoints=(station.mag.y_measured,))
    meas.register_parameter(station.lockin_2.X, setpoints=(station.mag.y_measured,))
    meas.register_custom_parameter("R_ac", unit="Ohm",setpoints=(station.mag.y_measured,))

    #Prepare the live plot
    win = qcm.pyplot.PlotWindow(title="Field Sweep 1D")
    win.resize(600,400)

    num_points = 0
    array_size = 1
    B_array = np.full((1,), np.nan)
    r_array = np.full((1,), np.nan)

    plot1 = win.addPlot(title ="R_ac(B)")
    plotdata = plot1.plot(setpoint_x = B_array)

    plot1.left_axis.label = "Resistance"
    plot1.left_axis.units = "Ohms"
    plot1.bot_axis.label = "B"
    plot1.bot_axis.units = "T"

    #Print the main lockin settings
    print(f'Stanford Gain V_AC ={stanford_gain_V_ac}')
   
    time_constant = station.lockin_2.time_constant()
    print(f'Integration time lockins {time_constant} s')

    print(f'Frequency Lockin : {station.lockin_2.frequency()} Hz')

    print(f'Filter lockin 1 : {station.lockin_1.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 1 : {station.lockin_1.sensitivity()} V')

    print(f'Filter lockin 2 : {station.lockin_2.filter_slope()} dB roll off')
    print(f'Sensitivity lockin 2 : {station.lockin_2.sensitivity()} A')

    #Initialisation of the lockin

    station.lockin_2.amplitude(amplitude)
    print(f'V_ac polarization : {amplitude/1e-3} mV')

    station.lockin_2.sine_outdc(v_polar)
    print(f'V_dc polarization : {v_polar/1e-3} mV')



    with meas.run() as datasaver:

        station.mag.y_target(b)
        station.mag.ramp('simul')

        while abs(station.mag.y_measured()-field_max)>0.001:
        
            time.sleep(5*time_constant)

            b_y = station.mag.y_measured()

            voltage_X_AC = station.lockin_1.X()/stanford_gain_V_ac
            current_X_AC = station.lockin_2.X()

            voltage_Y_AC = station.lockin_1.Y()/stanford_gain_V_ac
            current_Y_AC = station.lockin_2.Y()

            R_ac = voltage_X_AC/current_X_AC

            datasaver.add_result(("R_ac", R_ac),
                                (station.lockin_2.amplitude, amplitude),
                                (station.lockin_2.sine_outdc, v_polar),
                                (station.mag.y_measured, b_y),
                                (station.lockin_2.Y,current_Y_AC),
                                (station.lockin_1.Y,voltage_Y_AC),
                                (station.lockin_2.X,current_X_AC),
                                (station.lockin_1.X,voltage_X_AC))

            B_array[num_points] = b_y
            r_array[num_points] = R_ac
            plotdata.xData = B_array
            plotdata.update(r_array)
            num_points += 1

            if num_points == array_size:
                array_size *= 2
                B_array.resize(array_size)
                B_array[array_size//2:] = np.nan
                r_array.resize(array_size)
                r_array[array_size//2:] = np.nan


        ID_exp = datasaver.run_id

    station.lockin_2.sine_outdc(0)

    win.export('figures/Rac_Field_sweep_1D_ID_exp_'+str(ID_exp)+'.png')

    plot_by_id(ID_exp)
