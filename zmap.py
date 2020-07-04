
import random

import loader
import obj
import vec2
from log import *

# class MapSettings:
#     def __init__(self):
#         self.ID = None
#         self.name = None
#         self.width = 0
#         self.height = 0
#         self.rand_objects = {}
#         self.placed_objects = {}


class Map:
    def __init__(self, data):
        self.objects = []
        self.setData(data)
        self.open_starting_positions = {}

    def setData(self,data):
        self.data = {}
        self.required_data = []

        req_data = [
            'name','desc','width','height','teams','agents','starting_positions'
        ]
            
        for rd in req_data:
            if rd in data:
                self.data[rd] = data[rd]
            else:
                self.data[rd] = None
                LogError("MAP: Missing data "+rd)

        self.required_data += req_data

        opt_data = [
            'rand_objects','placed_objects'
        ]
        for od in opt_data:
            if od in data:
                self.data[od] = data[od]
                self.required_data.append(od)

        for k,v in self.data['starting_positions'].items():
            self.open_starting_positions[int(k)]=[]
            for pos in v:
                vec = vec2.Vec2(pos[0],pos[1])
                self.open_starting_positions[int(k)].append(vec)

    def getData(self,key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    def getOpenStartingPosition(self,team_index):
        if team_index in self.open_starting_positions:
            if len(self.open_starting_positions[team_index]) > 0:
                return self.open_starting_positions[team_index].pop()
            else:
                LogError("MAP: getOpenStartingPosition() attempt to get another position from empty team list.")
        else:
            LogError("MAP: getOpenStartingPosition() team_index not in open positions.")

    def addObject(self,obj):
        for o in self.objects:
            
        self.objects.append(obj)


    def addTeam(self,team,team_index):
        if team.getNumberOfAgents() != self.getData('agents'):
            LogError("MAP: addTeam() map does not support "+str(team.getNumberOfAgents())+" agents.")
        else:
            agents = team.getData('agents')
                    
            for i in range(len(agents)):
                agents[i].getObject().setPosition(self.getOpenStartingPosition(team_index))
                if not self.addObject(agents[i].getObject()):
                    LogError("MAP: addTeam() attempt to add agent to an already occupied location.")



    def generateMap(self,sim):
        count = 0
        # placed objects
        if 'placed_objects' in self.data:
            for k,v in self.data['placed_objects'].items():
                for data in v:
                    thisObj = sim.getObject(int(k))
                    thisObj.initObjectFromData(data)
                    self.addObject(thisObj)
        
        # rand objects
        if 'rand_objects' in self.data:
            for k,v in self.data['rand_objects'].items():
                for i in range(v):
                    thisObj = sim.getObject(int(k))
                    x = random.uniform(0.0,self.data['width'])
                    y = random.uniform(0.0,self.data['height'])
                    thisObj.setPosition(vec2.Vec2(x,y))
                    thisObj.randomize()
                    self.addObject(thisObj)

        

