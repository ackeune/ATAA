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
    reset1 = 0
    
    
    ammo = [False, False, False]
    #TODO: locs of all agents, set orders to closest agents.
    #TODO: locs of all enemies, to see if ur closer to ammo.
    orders = [None, None, None]
    allyLocs = None, None, None
    enemyLocs = [None, None, None]
    distance = [(1000,1000,1000), (1000,1000,1000)]
    ammo1loc = (152, 136)
    ammo2loc = (312, 136)
    ammoloc = [ammo1loc, ammo2loc]
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
        Agent.state[3][self.id] = observation.loc

        #Set visible enemy locations #TODO: keep track of enemy to predict movement/strategy 
        if observation.foes:
            
        
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
            '''if observation.loc == self.ammo1loc: 
                    Agent.state[2] = (False, Agent.state[2][1])
            if observation.loc == self.ammo2loc:
                    Agent.state[2] =(Agent.state[2][0], False)
            elif( self.locToZone(observation.loc) == 4):     #only if no ammo seen       
                  Agent.state[2] = (False, Agent.state[2][1])
                  if self.set1 == False:
                    Agent.set1 = True
                    Agent.reset1 = observation.step
            elif( self.locToZone(observation.loc) == 5):    #only if no ammo seen
                  Agent.state[2] =(Agent.state[2][0], False)
                  if self.set2 == False:
                    Agent.set2 = True
                    Agent.reset2 = observation.step'''

        #update CPS state
        Agent.state[1] =(observation.cps)
        
        
        #print self.state
        
        
        if observation.selected:
            #print observation
            pass
                    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        # Check if agent reached goal.
        #print self.goal
        #print type(self.goal)
        #print obs.loc
        #print 'orders', self.orders
        #print self.goal is not []
        spawnammo =[]
        if obs.respawn_in < 1:            
            for a in range (0, len(self.state[2])):
                #print 'state', self.state[2][a]
                if self.state[2][a] == True and self.ammoloc[a] not in self.orders:
                    spawnammo.append(self.ammoloc[a])
            if self.goal is not None  and point_dist(self.goal, obs.loc) < self.settings.tilesize: 
                self.goal = None
                Agent.orders[self.id] = None
                
            #cap uncapped points
            #cap spawned ammo
            print (self.id)
            print self.state
            print self.orders[self.id]
            #print 'made it'   
            #print len(self.state[1])
            if self.orders[self.id] in self.ammoloc:
                if self.orders[self.id] not in spawnammo:# got a goal of ammo that is not there.
                    self.goal = None
                    Agent.orders[self.id] = None
                else:
                    
                
                    #if enemy is closer, leave it

                    #if 
                
                    if 
                    self.goal = None
                    Agent.orders[self.id] = None
            if self.orders[self.id] == None:
                for n in range (0, len(self.state[1])):
                    #print'got here'
                    #print n
                    if self.state[1][n][2] != self.team and self.state[1][n][:2] not in self.orders:
                        #print self.orders
                        #print self.state[1][n][:2] not in self.orders
                        print'Going to cap'
                        #print self.id
                        #print self.state
                        self.goal = self.state[1][n][:2]
                        Agent.orders[self.id] = self.state[1][n][:2]
                        break
                     #defend capped points
                if self.orders[self.id] == None and self.state[0][self.id] == True:
                    ucp = []
                    #got ammo now what? 
                    for n in range (0, len(self.state[1])):
                        if self.state[1][n][2] != self.team and self.state[1][n][:2] :
                            ucp.append(self.state[1][n])
                           # print self.state[1][n]
                           #print 'uncapped point located'
                    #print type (ucp )
                    print 'got ammo trying to find a CP'
                    if ucp:
                        tgoal = self.closest_UCP (self.team,  obs.loc, ucp) # can return Noone ?! 
                        #print 'tgoal',tgoal
                        self.goal = tgoal
                        Agent.orders[self.id] = tgoal
                    if(self.orders[self.id] == None):
                        self.goal = obs.cps[self.closest_CP(obs.loc, obs.cps)][:2] #TODO: CLOSEST MIGHT NOT BE CLOSE IF THERE ARE WALLLSSSS
                        Agent.orders[self.id] = self.goal
                # we know some ammo has spawned            
                elif self.goal ==None and len(spawnammo) > 0  :
                    print 'Getting ammo'
                    print spawnammo
                    self.goal = self.closest_ammo(obs.loc, spawnammo)
                    Agent.orders[self.id] = self.goal
                    #print 'woops'
                    
                elif self.orders[self.id] == None:
                    #print obs.cps[self.closest_CP(obs.loc,obs.cps)]
                    #print self.closest_CP(obs.loc,obs.cps)
                    print 'Nothing new to do stay on point'
                    self.goal = obs.cps[self.closest_CP(obs.loc,obs.cps)][:2]
                    print self.goal
                            
        else:
            self.goal = obs.loc
            print 'IM DEAD :('
                        
        #print self.goal           
                        
                    
        # Drive to where the user clicked
        # Clicked is a list of tuples of (x, y, shift_down, is_selected)
        
        print self.orders
        
        # Shoot enemies
        shoot = False
        turn = 0
        speed = 0
        if (obs.ammo > 0 and 
            obs.foes and 
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = obs.foes[0][0:2]
            shoot = True
            for friendly in obs.friends:
                if line_intersects_circ(obs.loc, obs.foes[0][0:2], friendly, 8):
                    shoot = False
            

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
        pass
        
