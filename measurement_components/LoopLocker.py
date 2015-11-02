'''
Storage solution draft for dynamic series/preview acquisition
'''
from numpy import zeros,uint16
from PySide import QtCore
from PySide.QtCore import QObject
class LoopLocker(QObject):
    change_occurred = QtCore.Signal()
    def __init__(self):
        QObject.__init__(self)
        print 'hi'
        self.series = dict()
        self.floating = dict()
        self.fCount = 0
        self.sCount = 0
    
    def addToSeries(self,acquiredSingleImage):
        tilt = float("{0:.3f}".format(acquiredSingleImage.alpha ))
        if self.series.has_key(tilt): 
            self.series[tilt].append(acquiredSingleImage)
            print '-----append to series slot-----'
        else:
            self.series[tilt] = [acquiredSingleImage]       
            print '-----add to series-----'
        self.sCount += 1
        self.change_occurred.emit()

    def addToFloating(self,acquiredSingleImage):
        tilt = float("{0:.3f}".format(acquiredSingleImage.alpha ))

        if self.floating.has_key(tilt): 
            self.floating[tilt].append(acquiredSingleImage)
            print '-----append to series slot-----'
        else:
            self.floating[tilt] = [acquiredSingleImage]
        self.sCount += 1
        print '-----add to floating-----'
        self.change_occurred.emit()
    
    def moveFromSeries(self,tilt,imageId):
        for x in self.series[tilt]:
            if x.imageId == imageId:
                idx = self.series[tilt].index(x)
                self.addToFloating(self.series[tilt].pop(idx))
                self.sCount -= 1
                self.fCount += 1
        self.change_occurred.emit()
        print '-----remove a'+tilt+ ' from series-----'
    def moveFromFloating(self,tilt,imageId):
        for x in self.floating[tilt]:
            if x.imageId == imageId:
                idx = self.floating[tilt].index(x)
                self.addToSeries(self.floating[tilt].pop(idx))
                self.fCount -= 1
                self.sCount += 1
        self.change_occurred.emit()
        print '-----remove a'+tilt+ ' from floating-----'
    def deleteFromSeries(self,tilt,imageId):
        for x in self.series[tilt]:
            if x.imageId == imageId:
                self.series[tilt].remove(x)
                self.sCount -= 1
        print '-----remove a'+tilt+ ' from series-----'
        self.change_occurred.emit()
    def deleteFromFloating(self,tilt,imageId):
        for x in self.floating[tilt]:
            if x.imageId == imageId: 
                self.floating[tilt].remove(x)
                self.fCount -= 1
        print '-----remove a'+tilt+ ' from series-----'
        self.change_occurred.emit()
    
    def hasUnsavedSeries(self):
        if len(self.series): return True
        else: return False
    
    def flushSeries(self):
        for x in self.series.keys():
            self.floating.addToFloating(self.series.pop(x))
        self.fCount += self.sCount
        self.sCount = 0
        self.change_occurred.emit()

    def clearSeries(self):
        try: 
            while self.floating.popitem(): pass
        except: pass
        self.sCount = 0
        self.change_occurred.emit()

    def clearFloating(self):
        try: 
            while self.series.popitem(): pass
        except: pass
        self.fCount = 0
        self.change_occurred.emit()
    def clearData(self):
        self.clearFloating()
        self.clearSeries()
        self.change_occurred.emit()
    def abortedSeries(self):
        #not sure, probably need to take action here
        print 'LL: -----aborted series-----'
    def printStuff(self): #diagnostic
        print 'printstuff'
        print self.sCount
        for x in self.series.keys():
            print x
            print self.series[x][0].acqTime.time()
    def getDisplayRepr(self,loc,tilt,index):
        rtrn = -1
        if loc == 'seriesView': rtrn = self.series[tilt][index].acqData
        if loc == 'floatingView': rtrn = rtrn = self.floating[tilt][index].acqData
        return rtrn
            
class AcquiredSingleImage():
    def __init__(self,acqData,acqParams,acqTime,alpha):
        self.acqData = acqData
        self.acqParams = acqParams
        self.acqTime = acqTime
        self.alpha = alpha #for now
        
        #self.staParams = staParams   
        #self.alpha = self.staParams.A

    