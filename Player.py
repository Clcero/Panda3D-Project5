from CollideObjectBase import SphereCollideObject
from panda3d.core import Loader, NodePath, Vec3, TransparencyAttrib
from direct.task.Task import TaskManager
from typing import Callable
from direct.task import Task
from SpaceJamClasses import Missile
from direct.gui.OnscreenImage import OnscreenImage

class Spaceship(SphereCollideObject): # Player
    def __init__(self, base, loader: Loader, taskMgr: TaskManager, accept: Callable[[str, Callable], None], modelPath: str, parentNode: NodePath, nodeName: str, texPath: str, posVec: Vec3, scaleVec: float):
        super(Spaceship, self).__init__(loader, modelPath, parentNode, nodeName, Vec3(0, 0, 0), 10)
        self.taskMgr = taskMgr
        self.accept = accept
        self.modelNode.setPos(posVec)
        self.modelNode.setScale(scaleVec)
        self.modelNode.setName(nodeName) 
        tex = loader.loadTexture(texPath)
        self.modelNode.setTexture(tex, 1)

        self.SetKeyBindings()
        self.EnableHUD()
        self._SetMissiles()
        self.taskMgr.add(self.CheckIntervals, 'checkMissiles', 34) # Method to run, name for task, and priority

        self.base = base # Pass base when instanced from Showbase

    # All key bindings for ship's movement.
    def SetKeyBindings(self):
        '''Space moves forwards, WASD are turning controls, Q&E move left and right.'''
        self.accept('space', self.fwdThrust, [1])
        self.accept('space-up', self.fwdThrust, [0])
        self.accept('a', self.LeftTurn, [1])
        self.accept('a-up', self.LeftTurn, [0])
        self.accept('d', self.RightTurn, [1])
        self.accept('d-up', self.RightTurn, [0])
        self.accept('w', self.UpTurn, [1])
        self.accept('w-up', self.UpTurn, [0])
        self.accept('s', self.DownTurn, [1])
        self.accept('s-up', self.DownTurn, [0])
        self.accept('q', self.leftThrust, [1])
        self.accept('q-up', self.leftThrust, [0])
        self.accept('e', self.rightThrust, [1])
        self.accept('e-up', self.rightThrust, [0])
        self.accept('f', self.Fire) # Fire missile
    
    def EnableHUD(self):
        '''Sets aiming reticle.'''
        self.Hud = OnscreenImage(image = "./Assets/Hud/Reticle3b.png", pos = Vec3(0, 0, 0), scale = 0.1)
        self.Hud.setTransparency(TransparencyAttrib.MAlpha)

    # Missiles
    def _SetMissiles(self):
        '''Defines missile parameters.'''
        self.reloadTime = 0.25
        self.missileDistance = 4000
        self.missileBay = 1

    def Fire(self):
        '''Shoot missile if loaded, otherwise reload.'''
        if self.missileBay: # Check if missile in bay
            travRate = self.missileDistance

            aim = self.base.render.getRelativeVector(self.modelNode, Vec3.forward())
            aim.normalize()

            fireSolution = aim * travRate
            inFront = aim * 150 # Offset to put at front of spaceship

            travVec = fireSolution + self.modelNode.getPos() # Adjust to always follow model node and in front of player
            self.missileBay -= 1
            tag = 'Missile' + str(Missile.missileCount)
            
            posVec = self.modelNode.getPos() + inFront
            currentMissile = Missile(self.base.loader, './Assets/Phaser/phaser.egg', self.base.render, tag, posVec, 4.0) # Instantiate

            # Duration (2.0), Path to take (travVec), Starting position (posVec), Check collisions between frames (Fluid)
            Missile.Intervals[tag] = currentMissile.modelNode.posInterval(2.0, travVec, startPos = posVec, fluid = 1) # fluid = 1 checks in-between intervals
            
            Missile.Intervals[tag].start()
        
        else:
            if not self.taskMgr.hasTaskNamed('reload'):
                print('Preparing reload...')
                self.taskMgr.doMethodLater(0, self._Reload, 'reload') # Doing it 0 seconds later
                return Task.cont
    
    def _Reload(self, task):
        '''Called as part of Fire function, loads missile after reload time has passed.'''
        if task.time > self.reloadTime:
            self.missileBay += 1
            
            if self.missileBay > 1:
                self.missileBay = 1
            if self.missileBay < 0:
                self.missileBay = 0
            print('Reloaded.')
            return Task.done
        elif task.time <= self.reloadTime:
            print('Reloading...')
            return Task.cont

    def CheckIntervals(self, task):
        '''Handles missile node detachment and deletion.'''
        for i in Missile.Intervals:
            if not Missile.Intervals[i].isPlaying():
                Missile.cNodes[i].detachNode()
                Missile.fireModels[i].detachNode()

                del Missile.Intervals[i]
                del Missile.fireModels[i]
                del Missile.cNodes[i]
                del Missile.collisionSolids[i]
                print(i + ' has reached the end of its fire solution.')
                break # Memory still used when dictionary objects are deleted, so we break to refactor.

        return Task.cont

    # Movement
    def fwdThrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyFwdThrust, 'forward-thrust')
        else:
            self.taskMgr.remove('forward-thrust')
    
    def ApplyFwdThrust(self, task):
        rate = 25
        trajectory = self.base.render.getRelativeVector(self.modelNode, Vec3.forward())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont
    
    def leftThrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftThrust, 'left-thrust')
        else:
            self.taskMgr.remove('left-thrust')
    
    def ApplyLeftThrust(self, task):
        rate = 25
        trajectory = self.base.render.getRelativeVector(self.modelNode, Vec3.left())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont

    def rightThrust(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightThrust, 'right-thrust')
        else:
            self.taskMgr.remove('right-thrust')
    
    def ApplyRightThrust(self, task):
        rate = 25
        trajectory = self.base.render.getRelativeVector(self.modelNode, Vec3.right())
        trajectory.normalize()

        self.modelNode.setFluidPos(self.modelNode.getPos() + trajectory * rate)

        return Task.cont
    

    # Keeps player from going upside down
    def constrainPitch(self):
        '''Constrains pitch to straight up or straight down, does not allow
            the player to go upside down.'''
        pitch = self.modelNode.getP()
        if pitch > 89.0:
            self.modelNode.setP(89.0)
        elif pitch < -89.0:
            self.modelNode.setP(-89.0)

    def updateCameraRotation(self, headingChange, pitchChange):
        '''Updates the camera rotation, calls constrainPitch().'''
        self.modelNode.setH(self.modelNode.getH() + headingChange)
        self.modelNode.setP(self.modelNode.getP() + pitchChange)
        self.constrainPitch()

    # Left and Right Turns - Gimbal locks at high pitch values
    def LeftTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyLeftTurn, 'left-turn')      
        else:
            self.taskMgr.remove('left-turn')

    def ApplyLeftTurn(self, task):
        rate = 1.25
        self.updateCameraRotation(rate, 0)
        return Task.cont

    def RightTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyRightTurn, 'right-turn')     
        else:
            self.taskMgr.remove('right-turn')

    def ApplyRightTurn(self, task):
        rate = 1.25
        self.updateCameraRotation(-rate, 0)
        return Task.cont

    # Up and Down Turns - Stops at +-89
    def UpTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyUpTurn, 'up-turn')      
        else:
            self.taskMgr.remove('up-turn')

    def ApplyUpTurn(self, task):
        rate = 1.25
        self.updateCameraRotation(0, rate)
        return Task.cont

    def DownTurn(self, keyDown):
        if keyDown:
            self.taskMgr.add(self.ApplyDownTurn, 'down-turn')     
        else:
            self.taskMgr.remove('down-turn')

    def ApplyDownTurn(self, task):
        rate = 1.25
        self.updateCameraRotation(0, -rate)
        return Task.cont

