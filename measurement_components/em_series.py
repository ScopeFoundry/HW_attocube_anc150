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
        self.debug = True
        Measurement.__init__(self,gui)
        self.hardware = self.gui.hardware_components['em_acquirer']
        self.hardware.connect()
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)
        em_gui.__init__(self,gui)
    def setup(self):        
        self.display_update_period = 0.001 #seconds
        self.ui.aboBtn.released.connect(self.interrupt)
        self.ui.acqBtn.released.connect(self.start)
        self.measurement_sucessfully_completed.connect(self.postAcquisition)
        self.itr_finished[ndarray].connect(self.postIteration)
        
    def setupFigure(self):
        pass
    def TEMMODE(self):
        if not hasattr(self,'hardware'): self.getScope()
        em_gui.TEMMODE(self)
        self.hardware.setup4Tem()
    def STEMMODE(self):
        if not hasattr(self,'hardware'): self.getScope()
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
        self.Acq.AcquireImages()
        print '-----end of getscope-----'
    def postAcquisition(self):
        em_gui.postAcquisition(self)
        if self.debug: print 'entered post acq'
    def _run(self):
        try:
            em_gui.onAcquire(self)
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            self.dfList = self.DFLMaker(self.initialDF) #this sets self.numDF as well
            self._mstruct.setList(self.dfList,'False') 
            self.allocateStorage()
            self.imageCount = 0
            if self._mstruct.type == 'Foc':
                if self.debug: print 'in foc'
                self.startImage()
                self.acqFoc()
                self.stopImage()
            if self._mstruct.type == 'Rot':
                if self.debug: print 'in rot'
                self.startImage()
                self.acqRot()
                self.stopImage()
            print '----run thread complete-----'
        except Exception as err:
            print self.name, "error:", err
        #there seems to be no need to emit a finished signal...
    def acqFoc(self):
        for ii in range(len(self._mstruct.lisDel)):
            defVal = ((float(self._mstruct.lisDel[ii])) * 1e-9)
            if self._mstruct.lisRel == True: #if the list is relative or absolute
                defVal += self.initialDF
            self.Proj.Defocus =  defVal    
            for jj in range(int(self._mstruct.numRep)):
                acquiredImageSet = self.Acq.AcquireImages()      
                self.series[:,:,ii,jj] = array(acquiredImageSet(0).AsSafeArray)
                if self.debug: print '-----acquired @ '+str(self._mstruct.lisDel[ii])+'nm-----' 
                if self.debug: print 'Size:'+str(self.series.nbytes)  
                self.itr_finished.emit(self.series[:,:,ii,jj])
    def acqRot(self):
        for ii in range(int(self._mstruct.numDel)):
            print len(self._mstruct.lisDel)
            #change rotation value      
            for jj in range(int(self._mstruct.numRep)):
                acquiredImageSet = self.Acq.AcquireImages()      
                self.series[:,:,ii,jj] = array(acquiredImageSet(0).AsSafeArray)
                print '-----acquired @ '+str(self._mstruct.lisDel[ii])+'nm-----'
                #self.itr_finished.emit(self.series[:,:,ii,jj])
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
