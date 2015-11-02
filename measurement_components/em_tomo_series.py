from measurement import Measurement
from numpy import ndarray,array, round
import pyqtgraph as pg
import pythoncom
from PySide import QtCore, QtGui
import win32com.client
from random import choice, random, randint
from foundry_scope.logged_quantity import LQRange
from threading import Thread
from foundry_scope.measurement_components.LoopLocker import LoopLocker,\
    AcquiredSingleImage
import datetime
from PySide.QtGui import QAction, QTreeWidgetItem
class EMTomographySeries(Measurement):
    itr_finished = QtCore.Signal(ndarray)
    name = "em_tomography"
    ui_filename = "measurement_components/em_tomo.ui"
    def __init__(self,gui):
        self.debug = True
        self.dataLocker = LoopLocker() 
        Measurement.__init__(self, gui)         
    def setup(self):
        self.display_update_period = 0.1 #seconds
        self.getHardware()
        self.setupUI()  
    def getHardware(self):
        self.hardware = self.gui.hardware_components['em_hardware']
        self._id = pythoncom.CoMarshalInterThreadInterfaceInStream(pythoncom.IID_IDispatch,self.hardware.Scope)
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
            self.ui.seriesView.itemClicked.connect(self.selected)
            self.ui.floatingView.itemClicked.connect(self.selected)
            self.ui.seriesView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.ui.floatingView.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
            self.dataLocker.change_occurred.connect(self.updateTrees)
            #buttons
            self.ui.btnDiscard.released.connect(self.discardItem)
            self.ui.btnAverage.released.connect(self.averageItems)
            self.ui.btnSaveAll.released.connect(self.saveAll)
            self.ui.btnSaveFloating.released.connect(self.saveFloating)
            self.ui.btnSavePrimary.released.connect(self.saveSeries)            
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
            self.hardware.current_tilt.connect_bidir_to_widget(self.ui.alphaBox)
            #measurement LQs
            self.num_tilts.connect_bidir_to_widget(self.ui.numBox)
            self.step_tilt.connect_bidir_to_widget(self.ui.steBox)
            self.minimum_tilt.connect_bidir_to_widget(self.ui.minBox)
            self.maximum_tilt.connect_bidir_to_widget(self.ui.maxBox)
            self.num_repeats.connect_bidir_to_widget(self.ui.repBox)
            #measurement signals
            self.measurement_sucessfully_completed.connect(self.postAcquisition)
            self.itr_finished[ndarray].connect(self.postIteration)   
            d = { 'key1': 'value1', 
              'key2': 'value2',
              'key3': [1,2,3, { 1: 3, 7 : 9}],
              'key4': object(),
              'key5': { 'another key1' : 'another value1',
                        'another key2' : 'another value2'} }
#             self.ui.seriesView.setModel(self.seriesModel) 
#             self.item = QtGui.QTreeWidgetItem('Heheehehehe')
#             self.seriesModel.appendRow(self.item)
        except Exception as err: 
            print "EM_Tomography: could not connect to custom main GUI", err
    def updateTrees(self):
        print '-----update trees-----'
        self.fill_widget(self.ui.floatingView,self.dataLocker.floating)
        self.fill_widget(self.ui.seriesView,self.dataLocker.series)
    def saveAll(self):
        print '----save all-----'
    def saveFloating(self):
        print '----save floating----'
    def saveSeries(self):
        print '-----save series-----'
        
    def selected(self,item):
        self.updateView(self.dataLocker.getDisplayRepr(
                                        self.sender().objectName(),
                                        float(item.parent().text(0)),
                                        int(item.text(0))))
        print item.text(0)
    def discardItem(self):
        selected = self.ui.seriesView.selectedItems()

        selected = self.ui.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                
                print i.parent().text(0)
        selected = self.ui.floatingView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                print i.parent().text(0)
            
        print '-----remove something-----'
    def averageItems(self):
        selected = self.ui.seriesView.selectedItems()
        for i in selected:
            print i.parent().text(0)
    def fill_item(self,item, value):
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in sorted(value.iteritems()):
                child = QTreeWidgetItem()
                x = "{0:.3f}".format(key)
