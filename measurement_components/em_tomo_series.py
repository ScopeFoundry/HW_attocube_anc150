from measurement import Measurement
from numpy import ndarray,zeros,uint16,array, round
import pyqtgraph as pg
import pythoncom
from PySide import QtCore, QtGui
import win32com.client
from random import choice, random, randint

class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    
    def setup(self):
        self.display_update_period = 0.1 #seconds
        self.debug = True       
        self.getHardware()
        self.setupUI()

    def getHardware(self):
        self.hardware = self.gui.hardware_components['em_hardware']
        self.hardware.connect()
        self.hardware.debug_mode.update_value(new_val=True)
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)

    def setupUI(self):
        
        self.minimum_tilt = self.add_logged_quantity(
                                name = 'minimum_tilt',
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
        self.maximum_tilt = self.add_logged_quantity(
                                name = 'maximum_tilt',
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
        try:
            self.ui.setWindowTitle('NCEM Tomography Tool')
            self.ui.btnPre.released.connect(self.preview)
            self.ui.btnAcq.released.connect(self.start)
            self.ui.btnAbo.released.connect(self.interrupt)   
            self.ui.btnMinTilt.released.connect(self.minTilt)     
            self.ui.btnMaxTilt.released.connect(self.maxTilt)
            #bin stuff
            self.ui.buttonGroup.setId(self.ui.bin1,1)
            self.ui.buttonGroup.setId(self.ui.bin2,2)
            self.ui.buttonGroup.setId(self.ui.bin4,4)  
            self.ui.buttonGroup.buttonReleased[int].connect(self.binChanged)
            self.ui.buttonGroup.button(self.hardware.current_binning.val).setChecked(True)
            
            self.hardware.current_exposure.connect_bidir_to_widget(self.ui.expBox)
            self.hardware.current_defocus.connect_bidir_to_widget(self.ui.defBox)
            
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.itr_finished[ndarray].connect(self.postIteration)
            
#             self.minimum_tilt.connect_bidir_to_widget(self.gui.ui.minBox)
#             self.maximum_tilt.connect_bidir_to_widget(self.gui.ui.maxBox)
        except Exception as err: 
            print "EM_Tomography: could not connect to custom main GUI", err
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.initialDF = self.Proj.Defocus
        if self.debug: print '-----DF:', str(self.initialDF),'m-----'
        if self.debug: print '-----end of getscope-----'
    def dummyStuff(self):
        x = round(random(),2)
        y = round(random(),2)
        lblx = choice(['+','-'])
        lbly = choice(['+','-'])
        if x%2==1: lbl = '+'
        self.ui.lblXYShift.setText('('+lblx+str(x)+', '+lbly+str(y)+')')
        d = randint(0,6)
        lbld = choice(['+','-'])
        if d==0: lbld=''
        self.ui.lblDeltaDefocus.setText(lbld+str(d)+'nm')
    def allocateStorage(self):
        if self.debug: print '-----allocating arrays-----'
        deltas = len(self.tiltList)
        self.series = zeros([self.xRes,self.yRes,deltas],dtype=uint16,) #contains raw data
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        self.viewer = self.graph_layout.addViewBox()
        self.viewer.enableAutoRange()
    def acqFoc(self):
        for ii in range(len(self.tiltList)):
            tiltVal = float(self.tiltList[ii])
            self.hardware.setAlphaTilt(tiltVal)
            acquiredImageSet = self.Acq.AcquireImages()      
            self.series[:,:,ii] = array(acquiredImageSet(0).AsSafeArray)
            if self.debug: print '-----acquired @ '+str(self.tiltList[ii])+'deg-----' 
            if self.debug: print 'Size:'+str(self.series.nbytes)  
            self.itr_finished.emit(self.series[:,:,ii])
    def preview(self):
        try:
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            acquiredImageSet = self.Acq.AcquireImages()      
            itr = array(acquiredImageSet(0).AsSafeArray) 
            self.itr_finished.emit(itr)
        except Exception as err:
            print self.name, "error:", err
    def _run(self):
        try:
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            self.allocateStorage()
            #self.acqFoc()
        except Exception as err:
            print self.name, "error:", err
        #there seems to be no need to emit a finished signal...
    def postAcquisition(self):
        print 'postacq'
    def postIteration(self,data):
        self.viewer.clear()
        self.viewer.addItem(pg.ImageItem(data))
        self.dummyStuff()
        print 'shape:', data.shape
        print 'postiter'
    def minTilt(self):
        self.hardware.tiltAlpha(self.hardware.minimum_tilt.val)
        print 'min tilt'
    def maxTilt(self):
        self.hardware.tiltAlpha(self.hardware.maximum_tilt.val)
        print 'max tilt'
    def binChanged(self,btnId):
        if btnId in self.hardware.getBinnings():
            res = 2048/btnId
            self.xRes = res
            self.yRes = res
            self.ui.lblXYRes.setText('('+str(res)+", "+str(res)+')')
            self.hardware.current_binning.update_value(new_val=btnId)

    def update_display(self):        
        self.gui.app.processEvents()

