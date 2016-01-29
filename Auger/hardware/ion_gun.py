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

        self.beam_energy_target = self.add_logged_quantity(
                                    name='beam_energy_target',
                                    initial=0, dtype=float, fmt="%.3f",
                                    ro=False, unit="V", vmin=0, vmax=5000)
        self.beam_energy_readout = self.add_logged_quantity(
                                    name = 'beam_energy_readout',
                                    initial = 0, dtype=float, fmt="%.3f",
                                    ro=True, unit="V", vmin=0, vmax=5000)

        #self.beam_energy_target = self.add_logged_quantity(
        #                            name='beam_energy_target'
        #                            initial=0, dtype=float, fmt="%.3f",
        #                            ro=False, unit="V", vmin=0, vmax=5000) 
        # Find out more about this function before use

        self.condenser_target = self.add_logged_quantity(
                                        name = 'condenser_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=5500)
        self.condenser_readout = self.add_logged_quantity(
                                        name = 'condenser_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=5500)

        self.objective_target = self.add_logged_quantity(
                                        name = 'objective_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=5500) 
        self.objective_readout = self.add_logged_quantity(
                                        name = 'objective_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=5500) 

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


        # operations
        self.add_operation('zero state command', self.zero_state_command)
        self.add_operation('zero state gun on', self.zero_state_command_gunon)


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

        self.beam_energy_readout.hardware_read_func = \
                self.phiiongun.read_energy
        self.beam_energy_target.hardware_set_func = \
                self.phiiongun.write_energy

        #self.beam_energy_target.hardware_set_func = \
        #        self.phiiongun.write_beam_v
        # See corresponding logged quantity above.

        self.condenser_readout.hardware_read_func = \
                self.phiiongun.read_condenser_v
        self.condenser_target.hardware_set_func = \
                self.phiiongun.write_condenser_v

        self.objective_readout.hardware_read_func = \
                self.phiiongun.read_objective_v
        self.objective_target.hardware_set_func = \
                self.phiiongun.write_objective_v

        self.float_readout.hardware_read_func = \
                self.phiiongun.read_float
        self.float_target.hardware_set_func = \
                self.phiiongun.write_float_v

        self.bend_target.hardware_set_func = \
                self.phiiongun.write_bend_v
                
        self.grid_target.hardware_set_func = \
                self.phiiongun.write_grid_v
                
        self.extractor_readout.hardware_set_func = \
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
        self.phiiongun.State_Data_Packet(Gun_Firing_On=False)

    def zero_state_command_gunon(self):
        self.phiiongun.State_Data_Packet(Gun_Firing_On=True)
        
    def Set_gun_state(self, state):
        self.phiiongun.State_Data_Packet(beamv=self.beam_energy_target.val, gridv=self.grid_target.val, condv=self.condenser_target.val, 
                                                objv=self.objective_target.val, bendv=self.bend_target.val, emiv=self.emission_current_target.val, State=state)
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
