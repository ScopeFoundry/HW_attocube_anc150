from .measurement import Measurement 
import time

class LaserPowerFeedbackControl(Measurement):

    name = "laser_power_feedback_control"
    
    def setup(self):

        self.display_update_period = 0.1 #seconds


        self.update_interval = self.add_logged_quantity("update_interval",  dtype=float, unit="sec", intial=0.1)
        self.p_gain = self.add_logged_quantity("p_gain", dtype=float, units = "steps/V", initial = 100)


        self.max_position = self.add_logged_quantity("max_position", dtype=int, initial=2400)
        self.min_position = self.add_logged_quantity("max_position", dtype=int, initial=0)

        self.set_voltage      = self.add_logged_quantity("set_voltage",    dtype=float, ro=False, vmin=0, vmax=5)
        self.present_voltage  = self.add_logged_quantity("present_voltage", dtype=float, ro=True)

        self.encoder_position = self.add_logged_quantity("encoder_position", dtype=int, ro=True, unit="steps")

    def setup_figure(self):
        pass

    def _run(self):
        # hardware components
        self.power_wheel_hc = self.gui.power_wheel_arduino_hc
        self.power_analog_hc = self.gui.thorlabs_powermeter_analog_readout_hc


        #set up
        self.set_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

        while not self.interrupt_measurement_called:

            # read current state
            self.encoder_position.update_value(self.power_wheel_hc.encoder_pos.read_from_hardware())
            self.present_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

            # compute motion
            v_error = self.set_voltage.val - self.active_voltage.val
            move_delta_steps = int(v_error * self.p_gain.val)

            # Limit motion per step
            if move_delta_steps > 100:
                move_delta_steps = 100
            if move_delta_steps < -100:
                move_delta_steps = -100

            # Check limits on motion
            if self.encoder_position.val + move_delta_steps > self.max_position:
                move_delta_steps = self.max_position - self.encoder_position.val
            if self.encoder_position.val + move_delta_steps < self.min_position:
                move_delta_steps = self.min_position - self.encoder_position.val

            # move
            self.power_wheel_hc.power_wheel.write_steps_and_wait(move_delta_steps)
            # TODO: Check for interrupted measurement during motion

            # read final state
            self.encoder_position.update_value(self.power_wheel_hc.encoder_pos.read_from_hardware())
            self.present_voltage.update_value(self.power_analog_hc.voltage.read_from_hardware())

            time.sleep(self.update_interval.val)


    def update_display(self):
        pass
