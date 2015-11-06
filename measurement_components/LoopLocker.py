'''
Storage solution draft for dynamic series/preview acquisition

Requires two QTreeWidgets; buttons should be connected to goToSelectedAlpha,
    seriesToFloating, floatingToSeries, diffItems, saveAll, saveFloating, saveSeries,
    averageItems, discardItems
'''
from PySide.QtCore import QObject, Signal, Qt
from PySide.QtGui import QTreeWidgetItem, QAbstractItemView
from numpy import ndarray
class LoopLocker(QObject):
    change_occurred = Signal()
    display_request = Signal(ndarray)
    alpha_move_request = Signal(float)
    diagnostic_info = Signal(str)
    
    def __init__(self,seriesTreeWidget,floatingTreeWidget):
        QObject.__init__(self)
        self.series, self.sCount = dict(), 0
        self.floating, self.fCount = dict(),0
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
    def addToSeries(self,acquiredSingleImage):
        tilt = float("{0:.3f}".format(acquiredSingleImage.alpha))
        if self.series.has_key(tilt): 
            self.series[tilt].append(acquiredSingleImage)
            print '-----append to series slot-----'
        else:
            self.series[tilt] = [acquiredSingleImage]       
            print '-----add to series-----'
        self.sCount += 1
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def addToFloating(self,acquiredSingleImage):
        tilt = float("{0:.3f}".format(acquiredSingleImage.alpha))
        if self.floating.has_key(tilt): 
            self.floating[tilt].append(acquiredSingleImage)
            print '-----append to series slot-----'
        else:
            self.floating[tilt] = [acquiredSingleImage]
        self.sCount += 1
        print '-----add to floating-----'
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def moveFromSeries(self,tilt,index):
        self.addToFloating(self.series[tilt].pop(index))
        if len(self.series[tilt])==0: self.series.pop(tilt)
        self.fCount -= 1
        self.sCount += 1
        self.change_occurred.emit()

    #--------------------------------------------------------------------------- 
    def moveFromFloating(self,tilt,index):
        self.addToSeries(self.floating[tilt].pop(index))
        if len(self.floating[tilt])==0: self.floating.pop(tilt)
        self.fCount -= 1
        self.sCount += 1
        self.change_occurred.emit()
    
    #--------------------------------------------------------------------------- 
    def deleteFromSeries(self,tilt,index):
        self.series[tilt].remove(self.series[tilt][index])
        if len(self.series[tilt])==0: self.series.pop(tilt)
        print '-----remove a'+str(tilt)+ ' from series-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def deleteFromFloating(self,tilt,index):
        self.floating[tilt].remove(self.floating[tilt][index])
        if len(self.floating[tilt])==0: self.floating.pop(tilt)
        print '-----remove a'+str(tilt)+ ' from series-----'
        self.change_occurred.emit()
        
    #--------------------------------------------------------------------------- 
    def hasUnsavedSeries(self):
        if len(self.series): return True
        else: return False 
    
    #--------------------------------------------------------------------------- 
    def flushSeries(self):
        '''Moves everything from Series to Floating'''
        for x in self.series.keys():
            for y in self.series.pop(x):
                self.addToFloating(y)
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
    def getDisplayRepr(self,loc,tilt,index):
        '''returns the actual NxN numpy representation'''
        rtrn = -1
        if loc == 'seriesView': rtrn = self.series[tilt][index].acqData
        if loc == 'floatingView':  rtrn = self.floating[tilt][index].acqData
        return rtrn     
    #--------------------------------------------------------------------------- 

    #--------------------------------------------------------------------------- 
    '''GUI Functionality'''
    def fill_item(self,item, value):
        item.setExpanded(True)
        if type(value) is dict:
            for key, val in sorted(value.iteritems()):
                child = QTreeWidgetItem()
                x = "{0:.3f}".format(key)
