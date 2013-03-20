import math
import random


class Agent(object):    

    firstIteration = 1
    
    
    
    numAgents = 3
    numFoes = 3
    
    set1 = False
    set2 = False
    reset1 = 0
    reset2 = 0
    
    
    ammo = [False, False, False]
    orders = [None, None, None]
    allyLocs = [None, None, None]
    enemyLocs = [None, None, None]
    distance = [(1000,1000,1000), (1000,1000,1000)]
    
    tilesize = 16 #based on value in Settings
    
    cps1loc = (14.5*tilesize, 3.5*tilesize)
    cps2loc = (16.5*tilesize, 13.5*tilesize)
    ammo1loc = (11.5*tilesize, 10.5*tilesize)
    ammo2loc = (19.5*tilesize, 6.5*tilesize)
    ammoloc = [ammo1loc, ammo2loc]        
    cpsloc = [cps1loc, cps2loc]
    
    epsilon = 0.9
    gamma = 0.9
    gradientLearningRate = 0.05
     
    
    
    # state  = wie ammo heeft; locaties cps + wie ze heeft; ammospawn1, ammospawn2, allyLocs; enemyLocs (als ie ze ziet)
    state = [ammo, ((216, 56,-1),(248, 216, -1)), (True, True), allyLocs, enemyLocs]    
    lastState = None
    
    numActions = 5;    
    actionNames = ['cps1loc', 'cps2loc', 'ammo1loc', 'ammo2loc', 'stay in place', 'shoot']
    # shoot is not part of learning model
    
    maxNrSteps = 15
    
    maxTime = 50
    
    activeActions = [None]*3
    
    
                        
    featureVector = {       'as1 filled':    1, 
                            'as2 filled':    1,
                            'cp1 of us':      0, 
                            'cp2 of us':      0,
                            'distance to cp1': 0,
                            'distance to cp2': 0,
                            'Am I closest ally to cp1': 0, 
                            'Am I closest ally to cp2': 0,
                            'distance to as1': 0,
                            'distance to as2': 0,
                            'Am I closest ally to as1' : 0,
                            'Am I closest ally to as2' : 0,
                            'ammo amount': 0,
                            'nearest enemy distance to cp1': 0,
                            'nearest enemy distance to cp2' : 0,
                            'nearest enemy distance to as1' : 0,
                            'nearest enemy distance to as2' : 0,
                            'Am I dead': 0
                    }
                        
    parameterVectors = [{   'as1 filled':    0, 
                            'as2 filled':    0,
                            'cp1 of us':      0, 
                            'cp2 of us':      0,
                            'distance to cp1': 0,
                            'distance to cp2': 0,
                            'Am I closest ally to cp1': 0,
                            'Am I closest ally to cp2': 0,
                            'distance to as1': 0,
                            'distance to as2': 0,
                            'Am I closest ally to as1' : 0,
                            'Am I closest ally to as2' : 0,
                            'ammo amount': 0,
                            'nearest enemy distance to cp1': 0,
                            'nearest enemy distance to cp2' : 0,
                            'nearest enemy distance to as1' : 0,
                            'nearest enemy distance to as2' : 0,
                            'Am I dead': 0
                        }     
                        for i in range(numActions)]

    #blobdict = [None]*numActions

    NAME = "False Dmitriy I"
    
    printStuff = True
    
    onServer = False
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None, tilesize=None, **kwargs):
        """ Each agent is iniftialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.mesh = nav_mesh
        self.grid = field_grid
        self.settings = settings
        self.goal = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        
        
        # Read the binary blob, we're not using it though
        if blob is not None:
            
            try:
                blobObject = pickle.loads(blob.read())
                blob.seek(0) 
                if(Agent.printStuff):
                    print "Agent %s received binary blob of %s" % (
                   self.callsign, type(blobObject))
                Agent.parameterVectors = blobObject
            
                #print blob.read()
                #blob.seek(0) 
                #print blob
                #print Agent.parameterVectors
                
          
            except Exception, e:
                print "Could not read pickle as array."
                self.initParameterVectorsRandom()
                
            except:
                print "Unexpected error:", sys.exc_info()[0]
                self.initParameterVectorsRandom()
        
        else:
            self.initParameterVectorsRandom()
        
        
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)
        self.addNodeToMesh((21.5*16, 7.5*16))
        self.addNodeToMesh((7.5*16,9.5*16))
        
        self.featureVector = copy.deepcopy(Agent.featureVector)
        self.oldStateActionValue = 0
        self.lastaction = None #old
        
        self.lastFeatureVector = None
        self.lastActionNumber = None
        self.actionNumber = None
        self.oldActionNumber = None
        
        self.nrSteps = 0
        self.reward = 0
        self.isDead = False
        
        
        
    def addNodeToMesh(self, node):
        max_speed = self.settings.max_speed # - some value as they seem to slow down otherwise
        self.mesh[node] = dict([(n, math.ceil(point_dist(node,n) / float(max_speed)) * max_speed)  for n in self.mesh if not line_intersects_grid(node,n,self.grid,16)])
   
    def initParameterVectorsRandom(self):
        for i in range(Agent.numActions):
            for key in Agent.parameterVectors[i]:
                Agent.parameterVectors[i][key] = random.uniform(0,1) #between 0 and 1


    def calcPathTime(self, path, curTurn, curLoc):
        time = 0
        for subGoal in path: #for each subGoal               
            while curLoc != subGoal: #calc moves untill reached 
                dx = subGoal[0] - curLoc[0]
                dy = subGoal[1] - curLoc[1]               
                speed = ( dx ** 2 + dy ** 2 ) ** 0.5
                if speed < self.settings.tilesize: #goal reached
                    break
                if speed > self.settings.max_speed: #cant go faster than allowed :(
                    speed = self.settings.max_speed
                turn = angle_fix( math.atan2(dy, dx) - curTurn )
                if abs(turn) > self.settings.max_turn: #cant turn more than allowed :(
                    turn = self.settings.max_turn*turn/math.fabs(turn)
                    speed = self.reducedSpeed(curTurn, dy, dx, speed) #modify speed
                curTurn = curTurn + turn
                if curTurn >= math.pi: #fix of angles
                    curTurn -= -2*math.pi
                elif curTurn < -math.pi: #fix of angles
                    curTurn += 2*math.pi
                #update new location
                curLoc0 = round(curLoc[0] + math.cos(curTurn)*speed)
                curLoc1 = round(curLoc[1] + math.sin(curTurn)*speed)
                curLoc = (curLoc0, curLoc1)
                time += 1
        return time
    
    def reducedSpeed(self, startTurn, diffy, diffx, speed):
        maxSpeed = self.settings.max_speed
        turn = self.settings.max_turn
        tempspeed = maxSpeed
        #move in y direction while rotating if turned to +y only
        if(diffy > 0 and diffy < maxSpeed and startTurn+turn < 0 and startTurn+turn > -math.pi):
                tempspeed = diffy/math.sin(startTurn + turn)
                if(tempspeed < speed):
                        speed = tempspeed
        elif(diffy < 0 and -diffy < maxSpeed and startTurn+turn > 0):
                tempspeed = diffy/math.sin(startTurn + turn)
                if(tempspeed < speed):
                        speed = tempspeed
        #move in x direction while rotatingif turned to +x only
        if(diffx > 0 and diffx < maxSpeed and startTurn+turn > -math.pi/2 and startTurn+turn < math.pi/2):
                tempspeed = diffx/math.cos(startTurn+turn)
                if(tempspeed < speed):
                        speed = tempspeed
        elif(diffx < 0 and -diffx < maxSpeed and startTurn+turn < -math.pi/2 or startTurn+turn > math.pi/2):
                tempspeed = diffx/math.cos(startTurn+turn)
                if(tempspeed < speed):
                        speed = tempspeed
        if(tempspeed == maxSpeed):
                speed = 0
        if( speed < maxSpeed):
                speed = 0
        return speed
            

    def inVisionRange(self, loc1, loc2):
        if(point_dist(loc1, loc2) <= self.settings.max_see):
            return True
        else:
            return False
        
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected

        if (self.id == 0):
            Agent.lastState = copy.deepcopy(Agent.state)
            
            
        #Set global location variable
        Agent.state[3][self.id] = (observation.loc, observation.angle)

        #Set visible enemy locations #TODO: keep track of enemy to predict movement/strategy
        if self.id == 0:
            Agent.state[4] = [None, None,None]
        if observation.foes:
       
            for foe in observation.foes:
                if  foe not in self.state[4]: 
                   for n in range(0, len(Agent.state[4])):
                       if self.state[4][n] == None:
                            Agent.state[4][n] =foe
                            break
        # we are ded! 
        if observation.respawn_in > 0:
            Agent.orders[self.id] = None
        
        #update ammo status 
        if (observation.step - self.reset1)> 8 and self.set1 == True:
            Agent.state[2] = (True, Agent.state[2][1])
        if (observation.step - self.reset2)> 8 and self.set2 == True:
            Agent.state[2] =(Agent.state[2][0], True)
        
        ammopacks = filter(lambda x: x[2] == "Ammo", observation.objects)
        #print "ammopacks:"
        #print ammopacks
        #Update ammo State
        if observation.ammo > 0:
            Agent.ammo[self.id] = True
        else:
            Agent.ammo[self.id] = False
        if ammopacks:
            if ammopacks[0][0:2] == self.ammo1loc:
                Agent.state[2] = (True, Agent.state[2][1])
                Agent.set1 = False
            if ammopacks[0][0:2] == self.ammo2loc:
                Agent.state[2] =(Agent.state[2][0], True)
                Agent.set2 = False
        else:
            if self.inVisionRange(observation.loc, self.ammo1loc):
                Agent.state[2] = (False, Agent.state[2][1])
                if self.set1 == False:
                    Agent.set1 = True
                    Agent.reset1 = observation.step
            if self.inVisionRange(observation.loc, self.ammo2loc):
                Agent.state[2] =(Agent.state[2][0], False)
                if self.set2 == False:
                    Agent.set2 = True
                    Agent.reset2 = observation.step
        
        #update CPS state
        Agent.state[1] =(observation.cps)
        
        if (self.id == Agent.numAgents-1 and Agent.firstIteration == 1):
            Agent.firstIteration = 0
        
        # calculate this state's features
        self.calcFeatures()
        
        #self.writeFeaturesToFile()
        
        #~print "Agent.laststate: "
        #~print Agent.lastState
        #~print "Agent.state: "
        #~print Agent.state
        
        # print this state's features
        #sys.stdout.write('=====' + 'Agent '+ str(self.id) + '=====')
        #for k, v in self.featureVector.iteritems():
        #    sys.stdout.write(k + ': ' + str(v))
                
    def calcFeatures(self):        
         #featureVector = [{   'as1 filled':    0, # -1 for not filled, 1 for filled
                            #'as2 filled':    0,
                            #'cp1 of us':      0, # -1 for not of us, 1 for of us
                            #'cp2 of us':      0,
                            #'distance to cp1': 0,
                            #'distance to cp2': 0,
                            #'Am I closest ally to cp1': 0, # -1 for false, 1 for true
                            #'Am I closest ally to cp2': 0,
                            #'distance to as1': 0,
                            #'distance to as2': 0,
                            #'Am I closest ally to as1' : 0,
                            #'Am I closest ally to as2' : 0,
                            #'ammo amount': 0,
                            #'nearest enemy distance to cp1': 0,
                            #'nearest enemy distance to cp2' : 0,
                            #'nearest enemy distance to as1' : 0,
                            #'nearest enemy distance to as2' : 0
                        #}]
        
        # ammo points hwere ammo is present 
        if (Agent.state[2][0] == True):
            self.featureVector['as1 filled'] = 1
        else:
            self.featureVector['as1 filled'] = 0
        if (Agent.state[2][1] == True):
            self.featureVector['as2 filled'] = 1
        else:
            self.featureVector['as2 filled'] = 0
        
        # cp's owned 
        if (Agent.state[1][0][2] == self.team):
            self.featureVector['cp1 of us'] = 1
        else:
            self.featureVector['cp1 of us'] = 0
        if (Agent.state[1][1][2] == self.team):
            self.featureVector['cp2 of us'] = 1
        else:
            self.featureVector['cp2 of us'] = 0
        
        # needed for features below
        # (gedoe vanwege agent observatie volgorde eerste iteratie)
        #print "Agent.firstIteration:%d " % Agent.firstIteration
        agents = list(self.all_agents)      
        
        if (Agent.firstIteration == 1):   
            currAgents = []
            for i in range(0, self.id+1):
                currAgents.append(agents[i])
            agents = list(currAgents) # clone method
        
        foes = []
        for i in range(0, len(agents)):           
            f = agents[i].observation.foes
            if (len(f) > 0):
                foes = copy.deepcopy(f)
                       
        # control point 1 distance relations
        (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes) = self.getClosestEtc(agents, foes, Agent.state[1][0][0:2])
        self.featureVector['distance to cp1'] = myTime
        self.featureVector['nearest enemy distance to cp1'] = timeClosestAgentFoes
        if (closestAgentId == self.id):
            self.featureVector['Am I closest ally to cp1'] = 1
        else:
            self.featureVector['Am I closest ally to cp1'] = 0
        
        # control point 2 distance relations
        (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes) = self.getClosestEtc(agents, foes, Agent.state[1][1][0:2])
        self.featureVector['distance to cp2'] = myTime
        self.featureVector['nearest enemy distance to cp2'] = timeClosestAgentFoes
        if (closestAgentId == self.id):
            self.featureVector['Am I closest ally to cp2'] = 1
        else:
            self.featureVector['Am I closest ally to cp2'] = 0
        
        # ammo point 1 distance relations
        (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes) = self.getClosestEtc(agents, foes, Agent.ammoloc[0])
        self.featureVector['distance to as1'] = myTime
        self.featureVector['nearest enemy distance to as1'] = timeClosestAgentFoes
        if (closestAgentId == self.id):
            self.featureVector['Am I closest ally to as1'] = 1
        else:
            self.featureVector['Am I closest ally to as1'] = 0
              
        # ammo point 2 distance relations
        (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes) = self.getClosestEtc(agents, foes, Agent.ammoloc[1])
        self.featureVector['distance to as2'] = myTime
        self.featureVector['nearest enemy distance to as2'] = timeClosestAgentFoes
        if (closestAgentId == self.id):
            self.featureVector['Am I closest ally to as2'] = 1
        else:
            self.featureVector['Am I closest ally to as2'] = 0
      
        # ammo amount
        self.featureVector['ammo amount'] = self.observation.ammo
        
        self.featureVector['Am I dead'] = int(self.observation.respawn_in >= 1)
        if(Agent.printStuff):
            print self.featureVector
    
    def getClosestEtc(self, agents, foes, goal):
        # return: (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes)
        
        minTime = 99999.9
        closestAgentId = 0
        timePerAgent = [0.0]*3
        myTime = minTime
        
        minTimeFoes = 99999.9
        closestAgentIdFoes = 0
        timePerAgentFoes = [0.0]*3
        timeClosestAgentFoes = minTimeFoes
        
        for i in range(0, len(agents)):
            #print i
            path = find_path(agents[i].observation.loc, goal, self.mesh, self.grid, self.settings.tilesize)
            if path:
                time = self.calcPathTime(path, agents[i].observation.angle, agents[i].observation.loc)   #calcPathTime(self, path, curTurn, curLoc) 
            else:
                time = minTime # or is there always a path?
            timePerAgent[i] = time
            if time < minTime:
                minTime = time
                closestAgentId = i
        
        myTime = timePerAgent[self.id]
        #print "myTime: "
        #print myTime
        
        if foes: #wat is de volgorde want als de foes niet bewegen voor al de onze hebben bewogen hoeft dit maar eenmaal berekend te worden
            #print "foes: "
            #print foes
            for i in range(len(foes)):
                #print "foe:"
                #print foes[i]
                
                path = find_path(foes[i][0:2], goal, self.mesh, self.grid, self.settings.tilesize)
                if path:
                    time = self.calcPathTime(path, foes[i][2], foes[i][0:2])    #calcPathTime(self, path, curTurn, curLoc) 
                else:
                    time = minTimeFoes # or is there always a path?
                timePerAgentFoes[i] = time
                if time < minTimeFoes:
                    minTimeFoes = time
                    closestAgentIdFoes = i
                    
            timeClosestAgentFoes = timePerAgentFoes[closestAgentIdFoes]
        else:
            timeClosestAgentFoes = 15
        
        myTime = myTime / float(Agent.maxTime)
        timeClosestAgentFoes = timeClosestAgentFoes / float(Agent.maxTime)
        
        return (closestAgentId, myTime, closestAgentIdFoes, timeClosestAgentFoes)
        
    
    
    # old
    def getClosest(self, agents, foes, goal):
        '''
        agents: (agent, agent, agent)
        foes: [(x,y,angle),...]
        goal:(x, y)
        
        returns closest agent ID or -1 if foe 
        '''    
        closestAgent = agents[0]
        for agent in agents:
            closest = self.closestToGoal( (closestAgent.observation.loc, closestAgent.observation.angle), (agent.observation.loc, agent.observation.angle),  goal )
            if closest == 1:
                closestAgent = agent
        if foes:
            for foe in foes:
                closest = self.closestToGoal( (closestAgent.observation.loc, closestAgent.observation.angle), foe, goal)
                if closest == 1:
                    return -1
        return closestAgent.id
                    
                    
    def closestToGoal(self, agent0, agent1, goal):
        '''
        agents:(loc, angle) goal:(xloc, yloc)
        
        returns 0 for agent0, 1 for agent1
        '''
        bestTime = 99999
        path = find_path(agent0[0], goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            bestTime = self.calcPathTime(path, agent0[1], agent0[0]) # 
        path = find_path(agent1[0], goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            time = self.calcPathTime(path, agent1[1], agent1[0])
            if(time < bestTime):
                return 1
        return 0
    
        
    def pathTimeToGoal(self, goal):       
        
        path = find_path(self.observation.loc, goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            time = self.calcPathTime(path, self.observation.angle, self.observation.loc) #calcPathTime(self, path, curTurn, curLoc) 
            return time       
        else:
            return 99999 # maximum path time amount ? or is there always a path?


    def getAgent(self, agents, aId):
        for agent in agents:
            if agent.id == aId:
                return agent
    

    
        
    

    # uit test2
    def planAction(self, state):
        #f = open('planaction.txt','a')
        #f.write('doingit' + str(state) + '\n')
        #f.close()
        if str(state) in self.blobdict:
            values = self.blobdict[str(state)]
            randomVal = randint(0,len(values))
            cf = randint(0,10)
            if False: #cf==10
                action = values[randomVal]
            else:            
                maxVals = []
                maxVal = None
                for i in range(0,len(values)):
                    if(maxVal == None):
                        maxVal = values[i]
                        maxVals.append(i)
                    elif(values[i] > maxVal):
                        maxVal = values[i]
                        maxVals = [i]
                    elif(values[i] == maxVal):
                        maxVals.append(i)
                action = random.choice(maxVals)
                value = maxVal
            #f = open('planaction.txt','a')
            #f.write('Taking action from Q:' + str(values) + 'Action: ' + str(action) + '|' + str(value) + '\n')
            #f.close()
        else: 
            #[cap nearest, get ammo] hunt/camp points/control zone
            values = [self.Qinit, self.Qinit, self.Qinit, self.Qinit]
            Agent.blobdict[str(state)] = values
            action = random.choice(values)
            value = self.Qinit
            #f.write('notinblobyet' + '\n')
        return (action, value)
    
    # uit test2
    def updateBlob(self, laststate, lastaction, state, actionvalue, reward):
        oldvalues = self.blobdict[str(laststate)]
        toadd = self.alpha*(reward + self.gamma*actionvalue - oldvalues[lastaction])
        newvalues = oldvalues
        newvalues[lastaction] += toadd
        Agent.blobdict[str(laststate)] = newvalues
        #f.write('Reward: ' + str(reward) + 'Oldvalues: ' + str(oldvalues) + 'toadd: ' + str(toadd) + 'Newvalues: ' + str(newvalues) + '\n') 
    
    
    def calcValueAction(self, actionNumber):       
        valueOfAction = 0
        for keyFeature, valueFeature in self.featureVector.iteritems():                       
            valueOfAction = valueOfAction + Agent.parameterVectors[actionNumber][keyFeature] * valueFeature
            #sys.stdout.write('valueOfAction = valueOfAction + ' + str(Agent.parameterVectors[actionNumber][keyFeature]) + ' * ' + str(valueFeature) + '( = ' + str(valueOfAction) + ' )')
        
        return valueOfAction
        
    def calcValueActions(self):
        valueActions = []
        
        for i in range(0, Agent.numActions):
            valueActions.append(self.calcValueAction(i))
            
        return valueActions
        
    # incorporeren action number?
    def getReward_old(self):
        reward = 0
        #if obs.hit != None: #### Makes no sense for this to be a reward if shooting is not in our action model
        #    reward += 10
        #if obs.respawn_in == 10: # we're dead
        
        
        if (self.featureVector['Am I dead'] == 1 and self.lastFeatureVector['Am I dead'] == 0): #we died
            if self.observation.ammo > 0:
                reward += -7
            else:
                reward += -10
        if (self.lastFeatureVector['cp1 of us'] == 0 and self.featureVector['cp1 of us'] == 1): #catched cp1
            reward+=5
        if (self.lastFeatureVector['cp2 of us'] == 0 and self.featureVector['cp2 of us'] == 1): #catched cp2
            reward+=5
        if (self.lastFeatureVector['cp1 of us'] == 1 and self.featureVector['cp1 of us'] == 0): #lost cp1
            reward-=5
        if (self.lastFeatureVector['cp1 of us'] == 1 and self.featureVector['cp1 of us'] == 0): #lost cp2
            reward-=5
        #if ((state[0] == 2 and laststate[0] == 2 )or(state[0] == 3 and laststate[0] == 3)):        
           # if obs.ammo > 0 :
               # reward+=9
        if(self.lastFeatureVector['ammo amount'] < self.featureVector['ammo amount'] ):
            reward +=30
            if (self.lastFeatureVector['ammo amount'] == 0):
                reward+=30
        
        return reward
    
    
    def getReward(self):
        reward = 0
        #if obs.hit != None: #### Makes no sense for this to be a reward if shooting is not in our action model
        #    reward += 10
        #if obs.respawn_in == 10: # we're dead
        #print "Agent.laststate: "
        #print Agent.lastState
        #print "Agent.state: "
        #print Agent.state
        
        
        if (self.featureVector['Am I dead'] == 1 and self.lastFeatureVector['Am I dead'] == 0): #we died
            if self.observation.ammo > 0:
                reward += -7
            else:
                reward += -10
        if (Agent.lastState[1][0][2] != self.team and Agent.state[1][0][2] == self.team): #catched cp1
            reward+=10
        if (Agent.lastState[1][1][2] != self.team and Agent.state[1][1][2] == self.team): #catched cp2
            reward+=10
        if (Agent.lastState[1][0][2] == self.team and Agent.state[1][0][2] != self.team): #lost cp1
            reward-=10
        if (Agent.lastState[1][1][2] == self.team and Agent.state[1][1][2] != self.team): #lost cp2
            reward-=10
        #if ((state[0] == 2 and laststate[0] == 2 )or(state[0] == 3 and laststate[0] == 3)):        
           # if obs.ammo > 0 :
               # reward+=9
        if(self.lastFeatureVector['ammo amount'] < self.featureVector['ammo amount'] ):
            reward +=10
            if (self.lastFeatureVector['ammo amount'] == 0):
                reward+=30
        
        reward -= self.nrSteps / Agent.maxNrSteps
        
        return reward
        
        
    def selectAction(self):
        
        
        valuePerAction = self.calcValueActions()
        #print 'value per action: ' 
        #print valuePerAction
        
        randomNumber = random.uniform(0,1)
        selectedActionNumber = -1
        selectedActionValue = -1
        
        randomChoice = False
        
        if (randomNumber < Agent.epsilon):
            selectedActionNumber = random.randrange(0,Agent.numActions)
            selectedActionValue = valuePerAction[selectedActionNumber]
            randomChoice = True
        else:
            maxActionValue = max(valuePerAction)
            indices = [i for i, x in enumerate(valuePerAction) if x == maxActionValue]
            selectedActionNumber = indices[random.randrange(0,len(indices))] # choose random between highest
            selectedActionValue = maxActionValue

        
        if(Agent.printStuff):
            sys.stdout.write('Agent ' + str(self.id) + 's selectedAction: ' + Agent.actionNames[selectedActionNumber] + ' selectedActionValue: ' + str(selectedActionValue))
        if (randomChoice == True):
            if(Agent.printStuff):
                sys.stdout.write(' (chosen randomly)')
        return (selectedActionNumber, selectedActionValue)
   
   
    def goalReached_old(self):
        if(self.goal == self.observation.loc):
            if(Agent.printStuff):
                sys.stdout.write('=================> goal ' + Agent.actionNames[self.actionNumber] + ' reached by agent ' + str(self.id) + 'at pos ' + str(self.observation.loc))
            return True        
        else:
            return False
    
    def deadReached(self): 
        if(self.lastFeatureVector['Am I dead'] == 0 and self.featureVector['Am I dead'] == 1):
            return True
        else:
            return False
            
    def becomesAlive(self): 
        if(self.lastFeatureVector != None and self.lastFeatureVector['Am I dead'] == 1 and self.featureVector['Am I dead'] == 0):
            return True
        else:
            return False
            
    def goalReached(self):
        #f = open('goalreached.txt','a')
        #f.write('reached?:' + str(goal) + 'obs: ' + str(obs.loc) +'  ')
        #f.close()
        
        obs = self.observation
        
        if(self.goal == Agent.cps1loc):
            if(obs.cps[0][2] == self.team):
                return True           
        elif(self.goal == Agent.cps2loc):
            if(obs.cps[1][2] == self.team):
                return True           
        elif(self.goal == Agent.ammo1loc):
            if(self.observation.loc == Agent.ammo1loc ):
                return True
        elif(self.goal == Agent.ammo2loc):
            if(self.observation.loc == Agent.ammo2loc):
                return True
        elif(self.goal == self.observation.loc):           
                return True
        return False
    
    
    def writeFeaturesToFile(self):
        f = open('../src/features.txt', 'a+b')
        
        f.write('Agent ' + str(self.id) + ': \n')
        for keyParam, valueParam in self.featureVector.iteritems():            
            f.write(str(keyParam) + ' : ' + str(valueParam) + '\n')
        f.write('\n')
        
        f.close()
        
    def writeParametersToFile(self):
        f = open('../src/parameters.txt', 'wb')
        for i in range(0, Agent.numActions):
            f.write('Action ' + str(i) + ': ' + '(: '+ Agent.actionNames[i] + ') '+ '\n')
            for keyParam, valueParam in Agent.parameterVectors[i].iteritems():            
                f.write(str(keyParam) + ' : ' + str(valueParam) + '\n')
            f.write('\n')
        f.seek(0)
        f.close()
        
    def updateParameters(self, actionNumber, temporalDifferenceValue):
        if (actionNumber < Agent.numActions): # don't update for shoot
            if(Agent.printStuff):
                sys.stdout.write('==== Agent ' + str(self.id) + ' updated parameters for action ' + str(actionNumber) + '(: '+ Agent.actionNames[actionNumber] + ') '+ ': ====')
            for keyParam, valueParam in Agent.parameterVectors[actionNumber].iteritems():            
                if(Agent.printStuff):
                    sys.stdout.write(str(keyParam)  + '-> + ' +  str(Agent.gradientLearningRate * temporalDifferenceValue * self.lastFeatureVector[keyParam]))
                Agent.parameterVectors[actionNumber][keyParam] = Agent.parameterVectors[actionNumber][keyParam] + Agent.gradientLearningRate * temporalDifferenceValue * self.lastFeatureVector[keyParam]
            
            #Agent.blobdict[actionNumber] = Agent.parameterVectors[actionNumber]
        
            #self.writeParametersToFile();
            
            
            
    # uit test2
    def getActionAndUpdate(self):
        
        actionNumber = copy.deepcopy(self.actionNumber)
        newAction = False
        
        if(self.goal == None):         
            #init
            (actionNumber, value) = self.selectAction()   
            self.lastFeatureVector = copy.deepcopy(self.featureVector)
            newAction = True
            
        elif (self.oldActionNumber == 5):
            (actionNumber, value) = self.selectAction()
            self.lastFeatureVector = copy.deepcopy(self.featureVector)        
            newAction = True
        
        if (self.isDead and self.becomesAlive()):
            self.isDead = False
            self.oldActionNumber = self.actionNumber            
            (actionNumber, value) = self.selectAction()            
            reward = copy.deepcopy(self.reward)
            
            if(Agent.printStuff):
                sys.stdout.write('========= Agent ' + str(self.id) + ' awakens from dead') 
                sys.stdout.write('========= Agents ' + str(self.id) + ' reward: ' + str(reward))
            
            temporalDifferenceValue = reward + Agent.gamma * value - self.oldStateActionValue            
            self.oldStateActionValue = value            
            self.updateParameters(self.oldActionNumber, temporalDifferenceValue)
            newAction = True
                
        elif (self.goalReached() and not(self.deadReached()) and not self.isDead): 
        
            if (self.goalReached()):
                if(Agent.printStuff):
                    sys.stdout.write('=================> goal ' + Agent.actionNames[self.actionNumber] + ' reached according to agent ' + str(self.id) + 'at pos ' + str(self.observation.loc))

            #we have carried out action and observed reward, new state & featurevector (via self.observe)
            
            self.oldActionNumber = self.actionNumber            
            (actionNumber, value) = self.selectAction()            
            reward = self.getReward()
            
            if(Agent.printStuff):
                print "old fv: "
                print self.lastFeatureVector
                print "new fv: "
                print self.featureVector
        
            
            
            if(Agent.printStuff):
                sys.stdout.write('========= Agents ' + str(self.id) + ' reward: ' + str(reward))
            
            temporalDifferenceValue = reward + Agent.gamma * value - self.oldStateActionValue            
            self.oldStateActionValue = value            
            self.updateParameters(self.oldActionNumber, temporalDifferenceValue)
            self.lastFeatureVector = copy.deepcopy(self.featureVector)
            newAction = True
        
        elif(self.deadReached()):
            if(Agent.printStuff):
                sys.stdout.write('========= Agent ' + str(self.id) + ' just went dead while executing ' + Agent.actionNames[self.actionNumber]) 
            self.reward = copy.deepcopy(self.getReward())
            if(Agent.printStuff):
                sys.stdout.write('========= Agents ' + str(self.id) + ' reward: ' + str(self.reward))            
            self.lastFeatureVector = copy.deepcopy(self.featureVector)
            self.isDead = True
        
        
        elif (self.nrSteps >= Agent.maxNrSteps): 
            if(Agent.printStuff):
                sys.stdout.write('=================> Agent ' + str(self.id) + 'timed out')
            
            self.oldActionNumber = self.actionNumber            
            (actionNumber, value) = self.selectAction()  
            reward = self.getReward()
            
            if(Agent.printStuff):
                print "old fv: "
                print self.lastFeatureVector
                print "new fv: "
                print self.featureVector
        
            
            
            if(Agent.printStuff):
                sys.stdout.write('========= Agents ' + str(self.id) + ' reward: ' + str(reward))
            
            temporalDifferenceValue = reward + Agent.gamma * value - self.oldStateActionValue            
            self.oldStateActionValue = value            
            self.updateParameters(self.oldActionNumber, temporalDifferenceValue)
            self.lastFeatureVector = copy.deepcopy(self.featureVector)
            newAction = True
            
            
        if (newAction == True):
            self.nrSteps = 0
        else:
            self.nrSteps += 1
            
        return actionNumber            
      
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        
        self.actionNumber = self.getActionAndUpdate()
        obs = self.observation
        
        
        if (not(self.isDead)):
            # possible actions: go to cp1; go to cp2; go to as1; go to as2; do nothing
            if self.actionNumber == 0:
                self.goal = Agent.cps1loc 
            elif self.actionNumber == 1:
                self.goal = Agent.cps2loc 
            elif self.actionNumber == 2:
                self.goal = Agent.ammo1loc 
            elif self.actionNumber == 3:
                self.goal = Agent.ammo2loc 
            elif self.actionNumber == 4:
                self.goal = self.observation.loc
        else:
            self.goal = self.goal = self.observation.loc
                
        #### Shoot Enemy
        # If you have ammo, an enemy is in range and no friendly fire
        # override action with shoot action
        shoot = False      
        
        if (self.isDead == False):  
            targets = self.find_targets()
            if targets and obs.ammo > 0:
                self.actionNumber = 5
                self.goal = obs.foes[0][0:2]
                shoot = True
        
        if(Agent.printStuff):
            sys.stdout.write('====> action of Agent' + str(self.id) + ': ' + Agent.actionNames[self.actionNumber])
        if (shoot == True):    
            speed = 0
            turn = targets[0]
            if(Agent.printStuff):            
                print 'turn to shoot: ' , turn
                print 'FIIIIIIIIIIIRE!!!!'
                return (turn, speed, shoot)
        
        #### No shoot
        # Compute path, angle and drive
        path = find_path(self.observation.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if(Agent.printStuff):
            print "path: "
            print path
            print "self loc: "
            print self.observation.loc
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]               
            speed = ( dx ** 2 + dy ** 2 ) ** 0.5         
            turn = angle_fix( math.atan2(dy, dx) - obs.angle )
            if abs(turn) > self.settings.max_turn:
                startTurn = obs.angle
                speed = self.reducedSpeed(startTurn, dy, dx, speed)
                self.shoot = False
            #speed = ( dx ** 2 + dy ** 2 ) ** 0.5 / 3 # to overcome overshooting
        
        return (turn,speed,shoot)
    
    
    def find_targets(self):
        shoot = True #will be set to false if it is not allowed to shoot
        obs = self.observation
        loc = obs.loc
        targets = [] #angle to target foes
        max_turn = self.settings.max_turn
        max_range = self.settings.max_range
        radius = 8
        grid = self.grid
        tilesize = self.settings.tilesize
        
        #find foes: in shooting range and in turn range
        foes_in_range = []
        for foe in obs.foes:
            #calculate distance to foe
            dist_foe = point_dist(loc, foe[:2])
            #calculate angle to foe
            (loc_x, loc_y) = loc
            (foe_x, foe_y) = foe[:2]
            angle = math.atan2(foe_y-loc_y, foe_x-loc_x) - obs.angle
            angle_foe = angle_fix(angle)
            
            if dist_foe < max_range and angle_foe < max_turn:
                foes_in_range.append(foe)
                targets.append(angle_foe)
                #print 'added foe in range at point: ' , foe[:2]
        
        #if foes_in_range:
        #    print 'foes in range: ', foes_in_range
        
        #no foes in range or no ammo, return empty targets
        if not foes_in_range or obs.ammo == 0:
            shoot = False
            #print 'no foes in range or no ammo'
            return targets
        
        #don't shoot if a friend is in the way
        for friendly in obs.friends:
            if line_intersects_circ(loc, obs.foes[0][0:2], friendly, radius):
                shoot = False
                if(Agent.printStuff):
                    print 'Warning: friendly fire'
                
        #don't shoot if there is a wall in front of the enemy
        if line_intersects_grid(loc, obs.foes[0][0:2], self.grid, self.settings.tilesize):
            shoot = False
            if(Agent.printStuff):
                print 'wall in front of enemy'
        
        if shoot == True:
            if(Agent.printStuff):
                print 'CHARGING!'
                print 'Targets: ', targets
                print 'angle self: ', obs.angle
                print 'location self: ', obs.loc
                print 'location foe: ', foes_in_range[0]
            return targets
        else:
            return [] #not allowed to shoot, so return no targets
            
            
    def debug(self, surface):
        """ Allows the agents to draw on the game UI,
            Refer to the pygame reference to see how you can
            draw on a pygame.surface. The given surface is
            not cleared automatically. Additionally, this
            function will only be called when the renderer is
            active, and it will only be called for the active team.
        """
        import pygame
        # First agent clears the screen
        if self.id == 0:
            surface.fill((0,0,0,0))
        # Selected agents draw their info
        if self.selected:
            if self.goal is not None:
                pygame.draw.line(surface,(0,0,0),self.observation.loc, self.goal)
        
            if self.observation.ammo > 0:
                (loc_x, loc_y) = self.observation.loc
                pygame.draw.rect(surface, (255,0,0), (loc_x, loc_y, 10, 10), 2)
    
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        if(not(Agent.onServer)):
            pickle.dump(Agent.parameterVectors, open('../src/agent_test_avb2_blob', 'wb'))
        pass
        
    #############################
    ###### hardcoded stuff
    def plan(self, spawnammo):
        agents = list(self.all_agents)
        foes = []
        for agent in agents:
            foes.append(agent.observation.foes)
        for point in self.state[1]:
            if point[2] != self.team and point[:2] not in Agent.orders:
                closestId = self.getClosest(agents, None, point[:2])
                Agent.orders[closestId] = point[:2]
                agents.remove(self.getAgent(agents, closestId))
              
    def action_old(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        
        obs = self.observation
        spawnammo = []
        # If alive
        if obs.respawn_in < 1:
            # Spawned ammo that is not yet in a order
            for a in range(0, len(self.state[2])):
                if self.state[2][a] == True and self.ammoloc[a] not in Agent.orders:
                    spawnammo.append(self.ammoloc[a])
            # If goal is reached
            if self.goal is not None  and point_dist(self.goal, obs.loc) < self.settings.tilesize: 
                self.goal = None
                Agent.orders[self.id] = None
            # plan orders
            self.plan(spawnammo)
            self.goal = Agent.orders[self.id]
        else:
            self.goal = obs.loc

        if self.goal == None:
            self.goal = obs.loc
            
        shoot = False
        #### Shoot Enemy
        # If you have ammo, an enemy is in range and no friendly fire
        targets = self.find_targets()
        if targets and obs.ammo > 0:
            self.goal = obs.foes[0][0:2]
            shoot = True
            speed = 0
            turn = targets[0]
            if(Agent.printStuff):
                print 'turn to shoot: ' , turn
                print 'FIIIIIIIIIIIRE!!!!'
            return (turn, speed, shoot)
        
        #### No Enemy
        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]               
            speed = ( dx ** 2 + dy ** 2 ) ** 0.5         
            turn = angle_fix( math.atan2(dy, dx) - obs.angle )
            if abs(turn) > self.settings.max_turn:
                startTurn = obs.angle
                speed = self.reducedSpeed(startTurn, dy, dx, speed)
                self.shoot = False
            #speed = ( dx ** 2 + dy ** 2 ) ** 0.5 / 3 # to overcome overshooting
        
        return (turn,speed,shoot)

        
    
            
    #############################
    ###### end hardcoded stuff
            
    
