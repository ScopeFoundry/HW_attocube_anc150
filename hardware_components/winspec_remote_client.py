from ScopeFoundry import HardwareComponent
from equipment.winspec_remote_client import WinSpecRemoteClient

class WinSpecRemoteClientHC(HardwareComponent):
    
    name="WinSpecRemoteClient"
    
    def setup(self):
        
        self.settings.New('host', dtype=str, initial='192.168.236.128')
        self.settings.New('port', dtype=int, initial=9000, si=False)
        self.settings.New('acq_time', dtype=float, initial=1.0, unit='s', vmin=0.0,)
    
    def connect(self):
        # connect settings to hardware
        S = self.settings
        self.winspec_client = WinSpecRemoteClient(host=S['host'], port=S['port'], debug=S['debug_mode'])
        self.winspec_client.set_acq_time(S['acq_time'])
        
        self.settings.acq_time.hardware_set_func = self.winspec_client.set_acq_time
        self.settings.acq_time.hardware_read_func = self.winspec_client.get_acq_time
        
    
    def disconnect(self):
        #disconnect hardware
        #self.W.close()
        
        #disconnect logged quantities from hardware
        for lq in list(self.logged_quantities.values()):
            lq.hardware_read_func = None
            lq.hardware_set_func = None
        
        # clean up hardware object
        del self.W
        

        
        