#                 x = key
                child.setText(0, unicode(x))
                child.setFlags(Qt.ItemIsEnabled)
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
    def itemClicked(self,item):
        try:
            self.display_request.emit((self.getDisplayRepr(
                                            self.sender().objectName(),
                                            float(item.parent().text(0)),
                                            int(item.text(0)))))
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
        if len(selected)==1: self.display_request.emit(self.getDisplayRepr(
                                        self.sender().objectName(),
                                        float(selected[0].parent().text(0)),
                                        int(selected[0].text(0))))         
#             self.updateView(self.getDisplayRepr(
#                                         self.sender().objectName(),
#                                         float(selected[0].parent().text(0)),
#                                         int(selected[0].text(0))))
    def goToSelectedAlpha(self):
        selection = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        if len(selection)==1:
            self.alpha_move_request.emit(float(selection[0].parent().text(0)))   
    def seriesToFloating(self):
        self.blockSignals(True)
        moved = 0
        selected = self.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                print 'in selected loop s2f'
                self.dataLocker.moveFromSeries(float(i.parent().text(0)),
                                                (int(i.text(0))+moved))
                moved-=1
        self.blockSignals(False) 
        self.change_occurred.emit()
    def floatingToSeries(self):
        self.blockSignals(True)
        moved = 0
        selected = self.floatingView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.moveFromFloating(float(i.parent().text(0)),
                                                (int(i.text(0))+moved))
                moved-=1
        self.blockSignals(False) 
        self.change_occurred.emit()  
    def diffItems(self):
        if self.changed_selection:
            self.diffCounter = 0
            self.changed_selection = False
            self.tempSelect = self.seriesView.selectedItems() + self.floatingView.selectedItems()
        else:
            selected = self.tempSelect
            self.display_request.emit(self.getDisplayRepr(
                                        selected[self.diffCounter].treeWidget().objectName(),
                                        float(selected[self.diffCounter].parent().text(0)),
                                        int(selected[self.diffCounter].text(0))))
            self.diffCounter+=1
            if self.diffCounter == len(selected): self.diffCounter = 0
    def saveAll(self):
        print '----save all-----'
    def saveFloating(self):
        print '----save floating----'
    def saveSeries(self):
        print '-----save series-----'
    def averageItems(self):
            selected = self.seriesView.selectedItems() + self.floatingView.selectedItems()
            avg = None
            for item in selected:
                if type(avg).__name__=='NoneType': avg = self.getDisplayRepr(
                                        item.treeWidget().objectName(),
                                        float(item.parent().text(0)),
                                        int(item.text(0)))
                else: avg += self.getDisplayRepr(
                                        item.treeWidget().objectName(),
                                        float(item.parent().text(0)),
                                        int(item.text(0)))
            avg /= float(len(selected))
            self.display_request.emit(avg)     
    def discardItems(self):
        #could probably be cleaned up
        self.blockSignals(True)
        deleted = 0
        selected = self.seriesView.selectedItems()
        if len(selected)!=0:
            for i in selected:
                self.deleteFromSeries(float(i.parent().text(0)),
                                                (int(i.text(0))+deleted))
                deleted-=1
        selected = self.floatingView.selectedItems()
        deleted = 0
        if len(selected)!=0:
            for i in selected:
                self.deleteFromFloating(float(i.parent().text(0)),
                                                (int(i.text(0))+deleted))  
                deleted-=1      
        self.blockSignals(False)
        self.change_occurred.emit() 
        print '-----remove something-----'
class AcquiredSingleImage():
    def __init__(self,acqData,acqParams=None,acqTime=None,alpha=None):
        self.acqData = acqData
        self.acqParams = acqParams
        self.acqTime = acqTime
        self.alpha = alpha #for now    
        #self.staParams = staParams   
        #self.alpha = self.staParams.A
class AveragedImage(AcquiredSingleImage):
    def __init__(self,acqData):
        AcquiredSingleImage.__init__(self, acqData)
    