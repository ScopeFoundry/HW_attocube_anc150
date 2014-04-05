from PySide import QtCore, QtGui
from logged_quantity import LoggedQuantity
from collections import OrderedDict

class HardwareComponent(QtCore.QObject):

    def add_logged_quantity(self, name, **kwargs):
        lq = LoggedQuantity(name=name, **kwargs)
        self.logged_quantities[name] = lq
        return lq
    
    def __init__(self, gui, debug=False):
        """type gui: MicroscopeGUI
        """        
        QtCore.QObject.__init__(self)

        self.gui = gui
        self.debug = debug

        self.logged_quantities = OrderedDict()
        
        self.setup()
        
        self._add_control_widgets_to_hardware_tab()
        
    def setup(self):
        """
        Runs during __init__, before the hardware connection is established
        Should generate desired LoggedQuantities
        """
        raise NotImplementedError()
    
    def _add_control_widgets_to_hardware_tab(self):
        cwidget = self.gui.ui.hardware_tab_scrollArea_content_widget
        
        self.controls_groupBox = QtGui.QGroupBox(self.name)
        self.controls_formLayout = QtGui.QFormLayout()
        self.controls_groupBox.setLayout(self.controls_formLayout)
        
        cwidget.layout().addWidget(self.controls_groupBox)
        
        self.connect_hardware_checkBox = QtGui.QCheckBox("Connect to Hardware")
        self.controls_formLayout.addRow("Connect", self.connect_hardware_checkBox)
        
        self.connect_hardware_checkBox.stateChanged.connect(self.enable_connection)

        
        self.control_widgets = OrderedDict()
        for lqname, lq in self.logged_quantities.items():
            #: :type lq: LoggedQuantity
            if lq.choices is not None:
                widget = QtGui.QComboBox()
                for c in lq.choices:
                    widget.addItem((lq.fmt % c))
                #events
                lq.updated_choice_value[int].connect(widget.setCurrentIndex)
                widget.currentIndexChanged.connect(lq.update_choice_value)
                
            elif lq.dtype in [int, float]:
                widget = QtGui.QDoubleSpinBox()
                widget.setKeyboardTracking(False)
                if lq.vmin is not None:
                    widget.setMinimum(lq.vmin)
                if lq.vmax is not None:
                    widget.setMaximum(lq.vmax)
                if lq.unit is not None:
                    widget.setSuffix(" "+lq.unit)
                if lq.dtype == int:
                    widget.setDecimals(0)
                if lq.ro:
                    widget.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
                    widget.setReadOnly(True)
                #events
                lq.updated_value[float].connect(widget.setValue )
                widget.valueChanged[float].connect(lq.update_value)
            elif lq.dtype in [bool]:
                widget = QtGui.QCheckBox()  
                lq.update_value[bool].connect(widget.setChecked)
                widget.stateChanged.connect(widget.update_value) 
            elif lq.dtype in [str]:
                widget = QtGui.QLineEdit()
                lq.updated_text_value[str].connect(widget.setText)
                widget.setReadOnly(True)
            if lq.ro:
                widget.setReadOnly(True)
            # Add to formlayout
            self.controls_formLayout.addRow(lqname, widget)
            self.control_widgets[lqname] = widget
        
        self.read_from_hardware_button = QtGui.QPushButton("Read From Hardware")
        self.read_from_hardware_button.clicked.connect(self.read_from_hardware)
        self.controls_formLayout.addRow("", self.read_from_hardware_button)
        

    @QtCore.Slot()    
    def read_from_hardware(self):
        for name, lq in self.logged_quantities.items():
            print "read_from_hardware", name
            lq.read_from_hardware()
        
    
    def connect(self):
        """
        Opens a connection to hardware
        and connects hardware to associated LoggedQuantities
        """
        raise NotImplementedError()
        
        
    def disconnect(self):
        """
        Disconnects the hardware and severs hardware--LoggedQuantities link
        """
        
        raise NotImplementedError()
    
    @QtCore.Slot(bool)
    def enable_connection(self, enable=True):
        if enable:
            self.connect()
        else:
            self.disconnect()