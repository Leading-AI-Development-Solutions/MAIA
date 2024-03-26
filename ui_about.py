import tkinter as tk

from zexceptions import *
from ui_widgets import *

from main import *


class ui_about(tk.Frame):
    def __init__(self, controller, master=None, logger=None):
        tk.Frame.__init__(self, master)
        self.master = master
        self.logger = logger
        self.controller = controller

        self.BuildUI()

        self.UIMap = None

    def BuildUI(self):
        descText = "MAIA is a platform designed for AI competitions that provides a modular 2D \
            simulation environment for which students write AI to control competing agents.\n\
            The goal is to give coders all the tools necessary so that they can focus \
            primarily on analysis of information and decision-making.\n\n\
            MAIA was developed by Dr. Zachary Hutchinson during his graduate studies \
            at the University of Maine, Orono.\n Version 0.22, the most current version of MAIA,\
            was released in October of 2020.\n Further documentation, including overviews of the \
            AI scripts, can be found in the docs directory."
        # descText = re.sub(r"  +", "", descText)
        descText2 = descText.replace("            ", "")
        descText = descText2
        self.MAIALabel = uiLabel(master=self, text="Maine AI Arena")
        self.MAIALabel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.description = uiTextbox(master=self, width=60)
        self.description.insert(1.0, descText)
        self.description.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.description.config(state="disabled")
        self.btnHome = uiButton(
            master=self,
            text="Home",
            command=lambda: self.controller.show_frame("HomePage"),
        )
        self.btnHome.config(width=400)
        self.btnHome.pack(side=tk.TOP, fill="y", expand=True)