from .measurement import Measurement 
import time

class LaserPowerFeedbackControl(Measurement):

    name = "laser_power_feedback_control"
    
    def setup(self):

        self.display_update_period = 0.1 #seconds


        self.update_interval = self.add_logged_quantity("update_interval",  dtype=float, unit="sec", initial=0.1)
        self.p_gain = self.add_logged_quantity("p_gain", dtype=float, unit = "steps/V", initial = 1000)


        self.max_position = self.add_logged_quantity("max_position", dtype=int, unit="step", initial=2400)
        self.min_position = self.add_logged_quantity("min_position", dtype=int, unit="step", initial=0)

        self.set_voltage      = self.add_logged_quantity("set_voltage",    unit="V", dtype=float, ro=False, vmin=0, vmax=5)
        self.present_voltage  = self.add_logged_quantity("present_voltage", unit="V", dtype=float, ro=True)

        self.encoder_position = self.add_logged_quantity("encoder_position", dtype=int, ro=True, unit="steps")

    def setup_figure(self):
        pass

    def _run(self):
        # hardware components
        self.power_wheel_hc = self.gui.power_wheel_arduino_hc
        self.power_wheel    = self.gui.power_wheel_arduino_hc.power_wheel

        self.power_analog_hc = self.gui.thorlabs_powermeter_analog_readout_hc


        #set up
        self.set_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

        self.power_wheel.read_status()
        
        while not self.interrupt_measurement_called:

            # read current state
            self.encoder_position.update_value(self.power_wheel_hc.encoder_pos.read_from_hardware())
            self.present_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

            # compute motion
            v_error = self.set_voltage.val - self.present_voltage.val
            move_delta_steps = (v_error * self.p_gain.val)

            # Limit motion per step
            if move_delta_steps > 100:
                move_delta_steps = 100
            if move_delta_steps < -100:
                move_delta_steps = -100


            # Check limits on motion
            final_pos = self.encoder_position.val + move_delta_steps
            
            if final_pos > self.max_position.val:
                #print "too big"
                move_delta_steps = self.max_position.val - self.encoder_position.val
            if final_pos < self.min_position.val:
                #print "too small", self.min_position.val, self.encoder_position.val
                move_delta_steps = self.min_position.val - self.encoder_position.val

            # move
            move_delta_steps = int(move_delta_steps)
            self.power_wheel.write_steps(move_delta_steps)
            sleep_time = abs(move_delta_steps*1.0/self.power_wheel_hc.speed.val)
            time.sleep(sleep_time)
            self.power_wheel.read_status()
            while(self.power_wheel.is_moving_to):
                time.sleep(0.050)
                s = self.power_wheel.read_status()
                print s
                if self.interrupt_measurement_called:
                    self.power_wheel.write_brake()
                    break
            
            # old move version
            #t0 = time.time()
            #self.power_wheel.write_steps_and_wait(move_delta_steps)
            #print "moved {} steps in {} secs".format(move_delta_steps, time.time()-t0)

            #print "laser feedback:", v_error, move_delta_steps
            #if abs(move_delta_steps) > 0:
            #    print "moved", move_delta_steps

            # read final state
            self.encoder_position.update_value(self.power_wheel_hc.encoder_pos.read_from_hardware())
            self.present_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

            time.sleep(self.update_interval.val)


    def update_display(self):
        pass
