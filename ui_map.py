import tkinter as tk
from tkinter.font import Font
import tkinter.scrolledtext as scrolltext
import queue

class UIMap(tk.Toplevel):
    def __init__(self,map_width,map_height,sim,omsgr,master=None):
        super().__init__(master)
        self.master = master
        self.title("MAIA - Sim UI")

        # Store data
        self.sim = sim
        self.omsgr = omsgr
        self.map_width=map_width
        self.map_height=map_height

        # Create the left and right frames
        self.mapFrame = tk.Frame(self,relief=tk.RAISED,borderwidth=2)
        self.mapFrame.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
        self.logFrame = tk.Frame(self,relief=tk.RAISED,borderwidth=2)
        self.logFrame.pack(fill=tk.BOTH,expand=True,side=tk.RIGHT)

        # Create the map canvas
        self.xbar = tk.Scrollbar(self.mapFrame,orient=tk.HORIZONTAL)
        self.ybar = tk.Scrollbar(self.mapFrame,orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self.mapFrame,width=800,height=800,
                                xscrollcommand=self.xbar.set,
                                yscrollcommand=self.ybar.set)
        self.ybar.configure(command=self.canvas.yview)
        self.xbar.configure(command=self.canvas.xview)
        self.canvas.configure(scrollregion=(0,0,map_width*20,map_height*20))
        self.canvas.configure(background='white')
        self.ybar.pack(side=tk.RIGHT,fill=tk.Y)
        self.xbar.pack(side=tk.BOTTOM,fill=tk.X)
        self.canvas.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
        
        # Create the log
        self.scrollLog = tk.scrolledtext.ScrolledText(self.logFrame,wrap=tk.WORD,width=80)
        self.scrollLog.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
        self.scrollLog.configure(state='disabled')

        self.dataFrame1 = tk.Frame(self.logFrame,relief=tk.RAISED,borderwidth=2)
        self.dataFrame1.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
        self.lbTurnsToRun = tk.Label(self.dataFrame1,text="Turns To Run")
        self.lbTurnsToRun.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)
        self.tbTurnsToRun = tk.Entry(self.dataFrame1)
        self.tbTurnsToRun.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)


        
        self.dataFrame2 = tk.Frame(self.logFrame,relief=tk.RAISED,borderwidth=2)
        self.dataFrame2.pack(fill=tk.BOTH,expand=True,side=tk.TOP)

        self.btnFrame1 = tk.Frame(self.logFrame,relief=tk.RAISED,borderwidth=2)
        self.btnFrame1.pack(fill=tk.BOTH,expand=True,side=tk.TOP)
        self.btnRunXTurns = tk.Button(self.btnFrame1,text="Run X Turns",command=self.runXTurns)
        self.btnRunXTurns.pack(fill=tk.BOTH,expand=True,side=tk.LEFT)

        self.logFrame.after(100, self.updateLog)
        
        #TEST JUNK
        # self.canvas.create_text(50,50,text="Hello world")
        #self.canvas.create_rectangle(50,50,450,450,fill="green")
    def displayMsg(self,msg):
        m = msg.getText()
        self.scrollLog.configure(state='normal')
        self.scrollLog.insert(tk.END,m+"\n")
        self.scrollLog.configure(state='disabled')
        self.scrollLog.yview(tk.END)

    def updateLog(self):
        while True:
            try:
                m=self.omsgr.getMsg()
            except queue.Empty:
                break
            else:
                self.displayMsg(m)
        self.logFrame.after(100,self.updateLog)

    def runXTurns(self):
        turns_to_run = self.tbTurnsToRun.get()
        if turns_to_run.isdigit():
            turns_to_run = int(turns_to_run)
            self.sim.runSim(turns_to_run)

        
