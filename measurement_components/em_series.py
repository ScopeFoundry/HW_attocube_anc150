'''
Created on Oct 14, 2015

@author: Zach
'''
from measurement import Measurement
from EM_GUI import em_gui
from numpy import zeros,uint16,array,ndarray
import pythoncom
import win32com.client
from time import sleep
from PySide import QtCore
class SeriesMeasurement(Measurement,em_gui):
    itr_finished = QtCore.Signal(ndarray)

    name = "em_series"

    ui_filename = "measurement_components/em_window.ui"
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
    def setTemAcqVals(self,):
        myCcdAcqParams = self.Acq.Cameras(0).AcqParams
        myCcdAcqParams.Binning = int(self._mstruct.bin)
        myCcdAcqParams.ExposureTime = float(self._mstruct.doseTime)
        myCcdAcqParams.ImageCorrection = win32com.client.constants.AcqImageCorrection_Unprocessed #this has to be unprocessed. Not sure if it affects data from the micoscope itself
        myCcdAcqParams.ImageSize = win32com.client.constants.AcqImageSize_Full
        self.Acq.Cameras(0).AcqParams = myCcdAcqParams
        print '-----set TEM vals-----'
    def setStemAcqVals(self):
        self.myStemAcqParams = self.Acq.Detectors.AcqParams
        self.myStemAcqParams.Binning = int(self._mstruct.bin)
        self.myStemAcqParams.DwellTime = float(self._mstruct.doseTime)
        self.Acq.Detectors.AcqParams = self.myStemAcqParams
        print '-----set STEM vals-----'
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
        self.initialDF = self.Proj.Defocus
        print '-----DF:', str(self.initialDF),'m-----'
        if self._mstruct.mode == 'TEM': self.setTemAcqVals()
        if self._mstruct.mode == 'STEM': self.setStemAcqVals()

        print '-----end of getscope-----'
    def postAcquisition(self):
        print 'entered post acq'
        self.ui.lblStatus.setText('Acquisition complete')
    def _run(self):
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        em_gui.onAcquire(self)
        self.getScope()
        self.dfList = self.DFLMaker(self.initialDF) #this sets self.numDF as well
        self._mstruct.setList(self.dfList,'False') 
        self.allocateStorage()
        self.imageCount = 0
        if self._mstruct.type == 'Foc':
            print 'in foc'
            self.startImage()
            self.acqFoc()
            self.stopImage()
        if self._mstruct.type == 'Rot':
            self.startImage()
            self.acqRot()
            self.stopImage()
        print '----run thread complete-----'
        print self.Proj.Defocus
        pythoncom.CoUninitialize(0)
        #is this right place to put this?
        self.measurement_state_changed.emit(False)
        if not self.interrupt_measurement_called:
            self.measurement_sucessfully_completed.emit()
        else:
            self.measurement_interrupted.emit()
    def acqFoc(self):
        for ii in range(len(self._mstruct.lisDel)):
            defVal = ((float(self._mstruct.lisDel[ii])) * 1e-9)
            if self._mstruct.lisRel == True:
                defVal += self.initialDF
            print defVal
            self.Proj.Defocus =  defVal    
            for jj in range(int(self._mstruct.numRep)):
                acquiredImageSet = self.Acq.AcquireImages()      
                self.series[:,:,ii,jj] = array(acquiredImageSet(0).AsSafeArray)
                print '-----acquired @ '+str(self._mstruct.lisDel[ii])+'nm-----' 
                print 'Size:'+str(self.series.nbytes)  
                self.itr_finished.emit(self.series[:,:,ii,jj])
    def acqRot(self):
        for ii in range(int(self._mstruct.numDel)):
            print len(self._mstruct.lisDel)
            #change rotation value      
            for jj in range(int(self._mstruct.numRep)):
                acquiredImageSet = self.Acq.AcquireImages()      
                self.series[:,:,ii,jj] = array(acquiredImageSet(0).AsSafeArray)
                print '-----acquired @ '+str(self._mstruct.lisDel[ii])+'nm-----'
                self.itr_finished.emit(self.series[:,:,ii,jj])
    def startImage(self):
        acquiredImageSet=self.Acq.AcquireImages() #acquire 
        self.ssSeries[:,:,0] = array(acquiredImageSet(0).AsSafeArray)
        sleep(float(self._mstruct.setTim)) #delay to allow time to adjust defocus to starting val
        print '-----acquired start image-----'
    def stopImage(self):
        self.Proj.Defocus = self.initialDF
        sleep(self._mstruct.setTim)
        acquiredImageSet=self.Acq.AcquireImages() #acquire
        self.ssSeries[:,:,1] = array(acquiredImageSet(0).AsSafeArray)
        print '-----acquired stop image-----' 
    def update_display(self):
        self.gui.app.processEvents()
