from ScopeFoundry import BaseMicroscopeApp


import logging
logging.basicConfig(level='DEBUG')
logging.getLogger('').setLevel(logging.DEBUG)
logging.getLogger("ipykernel").setLevel(logging.WARNING)
logging.getLogger('PyQt4').setLevel(logging.WARNING)
logging.getLogger('PyQt5').setLevel(logging.WARNING)
logging.getLogger('traitlets').setLevel(logging.WARNING)

logging.getLogger('ScopeFoundry.logged_quantity.LoggedQuantity').setLevel(logging.WARNING)


class SupraCLApp(BaseMicroscopeApp):
    
    name = 'supra_cl'
    
    def setup(self):
        
        from Auger.sem_sync_raster_hardware import SemSyncRasterDAQ
        self.add_hardware_component(SemSyncRasterDAQ(self))

        from Auger.sem_sync_raster_measure import SemSyncRasterScan
        self.add_measurement_component(SemSyncRasterScan(self))

        self.settings_load_ini('supra_cl_defaults.ini')

        self.ui.show()

        
if __name__ == '__main__':
    app = SupraCLApp([])
    app.exec_()
