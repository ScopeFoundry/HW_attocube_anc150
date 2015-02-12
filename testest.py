'''
Created on Feb 12, 2015

@author: NIuser
'''
class Dog(object):
    
    def __init__(self,name='Dog'):
        self.name=name
    
    def createPuppy(self,name='Puppy'):
        parent=self
        
        class Puppy(object):
            def __init__(self,name='Puppy'):
                self.name=name
                self.parent=parent
                
            def bark(self):
                print('I am a Puppy!')
        
        return Puppy(name)
    
    def bark(self):
        print('I am a dog!')
                
    
mike=Dog('Mike')
adam=mike.createPuppy('Adam')
mike.bark()
adam.bark()
adam.parent.bark()