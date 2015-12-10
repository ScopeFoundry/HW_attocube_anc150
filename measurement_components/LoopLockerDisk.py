'''
Storage solution for flexible series/preview acquisition

Requires two QTreeWidgets and some buttons; buttons should be connected to goToSelectedAlpha,
    seriesToFloating, floatingToSeries, diffItems, saveAll, saveFloating, saveSeries,
    averageItems, discardItems
    
    Zach Anderson ver 1.0
'''
from PySide.QtCore import QObject, Signal, Qt
from PySide.QtGui import QTreeWidgetItem, QAbstractItemView
from numpy import array,string_,arange,zeros
import h5py
import datetime
from time import time
import os

class LoopLocker(QObject):
    change_occurred = Signal()
    display_request = Signal(object)
    alpha_move_request = Signal(float)
    diagnostic_info = Signal(str)
    
    SERIESFILESUFFIX = '_series.emd'
    FLOATINGFILESUFFIX = '_floating.emd'
    
    def __init__(self,seriesTreeWidget,floatingTreeWidget):
        QObject.__init__(self)

        #-----create hdf5 files-----
        self.createSeriesFile()        
        self.createFloatingFile()
        
        #-----view stuff-----
        self.seriesView = seriesTreeWidget
        self.floatingView = floatingTreeWidget
           
        #-----connect events-----
        self.change_occurred.connect(self.updateTrees)
        self.floatingView.itemSelectionChanged.connect(self.selectionChanged)
        self.seriesView.itemSelectionChanged.connect(self.selectionChanged)
        self.seriesView.itemClicked.connect(self.itemClicked)
        self.floatingView.itemClicked.connect(self.itemClicked)
        self.seriesView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.floatingView.setSelectionMode(QAbstractItemView.ExtendedSelection)        
        
    #--------------------------------------------------------------------------- 

