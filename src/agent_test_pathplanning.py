import random
import pygame
from random import randint

class Agent(object):

    alpha = 0.1
    gamma = 0.8
    Qinit = 0
    blobdict = {}
    lastaction = -1
    laststate = ()
    goal0 = (0,0)
    goal1 = (0,0)
    goal2 = (0,0)
    turns0 = 0
    turns1 = 0
    turns2 = 0
    estimate0 = 0
    estimate1 = 0
    estimate2 = 0
    cps1loc = (216, 56)
    cps2loc = (248, 216)
    ammo1loc = (9.5*16, 8.5*16)
    ammo2loc = (19.5*16, 8.5*16)

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
    tem = 0
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
        Agent.tem = team
        # Read the binary blob, we're not using it though
        if blob is not None:
            print "Agent %s received binary blob of %s" % (
               self.callsign, type(pickle.loads(blob.read())))
            # Reset the file so other agents can read it.
            blob.seek(0) 
            Agent.blobdict = pickle.loads(blob.read())
            blob.seek(0)
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
            #print observation
            pass

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
        
    def locToZone(self, loc):
        if loc[0] <= 4*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #left spawn
            return self.LEFTSPAWN
        elif loc[0] > 25*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #right spawn
            return self.RIGHTSPAWN
        elif loc[0] >= 7*16 and loc[0] <= 18*16 and loc[1] >= 12*16: #bot cap zone
            return self.BOTCAPZONE
        elif loc[0] >= 11*16 and loc[0] <= 22*16 and loc[1] <= 5*16: #top cap zone
            return self.TOPCAPZONE
        elif (loc[0] >= 4*16 and loc[0] <= 7*16 and loc[1] >= 9*16 and loc[1] <= 11*16) or (loc[0] >= 7*16 and loc[0] <= 11*16 and loc[1] >= 5*16 and loc[1] <= 11*16) : #left ammo zone
            return self.LEFTAMMOZONE
        elif (loc[0] >= 22*16 and loc[0] <= 25*16 and loc[1] >= 6*16 and loc[1] <= 8*16) or (loc[0] >= 18*16 and loc[0] <= 22*16 and loc[1] >= 6*16 and loc[1] <= 12*16) : #right ammo zone
            return self.RIGHTAMMOZONE
        elif loc[0] >= 11*16 and loc[0] <= 18*16 and loc[1] >= 6*16 and loc[1] <= 11*16: #battlefield zone
            return self.BATTLEFIELD
        elif loc[0] >= 4*16 and loc[0] <= 7*16 and loc[1] >= 5*16 and loc[1] <= 9*16: #pink left zone
            return self.PINKLEFTZONE
        elif loc[0] >= 22*16 and loc[0] <= 25*16 and loc[1] >= 8*16 and loc[1] <= 12*16: #pink right zone
            return self.PINKRIGHTZONE
        elif loc[0] <= 7*16 and loc[1] >= 11*16: #purple left zone
            return self.PURPLELEFTZONE
        elif loc[0] >= 22*16 and loc[1] <= 6*16: #purple right zone
            return self.PURPLERIGHTZONE
        elif loc[0] >= 7*16 and loc[0] <= 11*16 and loc[1] <= 5*16: #Orange left zone
            return self.ORANGELEFTZONE
        elif loc[0] >= 18*16 and loc[0] <= 22*16 and loc[1] >= 12*16: #Orange right zone
            return self.ORANGERIGHTZONE
        elif (loc[0] <= 7*16 and loc[1] <= 5*16) or (loc[0] <= 4*16 and loc[1] <= 6*16 and loc[1] >= 5*16): #Gray left zone
            return self.GRAYLEFTZONE
        elif (loc[0] >= 22*16 and loc[1] >= 12*16) or (loc[0] >= 25*16 and loc[1] <= 12*16 and loc[1] >= 11*16): #Gray right zone
            return self.GRAYRIGHTZONE
        else:
            f2 = open('fail.txt','a')
            f2.write(str(loc))
            f2.close()
            return -1
    
    def setGoal(self, goal):
        if(self.id == 0):
            Agent.goal0 = goal
        elif(self.id == 1):
            Agent.goal1 = goal
        elif(self.id == 2):
            Agent.goal2 = goal
        return


    def getReward(self, laststate, state, obs):
        reward = 0
        if obs.hit != None:
            reward += 10
        if obs.respawn_in == 9:
            if laststate[3] > 0:
                reward += -7
            reward += -10
        if (laststate[1] != self.team and state[1] == self.team):
            reward+=5
        if (laststate[2] != self.team and state[2] == self.team):
            reward+=5
        if (laststate[1] != state[1] and state[1] != self.team):
            reward-=5
        if (laststate[2] != state[2] and state[2] != self.team):
            reward-=5
        if ((state[0] == 2 and laststate[0] == 2 )or(state[0] == 3 and laststate[0] == 3)):
            if obs.ammo > 0 :
                reward+=9
        if(laststate[3]< state[3] ):
            reward +=30
            if laststate[3] ==0:
                reward+=30
        if(laststate[1] != self.team and state[1] == self.team and laststate[2] != self.team and state[2] == self.team):
            reward+=20
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
            self.goal(17,17)
        #just to check bugs
        #f = open('doaction.txt','a')
        #f.write('doingit' + str(self.goal) + '\n')
        #f.close()
        return shoot

    def planAction(self, state):
        #f = open('planaction.txt','a')
        #f.write('doingit' + str(state) + '\n')
        #f.close()
        if str(state) in self.blobdict:
            values = self.blobdict[str(state)]
            randomAct = randint(0,len(values)-1)
            cf = randint(0,30)
            if cf==30:
               value = values[randomAct]
               action = randomAct
            if True:#else:            
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

    def updateBlob(self, laststate, lastaction, state, actionvalue, reward):
        oldvalues = self.blobdict[str(laststate)]
        toadd = self.alpha*(reward + self.gamma*actionvalue - oldvalues[lastaction])
        newvalues = oldvalues
        newvalues[lastaction] += toadd
        Agent.blobdict[str(laststate)] = newvalues
        #f.write('Reward: ' + str(reward) + 'Oldvalues: ' + str(oldvalues) + 'toadd: ' + str(toadd) + 'Newvalues: ' + str(newvalues) + '\n') 

    def inVisionRange(self, loc1, loc2):
        if(point_dist(loc1, loc2) <= self.settings.max_see):
            return True
        else:
            return False

    def goalReached(self, goal, obs):
        #f = open('goalreached.txt','a')
        #f.write('reached?:' + str(goal) + 'obs: ' + str(obs.loc) +'  ')
        #f.close()
        if(point_dist(obs.loc, goal) < self.settings.tilesize):
            return True #after shooting ur done

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
    '''24 120
    24 120
    41 89
    79 77
    117 65
    155 54
    182 39
    216 53'''
    #returns events untill goal reached(error of 1 or 2)
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


    '''
    agents: (agent, agent, agent)
    foes: [(x,y,angle),...]
    goal:(x, y)
    
    returns closest agent ID or -1 if foe 
    '''
    def getClosest(self, agents, foes, goal):
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
                    

    
    '''
    agents:(loc, angle) goal:(xloc, yloc)
    
    returns 0 for agent0, 1 for agent1
    '''
    def closestToGoal(self, agent0, agent1, goal):
        bestTime = 99999
        path = find_path(agent0[0], goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            bestTime = self.calcPathTime(path, agent0[1], agent0[0])
        path = find_path(agent1[0], goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            time = self.calcPathTime(path, agent1[1], agent1[0])
            if(time < bestTime):
                return 1
        return 0
                
    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        print ('Action agent: ',self.id)
        for agent in self.all_agents:
            print agent.observation.loc
        closest = self.getClosest(self.all_agents, None, (24, 100))
        print ('Closest: ', closest)
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
            foes = []
            for i in range (0,len(obs.foes)):
                foes.append(self.locToZone((obs.foes[i])))
                            
        state = (self.locToZone(obs.loc), cps1[2], cps2[2], ammo, self.AMMO1, self.AMMO2, foes)
        
        
        action = -1
        
        if(self.goal == None):
            (action, value) = self.planAction(state)
            shoot = self.doAction(action, obs)
            self.lastaction = action
            self.laststate = state
            #f.write('Initialized: ' + str(state) + ' ' + str(action) + '\n')           
        elif(self.goalReached(self.goal, obs)):
            if self.id == 0:
                print ('Turns taken0 : ', self.turns0, self.estimate0)
                self.turns0 = 0
                self.estimate0 = 0
            elif self.id == 1:
                print ('Turns taken1 : ', self.turns1, self.estimate1)
                self.turns1 = 0
                self.estimate1 = 0
            elif self.id == 2:
                print ('Turns taken2 : ', self.turns2, self.estimate2)
                self.turns2 = 0
                self.estimate2 = 0
            (action, actionvalue) = self.planAction(state)
            reward = self.getReward(self.laststate, state, obs)
            self.updateBlob(self.laststate, self.lastaction, state, actionvalue, reward)            
            shoot = self.doAction(action, obs)
            #f.write('Updating Qvalues: ' + str(self.goal)+ '\n')
            self.lastaction = action
            self.laststate = state
            #f.write('Goal REACHED oldaction: ' + str(self.laststate)+'|'+str(self.lastaction)+ ' newaction: ' + str(state) + ' ' + str(action) + '\n')    
        

        #f.write('justbeforeshoot: ')
        shoot = False
        speed = 0
        turn = 0
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
        if path:
            pathTime = self.calcPathTime(path, obs.angle, obs.loc)
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]               
            speed = ( dx ** 2 + dy ** 2 ) ** 0.5
            turn = angle_fix( math.atan2(dy, dx) - obs.angle )
            if abs(turn) > self.settings.max_turn:
                startTurn = obs.angle
                speed = self.reducedSpeed(startTurn, dy, dx, speed)
                self.shoot = False
        #f.write('TODO: ' + str(speed) + "|" +str(self.settings.max_speed) + ' ' + str(turn) + "|" +str(self.settings.max_turn) + '\n\n')
        #f.close()
        if self.id == 0:
            self.turns0 += 1
        elif self.id == 1:
            self.turns1 += 1
        elif self.id == 2:
            self.turns2 += 1
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
                closest = self.getClosest(self.all_agents, None, self.goal)
                if closest == self.id:
                    pygame.draw.circle(surface, (0,255,0),self.observation.loc, 5, 5)
                else:
                    pygame.draw.circle(surface, (255,0,0),self.observation.loc, 5, 5)
                pygame.draw.line(surface,(0,0,0),self.observation.loc, self.goal)
        
    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        if self.score[self.tem] >= self.score[1-self.tem] :
            pass
        try:
            pickle.dump(self.blobdict, open('../src/agent_test_blob', 'wb'), pickle.HIGHEST_PROTOCOL)
    
        except:
            print ('error writing file !')
            
        
