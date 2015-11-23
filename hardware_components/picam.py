from . import HardwareComponent
try:
    from equipment.picam import PiCAM
except Exception as err:
    print "Could not load modules needed for AndorCCD:", err

import equipment.picam_ctypes as picam_ctypes
from equipment.picam_ctypes import PicamParameter


class PicamHardware(HardwareComponent):
    name = "picam"

    def setup(self):
        pass

        # Create logged quantities
        self.status = self.add_logged_quantity(name='ccd_satus', dtype=str, fmt="%s",ro=True)
    
        for name, param in PicamParameter.items():
            print name, param
            dtype_translate = dict(FloatingPoint=float, Boolean=bool, Integer=int)
            if param.param_type in dtype_translate:
                self.add_logged_quantity(name=param.short_name, dtype=dtype_translate[param.param_type])

            elif param.param_type == 'Enumeration':
                enum_name = "Picam{}Enum".format(param.short_name)
                if hasattr(picam_ctypes, enum_name):
                    enum_obj = getattr(picam_ctypes, enum_name)
                    choice_names = enum_obj.bysname.keys()
                    self.add_logged_quantity(name=param.short_name, dtype=str, choices=zip(choice_names, choice_names))

    
        #connect to custom gui - NOTE:  these are not disconnected! 

    def connect(self):
        if self.debug_mode.val: print "Connecting to PICAM"
        
        self.cam = PiCAM()

        supported_pnames = self.cam.get_param_names()

        for pname in supported_pnames:
            if pname in self.logged_quantities:
                print "connecting", pname
                lq = self.logged_quantities[pname]
                print "lq.name", lq.name
                lq.hardware_read_func = lambda pname=pname: self.cam.read_param(pname)
                print lq.read_from_hardware()
                

    def disconnect(self):
        
        #disconnect hardware
        self.cam.close()
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.cam
        
        #self.is_connected = False