#--------------------------------------------------------------------------- 
    def createSeriesFile(self):
        index = 1
        while os.path.isfile(str(index).zfill(3)+self.SERIESFILESUFFIX):
            index += 1
        self.seriesFileName = str(index).zfill(3)+self.SERIESFILESUFFIX
        self.seriesFile = h5py.File(self.seriesFileName,'w')
        root = self.seriesFile['/']
        root.attrs["ScopeFoundry_version"] = 100
        self.series = root.create_group('series_data')
        self.series.attrs['filename'] = self.seriesFileName
        self.series.attrs['emd_group_type'] = 1
        self.sCount = 0    
    def createFloatingFile(self):
        index = 1
        while os.path.isfile(str(index).zfill(3)+self.FLOATINGFILESUFFIX):
            index += 1
        self.floatingFileName = str(index).zfill(3)+self.FLOATINGFILESUFFIX   
        self.floatingFile = h5py.File(self.floatingFileName,'w')
        root = self.floatingFile['/']
        root.attrs["ScopeFoundry_version"] = 100  
        self.floating = root.create_group('floating_data')
        self.floating.attrs['filename'] = self.floatingFileName
        self.floating.attrs['emd_group_type'] = 1
        self.fCount = 0
    def addToSeries(self,EMImage):
        tilt = str("{0:.3f}".format(EMImage.stageAlpha))
        shape = EMImage.data.shape
        
        if tilt not in self.series.keys():
            tiltGroup = self.series.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
            
        grp = self.series[tilt].create_group(EMImage.ID)
        grp.attrs['emd_group_type'] = 1 
        dset = grp.create_dataset('data',shape,dtype='int16')
        dset[:,:] = EMImage.data
        
        dim1 = grp.create_dataset('dim1',(shape[0],),'f',)
        dim1.attrs['name'] = string_('x') #use string_ to write fixed length strings. The viewer does not accommodate the default variable length strings (yet...)
        dim1.attrs['units'] = string_('[n_m]') #represent units properly (nanometers)
        dim1[:] = arange(0,shape[0],1)*EMImage.xCal 
        
        dim2 = grp.create_dataset('dim2',(shape[1],),'f',)
        dim2.attrs['name'] = string_('y')
        dim2.attrs['units'] = string_('[n_m]')
        dim2[:] = arange(0,shape[1],1)*EMImage.yCal  
        
        settingsGrp = grp.create_group('parameters')
        for k,v in EMImage.__dict__.iteritems():
            if k != 'data':
                settingsGrp.attrs[k] = str(v)          
                   
        print '-----add to series-----'
        self.seriesFile.flush() #tell h5py to flush buffers to disk
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
        
        settingsGrp = grp.create_group('parameters')        
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
        print '-----remove a'+str(tilt)+ ' from series-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def deleteFromFloating(self,tilt,ID):
        tilt = str(tilt)
        ID = str(ID)
        self.floating[tilt].pop(ID)
        print '-----remove a'+str(tilt)+ ' from floating-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def hasUnsavedSeries(self):
        if len(self.series): return True
        else: return False 
    
    #--------------------------------------------------------------------------- 
    def flushSeries(self):
        '''Moves everything from Series to Floating'''
        for tilt in self.series.keys():
            if tilt in self.floating.keys():
                for imgID in self.floating[tilt]:
                    self.series.copy(self.series[tilt][imgID],self.floating[tilt])
                    self.series[tilt].pop(imgID)
            else:
                self.series[tilt].copy(self.series[tilt],self.floating)
                self.series.pop(tilt)
     
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
            grp = self.series[tilt][ID]['parameters']
        if loc == 'floatingView':  
            grp = self.floating[tilt][ID]['parameters']
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
            loc = item.treeWidget().objectName()
            tiltVal = item.parent().text(0)
            imgID = item.text(0)
            stemImage = self.getSTEMImage(loc, tiltVal, imgID)
            self.display_request.emit(stemImage)  
        except:
            pass    
    def getSTEMImage(self,loc,tiltVal,imgID):  
            if loc == 'seriesView':
                grp = self.series[tiltVal][imgID]
            if loc == 'floatingView':
                grp = self.floating[tiltVal][imgID]

            data = zeros(grp['data'].shape, dtype='int16')
            grp['data'].read_direct(data)
                          
            stemImage = STEMImage(data = data)
            stemImage.defocus = grp['parameters'].attrs['defocus']
            stemImage.time = grp['parameters'].attrs['time']
            stemImage.ID = grp['parameters'].attrs['ID']
            stemImage.stageAlpha = grp['parameters'].attrs['stageAlpha']
            stemImage.stageBeta = grp['parameters'].attrs['stageBeta']
            stemImage.stageX = grp['parameters'].attrs['stageX']
            stemImage.stageY = grp['parameters'].attrs['stageY']
            stemImage.stageZ = grp['parameters'].attrs['stageZ']
            stemImage.dwellTime = grp['parameters'].attrs['dwellTime']
            stemImage.comment = grp['parameters'].attrs['comment']   
            stemImage.xCal = grp['parameters'].attrs['xCal']       
            stemImage.yCal = grp['parameters'].attrs['yCal']       
            stemImage.calUnits = grp['parameters'].attrs['calUnits']  
            stemImage.stemRotation = grp['parameters'].attrs['stemRotation']   
    def updateTrees(self):
        for widget,value in [[self.floatingView,self.floating],
                        [self.seriesView,self.series]]:
            widget.clear()
            self.fill_item(widget.invisibleRootItem(), value)
    def selectionChanged(self):
        self.changed_selection = True
        selected = self.sender().selectedItems()
        if len(selected)==1:
            loc = selected[0].treeWidget().objectName()
            tiltVal = selected[0].parent().text(0)
            imgID = selected[0].text(0)
            stemImage = self.getSTEMImage(loc, tiltVal, imgID)
            self.display_request.emit(stemImage)
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
            loc = selected[self.diffCounter].treeWidget().objectName()
            tilt = selected[self.diffCounter].parent().text(0)
            imgID = selected[self.diffCounter].text(0)
            img = STEMImage(data=self.getDisplayRepr(loc,tilt,imgID))
            img.ID = imgID
            self.display_request.emit(img)
            self.diffCounter+=1
            if self.diffCounter == len(selected): self.diffCounter = 0
    def saveFloating(self):
        self.floatingFile.close()
        self.floatingView.clear()
        self.createFloatingFile()
        print '----save floating----'
    def saveSeries(self):
        self.seriesFile.close()
        self.seriesView.clear()
        self.createSeriesFile()
        print '-----save series-----'
            #creates file, saves data        
    def saveAll(self):
        try:
            self.saveFloating()
            self.saveSeries()
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
    def __init__(self,image=None,data=None,):
        self.ID = id
        self.time = str(datetime.datetime.now().strftime('%X %x %Z'))
        
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

        self.stemRotation = None
        self.dwellTime = None
        self.stemMag = None
        
class TEMImage(EMImage):
    def __init__(self,image=None,data=None):
        EMImage.__init__(self,image,data)
        
        self.expTime = None
        self.temMag = None
        
        
        
        
    