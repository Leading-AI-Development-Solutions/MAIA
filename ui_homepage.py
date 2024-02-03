import tkinter as tk
from tkinter import messagebox
from tkinter.font import Font
import tkinter.scrolledtext as scrolltext
import importlib.util
import sys
import os
import queue
import logging

import sim
import loader
import ui_sim
import msgs
from zexceptions import *
from ui_widgets import *
import ui_setup
import aboutPage
import main
from main import *


class UIHomepage(tk.Frame):
    def __init__(self,master=None,logger=None,parent=None):
        tk.Frame.__init__(self,parent)
        self.master = master
        self.logger = logger

        self.configure(bg=DARKCOLOR)
        #self.pack()
        self.master.title("MAIA - Maine AI Arena")
        self.master.geometry("700x800")

        #self.startGameFrame = ui_setup.UISetup(master=self.master, logger=self.logger)
        #self.aboutPageFrame = aboutPage.aboutPage(master=self.master, logger=self.logger)

        # Create the msgr objs
        self.msg_queue = queue.Queue()
        self.imsgr = msgs.IMsgr(self.msg_queue)
        self.omsgr = msgs.OMsgr(self.msg_queue)

        self.ldr = loader.Loader(self.logger)
        self.sim = sim.Sim(self.imsgr)

        self.combat_log = []

        self.BuildUI()
        #self.tkraise()
        self.UIMap = None

    def Run(self):
        self.mainloop()

    def BuildUI(self):
        #self.mainFrame = uiQuietFrame(master=self)
        self.MAIALabel = uiLabel(master=self, text="Maine AI Arena")
        self.MAIALabel.pack(side=tk.TOP,fill=tk.BOTH,expand=True)
        self.btnStartGame = uiButton(master=self,command=self.startGame,text="Start Game")
        self.btnStartGame.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)
        self.btnAbout = uiButton(master=self,command=self.aboutPage,text="About MAIA")
        self.btnAbout.pack(side=tk.BOTTOM,fill=tk.BOTH,expand=True)


    def startGame(self):
        self.pack_forget()
        #self.master.setup.tkraise()
        self.master.setup.pack(side="top", fill="both", expand=True)

    
    def aboutPage(self):
        self.pack_forget()
        #self.master.about.tkraise()
        self.master.about.pack(side="top", fill="both", expand=True)