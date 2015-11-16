'''
Storage solution draft for dynamic series/preview acquisition

Requires two QTreeWidgets; buttons should be connected to goToSelectedAlpha,
    seriesToFloating, floatingToSeries, diffItems, saveAll, saveFloating, saveSeries,
    averageItems, discardItems
'''
from PySide.QtCore import QObject, Signal, Qt
from PySide.QtGui import QTreeWidgetItem, QAbstractItemView
from numpy import array,ndarray,string_,int8,arange,zeros
import h5py
import datetime
from time import time
import os

class LoopLocker(QObject):
    change_occurred = Signal()
    display_request = Signal(object)
    alpha_move_request = Signal(float)
    diagnostic_info = Signal(str)
    
    def __init__(self,seriesTreeWidget,floatingTreeWidget):
        QObject.__init__(self)
        SERIESFILESUFFIX = '_series.emd'
        FLOATINGFILESUFFIX = '_floating.emd'
        index = 1
        while os.path.isfile(str(index).zfill(3)+SERIESFILESUFFIX):
            index += 1
        self.seriesFileName = str(index).zfill(3)+SERIESFILESUFFIX
        
        index = 1
        while os.path.isfile(str(index).zfill(3)+FLOATINGFILESUFFIX):
            index += 1
        self.floatingFileName = str(index).zfill(3)+FLOATINGFILESUFFIX
        
        self.seriesFile = h5py.File(self.seriesFileName,'w')
        self.floatingFile = h5py.File(self.floatingFileName,'w')
        
        self.series = self.seriesFile.create_group('series_data')
        self.series.attrs['filename'] = self.seriesFileName
        self.series.attrs['emd_group_type'] = 1
        self.sCount = 0
        
        self.floating = self.floatingFile.create_group('floating_data')
        self.floating.attrs['filename'] = self.floatingFileName
        self.floating.attrs['emd_group_type'] = 1
        self.fCount = 0
        
        #----view stuff-----
        self.seriesView = seriesTreeWidget
        self.floatingView = floatingTreeWidget
        
        self.change_occurred.connect(self.updateTrees)
        
        self.floatingView.itemSelectionChanged.connect(self.selectionChanged)
        self.seriesView.itemSelectionChanged.connect(self.selectionChanged)
        self.seriesView.itemClicked.connect(self.itemClicked)
        self.floatingView.itemClicked.connect(self.itemClicked)
        self.seriesView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.floatingView.setSelectionMode(QAbstractItemView.ExtendedSelection)        
        
    #--------------------------------------------------------------------------- 
    def closeFiles(self):
        self.seriesFile.close()
        self.floatingFile.close()
        
