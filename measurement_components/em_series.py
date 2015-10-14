'''
Created on Oct 14, 2015

@author: Zach
'''
from measurement import Measurement
from EM_GUI import em_gui
from numpy import zeros,uint16
import pythoncom
import win32com.client

class SeriesMeasurement(Measurement,em_gui):

    name = "em_series"

    ui_filename = "measurement_components/mainwindow.ui"
    def __init__(self,gui):
        Measurement.__init__(self,gui)
        em_gui.__init__(self,gui)
        self.hardware = self.gui.hardware_components['em_acquirer']
        self.m = self.hardware.Scope
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.m )

        

    def setup(self):        
        self.display_update_period = 0.001 #seconds
        # Connect events
        self.ui.aboBtn.released.connect(self.interrupt)
        self.ui.acqBtn.released.connect(self.start)
    def setGlobals(self):
        self.acquirer = None
    def TEMMODE(self):
        em_gui.TEMMODE(self)
        self.hardware.setup4Tem()
    def STEMMODE(self):
        print '-----STEMMODE called-----'
        em_gui.STEMMODE(self)
        self.hardware.setup4Stem()

#     def getAcquirer(self,params):
#         if self.acquirer==None:
#             self.acquirer = SeriesThread(self.m_temScripting,params,self.mode[0])
#             self.acquirer.acq_finished.connect(self.postAcquisition)
#             self.acquirer.itr_finished[ndarray].connect(self.postIteration)
#             self.threads.append(self.acquirer) 
    def allocateStorage(self):
        print '-----setting globals in SeriesThread-----'
        x = int(self._mstruct.xDim)
        y = int(self._mstruct.yDim)
        deltas = len(self._mstruct.lisDel)
        repeats = int(self._mstruct.numRep)
        self.series = zeros([x,y,deltas,repeats],dtype=uint16,) #contains raw data
        self.ssSeries = zeros([x,y,2],dtype=uint16) #contains start/stop images
    def getScope(self):

        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.Ill = self._m.Illumination    
        self.initialDF = self.Proj.Defocus
        print '-----DF:', str(self.initialDF),'m-----'
        print '-----end of getscope-----'
    def postAcquisition(self):
        print 'entered post acq'
        self.series = self.acquirer.series
        self.startstop = self.acquirer.ssSeries
        self.acquirer.terminate()
        self.ui.lblStatus.setText('Acquisition complete')
        self.threads.remove(self.acquirer)
        self.acquirer = None
    def _run(self):
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        em_gui.onAcquire(self)
        self.getScope()
        self.dfList = self.DFLMaker(self.initialDF) #this sets self.numDF as well
        self._mstruct.setList(self.dfList,'False') 
        self.allocateStorage()
        self.imageCount = 0
        self.ui.lblStatus.setText('Acquiring...')
        print '----run thread-----'
        print self.Proj.Defocus
        
        #is this right place to put this?
        self.measurement_state_changed.emit(False)
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            self.measurement_interrupted.emit()
        pythoncom.CoUninitialize(0)
    def update_display(self):
        self.gui.app.processEvents()
