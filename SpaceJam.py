# Luke Classen, 6/26/2024
# CONTROLS:
# WASD: Camera control, look up/left/down/right
# SPACE: Move forwards
# Q & E: Move left and right respectively


from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionHandlerPusher
import math, sys, random

import DefensePaths as defensePaths
import SpaceJamClasses as spaceJamClasses
import Player as player


class MyApp(ShowBase):

    def __init__(self):

        ShowBase.__init__(self)

        # Create world
        self.SetupScene()
        self.SetCamera()
        self.SetCollisions()

        # Start setting key bindings.    
        self.accept('escape', self.quit)

    def SetupScene(self):
        '''Spawns planets, the universe, space station, the player, and drones.'''
        self._generate_planets()
        self._generate_drones()

        self.Universe = spaceJamClasses.Universe(self.loader, "./Assets/Universe/Universe.x", self.render, 'Universe', "Assets/Universe/Universe.jpg", (0, 0, 0), 13500)
        self.SpaceStation1 = spaceJamClasses.SpaceStation(self.loader, "./Assets/Space Station/spacestation.obj", self.render, 'Space Station', "./Assets/Space Station/Metal.jpg", (-7500, 500, 100), 1)
        self.Hero = player.Spaceship(self, self.loader, self.taskMgr, self.accept, "./Assets/Spaceships/spaceship.obj", self.render, 'Hero', "./Assets/Spaceships/spaceship.jpg", (1000, 1200, -50), 0.5)

    def SetCollisions(self):
        '''Handles traversing and pushing collisions'''
        
        self.cTrav = CollisionTraverser()
        self.cTrav.traverse(self.render)
        self.pusher = CollisionHandlerPusher()
        self.pusher.addCollider(self.Hero.collisionNode, self.Hero.modelNode)
        self.cTrav.addCollider(self.Hero.collisionNode, self.pusher)
        self.cTrav.showCollisions(self.render) # Remove after collider labs

    def _generate_planets(self):
        '''Spawns planets at random positions with a minimum distance between each.'''

        # Path dictionary
        planets = [
            {"texture_path": "./Assets/Planets/Mars.jpg"},
            {"texture_path": "./Assets/Planets/Purple.png"},
            {"texture_path": "./Assets/Planets/Sand.png"},
            {"texture_path": "./Assets/Planets/Tiled.jpg"},
            {"texture_path": "./Assets/Planets/Wicker.jpg"},
            {"texture_path": "./Assets/Planets/Rock.jpg"}
        ]

        # Spawn planets at "random" positions within the player's view
        self.minDistance = 1000 # Drones rarely collide between planets
        self.existing_positions = []

        for i, planet_spec in enumerate(planets):
            position = self._generate_position(self.existing_positions, self.minDistance)
            planet = spaceJamClasses.Planet(self.loader, "./Assets/Planets/protoPlanet.x", self.render, f"Planet{i+1}", planet_spec["texture_path"], position, random.randint(150, 275))
            setattr(self, f"Planet{i+1}", planet)
            self.existing_positions.append(position)

    def _distance(self, pos1, pos2):
        '''Distance formula'''
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)
    
    def _generate_position(self, existing_positions, min_distance):
        '''Generate position, check if it's closer than the minimum distance, then return the position.'''
        while True:
            new_position = (random.randint(-2000, 10000), random.randint(2000, 7000), random.randint(-350, 3550))
            if all(self._distance(new_position, pos) >= min_distance for pos in existing_positions):
                return new_position

    def _generate_drones(self):
        '''Spawn Drones on planets 1, 2, and 3'''
        fullCycle = 60
        for j in range(fullCycle):
            spaceJamClasses.Drone.droneCount += 1
            nickName = "Drone" + str(spaceJamClasses.Drone.droneCount)

            # TODO Spawn on random planets
            self.DrawCloudDefense(self.Planet1, nickName)
            self.DrawBaseballSeams(self.Planet2, nickName, j, fullCycle, 2)
            self.DrawCircleX(self.Planet3, nickName, j)
            self.DrawCircleY(self.Planet3, nickName, j)
            self.DrawCircleZ(self.Planet3, nickName, j)

    def DrawBaseballSeams(self, centralObject, droneName, step, numSeams, radius = 1):
        unitVec = defensePaths.BaseballSeams(step, numSeams, B = 0.4)
        unitVec.normalize()
        position = unitVec * radius * 250 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCloudDefense(self, centralObject, droneName):
        unitVec = defensePaths.Cloud()
        unitVec.normalize()
        position = unitVec * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)
    
    def DrawCircleX(self, centralObject, droneName, step, radius=1):
        unitVec = defensePaths.CircleX(step)
        unitVec.normalize()
        position = unitVec * radius * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCircleY(self, centralObject, droneName, step, radius=1):
        unitVec = defensePaths.CircleY(step) 
        unitVec.normalize()
        position = unitVec * radius * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def DrawCircleZ(self, centralObject, droneName, step, radius=1):
        unitVec = defensePaths.CircleZ(step) 
        unitVec.normalize()
        position = unitVec * radius * 500 + centralObject.modelNode.getPos()
        spaceJamClasses.Drone(self.loader, "./Assets/DroneDefender/DroneDefender.obj", self.render, droneName, "./Assets/DroneDefender/octotoad1_auv.png", position, 5)

    def SetCamera(self):
        # TODO make 3rd person camera? 
        self.disableMouse()
        self.camera.reparentTo(self.Hero.modelNode)
        self.camera.setFluidPos(0, 0.1, 0) # Slight adjustment to avoid model clipping
        
    # Prepare message if server wants to quit.
    def quit(self):
        '''Exit game.'''
        sys.exit()
        
app = MyApp()
app.run()