#--------------------------------------------------------------------------- 
    def addToSeries(self,EMImage):
        tilt = str("{0:.3f}".format(EMImage.stageAlpha))
        shape = EMImage.data.shape
        
        if tilt not in self.series.keys():
            tiltGroup = self.series.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
            
        grp = self.series[tilt].create_group(EMImage.ID)
        dset = grp.create_dataset('data',shape,dtype='int16')
        dset[:,:] = EMImage.data
        
        dim1 = grp.create_dataset('dim1',(shape[0],),'f',)
        dim1.attrs['name'] = string_('x') #use string_ to write fixed length strings. The viewer does not accommodate the default variable length strings (yet...)
        dim1.attrs['units'] = string_('[n_m]') #represent units properly (nanometers)
        dim2 = grp.create_dataset('dim2',(shape[1],),'f',)
        dim2.attrs['name'] = string_('y')
        dim2.attrs['units'] = string_('[n_m]')
        dim1[:] = arange(0,shape[0],1)*EMImage.xCal 
        dim2[:] = arange(0,shape[1],1)*EMImage.yCal  
        
        settingsGrp = grp.create_group('settings')
        for k,v in EMImage.__dict__.iteritems():
            if k != 'data':
                settingsGrp.attrs[k] = str(v)          
                   
        print '-----add to series-----'
        self.seriesFile.flush()
        self.sCount += 1
        self.display_request.emit(EMImage)
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def addToFloating(self,EMImage):
        tilt = str("{0:.3f}".format(EMImage.stageAlpha))
        shape = EMImage.data.shape
        
        if tilt not in self.floating.keys():
            tiltGroup = self.floating.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
            
        grp = self.floating[tilt].create_group(EMImage.ID)
        dset = grp.create_dataset('data',shape,dtype='int16')
        dset[:,:] = EMImage.data
        
        dim1 = grp.create_dataset('dim1',(shape[0],),'f',)
        dim1.attrs['name'] = string_('x') #use string_ to write fixed length strings. The viewer does not accommodate the default variable length strings (yet...)
        dim1.attrs['units'] = string_('[n_m]') #represent units properly (nanometers)
        dim2 = grp.create_dataset('dim2',(shape[1],),'f',)
        dim2.attrs['name'] = string_('y')
        dim2.attrs['units'] = string_('[n_m]')
        dim1[:] = arange(0,shape[0],1)*EMImage.xCal 
        dim2[:] = arange(0,shape[1],1)*EMImage.yCal
        
        settingsGrp = grp.create_group('settings')        
        for k,v in EMImage.__dict__.iteritems():
            if k != 'data':
                print k
                settingsGrp.attrs[k] = str(v)

        print '-----add to floating-----'
        self.display_request.emit(EMImage)
        self.floatingFile.flush()
        self.fCount += 1
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def moveFromSeries(self,tilt,ID):
        tilt = str(tilt)
        ID = str(ID)
        if tilt not in self.floating.keys():
            tiltGroup = self.floating.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
        
        self.series[tilt].copy(ID,self.floating[tilt])
        self.series[tilt].pop(ID)

        if len(self.series[tilt])==0: self.series.pop(tilt)
        self.fCount -= 1
        self.sCount += 1
        self.change_occurred.emit()

    #--------------------------------------------------------------------------- 
    def moveFromFloating(self,tilt,ID):
        tilt = str(tilt)
        ID = str(ID)
        if tilt not in self.series.keys():
            tiltGroup = self.series.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
        
        self.floating[tilt].copy(ID,self.series[tilt])
        self.floating[tilt].pop(ID)

        if len(self.floating[tilt])==0: self.floating.pop(tilt)
        self.sCount -= 1
        self.fCount += 1
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def deleteFromSeries(self,tilt,ID):
        tilt = str(tilt)
        ID = str(ID)
        self.series[tilt].pop(ID)
        if len(self.series[tilt])==0: self.series.pop(tilt)
        print '-----remove a'+str(tilt)+ ' from series-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def deleteFromFloating(self,tilt,ID):
        tilt = str(tilt)
        ID = str(ID)
        self.floating[tilt].pop(ID)
        if len(self.floating[tilt])==0: self.floating.pop(tilt)
        print '-----remove a'+str(tilt)+ ' from floating-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def hasUnsavedSeries(self):
        if len(self.series): return True
        else: return False 
    
    #--------------------------------------------------------------------------- 
    def flushSeries(self):
        '''Moves everything from Series to Floating'''
        for x in self.series.keys():
            self.series.copy(x,self.floating)
            self.series.pop(x)
        self.fCount += self.sCount
        self.sCount = 0
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearSeries(self):
        try: 
            while self.series.popitem(): pass
        except: pass
        self.sCount = 0
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearFloating(self):
        try: 
            while self.floating.popitem(): pass
        except: pass
        self.fCount = 0
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearData(self):
        self.blockSignals(True)
        self.clearFloating()
        self.clearSeries()
        self.blockSignals(False)
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def abortedSeries(self):
        #not sure, probably need to take action here
        print 'LL: -----aborted series-----'
    
    #--------------------------------------------------------------------------- 
    def printStuff(self): #diagnostic
        '''prints the stored data'''
        print self.sCount
        for x in self.series.keys():
            print x
            print self.series[x][0].acqTime.time()
        for x in self.floating.keys():
            print x
            print self.floating[x][0].acqTime.time()
        print 'end diag'
    #--------------------------------------------------------------------------- 
    def getDisplayRepr(self,loc,tilt,ID):
        '''returns the actual NxN numpy representation'''
        tilt = str(tilt)
        ID = str(ID)
        if loc == 'seriesView': 
            rtrn = zeros(self.series[tilt][ID]['data'].shape, dtype='int16')
            self.series[tilt][ID]['data'].read_direct(rtrn)
        if loc == 'floatingView':  
            rtrn = zeros(self.floating[tilt][ID]['data'].shape, dtype='int16')
            self.floating[tilt][ID]['data'].read_direct(rtrn)
        return rtrn     
    #--------------------------------------------------------------------------- 
    def setComment(self,loc,tilt,ID,cmnt):
        tilt = str(tilt)
        ID = str(ID)
        if loc == 'seriesView': 
            grp = self.series[tilt][ID]['settings']
        if loc == 'floatingView':  
            grp = self.floating[tilt][ID]['settings']
        grp.attrs['comment'] = cmnt
    #--------------------------------------------------------------------------- 

    #--------------------------------------------------------------------------- 
    '''GUI Functionality'''
    def fill_item(self,item, value):
        item.setExpanded(True)
        for key, val in sorted(value.iteritems()):
            child = QTreeWidgetItem()
            child.setText(0, unicode(key))
            child.setFlags(Qt.ItemIsEnabled)
            item.addChild(child)
            for keykey in sorted(val.keys()):
                childchild = QTreeWidgetItem()
                child.addChild(childchild)
                childchild.setText(0, str(keykey))
                child.setExpanded(True)
                childchild.setExpanded(True)              
    def itemClicked(self,item):
        try:
            if item.treeWidget().objectName() == 'seriesView':
                grp = self.series[item.parent().text(0)][item.text(0)]
            if item.treeWidget().objectName() == 'floatingView':
                grp = self.floating[item.parent().text(0)][item.text(0)]

            data = zeros(grp['data'].shape, dtype='int16')
            grp['data'].read_direct(data)
                          
            stemImage = STEMImage(data = data)
            stemImage.defocus = grp['settings'].attrs['defocus']
            stemImage.time = grp['settings'].attrs['time']
            stemImage.stageAlpha = grp['settings'].attrs['stageAlpha']
            stemImage.stageBeta = grp['settings'].attrs['stageBeta']
            stemImage.stageX = grp['settings'].attrs['stageX']
            stemImage.stageY = grp['settings'].attrs['stageY']
            stemImage.stageZ = grp['settings'].attrs['stageZ']
            stemImage.dwellTime = grp['settings'].attrs['dwellTime']
            stemImage.comment = grp['settings'].attrs['comment']   
            stemImage.xCal = grp['settings'].attrs['xCal']       
            stemImage.yCal = grp['settings'].attrs['yCal']       
            stemImage.calUnits = grp['settings'].attrs['calUnits']              
            self.display_request.emit(stemImage)  
        except:
            pass        
    def updateTrees(self):
        for widget,value in [[self.floatingView,self.floating],
                        [self.seriesView,self.series]]:
            widget.clear()
            self.fill_item(widget.invisibleRootItem(), value)
    def selectionChanged(self):
        self.changed_selection = True
        selected = self.sender().selectedItems()
        if len(selected)==1:
            if selected[0].treeWidget().objectName() == 'seriesView':
                grp = self.series[selected[0].parent().text(0)][selected[0].text(0)]
            if selected[0].treeWidget().objectName() == 'floatingView':
                grp = self.floating[selected[0].parent().text(0)][selected[0].text(0)]
            data = zeros(grp['data'].shape, dtype='int16')
            grp['data'].read_direct(data)
                          
            stemImage = STEMImage(data = data)
            stemImage.defocus = grp['settings'].attrs['defocus']
            stemImage.time = grp['settings'].attrs['time']
            stemImage.stageAlpha = grp['settings'].attrs['stageAlpha']
            stemImage.stageBeta = grp['settings'].attrs['stageBeta']
            stemImage.stageX = grp['settings'].attrs['stageX']
            stemImage.stageY = grp['settings'].attrs['stageY']
            stemImage.stageZ = grp['settings'].attrs['stageZ']
            stemImage.dwellTime = grp['settings'].attrs['dwellTime']
            stemImage.comment = grp['settings'].attrs['comment']     
            stemImage.xCal = grp['settings'].attrs['xCal']       
            stemImage.yCal = grp['settings'].attrs['yCal']       
            stemImage.calUnits = grp['settings'].attrs['calUnits']       
            self.display_request.emit(stemImage) 