#                 x = key
                child.setText(0, unicode(x))
                child.setFlags(QtCore.Qt.ItemIsEnabled)
                item.addChild(child)
                self.fill_item(child, val)
        elif type(value) is list:
            for val in value:
                child = QTreeWidgetItem()
                item.addChild(child)
                if type(val) is dict:      
                    child.setText(0, '[dict]')
                    self.fill_item(child, val)
                elif type(val) is list:
                    child.setText(0, '[list]')
                    self.fill_item(child, val)
                else:
                    child.setText(0, str(value.index(val)))
                    child.setExpanded(True)
        else:
            print 'hi'
            child = QTreeWidgetItem()
            child.setText(0, unicode(value))
            item.addChild(child)  
    def fill_widget(self,widget, value):
        widget.clear()
        self.fill_item(widget.invisibleRootItem(), value)
    def getScope(self):
        self._m = win32com.client.Dispatch(pythoncom.CoGetInterfaceAndReleaseStream(self._id, 
                                                    pythoncom.IID_IDispatch))
        self.Acq = self._m.Acquisition
        self.Proj = self._m.Projection
        self.initialDF = self.Proj.Defocus
        self.Stage = self._m.Stage
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
        pass
    def setup_figure(self):
        if hasattr(self, 'graph_layout'):
            self.graph_layout.deleteLater() # see http://stackoverflow.com/questions/9899409/pyside-removing-a-widget-from-a-layout
            del self.graph_layout
        self.graph_layout=pg.GraphicsLayoutWidget(border=(100,100,100))
        self.ui.plot_groupBox.layout().addWidget(self.graph_layout)
        self.viewer = self.graph_layout.addViewBox()
        self.viewer.enableAutoRange()
    def acqSeries(self):
        for ii in range(len(self.tiltLQRange.array)):
            print len(self.tiltLQRange.array)
            print 'loop ' + str(ii)
            tiltVal = float(self.tiltLQRange.array[ii])
            self.hardware.current_tilt.update_value(tiltVal)
            for ii in range(self.num_repeats.val):
                acquiredImageSet = self.Acq.AcquireImages()      
                itr = array(acquiredImageSet(0).AsSafeArray) 
                self.dataLocker.addToSeries(AcquiredSingleImage(itr,
                                                self.Acq.Detectors.AcqParams,
                                                datetime.datetime.now(),
                                                tiltVal))
                self.itr_finished.emit(itr)
                if self.debug: print '-----acquired @ '+str(tiltVal)+'deg-----' 
                if self.debug: print 'Size:'+str(itr.nbytes)  
    def preview(self):
        try:
            print self.tiltLQRange.array
            #self.getScope()
            acquiredImageSet = self.hardware.acquire()      
            itr = array(acquiredImageSet(0).AsSafeArray)
            self.dataLocker.addToFloating(AcquiredSingleImage(itr,
                                                self.hardware.Acq.Detectors.AcqParams,
                                                datetime.datetime.now(),
                                                self.hardware.current_tilt.val))
            #self.ui.columnView.addAction(QAction(str(self.hardware.current_tilt.val),self.ui.columnView))
            self.itr_finished.emit(itr)
        except Exception as err:
            print self.name, "error:", err
    def _run(self):
        try:
            if not hasattr(self,'_m') or self._m == None: self.getScope()
            self.allocateStorage()
            self.acqSeries()
            self.measurement_sucessfully_completed.emit()
        except Exception as err:
            print self.name, "error:", err
    def postAcquisition(self):
        self.dataLocker.printStuff()
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
        self.hardware.current_tilt.update_value(self.minimum_tilt.val)
        print '-----min tilt-----'
    def maxTilt(self):
        self.hardware.current_tilt.update_value(self.maximum_tilt.val)
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


