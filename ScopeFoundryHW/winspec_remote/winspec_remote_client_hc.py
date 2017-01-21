from __future__ import division, absolute_import, print_function
from ScopeFoundry import HardwareComponent
from .winspec_remote_client import WinSpecRemoteClient

class WinSpecRemoteClientHW(HardwareComponent):
    
    name="winspec_remote_client"
    
    def setup(self):
        
        self.settings.New('host', dtype=str, initial='192.168.254.200')
        self.settings.New('port', dtype=int, initial=9000, si=False)
        self.settings.New('acq_time', dtype=float, initial=1.0, unit='s', vmin=0.0,)
        
        self.add_operation('reinitialize', self.reinitialize)
    
    def connect(self):
        # connect settings to device
        S = self.settings
        self.winspec_client = WinSpecRemoteClient(host=S['host'], port=S['port'], debug=S['debug_mode'])
        self.winspec_client.set_acq_time(S['acq_time'])
        
        self.settings.acq_time.hardware_set_func = self.winspec_client.set_acq_time
        self.settings.acq_time.hardware_read_func = self.winspec_client.get_acq_time
        
    def reinitialize(self):
        self.winspec_client.reinitialize()
    
    def disconnect(self):
        
        #disconnect logged quantities from hardware
        for lq in self.settings.as_list():
            lq.hardware_read_func = None
            lq.hardware_set_func = None

        if hasattr(self, 'winspec_client'):
            #disconnect device
            #self.winspec_client.close()
            
            # clean up device object
            del self.winspec_client
