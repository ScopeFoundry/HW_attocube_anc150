from PySide import  QtCore, QtGui

class LoggedQuantity(QtCore.QObject):

    updated_value = QtCore.Signal( (float,),(int,),(bool,), () ) # signal sent when value has been updated
    updated_text_value = QtCore.Signal(str)
    updated_choice_value = QtCore.Signal(int) # emits the index of the value in self.choices
    
    def __init__(self, name=None, dtype=float, 
                 hardware_read_func=None, hardware_set_func=None, 
                 initial=0, fmt="%g",
                 ro = False,
                 unit = None,
                 vmin=None, vmax=None, choices=None):
        QtCore.QObject.__init__(self)
        
        self.name = name
        self.dtype = dtype
        self.val = dtype(initial)
        self.hardware_read_func = hardware_read_func
        self.hardware_set_func = hardware_set_func
        self.fmt = fmt
        self.unit = unit
        self.vmin = vmin
        self.vmax = vmax
        self.choices = choices
        self.ro = ro
        
        self.oldval = None
        
    def read_from_hardware(self, send_signal=True):
        self.oldval = self.val
        if self.hardware_read_func:
            self.val = self.dtype(self.hardware_read_func())
            if send_signal:
                self.send_display_updates()
        return self.val

    @QtCore.Slot(str)
    @QtCore.Slot(float)
    @QtCore.Slot(int)
    @QtCore.Slot(bool)
    @QtCore.Slot()
    def update_value(self, new_val=None, update_hardware=True, send_signal=True):
        #print "called update_value"
        if new_val == None:
            new_val = self.sender().text()
        self.val = self.dtype(new_val)
        if update_hardware and self.hardware_set_func:
            self.hardware_set_func(self.val)   
        if send_signal:
            self.send_display_updates()
            
    def send_display_updates(self, force=False):
        if (self.oldval != self.val) or (force):
            #print "send display updates", self.name, self.val, self.oldval
            self.updated_value.emit(self.val)
            self.updated_text_value.emit( self.fmt % self.val )
            if self.choices is not None:
                self.updated_choice_value.emit( self.choices.index(self.val) )        
            self.oldval = self.val
            
    def update_choice_value(self, new_choice, **kwargs):
        self.update_value(self.choices[new_choice], **kwargs)
        
    def connect_bidir_to_widget(self, widget):
        if type(widget) == QtGui.QDoubleSpinBox:
            self.updated_value[float].connect(widget.setValue )
            widget.valueChanged[float].connect(self.update_value)
            widget.setKeyboardTracking(False)
            if self.vmin is not None:
                widget.setMinimum(self.vmin)
            if self.vmax is not None:
                widget.setMaximum(self.vmax)
            if self.unit is not None:
                widget.setSuffix(" "+self.unit)
            if self.dtype == int:
                widget.setDecimals(0)
            if self.ro:
                widget.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
                widget.setReadOnly(True)
            #events
            self.updated_value[float].connect(widget.setValue )
            widget.valueChanged[float].connect(self.update_value)
        elif type(widget) == QtGui.QCheckBox:
            self.update_value[bool].connect(widget.setChecked)
            widget.stateChanged.connect(widget.update_value)
            if self.ro:
                widget.setReadOnly(True)
        else:
            raise ValueError("Unknown widget type")
            

def print_signals_and_slots(obj):
    for i in xrange(obj.metaObject().methodCount()):
        m = obj.metaObject().method(i)
        if m.methodType() == QtCore.QMetaMethod.MethodType.Signal:
            print "SIGNAL: sig=", m.signature(), "hooked to nslots=",obj.receivers(QtCore.SIGNAL(m.signature()))
        elif m.methodType() == QtCore.QMetaMethod.MethodType.Slot:
            print "SLOT: sig=", m.signature()