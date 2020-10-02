import logging
import agent

class Team:
    def __init__(self,data):
        self.data={}
        self.logger = None

        if 'name' in data:
            self.logger = logging.getLogger(data['name'])
            self.handler = logging.FileHandler('log/'+self.logger.name+'.log',mode='w')
            self.formatter = logging.Formatter('%(name)s - %(message)s')
            self.handler.setFormatter(self.formatter)
            self.logger.addHandler(self.handler)
        else:
            raise KeyError('name')


        self.required_data=[]

        self.setData(data)

        self.createAgents()

    def setData(self,data):

        # Agents are created later based on agent_defs read from the json
        self.data['agents']={}

        req_data = [
            'size','agent_defs'
        ]

        for rd in req_data:
            if rd in data:
                self.data[rd] = data[rd]
            else:
                self.data[rd] = None
                self.logger.error("TEAM: Missing data "+rd)

        self.required_data += req_data

    def getData(self,key):
        if key in self.data:
            return self.data[key]
        else:
            return None

    def getNumberOfAgents(self):
        if 'agents' in self.data:
            return len(self.data['agents'])
        else:
            0

    def createAgents(self):
        agent_defs = self.getData('agent_defs')
        
        if agent_defs == None:
            self.logger.error("AGENT: Agent definition data is missing.")
        else:
            for ID,data in agent_defs.items():
                ID = int(ID)
                objid = data['object']
                ai_filename = data['AI_file']

                _agent = agent.Agent(ID,objid,ai_filename)
                self.data['agents'][ID]=_agent
                
