#from PySide import QtGui
import sys
from ScopeFoundry import BaseMicroscopeApp
#import spacenavigator
from hardware.connexion_hc import Connexion_HC
from measurement.connexion_mc import Connexion_MC

class ConnexionApp(BaseMicroscopeApp):
	
	def setup(self):
		self.connexion_hc = self.add_hardware_component(Connexion_HC(self))

		self.connexion_mc = self.add_measurement_component(Connexion_MC(self))
		self.ui.show()
		self.ui.activateWindow()

		
if __name__ == '__main__':
	
	app = ConnexionApp(sys.argv)
	
	sys.exit(app.exec_())
	
