from __future__ import division, print_function
import numpy as np
from ScopeFoundry.scanning.base_cartesian_scan import BaseCartesian2DSlowScan
from ScopeFoundry import Measurement, LQRange
import time

class MCLStage2DSlowScan(BaseCartesian2DSlowScan):
    
    name = "MCLStage2DSlowScan"
    
    def setup(self):
        BaseCartesian2DSlowScan.setup(self)
        #Hardware
        self.stage = self.app.hardware.mcl_xyz_stage

    def move_position_start(self, x,y):
        #self.stage.y_position.update_value(x)
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_slow(x,y,None)
    
    def move_position_slow(self, x,y, dx,dy):
        #self.stage.y_position.update_value(y)
        self.stage.nanodrive.set_pos_slow(x,y,None)
        self.stage.x_position.read_from_hardware()
        self.stage.y_position.read_from_hardware()

    def move_position_fast(self, x,y, dx,dy):
        #self.stage.x_position.update_value(x)
        self.stage.nanodrive.set_pos(x, y, None)            
    