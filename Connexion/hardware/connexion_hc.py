from ScopeFoundry import HardwareComponent
import spacenavigator


class Connexion_HC(HardwareComponent):

    name = "connexion_hc"

    def setup(self):
        
        self.initialize = spacenavigator.open()
        self.x = self.settings.New(name='x_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)
        self.y = self.settings.New(name='y_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)
        self.z = self.settings.New(name='z_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)

        self.roll = self.settings.New(name='roll_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)
        self.pitch = self.settings.New(name='pitch_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)
        self.yaw = self.settings.New(name='yaw_axis', initial=0,
                                            dtype=float, fmt="%.2f", 
                                            ro=True, vmin=-1.0, vmax=1.0)
        self.button = self.settings.New(name='button', initial=0, dtype=int, fmt="%i",
                                            ro=True, vmin=0, vmax=3)
        self.left = self.settings.New(name='left', initial=0, dtype=bool,
                                            ro=True)
        self.right = self.settings.New(name='right', initial=0, dtype=bool,
                                            ro=True)
        self.left_right = self.settings.New(name='left_right', initial=0, dtype=bool,
                                            ro=True)
        self.none_setting = self.settings.New(name='none', initial=0, dtype=bool,
                                            ro=True)

    def connect(self):

        
        
        self.dev = spacenavigator.open()


        self.x.hardware_read_func = self.read_state_x
        self.y.hardware_read_func = self.read_state_y
        self.z.hardware_read_func = self.read_state_z
        self.roll.hardware_read_func = self.read_state_roll
        self.pitch.hardware_read_func = self.read_state_pitch
        self.yaw.hardware_read_func = self.read_state_yaw
        self.button.hardware_read_func = self.read_state_button
         
    def disconnect(self):
        self.dev.close()
        
        # disconnect all LQ's
        # TODO
        
        # delete object
        del self.dev
        
    
    def read_state_x(self):
        return self.dev.read().x
    
    def read_state_y(self):
        return self.dev.read().y
    
    def read_state_z(self):
        return self.dev.read().z
    
    def read_state_roll(self):
        return self.dev.read().roll
    
    def read_state_pitch(self):
        return self.dev.read().pitch
    
    def read_state_yaw(self):
        return self.dev.read().yaw
    
    def read_state_button(self):
        return self.dev.read().button
    

        
#     def read_all(self):
#         state = self.dev.read()
#         self.x.update_value(state.x)
#         self.y.update_value(state.y)
#         return 0
        