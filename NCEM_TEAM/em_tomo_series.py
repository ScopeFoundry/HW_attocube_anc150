from measurement import Measurement
from numpy import round
import pyqtgraph as pg
import pythoncom
import win32com.client
from PySide import QtGui
from random import choice, random
from foundry_scope.logged_quantity import LQRange
from time import time, sleep
from foundry_scope.measurement_components.LoopLockerDisk import LoopLocker,\
    STEMImage
import threading

class EMTomographySeries(Measurement):
    tilt_snap_threshold = 5.0 #deg, if a change exceeds this, user must confirm

    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    bootTime = time() #used to generate unique imgIDs for each acquired image

    def __init__(self,gui,debug = True):
        self.debug = debug
        Measurement.__init__(self, gui) #calls setup()
        self.paused,self.workingList = False,[] #pausing variables
        self.aborted = True #False when acquiring, True when idle
    def getHardware(self):
        self.hardware = self.gui.hardware_components['em_hardware']
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.Ill = self._m.Illumination
        self.initialDF = self.Proj.Defocus
        self.Stage = self._m.Stage   
        if self.debug: print '-----DF:', str(self.initialDF),'m-----'
        if self.debug: print '-----end of getscope-----'     
    def setup(self):
        self.display_update_period = 0.1 #seconds
        self.getHardware()
        self.dataLocker = LoopLocker(self.ui.seriesView,self.ui.floatingView) #create a looplocker that uses these  treewidgets
        self.setupUI()   
        self.customButtonClass = CustomButtonSettings()
    def setup_figure(self):
        if hasattr(self, 'graphicsLayout'):
            self.graphicsLayout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graphicsLayout
        self.graphicsLayout=pg.GraphicsLayoutWidget(border=(100,100,100)) #GraphicsView with a single GraphicsLayout as its central item
        self.ui.plot_groupBox.layout().addWidget(self.graphicsLayout)
        self.viewBox = self.graphicsLayout.addViewBox()
        self.graphicsLayout.setCentralItem(self.viewBox)
        self.viewBox.invertY(True) #must be done
        self.viewBox.enableAutoRange(self.viewBox.XYAxes)
    def setupUI(self):
        #tilt series LQs (main tomo stuff)
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
        self.tiltLQRange = LQRange(self.minimum_tilt,self.maximum_tilt,
                                   self.step_tilt,self.num_tilts)
        
        #STEM Rotation series LQs (can be done at each tilt)
        self.rot_series_bool = self.add_logged_quantity(
                                name = 'rot_series_bool', initial = False,
                                dtype = bool, fmt="%r", ro=False)
        self.minimum_rotation = self.add_logged_quantity(
                                name = 'minimum_rotation', initial = -80.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-360.0,vmax=360.0)
        self.maximum_rotation = self.add_logged_quantity(
                                name = 'maximum_rotation', initial = 80.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-360.0,vmax=360.0)
        self.step_rotation = self.add_logged_quantity(
                                name = 'step_rotation', initial = 6.0,
                                dtype = float, fmt="%e", ro=False,
                                unit='deg', vmin=-360.0,vmax=360.0)
        self.num_rotations = self.add_logged_quantity(
                                name = 'num_rotations', initial = 10,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=2,vmax=160)
        self.rotationLQRange = LQRange(self.minimum_rotation,self.maximum_rotation,
                                   self.step_rotation,self.num_rotations)
        #cur_vi_rot: used to rotate the display [not implemented]
        self.current_view_rotation = self.add_logged_quantity(
                                name = 'current_view_rotation', initial = 0.0,
                                dtype = float, fmt="%e", ro=False,
                                unit=None, vmin=0,vmax=360)
        
        #num_repeats: repeat each image X times; default 1
        self.num_repeats = self.add_logged_quantity(
                                name = 'num_repeats', initial = 1,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=1,vmax=30)
        
        
        self.auto_pause = self.add_logged_quantity(name = 'auto_pause', initial = False,
                                dtype = bool, fmt="%r", ro=False)
        
        try:
            self.ui.setWindowTitle('NCEM Tomography Tool')
                        
            #measurement signals
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.tiltLQRange.updated_range.connect(self.updateListToolTip)
            self.progress.updated_value.connect(self.updateProgressBar)
            self.ui.progressBar.hide()

            #LoopLocker signals
            self.dataLocker.diagnostic_info.connect(self.printDiag)
            self.dataLocker.display_request.connect(self.updateFigure)
            self.dataLocker.alpha_move_request.connect(self.ensureTiltChange)
            self.ui.inComment.returnPressed.connect(self.saveCommentsToSelected)
            self.ui.inComment.textEdited.connect(self.cmntColor)    
            
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
            self.ui.btnSaveAll.released.connect(self.dataLocker.saveSeriesAndFloating)
            self.ui.btnSaveFloating.released.connect(self.dataLocker.saveFloating)
            self.ui.btnSavePrimary.released.connect(self.dataLocker.saveSeries)  
            
            #buttons
            self.ui.btnPreview.released.connect(self.preview)          
            self.ui.btnPreview_2.released.connect(self.preview)
            self.ui.btnAcq.released.connect(self.start)
            self.ui.btnPause.released.connect(self.pauseSeries)
            self.ui.btnAbo.released.connect(self.abortSeries)
            self.rot_series_bool.updated_value.connect(self.grayRotTab)
            
            self.ui.editCustom1.released.connect(self.setupCustomButton)
            self.ui.editCustom2.released.connect(self.setupCustomButton)
            self.ui.editCustom3.released.connect(self.setupCustomButton)
            
            self.ui.btnCustom1.released.connect(self.customPreview1)
            self.ui.btnCustom2.released.connect(self.customPreview2)
            self.ui.btnCustom3.released.connect(self.customPreview3)
            
            #bin stuff
            self.ui.buttonGroup.setId(self.ui.bin1,1)
            self.ui.buttonGroup.setId(self.ui.bin2,2)
            self.ui.buttonGroup.setId(self.ui.bin4,4)  
            self.ui.buttonGroup.setId(self.ui.bin8,8)
            self.ui.buttonGroup.buttonReleased[int].connect(self.binButtonClicked)
            self.ui.buttonGroup.button(self.hardware.current_binning.val).setChecked(True)
            self.updateResolutionStatus()
            
            #hardware LQs
            self.hardware.current_dwell.connect_bidir_to_widget(self.ui.expBox)
            self.hardware.current_defocus.connect_bidir_to_widget(self.ui.defBox)
            self.hardware.current_tilt.connect_bidir_to_widget(self.ui.alphaBox)
            self.hardware.current_stem_rotation.connect_bidir_to_widget(self.ui.stemRotBox)
            self.hardware.current_stem_rotation.updated_value.connect(self.updateRotationLabel)
            self.updateRotationLabel()
            
            
            #measurement LQs
            self.auto_pause.connect_bidir_to_widget(self.ui.apCheckbox)
            self.rot_series_bool.connect_bidir_to_widget(self.ui.rotCheckbox)
            self.num_tilts.connect_bidir_to_widget(self.ui.numBoxTilt)
            self.step_tilt.connect_bidir_to_widget(self.ui.steBoxTilt)
            self.minimum_tilt.connect_bidir_to_widget(self.ui.minBoxTilt)
            self.maximum_tilt.connect_bidir_to_widget(self.ui.maxBoxTilt)
            
            self.num_rotations.connect_bidir_to_widget(self.ui.numBoxRot)
            self.step_rotation.connect_bidir_to_widget(self.ui.steBoxRot)
            self.minimum_rotation.connect_bidir_to_widget(self.ui.minBoxRot)
            self.maximum_rotation.connect_bidir_to_widget(self.ui.maxBoxRot)
            self.num_repeats.connect_bidir_to_widget(self.ui.repBox)
            
            self.num_repeats.connect_bidir_to_widget(self.ui.repBox)


        except Exception as err: 
            print "EM_Tomography: error in setupUI block\n\
            Most likely cause: change in .ui widgets,", err
    def cmntColor(self): #comment box is white if empty, red if unsaved
        if self.sender().text() == '': color = '#ffffff' # white
        else: color = '#f6989d' # red
        self.sender().setStyleSheet('QLineEdit { background-color: %s }' % color)
    def setupCustomButton(self):
        sender = self.sender().objectName()
        self.setCustomButtonBin(sender)
        self.setCustomButtonDwell(sender)
    def customPreview1(self):
        prevDwell = self.hardware.current_dwell.val #.oldval not working?
        prevBin = self.hardware.current_binning.val
        self.hardware.current_binning.update_value(self.customButtonClass.bin1)
        self.hardware.current_dwell.update_value(self.customButtonClass.dwell1)
        self.preview()
        self.hardware.current_binning.update_value(prevBin)
        self.hardware.current_dwell.update_value(prevDwell)
    def customPreview2(self):
        prevDwell = self.hardware.current_dwell.val
        prevBin = self.hardware.current_binning.val
        self.hardware.current_binning.update_value(self.customButtonClass.bin2)
        self.hardware.current_dwell.update_value(self.customButtonClass.dwell2)
        self.preview()
        self.hardware.current_binning.update_value(prevBin)
        self.hardware.current_dwell.update_value(prevDwell)
    def customPreview3(self):
        prevDwell = self.hardware.current_dwell.val
        prevBin = self.hardware.current_binning.val
        self.hardware.current_binning.update_value(self.customButtonClass.bin3)
        self.hardware.current_dwell.update_value(self.customButtonClass.dwell3)
        self.preview()
        self.hardware.current_binning.update_value(prevBin)
        self.hardware.current_dwell.update_value(prevDwell)
    def setCustomButtonBin(self,sender):
        if sender == 'editCustom1':
            binning, ok = QtGui.QInputDialog.getInt(None, "Enter Binning", 
    "Custom Binning:")
            if ok:
                if binning in self.hardware.getBinnings():
                    self.customButtonClass.bin1 = binning
                else:
                    self.setCustomButtonBin(sender)
        if sender == 'editCustom2':
            binning, ok = QtGui.QInputDialog.getInt(None, "Enter Binning", 
    "Custom Binning:")
            if ok:
                if binning in self.hardware.getBinnings():
                    self.customButtonClass.bin2 = binning
                else:
                    self.setCustomButtonBin(sender)
                    
        if sender == 'editCustom3':
            binning, ok = QtGui.QInputDialog.getInt(None, "Enter Binning", 
    "Custom Binning:")
            if ok:
                if binning in self.hardware.getBinnings():
                    self.customButtonClass.bin3 = binning
                else:
                    self.setCustomButtonBin(sender)
    def setCustomButtonDwell(self,sender):
        if sender == 'editCustom1':
            dwell, ok = QtGui.QInputDialog.getDouble(None, "Enter Dwell Time", 
    "Custom Dwell Time (us):")
            if ok:
                if dwell > 2.0:
                    self.customButtonClass.dwell1 = dwell
                else:
                    self.setCustomButtonDwell(sender)
        if sender == 'editCustom2':
            dwell, ok = QtGui.QInputDialog.getDouble(None, "Enter Dwell Time", 
    "Custom Dwell Time (us):")
            if ok:
                if dwell > 2.0:
                    self.customButtonClass.dwell2 = dwell
                else:
                    self.setCustomButtonDwell(sender)
                    
        if sender == 'editCustom3':
            dwell, ok = QtGui.QInputDialog.getDouble(None, "Enter Dwell Time", 
    "Custom Dwell Time (us):")
            if ok:
                if dwell > 2.0:
                    self.customButtonClass.dwell3 = dwell
                else:
                    self.setCustomButtonDwell(sender)
    def updateProgressBar(self,pct):
        self.ui.progressBar.setValue(pct)
    def updateListToolTip(self,data = None):
        ############
        # Hovering pause or start will display the list of tilt values to be acquired
        ############
        if data is None:
            self.ui.btnAcq.setToolTip(str(self.tiltLQRange.array))
            self.ui.btnPause.setToolTip(str(self.tiltLQRange.array))
        else: 
            self.ui.btnAcq.setToolTip(str(data))
            self.ui.btnPause.setToolTip(str(data))
    def saveCommentsToSelected(self):
        cmnt = self.ui.inComment.text()
        self.dataLocker.setSelectedComments(cmnt)
        #make the textEdit green
        self.sender().setStyleSheet('QLineEdit { background-color: %s }' % '#c4df9b')
    def pauseSeries(self):
        if not self.paused:
            self.paused = True
            self.ui.btnAcq.setEnabled(False)
            self.ui.btnPause.setText('Resume')
            self.updateListToolTip(self.workingList)
        else: #let 'Pause' function as 'Resume'
            self.ui.btnAcq.setEnabled(True)
            self.ui.btnPause.setText('Pause')
            self.ui.btnAcq.released.emit() #resumes acquisition
    def abortSeries(self):
        if not self.aborted: 
            if self.paused:
                self.paused = False #no longer paused
                self.aborted = True #return to idle state
                self.ui.btnPause.setText('Pause') #from 'Resume'
                #self.ui.btnPause.setEnabled(True) #ungrey the pause button
                self.grayUI(False)
            else:
                self.aborted = True
                self.grayUI(False)
                self.interrupt()
            self.workingList = list(self.tiltLQRange.array[::-1])

    def printDiag(self,junk): #allows LoopLocker to print stuff
        print junk
    def updateRotationLabel(self): #updates 'relative to: XXXX'
        self.ui.lblRot_RotationTab.setText(str(self.hardware.current_stem_rotation.val))
    def updateDriftLabel(self): #fakes the drift magnitude
        x = round(random(),2)
        y = round(random(),2)
        lblx = choice(['','-'])
        lbly = choice(['','-'])
        self.ui.lblXYShift.setText('('+lblx+str(x)+'um, '+lbly+str(y)+'um)')
    def grayUI(self,val,preview=False): #grays most stuff while acquiring a series
        val = not val
        self.ui.btnAcq.setEnabled(val) 
        self.ui.btnPreview_2.setEnabled(val)
        self.ui.btnCustom1.setEnabled(val)
        self.ui.btnCustom2.setEnabled(val)
        self.ui.btnCustom3.setEnabled(val)
        self.ui.editCustom1.setEnabled(val)
        self.ui.editCustom2.setEnabled(val)
        self.ui.editCustom3.setEnabled(val)
        

        self.ui.lockerWidget.setEnabled(val)
        self.ui.ParamsBox.setEnabled(val)
        self.ui.StatusBox.setEnabled(val)

        if self.paused and val:
            self.ui.btnAcq.setEnabled(not val)
        
        if preview:
            self.ui.btnAcq.setEnabled(val)
            self.ui.btnAbo.setEnabled(val)
            self.ui.apCheckbox.setEnabled(val)
            self.ui.btnPause.setEnabled(val)
            
            #if it's a single-image preview
            if val:
                self.previewBar() #does a pretty animation if we're previewing
        
        #make the bar visible or not        
        if val: 
            self.ui.progressBar.show()#hide()
        else: self.ui.progressBar.show()
    def previewBar(self):
            est = (self.res*self.res*self.hardware.current_dwell.val)+0.2
            startTime = time()
            while True:
                sleep(0.02)
                self.set_progress((time()-startTime)/est)
                QtGui.qApp.processEvents()

