from measurement import Measurement
from numpy import ndarray, round
import pyqtgraph as pg
import pythoncom
import win32com.client
from PySide import QtCore, QtGui
from random import choice, random, randint
from foundry_scope.logged_quantity import LQRange
from time import time
from foundry_scope.measurement_components.LoopLockerDisk import LoopLocker,\
    STEMImage

class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    series_paused = QtCore.Signal()
    tilt_snap_threshold = 5.0 #deg, if a change exceeds this, user must confirm


    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    bootTime = time()
    def __init__(self,gui):
        Measurement.__init__(self, gui) #calls setup()
        self.debug = True
        self.paused,self.workingList = False, [] #pausing  
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
        self.dataLocker = LoopLocker(self.ui.seriesView,self.ui.floatingView) 
        self.setupUI()     
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        self.viewer = self.graph_layout.addViewBox()
        self.graph_layout.setCentralItem(self.viewer)
        self.viewer.invertY(True)
        self.viewer.enableAutoRange(self.viewer.XYAxes)
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
                                name = 'num_tilts', initial = 10,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=2,vmax=160)
        
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
        self.num_repeats = self.add_logged_quantity(
                                name = 'num_repeats', initial = 1,
                                dtype = int, fmt="%e", ro=False,
                                unit=None, vmin=1,vmax=30)
        self.rotationLQRange = LQRange(self.minimum_rotation,self.maximum_rotation,
                                   self.step_rotation,self.num_rotations)
        
        self.tiltLQRange = LQRange(self.minimum_tilt,self.maximum_tilt,
                                   self.step_tilt,self.num_tilts)
        
        self.auto_pause = self.add_logged_quantity(
                                name = 'auto_pause', initial = False,
                                dtype = bool, fmt="%r", ro=False)
        self.rot_series_bool = self.add_logged_quantity(
                                name = 'rot_series_bool', initial = False,
                                dtype = bool, fmt="%r", ro=False)
        
        self.current_view_rotation = self.add_logged_quantity(
                                name = 'current_view_rotation', initial = 0.0,
                                dtype = float, fmt="%e", ro=False,
                                unit=None, vmin=0,vmax=360)
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
            self.ui.inComment.returnPressed.connect(self.commentSaver)
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
            self.ui.btnSaveAll.released.connect(self.dataLocker.saveAll)
            self.ui.btnSaveFloating.released.connect(self.dataLocker.saveFloating)
            self.ui.btnSavePrimary.released.connect(self.dataLocker.saveSeries)  
            
            #buttons
            self.ui.btnPreview.released.connect(self.preview)          
            self.ui.btnPreview_2.released.connect(self.preview)
            self.ui.btnAcq.released.connect(self.start)
            self.ui.btnPause.released.connect(self.pauseSeries)
            self.ui.btnAbo.released.connect(self.interrupt)
            self.rot_series_bool.updated_value.connect(self.grayRotTab)
            
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
            print "EM_Tomography: error in setupUI block", err
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
    def updateRotationLabel(self):
        self.ui.lblStemRot2.setText(str(self.hardware.current_stem_rotation.val))
    def dummyStuff(self):
        '''temporary, fills some data boxes until later implementation'''
        x = round(random(),2)
        y = round(random(),2)
        lblx = choice(['','-'])
        lbly = choice(['','-'])
        self.ui.lblXYShift.setText('('+lblx+str(x)+'um, '+lbly+str(y)+'um)')
    def toggleUI(self,val):
        self.ui.btnAcq.setEnabled(val) 
        self.ui.btnPreview_2.setEnabled(val)
        self.ui.btnCustom1.setEnabled(val)
        self.ui.btnCustom2.setEnabled(val)
        self.ui.btnCustom3.setEnabled(val)
        self.ui.toolButton1.setEnabled(val)
        self.ui.toolButton2.setEnabled(val)
        self.ui.toolButton3.setEnabled(val)
        

        self.ui.lockerWidget.setEnabled(val)
        self.ui.ParamsBox.setEnabled(val)
        self.ui.StatusBox.setEnabled(val)
                
        if val: self.ui.progressBar.hide()
        else: self.ui.progressBar.show()
    def grayRotTab(self):
        self.ui.rotationTab.setEnabled(self.rot_series_bool.val)
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
#         except Exception as err:
#             print self.name, "error:", err
    def _run(self):
        #try:
        if not hasattr(self,'_m') or self._m == None: self.getScope()
        changed = False
        if not hasattr(self, 'prev_tiltLQRange'): 
            self.prev_tiltLQRange=self.tiltLQRange.array
        if list(self.prev_tiltLQRange)!=list(self.tiltLQRange.array):
            self.prev_tiltLQRange=self.tiltLQRange.array
            changed = True
            print 'changed'
        
        if not self.workingList or changed:
            print 'updating workinglist'
            self.workingList = list(self.tiltLQRange.array[::-1])
        self.paused = False
        totalImages = len(self.workingList)*self.num_repeats.val
        if self.rot_series_bool.val: totalImages *= len(self.rotationLQRange.array)
        imagePct = int((100.0/totalImages))
        imagesTaken = 0
        self.set_progress(0)
        self.toggleUI(False)
        while self.workingList:
            if self.debug: print len(self.workingList)
            tiltVal = round(float(self.workingList.pop()),2)
            self.hardware.current_tilt.update_value(tiltVal)
            if self.rot_series_bool.val:
                print 'list of rots:', self.rotationLQRange.array
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
            else:
                for _ in range(self.num_repeats.val):
                    self.dataLocker.addToSeries(self.acquireSTEMImage())
                    imagesTaken += 1
                    self.set_progress(imagesTaken*imagePct)
                    if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----'
                    if self.auto_pause.val: self.pauseSeries()
                    if self.paused: break
         #except Exception as err:
             #print self.name, "error:", err
    def acquireSTEMImage(self):
        acquiredImageSet = self.Acq.AcquireImages()      
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
        
        return stemImage
    def postAcquisition(self):
        self.set_progress(0)
        self.toggleUI(True)
        print '-----postacq-----'
    def updateFigure(self,stemImage):
        data = stemImage.data
        print data
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
        self.ui.lblXCal_details.setText(str(stemImage.xCal)+str(stemImage.calUnits))
        self.ui.lblYCal_details.setText(str(stemImage.yCal)+str(stemImage.calUnits))
        
        #-----draft for rotating the view in step with stem coils
        #self.viewer.rotate(-(self.current_view_rotation.val))
        #self.current_view_rotation.update_value(stemImage.stemRotation)
        #self.viewer.rotate(self.current_view_rotation.val)

        self.viewer.clear()
        x = pg.ImageItem(data)
        self.viewer.addItem(x)
        self.update_display()
        self.dummyStuff() #fills Status Box with false values
        print '-----postiter-----'
    def minTilt(self):
        self.ensureTiltChange(self.minimum_tilt.val)
        print '-----min tilt-----'
    def maxTilt(self):
        self.ensureTiltChange(self.maximum_tilt.val)
        print '-----max tilt-----'
    def closeEvent(self,event):
        self.dataLocker.saveAll()
    def ensureTiltChange(self,desiredTilt):
        if abs(self.hardware.current_tilt.val-desiredTilt)>self.tilt_snap_threshold:
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
    


