from ScopeFoundry import HardwareComponent
import equipment.spacenavigator_new as spacenavigator


class Connexion_HC(HardwareComponent):

    name = "connexion_hc"

    def setup(self):
                
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
        self.devices = self.settings.New(name='devices', initial="Auto", dtype=str, choices = [("Auto", "Auto"),("SpaceNavigator", "SpaceNavigator"),("SpaceMouse", "SpaceMouse")])

    
    def connect(self):
        print("connect connexion")
        ##self.dev = self.open()
        self.dev()
        assert not self.dev is None
                
        self.x.hardware_read_func = self.read_x
        self.y.hardware_read_func = self.read_y
        self.z.hardware_read_func = self.read_z
        self.roll.hardware_read_func = self.read_roll
        self.pitch.hardware_read_func = self.read_pitch
        self.yaw.hardware_read_func = self.read_yaw
        self.button.hardware_read_func = self.read_button
        print("done")
        
    
    def disconnect(self):
        self.dev.close()
        
        # disconnect all LQ's
        # TODO
        
        # delete object
        del self.dev
    

    
    def dev(self):
        if self.devices.val == "Auto":
            self.success = spacenavigator.open()
        else:
            self.success = spacenavigator.open(device=self.devices.val)
        
    def read_x(self):
        return self.success.read().x
    
    def read_y(self):
        return self.success.read().y
    
    def read_z(self):
        return self.success.read().z

    def read_roll(self):
        return self.success.read().roll

    def read_pitch(self):
        return self.success.read().pitch
    
    def read_yaw(self):
        return self.success.read().yaw

    def read_button(self):
        return self.success.read().button
