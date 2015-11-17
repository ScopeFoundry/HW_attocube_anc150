from measurement import Measurement
from numpy import ndarray, round
import pyqtgraph as pg
import pythoncom
import win32com.client
from PySide import QtCore, QtGui
from random import choice, random, randint
from foundry_scope.logged_quantity import LQRange
from foundry_scope.measurement_components.LoopLockerDisk import LoopLocker,\
    STEMImage

TILT_SNAP_THRESHOLD = 5.0 
class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    series_paused = QtCore.Signal()

    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    def __init__(self,gui):
        self.debug = True
        self.paused = False
        self.workingList = [] #used to support pausing
        
        Measurement.__init__(self, gui)         
    def getHardware(self):
        self.hardware = self.gui.hardware_components['em_hardware']
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.initialDF = self.Proj.Defocus
        self.Stage = self._m.Stage
        
#         myCcdAcqParams = self.Acq.Cameras(0).AcqParams
#         myCcdAcqParams.Binning = self.hardware.current_binning.val
#         myCcdAcqParams.ExposureTime = self.hardware.current_exposure.val
#         myCcdAcqParams.ImageCorrection = win32com.client.constants.AcqImageCorrection_Unprocessed #this has to be unprocessed. Not sure if it affects data from the micoscope itself
#         myCcdAcqParams.ImageSize = win32com.client.constants.AcqImageSize_Full
#         self.Acq.Cameras(0).AcqParams = myCcdAcqParams
        
        if self.debug: print '-----DF:', str(self.initialDF),'m-----'
        if self.debug: print '-----end of getscope-----'
    def setup(self):
        self.display_update_period = 0.1 #seconds
        self.getHardware()
        self.dataLocker = LoopLocker(self.ui.seriesView,self.ui.floatingView) 
        self.setupUI() 
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        self.viewer = self.graph_layout.addViewBox()
        self.viewer.enableAutoRange()
    def setupUI(self):
        self.seriesModel = QtGui.QStandardItemModel()   
        self.floatingModel = QtGui.QStandardItemModel()     
  

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
                                name = 'num_tilts', initial = 10,
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
                        
            #measurement signals
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.progress.updated_value.connect(self.updateProgressBar)

            #LoopLocker signals
            self.dataLocker.diagnostic_info.connect(self.printDiag)
            self.dataLocker.display_request.connect(self.updateFigure)
            self.dataLocker.alpha_move_request.connect(self.ensureTiltChange)
            self.ui.inComment.returnPressed.connect(self.commentSaver)
            self.ui.inComment.textEdited.connect(self.cmntColor)
            
            self.tiltLQRange.updated_range.connect(self.updateListToolTip)
            #LoopLocker button connections
            self.ui.btnGoTo.released.connect(self.dataLocker.goToSelectedAlpha)
            self.ui.btnDiff.released.connect(self.dataLocker.diffItems)
            self.ui.btnS2F.released.connect(self.dataLocker.seriesToFloating)
            self.ui.btnF2S.released.connect(self.dataLocker.floatingToSeries) 
            self.ui.btnFlushPrimary.released.connect(self.dataLocker.flushSeries)
            self.ui.btnClearFloating.released.connect(self.dataLocker.clearFloating)
            self.ui.btnClearAll.released.connect(self.dataLocker.clearData)
            self.ui.btnDiscard.released.connect(self.dataLocker.discardItems)
            self.ui.btnAverage.released.connect(self.dataLocker.averageItems)
            self.ui.btnSaveAll.released.connect(self.dataLocker.saveAll)
            self.ui.btnSaveFloating.released.connect(self.dataLocker.saveFloating)
            self.ui.btnSavePrimary.released.connect(self.dataLocker.saveSeries)  
            
            #buttons
            self.ui.btnPreview.released.connect(self.preview)          
            self.ui.btnPreview_2.released.connect(self.preview)
            self.ui.btnAcq.released.connect(self.start)
            self.ui.btnPause.released.connect(self.pauseSeries)
            self.ui.btnAbo.released.connect(self.interrupt)   
            self.ui.btnMinTilt.released.connect(self.minTilt)     
            self.ui.btnMaxTilt.released.connect(self.maxTilt)
            self.ui.btnCustom1.released.connect(self.doubleClickChecker)
            self.ui.btnCustom2.released.connect(self.doubleClickChecker)
            
            self.doubleClickTimer = QtCore.QTimer()
            self.doubleClickTimer.setInterval(500)
            self.doubleClickTimer.setSingleShot(True)
            
            #bin stuff
            self.ui.buttonGroup.setId(self.ui.bin1,1)
            self.ui.buttonGroup.setId(self.ui.bin2,2)
            self.ui.buttonGroup.setId(self.ui.bin4,4)  
            self.ui.buttonGroup.setId(self.ui.bin8,8)
            self.ui.buttonGroup.buttonReleased[int].connect(self.binChanged)
            self.ui.buttonGroup.button(self.hardware.current_binning.val).setChecked(True)
            self.binChanged(self.ui.buttonGroup.checkedId())
            #hardware LQs
            self.hardware.current_dwell.connect_bidir_to_widget(self.ui.expBox)
            self.hardware.current_defocus.connect_bidir_to_widget(self.ui.defBox)
            self.hardware.current_tilt.connect_bidir_to_widget(self.ui.alphaBox)
            
            #measurement LQs
            self.num_tilts.connect_bidir_to_widget(self.ui.numBox)
            self.step_tilt.connect_bidir_to_widget(self.ui.steBox)
            self.minimum_tilt.connect_bidir_to_widget(self.ui.minBox)
            self.maximum_tilt.connect_bidir_to_widget(self.ui.maxBox)
            self.num_repeats.connect_bidir_to_widget(self.ui.repBox)
            

        except Exception as err: 
            print "EM_Tomography: could not connect to custom main GUI", err
    def cmntColor(self):
        if self.sender().text() == '':
            color = '#ffffff' # white
        else:
            color = '#f6989d' # red
        self.sender().setStyleSheet('QLineEdit { background-color: %s }' % color)
    def updateProgressBar(self,num):
        self.ui.progressBar.setValue(num)
    def updateListToolTip(self,data = None):
        if data is None:
            self.ui.btnAcq.setToolTip(str(self.tiltLQRange.array))
            self.ui.btnPause.setToolTip(str(self.tiltLQRange.array))
        else: 
            self.ui.btnAcq.setToolTip(str(data))
            self.ui.btnPause.setToolTip(str(data))
    def doubleClickChecker(self):
        if  not self.doubleClickTimer.isActive():
            self.doubleClickTimer.start()
            return
        if self.doubleClickTimer.isActive() : 
            print "DoubleClick"
            self.doubleClickTimer.stop()
            self.doDoubleClickAction()
    def commentSaver(self):
        self.sender().setStyleSheet('QLineEdit { background-color: %s }' % '#c4df9b')
        cmnt = self.ui.inComment.text()
        self.dataLocker.setSelectedComments(cmnt)
    def pauseSeries(self):
        if not self.paused:
            self.paused = True
            self.toggleUI(True)
            self.updateListToolTip(self.workingList)
        else:
            self.ui.btnAcq.released.emit()       
    def doDoubleClickAction(self):
        print "Double Click on pushButton detected"        
    def printDiag(self,junk):
        print junk
    def dummyStuff(self):
        '''temporary, fills some data boxes until later implementation'''
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
    def toggleUI(self,val):
        self.ui.btnAcq.setEnabled(val) 
        self.ui.btnMaxTilt.setEnabled(val) 
        self.ui.btnMinTilt.setEnabled(val) 
        self.ui.btnPreview_2.setEnabled(val)
        self.ui.btnCustom1.setEnabled(val)
        self.ui.btnCustom2.setEnabled(val)
        self.ui.btnAddCustom.setEnabled(val) 

        self.ui.lockerWidget.setEnabled(val)
        self.ui.seriesBox.setEnabled(val)
        self.ui.statusBox.setEnabled(val)
                
        if val: self.ui.progressBar.hide()
        else: self.ui.progressBar.show()


    def preview(self):
