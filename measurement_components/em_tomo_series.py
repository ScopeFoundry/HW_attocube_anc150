from measurement import Measurement
from numpy import ndarray,zeros,uint16,array
import pyqtgraph as pg
import pythoncom
from PySide import QtCore, QtGui
import win32com.client
class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    
    def setup(self):        
        self.display_update_period = 0.1 #seconds
        self.debug = True
        self.hardware = self.gui.hardware_components['em_hardware']
        self.hardware.connect()
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)

        try:
            self.ui.btnAcq.released.connect(self.start)
            self.ui.btnAbo.released.connect(self.interrupt)   
            self.ui.btnMinTilt.released.connect(self.minTilt)     
            self.ui.btnMaxTilt.released.connect(self.maxTilt)  
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.itr_finished[ndarray].connect(self.postIteration)
            
            self.minimum_tilt = self.add_logged_quantity(
                                name = 'minimum_tilt',
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
            self.maximum_tilt = self.add_logged_quantity(
                                name = 'maximum_tilt',
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
            self.minimum_tilt.connect_bidir_to_widget(self.gui.ui.minBox)
            self.maximum_tilt.connect_bidir_to_widget(self.gui.ui.maxBox)
        except Exception as err:
            print "EM_Tomography: could not connect to custom main GUI", err
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.initialDF = self.Proj.Defocus
        print '-----DF:', str(self.initialDF),'m-----'
        self.setTemAcqVals()
        print '-----end of getscope-----'
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        ## Add 3 plots into the first row (automatic position)
        self.viewer = self.graph_layout.addViewBox()
        self.viewer.enableAutoRange()
    def _run(self):
        try:
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            acquiredImageSet = self.Acq.AcquireImages()      
            something = array(acquiredImageSet(0).AsSafeArray) 
            self.itr_finished.emit(something)
        except Exception as err:
            print self.name, "error:", err
        #there seems to be no need to emit a finished signal...
    def setTemAcqVals(self,):
        myCcdAcqParams = self.Acq.Cameras(0).AcqParams
        #myCcdAcqParams.Binning = 4
        #myCcdAcqParams.ExposureTime = 0.1
        myCcdAcqParams.ImageCorrection = win32com.client.constants.AcqImageCorrection_Unprocessed #this has to be unprocessed. Not sure if it affects data from the micoscope itself
        myCcdAcqParams.ImageSize = win32com.client.constants.AcqImageSize_Full
        self.Acq.Cameras(0).AcqParams = myCcdAcqParams
        print '-----set TEM vals-----'
    def postAcquisition(self):
        print 'postacq'
    def postIteration(self,data):
        self.viewer.addItem(pg.ImageItem(data))

        print 'shape:', data.shape
        print 'postiter'
    def minTilt(self):
        self.hardware.tiltAlpha(0)
        print 'min tilt'
    def maxTilt(self):
        self.hardware.tiltAlpha(0)
        print 'max tilt'
    def update_display(self):        
        self.gui.app.processEvents()

