from random import randint

class Agent(object):

    alpha = 0.1
    gamma = 0.8
    Qinit = 0.0
    blobdict = {}
    policy = {}
    avgPolicy = {}
    avgPolicyCounter = {}
    delta = 0.1
    deltaWin = 0.1
    deltaLose = 0.3
    lastaction = -1
    laststate = ()
    goal0 = (0,0)
    goal1 = (0,0)
    goal2 = (0,0)
    cps1loc = (14.5*16, 3.5*16)
    cps2loc = (16.5*16, 13.5*16)
    ammo1loc = (11.5*16, 10.5*16)
    ammo2loc = (19.5*16, 6.5*16)

    LEFTSPAWN = 0
    RIGHTSPAWN = 1
    BOTCAPZONE = 2
    TOPCAPZONE = 3
    LEFTAMMOZONE = 4
    RIGHTAMMOZONE = 5
    BATTLEFIELD = 6
    PINKLEFTZONE = 7
    PINKRIGHTZONE = 8
    PURPLELEFTZONE = 9
    PURPLERIGHTZONE = 10
    ORANGELEFTZONE = 11
    ORANGERIGHTZONE = 12
    GRAYLEFTZONE = 13
    GRAYRIGHTZONE = 14
    score = (0,0)
    AMMO1 = True
    AMMO2 = True

    NAME = "default_agent"

    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None, **kwargs):
        """ Each agent is initialized at the beginning of each game.
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
            print "Agent %s received binary blob of %s" % (
               self.callsign, type(pickle.loads(blob.read())))
            # Reset the file so other agents can read it.
            blob.seek(0)
            self.blobdict = pickle.loads(blob.read())
            blob.seek(0)
        print "init test agent\n"
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected
        Agent.score = observation.score
        if observation.selected:
            print observation

    def diffGoal(self, goal):
        if(self.id == 0):
            if(self.goal1 == goal or self.goal2 == goal):
                return False
        elif(self.id == 1):
            if(self.goal0 == goal or self.goal2 == goal):
                return False
        elif(self.id == 2):
            if(self.goal0 == goal or self.goal1 == goal):
                return False
        return True
#new map
    def locToZone(self, loc):
        if loc[0] <= 3*16 and loc[1] >= 6*16 and loc[1] <= 10*16: #left spawn
            return self.LEFTSPAWN
        elif loc[0] >= 27*16 and loc[1] >= 6*16 and loc[1] <= 10*16: #right spawn
            return self.RIGHTSPAWN
        elif loc[0] >= 8*16 and loc[0] <= 22*16 and loc[1] >= 12*16: #bot cap zone
            return self.BOTCAPZONE
        elif loc[0] >= 8*16 and loc[0] <= 22*16 and loc[1] <= 4*16: #top cap zone
            return self.TOPCAPZONE
        elif (loc[0] >= 4*16 and loc[0] <= 8*16 and loc[1] >= 9*16 and loc[1] <= 10*16) or (loc[0] >= 8*16 and loc[0] <= 12*16 and loc[1] >= 6*16 and loc[1] <= 10*16) : #left ammo zone
            return self.LEFTAMMOZONE
        elif (loc[0] >= 22*16 and loc[0] <= 25*16 and loc[1] >= 6*16 and loc[1] <= 7*16) or (loc[0] >= 18*16 and loc[0] <= 21*16 and loc[1] >= 6*16 and loc[1] <= 10*16) : #right ammo zone
            return self.RIGHTAMMOZONE
        elif loc[0] >= 13*16 and loc[0] <= 17*16 and loc[1] >= 6*16 and loc[1] <= 10*16: #battlefield zone
            return self.BATTLEFIELD
        elif loc[0] >= 5*16 and loc[0] <= 7*16 and loc[1] >= 5*16 and loc[1] <= 8*16: #pink left zone
            return self.PINKLEFTZONE
        elif loc[0] >= 23*16 and loc[0] <= 25*16 and loc[1] >= 8*16 and loc[1] <= 11*16: #pink right zone
            return self.PINKRIGHTZONE
        elif loc[0] <= 7*16 and loc[1] >= 11*16: #purple left zone
            return self.PURPLELEFTZONE
        elif loc[0] >= 23*16 and loc[1] <= 5*16: #purple right zone
            return self.PURPLERIGHTZONE
        elif (loc[0] <= 7*16 and loc[1] <= 4*16) or (loc[0] <= 3*16 and loc[1] == 5*16): #Gray left zone
            return self.GRAYLEFTZONE
        elif (loc[0] >= 23*16 and loc[1] >= 12*16) or (loc[0] >= 26*16 and loc[1] == 11*16): #Gray right zone
            return self.GRAYRIGHTZONE
        else:
            f2 = open('fail.txt','a')
            f2.write(str(loc))
            f2.close()
            return -1

#old map
    #def locToZone(self, loc):
    #    if loc[0] <= 4*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #left spawn
    #        return self.LEFTSPAWN
    #    elif loc[0] > 25*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #right spawn
    #        return self.RIGHTSPAWN
    #    elif loc[0] >= 7*16 and loc[0] <= 18*16 and loc[1] >= 12*16: #bot cap zone
    #        return self.BOTCAPZONE
    #    elif loc[0] >= 11*16 and loc[0] <= 22*16 and loc[1] <= 5*16: #top cap zone
    #        return self.TOPCAPZONE
    #    elif (loc[0] >= 4*16 and loc[0] <= 7*16 and loc[1] >= 9*16 and loc[1] <= 11*16) or (loc[0] >= 7*16 and loc[0] <= 11*16 and loc[1] >= 5*16 and loc[1] <= 11*16) : #left ammo zone
    #        return self.LEFTAMMOZONE
    #    elif (loc[0] >= 22*16 and loc[0] <= 25*16 and loc[1] >= 6*16 and loc[1] <= 8*16) or (loc[0] >= 18*16 and loc[0] <= 22*16 and loc[1] >= 6*16 and loc[1] <= 12*16) : #right ammo zone
    #        return self.RIGHTAMMOZONE
    #    elif loc[0] >= 11*16 and loc[0] <= 18*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #battlefield zone
    #        return self.BATTLEFIELD
    #    elif loc[0] >= 4*16 and loc[0] <= 7*16 and loc[1] >= 5*16 and loc[1] <= 9*16: #pink left zone
    #        return self.PINKLEFTZONE
    #    elif loc[0] >= 22*16 and loc[0] <= 25*16 and loc[1] >= 8*16 and loc[1] <= 12*16: #pink right zone
    #        return self.PINKRIGHTZONE
    #    elif loc[0] <= 7*16 and loc[1] >= 11*16: #purple left zone
    #        return self.PURPLELEFTZONE
    #    elif loc[0] >= 22*16 and loc[1] <= 6*16: #purple right zone
    #        return self.PURPLERIGHTZONE
    #    elif loc[0] >= 7*16 and loc[0] <= 11*16 and loc[1] <= 5*16: #Orange left zone
    #        return self.ORANGELEFTZONE
    #    elif loc[0] >= 18*16 and loc[0] <= 22*16 and loc[1] >= 12*16: #Orange right zone
    #        return self.ORANGERIGHTZONE
    #    elif (loc[0] <= 7*16 and loc[1] <= 5*16) or (loc[0] <= 4*16 and loc[1] <= 6*16 and loc[1] >= 5*16): #Gray left zone
    #        return self.GRAYLEFTZONE
    #    elif (loc[0] >= 22*16 and loc[1] >= 12*16) or (loc[0] >= 25*16 and loc[1] <= 12*16 and loc[1] >= 11*16): #Gray right zone
    #        return self.GRAYRIGHTZONE
    #    else:
    #        f2 = open('fail.txt','a')
    #        f2.write(str(loc))
    #        f2.close()
    #        return -1

    def setGoal(self, goal):
        if(self.id == 0):
            Agent.goal0 = goal
        elif(self.id == 1):
            Agent.goal1 = goal
        elif(self.id == 2):
            Agent.goal2 = goal
        return


    def getReward(self, laststate, state, obs):
        reward = 0.0
        if obs.hit != None:
            reward += 10.0
        if obs.respawn_in == 9:
            if laststate[3] > 0:
                reward += -7.0
            reward += -10.0
        if (laststate[1] != self.team and state[1] == self.team):
            reward+=5.0
        if (laststate[2] != self.team and state[2] == self.team):
            reward+=5.0
        if (laststate[1] != state[1] and state[1] != self.team):
            reward-=5.0
        if (laststate[2] != state[2] and state[2] != self.team):
            reward-=5.0
        if ((state[0] == 2 and laststate[0] == 2 )or(state[0] == 3 and laststate[0] == 3)):
            if obs.ammo > 0 :
                reward+=9.0
        if(laststate[3]< state[3] ):
            reward +=30.0
            if laststate[3] ==0:
                reward+=30.0
        if(laststate[1] != self.team and state[1] == self.team and laststate[2] != self.team and state[2] == self.team):
            reward+=20.0
        return reward


    def doAction(self, action, obs):
        shoot = False
        #f = open('doaction.txt','a')
        #f.write('doingit\n')
        #f.close()
        if action == 0:
            self.goal = self.cps1loc #nearestCPS(obs.loc)
        elif action == 1:
            self.goal = self.cps2loc #nearestCPS(obs.loc)
        elif action == 2:
            self.goal = self.ammo1loc #closest ammo/spawned ammo
        elif action == 3:
            self.goal = self.ammo2loc #closest ammo/spawned ammo
        else:
            self.goal = (17,17) #just to check bugs
        #f = open('doaction.txt','a')
        #f.write('doingit' + str(self.goal) + '\n')
        #f.close()
        return shoot

    def planAction(self, state):
        #f = open('planaction.txt','a')
        #f.write('doingit' + str(state) + '\n')
        #f.close()
        if str(state) in self.blobdict:
            print 'planAction says that ' +str(state) + 'does exist'
            values = self.blobdict[str(state)]
            randomAct = randint(0,len(values)-1)
            cf = randint(0,30)
            if cf==30:
                value = values[randomAct]
                action = randomAct
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
            print 'planAction says that ' +str(state) + 'does NOT exist'
            #[cap nearest, get ammo] hunt/camp points/control zone
            values = [self.Qinit, self.Qinit, self.Qinit, self.Qinit]
            self.blobdict[str(state)] = values
            action = random.choice(values)
            value = self.Qinit
            #f.write('notinblobyet' + '\n')
        return (action, value)

    def updateBlob(self, laststate, lastaction, state, actionvalue, reward):
        oldvalues = self.blobdict[str(laststate)]
        toadd = self.alpha*(reward + self.gamma*actionvalue - oldvalues[lastaction])
        newvalues = oldvalues
        newvalues[lastaction] += toadd
        self.blobdict[str(laststate)] = newvalues
        print 'Reward: ' + str(reward) + 'Oldvalues: ' + str(oldvalues) + 'toadd: ' + str(toadd) + 'Newvalues: ' + str(newvalues) + '\n'

#PHC
    def planActionPHC(self, state):
        #f = open('planaction.txt','a')
        #f.write('doingit' + str(state) + '\n')
        #f.close()
#making it greedy
        if state in self.policy:
            policyValues = self.policy[state]
            values = self.blobdict[str(state)]
            maxActions = []
            maxVal = None
            for i in range(0,len(policyValues)):
                if(maxVal == None):
                    maxVal = values[i]
                    maxActions.append(i)
                elif(values[i] > maxVal):
                    maxVal = values[i]
                    maxActions = [i]
                elif(values[i] == maxVal):
                    maxActions.append(i)
            action = random.choice(maxActions)
            value = maxVal
            #f = open('planaction.txt','a')
            #f.write('Taking action from Q:' + str(values) + 'Action: ' + str(action) + '|' + str(value) + '\n')
            #f.close()
        else:
            print 'planActionPHC says that ' +str(state) + 'does NOT exist'
            #[cap nearest, get ammo] hunt/camp points/control zone
            values = [self.Qinit, self.Qinit, self.Qinit, self.Qinit]
            self.initPolicy(state,values)
            self.blobdict[str(state)] = values
            action = random.choice(range(len(values)))
            value = self.Qinit
            #f.write('notinblobyet' + '\n')
        print 'planActionPHC selected action {0} with value {1} from values {2}'.format(action,value,values)
        return (action, value)


    def updatePolicyWoLFPHC(self, state, action, values):
        if action != -1:
#        values = self.blobdict[str(state)]
            self.avgPolicyCounter[state] += 1.0
            print 'the average Policy for {0} is {1} BEFORE:'.format(state, self.avgPolicy[state])
            avgPolicyValueSum = 0
            for b in range(len(values)):
                self.avgPolicy[state][b] += 1/self.avgPolicyCounter[state]*(self.policy[state][b] - self.avgPolicy[state][b])
                avgPolicyValueSum += self.avgPolicy[state][b]

            for b in range(len(values)):
                self.avgPolicy[state][b] /= avgPolicyValueSum

            avgPolicyQSum = 0.0
            for b in range(len(values)):
                avgPolicyQSum += self.avgPolicy[state][b]*values[b]

            print 'the average Policy for {0} is {1} AFTER:'.format(state, self.avgPolicy[state])
            maxVals = []
            maxVal = None
            print 'Q values {0}'.format(values)
            for i in range(0,len(values)):
                if(maxVal == None):
                    maxVal = values[i]
                    maxVals.append(i)
                elif(values[i] > maxVal):
                    maxVal = values[i]
                    maxVals = [i]
                elif(values[i] == maxVal):
                    maxVals.append(i)
            favouredAction = random.choice(maxVals)
            print 'favouredAction {0}'.format(favouredAction)
            policyQSum = 0.0
            for i in range(len(values)):
                policyQSum += self.policy[state][i]*values[i]
            print '****************************************************'
            print 'policyQSum {0}'.format(policyQSum)
            print 'avgPolicyQSum {0}'.format(avgPolicyQSum)
            if policyQSum > avgPolicyQSum:
                self.delta = self.deltaWin
                print 'win delta {0}'.format(self.delta)
            else:
                self.delta = self.deltaLose
                print 'loose delta {0}'.format(self.delta)
            print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
            policyOffset = 0.0
            for i in range(len(values)):
                if i == favouredAction:
                    self.policy[state][i] += self.delta
                    print '{0} is the favouredAction'.format(i)
                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])
                else:
                    self.policy[state][i] -= self.delta/(len(values)-1)
                    print '{0} is NOT the favouredAction'.format(i)
                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])

                if (self.policy[state][i] < 0.0) and (abs(self.policy[state][i]) > policyOffset):
                    policyOffset = abs(self.policy[state][i])
                    print 'value of action {0} is {1}, which is negative'.format(i, self.policy[state][i])
#                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])

            #if action == favouredAction:
            #    self.policy[state][action] += self.delta
            #else:
            #    self.policy[state][action] -= self.delta/(len(values)-1)
            #policyOffset = 0
            #if self.policy[state][action] < 0:
            #    policyOffset = abs(self.policy[state][action])
            policyValueSum = 0.0
            for i in range(len(values)):
                self.policy[state][i] += policyOffset
                policyValueSum += self.policy[state][i]

            for i in range(len(values)):
                self.policy[state][i] = self.policy[state][i]/policyValueSum
#           self.policy[state][i] = 0.0
#      self.policy[state][action] = 1.0
#            value = maxVal
            #print 'I updated the policy for state {0} and action {1} with the following value {2}, so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])
            print 'I updated the policy for state {0} and action {1} with the following value {2} so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])
            #maxVals = []
            #maxVal = None
            #for i in range(0,len(values)):
            #    if(maxVal == None):
            #        maxVal = values[i]
            #        maxVals.append(i)
            #    elif(values[i] > maxVal):
            #        maxVal = values[i]
            #        maxVals = [i]
            #    elif(values[i] == maxVal):
            #        maxVals.append(i)
            #favouredAction = random.choice(maxVals)
            #if action == favouredAction:
            #    self.policy[state][action] += self.delta
            #else:
            #    self.policy[state][action] -= self.delta/(len(values)-1)
            #policyOffset = 0
            #if self.policy[state][action] < 0:
            #    policyOffset = abs(self.policy[state][action])
            #policyValueSum = 0
            #for i in range(len(values)):
            #    self.policy[state][i] += policyOffset
            #    policyValueSum += self.policy[state][i]

            #for i in range(len(values)):
            #    self.policy[state][i] /= policyValueSum
#           #self.policy[state][i] = 0.0
#      self.#policy[state][action] = 1.0
#           # value = maxVal
            ##print 'I updated the policy for state {0} and action {1} with the following value {2}, so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])
            #print 'I updated the policy for state {0} and action {1} with the following value {2} so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])

    def updatePolicyPHC(self, state, action, values):
        if action != -1:
            print 'BEFORE UPDATE policy {0}'.format(self.policy[state])
#        values = self.blobdict[str(state)]
            maxVals = []
            maxVal = None
            print 'Q values {0}'.format(values)
            for i in range(0,len(values)):
                if(maxVal == None):
                    maxVal = values[i]
                    maxVals.append(i)
                elif(values[i] > maxVal):
                    maxVal = values[i]
                    maxVals = [i]
                elif(values[i] == maxVal):
                    maxVals.append(i)
            favouredAction = random.choice(maxVals)
            print 'favouredAction {0}'.format(favouredAction)
            policyOffset = 0.0
            for i in range(len(values)):
                if i == favouredAction:
                    self.policy[state][i] += self.delta
                    print '{0} is the favouredAction'.format(i)
                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])
                else:
                    self.policy[state][i] -= self.delta/(len(values)-1)
                    print '{0} is NOT the favouredAction'.format(i)
                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])

                if (self.policy[state][i] < 0.0) and (abs(self.policy[state][i]) > policyOffset):
                    policyOffset = abs(self.policy[state][i])
                    print 'value of action {0} is {1}, which is negative'.format(i, self.policy[state][i])
#                    print 'self.policy[{0}][{1}] = {2}'.format(state,i,self.policy[state][i])

            #if action == favouredAction:
            #    self.policy[state][action] += self.delta
            #else:
            #    self.policy[state][action] -= self.delta/(len(values)-1)
            #policyOffset = 0
            #if self.policy[state][action] < 0:
            #    policyOffset = abs(self.policy[state][action])
            policyValueSum = 0.0
            for i in range(len(values)):
                self.policy[state][i] += policyOffset
                policyValueSum += self.policy[state][i]

            for i in range(len(values)):
                self.policy[state][i] = self.policy[state][i]/policyValueSum
#           self.policy[state][i] = 0.0
#      self.policy[state][action] = 1.0
#            value = maxVal
            #print 'I updated the policy for state {0} and action {1} with the following value {2}, so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])
            print 'I updated the policy for state {0} and action {1} with the following value {2} so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])

    def updatePolicyGreedy(self, state, action, values):
        if action != -1:
#        values = self.blobdict[str(state)]
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
            favouredAction = random.choice(maxVals)
            if action == favouredAction:
                for i in range(len(values)):
                    self.policy[state][i] = 0.0
                self.policy[state][action] = 1.0
            value = maxVal
            #print 'I updated the policy for state {0} and action {1} with the following value {2}, so now the policy is: {3}'.format(state, action, self.policy[state][action], self.policy[state])
            print 'I updated the policy for state {0}'.format(state)
            print 'and action {0}'.format(action)
            print 'with the following value {0}'.format(self.policy[state][action])
            print 'so now the policy is: {0}'.format(self.policy[state])

    def initPolicy(self, state, actions):
        self.policy[state] = {}
        self.avgPolicy[state] = {}
        for action in range(len(actions)):
            self.policy[state][action] = 1.0/len(actions)
            self.avgPolicy[state][action] = 1.0/len(actions)
        self.avgPolicyCounter[state] = 0
        print 'I initiated the policy for state {0} with the following values {1}'.format(state, self.policy[state])
        print 'So now the policy looks like:'
        for state in self.policy:
            print '{0}:{1}'.format(state, self.policy[state])


    def updateBlobPHC(self, laststate, lastaction, state, actionvalue, reward):
        oldvalues = self.blobdict[str(laststate)]
        toadd = self.alpha*(reward + self.gamma*actionvalue - oldvalues[lastaction])
        newvalues = oldvalues
        newvalues[lastaction] += toadd
        self.blobdict[str(laststate)] = newvalues
        print 'Reward: {0}, oldValues {1}, toAdd {2}, newValues {3}'.format(reward, oldvalues, toadd, newvalues)

    def pHC(self, laststate, lastaction, state, actionvalue, reward):
        print 'pHC has: laststate {0}, lastaction{1}, state {2}, actionvalue {3}, reward {4}'.format(laststate, lastaction, state, actionvalue, reward)
        oldvalues = self.blobdict[str(laststate)]
        print 'oldvalues: {0}, oldvalues[lastaction] {1}'.format(oldvalues, oldvalues[lastaction])
        toadd = self.alpha*(reward + self.gamma*actionvalue)
        newvalues = oldvalues
        newvalues[lastaction] = (1-self.alpha)*newvalues[lastaction]
        newvalues[lastaction] += toadd
        self.blobdict[str(laststate)] = newvalues
        self.updatePolicyWoLFPHC(laststate, lastaction, newvalues)
#        self.updatePolicyPHC(laststate, lastaction, newvalues)
#        self.updatePolicyGreedy(laststate, lastaction, newvalues)
        print 'Reward: {0}, oldValues {1}, toAdd {2}, newValues {3}'.format(reward, oldvalues, toadd, newvalues)

    def inVisionRange(self, loc1, loc2):
        if(point_dist(loc1, loc2) <= self.settings.max_see):
            return True
        else:
            return False

    def goalReached(self, goal, obs):
        #f = open('goalreached.txt','a')
        #f.write('reached?:' + str(goal) + 'obs: ' + str(obs.loc) +'  ')
        #f.close()
        if(goal == self.cps1loc):
            if(obs.cps[0][2] == self.team):
                return True
            else:
                return False
        elif(goal == self.cps2loc):
            if(obs.cps[1][2] == self.team):
                return True
            else:
                return False
        elif(goal == self.ammo1loc):
            if(self.AMMO1):
                return False
            else:
                return True
        elif(goal == self.ammo2loc):
            if(self.AMMO2):
                return False
            else:
                return True
        return True #after shooting ur done


    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """

        obs = self.observation
        #f = open('testfile.txt','a')
        #f.write('CheckingVision: ' + str(self.goal) + '\n')
        if(self.inVisionRange(obs.loc, self.ammo1loc) != self.inVisionRange(obs.loc, self.ammo2loc)):
            if(self.inVisionRange(obs.loc, self.ammo1loc)):
                if(len(obs.objects)>0):
                    Agent.AMMO1 = True
                else:
                    Agent.AMMO1 = False
            else:
                if(len(obs.objects)>0):
                    Agent.AMMO2 = True
                else:
                    Agent.AMMO2 = False
        cps1 = obs.cps[0]
        cps2 = obs.cps[1]
        ammo = False
        if(obs.ammo > 0):
            ammo = True
        foes = False
        if(len(obs.foes) > 0):
            foes = True
        state = (self.locToZone(obs.loc), cps1[2], cps2[2], ammo, self.AMMO1, self.AMMO2, foes)


        action = -1


        if(self.goal == None):
            shoot = self.doAction(action, obs)
            self.lastaction = action
            self.laststate = state
            if not(str(state) in self.blobdict):
                print 'action says that ' +str(state) + 'does NOT exist'
                #[cap nearest, get ammo] hunt/camp points/control zone
                values = [self.Qinit, self.Qinit, self.Qinit, self.Qinit]
                self.blobdict[str(state)] = values
                self.initPolicy(state,values)
        elif(self.goalReached(self.goal, obs)):
            #(action, actionvalue) = self.planAction(state)
            (action, actionvalue) = self.planActionPHC(state)
            reward = self.getReward(self.laststate, state, obs)
            #self.updateBlob(self.laststate, self.lastaction, state, actionvalue, reward)
            self.pHC(self.laststate, self.lastaction, state, actionvalue, reward)
            shoot = self.doAction(action, obs)
            #f.write('Updating Qvalues: ' + str(self.goal)+ '\n')
            self.lastaction = action
            self.laststate = state
            #f.write('Goal REACHED oldaction: ' + str(self.laststate)+'|'+str(self.lastaction)+ ' newaction: ' + str(state) + ' ' + str(action) + '\n')


        #f.write('justbeforeshoot: ')
        shoot = False
        # Shoot enemies
        if (obs.ammo > 0 and
            obs.foes and
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
                foe = obs.foes[0][0:2]
                pathtofoe = find_path(obs.loc, foe, self.mesh, self.grid, self.settings.tilesize)
                dx = pathtofoe[0][0] - obs.loc[0]
                dy = pathtofoe[0][1] - obs.loc[1]
                turn = angle_fix(math.atan2(dy, dx) - obs.angle)
                if turn <= self.settings.max_turn or turn >= -self.settings.max_turn:
                    shoot = True
                    self.goal = foe


        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        #f.write('Path: ' + str(path) +'\n')
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
            speed = (dx**2 + dy**2)**0.5
        else:
            turn = 0
            speed = 0
        #f.write('TODO: ' + str(speed) + "|" +str(self.settings.max_speed) + ' ' + str(turn) + "|" +str(self.settings.max_turn) + '\n\n')
        #f.close()
        if self.id == 0:
            #print 'agent ' + str(self.id) + ' turn ' + str(turn) + ' speed ' + str(speed) + ' shoot ' + str(shoot) + '\n'
            banana = 0
        else:
#            turn = 0.0
 #           speed = 0.0
  #          shoot = False
            banana = 0
            #print 'agent ' + str(self.id) + ' turn ' + str(turn) + ' speed ' + str(speed) + ' shoot ' + str(shoot) + '\n'
        return (turn,speed,shoot)

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

    def finalize(self, interrupted=False):
        """ This function is called after the game ends,
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        #if self.score[self.team] >= self.score[1-self.team] :
        if 1:
            pickle.dump(self.blobdict, open('../src/agent_test_blob', 'wb'))
        pass

