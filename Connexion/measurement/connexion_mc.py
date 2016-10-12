"""Written by Ed Barnard and Alan Buckley"""
from ScopeFoundry.measurement import Measurement
import time
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file

class Connexion_MC(Measurement):

    name = "connexion_mc"

    #ui_filename = "../measurement/3D_control.ui"
    button_map = {  0: "none",
                    1: "left",
                    2: "right",
                    3: "left_right"}
    

    def setup(self):
        self.dt = 0.05
        self.gui
        
        self.ui_filename = "measurement/3D_control.ui"
        # UI 
        #self.ui_filename = sibling_path(__file__,"pl_img_linescan.ui")
        self.ui = load_qt_ui_file(self.ui_filename)
        self.ui.setWindowTitle(self.name)
        
        self.connexion = self.app.hardware.connexion_hc

        #self.open = self.connexion.initialize()
        #self.open = self.connexion.initialize
        
        
        self.connexion.x.connect_bidir_to_widget(
                self.ui.x_dsb)
        self.connexion.y.connect_bidir_to_widget(
                self.ui.y_dsb)
        self.connexion.z.connect_bidir_to_widget(
                self.ui.z_dsb)
        self.connexion.roll.connect_bidir_to_widget(
                self.ui.roll_dsb)
        self.connexion.pitch.connect_bidir_to_widget(
                self.ui.pitch_dsb)
        self.connexion.yaw.connect_bidir_to_widget(
                self.ui.yaw_dsb)
        self.connexion.button.connect_bidir_to_widget(
                self.ui.button_dsb)
        self.connexion.left.connect_bidir_to_widget(
                self.ui.left_cb)
        self.connexion.right.connect_bidir_to_widget(
                self.ui.right_cb)
        self.connexion.left_right.connect_bidir_to_widget(
                self.ui.lr_cb)

    def run(self):
        print "run"
        while not self.interrupt_measurement_called:
            
            self.state = self.connexion.dev.read()
            """Hardware object: self.connexion = self.app.hardware.connexion_hc"""
            self.connexion.settings['x_axis'] = self.state.x
            self.connexion.settings['y_axis'] = self.state.y
            self.connexion.settings['z_axis'] = self.state.z
            self.connexion.settings['roll_axis'] = self.state.roll
            self.connexion.settings['pitch_axis'] = self.state.pitch
            self.connexion.settings['yaw_axis'] = self.state.yaw
            self.connexion.settings['button'] = self.state.button
            for k in set(self.button_map.values()):
                self.connexion.settings[k] = False
            self.button_resp = self.state.button
            try:
                self.connexion.settings[self.button_map[self.button_resp]] = True
            except KeyError:
                print("Unknown button/button out of range. %i" % self.button_resp)
            time.sleep(self.dt)

