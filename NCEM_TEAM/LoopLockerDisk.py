'''
Storage solution for flexible series/preview acquisition

Requires two QTreeWidgets and some buttons; buttons should be connected to goToSelectedAlpha,
    seriesToFloating, floatingToSeries, diffItems, saveSeriesAndFloating, saveFloating, saveSeries,
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
    
    def __init__(self,seriesTreeWidget,floatingTreeWidget,debug=True):
        QObject.__init__(self)
        self.debug = debug

        #-----create hdf5 files-----
        self.createSeriesFile()        
        self.createFloatingFile()
        
        #-----view stuff-----
        self.seriesView = seriesTreeWidget
        self.floatingView = floatingTreeWidget
           
        #-----connect events-----
        self.change_occurred.connect(self.updateTrees)
        
        self.seriesView.itemSelectionChanged.connect(self.selectionChanged)
        self.floatingView.itemSelectionChanged.connect(self.selectionChanged)
        
        self.seriesView.itemClicked.connect(self.itemClicked)
        self.floatingView.itemClicked.connect(self.itemClicked)
        
        self.seriesView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.floatingView.setSelectionMode(QAbstractItemView.ExtendedSelection)        
        
    #--------------------------------------------------------------------------- 

#--------------------------------------------------------------------------- 
    def createSeriesFile(self):
        index = 1 # '001_series.emd'
        while os.path.isfile(str(index).zfill(3)+self.SERIESFILESUFFIX):
            index += 1
        self.seriesFileName = str(index).zfill(3)+self.SERIESFILESUFFIX
        self.seriesFile = h5py.File(self.seriesFileName,'w')
        root = self.seriesFile['/']
        root.attrs["ScopeFoundry_version"] = 100
        self.series = root.create_group('series_data')
        self.series.attrs['filename'] = self.seriesFileName
        self.series.attrs['emd_group_type'] = 1
    def createFloatingFile(self):
        index = 1 # '001_floating.emd'
        while os.path.isfile(str(index).zfill(3)+self.FLOATINGFILESUFFIX):
            index += 1
        self.floatingFileName = str(index).zfill(3)+self.FLOATINGFILESUFFIX   
        self.floatingFile = h5py.File(self.floatingFileName,'w')
        root = self.floatingFile['/']
        root.attrs["ScopeFoundry_version"] = 100  
        self.floating = root.create_group('floating_data')
        self.floating.attrs['filename'] = self.floatingFileName
        self.floating.attrs['emd_group_type'] = 1
    def addToSeries(self,emImage): #adds an EMImage to the Series file
        tilt = str("{0:.3f}".format(emImage.stageAlpha))
        shape = emImage.data.shape
        
        if tilt not in self.series.keys():
            tiltGroup = self.series.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
            
        grp = self.series[tilt].create_group(emImage.ID)
        grp.attrs['emd_group_type'] = 1 
        dset = grp.create_dataset('data',shape,dtype='int16')
        dset[:,:] = emImage.data
        
        dim1 = grp.create_dataset('dim1',(shape[0],),'f',)
        dim1.attrs['name'] = string_('x') #use string_ to write fixed length strings. The viewer does not accommodate the default variable length strings (yet...)
        dim1.attrs['units'] = string_('[n_m]') #represent units properly (nanometers)
        dim1[:] = arange(0,shape[0],1)*emImage.xCal 
        
        dim2 = grp.create_dataset('dim2',(shape[1],),'f',)
        dim2.attrs['name'] = string_('y')
        dim2.attrs['units'] = string_('[n_m]')
        dim2[:] = arange(0,shape[1],1)*emImage.yCal  
        
        settingsGrp = grp.create_group('parameters')
        for k,v in emImage.__dict__.iteritems():
            if k != 'data':
                settingsGrp.attrs[k] = str(v)          
                   
        if self.debug: print '-----add to series-----'
        self.seriesFile.flush() #tell h5py to flush buffers to disk
        self.display_request.emit(emImage)
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def addToFloating(self,emImage):
        tilt = str("{0:.3f}".format(emImage.stageAlpha))
        shape = emImage.data.shape
        
        if tilt not in self.floating.keys():
            tiltGroup = self.floating.create_group(tilt)            
            tiltGroup.attrs['emd_group_type'] = 1   
            
        grp = self.floating[tilt].create_group(emImage.ID)
        dset = grp.create_dataset('data',shape,dtype='int16')
        dset[:,:] = emImage.data
        
        #dimensions, calibration stuff
        dim1 = grp.create_dataset('dim1',(shape[0],),'f',)
        dim1.attrs['name'] = string_('x') #use string_ to write fixed length strings. The viewer does not accommodate the default variable length strings (yet...)
        dim1.attrs['units'] = string_('[n_m]') #represent units properly (nanometers)
        dim2 = grp.create_dataset('dim2',(shape[1],),'f',)
        dim2.attrs['name'] = string_('y')
        dim2.attrs['units'] = string_('[n_m]')
        dim1[:] = arange(0,shape[0],1)*emImage.xCal 
        dim2[:] = arange(0,shape[1],1)*emImage.yCal
        
        settingsGrp = grp.create_group('parameters')        
        for k,v in emImage.__dict__.iteritems():
            if k != 'data':
                print k
                settingsGrp.attrs[k] = str(v)

        if self.debug: print '-----add to floating-----'
        self.display_request.emit(emImage)
        self.floatingFile.flush()
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def moveFromSeries(self,tiltVal,imgID): #moves a specific img
        tiltVal = str(tiltVal)
        imgID = str(imgID)
        if tiltVal not in self.floating.keys():
            tiltGroup = self.floating.create_group(tiltVal)            
            tiltGroup.attrs['emd_group_type'] = 1   
        
        self.series[tiltVal].copy(imgID,self.floating[tiltVal])
        self.series[tiltVal].pop(imgID)

        if len(self.series[tiltVal])==0: self.series.pop(tiltVal)
        self.change_occurred.emit()

    #--------------------------------------------------------------------------- 
    def moveFromFloating(self,tiltVal,imgID): #moves a specific img
        tiltVal = str(tiltVal)
        imgID = str(imgID)
        if tiltVal not in self.series.keys():
            tiltGroup = self.series.create_group(tiltVal)            
            tiltGroup.attrs['emd_group_type'] = 1   
        
        self.floating[tiltVal].copy(imgID,self.series[tiltVal])
        self.floating[tiltVal].pop(imgID)

        if len(self.floating[tiltVal])==0: self.floating.pop(tiltVal)
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def deleteFromSeries(self,tiltVal,imgID): #deletes an image
        tiltVal = str(tiltVal)
        imgID = str(imgID)
        self.series[tiltVal].pop(imgID)
        print '-----remove a'+str(tiltVal)+ ' from series-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def deleteFromFloating(self,tiltVal,imgID): #deletes an image
        tiltVal = str(tiltVal)
        imgID = str(imgID)
        self.floating[tiltVal].pop(imgID)
        print '-----remove a'+str(tiltVal)+ ' from floating-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 

    
    #--------------------------------------------------------------------------- 
    def flushSeries(self): #Moves everything from Series to Floating
        for tiltVal in self.series.keys():
            if tiltVal in self.floating.keys():
                for imgID in self.floating[tiltVal]:
                    self.series.copy(self.series[tiltVal][imgID],self.floating[tiltVal])
                    self.series[tiltVal].pop(imgID)
            else:
                self.series[tiltVal].copy(self.series[tiltVal],self.floating)
                self.series.pop(tiltVal)
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearSeries(self): #erases the Series contents
        try: 
            while self.series.popitem(): pass
        except: pass
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearFloating(self): #erases the Floating contents
        try: 
            while self.floating.popitem(): pass
        except: pass
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def clearData(self):
        self.blockSignals(True)
        self.clearFloating()
        self.clearSeries()
        self.blockSignals(False)
        self.change_occurred.emit()
            
    #--------------------------------------------------------------------------- 
    def printStuff(self): #diagnostic
        '''prints the stored data'''
        for x in self.series.keys():
            print x
            print self.series[x][0].acqTime.time()
        for x in self.floating.keys():
            print x
            print self.floating[x][0].acqTime.time()
        print 'end diag'
    #--------------------------------------------------------------------------- 
    def getDisplayRepr(self,loc,tiltVal,imgID): #returns data array for avg
        '''returns the actual NxN numpy representation'''
        tiltVal = str(tiltVal)
        imgID = str(imgID)
        if loc == 'seriesView': 
            rtrn = zeros(self.series[tiltVal][imgID]['data'].shape, dtype='int16')
            self.series[tiltVal][imgID]['data'].read_direct(rtrn)
        if loc == 'floatingView':  
            rtrn = zeros(self.floating[tiltVal][imgID]['data'].shape, dtype='int16')
            self.floating[tiltVal][imgID]['data'].read_direct(rtrn)
        return rtrn     
    #--------------------------------------------------------------------------- 
    def setComment(self,loc,tilt,imgID,cmnt):
        tilt = str(tilt)
        imgID = str(imgID)
        if loc == 'seriesView': 
            grp = self.series[tilt][imgID]['parameters']
        if loc == 'floatingView':  
            grp = self.floating[tilt][imgID]['parameters']
        grp.attrs['comment'] = cmnt
    #--------------------------------------------------------------------------- 

    #--------------------------------------------------------------------------- 
    '''GUI Functionality'''
    def itemClicked(self,item):
        try:
            loc = item.treeWidget().objectName()
            tiltVal = item.parent().text(0)
            imgID = item.text(0)
            stemImage = self.getSTEMImage(loc, tiltVal, imgID)
            self.display_request.emit(stemImage)  
        except:
            pass    
    def getSTEMImage(self,loc,tiltVal,imgID): #returns an EMImage
            if loc == 'seriesView':
                grp = self.series[tiltVal][imgID]
            if loc == 'floatingView':
                grp = self.floating[tiltVal][imgID]

            data = zeros(grp['data'].shape, dtype='int16')
            grp['data'].read_direct(data) #read array into 'data' var
                          
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
            return stemImage
    def updateTrees(self): #update both trees
        for widget,value in [[self.floatingView,self.floating],
                        [self.seriesView,self.series]]:
            widget.clear()
            self.fill_item(widget.invisibleRootItem(), value)
    def fill_item(self,item, value): #recursively fills the tree
        item.setExpanded(True)
        for key, val in sorted(value.iteritems()): #tilts
            child = QTreeWidgetItem()
            child.setText(0, unicode(key))
            child.setFlags(Qt.ItemIsEnabled)
            item.addChild(child)
            for keykey in sorted(val.keys()): #imgIDs
                childchild = QTreeWidgetItem()
                child.addChild(childchild)
                childchild.setText(0, str(keykey))
                child.setExpanded(True)
                childchild.setExpanded(True)              
    def selectionChanged(self):
        self.changed_selection = True
        selected = self.sender().selectedItems()
        if len(selected)==1:
            loc = selected[0].treeWidget().objectName()
            tiltVal = selected[0].parent().text(0)
            imgID = selected[0].text(0)
            stemImage = self.getSTEMImage(loc, tiltVal, imgID)
            self.display_request.emit(stemImage)
    def goToSelectedAlpha(self): #goes to tilt of selected single image
        selection = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        if len(selection)==1: self.alpha_move_request.emit(float(selection[0].parent().text(0)))
    def setSelectedComments(self,cmnt): #sets comments on selected images
        selected = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        for item in selected:
            self.setComment(item.treeWidget().objectName(),
                                        item.parent().text(0),
                                        item.text(0),cmnt)
    def seriesToFloating(self): #moves selected in 'floating' to 'series'
        self.blockSignals(True)
        selected = self.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.moveFromSeries(i.parent().text(0),i.text(0))
        self.blockSignals(False) 
        self.change_occurred.emit()
    def floatingToSeries(self): #moves selected in 'floating' to 'series'
        self.blockSignals(True)
        selected = self.floatingView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.moveFromFloating(i.parent().text(0),i.text(0))
        self.blockSignals(False) 
        self.change_occurred.emit()  
    def diffItems(self): #'flips' through selected items
        if self.changed_selection:
            self.diffIterator = 0
            self.changed_selection = False
            self.tempSelect = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        else:
            selected = self.tempSelect
            loc = selected[self.diffIterator].treeWidget().objectName()
            tiltVal = selected[self.diffIterator].parent().text(0)
            imgID = selected[self.diffIterator].text(0)
            self.display_request.emit(self.getSTEMImage(loc, tiltVal, imgID))
            self.diffIterator+=1
            if self.diffIterator == len(selected): self.diffIterator = 0
    def saveFloating(self): #closes 'floating' file, creates new one
        self.floatingFile.close()
        self.floatingView.clear()
        self.createFloatingFile()
        print '----save floating----'
    def saveSeries(self): #closes 'series' file, creates new one
        self.seriesFile.close()
        self.seriesView.clear()
        self.createSeriesFile()
        print '-----save series-----'
            #creates file, saves data        
    def saveSeriesAndFloating(self):
        self.saveFloating()
        self.saveSeries()
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
    def discardItems(self): #deletes selected items
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
        if self.debug: print '-----discarded items-----'
                
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
        
        
        
        
    