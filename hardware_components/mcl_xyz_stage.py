'''
Created on Jul 27, 2014

@author: Edward Barnard
'''
from ScopeFoundry import HardwareComponent
try:
    from equipment.mcl_nanodrive import MCLNanoDrive
except Exception as err:
    print "Cannot load required modules for MclXYZStage:", err
from PySide import QtCore


class MclXYZStage(HardwareComponent):
    


    
    def setup(self):
        self.name = 'mcl_xyz_stage'

        
        # Created logged quantities
        lq_params = dict(  dtype=float, ro=True,
                           initial = -1,
                           vmin=-1,
                           vmax=100,
                           si = False,
                           unit='um')
        self.x_position = self.add_logged_quantity("x_position", **lq_params)
        self.y_position = self.add_logged_quantity("y_position", **lq_params)       
        self.z_position = self.add_logged_quantity("z_position", **lq_params)
        
        lq_params = dict(  dtype=float, ro=False,
                           initial = -1,
                           vmin=-1,
                           vmax=100,
                           unit='um')
        self.x_target = self.add_logged_quantity("x_target", **lq_params)
        self.y_target = self.add_logged_quantity("y_target", **lq_params)       
        self.z_target = self.add_logged_quantity("z_target", **lq_params)        
        
        
        lq_params = dict(unit="um", dtype=float, ro=True, initial=100, si=False)
        self.x_max = self.add_logged_quantity("x_max", **lq_params)
        self.y_max = self.add_logged_quantity("y_max", **lq_params)
        self.z_max = self.add_logged_quantity("z_max", **lq_params)

        lq_params = dict(dtype=str, choices=[("X","X"), ("Y","Y"),("Z","Z")])
        self.h_axis = self.add_logged_quantity("h_axis", initial="X", **lq_params)
        self.v_axis = self.add_logged_quantity("v_axis", initial="Y", **lq_params)
        
        self.MCL_AXIS_ID = dict(X = 2, Y = 1, Z = 3)
        self.xyz_axis_map = self.add_logged_quantity('xyz_axis_map', dtype=str, initial='213')
        self.xyz_axis_map.updated_value.connect(self.on_update_xyz_axis_map)
        
        
        self.move_speed = self.add_logged_quantity(name='move_speed',
                                                             initial = 1.0,
                                                             unit = "um/s",
                                                             vmin = 1e-4,
                                                             vmax = 1000,
                                                             si = False,
                                                             dtype=float)        
        
        # connect GUI
        if hasattr(self.app.ui, "cx_doubleSpinBox"):
            self.x_position.connect_bidir_to_widget(self.app.ui.cx_doubleSpinBox)
            self.app.ui.x_set_lineEdit.returnPressed.connect(self.x_target.update_value)
            self.app.ui.x_set_lineEdit.returnPressed.connect(lambda: self.app.ui.x_set_lineEdit.setText(""))

        if hasattr(self.app.ui, "cy_doubleSpinBox"):
            self.y_position.connect_bidir_to_widget(self.app.ui.cy_doubleSpinBox)
            self.app.ui.y_set_lineEdit.returnPressed.connect(self.y_target.update_value)
            self.app.ui.y_set_lineEdit.returnPressed.connect(lambda: self.app.ui.y_set_lineEdit.setText(""))

        if hasattr(self.app.ui, "cz_doubleSpinBox"):
            self.z_position.connect_bidir_to_widget(self.app.ui.cz_doubleSpinBox)
            self.app.ui.z_set_lineEdit.returnPressed.connect(self.z_target.update_value)
            self.app.ui.z_set_lineEdit.returnPressed.connect(lambda: self.app.ui.z_set_lineEdit.setText(""))

        if hasattr(self.app.ui, "nanodrive_move_slow_doubleSpinBox"):
            self.move_speed.connect_bidir_to_widget(
                                  self.app.ui.nanodrive_move_slow_doubleSpinBox)
        
        if hasattr(self.app.ui, "h_axis_comboBox"):
            self.h_axis.connect_bidir_to_widget(self.app.ui.h_axis_comboBox)
        if hasattr(self.app.ui, "v_axis_comboBox"):
            self.v_axis.connect_bidir_to_widget(self.app.ui.v_axis_comboBox)
        
        # connect logged quantities together
        self.x_target.updated_value[()].connect(self.read_pos)
        self.y_target.updated_value[()].connect(self.read_pos)
        self.z_target.updated_value[()].connect(self.read_pos)
        
    def on_update_xyz_axis_map(self):
        print "on_update_xyz_axis_map"
        map_str = self.xyz_axis_map.val
        self.MCL_AXIS_ID['X'] = int(map_str[0])
        self.MCL_AXIS_ID['Y'] = int(map_str[1])
        self.MCL_AXIS_ID['Z'] = int(map_str[2])
    
    def move_pos_slow(self, x=None,y=None,z=None):
        # move slowly to new position
        new_pos = [None, None,None]
        new_pos[self.MCL_AXIS_ID['X']-1] = x
        new_pos[self.MCL_AXIS_ID['Y']-1] = y
        new_pos[self.MCL_AXIS_ID['Z']-1] = z
        self.nanodrive.set_pos_slow(*new_pos)

        self.read_pos()
        
    def move_pos_fast(self,  x=None,y=None,z=None):
        new_pos = [None, None,None]
        new_pos[self.MCL_AXIS_ID['X']-1] = x
        new_pos[self.MCL_AXIS_ID['Y']-1] = y
        new_pos[self.MCL_AXIS_ID['Z']-1] = z
        self.nanodrive.set_pos(*new_pos)

    
    @QtCore.Slot()
    def read_pos(self):
        print "read_pos"
        self.x_position.read_from_hardware()
        self.y_position.read_from_hardware()
        if self.nanodrive.num_axes > 2:
            self.z_position.read_from_hardware()
        
    def connect(self):
        if self.debug_mode.val: print "connecting to mcl_xyz_stage"
        
        # Open connection to hardware
        self.nanodrive = MCLNanoDrive(debug=self.debug_mode.val)
        
        # connect logged quantities
        self.x_target.hardware_set_func  = \
            lambda x: self.nanodrive.set_pos_ax_slow(x, self.MCL_AXIS_ID["X"])
        self.y_target.hardware_set_func  = \
            lambda y: self.nanodrive.set_pos_ax_slow(y, self.MCL_AXIS_ID["Y"])
        if self.nanodrive.num_axes > 2:
            self.z_target.change_readonly(False)
            self.z_target.hardware_set_func  = \
                lambda z: self.nanodrive.set_pos_ax_slow(z, self.MCL_AXIS_ID["Z"])
        else:
            self.z_target.change_readonly(True)

        self.x_position.hardware_read_func = \
            lambda: self.nanodrive.get_pos_ax(int(self.MCL_AXIS_ID["X"]))
        self.y_position.hardware_read_func = \
            lambda: self.nanodrive.get_pos_ax(int(self.MCL_AXIS_ID["Y"]))
        if self.nanodrive.num_axes > 2:
            self.z_position.hardware_read_func = \
                lambda: self.nanodrive.get_pos_ax(self.MCL_AXIS_ID["Z"])
            
            
        self.x_max.hardware_read_func = lambda: self.nanodrive.cal[self.MCL_AXIS_ID["X"]]
        self.y_max.hardware_read_func = lambda: self.nanodrive.cal[self.MCL_AXIS_ID["Y"]]
        if self.nanodrive.num_axes > 2:
            self.z_max.hardware_read_func = lambda: self.nanodrive.cal[self.MCL_AXIS_ID["Z"]]
        
        self.move_speed.hardware_read_func = self.nanodrive.get_max_speed
        self.move_speed.hardware_set_func =  self.nanodrive.set_max_speed
        
        self.read_from_hardware()

    def disconnect(self):
        #disconnect logged quantities from hardware
        for lq in self.settings.as_dict().values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.nanodrive.close()
        
        # clean up hardware object
        del self.nanodrive
        
    @property
    def v_axis_id(self):
        return self.MCL_AXIS_ID[self.v_axis.val]
    
    @property
    def h_axis_id(self):
        return self.MCL_AXIS_ID[self.h_axis.val]
    
    @property
    def x_axis_id(self):
        return self.MCL_AXIS_ID["X"]
    
    @property
    def y_axis_id(self):
        return self.MCL_AXIS_ID["Y"]
    
    @property
    def z_axis_id(self):
        return self.MCL_AXIS_ID["Z"]
    