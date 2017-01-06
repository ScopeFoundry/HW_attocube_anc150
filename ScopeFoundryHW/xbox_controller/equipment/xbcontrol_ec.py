#import pygame
import pygame.joystick
import time
from pygame.constants import JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYBUTTONUP

class XboxControlDevice(object):
        
    def __init__(self):
        """Creates and initializes pygame.joystick object and creates 
        subordinate pygame.joystick.Joystick module"""
        self.debug = True
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_init():
            print("Joystick module initialized!")
            print("%s joysticks detected." % pygame.joystick.get_count())
        self.joystick = pygame.joystick.Joystick(0)
        print("Joystick instance created.")
        
        """Initializes joystick hardware and scans for number of 
        available HID features such as hats, sticks and buttons."""
        self.joystick.init()
        if self.joystick.get_init():
            print("Joystick initialized:", self.joystick.get_name())
        self.num_buttons = self.joystick.get_numbuttons()
        self.num_hats = self.joystick.get_numhats()
        self.num_axes = self.joystick.get_numaxes()
        
    def close(self):
        """Disconnects and removes modules upon closing application.
        Included are the pygame.joystick and pygame.joystick.Joystick modules."""
        self.joystick.quit()
        del self.joystick
        pygame.joystick.quit()
        #del pygame.joystick
        pygame.quit()
    
