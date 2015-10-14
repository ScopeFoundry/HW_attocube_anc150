'''
A PyQT boilerplate for acquiring a series

@author Zach
'''

from PySide import QtCore, QtGui, QtUiTools

from numpy import around,append,arange,float,ndarray
from _m_struct import _Series_Params, _Mode
import ConfigParser
import time
import os

class em_gui(QtGui.QMainWindow):
    def __del__ ( self ): 
        self.ui = None
    def show(self): 
        #self.ui.exec_()
        self.ui.show()
    def __init__(self,app):
        self.app = app
        super(em_gui,self).__init__()
        self._loadSettings()
        self._defaults()
        self.setupUI()
        self.getUsrAcqVals()
        self.setup()
    def setup(self):
        pass
        """ Override to to stuff """ 
    def _defaults(self):
        self.mode = ['STEM','Focal']
        self.binnings = [1,2,4,8]

        self.threads = [] 
        self.acquirer = None
    def updateTitle(self):
        self.ui.setWindowTitle('%s %s Series'%(self.mode[0],self.mode[1]))
    def TEMMODE(self):
        print '-----TEMMODE called-----'
        self.ui.actionSTEM.setChecked(False)
        self.ui.actionTEM.setChecked(True)
        self.ui.lblTim.setText('Exposure Time (s)')
        self.ui.inTim.setText('0.1')
        self.ui.inFilPre.setText("TEMSeries $time $params")
        self.ui.inMaxBin.setText('2048')
        self.ui.inBin.setText('4')
        self.binnings = [1,2,4]


        self.mode[0] = 'TEM'
        self.updateTitle()
        
    def STEMMODE(self):
        print '-----STEMMODE called-----'
        self.ui.actionTEM.setChecked(False)
        self.ui.actionSTEM.setChecked(True)
        self.ui.lblTim.setText('Dwell Time (us)')
        self.ui.inTim.setText('12')
        self.binnings = [1,2,4,8]
        self.mode[0] = 'STEM'
        self.updateTitle()    
    def TILTMODE(self):
        print '-----TILTMODE called-----'
        self.ui.actionFocal.setChecked(False)
        self.ui.actionTilt.setChecked(True)
        self.ui.lblPar.setText('Tilt Parameters')
        self.ui.lblSte.setText('Tilt Step')
        self.ui.lblMax.setText('Maximum Tilt')
        self.ui.lblMin.setText('Minimum Tilt')
        self.ui.lblReps.setText('Repeats per Tilt')
        self.mode[1] = 'Tilt'
        self.updateTitle()        
    def FOCMODE(self):
        print '-----FOCMODE called-----'
        self.ui.lblPar.setText('Focus Parameters')
        self.ui.lblSte.setText('Defocus Step (nm)')
        self.ui.lblMin.setText('Min Defocus (nm)')
        self.ui.lblMax.setText('Max Defocus (nm)')
        self.ui.lblReps.setText('Repeats per Defocus')


        self.ui.actionTilt.setChecked(False)
        self.ui.actionFocal.setChecked(True)
        self.mode[1] = 'Focal'
        self.updateTitle()
    def setupUI(self):
        #self.app.setWindowIcon(QtGui.QIcon('../icons/favicon.png'))

        ui_filename = self.ui_filename
        ui_loader = QtUiTools.QUiLoader()
        ui_file = QtCore.QFile(ui_filename)
        ui_file.open(QtCore.QFile.ReadOnly); 
        self.ui = ui_loader.load(ui_file)
        ui_file.close()
        

        self.ui.setWindowTitle('STEM Focal Series')
        self.ui.inTim.setText(str(self.dweTim))
        self.ui.inBin.setText(str(self.bin))
        self.ui.inOutDir.setText(os.getcwd())
        self.ui.inFilInd.setText(str(self.intIndex))
        self.ui.inUsrOutDir.setText(str(self.usrDir))
        self.ui.inSamInf.setText(str(self.samInf))
        self.ui.inResNam.setText(str(self.usrNam))
        self.ui.lblSlider.setText('Image 1 of 11')
        self.ui.inMaxBin.setText("2048")
        self.ui.inFilPre.setText("STEMSeries $time $params")
        self.ui.inNum.setText("11")
        self.ui.inTim.setText("12")
        self.ui.inSte.setText("2")
        self.ui.inMax.setText("10")
        self.ui.inMin.setText("-10")
        self.ui.inSetTim.setText("2")
        self.ui.inNumRep.setText("1")
        self.ui.lblStatus.setText('Idle...')
        
        self.ui.viewSlider.setMinimum(1)
        self.ui.viewSlider.setMaximum(11)
        self.ui.viewSlider.setTickInterval(1)
        self.ui.viewSlider.setSingleStep(1)
        self.ui.viewSlider.setTickPosition(QtGui.QSlider.TickPosition(3))
        self.ui.viewSlider.valueChanged.connect(self.sliderMoved)
        self.ui.progressBar.setVisible(False)
        self.ui.progressBar.setMinimum(1)
        self.ui.progressBar.setMaximum(11)
        self.ui.inMin.setValidator(QtGui.QDoubleValidator())
        self.ui.inSte.setValidator(QtGui.QDoubleValidator())
        self.ui.inBin.setValidator(QtGui.QIntValidator())
        self.ui.inMin.textChanged.connect(self.checkDef)
        self.ui.inSte.textChanged.connect(self.checkDef)
        self.ui.connect(self.ui.inOutDir, QtCore.SIGNAL ('textChanged()'), self.checkDir())
        self.ui.inOutDir.textChanged.connect(self.checkDir)
        self.ui.inBin.textChanged.connect(self.checkBin) 
        self.ui.actionSTEM.triggered.connect(self.STEMMODE)
        self.ui.actionTEM.triggered.connect(self.TEMMODE)
        self.ui.actionFocal.triggered.connect(self.FOCMODE)
        self.ui.actionTilt.triggered.connect(self.TILTMODE)

        self.ui.actionSTEM.setCheckable(True)
        self.ui.actionTEM.setCheckable(True)
        self.ui.actionFocal.setCheckable(True)
        self.ui.actionTilt.setCheckable(True)
        
        self.ui.actionSTEM.setChecked(True)
        self.ui.actionFocal.setChecked(True)
        
        self.ui.inSte.returnPressed.connect(self.updateCount)
        self.ui.inMin.returnPressed.connect(self.updateCount)
        self.ui.inMax.returnPressed.connect(self.updateCount)
        self.ui.inNum.returnPressed.connect(self.updateStep)
        
        self.ui.usrButton.released.connect(self._saveUserSettings)
        self.ui.acqBtn.released.connect(self.onAcquire)
        self.ui.savBtn.released.connect(self.onSave)
        self.ui.aboBtn.released.connect(self.onAbort)
        self.ui.broBtn.released.connect(self.onBrowse)
        self.ui.usrBroBtn.released.connect(self.onBrowse)
        self.scene = QtGui.QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.graphicsView.fitInView(self.scene.itemsBoundingRect(),QtCore.Qt.KeepAspectRatio)
        #self.app.aboutToQuit.connect(self._saveAcqSettings())

        self.hotkeys()
    def onConnect(self):
        raise NotImplementedError
    def onAcquire(self):
        self.slipperyChange()
        self.getUsrAcqVals()
        self.ui.lblStatus.setText('Starting acquisition...')
    def onAbort(self):
        raise NotImplementedError
    def onSave(self):
        raise NotImplementedError    
    def updateProgressBar(self,i):
        if i == 0:
            self.ui.progressBar.setVisible(True)
            self.ui.progressBar.setMaximum((self.numDef*self.numPerDef))
        self.ui.progressBar.setValue(i+1)
        if i==(self.numDef*self.numPerDef)-1 or i == -1:
            self.ui.progressBar.setVisible(False)     
    @QtCore.Slot(ndarray)
    def postIteration(self,data):
        self.updateProgressBar(self.imageCount)
        self.imageCount+=1
        #self.updateView(QtCore.Qt.QString(data))
    def onBrowse(self):
        _dir = QtGui.QFileDialog.getExistingDirectory(self)
        if self.sender() == self.ui.broBtn:
            self.ui.inOutDir.setText(_dir)
        else:
            self.ui.inOutDir.setText(_dir)
            self.ui.inUsrOutDir.setText(_dir)            
    def checkDir(self, *args, **kwargs):       
        if os.path.isdir(self.ui.inOutDir.text()):
            color = '#c4df9b' # green
        else:
            color = '#f6989d' # red
        self.ui.inOutDir.setStyleSheet('QLineEdit { background-color: %s }' % color)   
    def checkBin(self, *args, **kwargs):  
        _maxBin = int(self.ui.inMaxBin.text())
        try:
            _bin = int(self.ui.inBin.text())     
            if _bin in self.binnings:
                color = '#c4df9b' # green
                self.bin = _bin
                self.updateInfo()
            else:
                color = '#f6989d' # red
            self.ui.inBin.setStyleSheet('QLineEdit { background-color: %s }' % color)
        except:
            pass
    def checkDef(self):
        if self.sender().text() != '':
            color = '#ffffff' # white
        else:
            color = '#f6989d' # red
        self.sender().setStyleSheet('QLineEdit { background-color: %s }' % color)
    #gets things that really only need to be pulled when saving
    def getSaveStuff(self):
        self.sampCmnt= self.ui.inSamInf.text()
        self.rName = self.ui.inResNam.text()
        self.comment = self.ui.inSerCom.text()
        self.fullName = self.ui.inOutDir.text()
        self.fullName += os.sep + self.ui.inFilPre.text
    def updateInfo(self): #updates acquisition info displayed on usrTab
        self.xDim = (self.maxBin)/self.bin
        self.yDim = (self.maxBin)/self.bin
        self.ui.lblXRes.setText("("+str(self.xDim)+",")
        self.ui.lblYRes.setText(str(self.yDim)+")")
        self.ui.outMaxX.setText('4096')
        self.ui.outMaxY.setText('4096')        
        self.ui.outCurBin.setText(str(self.bin))
        self.ui.outCurX.setText(str(self.xDim))
        self.ui.outCurY.setText(str(self.yDim))                          
    def getUsrAcqVals(self):
        #get the literals
        _filPre = self.ui.inFilPre.text() #file prefix (name)
        _filDir = self.ui.inOutDir.text() #file directory   
        _iniDef = self.ui.inMin.text()
        _lasDef = self.ui.inMax.text()
        _defSte = self.ui.inSte.text()
        _maxBin = self.ui.inMaxBin.text()
        _dweTim = self.ui.inTim.text()
        _setTim = self.ui.inSetTim.text()
        _numDef = self.ui.inNum.text()
        _numRep = self.ui.inNumRep.text()
        _bin = self.ui.inBin.text()
        
        _parStr = _iniDef+";"+_defSte+";"+_bin+";"+_dweTim #parameter string
        _filPre = _filPre.replace("$params",_parStr) #replace with parameters
        _filPre = _filPre.replace("$time",time.strftime("%Y-%m-%d@%H.%M.%S"))     
        
        self.filPre = _filPre
        self.fullName = _filDir + os.sep + _filPre
        self.numDef = int(_numDef)
        self.iniDef = float(_iniDef)
        self.lasDef = float(_lasDef)
        self.steDef = float(_defSte)
        self.maxBin = int(_maxBin)
        self.dweTim = float(_dweTim)*1e-6
        self.setTim = float(_setTim)
        self.bin = int(_bin)
        self.xDim = (self.maxBin)/self.bin
        self.yDim = (self.maxBin)/self.bin
        self.numPerDef = int(_numRep)
        self.dfList = self.DFLMaker()

        
        self._mstruct = _Series_Params('Foc',self.xDim,self.yDim,self.numPerDef,self.bin,
                                  self.dweTim,self.setTim,False)
        self._mstruct.setList(self.dfList,'True')
        self.updateInfo()
