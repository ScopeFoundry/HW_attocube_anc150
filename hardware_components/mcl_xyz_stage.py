'''
Created on Jul 27, 2014

@author: Edward Barnard
'''
from . import HardwareComponent
try:
    from equipment.mcl_nanodrive import MCLNanoDrive
except Exception as err:
    print "Cannot load required modules for MclXYZStage:", err

MCL_AXIS_ID = dict(X = 2, Y = 1, Z = 3)


class MclXYZStage(HardwareComponent):
    
    def setup(self):
        self.name = 'mcl_xyz_stage'
        self.debug = False
        
        # Created logged quantities
        self.x_position = self.add_logged_quantity("x_position", 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-1,
                                                   vmax=100,
                                                   unit='um'
                                                   )
        self.y_position = self.add_logged_quantity("y_position", 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-1,
                                                   vmax=100,
                                                   unit='um'
                                                   )        
        self.z_position = self.add_logged_quantity("y_position", 
                                                   dtype=float,
                                                   ro=False,
                                                   vmin=-1,
                                                   vmax=100,
                                                   unit='um'
                                                   )     
        
        self.x_max = self.add_logged_quantity("x_max", dtype=float, ro=True, initial=100)
        self.y_max = self.add_logged_quantity("y_max", dtype=float, ro=True, initial=100)
        self.z_max = self.add_logged_quantity("z_max", dtype=float, ro=True, initial=100)

        self.h_axis = self.add_logged_quantity("h_axis", 
                                               dtype=str,
                                               initial="X", 
                                               choices=[("X","X"), 
                                                        ("Y","Y"),
                                                        ("Z","Z")])        

        self.v_axis = self.add_logged_quantity("v_axis", 
                                               dtype=str,
                                               initial="Y",
                                               choices=[("X","X"), 
                                                        ("Y","Y"),
                                                        ("Z","Z")])

        
        self.nanodrive_move_speed = self.add_logged_quantity(name='nanodrive_move_speed', 
                                                             dtype=float)        
        
        # connect GUI
        self.x_position.updated_value.connect(self.gui.ui.cx_doubleSpinBox.setValue)
        self.gui.ui.x_set_lineEdit.returnPressed.connect(self.x_position.update_value)

        self.y_position.updated_value.connect(self.gui.ui.cy_doubleSpinBox.setValue)
        self.gui.ui.y_set_lineEdit.returnPressed.connect(self.y_position.update_value)

        self.z_position.updated_value.connect(self.gui.ui.cz_doubleSpinBox.setValue)
        self.gui.ui.z_set_lineEdit.returnPressed.connect(self.z_position.update_value)
        
        self.nanodrive_move_speed.connect_bidir_to_widget(self.gui.ui.nanodrive_move_slow_doubleSpinBox)
        
    def connect(self):
        if self.debug: print "connecting to mcl_xyz_stage"
        
        # Open connection to hardware                        
        self.nanodrive = MCLNanoDrive(debug=self.debug)
        
        # connect logged quantities
        self.x_position.hardware_set_func = lambda x: self.nanodrive.set_pos_ax_slow(x, MCL_AXIS_ID["X"])
        self.y_position.hardware_set_func = lambda y: self.nanodrive.set_pos_ax_slow(y, MCL_AXIS_ID["Y"])
        self.z_position.hardware_set_func = lambda z: self.nanodrive.set_pos_ax_slow(z, MCL_AXIS_ID["Z"])

        
        self.nanodrive_move_speed.hardware_read_func = self.nanodrive.get_max_speed
        self.nanodrive_move_speed.hardware_set_func =  self.nanodrive.set_max_speed

    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.nanodrive.close()
        
        # clean up hardware object
        del self.nanodrive
        
    @property
    def v_axis_id(self):
        return MCL_AXIS_ID[self.v_axis.val]
    
    @property
    def h_axis_id(self):
        return MCL_AXIS_ID[self.h_axis.val]
    
    
    