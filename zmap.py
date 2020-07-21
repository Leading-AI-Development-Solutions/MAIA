
import random

import loader
import obj
import vec2
from log import *
import zmath

class Map:
    def __init__(self, data):
        self.data = data

    def setData(self,key,val):
        self.data[key]=val
    def getData(self,key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    # Build the map 2 hexes wider and taller. This allows for
    # the placing of blocks around the edge while still keeping
    # the same playable space outlined in the map json. And
    # it means we do not have to worry about accounting for edge
    # boundries as they cannot be reached (if the edge obj is indestructible).
    def buildMapGrid(self):
        newmap=[]
        for x in range(self.data['width']+2):
            newcol = []
            for y in range(self.data['height']+2):
                newcol.append(None)
            newmap.append(newcol)

        self.data['grid']=newmap

    def addObj(self,x,y,_uuid):
        self.data['grid'][x][y]=_uuid
    def removeObj(self,x,y,_uuid):
        if self.data['grid'][x][y]==_uuid:
            self.data['grid'][x][y]=None

    # Creates a list of the coordinates of the world edge.
    def getListOfEdgeCoordinates(self):
        edge_coords = []
        wide=self.data['width']
        high=self.data['height']
        for x in range(wide):
            edge_coords.append((x,0))
            edge_coords.append((x,high-1))
        for y in range(1,high-1):
            edge_coords.append((0,y))
            edge_coords.append((wide-1,y))
        return edge_coords

    def isCellEmpty(self,x,y):
        return self.getData('grid')[x][y]==None
    def getCellOccupant(self,x,y):
        return self.getData('grid')[x][y]

    def moveObjFromTo(self,objuuid,from_x,from_y,to_x,to_y):
        grid = self.getData('grid')
        if grid[from_x][from_y]==objuuid:
            grid[from_x][from_y]=None
            grid[to_x][to_y]=objuuid

    def getAllObjUUIDAlongTrajectory(self,x,y,angle,distance):

        found_objs = []

        grid = self.getData('grid')

        cells = zmath.getCellsAlongTrajectory(x,y,angle,distance)

        for cell in cells:
            if 0 <= cell[0] < self.getData('width') and 0<=cell[1]<self.getData('height'):
                if grid[cell[0]][cell[1]] != None:
                    _uuid = grid[cell[0]][cell[1]]
                    ping = {}
                    ping['x']=cell[0]
                    ping['y']=cell[1]
                    ping['distance']=zmath.distance(x,y,cell[0],cell[1])
                    ping['uuid']=_uuid
                    found_objs.append(ping)
            else:
                break

        return found_objs
