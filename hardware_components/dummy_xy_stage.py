from . import HardwareComponent


class DummmyXYStageEquipment(object):
    
    def __init__(self):
        self.x = 0
        self.y = 0
        # communicate with hardware here
    
    def read_x(self):
        self.x = self.x + self.noise()
        return self.x

    def read_y(self):
        self.y = self.y + self.noise()
        return self.y
    
    def write_x(self, x):
        self.x = x

    def write_y(self, y):
        self.y = y
    
    def close(self):
        print "dummy_xy_stage_equipment close"

class DummyXYStage(HardwareComponent):
    
    name = "dummy_xy_stage"
    
    def setup(self):
        lq_params = dict(  dtype=float, ro=False,
                           initial = -1,
                           vmin=-1,
                           vmax=100,
                           si = False,
                           unit='um')
        self.x_position = self.add_logged_quantity("x_position", **lq_params)
        self.y_position = self.add_logged_quantity("y_position", **lq_params)       

        self.x_position.reread_from_hardware_after_write = True
        self.x_position.spinbox_decimals = 3
        
        self.y_position.reread_from_hardware_after_write = True
        self.y_position.spinbox_decimals = 3

    def connect(self):
        if self.debug_mode.val: print "connecting to dummy_xy_stage"

        # Open connection to hardware
        self.stage_equip = DummmyXYStageEquipment()

        # connect logged quantities
        self.x_position.hardware_read_func = self.stage_equip.read_x
        self.y_position.hardware_read_func = self.stage_equip.read_y
        

    def disconnect(self):
        if self.debug_mode.val: print "disconnecting to dummy_xy_stage"
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        #disconnect hardware
        self.stage_equip.close()
        
        # clean up hardware object
        del self.stage_equip



