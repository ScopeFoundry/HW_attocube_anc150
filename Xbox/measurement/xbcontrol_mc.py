"""Written by Alan Buckley with suggestions for improvement 
from Ed Barnard and Lev Lozhkin"""
from ScopeFoundry.measurement import Measurement
import time
from ScopeFoundry.helper_funcs import sibling_path, load_qt_ui_file
import pygame.event
from pygame.constants import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP
from equipment.xbcontrol_ec import XboxControl_EC

class XboxControl_MC(Measurement):

    name = "xbcontrol_mc"
    direction_map = {
        (0,1): 'N', 
        (-1,1): 'NW',
        (-1,0): 'W',
        (-1,-1): 'SW',
        (0,-1): 'S',
        (1,-1): 'SE',
        (1,0): 'E',
        (1,1): 'NE',
        (0,0): 'Origin'}
    button_map = {
        0: 'A',
        1: 'B',
        2: 'X',
        3: 'Y',
        4: 'LB',
        5: 'RB',
        6: 'Back',
        7: 'Start',
        8: 'LP',
        9: 'RP'}

    def setup(self):
        self.dt = 0.05
        self.gui
        
        self.ui_filename = "measurement/Controller.ui"
        # UI
        self.ui = load_qt_ui_file(self.ui_filename)
        self.ui.setWindowTitle(self.name)
        
        self.control = self.app.hardware.xbcontrol_hc


        #Access equipment class:
        EC = XboxControl_EC()
        EC.connect()
        self.joystick = EC.joystick
        self.range_axes = EC.joystick.get_numaxes()
        self.range_buttons = EC.joystick.get_numbuttons()
        self.range_hats = EC.joystick.get_numhats()
        
        # Buttons
        self.control.A.connect_bidir_to_widget(self.ui.a_radio)
        self.control.B.connect_bidir_to_widget(self.ui.b_radio)
        self.control.X.connect_bidir_to_widget(self.ui.x_radio)
        self.control.Y.connect_bidir_to_widget(self.ui.y_radio)
        self.control.LB.connect_bidir_to_widget(self.ui.LB_radio)
        self.control.RB.connect_bidir_to_widget(self.ui.RB_radio)
        self.control.ls_lr.connect_bidir_to_widget(self.ui.ls_hdsb)
        self.control.ls_ud.connect_bidir_to_widget(self.ui.ls_vdsb)
        self.control.rs_lr.connect_bidir_to_widget(self.ui.rs_hdsb)
        self.control.rs_ud.connect_bidir_to_widget(self.ui.rs_vdsb)
        self.control.triggers.connect_bidir_to_widget(self.ui.trig_dsb)
        
        # Dpad positions
        self.control.N.connect_bidir_to_widget(self.ui.north)
        self.control.NW.connect_bidir_to_widget(self.ui.northwest)
        self.control.W.connect_bidir_to_widget(self.ui.west)
        self.control.SW.connect_bidir_to_widget(self.ui.southwest)
        self.control.S.connect_bidir_to_widget(self.ui.south)
        self.control.SE.connect_bidir_to_widget(self.ui.southeast)
        self.control.E.connect_bidir_to_widget(self.ui.east)
        self.control.NE.connect_bidir_to_widget(self.ui.northeast)
        self.control.origin.connect_bidir_to_widget(self.ui.origin)
        
        # Controller name readout in ui element
        self.control.controller_name.connect_bidir_to_widget(self.ui.control_name_field)
        self.control.settings['Controller_Name'] = self.joystick.get_name()

    def run(self):
        print "run"
        while not self.interrupt_measurement_called:  
            time.sleep(self.dt)
            event_list = pygame.event.get()
            for event in event_list:
                if event.type == pygame.JOYAXISMOTION:
                    for i in range(self.range_axes):
                        self.control.settings['Axis_' + str(i)] = self.joystick.get_axis(i)

                elif event.type == pygame.JOYHATMOTION:
                    for i in range(self.range_hats):
                        # Clear Directional Pad values
                        for k in set(self.direction_map.values()):
                            self.control.settings[k] = False

                        # Check button status and record it
                        resp = self.joystick.get_hat(i)
                        try:
                            self.control.settings[XboxControl_MC.direction_map[resp]] = True
                        except KeyError:
                            print("Unknown dpad hat: ", resp)

                elif event.type in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
                    button_state = (event.type == pygame.JOYBUTTONDOWN)

                    for i in range(self.range_buttons):
                        if self.joystick.get_button(i) == button_state:
                            try:
                                self.control.settings[XboxControl_MC.button_map[i]] = button_state
                            except KeyError:
                                print("Unknown button: %i (target state: %s)" % (i,
                                    'down' if button_state else 'up'))

                else:
                    print("Unknown event type: ", event.type)

