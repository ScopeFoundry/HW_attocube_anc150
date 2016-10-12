#import pygame
import pygame.joystick
import time
from pygame.constants import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP

class XboxControl_EC(object):
        
    def __init__(self):
        self.debug = True
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_init():
            print("Joystick module initialized!")
            print("%s joysticks detected." % pygame.joystick.get_count())
        self.joystick = pygame.joystick.Joystick(1)
        

        print("Joystick instance created.")
        
    def connect(self):
        self.joystick.init()
        if self.joystick.get_init():
            print("Joystick initialized:", self.joystick.get_name())
        self.range_buttons = self.joystick.get_numbuttons()
        self.range_hats = self.joystick.get_numhats()
        self.range_axes = self.joystick.get_numaxes()
    


#     def call_event_queue(self):

#  
#         event_list = pygame.event.get()
#         for event in event_list:
#             if event.type == pygame.JOYAXISMOTION:
#                 if self.debug: print("Joy Axis Moved.")
#                 for i in range(self.range_axes):
#                     resp = self.joystick.get_axis(i)
#                     #if resp != 0:
#                     print(resp, "Moved axis: %i" % i)
#             elif event.type == pygame.JOYHATMOTION:
#                 if self.debug: print("Joy Hat Moved.")
#                 for i in range(self.range_hats):
#                     resp = self.joystick.get_hat(i)
#                     print(resp, "Pressed hat: %i" % i)
# 
#             elif event.type == pygame.JOYBUTTONUP:
#                 if self.debug: print("Button Released.")
#             elif event.type == pygame.JOYBUTTONDOWN:
#                 if self.debug: print("Button Pressed.")
#                 for i in range(self.range_buttons):
#                     resp = self.joystick.get_button(i)
#                     print(resp, "Pressed button: %i" % i)
    

                        
    
    
    
    def disconnect(self):
        self.joystick.quit()
        del self.joystick
        pygame.joystick.quit()
        #del pygame.joystick
        pygame.quit()
    
        
## Debug stage; temporary! ##
    
# if __name__ == '__main__':
#     xb = XboxControl_EC()
#     xb.connect()
#     xb.call_event_queue()
#     time.sleep(0.2)
#     xb.call_event_queue()
#     time.sleep(0.2)
#     xb.call_event_queue()
#     time.sleep(0.2)
#     xb.call_event_queue()
#     time.sleep(0.2)
#     xb.call_event_queue()
    
#     xb.disconnect()