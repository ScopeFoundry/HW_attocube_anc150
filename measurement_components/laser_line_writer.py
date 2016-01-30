'''
Created on Aug 5, 2015

@author: Edward Barnard and Benedikt Ursprung
'''
import time
from ScopeFoundry import Measurement

class LaserLineWriter(Measurement):
    name = 'laser_line_writer'
    
    def setup(self):
        
        #logged quantities
        
        #GUI events
        pass
        
    def setup_figure(self):
        pass
    
    def _run(self):
        #hardware 
        self.stage_hc = self.gui.mcl_xyz_stage_hc
        self.nanodrive = self.stage_hc.nanodrive
        shutter_lq = self.gui.shutter_servo_hc.shutter_open
        
        # x, y, open
        moves = [
                 ( 0,  0, False),
                 (75,  0, True),
                 (75, 75, True),
                 ( 0, 75, True),
                 ( 0,  0, True),
        ]
               
        #test pattern
        moves = (
            self.rect(10,10, 20,10) +
            self.cross(50,20, 10,10) 
            )
        
        for ii in range(0,5):
            moves += self.digit(10+ii*10, 60,  w=5, h=10, N=ii)
        for ii in range(5,10):
            moves += self.digit(10+(ii-5)*10, 45,  w=5, h=10, N=ii)
        for ii in range(10,16):
            moves += self.digit(10+(ii-10)*10, 30,  w=5, h=10, N=ii)

        # corner cross and labeling
        #moves = self.labeled_cross(35, 35, 10, N=1)


        #moves = self.v_arrow(xtip=35, ytip=20, w=20, h=+50)
        moves = self.v_arrow(xtip=35, ytip=10, w=20, h=+50)

        #moves = self.h_arrow(10, 35, 50, 20)

        # close shutter
        shutter_lq.update_value(False)
        time.sleep(0.500)

        
        for move in moves:
            print self.name , "move:", move
            x, y, shutter_open_for_move = move
            
            if shutter_open_for_move != shutter_lq.val:
                shutter_lq.update_value(shutter_open_for_move)
                time.sleep(0.500)

            # move slowly to position
            self.stage_hc.move_pos_slow(x=x, y=y)
            self.stage_hc.read_pos()
        
        # close shutter
        shutter_lq.update_value(False)
        time.sleep(0.500)
        
        print self.name , "done"
        
        
    def update_display(self):
        pass
    
    def rect(self, xc, yc, w, h):
        x0 = xc - 0.5*w
        x1 = xc + 0.5*w
        y0 = yc - 0.5*h
        y1 = yc + 0.5*h
        return [
                 ( x0, y0, False),
                 ( x1, y0, True),
                 ( x1, y1, True),
                 ( x0, y1, True),
                 ( x0, y0, True),
        ]
    
    def cross(self, xc, yc, w, h):
        x0 = xc - 0.5*w
        x1 = xc + 0.5*w
        y0 = yc - 0.5*h
        y1 = yc + 0.5*h
        return [
                 ( x0, yc, False),
                 ( x1, yc, True),
                 ( xc, y0, False),
                 ( xc, y1, True),
        ]
        
    def digit(self, xc, yc, w, h, N):
        x0 = xc - 0.5*w
        x1 = xc + 0.5*w
        y0 = yc - 0.5*h
        y1 = yc + 0.5*h
        # Hexadecimal encodings for displaying the digits 0 to F
        num_encoding = [0x7E, 0x30, 0x6D, 0x79, 0x33, 0x5B, 0x5F, 0x70,
                        0x7F, 0x7B, 0x77, 0x1F, 0x4E, 0x3D, 0x4F, 0x47]
        abcdefg = num_encoding[N]
        open_shutter_list = [abcdefg >> i & 1 for i in range(6,-1,-1)]
        a,b,c,d,e,f,g = open_shutter_list
        
        moves = [
         (x0, y1, False),
         (x1, y1, a),
         (x1, yc, b),
         (x1, y0, c),
         (x0, y0, d),
         (x0, yc, e),
         (x0, y1, f),
         (x0, yc, False),
         (x1, yc, g),
        ]
        
        return moves
    
    def R(self, xc,yc, w, h):
        x0 = xc - 0.5*w
        x1 = xc + 0.5*w
        y0 = yc - 0.5*h
        y1 = yc + 0.5*h

        """ 
             x0 x1
          --------
        y1:  1 \
          :  |  2
        yc:  3 /
          :  |\
        y0:  0  4
        """
        
        return [
                (x0, y0, False),
                (x0, y1, True),
                (x1, 0.5*(yc+y1), True),
                (x0, yc, True),
                (x1, y0, True)
                ]

        
    def labeled_cross(self, xc, yc, h, N ):
        moves = []
        moves += self.cross(xc, yc, h, h)
        moves += self.digit(xc-1.5*h, yc, 0.5*h, h, N)
        moves += self.R(xc-2.5*h, yc, 0.5*h, h)
        return moves
    
    def v_arrow(self, xtip,ytip, w, h):
        # h < 0 up arrow
        # h > 0 down arrow
        
        y1 =ytip + h
        yhead = ytip + 0.25*h
        x0 = xtip - 0.5*w
        x1 = xtip + 0.5*w
        
        moves = [
                 (xtip, ytip, False),
                 (x0,   yhead, True),
                 (x1,   yhead, True),
                 (xtip, ytip, True),
                 (xtip, y1, True),
                 ]
        return moves
        
    def h_arrow(self, xtip, ytip, w, h):
        # w > 0 left point arrow
        # w < 0 right pointing arrow
        
        x1 = xtip + w
        xhead = xtip + 0.25*w
        y0 = ytip - 0.5*h
        y1 = ytip + 0.5*h
        
        moves = [
                 (xtip, ytip, False),
                 (xhead,   y0, True),
                 (xhead,   y1, True),
                 (xtip, ytip, True),
                 (x1, ytip, True),
                 ]
        return moves
        
                
        
        
        
        
        
        
        
        
        
        