#         self.sld.SetRange(1,self.numDF) #update the slider
#         self.sld.SetValue(1)
        
        #self.checkUsrAcqVals()
    def sliderMoved(self):
        val = self.sender().value()
        print val
        self.updateView(self.series[val])
        self.ui.lblSlider.setText('Image %i of %i'%(val,self.numDef))
    def hotkeys(self):
        QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self, self.onAcquire)    
        QtGui.QShortcut(QtGui.QKeySequence("Esc"), self, self.onAbort)    
    def _createDefaultINI(self):
        c = ConfigParser.ConfigParser()
        c.add_section('Acquisition')
        c.set('Acquisition','_bin','2')
        c.set('Acquisition','_dwe','12')
        c.set('Acquisition','_npd','1')
        c.set('Acquisition','_set','1')
        
        c.add_section('User')
        c.set('User','_sam','')
        c.set('User','_dir','')
        c.set('User','_nam','')
        c.set('User','_ind','1')
        
        with open('config.ini','wb') as configfile:
            c.write(configfile)
        print '-----created default settings file-----'                
    def _saveAcqSettings(self):
        c = ConfigParser.RawConfigParser()
        c.read('config.ini')
        c.set('Acquisition','_bin',self.bin)
        c.set('Acquisition','_dwe',self.dweTim)
        c.set('Acquisition','_npd',self.numPerDef)
        c.set('Acquisition','_set',self.setTim)
        with open('config.ini','wb') as configfile:
            c.write(configfile)   
    def _saveUserSettings(self):
        c = ConfigParser.RawConfigParser()
        c.read('config.ini')
        c.set('User','_nam',self.ui.inResNam.text())
        c.set('User','_sam',self.ui.inSamInf.text())
        c.set('User','_dir',self.ui.inUsrOutDir.text())
        c.set('User','_ind',self.ui.inFilInd.text())
        with open('config.ini','wb') as configfile:
            c.write(configfile)
        print '-----updating cfg-----'       
    def _loadSettings(self):
        try:
            c = ConfigParser.ConfigParser()
            c.read('config.ini')
            print 'opened'
            self.usrNam = c.get('User','_nam')
            self.samInf = c.get('User','_sam')
            self.usrDir = c.get('User','_dir')
            self.intIndex = c.getint('User','_ind')

            self.bin = c.getint('Acquisition','_bin')
            self.dweTim = c.getfloat('Acquisition','_dwe')
            self.setTim = c.getfloat('Acquisition','_set')
            self.numPerDef = c.getint('Acquisition','_npd')
     
        except:
            self._createDefaultINI()
            self._loadSettings()       
    def slipperyChange(self):
        idf = float(self.ui.inMin.text())
        sdf = float(self.ui.inMax.text())
        stepdf = float(self.ui.inSte.text())
        numdf = int(self.ui.inNum.text())        
        if idf != self.iniDef or sdf != self.lasDef or stepdf !=self.steDef:
            self.updateCount()#pretend they did their job
        if numdf !=self.numDef:
            self.updateStep() #though we all know the truth           
    def updateCount(self):
        self.getUsrAcqVals()
        self.dfList = self.DFLMaker(self.acquirer.getIDF())
        self.updateSlider()    
    def updateSlider(self):
        self.ui.inNum.setText(str(self.numDef)) #update GUI
        self.ui.viewSlider.setMaximum(self.numDef) #update slider
        self.ui.progressBar.setMaximum(self.numDef)
        self.ui.viewSlider.setValue(1)
        self.ui.lblSlider.setText('Image 1 of %i'%(self.numDef,))        
    def updateView(self,npa):
        print type(npa)
        self.npa = npa
        self.images = [QtGui.QPixmap("../icons/favicon.png")]
        pixItem = QtGui.QImage(self.npa, self.xDim, self.yDim, QtGui.QImage.Format_RGB32)
        pixItem = pixItem.scaled(500,500,QtCore.Qt.KeepAspectRatio)
        #pixItem = QtGui.QGraphicsPixmapItem(Image.fromarray(npa))
        self.scene.clear()
        self.scene.addPixmap(QtGui.QPixmap.fromImage(pixItem))
    def updateStep(self,):
        self.getUsrAcqVals()
        self.updateSlider()
        a = float(self.iniDef)
        b=float(self.lasDef)
        c=float(self.numDef-1)
        self.steDef = abs(a-b)/c
        self.dfList = self.DFLMaker()
        self.ui.inSte.setText(str(self.steDef))    
    def DFLMaker(self,zeroDF=0):
        zeroDF*=1e9
        start, stop = zeroDF+self.iniDef, zeroDF+self.lasDef
        count = (stop-start)/self.steDef      
        DFList = arange(start,stop,self.steDef)
        DFList = DFList[:count]
        DFList = append(DFList,stop)
        self.numDef=len(DFList)
        self.dfList = list(DFList)
        print "------Defocus List Maker Diag------"
        printList = around(DFList,2)
        print("Zero defocus point: " +str(zeroDF))
        print('Defocus values: ');
        print printList      
        return DFList