from ScopeFoundry import HardwareComponent
from ScopeFoundryHW.ni_daq import NI_AdcTask

class NI_ADC_HW(HardwareComponent):
    
    def __init__(self, app, name='ni_adc', debug=False):
        self.name = name
        HardwareComponent.__init__(self, app, debug=debug)
        
        self.settings.New('adc_val', dtype=float, ro=True)
        self.settings.New('channel', dtype=str, inital='/Dev1/ai0')
        self.settings.New('terminal_config', dtype=str, initial='default',
                          choices=['default', 'rse', 'nrse', 'diff', 'pdiff'])
        
    def connect(self):
        S = self.settings
        
        # Open connection to hardware
        self.adc_task = NI_AdcTask(channel=S['channel'], range=S['range'], 
                                   name=self.name, terminalConfig=S['terminal_config'])
        
        self.adc_task.set_single()
        self.adc_task.start()
        
        #TODO disable channel and terminal_config 
        
        #connect settings to hardware
        self.settings.adc_val.connect_to_hardware(
                                read_func=self.read_adc_single)
        
    def disconnect(self):
        self.settings.disconnect_all_from_hardware()

        #TODO reenable channel and terminal_config 
        
        if hasattr(self, 'adc_task'):
            self.adc_task.close()
            del self.adc_task


            
    def read_adc_single(self):
        resp = self.adc.get()
        if self.debug_mode.val:
            self.log.debug( "read_adc_single resp: {}".format( resp))
        return float(resp[0])
    
    