#         try:
            print self.tiltLQRange.array
            acquiredImageSet = self.hardware.acquire()      
            itr = acquiredImageSet(0)
            self.TIA = win32com.client.Dispatch("ESVision.Application")
            window = self.TIA.ActiveDisplayWindow()
            img = window.FindDisplay(window.DisplayNames(0)); #returns an image display object
            units = img.SpatialUnit.unitstring
            units = ' '+units 
            calX = img.image.calibration.deltaX #returns the x calibration
            calY = img.image.calibration.deltaY
            calibration = (calX,calY,units,)
            
            stemImage = STEMImage(itr)
            stemImage.setCalibration(calibration)
            stemImage.binning = self.hardware.current_binning.val
            stemImage.defocus = self.hardware.current_defocus.val
            stemImage.dwellTime = self.hardware.current_dwell.val
            stemImage.stageAlpha = self.hardware.current_tilt.val       
            
            self.dataLocker.addToFloating(stemImage)
#         except Exception as err:
#             print self.name, "error:", err
    def _run(self):
#         try:
        if not hasattr(self,'_m') or self._m == None: self.getScope()
        changed = False
        self.prev_tiltLQRange = None
        if self.prev_tiltLQRange==None or self.prev_tiltLQRange!=self.tiltLQRange.array:
            self.prev_tiltLQRange=self.tiltLQRange.array
            changed = True
        
        if not self.workingList or changed:
            self.workingList = list(self.tiltLQRange.array[::-1])
        self.paused = False
        totalImages = len(self.workingList)*self.num_repeats.val
        imagePct = int((100.0/totalImages))
        imagesTaken = 0
        self.set_progress(0)
        self.toggleUI(False)
        while self.workingList:
            if self.debug: print len(self.workingList)
            tiltVal = float(self.workingList.pop())
            self.hardware.current_tilt.update_value(tiltVal)
            for x in range(self.num_repeats.val):
                acquiredImageSet = self.Acq.AcquireImages()      
                itr = acquiredImageSet(0)
                self.TIA = win32com.client.Dispatch("ESVision.Application")
                window = self.TIA.ActiveDisplayWindow()
                img = window.FindDisplay(window.DisplayNames(0)); #returns an image display object
                units = img.SpatialUnit.unitstring 
                units = ' '+units 
                calX = img.image.calibration.deltaX #returns the x calibration
                calY = img.image.calibration.deltaY
                calibration = (calX,calY,units,)
                
                stemImage = STEMImage(itr)
                stemImage.setCalibration(calibration)
                stemImage.binning = self.hardware.current_binning.val
                stemImage.defocus = self.hardware.current_defocus.val
                stemImage.dwellTime = self.hardware.current_dwell.val
                stemImage.stageAlpha = self.hardware.current_tilt.val       
                
                self.dataLocker.addToSeries(stemImage)
                imagesTaken += 1
                self.set_progress(imagesTaken*imagePct)
                if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----'
            if self.paused: break