#             self.updateView(self.getDisplayRepr(
#                                         self.sender().objectName(),
#                                         float(selected[0].parent().text(0)),
#                                         int(selected[0].text(0))))
    def goToSelectedAlpha(self):
        selection = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        if len(selection)==1:
            self.alpha_move_request.emit(float(selection[0].parent().text(0)))
    def setSelectedComments(self,cmnt):
        selected = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        for item in selected:
            self.setComment(item.treeWidget().objectName(),
                                        item.parent().text(0),
                                        item.text(0),cmnt)
    def seriesToFloating(self):
        self.blockSignals(True)
        moved = 0
        selected = self.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                print 'in selected loop s2f'
                self.moveFromSeries(i.parent().text(0),i.text(0))
                moved-=1
        self.blockSignals(False) 
        self.change_occurred.emit()
    def floatingToSeries(self):
        self.blockSignals(True)
        selected = self.floatingView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.moveFromFloating(i.parent().text(0),i.text(0))
        self.blockSignals(False) 
        self.change_occurred.emit()  
    def diffItems(self):
        #optimize w/ buffer
        if self.changed_selection:
            self.diffCounter = 0
            self.changed_selection = False
            self.tempSelect = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        else:
            selected = self.tempSelect
            self.display_request.emit(STEMImage(data=self.getDisplayRepr(
                                        selected[self.diffCounter].treeWidget().objectName(),
                                        selected[self.diffCounter].parent().text(0),
                                        selected[self.diffCounter].text(0))))
            self.diffCounter+=1
            if self.diffCounter == len(selected): self.diffCounter = 0
    def saveData(self):
        print '----save all-----'
    def saveFloating(self):
        print '----save floating----'
    def saveSeries(self):
        print '-----save series-----'
            #creates file, saves data        
    def saveAll(self):
        try:
            self.floatingFile.close()
            self.seriesFile.close()
        except:
            pass
    def averageItems(self):
        try:
            selected = self.seriesView.selectedItems() + self.floatingView.selectedItems()
            avg = None
            for item in selected:
                if type(avg).__name__=='NoneType': avg = self.getDisplayRepr(
                                        item.treeWidget().objectName(),
                                        item.parent().text(0),
                                        item.text(0))
                else: avg += self.getDisplayRepr(
                                        item.treeWidget().objectName(),
                                        item.parent().text(0),
                                        item.text(0))
            avg /= float(len(selected))
            self.display_request.emit(STEMImage(data=avg))    
        except:
            pass 
    def discardItems(self):
        self.blockSignals(True)
        selected = self.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.deleteFromSeries(i.parent().text(0),
                                      i.text(0))
        selected = self.floatingView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.deleteFromFloating(i.parent().text(0),
                                        i.text(0))  
                   
        self.blockSignals(False)
        self.change_occurred.emit() 
        print '-----remove something-----'
                
