from . import HardwareComponent
try:
    from equipment.phi_ion_gun import PhiIonGun
except Exception as err:
    print "Cannot load required modules for PhiIonGun", err

import time

class PhiIonGunHardwareComponent(HardwareComponent):
    
    name = "phi_ion_gun"

    def setup(self):

        #create logged quantities
        self.emission_current_target = self.add_logged_quantity(
                                    name = 'emission_current_target',
                                    initial = 0, dtype=float, fmt="%.3f",
                                    ro=False, unit="mA", vmin=0, vmax=30)
        self.emission_current_readout = self.add_logged_quantity(
                                    name = 'emission_current_readout',
                                    initial = 0, dtype=float, fmt="%.3f",
                                    ro=True, unit="mA", vmin=0, vmax=30)

        self.energy_target = self.add_logged_quantity(
                                    name='energy_target',
                                    initial=0, dtype=float, fmt="%.3f",
                                    ro=False, unit="V", vmin=0, vmax=5000)
        self.energy_readout = self.add_logged_quantity(
                                    name = 'energy_readout',
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
                                        ro=False, unit="V", vmin=0, vmax=1400) #Check thresholds
        self.condenser_readout = self.add_logged_quantity(
                                        name = 'condenser_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=1400) #Check thresholds

        self.objective_target = self.add_logged_quantity(
                                        name = 'objective_target',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=False, unit="V", vmin=0, vmax=1400) #Check thresholds
        self.objective_readout = self.add_logged_quantity(
                                        name = 'objective_readout',
                                        initial=0, dtype=float, fmt="%.3f",
                                        ro=True, unit="V", vmin=0, vmax=1400) #Check thresholds

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
                                        ro=False, unit="V", vmin=-100, vmax=0) # Check thresholds

        self.grid_target = self.add_logged_quantity(
                                        name = 'grid_target',
                                        initial=0, dtype=float, fmt="%.3f", 
                                        ro=False, unit="V", vmin=120, vmax=200)
        
        

        self.dummy_mode = self.add_logged_quantity(name='dummy mode', dtype=bool, initial=False, ro=False)


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

        self.energy_readout.hardware_read_func = \
                self.phiiongun.read_energy
        self.energy_target.hardware_set_func = \
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

        
        # Note to self: these assignments are only part of the link between equipment level
        # commands and the GUI. These are hardware class associations.
        # Bidirectional gui link commands are found in measurement class. 


        


    def disconnect(self):
        #disconnect hardware
        self.phiiongun.close() #changed
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.phiiongun #changed
