import importlib
import uuid
import random

import obj
import copy
import zmap
import comp
import vec2
import loader
import zmath
import msgs
from zexceptions import *
import valid
import views
#from log import *

class Sim:
    def __init__(self, imsgr):
        self.reset()
        self.imsgr = imsgr
        self.command_validator = valid.CommandValidator()

        self.action_dispatch_table = {}
        self.buildActionDispatchTable()

        self.view_manager = views.ViewManager()
    def reset(self):
        self.map = None
        self.objs = {}
        self.items = {}
        self.destroyed_objs={}
        self.sides={}
        self.ticks_per_turn=1
        self.tick = 0

        self.comp_views={}

    def buildActionDispatchTable(self):
        self.action_dispatch_table['HIGHSPEED_PROJECTILE'] = self.ACTN_HighspeedProjectile
        self.action_dispatch_table['MOVE']=self.ACTN_Move
        self.action_dispatch_table['TURN']=self.ACTN_Turn
        self.action_dispatch_table['TRANSMIT_RADAR']=self.ACTN_TransmitRadar
        self.action_dispatch_table['BROADCAST']=self.ACTN_BroadcastMessage

    ##########################################################################
    # MAP
    def setMap(self,_map):
        self.map = _map
        sides = self.map.getData('sides')
        for k,v in sides.items():
            self.addSide(k,v)
    def getMap(self):
        return self.map
    def hasMap(self):
        return self.map!=None

    ##########################################################################
    # SIDES
    def addSideID(self,ID):
        self.sides[ID]=None
    def addSide(self,ID,side):
        self.sides[ID]=side
        self.sides[ID]['teamname']=None
    def getSides(self):
        return self.sides
    
    ##########################################################################
    # TEAMS
    def addTeamName(self,ID,teamname):
        self.sides[ID]['teamname']=teamname
    def getTeamName(self,ID):
        return self.sides[ID]['teamname']
    def delTeamName(self,ID):
        self.sides[ID]['teamname']=None

    ##########################################################################
    # VIEWS
    # def addSelfView(self,_uuid,view):
    #     if _uuid not in self.self_views:
    #         self.self_views[_uuid]=[]
    #     self.self_views[_uuid].append(view)
    def addCompView(self,_uuid,view):
        if _uuid not in self.comp_views:
            self.comp_views[_uuid]=[]

        self.comp_views[_uuid].append(view)

    ##########################################################################
    # BUILD SIM
    def buildSim(self, ldr):

        if not self.hasMap():
            raise BuildException("No map was selected.")

        for k,v in self.sides.items():
            if v['teamname']==None:
                raise BuildException("Side "+k+" has no team assignment.")

        config = ldr.copyMainConfig()
        team_dir = config['team_dir']

        # Set the number of ticks per turn
        self.ticks_per_turn = config['ticks_per_turn']
        self.tick=0

        # Build the map grid
        self.map.buildMapGrid()

        # Create the map border
        edge_obj_id = self.map.getData('edge_obj_id')
        edge_coords = self.map.getListOfEdgeCoordinates()
        for ec in edge_coords:
            # Copy the obj
            newobj = ldr.copyObjTemplate(edge_obj_id)
            # Create obj place data
            data = {}
            data['x']=ec[0]
            data['y']=ec[1]
            data['uuid']=uuid.uuid4()
            # Place, add to objDict and add to map
            newobj.place(data)
            self.objs[data['uuid']]=newobj
            self.map.addObj(data['x'],data['y'],data['uuid'])

        # Add all placed objects
        pl_objs = self.map.getData('placed_objects')
        for oid,lst in pl_objs.items():
            for o in lst:
                # If an object entry in placed_objs does not
                # have a position, it is ignored.
                if 'x' in o and 'y' in o:
                    newobj = ldr.copyObjTemplate(oid)
                    data=o
                    data['uuid']=uuid.uuid4()
                    newobj.place(data)
                    self.objs[data['uuid']]=newobj
                    self.map.addObj(data['x'],data['y'],data['uuid'])

        # Add all placed items
        pl_items = self.map.getData('placed_items')
        for iid,lst in pl_items.items():
            for i in lst:
                # If an item entry does not have a position, ignore.
                if 'x' in i and 'y' in i:
                    newitem = ldr.copyItemTemplate(iid)
                    data=i
                    data['uuid']=uuid.uuid4()
                    newitem.place(data)
                    self.items[data['uuid']]=newitem
                    self.map.addItem(data['x'],data['y'],data['uuid'])

        # Add teams and ai-controlled objs
        for k,v in self.sides.items():
            team_data = ldr.copyTeamTemplate(v['teamname'])
            team_data['side']=k
            team_data['agents']={}
            team_name = team_data['name']
            # Copy so we don't f-up the original
            starting_locations = list(v['starting_locations'])

            for agent in team_data['agent_defs']:
                newobj = ldr.copyObjTemplate(agent['object'])
                data={}
                data['side']=k
                data['ticks_per_turn']=config['ticks_per_turn']
                data['callsign']=agent['callsign']
                data['teamname']=team_data['name']
                data['squad']=agent['squad']
                data['object']=agent['object']
                data['uuid']=uuid.uuid4()

                # Randomly choose a starting location
                sl = random.randint(0,len(starting_locations)-1)
                data['x'] = starting_locations[sl][0]
                data['y'] = starting_locations[sl][1]

                # Delete the chosen location so no other team mate gets it.
                del starting_locations[sl]

                
                # select a random facing.
                facing = v['facing']
                if facing == "None":
                    facing = random.random()*360.0
                else:
                    facing = float(facing)

                data['facing'] = facing
                

                # Load and set AI
                ai_filename = agent['AI_file']
                ai_spec = importlib.util.spec_from_file_location(ai_filename,team_dir+'/'+team_name+'/'+ai_filename)
                ai_module = importlib.util.module_from_spec(ai_spec)
                ai_spec.loader.exec_module(ai_module)
                AI=ai_module.AI()
                AI.initData(data)

                # Store the AI object after initialization
                # to avoid including it in the data dict passed
                # to the AI itself.
                data['ai'] = AI

                # Create and store components
                for c in newobj.getData('comp_ids'):
                    newcomp = ldr.copyCompTemplate(c)
                    newcomp.setData('parent',newobj)
                    newobj.addComp(newcomp)

                # Place and store and add to map
                newobj.place(data)
                self.objs[data['uuid']]=newobj
                self.map.addObj(data['x'],data['y'],data['uuid'])

                # Add agent obj to team dictionary of agents
                team_data['agents'][data['uuid']]=newobj

            # Add the team data to the side entry
            v['team']=team_data

    ##########################################################################
    # Get the world view
    def getGeneralView(self):
        view = {}
        view['tick']=self.tick
        return view


    ##########################################################################
    # CHECK END OF GAME
    def checkEndOfSim(self):

        # Only 1 team remaining
        teams_remaining = []
        for name,data in self.sides.items():
            team_eliminated = True

            for obj in data['team']['agents'].values():
                if obj.getData('alive'):
                    team_eliminated=False
                    break
            if not team_eliminated:
                teams_remaining.append(name)
        
        if len(teams_remaining) == 1:
            self.imsgr.addMsg(msgs.Msg(self.tick,"---GAME OVER---","The winning side is: " + teams_remaining[0]))
            return True
        if len(teams_remaining) == 0:
            self.imsgr.addMsg(msgs.Msg(self.tick,"---GAME OVER---","All teams are dead???"))
            return True
        return False

    def getPointsData(self):
        msg = ""
        for name,data in self.sides.items():
            msg += "  TEAM: "+name+"\n"
            total = 0
            for obj in data['team']['agents'].values():
                msg += "    "+obj.getBestDisplayName()+": "+str(obj.getData('points'))+"\n"
                total += obj.getData('points')
            msg += "    TOTAL: "+str(total)+"\n"

        m=msgs.Msg(str(self.tick),"CURRENT POINTS",msg)
        self.imsgr.addMsg(m)
                

    ##########################################################################
    # RUN SIM
    def runSim(self, turns):

        
        
        
        for turn in range(turns):
            # A place to store the commands by uuid and tick
            cmds_by_uuid = {}
            
            # get the general view to pass onto objects.
            general_view = self.getGeneralView()

            # Run all obj's updates, storing the returned commands
            # Don't need to shuffle order while getting commands
            for objuuid,obj in self.objs.items():

                cmd = None
                view = {}
                view['general']=general_view
                if objuuid in self.comp_views:
                    view['comp']=self.comp_views[objuuid]
                
                # Call update and get commands
                cmd = obj.update(view)

                # Validate commands
                cmd = self.command_validator.validateCommands(cmd)

                if cmd != None:
                    if type(cmd) == dict and len(cmd) > 0:
                        cmds_by_uuid[objuuid]=cmd


            # Flush the obj_views, so no one gets old data.
            self.comp_views = {}
            
            # Get the list of obj uuids which have issued cmds.
            objuuids_list = list(cmds_by_uuid.keys())

            # Run each tick
            for tick in range(self.ticks_per_turn):
                self.imsgr.addMsg(msgs.Msg(self.tick,"---NEW TICK---",""))

                # Shuffle turn order.
                random.shuffle(objuuids_list)

                # Check all commands to see if there is
                # something to do this tick.
                #for objuuid,objcmds in cmds_by_uuid.items():
                for objuuid in objuuids_list:
                    objcmds = cmds_by_uuid[objuuid]
                    if str(tick) in objcmds:
                        cmds_this_tick = objcmds[str(tick)]
                        self.processCommands(objuuid,cmds_this_tick)

                # Check if the sim is over.
                if self.checkEndOfSim():
                    return

                self.tick += 1



    def processCommands(self,objuuid,cmds):

        # Prevents commands from objs destroyed in this tick
        # from taking place.
        if objuuid in self.objs:

            obj = self.objs[objuuid]
            
            # Send the commands to the object so they can be
            # processed. This returns a list of actions.
            actions = self.objs[objuuid].processCommands(cmds)

            # Dispatch each action to the function that
            # handles its execution.
            for a in actions:

                self.action_dispatch_table[a.getType()](obj,a)

    ##########################################################################
    # ACTION PROCESSING FUNCTIONS
    # These handle the meat of turning actions into world changes.
    # All the sexy happens here.
    ##########################################################################

    # High-speed projectile action
    def ACTN_HighspeedProjectile(self,obj,actn):

        view = self.view_manager.getViewTemplate('projectile')
        view['compname']=actn.getData('compname')
        
        # Get list of cells through which the shell travels.
        cells_hit = zmath.getCellsAlongTrajectory(
            obj.getData('x'),
            obj.getData('y'),
            actn.getData('direction'),
            actn.getData('range')
        )

        # Get the list of cells through which the shell travels.
        damage = random.randint(actn.getData('min_damage'),actn.getData('max_damage'))

        # If there's something in a cell, damage the first thing
        # along the path and quit.
        for cell in cells_hit:
            id_in_cell = self.map.getCellOccupant(cell[0],cell[1])
            if id_in_cell == obj.getData('uuid'):
                continue
            elif id_in_cell != None:

                view['hit_x']=cell[0]
                view['hit_y']=cell[1]
                view['objname']=self.objs[id_in_cell].getData('objname')

                damage_str = obj.getBestDisplayName()+" shot "+self.objs[id_in_cell].getBestDisplayName() + \
                    " for "+str(damage)+" points of damage."
                self.logMsg("DAMAGE",damage_str)

                points = self.damageObj(id_in_cell,damage)

                obj.setData('points',points)

                break

        self.addCompView(obj.getData('uuid'),view)

            
    # Regular object move action
    def ACTN_Move(self,obj,actn):
        # Get current data
        direction = actn.getData('direction')
        cur_speed = actn.getData('speed')
        old_x = obj.getData('x')
        old_y = obj.getData('y')
        old_cell_x = obj.getData('cell_x')
        old_cell_y = obj.getData('cell_y')
        x = old_x + old_cell_x
        y = old_y + old_cell_y
        # translate and new data
        new_position = zmath.translatePoint(x,y,direction,cur_speed)
        new_x = int(new_position[0])
        new_y = int(new_position[1])
        new_cell_x = abs(new_position[0]-abs(new_x))
        new_cell_y = abs(new_position[1]-abs(new_y))
        # see if move is possible.
        if new_x != old_x or new_y != old_y:
            if self.map.isCellEmpty(new_x,new_y):
                self.map.moveObjFromTo(obj.getData('uuid'),old_x,old_y,new_x,new_y)
                obj.setData('x',new_x)
                obj.setData('y',new_y)
                obj.setData('cell_x',new_cell_x)
                obj.setData('cell_y',new_cell_y)
            else:
                # CRASH INTO SOMETHING
                
                # We're still in the same cell but we need to move the obj to the edge
                # of the old cell to simulate that they reached the edge of it before
                # crashing.
                if new_x != old_x:
                    if new_x > old_x:
                        obj.setData('cell_x',0.99)
                    else:
                        obj.setData('cell_x',0.0)
                if new_y != old_y:
                    if new_y > old_y:
                        obj.setData('cell_y',0.99)
                    else:
                        obj.setData('cell_y',0.0)
        else:
            obj.setData('cell_x',new_cell_x)
            obj.setData('cell_y',new_cell_y)
            pass


    # Turns the obj
    def ACTN_Turn(self,obj,actn):

        cur_facing = obj.getData('facing')
        new_facing = cur_facing + actn.getData('turnrate')
        while new_facing < 0:
            new_facing += 360
        while new_facing >= 360:
            new_facing -= 360
        obj.setData('facing',new_facing)


    # Performs a radar transmission
    def ACTN_TransmitRadar(self,obj,actn):

        view = self.view_manager.getViewTemplate('radar')
        view['tick']=self.tick
        view['ctype']=actn.getData('ctype')
        view['compname']=actn.getData('compname')
        view['slot_id']=actn.getData('slot_id')

        # Set up the necessary data for easy access
        radar_facing = actn.getData('facing')+actn.getData('offset_angle')
        start = radar_facing-actn.getData('visarc')
        end = radar_facing+actn.getData('visarc')
        angle = start
        jump = actn.getData('resolution')
        x = actn.getData('x')
        y = actn.getData('y')
        _range = actn.getData('range')

    

        temp_view = []

        # While we're in our arc of visibility
        while angle <= end:
            # Get all objects along this angle
            pings = self.map.getAllObjUUIDAlongTrajectory(
                x,y,angle,_range
            )
            # Pings should be in order. Start adding if they're not there.
            # If the radar's level is less than the obj's density, stop. We can't see through.
            # Else keep going.

            
            for ping in pings:

                # Pinged ourself
                if ping['x']==x and ping['y']==y:
                    pass
                else:
                    # For now all we're giving the transmitting player
                    # the object name. Up to the player to figure out
                    # if this is a teammate.
                    ping['objname']=self.objs[ping['uuid']].getData('objname')
                    
                    # Make sure the reported direction is 0-360
                    direction = angle
                    if direction < 0:
                        direction += 360
                    if direction >= 360:
                        direction -= 360

                    ping['direction']=direction
                    ping['cell_x']=self.objs[ping['uuid']].getData('cell_x')
                    ping['cell_y']=self.objs[ping['uuid']].getData('cell_y')
                    ping['alive']=self.objs[ping['uuid']].isAlive()
                    temp_view.append(ping)
                    
                    # If our radar level can't penetrate the object, stop.
                    if actn.getData('level') < self.objs[ping['uuid']].getData('density'):
                        break

            angle += jump



        for ping in temp_view:
            del ping['uuid']
            view['pings'].append(ping)

        self.addCompView(obj.getData('uuid'),view)


    def ACTN_BroadcastMessage(self,obj,actn):

        view = {}
        view['vtype']='message'
        view['tick']=self.tick
        view['message']=actn.getData('message')

        for uuid,other_obj in self.objs.items():
            if uuid != obj.getData('uuid'):

                distance = zmath.distance(
                    obj.getData('x'),obj.getData('y'),
                    other_obj.getData('x'),other_obj.getData('y')
                )
                
                # if the distance to the other obj is less than
                # the broadcast range, add the view.
                if distance <= actn.getData('range'):
                    self.addCompView(uuid,view)
        

    ##########################################################################
    # ADDITIONAL HELPER FUNCTIONS
    # Some of the ACTN function do similar work.
    ##########################################################################

    def damageObj(self,_uuid,damage):
        # Damage object
        points = self.objs[_uuid].damageObj(damage)
        
        # If obj is dead, remove it.
        if not self.objs[_uuid].isAlive():

            dead_obj = self.objs[_uuid]
            # Remove from map
            
            self.map.removeObj(dead_obj.getData('x'),dead_obj.getData('y'),dead_obj.getData('uuid'))
            
            # Remove from obj dict
            del self.objs[_uuid]

            # # Add to destroyed objs
            self.destroyed_objs[_uuid]=dead_obj

            # # Log destruction
            # self.logMsg("DESTROYED",dead_obj.getData('callsign')+" was destroyed.")

        return points


    ##########################################################################
    # DRAWING DATA
    # This gets and returns a list of all drawing necessary data from the
    # live objects.
    ##########################################################################

    def getObjDrawData(self):
        dd = []
        for obj in self.destroyed_objs.values():
            dd.append(obj.getDrawData())
        for obj in self.objs.values():
            dd.append(obj.getDrawData())
        return dd

    def getItemDrawData(self):
        dd = []
        for item in self.items.values():
            dd.append(item.getDrawData())
        return dd

    ##########################################################################
    # SEND MESSAGE TO HANDLER
    ##########################################################################
    # Convenience function to create a message for the UI's log
    def logMsg(self,title,text):
        self.imsgr.addMsg(msgs.Msg(self.tick,title,text))