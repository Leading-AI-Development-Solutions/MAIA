import ai_helpers as aih

class AI:
    def __init__(self):
        None
        
    def initData(self,sim_data):
        self.sim_data = sim_data

        self.cmd_maker = aih.CmdMaker()


    # Implement AI here.
    # IMPORTANT: Must return commands a dictionary that follows the command
    # specifications. Can return empty dictionary or None if there are no
    # commands.
    def runAI(self,data):
        print(data['self'])
        self.cmd_maker.addCmd(0,2,aih.CMD_SetSpeed(1.0))

        return self.cmd_maker.getCmds()
