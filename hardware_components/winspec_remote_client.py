from ScopeFoundry import HardwareComponent

class WinSpecRemoteClient(HardwareComponent):
    
    def setup(self):
        
        self.settings.New('host', dtype='str', initial='192.168.1.1:9000')
    
    def connect(self):
        # connect settings to hardware
        pass
    
    def disconnect(self):
        #disconnect hardware
        #self.cam.close()
        
        #disconnect logged quantities from hardware
        for lq in self.logged_quantities.values():
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        # del self.cam
