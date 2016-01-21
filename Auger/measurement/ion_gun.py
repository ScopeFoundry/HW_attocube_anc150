from measurement import Measurement
import time

class IonGunStatus(Measurement):

	name = "ion_gun_status"

	ui_filename = "measurement_components/ion_gun.ui"

	def setup(self):
		self.update_period = 0.1 #seconds
		self.gui

		# Or: self.phi_ion_gun = self.gui.hardware_components['phi_ion_gun']
		self.phi_ion_gun = self.gui.phi_ion_gun
		
		#connect to gui:

		self.phi_ion_gun.emission_current_target.connect_bidir_to_widget(
			self.ui.emission_current_target_doubleSpinBox)
		self.phi_ion_gun.emission_current_readout.connect_bidir_to_widget(
			self.ui.emission_current_readout_doubleSpinBox)

		self.phi_ion_gun.energy_target.connect_bidir_to_widget(
			self.ui.energy_target_doubleSpinBox)
		self.phi_ion_gun.energy_readout.connect_bidir_to_widget(
			self.ui.energy_readout_doubleSpinBox)
		
		self.phi_ion_gun.grid_target.connect_bidir_to_widget(
			self.ui.grid_target_doubleSpinBox)
		
		self.phi_ion_gun.condenser_target.connect_bidir_to_widget(
			self.ui.condenser_target_doubleSpinBox)
		self.phi_ion_gun.condenser_readout.connect_bidir_to_widget(
			self.ui.condenser_readout_doubleSpinBox)
		
		self.phi_ion_gun.objective_target.connect_bidir_to_widget(
			self.ui.objective_target_doubleSpinBox)
		self.phi_ion_gun.objective_readout.connect_bidir_to_widget(
			self.ui.objective_readout_doubleSpinBox)
		
		self.phi_ion_gun.float_target.connect_bidir_to_widget(
			self.ui.float_target_doubleSpinBox)
		self.phi_ion_gun.float_readout.connect_bidir_to_widget(
			self.ui.float_readout_doubleSpinBox)
		
		self.phi_ion_gun.bend_target.connect_bidir_to_widget(
			self.ui.bend_readout_doubleSpinBox)
		# Couldn't find readout command during logging
		
		
		

