from measurement import Measurement
from numpy import ndarray,zeros,uint16,array, round
import pyqtgraph as pg
import pythoncom
from PySide import QtCore
import win32com.client
from random import choice, random, randint
from foundry_scope.logged_quantity import LQRange
from threading import Thread

class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    def __init__(self,gui):
        self.debug = True
        Measurement.__init__(self, gui)
         
    def setup(self):
        self.display_update_period = 0.1 #seconds
        self.getHardware()
        self.setupUI()

    def getHardware(self):
        self.hardware = self.gui.hardware_components['em_hardware']
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)

    def setupUI(self):
        
        self.minimum_tilt = self.add_logged_quantity(
                                name = 'minimum_tilt', initial = -80.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
        self.maximum_tilt = self.add_logged_quantity(
                                name = 'maximum_tilt', initial = 80.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
        self.step_tilt = self.add_logged_quantity(
                                name = 'step_tilt', initial = 6.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-80.0,vmax=80.0)
        self.num_tilts = self.add_logged_quantity(
                                name = 'num_tilts', initial = 30,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=2,vmax=160)
        self.num_repeats = self.add_logged_quantity(
                                name = 'num_repeats', initial = 1,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=1,vmax=30)
        self.tiltLQRange = LQRange(self.minimum_tilt,self.maximum_tilt,
                                   self.step_tilt,self.num_tilts)
        
        try:
            self.ui.setWindowTitle('NCEM Tomography Tool')
            self.ui.btnPreview.released.connect(self.preview)
            self.ui.btnPreview_2.released.connect(self.preview)
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
            #hardware LQs
            self.hardware.current_exposure.connect_bidir_to_widget(self.ui.expBox)
            self.hardware.current_defocus.connect_bidir_to_widget(self.ui.defBox)
            #measurement LQs
            self.num_tilts.connect_bidir_to_widget(self.ui.numBox)
            self.step_tilt.connect_bidir_to_widget(self.ui.steBox)
            self.minimum_tilt.connect_bidir_to_widget(self.ui.minBox)
            self.maximum_tilt.connect_bidir_to_widget(self.ui.maxBox)
            self.num_repeats.connect_bidir_to_widget(self.ui.repBox)
            #signals
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.itr_finished[ndarray].connect(self.postIteration)        

        except Exception as err: 
            print "EM_Tomography: could not connect to custom main GUI", err
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.initialDF = self.Proj.Defocus
        myCcdAcqParams = self.Acq.Cameras(0).AcqParams
        myCcdAcqParams.Binning = self.hardware.current_binning.val
        myCcdAcqParams.ExposureTime = self.hardware.current_exposure.val
        myCcdAcqParams.ImageCorrection = win32com.client.constants.AcqImageCorrection_Unprocessed #this has to be unprocessed. Not sure if it affects data from the micoscope itself
        myCcdAcqParams.ImageSize = win32com.client.constants.AcqImageSize_Full
        self.Acq.Cameras(0).AcqParams = myCcdAcqParams
        if self.debug: print '-----DF:', str(self.initialDF),'m-----'
        if self.debug: print '-----end of getscope-----'
    def dummyStuff(self):
        x = round(random(),2)
        y = round(random(),2)
        lblx = choice(['+','-'])
        lbly = choice(['+','-'])
        if x%2==1: lbl = '+'
        self.ui.lblXYShift.setText('('+lblx+str(x)+'um, '+lbly+str(y)+'um)')
        d = randint(0,6)
        lbld = choice(['+','-'])
        if d==0: lbld=''
        self.ui.lblDeltaDefocus.setText(lbld+str(d)+'nm')
    def allocateStorage(self):
        if self.debug: print '-----allocating arrays-----'
        deltas = len(self.tiltLQRange.array)
        self.seriesDict = dict()
        for x in self.tiltLQRange.array:
            self.seriesDict.update(x=[])
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        self.viewer = self.graph_layout.addViewBox()
        self.viewer.enableAutoRange()
    def acqFoc(self):
        pass
    def preview(self):
        try:
            print self.tiltLQRange.array
            #self.getScope()
            acquiredImageSet = self.hardware.acquire()      
            itr = array(acquiredImageSet(0).AsSafeArray) 
            self.itr_finished.emit(itr)
        except Exception as err:
            print self.name, "error:", err
    def _run(self):
        try:
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            self.allocateStorage()
            for ii in range(len(self.tiltLQRange.array)):
                print len(self.tiltLQRange.array)
                print 'loop ' + str(ii)
                tiltVal = float(self.tiltLQRange.array[ii])
                #self.hardware.setAlphaTilt(tiltVal)
                acquiredImageSet = self.Acq.AcquireImages()      
                itr = array(acquiredImageSet(0).AsSafeArray) 
                self.itr_finished.emit(itr)
                if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----' 
                if self.debug: print 'Size:'+str(itr.nbytes)  
            self.measurement_sucessfully_completed.emit()
        except Exception as err:
            print self.name, "error:", err
    def postAcquisition(self):
        print '-----postacq-----'
    def updateView(self,data):
        self.viewer.clear()
        self.viewer.addItem(pg.ImageItem(data))
        self.dummyStuff()
        self.update_display()
        print 'shape:', data.shape
        print '-----postiter-----'
    def postIteration(self,data):
#         thread = Thread(target = self.updateView,args = (data,))
#         thread.start()
#         thread.join()
        self.updateView(data)

    def minTilt(self):
        self.hardware.setAlphaTilt(self.minimum_tilt.val)
        print '-----min tilt-----'
    def maxTilt(self):
        self.hardware.setAlphaTilt(self.maximum_tilt.val)
        print '-----max tilt-----'
    def binChanged(self,btnId):
        if btnId in self.hardware.getBinnings():
            res = 2048/btnId
            self.xRes = res
            self.yRes = res
            self.ui.lblXYRes.setText('('+str(res)+", "+str(res)+')')
            self.hardware.current_binning.update_value(new_val=btnId)
    def update_display(self):        
        self.gui.app.processEvents()


