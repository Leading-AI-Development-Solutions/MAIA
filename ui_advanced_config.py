import tkinter as tk
from tkinter.font import Font
import tkinter.scrolledtext as scrolltext
import queue
import cProfile
import logging
import loader
import json
import comp
import obj
import zmap
from tkinter.messagebox import askyesno
from tkinter.messagebox import showwarning
from tkinter.simpledialog import askstring

import ui_map_config
from ui_widgets import *


class UISettings(tk.Toplevel):
    def __init__(self, master=None, logger=None):
        super().__init__(master)
        self.master = master
        self.configure(bg=BGCOLOR)
        self.title("MAIA - Advanced Configuration")

        self.geometry("1450x700")
        self.minsize(width=1400, height=700)
        self.logger = logger
        self.ldr = loader.Loader(self.logger)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.FixedGunKeys = [
            "reload_ticks",
            "reload_ticks_remaining",
            "reloading",
            "ammunition",
            "min_damage",
            "max_damage",
            "range",
        ]
        self.EngineKeys = [
            "min_speed",
            "max_speed",
            "cur_speed",
            "max_turnrate",
            "cur_turnrate",
        ]
        self.RadarKeys = [
            "active",
            "range",
            "level",
            "visarc",
            "offset_angle",
            "resolution",
        ]
        self.CnCKeys = ["max_cmds_per_tick"]
        self.RadioKeys = ["max_range", "cur_range", "message"]
        self.ArmKeys = ["max_weight", "max_bulk", "item"]

        self.prev_component_combo = None

        self.build_ui()

        self.UIMap = None

    def validate_number_entry(self, input):
        input.replace(".", "", 1)
        input.replace("-", "", 1)
        if input.isdigit() or input == "" or "-" in input or "." in input:
            return True

        else:
            return False

    def validate_string_entry(self, input):
        if len(input) != 0:
            return True
        else:
            return False

    def get_focused_entry(self):
        focused_entry = self.focus_get()
        print(focused_entry)
        return focused_entry

    def show_help(self):
        return

    def build_ui(self):
        """
        Initializes all widgets and places them.
        """
        # Make main widgets

        self.mainFrame = uiQuietFrame(master=self)
        self.teamsColumn = uiQuietFrame(master=self.mainFrame)
        self.componentsColumn = uiQuietFrame(master=self.mainFrame)
        self.objectsColumn = uiQuietFrame(master=self.mainFrame)
        self.mapsColumn = uiQuietFrame(master=self.mainFrame)
        self.titleLabel = uiLabel(master=self.mainFrame, text="Advanced Settings")

        self.validateNum = self.teamsColumn.register(self.validate_number_entry)
        self.validateString = self.teamsColumn.register(self.validate_string_entry)

        # Place main widgets
        self.mainFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.titleLabel.pack(side=tk.TOP, fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Make Team Widgets

        self.selectTeamCombo = uiComboBox(master=self.teamsColumn)
        self.selectTeamCombo.configure(state="readonly")
        self.teamsLabel = uiLabel(master=self.teamsColumn, text="Teams")
        self.teamSizeLabel = uiLabel(master=self.teamsColumn, text="Size:")
        self.teamSizeEntry = EntryHelp(
            master=self.teamsColumn,
            text=(
                "The team size field represents how many agents you want in the selected team."
                " This field takes numeric values only."
            ),
        )
        self.teamSizeEntry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.teamNameLabel = uiLabel(master=self.teamsColumn, text="Name:")
        self.teamNameEntry = EntryHelp(master=self.teamsColumn, text="To be added.")
        self.agentFrame = uiQuietFrame(
            master=self.teamsColumn, borderwidth=5, relief="ridge", sticky="nsew"
        )
        self.callsignLabel = uiLabel(master=self.agentFrame, text="Callsign:")
        self.callsignEntry = EntryHelp(master=self.agentFrame, text="To be added.")
        self.squadLabel = uiLabel(master=self.agentFrame, text="Squad:")
        self.squadEntry = EntryHelp(master=self.agentFrame, text="To be added.")
        self.agentObjectLabel = uiLabel(master=self.agentFrame, text="Object:")
        self.agentObjectEntry = EntryHelp(master=self.agentFrame, text="To be added.")
        self.aiFileLabel = uiLabel(master=self.agentFrame, text="AI File:")
        self.aiFileEntry = EntryHelp(master=self.agentFrame, text="To be added.")
        self.teamsUpdateButton = uiButton(
            master=self.teamsColumn, command=self.update_teams_json, text="Update"
        )
        self.teamsCreateButton = uiButton(
            master=self.teamsColumn, command=self.create_team, text="Create"
        )
        self.teamsDeleteButton = uiButton(
            master=self.teamsColumn, command=self.delete_team, text="Delete"
        )
        self.helpButton = uiButton(
            master=self.teamsColumn, command=self.show_help, text="Help"
        )

        # Place Team Widgets
        self.teamsColumn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.selectTeamCombo.grid(
            row=1, column=1, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10
        )
        self.teamsLabel.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.teamSizeLabel.grid(row=3, column=1, sticky="nsew")
        self.teamSizeEntry.frame.grid(row=3, column=2, sticky="nsew")
        self.teamNameLabel.grid(row=4, column=1, sticky="nsew")
        self.teamNameEntry.frame.grid(row=4, column=2, sticky="nsew")
        self.agentFrame.grid(
            row=5, column=1, columnspan=2, rowspan=2, sticky="nsew", ipadx=0, ipady=0
        )
        self.callsignLabel.grid(row=1, column=1, sticky="nsew")
        self.callsignEntry.frame.grid(row=1, column=2, sticky="nsew")
        self.squadLabel.grid(row=2, column=1, sticky="nsew")
        self.squadEntry.frame.grid(row=2, column=2, sticky="nsew")
        self.agentObjectLabel.grid(row=3, column=1, sticky="nsew")
        self.agentObjectEntry.frame.grid(row=3, column=2, sticky="nsew")
        self.aiFileLabel.grid(row=4, column=1, sticky="nsew")
        self.aiFileEntry.frame.grid(row=4, column=2, sticky="nsew")
        self.teamsUpdateButton.grid(
            row=7,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.teamsCreateButton.grid(
            row=8,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.teamsDeleteButton.grid(
            row=9,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )

        # Make Component Widgets
        self.selectComponentCombo = uiComboBox(master=self.componentsColumn)
        self.selectComponentCombo.configure(state="readonly")
        self.componentsLabel = uiLabel(master=self.componentsColumn, text="Components")
        self.componentsUpdateButton = uiButton(
            master=self.componentsColumn,
            command=self.update_components_json,
            text="Update",
        )
        self.componentsCreateButtom = uiButton(
            master=self.componentsColumn, command=self.create_component, text="Create"
        )
        self.componentsDeleteButton = uiButton(
            master=self.componentsColumn, command=self.delete_components, text="Delete"
        )
        self.componentsIDLabel = uiLabel(master=self.componentsColumn, text="ID:")
        self.componentsIDEntry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsNameLabel = uiLabel(master=self.componentsColumn, text="Name:")
        self.componentsNameEntry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsCTypeLabel = uiLabel(master=self.componentsColumn, text="CType:")
        self.componentsTypeLabel = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeCombo = uiComboBox(master=self.componentsColumn)
        self.componentsTypeAttr1Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr1Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr2Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr2Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr3Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr3Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr4Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr4Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr5Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr5Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr6Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr6Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )
        self.componentsTypeAttr7Label = uiLabel(master=self.componentsColumn, text="")
        self.componentsTypeAttr7Entry = EntryHelp(
            master=self.componentsColumn, text="To be added."
        )

        # Place Component Widgets
        self.componentsColumn.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )
        self.selectComponentCombo.grid(
            row=1, column=1, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10
        )
        self.componentsLabel.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.componentsIDLabel.grid(row=3, column=1, sticky="nsew")
        self.componentsIDEntry.frame.grid(row=3, column=2, sticky="nsew")
        self.componentsNameLabel.grid(row=4, column=1, sticky="nsew")
        self.componentsNameEntry.frame.grid(row=4, column=2, sticky="nsew")
        self.componentsCTypeLabel.grid(row=5, column=1, sticky="nsew")
        self.componentsTypeLabel.grid(row=5, column=2, sticky="nsew")

        self.componentsTypeAttr1Label.grid(row=6, column=1, sticky="nsew")
        self.componentsTypeAttr1Entry.frame.grid(row=6, column=2, sticky="nsew")
        self.componentsTypeAttr1Entry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr2Label.grid(row=7, column=1, sticky="nsew")
        self.componentsTypeAttr2Entry.frame.grid(row=7, column=2, sticky="nsew")
        self.componentsTypeAttr2Entry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr3Label.grid(row=8, column=1, sticky="nsew")
        self.componentsTypeAttr3Entry.frame.grid(row=8, column=2, sticky="nsew")
        self.componentsTypeAttr3Entry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr4Label.grid(row=9, column=1, sticky="nsew")
        self.componentsTypeAttr4Entry.frame.grid(row=9, column=2, sticky="nsew")
        self.componentsTypeAttr4Entry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr5Label.grid(row=10, column=1, sticky="nsew")
        self.componentsTypeAttr5Entry.frame.grid(row=10, column=2, sticky="nsew")
        self.componentsTypeAttr5Entry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr6Label.grid(row=11, column=1, sticky="nsew")
        self.componentsTypeAttr6Entry.frame.grid(row=11, column=2, sticky="nsew")
        self.componentsTypeAttr6Entry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr7Label.grid(row=12, column=1, sticky="nsew")
        self.componentsTypeAttr7Entry.frame.grid(row=12, column=2, sticky="nsew")
        self.componentsTypeAttr7Entry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeCombo.grid(row=13, column=1, columnspan=2, sticky="nsew")
        self.componentsUpdateButton.grid(
            row=14,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.componentsCreateButtom.grid(
            row=15,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.componentsDeleteButton.grid(
            row=16,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )

        # Make Object Widgets
        self.selectObjectsCombo = uiComboBox(master=self.objectsColumn)
        self.selectObjectsCombo.configure(state="readonly")
        self.objectsLabel = uiLabel(master=self.objectsColumn, text="Objects")
        self.objectsUpdateButton = uiButton(
            master=self.objectsColumn, command=self.update_objects_json, text="Update"
        )
        self.objectsCreateButton = uiButton(
            master=self.objectsColumn, command=self.create_object, text="Create"
        )
        self.objectsDeleteButton = uiButton(
            master=self.objectsColumn, command=self.delete_object, text="Delete"
        )
        self.objectsIDLabel = uiLabel(master=self.objectsColumn, text="ID:")
        self.objectsIDEntry = EntryHelp(master=self.objectsColumn, text="To be added.")
        self.objectsNameLabel = uiLabel(master=self.objectsColumn, text="Name:")
        self.objectsNameEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsFillAliveLabel = uiLabel(
            master=self.objectsColumn, text="Fill Alive:"
        )
        self.objectsFillAliveEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsFillDeadLabel = uiLabel(
            master=self.objectsColumn, text="Fill Dead:"
        )
        self.objectsFillDeadEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsTextLabel = uiLabel(master=self.objectsColumn, text="Text:")
        self.objectsTextEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsHealthLabel = uiLabel(master=self.objectsColumn, text="Health:")
        self.objectsHealthEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsHealthEntry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.objectsDensityLabel = uiLabel(master=self.objectsColumn, text="Density:")
        self.objectsDensityEntry = EntryHelp(
            master=self.objectsColumn, text="To be added."
        )
        self.objectsDensityEntry.entry.config(
            validate="all", validatecommand=(self.validateNum, "%P")
        )
        self.objectsCompIDsLabel = uiLabel(master=self.objectsColumn, text="Comp IDs:")
        self.objectsCompIDsCombo = ComboBoxHelp(master=self.objectsColumn, text="To be Added.")
        self.objectsPointsCountLabel = uiLabel(
            master=self.objectsColumn, text="Points Count:"
        )
        self.objectsPointsCountCombo = ComboBoxHelp(master=self.objectsColumn, text="To be Added.")

        # Place Object Widgets
        self.objectsColumn.pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10
        )
        self.selectObjectsCombo.grid(
            row=1, column=1, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10
        )
        self.objectsLabel.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.objectsIDLabel.grid(row=3, column=1, sticky="nsew")
        self.objectsIDEntry.frame.grid(row=3, column=2, sticky="nsew")
        self.objectsNameLabel.grid(row=4, column=1, sticky="nsew")
        self.objectsNameEntry.frame.grid(row=4, column=2, sticky="nsew")
        self.objectsFillAliveLabel.grid(row=5, column=1, sticky="nsew")
        self.objectsFillAliveEntry.frame.grid(row=5, column=2, sticky="nsew")
        self.objectsFillDeadLabel.grid(row=6, column=1, sticky="nsew")
        self.objectsFillDeadEntry.frame.grid(row=6, column=2, sticky="nsew")
        self.objectsTextLabel.grid(row=7, column=1, sticky="nsew")
        self.objectsTextEntry.frame.grid(row=7, column=2, sticky="nsew")
        self.objectsHealthLabel.grid(row=8, column=1, sticky="nsew")
        self.objectsHealthEntry.frame.grid(row=8, column=2, sticky="nsew")
        self.objectsDensityLabel.grid(row=9, column=1, sticky="nsew")
        self.objectsDensityEntry.frame.grid(row=9, column=2, sticky="nsew")
        self.objectsCompIDsLabel.grid(row=10, column=1, sticky="nsew")
        self.objectsCompIDsCombo.frame.grid(row=10, column=2, sticky="nsew")
        self.objectsPointsCountLabel.grid(row=11, column=1, sticky="nsew")
        self.objectsPointsCountCombo.frame.grid(row=11, column=2, sticky="nsew")
        self.objectsUpdateButton.grid(
            row=12,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.objectsCreateButton.grid(
            row=13,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.objectsDeleteButton.grid(
            row=14,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )

        # Make Map Widgets
        self.selectMapsCombo = uiComboBox(master=self.mapsColumn)
        self.selectMapsCombo.configure(state="readonly")
        self.mapsLabel = uiLabel(master=self.mapsColumn, text="Maps")
        self.mapsShowButton = uiButton(
            master=self.mapsColumn, command=self.show_map, text="Show"
        )
        self.mapsUpdateButton = uiButton(
            master=self.mapsColumn, command=self.update_maps_json, text="Update"
        )
        self.mapsCreateButton = uiButton(
            master=self.mapsColumn, command=self.create_map, text="Create"
        )
        self.mapsDeleteButton = uiButton(
            master=self.mapsColumn, command=self.delete_map, text="Delete"
        )
        self.mapsIDLabel = uiLabel(master=self.mapsColumn, text="ID:")
        self.mapsIDEntry = EntryHelp(master=self.mapsColumn, text="To be added.")
        self.mapsNameLabel = uiLabel(master=self.mapsColumn, text="Name:")
        self.mapsNameEntry = EntryHelp(master=self.mapsColumn, text="To be added.")
        self.mapsEdgeObjIDLabel = uiLabel(
            master=self.mapsColumn, text="Edge Object ID:"
        )
        self.mapsEdgeObjIDEntry = EntryHelp(master=self.mapsColumn, text="To be added.")
        self.mapsDescLabel = uiLabel(master=self.mapsColumn, text="Desc:")
        self.mapsDescEntry = EntryHelp(master=self.mapsColumn, text="To be added.")
        self.mapsWidthLabel = uiLabel(master=self.mapsColumn, text="Width:")
        self.mapsWidthEntry = EntryHelp(master=self.mapsColumn, text="To be added.")
        self.mapsHeightLabel = uiLabel(master=self.mapsColumn, text="Height:")
        self.mapsHeightEntry = EntryHelp(master=self.mapsColumn, text="To be added.")

        # Place Map Widgets
        self.mapsColumn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.selectMapsCombo.grid(
            row=1, column=1, columnspan=2, padx=10, pady=10, ipadx=10, ipady=10
        )
        self.mapsLabel.grid(row=2, column=1, columnspan=2, sticky="nsew")
        self.mapsIDLabel.grid(row=3, column=1, sticky="nsew")
        self.mapsIDEntry.frame.grid(row=3, column=2, sticky="nsew")
        self.mapsNameLabel.grid(row=4, column=1, sticky="nsew")
        self.mapsNameEntry.frame.grid(row=4, column=2, sticky="nsew")
        self.mapsEdgeObjIDLabel.grid(row=5, column=1, sticky="nsew")
        self.mapsEdgeObjIDEntry.frame.grid(row=5, column=2, sticky="nsew")
        self.mapsDescLabel.grid(row=6, column=1, sticky="nsew")
        self.mapsDescEntry.frame.grid(row=6, column=2, sticky="nsew")
        self.mapsWidthLabel.grid(row=7, column=1, sticky="nsew")
        self.mapsWidthEntry.frame.grid(row=7, column=2, sticky="nsew")
        self.mapsWidthEntry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.mapsHeightLabel.grid(row=8, column=1, sticky="nsew")
        self.mapsHeightEntry.frame.grid(row=8, column=2, sticky="nsew")
        self.mapsHeightEntry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.mapsShowButton.grid(
            row=9,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.mapsUpdateButton.grid(
            row=10,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.mapsCreateButton.grid(
            row=11,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )
        self.mapsDeleteButton.grid(
            row=12,
            column=1,
            columnspan=2,
            sticky="nsew",
            ipadx=2,
            ipady=2,
            padx=10,
            pady=10,
        )

        self.init_entry_widgets()

    def init_entry_widgets(self):
        """
        Gets information from the loader and assigns current values for each setting type.
        """
        # TEAM
        self.teamData = self.ldr.team_templates
        self.teamNames = self.ldr.getTeamNames()
        print(self.teamNames)
        self.currentTeamData = self.teamData[self.teamNames[0]]

        self.selectTeamCombo.configure(values=self.teamNames)
        self.selectTeamCombo.current(0)
        self.selectTeamCombo.bind(
            "<<ComboboxSelected>>", self.change_team_entry_widgets
        )
        self.selectTeamCombo.bind("<Enter>", self.get_previous_team_combo)
        self.show_team_entry(self.currentTeamData)

        # COMPONENT
        self.componentData = self.ldr.comp_templates
        self.componentIDs = self.ldr.getCompIDs()
        # self.componentNames = self.ldr.
        self.componentTypes = self.ldr.getCompTypes()
        self.currentComponentData = self.componentData[self.componentIDs[0]]
        self.componentTypeAttr = self.currentComponentData.view_keys

        self.selectComponentCombo.configure(values=self.componentIDs)
        self.selectComponentCombo.current(0)
        self.selectComponentCombo.bind(
            "<<ComboboxSelected>>", self.change_components_entry_widgets
        )
        self.selectComponentCombo.bind("<Enter>", self.get_previous_component_combo)

        self.show_component_entries(self.currentComponentData)

        # OBJECT
        self.objectData = self.ldr.obj_templates
        self.objectIDs = self.ldr.getObjIDs()
        self.currentObjectData = self.objectData[self.objectIDs[0]]
        self.selectObjectsCombo.configure(values=self.objectIDs)
        self.selectObjectsCombo.current(0)
        self.selectObjectsCombo.bind(
            "<<ComboboxSelected>>", self.change_objects_entry_widgets
        )
        self.selectObjectsCombo.bind("<Enter>", self.get_previous_object_combo)

        self.show_object_entry(self.currentObjectData)

        # MAP
        self.mapData = self.ldr.map_templates
        self.mapIDs = self.ldr.getMapIDs()
        print(self.mapIDs)
        self.currentMapData = self.mapData[self.mapIDs[0]]

        self.selectMapsCombo.configure(values=self.mapIDs)
        self.selectMapsCombo.current(0)
        self.selectMapsCombo.bind(
            "<<ComboboxSelected>>", self.change_maps_entry_widgets
        )
        self.selectMapsCombo.bind("<Enter>", self.get_previous_map_combo)

        self.show_map_entry(self.currentMapData)

    def get_previous_component_combo(self, event):
        self.prev_component_combo = self.selectComponentCombo.current()

    def get_previous_object_combo(self, event):
        self.prev_object_combo = self.selectObjectsCombo.current()

    def get_previous_map_combo(self, event):
        self.prev_map_combo = self.selectMapsCombo.current()

    def get_previous_team_combo(self, event):
        self.prev_team_combo = self.selectTeamCombo.current()

    def change_team_entry_widgets(self, event=None):
        """
        Gets the correct team data for the currently selected team.
        """
        # the answer variable defaults to true
        self.answer = True
        self.get_focused_entry()
        # if any of the team entry values differ from their starting values,
        # the user is warned that they could be overwritten
        if not (
            (
                (self.teamNameEntry.entry.get() == self.currentTeamData["name"])
                and (
                    self.teamSizeEntry.entry.get() == str(self.currentTeamData["size"])
                )
                and (
                    self.callsignEntry.entry.get()
                    == self.currentTeamData["agent_defs"][0]["callsign"]
                )
                and (
                    self.squadEntry.entry.get()
                    == self.currentTeamData["agent_defs"][0]["squad"]
                )
                and (
                    self.agentObjectEntry.entry.get()
                    == self.currentTeamData["agent_defs"][0]["object"]
                )
                and (
                    self.aiFileEntry.entry.get()
                    == self.currentTeamData["agent_defs"][0]["AI_file"]
                )
            )
        ):
            self.answer = askyesno(
                title="confirmation",
                message="""Warning: You have modified Team values and have not Updated.
                  Your changes will not be saved. Are you sure you would like continue?""",
            )

        # the current team is successfully changed if the user made no changes,
        # or if the user confirms they are fine with their changes being overwritten
        if self.answer:
            # currentTeamIdx = self.selectTeamCombo.current()
            self.currentTeamData = self.teamData[self.selectTeamCombo.get()]
            self.show_team_entry(self.currentTeamData)
        else:
            self.selectTeamCombo.current(self.prev_team_combo)

    def change_components_entry_widgets(self, event):
        self.answer = True

        if self.currentComponentData.getData("ctype") == "CnC":
            ctype_attributes = self.CnCKeys
        elif self.currentComponentData.getData("ctype") == "FixedGun":
            ctype_attributes = self.FixedGunKeys
        elif self.currentComponentData.getData("ctype") == "Engine":
            ctype_attributes = self.EngineKeys
        elif self.currentComponentData.getData("ctype") == "Radar":
            ctype_attributes = self.RadarKeys
        elif self.currentComponentData.getData("ctype") == "Radio":
            ctype_attributes = self.RadioKeys
        elif self.currentComponentData.getData("ctype") == "Arm":
            ctype_attributes = self.ArmKeys

        if not (
            (
                (
                    self.componentsIDEntry.entry.get()
                    == self.currentComponentData.getData("id")
                )
                and (
                    self.componentsNameEntry.entry.get()
                    == self.currentComponentData.getData("name")
                )
                and (
                    self.componentsTypeCombo.get()
                    == self.currentComponentData.getData("ctype")
                )
                and (
                    self.componentsTypeAttr1Entry.entry.get()
                    == str(self.currentComponentData.getData(ctype_attributes[0]))
                )
                and (
                    (len(ctype_attributes) < 2)
                    or (
                        self.componentsTypeAttr2Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[1]))
                    )
                )
                and (
                    (len(ctype_attributes) < 3)
                    or self.currentComponentData.getData(ctype_attributes[2]) is None
                    or (
                        self.componentsTypeAttr3Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[2]))
                    )
                )
                and (
                    (len(ctype_attributes) < 4)
                    or (
                        self.componentsTypeAttr4Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[3]))
                    )
                )
                and (
                    (len(ctype_attributes) < 5)
                    or (
                        self.componentsTypeAttr5Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[4]))
                    )
                )
                and (
                    (len(ctype_attributes) < 6)
                    or (
                        self.componentsTypeAttr6Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[5]))
                    )
                )
                and (
                    (len(ctype_attributes) < 7)
                    or (
                        self.componentsTypeAttr7Entry.entry.get()
                        == str(self.currentComponentData.getData(ctype_attributes[6]))
                    )
                )
            )
        ):
            self.answer = askyesno(
                title="confirmation",
                message="""Warning: You have modified Component values and have not Updated.
                 Your changes will not be saved. Are you sure you would like continue?""",
            )

        if self.answer is True:
            currentComponentIdx = self.selectComponentCombo.current()
            self.componentTypeAttr = self.componentData[
                self.componentIDs[currentComponentIdx]
            ].view_keys
            self.currentComponentData = self.componentData[
                self.componentIDs[currentComponentIdx]
            ]
            self.show_component_entries(self.currentComponentData)
        else:
            print(self.prev_component_combo)
            self.selectComponentCombo.current(self.prev_component_combo)

    def change_objects_entry_widgets(self, event=None):
        self.answer = True
        print(self.currentObjectData.getData("comp_ids"))
        print(self.currentObjectData.getData("id"))
        print(self.currentObjectData.getData("name"))
        print(self.currentCompIDs)
        compIds = self.currentCompIDs
        if len(compIds) != 0:
            if compIds[-1] == "Add New Comp ID":
                compIds.pop(-1)
        print(compIds)
        print(self.currentObjectData.getData("comp_ids"))
        if not (
            (
                (
                    self.objectsIDEntry.entry.get()
                    == self.currentObjectData.getData("id")
                )
                and (
                    self.objectsNameEntry.entry.get()
                    == self.currentObjectData.getData("name")
                )
                and (
                    self.objectsFillAliveEntry.entry.get()
                    == self.currentObjectData.getData("fill_alive")
                )
                and (
                    self.objectsFillDeadEntry.entry.get()
                    == self.currentObjectData.getData("fill_dead")
                )
                and (
                    self.objectsTextEntry.entry.get()
                    == self.currentObjectData.getData("text")
                )
                and (
                    self.objectsHealthEntry.entry.get()
                    == str(self.currentObjectData.getData("health"))
                )
                and (
                    self.objectsDensityEntry.entry.get()
                    == str(self.currentObjectData.getData("density"))
                )
                and (compIds == self.currentObjectData.getData("comp_ids"))
                and (
                    bool(self.objectsPointsCountCombo.combobox.current())
                    == self.currentObjectData.getData("points_count")
                )
            )
        ):
            self.answer = askyesno(
                title="confirmation",
                message="""Warning: You have modified Object values and have not Updated.
                 Your changes will not be saved. Are you sure you would like continue?""",
            )

        if self.answer:
            currentObject = self.selectObjectsCombo.get()
            print(currentObject)
            self.currentObjectData = self.objectData[currentObject]

            self.show_object_entry(self.currentObjectData)
        else:
            self.selectObjectsCombo.current(self.prev_object_combo)

    def change_maps_entry_widgets(self, event=None):
        self.answer = True

        print(self.currentMapData.getData("name"))
        print(self.currentMapData.getData("edge_obj_id"))
        if not (
            (
                (self.mapsNameEntry.entry.get() == self.currentMapData.getData("name"))
                and (
                    self.mapsEdgeObjIDEntry.entry.get()
                    == self.currentMapData.getData("edge_obj_id")
                )
                and (
                    self.mapsDescEntry.entry.get()
                    == self.currentMapData.getData("desc")
                )
                and (
                    int(self.mapsWidthEntry.entry.get())
                    == self.currentMapData.getData("width")
                )
                and (
                    int(self.mapsHeightEntry.entry.get())
                    == self.currentMapData.getData("height")
                )
            )
        ):
            self.answer = askyesno(
                title="confirmation",
                message="""Warning: You have modified Map values and have not Updated.
                 Your changes will not be saved. Are you sure you would like continue?""",
            )
        if self.answer is True:
            currentMapID = self.selectMapsCombo.get()
            print(currentMapID)
            self.currentMapData = self.mapData[currentMapID]
            print(self.currentMapData)

            self.show_map_entry(self.currentMapData)
        else:
            self.selectMapsCombo.current()

    def show_component_entries(self, currentComp):
        """
        Updates the values in the component entry widgets.
        """
        self.componentTypeAttr = currentComp.view_keys
        self.componentsIDEntry.entry.delete(0, tk.END)
        self.componentsIDEntry.entry.insert(0, currentComp.getData("id"))
        self.componentsNameEntry.entry.delete(0, tk.END)
        self.componentsNameEntry.entry.insert(
            0,
            currentComp.getData("name"),
        )
        print(currentComp)
        self.componentsTypeCombo.configure(values=self.componentTypes)
        self.componentsTypeCombo.set(currentComp.getData("ctype"))
        self.componentsTypeLabel.config(text=currentComp.getData("ctype"))
        self.componentsTypeAttr1Entry.entry.configure(state="normal")
        self.componentsTypeAttr2Entry.entry.configure(state="normal")
        self.componentsTypeAttr3Entry.entry.configure(state="normal")
        self.componentsTypeAttr4Entry.entry.configure(state="normal")
        self.componentsTypeAttr5Entry.entry.configure(state="normal")
        self.componentsTypeAttr6Entry.entry.configure(state="normal")
        self.componentsTypeAttr7Entry.entry.configure(state="normal")
        self.componentsTypeAttr1Entry.help_button.configure(state="normal")
        self.componentsTypeAttr2Entry.help_button.configure(state="normal")
        self.componentsTypeAttr3Entry.help_button.configure(state="normal")
        self.componentsTypeAttr4Entry.help_button.configure(state="normal")
        self.componentsTypeAttr5Entry.help_button.configure(state="normal")
        self.componentsTypeAttr6Entry.help_button.configure(state="normal")
        self.componentsTypeAttr7Entry.help_button.configure(state="normal")
        self.componentsTypeAttr1Label.config(text="")
        self.componentsTypeAttr2Label.config(text="")
        self.componentsTypeAttr3Label.config(text="")
        self.componentsTypeAttr4Label.config(text="")
        self.componentsTypeAttr5Label.config(text="")
        self.componentsTypeAttr6Label.config(text="")
        self.componentsTypeAttr7Label.config(text="")
        self.componentsTypeAttr1Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr1Entry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr2Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr3Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr3Entry.entry.config(
            validate="key", validatecommand=(self.validateNum, "%P")
        )
        self.componentsTypeAttr4Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr5Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr6Entry.entry.delete(0, tk.END)
        self.componentsTypeAttr7Entry.entry.delete(0, tk.END)

        if currentComp.getData("ctype") == "CnC":
            self.componentsTypeAttr1Label.config(text=self.componentTypeAttr[4])
            self.componentsTypeAttr1Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[4])
            )
            self.componentsTypeAttr2Entry.entry.configure(state="readonly")
            self.componentsTypeAttr3Entry.entry.configure(state="readonly")
            self.componentsTypeAttr4Entry.entry.configure(state="readonly")
            self.componentsTypeAttr5Entry.entry.configure(state="readonly")
            self.componentsTypeAttr6Entry.entry.configure(state="readonly")
            self.componentsTypeAttr7Entry.entry.configure(state="readonly")
            self.componentsTypeAttr2Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr3Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr4Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr5Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr6Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr7Entry.help_button.configure(state="disabled")
        elif currentComp.getData("ctype") == "FixedGun":
            self.componentsTypeAttr3Entry.entry.configure(validate="none")
            self.componentsTypeAttr1Label.config(text=self.componentTypeAttr[4])
            self.componentsTypeAttr1Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[4])
            )
            self.componentsTypeAttr2Label.config(text=self.componentTypeAttr[5])
            self.componentsTypeAttr2Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[5])
            )
            self.componentsTypeAttr3Label.config(text=self.componentTypeAttr[6])
            self.componentsTypeAttr3Entry.entry.insert(
                0,
                (
                    currentComp.getData(self.componentTypeAttr[6])
                    if currentComp.getData("reloading") is not False
                    else "False"
                ),
            )
            self.componentsTypeAttr3Entry.entry.configure(
                state="readonly", validate="none"
            )
            self.componentsTypeAttr4Label.config(text=self.componentTypeAttr[7])
            self.componentsTypeAttr4Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[7])
            )
            self.componentsTypeAttr5Label.config(text=self.componentTypeAttr[8])
            self.componentsTypeAttr5Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[8])
            )
            self.componentsTypeAttr6Label.config(text=self.componentTypeAttr[9])
            self.componentsTypeAttr6Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[9])
            )
            self.componentsTypeAttr7Label.config(text=self.componentTypeAttr[10])
            self.componentsTypeAttr7Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[10])
            )
        elif currentComp.getData("ctype") == "Engine":
            self.componentsTypeAttr1Label.config(text=self.componentTypeAttr[4])
            self.componentsTypeAttr1Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[4])
            )
            self.componentsTypeAttr2Label.config(text=self.componentTypeAttr[5])
            self.componentsTypeAttr2Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[5])
            )
            self.componentsTypeAttr3Label.config(text=self.componentTypeAttr[6])
            self.componentsTypeAttr3Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[6])
            )
            self.componentsTypeAttr4Label.config(text=self.componentTypeAttr[7])
            self.componentsTypeAttr4Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[7])
            )
            self.componentsTypeAttr5Label.config(text=self.componentTypeAttr[8])
            self.componentsTypeAttr5Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[8])
            )
            self.componentsTypeAttr6Entry.entry.configure(state="readonly")
            self.componentsTypeAttr7Entry.entry.configure(state="readonly")
            self.componentsTypeAttr6Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr7Entry.help_button.configure(state="disabled")
        elif currentComp.getData("ctype") == "Radar":
            self.componentsTypeAttr1Entry.entry.configure(validate="none")
            self.componentsTypeAttr1Label.config(text=self.componentTypeAttr[4])
            self.componentsTypeAttr1Entry.entry.insert(
                0,
                (
                    currentComp.getData(self.componentTypeAttr[4])
                    if currentComp.getData("active") is not False
                    else "False"
                ),
            )
            self.componentsTypeAttr1Entry.entry.configure(
                state="readonly", validate="none"
            )
            self.componentsTypeAttr2Label.config(text=self.componentTypeAttr[5])
            self.componentsTypeAttr2Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[5])
            )
            self.componentsTypeAttr3Label.config(text=self.componentTypeAttr[6])
            self.componentsTypeAttr3Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[6])
            )
            self.componentsTypeAttr4Label.config(text=self.componentTypeAttr[7])
            self.componentsTypeAttr4Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[7])
            )
            self.componentsTypeAttr5Label.config(text=self.componentTypeAttr[8])
            self.componentsTypeAttr5Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[8])
            )
            self.componentsTypeAttr6Label.config(text=self.componentTypeAttr[9])
            self.componentsTypeAttr6Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[9])
            )
            self.componentsTypeAttr7Entry.entry.configure(state="readonly")
            self.componentsTypeAttr7Entry.help_button.configure(state="disabled")
        elif currentComp.getData("ctype") == "Radio":
            self.componentsTypeAttr3Entry.entry.configure(validate="none")
            self.componentsTypeAttr1Label.config(text="max_range")
            self.componentsTypeAttr1Entry.entry.insert(
                0, currentComp.getData("max_range")
            )
            self.componentsTypeAttr2Label.config(text="cur_range")
            self.componentsTypeAttr2Entry.entry.insert(
                0, currentComp.getData("cur_range")
            )
            self.componentsTypeAttr3Label.config(text="message")
            self.componentsTypeAttr3Entry.entry.insert(
                0,
                (
                    currentComp.getData("message")
                    if currentComp.getData("message") is not None
                    else "null"
                ),
            )
            self.componentsTypeAttr3Entry.entry.configure(state="readonly")
            self.componentsTypeAttr4Entry.entry.configure(state="readonly")
            self.componentsTypeAttr5Entry.entry.configure(state="readonly")
            self.componentsTypeAttr6Entry.entry.configure(state="readonly")
            self.componentsTypeAttr7Entry.entry.configure(state="readonly")
            self.componentsTypeAttr3Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr4Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr5Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr6Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr7Entry.help_button.configure(state="disabled")
        elif self.currentComponentData.getData("ctype") == "Arm":
            self.componentsTypeAttr3Entry.entry.configure(validate="none")
            self.componentsTypeAttr1Label.config(text=self.componentTypeAttr[4])
            self.componentsTypeAttr1Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[4])
            )
            self.componentsTypeAttr2Label.config(text=self.componentTypeAttr[5])
            self.componentsTypeAttr2Entry.entry.insert(
                0, currentComp.getData(self.componentTypeAttr[5])
            )
            self.componentsTypeAttr3Label.config(text=self.componentTypeAttr[6])
            self.componentsTypeAttr3Entry.entry.insert(
                0,
                (
                    currentComp.getData(self.componentTypeAttr[6])
                    if currentComp.getData(self.componentTypeAttr[6]) is not None
                    else "null"
                ),
            )
            self.componentsTypeAttr3Entry.entry.configure(state="readonly")
            self.componentsTypeAttr4Entry.entry.configure(state="readonly")
            self.componentsTypeAttr5Entry.entry.configure(state="readonly")
            self.componentsTypeAttr6Entry.entry.configure(state="readonly")
            self.componentsTypeAttr7Entry.entry.configure(state="readonly")
            self.componentsTypeAttr3Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr4Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr5Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr6Entry.help_button.configure(state="disabled")
            self.componentsTypeAttr7Entry.help_button.configure(state="disabled")

    def show_team_entry(self, currentTeam):
        """
        Updates the values stored in the team entry widgets.
        """
        self.teamNameEntry.entry.delete(0, tk.END)
        self.teamNameEntry.entry.insert(0, currentTeam["name"])
        self.teamSizeEntry.entry.delete(0, tk.END)
        self.teamSizeEntry.entry.insert(0, currentTeam["size"])
        self.callsignEntry.entry.delete(0, tk.END)
        self.callsignEntry.entry.insert(
            0, self.currentTeamData["agent_defs"][0]["callsign"]
        )
        self.squadEntry.entry.delete(0, tk.END)
        self.squadEntry.entry.insert(0, currentTeam["agent_defs"][0]["squad"])
        self.agentObjectEntry.entry.delete(0, tk.END)
        self.agentObjectEntry.entry.insert(0, currentTeam["agent_defs"][0]["object"])
        self.aiFileEntry.entry.delete(0, tk.END)
        self.aiFileEntry.entry.insert(0, currentTeam["agent_defs"][0]["AI_file"])

    def show_map_entry(self, currentMap):
        """
        Updates the values stored in the map entry widgets.
        """
        self.mapsIDEntry.entry.delete(0, tk.END)
        self.mapsIDEntry.entry.insert(0, self.selectMapsCombo.get())
        self.mapsNameEntry.entry.delete(0, tk.END)
        self.mapsNameEntry.entry.insert(0, currentMap.getData("name"))
        self.mapsEdgeObjIDEntry.entry.delete(0, tk.END)
        self.mapsEdgeObjIDEntry.entry.insert(
            0, self.currentMapData.getData("edge_obj_id")
        )
        self.mapsDescEntry.entry.delete(0, tk.END)
        self.mapsDescEntry.entry.insert(0, currentMap.getData("desc"))
        self.mapsWidthEntry.entry.delete(0, tk.END)
        self.mapsWidthEntry.entry.insert(0, currentMap.getData("width"))
        self.mapsHeightEntry.entry.delete(0, tk.END)
        self.mapsHeightEntry.entry.insert(0, currentMap.getData("height"))

    def show_object_entry(self, currentObj):
        """
        Updates the values stored in the object entry widgets.
        """
        self.objectsIDEntry.entry.delete(0, tk.END)
        self.objectsIDEntry.entry.insert(0, currentObj.getData("id"))
        self.objectsNameEntry.entry.delete(0, tk.END)
        self.objectsNameEntry.entry.insert(0, currentObj.getData("name"))
        self.objectsFillAliveEntry.entry.delete(0, tk.END)
        self.objectsFillAliveEntry.entry.insert(0, currentObj.getData("fill_alive"))
        self.objectsFillDeadEntry.entry.delete(0, tk.END)
        self.objectsFillDeadEntry.entry.insert(0, currentObj.getData("fill_dead"))
        self.objectsTextEntry.entry.delete(0, tk.END)
        self.objectsTextEntry.entry.insert(0, currentObj.getData("text"))
        self.objectsHealthEntry.entry.delete(0, tk.END)
        self.objectsHealthEntry.entry.insert(0, currentObj.getData("health"))
        self.objectsDensityEntry.entry.delete(0, tk.END)
        self.objectsDensityEntry.entry.insert(0, currentObj.getData("density"))
        self.currentCompIDs = currentObj.getData("comp_ids")[:]
        print(self.currentCompIDs)
        self.objectsCompIDsCombo.combobox.set("")
        self.objectsCompIDsCombo.combobox.configure(values=self.currentCompIDs)
        if len(self.currentCompIDs) != 0:
            self.objectsCompIDsCombo.combobox.current(0)
        self.objectsCompIDsCombo.combobox.bind("<<ComboboxSelected>>", self.get_current_comp_id)
        self.objectsCompIDsCombo.combobox.bind("<Enter>", self.add_empty_comp_id)
        self.objectsCompIDsCombo.combobox.bind("<Return>", self.add_new_comp_id)
        self.objectsCompIDsCombo.combobox.bind("<KeyRelease>", self.delete_comp_id)
        self.objectsPointsCountCombo.combobox.configure(values=["False", "True"])
        self.objectsPointsCountCombo.combobox.config(state="normal")
        if bool(currentObj.getData("points_count")) is True:
            self.objectsPointsCountCombo.combobox.current(1)
        else:
            self.objectsPointsCountCombo.combobox.current(0)
        self.objectsPointsCountCombo.combobox.config(state="readonly")

    def add_empty_comp_id(self, event):
        """
        Adds an empty component ID for users to select to add new component ID.
        """
        if len(self.currentCompIDs) == 0:
            self.currentCompIDs.append("Add New Comp ID")
            self.objectsCompIDsCombo.combobox.configure(values=self.currentCompIDs)
        elif self.currentCompIDs[-1] != "Add New Comp ID":
            self.currentCompIDs.append("Add New Comp ID")
            self.objectsCompIDsCombo.combobox.configure(values=self.currentCompIDs)

    def get_current_comp_id(self, event):
        self.currentCompIDIdx = self.objectsCompIDsCombo.combobox.current()
        self.currentCompID = self.objectsCompIDsCombo.combobox.get()

    def delete_comp_id(self, event):
        currentCompID = self.objectsCompIDsCombo.combobox.get()
        if len(currentCompID) == 0:
            if self.currentCompIDIdx != len(self.currentCompIDs) - 1:
                self.currentCompIDs.pop(self.currentCompIDIdx)
                self.objectsCompIDsCombo.combobox.configure(values=self.currentCompIDs)

    def add_new_comp_id(self, event):
        newComboID = self.objectsCompIDsCombo.combobox.get()
        newComboIDIndex = self.currentCompIDIdx
        print(newComboIDIndex)
        if newComboID not in self.currentCompIDs and newComboID.strip() != "":
            self.currentCompIDs[newComboIDIndex] = newComboID
            self.objectsCompIDsCombo.combobox.configure(values=self.currentCompIDs)
            self.objectsCompIDsCombo.combobox.set(newComboID)

    ### UPDATE JSON FILES###
    def update_teams_json(self):
        if (
            self.teamNameEntry.entry.get() in self.teamData.keys()
            and self.teamNameEntry.entry.get() != self.selectTeamCombo.get()
        ):
            showwarning(
                title="Warning",
                message="The name you are trying to use is already in use by another team. Please use another name.",
            )
        else:
            if (
                self.teamSizeEntry.entry.get() != ""
                and self.callsignEntry.entry.get() != ""
                and self.teamNameEntry.entry.get() != ""
                and self.squadEntry.entry.get() != ""
                and self.agentObjectEntry.entry.get() != ""
                and self.aiFileEntry.entry.get() != ""
            ):
                self.currentTeamData["size"] = int(self.teamSizeEntry.entry.get())
                self.currentTeamData["agent_defs"][0][
                    "callsign"
                ] = self.callsignEntry.entry.get()
                self.currentTeamData["name"] = self.teamNameEntry.entry.get()
                self.currentTeamData["agent_defs"][0][
                    "squad"
                ] = self.squadEntry.entry.get()
                self.currentTeamData["agent_defs"][0][
                    "object"
                ] = self.agentObjectEntry.entry.get()
                self.currentTeamData["agent_defs"][0][
                    "AI_file"
                ] = self.aiFileEntry.entry.get()

                self.teamData.update(
                    {self.currentTeamData["name"]: self.currentTeamData}
                )

                self.teamsJSON = json.dumps(self.teamData, indent=4)

                with open("settings/teams.json", "r") as f:
                    teamJSON = json.load(f)

                if self.currentTeamData["name"] != self.selectTeamCombo.get():
                    if self.selectTeamCombo.get() in teamJSON:
                        teamJSON.pop(self.selectTeamCombo.get())
                    if self.selectTeamCombo.get() in self.teamData:
                        self.teamData.pop(self.selectTeamCombo.get())
                    self.teamNames.pop(self.selectTeamCombo.current())
                    self.teamNames.append(self.currentTeamData["name"])
                    self.selectTeamCombo.config(values=self.teamNames)
                    self.selectTeamCombo.current(len(self.teamNames) - 1)

                teamJSON[self.currentTeamData["name"]] = self.currentTeamData

                self.teamData[self.currentTeamData["name"]] = self.currentTeamData

                f.close()

                with open("settings/teams.json", "w") as f:
                    json.dump(teamJSON, f, indent=4)
                f.close()

    def update_components_json(self):
        if (
            self.componentsIDEntry.entry.get() in self.componentData.keys()
            and self.componentsIDEntry.entry.get() != self.selectComponentCombo.get()
        ):
            showwarning(
                title="Warning",
                message="The ID you are trying to use is already in use by another component. Please use another ID.",
            )
        else:
            if (
                self.componentsIDEntry.entry.get() != ""
                and self.componentsNameEntry.entry.get() != ""
                and self.componentsTypeAttr1Entry.entry.get() != ""
                and self.componentsTypeAttr2Entry.entry.get() != ""
                and self.componentsTypeAttr3Entry != ""
            ):
                self.currentComponentData.setData(
                    "id", self.componentsIDEntry.entry.get()
                )
                self.currentComponentData.setData(
                    "name", self.componentsNameEntry.entry.get()
                )
                self.currentComponentData.setData(
                    "ctype", self.componentsTypeCombo.get()
                )
                if self.currentComponentData.getData("ctype") == "CnC":
                    self.currentComponentData.setData(
                        "max_cmds_per_tick",
                        int(self.componentsTypeAttr1Entry.entry.get()),
                    )
                if self.currentComponentData.getData("ctype") == "FixedGun":
                    self.currentComponentData.setData(
                        "reload_ticks", int(self.componentsTypeAttr1Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "reload_ticks_remaining",
                        int(self.componentsTypeAttr2Entry.entry.get()),
                    )
                    self.currentComponentData.setData(
                        "reloading",
                        (
                            self.componentsTypeAttr3Entry.entry.get()
                            if self.componentsTypeAttr3Entry.entry.get() != "False"
                            else False
                        ),
                    )
                    self.currentComponentData.setData(
                        "ammunition", int(self.componentsTypeAttr4Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "min_damage", int(self.componentsTypeAttr5Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "max_damage", int(self.componentsTypeAttr6Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "range", int(self.componentsTypeAttr7Entry.entry.get())
                    )
                if self.currentComponentData.getData("ctype") == "Engine":
                    self.currentComponentData.setData(
                        "min_speed", float(self.componentsTypeAttr1Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "max_speed", float(self.componentsTypeAttr2Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "cur_speed", float(self.componentsTypeAttr3Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "max_turnrate", float(self.componentsTypeAttr4Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "cur_turnrate", float(self.componentsTypeAttr5Entry.entry.get())
                    )
                if self.currentComponentData.getData("ctype") == "Radar":
                    self.currentComponentData.setData(
                        "active",
                        (
                            self.componentsTypeAttr1Entry.entry.get()
                            if self.componentsTypeAttr1Entry.entry.get() != "False"
                            else False
                        ),
                    )
                    self.currentComponentData.setData(
                        "range", int(self.componentsTypeAttr2Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "level", int(self.componentsTypeAttr3Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "visarc", int(self.componentsTypeAttr4Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "offset_angle", int(self.componentsTypeAttr5Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "resolution", int(self.componentsTypeAttr6Entry.entry.get())
                    )
                if self.currentComponentData.getData("ctype") == "Radio":
                    self.currentComponentData.setData(
                        "max_range", int(self.componentsTypeAttr1Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "cur_range", int(self.componentsTypeAttr2Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "message",
                        (
                            self.componentsTypeAttr3Entry.entry.get()
                            if self.componentsTypeAttr3Entry.entry.get() != ""
                            else None
                        ),
                    )
                if self.currentComponentData.getData("ctype") == "Arm":
                    self.currentComponentData.setData(
                        "max_weight", int(self.componentsTypeAttr1Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "max_bulk", int(self.componentsTypeAttr2Entry.entry.get())
                    )
                    self.currentComponentData.setData(
                        "item",
                        (
                            self.componentsTypeAttr3Entry.entry.get()
                            if self.componentsTypeAttr3Entry.entry.get() != "null"
                            else None
                        ),
                    )

                with open("settings/components.json", "r") as f:
                    componentJSON = json.load(f)

                if (
                    self.currentComponentData.getData("id")
                    != self.selectComponentCombo.get()
                ):
                    if self.selectComponentCombo.get() in componentJSON:
                        componentJSON.pop(self.selectComponentCombo.get())
                    if self.selectComponentCombo.get() in self.componentData:
                        self.componentData.pop(self.selectComponentCombo.get())
                    self.componentIDs.pop(self.selectComponentCombo.current())
                    self.componentIDs.append(self.currentComponentData.getData("id"))
                    self.selectComponentCombo.configure(values=self.componentIDs)
                    self.selectComponentCombo.current(len(self.componentIDs) - 1)

                componentJSON[self.currentComponentData.getData("id")] = (
                    self.currentComponentData.getSelfView()
                )
                f.close()

                self.componentData[self.currentComponentData.getData("id")] = (
                    self.currentComponentData
                )

                if (
                    "slot_id"
                    in componentJSON[self.currentComponentData.getData("id")].keys()
                ):
                    componentJSON[self.currentComponentData.getData("id")].pop(
                        "slot_id"
                    )

                with open("settings/components.json", "w") as f:
                    json.dump(componentJSON, f, indent=4)
                f.close()

    def update_objects_json(self):
        if (
            self.objectsIDEntry.entry.get() in self.objectData.keys()
            and self.objectsIDEntry.entry.get() != self.selectObjectsCombo.get()
        ):
            showwarning(
                title="Warning",
                message="The ID you are trying to use is already in use by another object. Please use another ID.",
            )
        else:
            if (
                self.objectsIDEntry.entry.get() != ""
                and self.objectsNameEntry.entry.get() != ""
                and self.objectsFillDeadEntry.entry.get() != ""
                and self.objectsFillAliveEntry.entry.get() != ""
                and self.objectsTextEntry.entry.get() != ""
                and self.objectsHealthEntry.entry.get() != ""
                and self.objectsDensityEntry.entry.get() != ""
            ):
                self.currentObjectData.setData("id", self.objectsIDEntry.entry.get())
                self.currentObjectData.setData(
                    "name", self.objectsNameEntry.entry.get()
                )
                self.currentObjectData.setData(
                    "fill_alive", self.objectsFillAliveEntry.entry.get()
                )
                self.currentObjectData.setData(
                    "fill_dead", self.objectsFillDeadEntry.entry.get()
                )
                self.currentObjectData.setData(
                    "text", self.objectsTextEntry.entry.get()
                )
                self.currentObjectData.setData(
                    "health", int(self.objectsHealthEntry.entry.get())
                )
                self.currentObjectData.setData(
                    "density", int(self.objectsDensityEntry.entry.get())
                )
                if len(self.currentCompIDs) != 0:
                    if self.currentCompIDs[-1] == "Add New Comp ID":
                        self.currentCompIDs.pop(-1)
                self.currentObjectData.setData("comp_ids", self.currentCompIDs)
                self.currentObjectData.setData(
                    "points_count", bool(self.objectsPointsCountCombo.combobox.current())
                )

                print(self.currentObjectData.getJSONView())
                with open("settings/objects.json", "r") as f:
                    objectJSON = json.load(f)

                print(self.selectObjectsCombo.get())
                if (
                    self.currentObjectData.getData("id")
                    != self.selectObjectsCombo.get()
                ):
                    if self.selectObjectsCombo.get() in objectJSON:
                        objectJSON.pop(self.selectObjectsCombo.get())
                    if self.selectObjectsCombo.get() in self.objectData:
                        self.objectData.pop(self.selectObjectsCombo.get())
                    self.objectIDs.pop(self.selectObjectsCombo.current())
                    self.objectIDs.append(self.currentObjectData.getData("id"))
                    self.selectObjectsCombo.configure(values=self.objectIDs)
                    self.selectObjectsCombo.current(len(self.objectIDs) - 1)

                objectJSON[self.currentObjectData.getData("id")] = (
                    self.currentObjectData.getJSONView()
                )

                self.objectData[self.currentObjectData.getData("id")] = (
                    self.currentObjectData
                )

                if "slot_id" in objectJSON[self.currentObjectData.getData("id")].keys():
                    objectJSON[self.currentObjectData.getData("id")].pop("slot_id")
                f.close()

                with open("settings/objects.json", "w") as f:
                    json.dump(objectJSON, f, indent=4)
                f.close()
                print(self.objectData)

    def update_maps_json(self):

        if (
            self.mapsIDEntry.entry.get() in self.mapData.keys()
            and self.mapsIDEntry.entry.get() != self.selectMapsCombo.get()
        ):
            showwarning(
                title="Warning",
                message="The ID you are trying to use is already in use by another map. Please use another ID.",
            )
        else:
            if (
                self.mapsNameEntry.entry.get() != ""
                and self.mapsEdgeObjIDEntry.entry.get() != ""
                and self.mapsDescEntry.entry.get() != ""
                and self.mapsWidthEntry.entry.get != ""
                and self.mapsHeightEntry.entry.get() != ""
            ):
                self.currentMapData.setData("name", self.mapsNameEntry.entry.get())
                self.currentMapData.setData(
                    "edge_obj_id", self.mapsEdgeObjIDEntry.entry.get()
                )
                self.currentMapData.setData("desc", self.mapsDescEntry.entry.get())
                self.currentMapData.setData(
                    "width", int(self.mapsWidthEntry.entry.get())
                )
                self.currentMapData.setData(
                    "height", int(self.mapsHeightEntry.entry.get())
                )
                with open("settings/maps.json", "r") as f:
                    mapJSON = json.load(f)
                    print(self.currentMapData.data)
                    mapJSON[self.selectMapsCombo.get()] = self.currentMapData.data
                f.close()

                with open("settings/maps.json", "w") as f:
                    json.dump(mapJSON, f, indent=4)
                f.close()

    ### CREATE NEW ###

    def create_team(self):
        self.teamID = askstring("Team ID", "Please enter an ID for the new team.")
        while len(self.teamID) == 0 or self.teamID in self.teamData.keys():
            if len(self.teamID) == 0:
                messagebox.showwarning(
                    "Warning", "You must enter a team ID to continue"
                )
            else:
                messagebox.showwarning(
                    "Warning", "This ID already exists, please enter a new ID."
                )
            self.teamID = askstring("Team ID", "Please enter an ID for the new team.")
        if len(self.teamID) != 0:
            self.teamNames.append(self.teamID)
            self.selectTeamCombo.configure(values=self.teamNames)
            self.selectTeamCombo.current(len(self.teamNames) - 1)
            self.currentTeamData = {
                "size": "",
                "name": self.teamID,
                "agent_defs": [
                    {"callsign": "", "squad": "", "object": "", "AI_file": ""}
                ],
            }
            self.teamData.update({self.teamID: self.currentTeamData})
            self.show_team_entry(self.currentTeamData)

    def create_component(self):
        self.componentID = askstring(
            "Component ID", "Please enter an ID for the new component."
        )
        while (
            len(self.componentID) == 0 or self.componentID in self.componentData.keys()
        ):
            if len(self.componentID) == 0:
                messagebox.showwarning(
                    "Warning", "Please enter an ID for the new component"
                )
            else:
                messagebox.showwarning(
                    "Warning", "This ID already exists, please enter a new ID."
                )
            self.componentID = askstring(
                "Component ID", "Please enter an ID for the new component."
            )
        if len(self.componentID) != 0:
            self.componentIDs.append(self.componentID)
            self.selectComponentCombo.configure(values=self.componentIDs)
            self.selectComponentCombo.current(len(self.componentIDs) - 1)
            self.newDict = {"id": self.componentID, "name": "", "ctype": ""}

            if self.componentsTypeCombo.get() == "CnC":
                self.newDict["ctype"] = "CnC"
                for key in self.CnCKeys:
                    self.newDict[key] = ""
            elif self.componentsTypeCombo.get() == "FixedGun":
                self.newDict["ctype"] = "FixedGun"
                for key in self.FixedGunKeys:
                    self.newDict[key] = ""
                self.newDict["reloading"] = False
            elif self.componentsTypeCombo.get() == "Engine":
                self.newDict["ctype"] = "Engine"
                for key in self.EngineKeys:
                    self.newDict[key] = ""
            elif self.componentsTypeCombo.get() == "Radar":
                self.newDict["ctype"] = "Radar"
                for key in self.RadarKeys:
                    self.newDict[key] = ""
                self.newDict["active"] = False
            elif self.componentsTypeCombo.get() == "Radio":
                self.newDict["ctype"] = "Radio"
                for key in self.RadioKeys:
                    self.newDict[key] = ""
            elif self.componentsTypeCombo.get() == "Arm":
                self.newDict["ctype"] = "Arm"
                for key in self.ArmKeys:
                    self.newDict[key] = ""

            print(self.newDict)
            self.currentComponentData = comp.Comp(self.newDict)

            self.componentData[self.componentID] = self.currentComponentData
            self.show_component_entries(self.currentComponentData)

    def create_object(self):
        self.objectID = askstring("Object ID", "Please enter an ID for the new object.")
        while len(self.objectID) == 0 or self.objectID in self.objectData:
            if len(self.objectID) == 0:
                messagebox.showwarning(
                    "Warning", "Please enter an ID for the new object"
                )
            else:
                messagebox.showwarning(
                    "Warning", "This ID already exists, please enter a new ID."
                )
            self.objectID = askstring(
                "Object ID", "Please enter an ID for the new object."
            )
        if len(self.objectID) != 0:
            self.objectIDs.append(self.objectID)
            self.selectObjectsCombo.configure(values=self.objectIDs)
            self.selectObjectsCombo.current(len(self.objectIDs) - 1)
            self.currentObjectData = obj.Object(
                {
                    "id": self.objectID,
                    "name": "",
                    "fill_alive": "",
                    "fill_dead": "",
                    "text": "",
                    "health": "",
                    "density": "",
                    "comp_ids": [],
                    "points_count": "",
                }
            )
            self.objectData[self.objectID] = self.currentObjectData
            self.show_object_entry(self.currentObjectData)

    def create_map(self):
        self.mapName = askstring("Map Name", "Please enter a name for a new map.")
        while len(self.mapName) == 0 or self.mapName in self.mapData.keys():
            if len(self.mapName) == 0:
                messagebox.showwarning("Warning", "Please enter an ID for the new map")
            else:
                messagebox.showwarning(
                    "Warning", "This Name already exists, please enter a new Name."
                )
            self.mapName = askstring("Map Name", "Please enter a name for a new map.")
        if len(self.mapName) != 0:
            self.mapIDs.append(self.mapName)
            self.selectMapsCombo.configure(values=self.mapIDs)
            self.selectMapsCombo.current(len(self.mapIDs) - 1)
            self.currentMapData = zmap.Map(
                {
                    "name": "",
                    "edge_obj_id": "",
                    "desc": "",
                    "width": "",
                    "height": "",
                    "placed_objects": {},
                    "placed_items": {},
                    "sides": {},
                    "win_states": [],
                }
            )
            self.mapData[self.mapName] = self.currentMapData
            self.show_map_entry(self.currentMapData)

    ### DELETE ###

    def delete_team(self):
        if self.selectTeamCombo.get() in self.teamData:
            self.teamData.pop(self.selectTeamCombo.get())
            self.teamNames.pop(self.selectTeamCombo.current())

            with open("settings/teams.json", "r") as f:
                teamJSON = json.load(f)
            f.close()
            teamJSON.pop(self.selectTeamCombo.get())
            with open("settings/teams.json", "w") as f:
                json.dump(teamJSON, f, indent=4)
            f.close()

            self.selectTeamCombo.configure(values=self.teamNames)
            self.selectTeamCombo.current(len(self.teamNames) - 1)
            self.change_team_entry_widgets()

    def delete_components(self):
        if self.selectComponentCombo.get() in self.componentData:
            self.componentData.pop(self.selectComponentCombo.get())

            with open("settings/components.json", "r") as f:
                componentJSON = json.load(f)
                componentJSON.pop(self.selectComponentCombo.get())
            f.close()
            with open("settings/components.json", "w") as f:
                json.dump(componentJSON, f, indent=4)
            f.close()
        self.componentIDs.pop(self.selectComponentCombo.current())
        self.selectComponentCombo.configure(values=self.componentIDs)
        self.selectComponentCombo.current(len(self.componentIDs) - 1)
        self.change_components_entry_widgets()

    def delete_object(self):
        if self.selectObjectsCombo.get() in self.objectData:
            self.objectData.pop(self.selectObjectsCombo.get())
            self.objectIDs.pop(self.selectObjectsCombo.current())
            self.selectObjectsCombo.configure(values=self.objectIDs)
            self.selectObjectsCombo.current(len(self.objectIDs) - 1)
            self.change_objects_entry_widgets()

    def delete_map(self):
        if self.selectMapsCombo.get() in self.mapData:
            self.mapData.pop(self.selectMapsCombo.get())
            with open("settings/maps.json", "r") as f:
                mapJSON = json.load(f)
                mapJSON.pop(self.selectMapsCombo.get())
            f.close()
            with open("settings/maps.json", "w") as f:
                json.dump(mapJSON, f, indent=4)
            f.close()
        self.mapIDs.pop(self.selectMapsCombo.current())
        self.selectMapsCombo.configure(values=self.mapIDs)
        self.selectMapsCombo.current(len(self.mapIDs) - 1)
        self.change_maps_entry_widgets()

    ### SHOW MAP WINDOW ###
    def show_map(self):
        self.UIMap = ui_map_config.UIMapConfig(
            self.currentMapData, self, logger=self.logger
        )
