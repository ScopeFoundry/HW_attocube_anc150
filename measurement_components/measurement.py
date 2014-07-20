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
    measurement_interrupted = QtCore.Signal(()) # signal sent when  measurement is complete due to an interruption
    measurement_state_changed = QtCore.Signal(bool) # signal sent when measurement started or stopped
    
    def __init__(self, gui, name):
        """type gui: MicroscopeGUI
        """
        
        QtCore.QObject.__init__(self)

        self.gui = gui
        self.name = name
        
        self.display_update_period = 0.1 # seconds
        self.display_update_timer = QtCore.QTimer(self.gui.ui)
        self.display_update_timer.timeout.connect(self.on_display_update_timer)
        self.acq_thread = None
        
        self.logged_quantities = OrderedDict()
        
        #self.setup()
        
        #self._add_control_widgets_to_measurements_tab()


    def setup_figure(self):
        print "Empy setup_figure called"
        pass
    
    def _run(self):
        raise NotImplementedError("Measurement _run not defined")
    
    @QtCore.Slot()
    def start(self):
        print "measurement", self.name, "start"
        self.interrupt_measurement_called = False
        if (self.acq_thread is not None) and self.is_measuring():
            raise RuntimeError("Cannot start a new measurement while still measuring")
        self.acq_thread = threading.Thread(target=self._run)
        # TODO Stop Display Timers
        self.gui.stop_display_timers()
        self.measurement_state_changed.emit(True)
        self.acq_thread.start()
        self.t_start = time.time()
        self.display_update_timer.start(self.display_update_period*1000)
    
    @QtCore.Slot()
    def interrupt(self):
        print "measurement", self.name, "interrupt"
        self.interrupt_measurement_called = True
        #Make sure display is up to date        
        #self.on_display_update_timer()

    def start_stop(self, start):
        print self.name, "start_stop", start
        if start:
            self.start()
        else:
            self.interrupt()


        
    def is_measuring(self):
        return self.acq_thread.is_alive()
        
    
    def update_display(self):
        "Override this function to provide figure updates when the display timer runs"
        pass
    
    @QtCore.Slot()
    def on_display_update_timer(self):
        #update figure
        try:
            self.update_display()
        except Exception, err:
            print self.name, "Failed to update figure:", err            
        finally:
            if not self.is_measuring():
                self.display_update_timer.stop()

    def add_logged_quantity(self, name, **kwargs):
        lq = LoggedQuantity(name=name, **kwargs)
        self.logged_quantities[name] = lq
        return lq

    #def _add_control_widgets_to_measurements_tab(self):

