# -*- coding: utf-8 -*-
"""
Created on Tue Apr  1 09:25:48 2014

@author: esbarnard
"""

from PySide import QtCore
import threading
import time
from logged_quantity import LoggedQuantity
from collections import OrderedDict

class Measurement(QtCore.QObject):
    
    measurement_sucessfully_completed = QtCore.Signal(()) # signal sent when full measurement is complete

    def __init__(self, gui):
        """type gui: MicroscopeGUI
        """
        
        QtCore.QObject.__init__(self)

        self.gui = gui

        self.display_update_period = 0.1 # seconds
        self.display_update_timer = QtCore.QTimer(self.gui.ui)
        self.display_update_timer.timeout.connect(self.on_display_update_timer)
        self.acq_thread = None
        
        self.logged_quantities = OrderedDict()

    def setup_figure(self):
        pass
    
    def _run(self):
        raise NotImplementedError("Measurement _run not defined")
    
    @QtCore.Slot()
    def start(self):
        self.interrupt_measurement_called = False
        if (self.acq_thread is not None) and self.is_measuring():
            raise RuntimeError("Cannot start a new measurement while still measuring")
        self.acq_thread = threading.Thread(target=self._run)
        # TODO Stop Display Timers
        self.gui.stop_display_timers()
        self.acq_thread.start()
        self.t_start = time.time()
        self.display_update_timer.start(self.display_update_period*1000)
    
    @QtCore.Slot()
    def interrupt(self):
        self.interrupt_measurement_called = True
        #Make sure display is up to date        
        #self.on_display_update_timer()

    def is_measuring(self):
        return self.acq_thread.is_alive()
        
    
    @QtCore.Slot()
    def on_display_update_timer(self):
        #update figure
                
        if not self.is_measuring():
            self.display_update_timer.stop()

    def add_logged_quantity(self, name, **kwargs):
        lq = LoggedQuantity(name=name, **kwargs)
        self.logged_quantities[name] = lq
        return lq