#             timer = QTimer
#             self.ui.progressBar.connect(timer,SIGNAL("timeout()"),self.ui.progressBar,Slot("increaseValue()"))
#             timer.start(est)
        
    def grayRotTab(self): #grays rotation tab doing one
        self.ui.rotationTab.setEnabled(self.rot_series_bool.val)
    def preview(self):
        self.grayUI(True,preview=True)
        self.update_display()
        print 'starting thread'
        self.prevThread = threading.Thread(target=self._previewThread())
        print 'starting thread'
        self.prevThread.start()
    def _previewThread(self):
        #         try:
            acquiredImageSet = self.hardware.acquire()      
            itr = acquiredImageSet(0)
            self.TIA = win32com.client.Dispatch("ESVision.Application")
            window = self.TIA.ActiveDisplayWindow()
            img = window.FindDisplay(window.DisplayNames(0)); #returns an image display object
            units = img.SpatialUnit.unitstring
            units = ' '+units 
            
            calX = img.image.calibration.deltaX*1e9 #returns the x calibration
            calY = img.image.calibration.deltaY*1e9
            calibration = (calX,calY,units,)
            
            stemImage = STEMImage(itr)
            stemImage.setCalibration(calibration)
            stemImage.ID = str(round(time() - self.bootTime,2))
            stemImage.stemRotation = self.hardware.current_stem_rotation.val
            stemImage.binning = self.hardware.current_binning.val
            stemImage.defocus = self.hardware.current_defocus.val
            stemImage.dwellTime = self.hardware.current_dwell.val 
            stemImage.stageAlpha = self.hardware.current_tilt.val       
            
            self.dataLocker.addToFloating(stemImage)
            self.grayUI(False,preview=True)
