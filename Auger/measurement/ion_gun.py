from ScopeFoundry import Measurement
import time

class IonGunStatus(Measurement):

	name = "ion_gun_status"

	ui_filename = "../Auger/measurement/ion_gun.ui"

	def setup(self):
		self.update_period = 0.05 #seconds
		self.gui # What is this, can I eat it?
		
		
		# Or: self.phi_ion_gun = self.gui.hardware_components['phi_ion_gun']
		self.phi_ion_gun = self.gui.phi_ion_gun
		
		#connect (Logged quantities?) to gui:

		self.phi_ion_gun.emission_current_target.connect_bidir_to_widget(
			self.ui.emission_current_target_doubleSpinBox)
		self.phi_ion_gun.emission_current_readout.connect_bidir_to_widget(
			self.ui.emission_current_readout_doubleSpinBox)

		self.phi_ion_gun.beam_voltage_target.connect_bidir_to_widget(
			self.ui.beam_voltage_target_doubleSpinBox)
		self.phi_ion_gun.beam_voltage_readout.connect_bidir_to_widget(
			self.ui.beam_voltage_readout_doubleSpinBox)
		
		self.phi_ion_gun.grid_target.connect_bidir_to_widget(
			self.ui.grid_target_doubleSpinBox)
		
		self.phi_ion_gun.condenser_percentage_target.connect_bidir_to_widget(
			self.ui.condenser_target_doubleSpinBox)
		self.phi_ion_gun.condenser_percentage_readout.connect_bidir_to_widget(
			self.ui.condenser_readout_doubleSpinBox)
		
		self.phi_ion_gun.objective_percentage_target.connect_bidir_to_widget(
			self.ui.objective_target_doubleSpinBox)
		self.phi_ion_gun.objective_percentage_readout.connect_bidir_to_widget(
			self.ui.objective_readout_doubleSpinBox)
		
		self.phi_ion_gun.float_target.connect_bidir_to_widget(
			self.ui.float_target_doubleSpinBox)
		self.phi_ion_gun.float_readout.connect_bidir_to_widget(
			self.ui.float_readout_doubleSpinBox)
		
		#self.phi_ion_gun.bend_target.connect_bidir_to_widget(
		#	self.ui.bend_target_doubleSpinBox)
		# Couldn't find readout command during logging
		
		self.phi_ion_gun.extractor_readout.connect_bidir_to_widget(
			self.ui.Extractor_readout_doubleSpinBox)
		
		self.phi_ion_gun.gun_state.connect_bidir_to_widget(
			self.ui.Gun_mode_comboBox)





		
		self.phi_ion_gun.raster_mode.connect_bidir_to_widget(
			self.ui.Raster_comboBox)
		
		self.phi_ion_gun.xsize_target.connect_bidir_to_widget(
			self.ui.X_raster_spinbox)
		
		self.phi_ion_gun.ysize_target.connect_bidir_to_widget(
			self.ui.Y_raster_spinbox)
		
		self.phi_ion_gun.xoff_target.connect_bidir_to_widget(
			self.ui.X_offset_spinbox)
		
		self.phi_ion_gun.yoff_target.connect_bidir_to_widget(
			self.ui.Y_offset_spinbox)

	def _run(self):
		t = 0.1
		while not self.interrupt_measurement_called:
			#print "phi_ion_gun_status loop"
			self.phi_ion_gun.beam_voltage_readout.read_from_hardware()
			time.sleep(t)
			self.phi_ion_gun.emission_current_readout.read_from_hardware()
			time.sleep(t)
			self.phi_ion_gun.condenser_voltage_readout.read_from_hardware()
			time.sleep(t)
			self.phi_ion_gun.objective_voltage_readout.read_from_hardware()
			time.sleep(t)
			self.phi_ion_gun.float_readout.read_from_hardware()
			time.sleep(t)
			self.phi_ion_gun.extractor_readout.read_from_hardware()
			time.sleep(t)
			
			#self.logged_quantity.LoggedQuantity.read_from_hardware()