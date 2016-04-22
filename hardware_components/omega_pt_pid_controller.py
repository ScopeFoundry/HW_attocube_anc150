from __init__ import HardwareComponent
from colorama.initialise import init

try:
    from equipment.omega_pt_pid_controller import OmegaPtPIDController
except Exception as err:
    print "Cannot load required modules for OmegaPtPIDControllerHardware:", err

class OmegaPtPIDControllerHardware(HardwareComponent):

    name = 'omega_pt_pid_controller' 

    def setup(self):
        
        # Create logged quantities
        self.setpoint1 = self.add_logged_quantity('setpoint1', dtype=float, ro=False, unit='C', si=False, vmin=-300, vmax=200 )
        self.setpoint2 = self.add_logged_quantity('setpoint2', dtype=float, ro=False, unit='C', si=False, vmin=-300, vmax=200 )
        self.temp = self.add_logged_quantity('temp', dtype=float, ro=True, unit='C', si=False)
        self.pid_output = self.add_logged_quantity('pid_output', dtype=float, ro=True, unit='%', si=False)
        
        self.run_mode = self.add_logged_quantity('run_mode', dtype=str, ro=True)
        
        self.pid_P = self.add_logged_quantity('pid_P', dtype=float, ro=False, si=False)
        self.pid_I = self.add_logged_quantity('pid_I', dtype=float, ro=False, si=False)
        self.pid_D = self.add_logged_quantity('pid_D', dtype=float, ro=False, si=False)
        
        self.port = self.add_logged_quantity('port', dtype=str, initial='COM8')
        self.address = self.add_logged_quantity('address', dtype=int, initial=1)

        # Operations
        self.add_operation('run', self.run_mode_run)
        self.add_operation('stop', self.run_mode_stop)


        # connect to gui
            # none for now

    def connect(self):
        if self.debug_mode.val: print "connecting to", self.name, self.port.val
        
        # Open connection to hardware
        self.pid = OmegaPtPIDController(self.port.val, self.address.val)            
        
        self.pid.debug = True#self.debug_mode.val
        
        # connect logged quantities
        self.setpoint1.hardware_read_func = self.pid.read_setpoint1
        self.setpoint1.hardware_set_func = self.pid.write_setpoint1
        self.setpoint2.hardware_read_func = self.pid.read_setpoint2
        self.setpoint2.hardware_set_func = self.pid.write_setpoint2
        
        self.temp.hardware_read_func = self.pid.read_temp
        
        self.pid_output.hardware_read_func = self.pid.read_pid_output
        
        self.run_mode.hardware_read_func = self.pid.read_run_mode
        
        self.pid_P.hardware_read_func = self.pid.read_pid_P
        self.pid_P.hardware_set_func = self.pid.write_pid_P
        
        self.pid_I.hardware_read_func = self.pid.read_pid_I
        self.pid_I.hardware_set_func = self.pid.write_pid_I

        self.pid_D.hardware_read_func = self.pid.read_pid_D
        self.pid_D.hardware_set_func = self.pid.write_pid_D
        
        self.port.change_readonly(True)
        self.address.change_readonly(True)
        
        # connect GUI
            # not right now
            
    def disconnect(self):
        print "disconnect" + self.name
        #disconnect hardware
        #self.pid.serial.close()

        self.port.change_readonly(False)
        self.address.change_readonly(False)


        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.pid

    def run_mode_run(self):
        self.pid.write_run_mode('RUN')
        self.run_mode.read_from_hardware()

    def run_mode_stop(self):
        self.pid.write_run_mode('STOP')
        self.run_mode.read_from_hardware()

if __name__ == '__main__':
    from PySide import QtGui
    from base_gui import BaseMicroscopeGUI
    import sys

    class TestGUI(BaseMicroscopeGUI):
        
        ui_filename = "../base_gui.ui"
        
        def setup(self):
                    #Add hardware components
            print "Adding Hardware Components"
            
            self.omega_pt_pid = self.add_hardware_component(OmegaPtPIDControllerHardware(self))
                          
            #Add measurement components
            print "Create Measurement objects"
    
            #Add additional logged quantities
    
            # Connect to custom gui



    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Test Gui")
    
    gui = TestGUI(app)
    gui.show()
    
    sys.exit(app.exec_())