#         except Exception as err:
#             print self.name, "error:", err
    def _run(self):
        #try:
        if not hasattr(self,'_m') or self._m == None: self.getScope()
        
        tiltListChanged = False #create variable        
        if not hasattr(self, 'prev_tiltLQRange'):
            self.prev_tiltLQRange=self.tiltLQRange.array

        #if the tiltLQRange has been changed
        if list(self.prev_tiltLQRange)!=list(self.tiltLQRange.array): 
            self.prev_tiltLQRange=self.tiltLQRange.array
            tiltListChanged = True

        #if workingList has been exhausted or the user has updated tiltLQRange
        if len(self.workingList)==0 or tiltListChanged: 
            self.workingList = list(self.tiltLQRange.array[::-1])

        self.paused, self.aborted = False, False
        
        #these lines are for progress bar/percentage stuff
        totalImages = len(self.workingList)*self.num_repeats.val
        if self.rot_series_bool.val: totalImages *= len(self.rotationLQRange.array)
        imagePct, imagesTaken = int((100.0/totalImages)), 0 

        self.set_progress(0) #progress bar
        self.grayUI(True) #gray stuff that shouldn't be touched during acq
        
        while self.workingList: 
            if self.debug: print len(self.workingList)
            tiltVal = round(float(self.workingList.pop()),2)
            self.hardware.current_tilt.update_value(tiltVal)
            if self.rot_series_bool.val:
                if self.debug: print 'list of rots:', self.rotationLQRange.array
                for i in self.rotationLQRange.array:
                    i = round(i,2)
                    self.hardware.current_stem_rotation.update_value(i,update_hardware=False,send_signal=False)
                    self.Ill.StemRotation = i
                    for _ in range(self.num_repeats.val):
                        self.dataLocker.addToSeries(self.acquireSTEMImage())
                        imagesTaken += 1
                        self.set_progress(imagesTaken*imagePct)
                        if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----'
                        if self.auto_pause.val: self.pauseSeries()
                if self.paused: break
                if self.aborted: break
            else:
                for _ in range(self.num_repeats.val):
                    self.dataLocker.addToSeries(self.acquireSTEMImage())
                    imagesTaken += 1
                    self.set_progress(imagesTaken*imagePct)
                    if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----'
                    if self.auto_pause.val: self.pauseSeries()
                if self.paused: break
                if self.aborted: break
        #except Exception as err:
            #print self.name, "error:", err
    
    def acquireSTEMImage(self): #acquire image and calibration, return EMImage
        acquiredImageSet = self.Acq.AcquireImages()      
        itr = acquiredImageSet(0)
        self.TIA = win32com.client.Dispatch("ESVision.Application")
        window = self.TIA.ActiveDisplayWindow()
        img = window.FindDisplay(window.DisplayNames(0))
        units = img.SpatialUnit.unitstring 
        units = ' '+units 
        calX = img.image.calibration.deltaX*1e9 #x calibration
        calY = img.image.calibration.deltaY*1e9 #y calibration
        calibration = (calX,calY,units,)
        
        stemImage = STEMImage(itr)
        stemImage.setCalibration(calibration)
        stemImage.ID = str((round(time() - self.bootTime,2))*100)
        stemImage.stemRotation = self.hardware.current_stem_rotation.val
        stemImage.binning = self.hardware.current_binning.val
        stemImage.defocus = self.hardware.current_defocus.val
        stemImage.dwellTime = self.hardware.current_dwell.val
        stemImage.stageAlpha = self.hardware.current_tilt.val       
        
        return stemImage
    def postAcquisition(self): #runs in main thread after acquisition is finished
        self.set_progress(0)
        self.grayUI(False)
        if not self.workingList:
            self.updateListToolTip()
        print '-----postacq-----'
    def updateFigure(self,stemImage): 
        if self.debug: print stemImage.data
        
        #update information groupbox above view
        self.ui.lblXYRes_details.setText('('+str(stemImage.width)+', '+
                                         str(stemImage.height)+')')
        self.ui.lblID_details.setText(str(stemImage.ID))
        self.ui.lblX_details.setText(str(stemImage.stageX)+' um')
        self.ui.lblY_details.setText(str(stemImage.stageY)+' um')
        self.ui.lblZ_details.setText(str(stemImage.stageZ)+' um')
        self.ui.lblAlpha_details.setText(str(stemImage.stageAlpha)+' deg')
        self.ui.lblBeta_details.setText(str(stemImage.stageBeta)+' deg')
        self.ui.lblTime_details.setText(str(stemImage.time))
        self.ui.lblDef_details.setText(str(stemImage.defocus)+' nm')
        self.ui.lblRot_details.setText(str(stemImage.stemRotation)+' deg')
        self.ui.lblDwell_details.setText(str(stemImage.dwellTime)+' us')
        self.ui.inComment.setText(str(stemImage.comment))
        self.ui.inComment.setStyleSheet('QLineEdit { background-color: %s }' % '#ffffff')
        self.ui.lblXCal_details.setText(str(round(stemImage.xCal,2))
                                        +str(stemImage.calUnits))
        self.ui.lblYCal_details.setText(str(round(stemImage.yCal,2))
                                        +str(stemImage.calUnits))
        
        #-----untested draft for rotating the view in step with stem coils
        #self.viewBox.rotate(-(self.current_view_rotation.val))
        #self.current_view_rotation.update_value(stemImage.stemRotation)
        #self.viewBox.rotate(self.current_view_rotation.val)
        
        #update displayed image
        self.viewBox.clear()
        self.viewBox.addItem(pg.ImageItem(stemImage.data))
        self.update_display()
        self.updateDriftLabel() #fills Status Box with false values
        if self.debug: print '-----display updated with new image-----'
    def closeEvent(self,event): #sure the LoopLocker files are saved; otherwise caches may not be flushed
        self.dataLocker.saveSeriesAndFloating()
    def ensureTiltChange(self,desiredTilt): 
        ############
        #if a tilt change is made by a call to this function, the user must confirm if
        # the requested shift magnitude is greater than tilt_snap_threshold
        ############
        if abs(self.hardware.current_tilt.val-desiredTilt)>self.tilt_snap_threshold:
            reply = QtGui.QMessageBox.question(None, 
                        "Large Change", 
                        "Current: %s deg\nDesired: %s deg\n Make Change?" % (self.hardware.current_tilt.val,desiredTilt,),
                        QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.hardware.current_tilt.update_value(desiredTilt)
        else: 
            self.hardware.current_tilt.update_value(desiredTilt)
    def binButtonClicked(self,btnId): #if a binning radio button is clicked
        if btnId in self.hardware.getBinnings(): #TEM only has 1,2,4
            self.hardware.current_binning.update_value(new_val=btnId)
            self.updateResolutionStatus()
    def updateResolutionStatus(self):
        self.res = 2048/self.hardware.current_binning.val
        self.ui.lblXYRes.setText('('+str(self.res)+", "+str(self.res)+')')
    def update_display(self):        
        self.gui.app.processEvents()
    
class CustomButtonSettings():
    bin1 = 1
    bin2 = 2
    bin3 = 8
    
    dwell1 = 12.0
    dwell2 = 12.0
    dwell3 = 12.0
    
    


