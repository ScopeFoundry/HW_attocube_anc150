from ScopeFoundry import HardwareComponent
from Auger.auger_equipment.phi_ion_gun import PhiIonGun
from sympy.functions.special.polynomials import _x
try:
    from Auger.auger_equipment.phi_ion_gun import PhiIonGun
except Exception as err:
    print "Cannot load required modules for PhiIonGun", err

import time


class PhiIonGunHardwareComponent(HardwareComponent):
    
    name = "phi_ion_gun"

    def setup(self):
        """This section is where logged quantities and signals are defined for uses specific to our PHI ion gun."""
        #create logged quantities
        self.configure = self.add_operation("Configure", self.Initial_gun_state)

        self.gun_state = self.add_logged_quantity("gun_state", dtype=str,
                                                        choices = [
                                                                ("Off", 'OFF'),
                                                                ("Blank", 'BLANK'),
                                                                ("Standby", 'STANDBY'),
                                                                ("Active", 'ACTIVE')]
                                                )
        self.gun_state2 = self.add_logged_quantity("gun_state2", dtype=str,
                                                        choices = [
                                                                ("Off", 'OFF'),
                                                                ("Blank", 'BLANK'),
                                                                ("Standby", 'STANDBY'),
                                                                ("Active", 'ACTIVE')]
                                                )


        self.raster_mode = self.add_logged_quantity("raster_mode", dtype=str,
                                                choices = [
                                                        ("Off", 'OFF'),
                                                        ("Internal", 'INTERNAL'),
                                                        ("External", 'EXTERNAL')]
                                                )
        
        self.emission_current_target = self.add_logged_quantity(
                                    name = 'emission_current_target',
                                    initial = 0, dtype=float, fmt="%.3f",
                                    ro=False, unit="mA", vmin=0, vmax=30)
        self.emission_current_readout = self.add_logged_quantity(
                                    name = 'emission_current_readout',
                                    initial = 0, dtype=float, fmt="%.3f",
                                    ro=True, unit="mA", vmin=0, vmax=30)

        self.beam_voltage_target = self.add_logged_quantity(
                                    name='beam_voltage_target',
                                    initial=0, dtype=float, fmt="%.0f",
                                    ro=False, unit="V", vmin=0, vmax=5000)
        self.beam_voltage_target.spinbox_decimals = 0
        self.beam_voltage_readout = self.add_logged_quantity(
                                    name = 'beam_voltage_readout',
                                    initial = 0, dtype=float, fmt="%.0f",
                                    ro=True, unit="V", vmin=0, vmax=5000)
        self.beam_voltage_readout.spinbox_decimals = 0
        
        self.condenser_voltage_target = self.add_logged_quantity(
                                        name = 'condenser_voltage_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=5500)
        self.condenser_voltage_readout = self.add_logged_quantity(
                                        name = 'condenser_voltage_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=5500)
        
        self.condenser_percentage_target = self.add_logged_quantity(
                                        name = 'condenser_percentage_target',
                                        initial=0, dtype=float, fmt="%.1f",
                                        ro=False, unit="%", vmin=0, vmax=110)
        self.condenser_percentage_readout = self.add_logged_quantity(
                                        name = 'condenser_percentage_readout',
                                        initial=0, dtype=float, fmt="%.1f",
                                        ro=True, unit="%", vmin=0, vmax=110)

        self.objective_voltage_target = self.add_logged_quantity(
                                        name = 'objective_voltage_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=5500) 
        self.objective_voltage_readout = self.add_logged_quantity(
                                        name = 'objective_voltage_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=5500)
        
        self.objective_percentage_target = self.add_logged_quantity(
                                        name = 'objective_percentage_target',
                                        initial=0, dtype=float, fmt="%.1f",
                                        ro=False, unit="%", vmin=0, vmax=110) 
        self.objective_percentage_readout = self.add_logged_quantity(
                                        name = 'objective_percentage_readout',
                                        initial=0, dtype=float, fmt="%.1f",
                                        ro=True, unit="%", vmin=0, vmax=110)       

        self.float_target = self.add_logged_quantity(
                                        name = 'float_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=500)
        self.float_readout = self.add_logged_quantity(
                                        name = 'float_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=500)

        self.bend_target = self.add_logged_quantity(
                                        name = 'bend_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=-350, vmax=0) # Check thresholds. Checked.

        self.grid_target = self.add_logged_quantity(
                                        name = 'grid_target',
                                        initial=0, dtype=float, fmt="%.3f", 
                                        ro=False, unit="V", vmin=120, vmax=200)
        
        self.extractor_readout = self.add_logged_quantity(name = 'extractor_pressure',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="mPa", vmin=0, vmax=50)

        self.xsize_target = self.add_logged_quantity(name='xsize_target',
                                        initial = 0, dtype=float, fmt="%.3f",
                                        ro=False, unit="mm", vmin=-10, vmax=10)
        
        self.ysize_target = self.add_logged_quantity(name='ysize_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit='mm', vmin=-10, vmax=10)
        
        self.xoff_target = self.add_logged_quantity(name='xoff_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit='mm', vmin=-10, vmax=10)
        
        self.yoff_target = self.add_logged_quantity(name='yoff_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit='mm', vmin=-10, vmax=10)

        self.dummy_mode = self.add_logged_quantity(name='dummy mode', dtype=bool, initial=False, ro=False)

        self.timer = self.add_logged_quantity(name='timer', dtype=float, fmt="%.2f",
                                        ro=False, unit='s', vmin=0, vmax=3600) 
                                        #set to an hour.. not sure what users want in terms of maximum times.

        # Connect Percent LQ's to voltage (hardware-connected) LQ's
        self.objective_percentage_target.updated_value.connect(self.on_objective_percent_target_updated)
        self.objective_voltage_target.updated_value.connect(self.on_objective_voltage_target_updated)
        self.objective_voltage_readout.updated_value.connect(self.on_objective_voltage_readout_updated)
        self.condenser_voltage_readout.updated_value.connect(self.on_condenser_voltage_readout_updated)
    
        self.condenser_percentage_target.updated_value.connect(self.on_condenser_percent_target_updated)
        self.condenser_voltage_target.updated_value.connect(self.on_condenser_voltage_target_updated)
        
        self.beam_voltage_target.updated_value.connect(self.on_beam_voltage_target_updated)


        self.add_operation('timer start', self.timed_state)
        # operations
        self.add_operation('zero state command', self.zero_state_command)
        self.add_operation('zero state gun on', self.zero_state_command_gunon)

    def on_beam_voltage_target_updated(self):
        """Once the beam voltage is altered by the user, this signal triggers objective and 
        condensor voltage update (as a percentage), and a raster offset and size update."""
        self.on_objective_percent_target_updated()
        self.on_condenser_percent_target_updated()
        self.refresh_xy_offset()
        self.refresh_xy_size()

    def on_objective_percent_target_updated(self):
        """Takes an updated objective lens voltage percentage and updates the logged quantity
        as a voltage."""
        pct = self.objective_percentage_target.val
        beam_v = self.beam_voltage_target.val
        self.objective_voltage_target.update_value(0.01*pct*beam_v)
    
    def on_objective_voltage_readout_updated(self):
        """Updates the read-only logged quantity with the percentage value of this quantity:
        Objective voltage as a fraction of beam voltage.

        This is the case because lens system voltages are calculated as a fraction of ion beam 
        voltage, which is in turn, dependent on float voltage according to manufacturer 
        specifications.
        """
        obj_v = self.objective_voltage_readout.val
        beam_v = self.beam_voltage_readout.val
        if beam_v:
            self.objective_percentage_readout.update_value(100*obj_v/beam_v)
        
    def on_objective_voltage_target_updated(self):
        """When the user updates the objective voltage value, this signal is issued, 
        and the voltage is converted to a percentage and displayed as a logged quantity"""
        beam_v = self.beam_voltage_target.val
        obj_v = self.objective_voltage_target.val
        if beam_v == 0:
            return
        else:
            pct = 100*obj_v/beam_v
            self.objective_percentage_target.update_value(pct)
            
    def on_condenser_percent_target_updated(self):
        """When the user updates the condensor percentage value, this signal is issued, 
        and the voltage is converted from the input percentage to a voltage."""
        pct = self.condenser_percentage_target.val
        beam_v = self.beam_voltage_target.val
        self.condenser_voltage_target.update_value(0.01*pct*beam_v)
    
    def on_condenser_voltage_readout_updated(self):
        """When the user updates the condensor voltage value, this signal is issued, 
        and the voltage is converted to a percentage and displayed as a logged quantity"""
        cond_v = self.condenser_voltage_readout.val
        beam_v = self.beam_voltage_readout.val
        if beam_v:
            self.condenser_percentage_readout.update_value(100*cond_v/beam_v)
        
    def on_condenser_voltage_target_updated(self):
        """When the user updates the condensor voltage, this signal is issued,
        and the condensor voltage as a fraction of beam voltage is converted to a percentage."""
        beam_v = self.beam_voltage_target.val
        cond_v = self.condenser_voltage_target.val
        if beam_v == 0:
            return
        else:
            pct = 100*cond_v/beam_v
            self.condenser_percentage_target.update_value(pct)
    
    def refresh_xy_offset(self):
        """This function is triggered by a signal 'on_beam_voltage_target_updated.'
        The function simply refreshes the raster offset values to ensure they're 
        properly registered with their respective logged quantities.
        """
        beam_v = self.beam_voltage_target.val
        _xoffset = self.xoff_target.val
        _yoffset = self.yoff_target.val
        if beam_v:
            self.xoff_target.update_value(_xoffset)
            self.yoff_target.update_value(_yoffset)
            
    def refresh_xy_size(self):
        """This function is triggered by a signal 'on_beam_voltage_target_updated.'
        The function simply refreshes the raster size values to ensure they're 
        properly registered with their respective logged quantities.
        """
        beam_v = self.beam_voltage_target.val
        _xsize = self.xsize_target.val
        _ysize = self.ysize_target.val
        if beam_v:
            self.xsize_target.update_value(_xsize)
            self.ysize_target.update_value(_ysize)
        

    ## To do:        
    ## Update signals such that percentages can be updated in the phi_ion_gun gui:
    
    
    
            
    def connect(self):
        """This function links logged quantities at hardware control
        level to their respective functions at equipment level (where basic commands are defined)"""
        if self.debug_mode.val: print "Connecting to Phi Ion Gun"
        # Open connection to Hardware

        if not self.dummy_mode.val:
            self.phiiongun = PhiIonGun(port="COM7", address=3, debug=self.debug_mode.val)
        else:
            if self.debug_mode.val: print "Connecting to Phi Ion Gun (Dummy Mode)"

        #Connect logged quantities:
        self.emission_current_readout.hardware_read_func = \
                self.phiiongun.read_emission_current
        self.emission_current_target.hardware_set_func = \
                self.phiiongun.write_emission_current

        self.beam_voltage_readout.hardware_read_func = \
                self.phiiongun.read_beam_v
        self.beam_voltage_target.hardware_set_func = \
                self.phiiongun.write_beam_v

        self.condenser_voltage_readout.hardware_read_func = \
                self.phiiongun.read_condenser_v
        self.condenser_voltage_target.hardware_set_func = \
                self.phiiongun.write_condenser_v


        self.objective_voltage_readout.hardware_read_func = \
                self.phiiongun.read_objective_v
        self.objective_voltage_target.hardware_set_func = \
                self.phiiongun.write_objective_v

        self.float_readout.hardware_read_func = \
                self.phiiongun.read_float
        self.float_target.hardware_set_func = \
                self.phiiongun.write_float_v

        self.bend_target.hardware_set_func = \
                self.phiiongun.write_bend_v
                
        self.grid_target.hardware_set_func = \
                self.phiiongun.write_grid_v
                
        self.extractor_readout.hardware_read_func = \
                self.phiiongun.read_extractor_p

        
        # Note to self: these assignments are only part of the link between equipment level
        # commands and the GUI. These are hardware class associations.
        # Bidirectional gui link commands are found in measurement class. 

        self.gun_state.hardware_set_func = \
                self.Set_gun_state
        #Runs single command for 4 possible states using stored values in hardware class.

        self.gun_state2.hardware_set_func = \
                self.Set_gun_state

        # start button?

        self.raster_mode.hardware_set_func = \
                self.Set_raster_mode
                
        self.xsize_target.hardware_set_func = \
                self.phiiongun.xsize

        self.ysize_target.hardware_set_func = \
                self.phiiongun.ysize
        
        self.xoff_target.hardware_set_func = \
                self.phiiongun.xoff
        
        self.yoff_target.hardware_set_func = \
                self.phiiongun.yoff
        
    
    def timed_state(self):
        self.old_state = self.gun_state.val
        self.new_state = self.gun_state2.val
        self.time = self.timer.val
        t0 = time.time()
        while time.time() < t0 + self.time:
            self.gun_state.update_value(self.new_state)
            #I'm very much hesitant to implement this update command:
            '''choices = [("Off", 'OFF')]''' 
            #(Given that this is a tuple, and not the usual integer or float datatype)
        else:
            self.gun_state.update_value(self.old_state)
            #See above comments. 








    
    def zero_state_command(self):
        """Sets ion gun Power Supply Unit voltages to zero across the board. 
        This function simply issues the Set_gun_state function with every value set to zero."""
        self.phiiongun.State_Data_Packet()
    
    def Initial_gun_state(self):
        """Sets the ion gun PSU voltages to arbitrarily defined voltages as a modifiable starting point for the user.
        Float = 500 V    Grid = 150 V     Cond = 500 V      Obj = 350 V       Bend = -7 V   Emission = 25 mA"""
        self.phiiongun.State_Data_Packet(beamv=float(500), gridv=float(150), condv=float(500), objv=float(350), bendv=float(-7), emiv=float(25), State='STANDBY')
        
    def Set_gun_state(self, state):
        """The State_Data_Packet function is a single function which issues a series of voltage and current values at once.
        """
        self.phiiongun.State_Data_Packet(beamv=self.beam_voltage_target.val, gridv=self.grid_target.val, condv=self.condenser_voltage_target.val, 
                                                objv=self.objective_voltage_target.val, bendv=self.bend_target.val, emiv=self.emission_current_target.val, State=state)
        #Reads logged quantity values stored in hardware class
        
    def Set_raster_mode(self, state):
        """This function sets ion gun raster mode to any of the following choices:
        Internal, External, or Off."""
        self.phiiongun.Set_Raster_Mode(State=state)

    def disconnect(self):
        """This function properly closes out our program and removes leftover objects."""
        #disconnect hardware
        self.phiiongun.close() #changed
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.phiiongun #changed
