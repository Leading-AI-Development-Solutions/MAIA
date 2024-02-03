##############################################################################
# UI SIM
#
# The main UI element for a simulation in progress.
##############################################################################
import tkinter as tk
from tkinter.font import Font
import tkinter.scrolledtext as scrolltext
import queue
import cProfile
import logging

from ui_widgets import *

class UISim(tk.Toplevel):
    def __init__(self,map_width,map_height,sim,omsgr,master=None,logger=None):
        super().__init__(master)
        self.master = master
        self.configure(bg=DARKCOLOR)
        self.title("MAIA - Sim UI")
        self.geometry("1200x900")
        self.logger=logger
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_columnconfigure(0, weight=1, uniform="equal")
        self.grid_columnconfigure(1, weight=1, uniform="equal")

        # Store data
        self.sim = sim
        self.omsgr = omsgr
        self.map_width=map_width
        self.map_height=map_height

        self.BuildUI()

    def BuildUI(self):

        self.cell_size=32
        self.map_obj_char_size=24
        self.map_item_char_size=10
        self.char_offset = (self.cell_size-self.map_obj_char_size)/2
        self.map_obj_font = tk.font.Font(family='TkFixedFont',size=self.map_obj_char_size)
        self.map_item_font = tk.font.Font(family='TkFixedFont',size=self.map_item_char_size)

        # Make main containers
        self.titleFrame = uiQuietFrame(master=self)
        self.mapFrame = uiQuietFrame(master=self)
        self.logFrame = uiQuietFrame(master=self)
        self.displayFrame= uiQuietFrame(master=self)
        self.turnQuantFrame = uiQuietFrame(master=self)
        self.turnButtFrame = uiQuietFrame(master=self)

        # Add page title
        self.titleLabel = uiLabel(master=self.titleFrame, text="MAIA")

        # Place containers in grid 
        self.titleFrame.grid(row=0,column=0,columnspan=2)
        self.mapFrame.grid(row=1,column=0,sticky="e",padx=20,pady=20)
        self.logFrame.grid(row=1,column=1,sticky="w",padx=10,pady=10)
        self.displayFrame.grid(row=2,column=0,columnspan=2,padx=10,pady=10)
        self.turnQuantFrame.grid(row=3,column=0,sticky="e",padx=10,pady=10)
        self.turnButtFrame.grid(row=3,column=1,sticky="w",padx=10,pady=10)

        # Create screen title
        self.titleLabel.pack(side=tk.TOP,fill=tk.BOTH,expand=False,padx=10,pady=10)

        # Create the map canvas
        self.xbar = tk.Scrollbar(self.mapFrame,orient=tk.HORIZONTAL)
        self.ybar = tk.Scrollbar(self.mapFrame,orient=tk.VERTICAL)
        self.canvas = uiCanvas(
            master=self.mapFrame,
            width=400,
            height=400,
            xscrollcommand=self.xbar.set,
            yscrollcommand=self.ybar.set,
            scrollregion=(0,0,(self.map_width+2)*self.cell_size,(self.map_height+2)*self.cell_size),
            cell_size=self.cell_size,
            obj_char_size=self.map_obj_char_size,
            item_char_size=self.map_item_char_size,
            char_offset=self.char_offset,
            obj_font = self.map_obj_font,
            item_font = self.map_item_font
        )
        self.ybar.configure(command=self.canvas.yview)
        self.xbar.configure(command=self.canvas.xview)
        self.ybar.pack(fill=tk.Y,side=tk.RIGHT)
        self.xbar.pack(fill=tk.X,side=tk.BOTTOM)
        self.canvas.pack()

        self.canvas.yview_moveto(0.0)
        self.canvas.xview_moveto(0.0)
        
        # Create the log notebook and scrolling
        self.logNotebook = uiNotebook(master=self.logFrame)
        self.logNotebook.pack()
        self.scrollLog = uiScrollText(master=self.logFrame)
        self.scrollLog.pack(side=tk.TOP)
        self.scrollLog.configure(state='disabled')
        
        # Create display points button
        self.btnDisplayPoints = uiButton(master=self.displayFrame,text="Display Points",command=self.displayPoints)
        self.btnDisplayPoints.pack(side=tk.TOP)
        
        # Create button to run x terms and entry to set x
        self.turnsToRunLabel = uiLabel(master=self.turnQuantFrame, text="Turns To Run")
        self.turnsToRunEntry = uiEntry(master=self.turnQuantFrame)
        self.turnsToRunLabel.grid(row=0,column=0,sticky="e")
        self.turnsToRunEntry.grid(row=0,column=1,sticky="e")
        self.btnRunXTurns = uiButton(master=self.turnButtFrame,text="Run X Turns",command=self.runXTurns)
        self.btnRunXTurns.pack(side=tk.LEFT)
        

        self.logFrame.after(100, self.updateLog)

        # Draw the background tiles
        self.canvas_background_tile_ids = []
        self.canvas_background_RCnum_ids = []
        self.drawTiles()

        self.obj_drawIDs = {}
        self.initObjects()

        self.item_drawIDs = {}
        self.initItems()
        
        #TEST JUNK
        # self.canvas.create_text(50,50,text="Hello world")
        #self.canvas.create_rectangle(50,50,450,450,fill="green")
    
    def displayMsgMain(self,msg):
        m = msg.getText()
        self.scrollLog.configure(state='normal')
        self.scrollLog.insert(tk.END,m+"\n")
        self.scrollLog.configure(state='disabled')
        self.scrollLog.yview(tk.END)

    def drawTiles(self):
        
        w = self.map_width+2
        h = self.map_height+2

        for x in range(w):
            for y in range(h):

                if x != 0 and x != w-1 and y != 0 and y != h-1:
                    tile_id = self.canvas.drawTile(
                        x=x,
                        y=y,
                        fill='gray25'
                    )
                    self.canvas_background_tile_ids.append(tile_id)

                if (x==0 and (y != 0 and y != h-1)) or (x==w-1 and(y!=0 and y!=h-1)):
                    RCnum_id = self.canvas.drawRCNumber(
                        x=x,y=y,
                        fill='gray35',
                        text=str(y-1)
                    )
                    self.canvas_background_RCnum_ids.append(RCnum_id)
                elif (y==0 and (x != 0 and x != w-1)) or (y==h-1 and(x!=0 and x!=w-1)):
                    RCnum_id = self.canvas.drawRCNumber(
                        x=x,y=y,
                        fill='gray35',
                        text=str(x-1)
                    )
                    self.canvas_background_RCnum_ids.append(RCnum_id)
    
    #####################################################
    # OBJECT DRAWING
    def addObjectDrawID(self,_uuid,_drawID):
        self.obj_drawIDs[_uuid]=_drawID
    def getObjectDrawID(self,_uuid):
        try:
            return self.obj_drawIDs[_uuid]
        except KeyError:
            self.logger.error("UISim: KeyError "+str(_uuid)+" in getObjectDrawID().")
            return None
    def removeObjectDrawID(self,_uuid):
        objID = self.getObjectDrawID(_uuid)
        if objID != None:
            self.canvas.removeObj(objID)
            del self.obj_drawIDs[_uuid]
    
    def initObjects(self):
        #self.canvas.delete(tk.ALL)
        draw_data = self.sim.getObjDrawData()
                
        for dd in draw_data:
            obj_id = self.canvas.drawObj(dd=dd)
            self.addObjectDrawID(dd['uuid'],obj_id)
    def updateObjects(self):
        draw_data = self.sim.getObjDrawData()
        for dd in draw_data:
            if dd['redraw']:
                objID = self.getObjectDrawID(dd['uuid'])
                objID = self.canvas.redrawObj(dd=dd,objID=objID)
                self.addObjectDrawID(dd['uuid'],objID)
            else:
                objID = self.getObjectDrawID(dd['uuid'])
                self.canvas.updateDrawnObj(dd=dd,objID=objID)

    ######################################################
    # ITEM DRAWING
    def addItemDrawID(self,_uuid,_drawID):
        self.item_drawIDs[_uuid]=_drawID
    def getItemDrawID(self,_uuid):
        try:
            return self.item_drawIDs[_uuid]
        except KeyError:
            self.logger.error("UISim: KeyError "+str(_uuid)+" in getItemDrawID().")
            return None
    def removeItemDrawID(self,_uuid):
        del self.item_drawIDs[_uuid]
    def initItems(self):
        draw_data = self.sim.getItemDrawData()
        for dd in draw_data:
            item_id = self.canvas.drawItem(dd=dd)
            self.addItemDrawID(dd['uuid'],item_id)
    def updateItems(self):
        draw_data = self.sim.getItemDrawData()
        for dd in draw_data:
            item_id = self.getItemDrawID(dd['uuid'])
            self.canvas.updateDrawnItem(dd=dd,itemID=item_id)

    def updateLog(self):
        while True:
            try:
                m=self.omsgr.getMsg()
            except queue.Empty:
                break
            else:
                self.displayMsgMain(m)
        self.logFrame.after(100,self.updateLog)

    def runXTurns(self):
        turns_to_run = self.turnsToRunEntry.get()
        if turns_to_run.isdigit():
            turns_to_run = int(turns_to_run)
            self.sim.runSim(turns_to_run)


        self.updateObjects()
        self.updateItems()

    def displayPoints(self):
        self.sim.getPointsData()


        
