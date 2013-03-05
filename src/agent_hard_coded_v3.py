import math
class Agent(object):
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

    set1 = False
    set2 = False
    reset1 = 0
    reset2 = 0
    
    
    ammo = [False, False, False]
    orders = [None, None, None]
    allyLocs = [None, None, None]
    enemyLocs = [None, None, None]
    distance = [(1000,1000,1000), (1000,1000,1000)]
    ammo1loc = (152, 136)
    ammo2loc = (312, 136)
    ammoloc = [ammo1loc, ammo2loc]

    # state  = wie ammo heeft; locaties cps + wie ze heeft; ammospawn1, ammospawn2, allyLocs; enemyLocs (als ie ze ziet)
    state = [ammo, ((216, 56,-1),(248, 216, -1)), (True, True), allyLocs, enemyLocs]
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
        
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
        self.all_agents.append(self)
        self.addNodeToMesh((21.5*16, 7.5*16))
        self.addNodeToMesh((7.5*16,9.5*16))

    def addNodeToMesh(self, node):
        max_speed = self.settings.max_speed # - some value as they seem to slow down otherwise
        self.mesh[node] = dict([(n, math.ceil(point_dist(node,n) / float(max_speed)) * max_speed)  for n in self.mesh if not line_intersects_grid(node,n,self.grid,16)])

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

    def closest_CP(self, loc, CPS):
        print loc
        print CPS
        bestdist = 9999
        best = 0
        for i in range (0, len(CPS)):
            dist = ((loc[0]-CPS[i][0]) ** 2 + (loc[1]-CPS[i][1]) ** 2) ** 0.5
            if dist < bestdist:
                bestdist = dist
                best = i
        if (len(CPS) == 1):
            print 'only 1 cps lol?'
            return 0
        print best
        return best
    
    def closest_UCP (self, team,  loc, cps):
        closestcp = self.closest_CP(loc,cps)
        #print'==========='
        #print len(cps)
        #print closestcp
        #print cps[closestcp]
        #print team
        #print '===='
        if cps[closestcp][2] != team:
            #fix dis
            return (cps[closestcp][:2]) 
        elif (len(cps) > 1):
            newCPS = list(cps)
            newCPS.remove(cps[closestcp])
            self.closest_UCP(team,  loc, newCPS)
   
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
            
    def closest_ammo(self, loc, Ammo):
            bestdist = 9999
            best = 0
            for i in range (0, len(Ammo)):
                dist = ((loc[0]-Ammo[i][0]) ** 2 + (loc[1]-Ammo[i][1]) ** 2) ** 0.5
                if dist < bestdist:
                    bestdist = dist
                    best = i
            return Ammo[best]
        
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
        
        
        if observation.selected:
            pass

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
            bestTime = self.calcPathTime(path, agent0[1], agent0[0])
        path = find_path(agent1[0], goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            time = self.calcPathTime(path, agent1[1], agent1[0])
            if(time < bestTime):
                return 1
        return 0

    def getAgent(self, agents, aId):
        for agent in agents:
            if agent.id == aId:
                return agent
    
    def plan(self, spawnammo):
        agents = list(self.all_agents)
        foes = []
        for agent in agents:
            foes.append(agent.observation.foes)
        for point in self.state[1]:
            if point[2] != self.team and point[:2] not in self.orders:
                closestId = self.getClosest(agents, None, point[:2])
                Agent.orders[closestId] = point[:2]
                agents.remove(self.getAgent(agents, closestId))
              
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        spawnammo = []
        # If alive
        if obs.respawn_in < 1:
            # Spawned ammo that is not yet in a order
            for a in range(0, len(self.state[2])):
                if self.state[2][a] == True and self.ammoloc[a] not in self.orders:
                    spawnammo.append(self.ammoloc[a])
            # If goal is reached
            if self.goal is not None  and point_dist(self.goal, obs.loc) < self.settings.tilesize: 
                self.goal = None
                Agent.orders[self.id] = None
            # plan orders
            self.plan(spawnammo)
            self.goal = self.orders[self.id]
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
                print 'Warning: friendly fire'
                
        #don't shoot if there is a wall in front of the enemy
        if line_intersects_grid(loc, obs.foes[0][0:2], self.grid, self.settings.tilesize):
            shoot = False
            print 'wall in front of enemy'
        
        if shoot == True:
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
        pass
