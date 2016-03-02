from ScopeFoundry import HardwareComponent
from Auger.equipment.phi_ion_gun import PhiIonGun
try:
    from Auger.equipment.phi_ion_gun import PhiIonGun
except Exception as err:
    print "Cannot load required modules for PhiIonGun", err



class PhiIonGunHardwareComponent(HardwareComponent):
    
    name = "phi_ion_gun"

    def setup(self):

        #create logged quantities
        self.configure = self.add_operation("Configure", self.Initial_gun_state)

        self.gun_state = self.add_logged_quantity("gun_state", dtype=str,
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


        # Connect Percent LQ's to voltage (hardware-connected) LQ's
        self.objective_percentage_target.updated_value.connect(self.on_objective_percent_target_updated)
        self.objective_voltage_target.updated_value.connect(self.on_objective_voltage_target_updated)
        self.objective_voltage_readout.updated_value.connect(self.on_objective_voltage_readout_updated)
        self.condenser_voltage_readout.updated_value.connect(self.on_condenser_voltage_readout_updated)
    
        self.condenser_percentage_target.updated_value.connect(self.on_condenser_percent_target_updated)
        self.condenser_voltage_target.updated_value.connect(self.on_condenser_voltage_target_updated)
        
        self.beam_voltage_target.updated_value.connect(self.on_beam_voltage_target_updated)


        # operations
        self.add_operation('zero state command', self.zero_state_command)
        self.add_operation('zero state gun on', self.zero_state_command_gunon)

    def on_beam_voltage_target_updated(self):
        self.on_objective_percent_target_updated()
        self.on_condenser_percent_target_updated()

    def on_objective_percent_target_updated(self):
        pct = self.objective_percentage_target.val
        beam_v = self.beam_voltage_target.val
        self.objective_voltage_target.update_value(0.01*pct*beam_v)
    
    def on_objective_voltage_readout_updated(self):
        obj_v = self.objective_voltage_readout.val
        beam_v = self.beam_voltage_readout.val
        if beam_v:
            self.objective_percentage_readout.update_value(100*obj_v/beam_v)
        
    def on_objective_voltage_target_updated(self):
        beam_v = self.beam_voltage_target.val
        obj_v = self.objective_voltage_target.val
        if beam_v == 0:
            return
        else:
            pct = 100*obj_v/beam_v
            self.objective_percentage_target.update_value(pct)
            
    def on_condenser_percent_target_updated(self):
        pct = self.condenser_percentage_target.val
        beam_v = self.beam_voltage_target.val
        self.condenser_voltage_target.update_value(0.01*pct*beam_v)
    
    def on_condenser_voltage_readout_updated(self):
        cond_v = self.condenser_voltage_readout.val
        beam_v = self.beam_voltage_readout.val
        if beam_v:
            self.condenser_percentage_readout.update_value(100*cond_v/beam_v)
        
    def on_condenser_voltage_target_updated(self):
        beam_v = self.beam_voltage_target.val
        obj_v = self.condenser_voltage_target.val
        if beam_v == 0:
            return
        else:
            pct = 100*obj_v/beam_v
            self.condenser_percentage_target.update_value(pct)
            
    ## To do:        
    ## Update signals such that percentages can be updated in the phi_ion_gun gui:
    
    
    
            
    def connect(self):
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
        
        
    
    def zero_state_command(self):
        self.phiiongun.State_Data_Packet()

    def zero_state_command_gunon(self):
        self.phiiongun.State_Data_Packet(Gun_Firing_On=True)
    
    def Initial_gun_state(self):
        self.phiiongun.State_Data_Packet(beamv=float(500), gridv=float(150), condv=float(500), objv=float(350), bendv=float(-7), emiv=float(25), State='STANDBY')
        
    def Set_gun_state(self, state):
        self.phiiongun.State_Data_Packet(beamv=self.beam_voltage_target.val, gridv=self.grid_target.val, condv=self.condenser_voltage_target.val, 
                                                objv=self.objective_voltage_target.val, bendv=self.bend_target.val, emiv=self.emission_current_target.val, State=state)
        #Reads logged quantity values stored in hardware class
        
    def Set_raster_mode(self, state):
        self.phiiongun.Set_Raster_Mode(State=state)

    def disconnect(self):
        #disconnect hardware
        self.phiiongun.close() #changed
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.phiiongun #changed