#         except Exception as err:
#             print self.name, "error:", err
    def postAcquisition(self):
        self.set_progress(0)
        self.toggleUI(True)
        print '-----postacq-----'
    def updateFigure(self,stemImage):
        data = stemImage.data
        print data
        self.ui.lblXYRes_details.setText('('+str(stemImage.width)+', '+
                                         str(stemImage.height)+')')
        self.ui.lblX_details.setText(str(stemImage.stageX)+' um')
        self.ui.lblY_details.setText(str(stemImage.stageY)+' um')
        self.ui.lblZ_details.setText(str(stemImage.stageZ)+' um')
        self.ui.lblAlpha_details.setText(str(stemImage.stageAlpha)+' deg')
        self.ui.lblBeta_details.setText(str(stemImage.stageBeta)+' deg')
        self.ui.lblTime_details.setText(str(stemImage.time))
        self.ui.lblDef_details.setText(str(stemImage.defocus)+' nm')
        self.ui.lblDwell_details.setText(str(stemImage.dwellTime)+' us')
        self.ui.inComment.setText(str(stemImage.comment))
        self.ui.inComment.setStyleSheet('QLineEdit { background-color: %s }' % '#ffffff')
        self.ui.lblXCal_details.setText(str(stemImage.xCal)+str(stemImage.calUnits))
        self.ui.lblYCal_details.setText(str(stemImage.yCal)+str(stemImage.calUnits))

        self.viewer.clear()
        self.viewer.addItem(pg.ImageItem(data))
        self.update_display()

        self.dummyStuff()
        print '-----postiter-----'
    def minTilt(self):
        self.ensureTiltChange(self.minimum_tilt.val)
        print '-----min tilt-----'
    def maxTilt(self):
        self.ensureTiltChange(self.maximum_tilt.val)
        print '-----max tilt-----'
    def closeEvent(self,event):
        self.dataLocker.closeFiles()
        event.accept()  
    def ensureTiltChange(self,desiredTilt):
        if abs(self.hardware.current_tilt.val-desiredTilt)>TILT_SNAP_THRESHOLD:
            reply = QtGui.QMessageBox.question(None, 
                        "Large Change", 
                        "Current: %s deg\nDesired: %s deg\n Make Change?" % (self.hardware.current_tilt.val,desiredTilt,),
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.hardware.current_tilt.update_value(desiredTilt)
            else: pass
        else: 
            self.hardware.current_tilt.update_value(desiredTilt)
    def binChanged(self,btnId):
        if btnId in self.hardware.getBinnings():
            res = 2048/btnId
            self.xRes = res
            self.yRes = res
            self.ui.lblXYRes.setText('('+str(res)+", "+str(res)+')')
            self.hardware.current_binning.update_value(new_val=btnId)
    def update_display(self):        
        self.gui.app.processEvents()


