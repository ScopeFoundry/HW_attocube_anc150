'''
Created on Sep 16, 2016

@author: Edward Barnard
'''
from ScopeFoundry import Measurement
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import time

class AttocubeInterface(Measurement):

    name = 'attocube_interface'


    def setup(self):
        self.ui_filename = sibling_path(__file__,"attocube_interface.ui")
        self.ui = load_qt_ui_file(self.ui_filename)
        #self.ui.show()
        self.ui.setWindowTitle(self.name)
        
        stage = self.app.hardware['attocube_xy_stage']
        
        ui_connections = [
            ('x_position', 'a1_pos_doubleSpinBox'),
            ('x_target_position', 'a1_auto_target_doubleSpinBox'),
            #('x_step_voltage', 'a1_amp_doubleSpinBox'),
            ('x_electrically_connected', 'a1_electrically_connected_checkBox'),
            ('x_enable_closedloop', 'a1_auto_move_checkBox'),
            ]
        
        for lq_name, widget_name in ui_connections:                          
            stage.settings.get_lq(lq_name).connect_bidir_to_widget(getattr(self.ui, widget_name))

        self.activation.connect_bidir_to_widget(self.ui.live_update_checkBox)

    def setup_figure(self):
        pass
#         self.clear_qt_attr('graph_layout')
#         self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
#         self.ui.plot_groupBox.layout().addWidget(self.graph_layout)

    def run(self):
        stage = self.app.hardware['attocube_xy_stage']
        while not self.interrupt_measurement_called:
            stage.read_from_hardware()
            import time
            time.sleep(0.05)