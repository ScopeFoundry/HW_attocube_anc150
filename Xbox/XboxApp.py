#from PySide import QtGui
import sys
from ScopeFoundry import BaseMicroscopeApp
from measurement.xbcontrol_mc import XboxControl_MC
from hardware.xbcontrol_hc import XboxControl_HC

class XboxApp(BaseMicroscopeApp):
	"""This class loads ScopeFoundry modules into the ScopeFoundry app related to
	Xbox hardware and measurement modules."""
	def setup(self):
		"""Setup function attempts to load desired modules into ScopeFoundry app
		and activates its respective graphical user interface."""
		self.xbcontrol_hc = self.add_hardware_component(XboxControl_HC(self))
		self.xbcontrol_mc = self.add_measurement_component(XboxControl_MC(self))
		self.ui.show()
		self.ui.activateWindow()

		
if __name__ == '__main__':
	
	app = XboxApp(sys.argv)
	
	sys.exit(app.exec_())
	