class EMImage():
    def __init__(self,image=None,data=None):
        self.ID = str(time())
        self.time = str(datetime.datetime.now())
        
        if image is not None:
            self.data = array(image.AsSafeArray)
            self.name = image.Name
            self.height = image.Height
            self.width = image.Width
            self.depth = image.Depth
        
        if data is not None:
            self.data = data
            self.height = data.shape[1]
            self.width = data.shape[0]
        
        self.xCal = None
        self.yCal = None
        self.calUnits = None
        
        self.binning = None
        self.defocus = None
        self.comment = ''
        
        self.stageX = 0.0
        self.stageY = 0.0
        self.stageZ = 0.0
        self.stageAlpha = 0.0
        self.stageBeta = 0.0
    def setStagePosition(self,staPos):
        self.stageX = staPos.X
        self.stageY = staPos.Y
        self.stageZ = staPos.Z
        self.stageAlpha = staPos.A
        self.stageBeta = staPos.B
    def setCalibration(self,calibration):
        self.xCal = calibration[0]
        self.yCal = calibration[1]
        self.calUnits = calibration[2]
        
class STEMImage(EMImage):
    def __init__(self,image=None,data=None):
        EMImage.__init__(self,image,data)
        
        self.dwellTime = None
        self.stemMag = None
        
class TEMImage(EMImage):
    def __init__(self,image=None,data=None):
        EMImage.__init__(self,image,data)
        
        self.expTime = None
        self.temMag = None
        
        
        
        
    