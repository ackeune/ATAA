from random import choice
import math
class Agent(object):
    goal0 = (0,0)
    goal1 = (0,0)
    goal2 = (0,0)
    cps1loc = (216, 56)
    cps2loc = (248, 216)
    ammo1loc = (9.5*16, 8.5*16)
    ammo2loc = (19.5*16, 8.5*16)
    NAME = "Hard_Coded"
    AMMO1 = True
    AMMO2 = True
    set1 = False
    set2 = False
    Ammo = [ammo1loc, ammo2loc]
    Ammospawned = [AMMO1, AMMO2]
    CPS =[cps1loc, cps2loc]        
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
    camp1loc = (12.5*16 , 4.5*16)
    camp2loc = (16.5*16, 12.5*16)
    camplocs= (camp1loc,camp2loc)
    score = (0,0)
    reset1= 0
    reset2=0

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
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        
        self.observation = observation
        if self.observation.respawn_in  > -1:
            self.setGoal((0,0))
        self.selected = observation.selected
        if observation.selected:
            pass
           # print observation

    def diffGoal(self, goal):
        goal = self.locToZone(goal)
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
        

    
    def setGoal(self, goal):
        if(self.id == 0):
            Agent.goal0 = self.locToZone(goal)
        elif(self.id == 1):
            Agent.goal1 = self.locToZone(goal)
        elif(self.id == 2):
            Agent.goal2 = self.locToZone(goal)
        
        return goal

    def attack (self, obs):
        bestPC = self.closest_UCP(self.team, obs)
        copy = list(self.CPS)
        if bestPC is not None:
            copy.remove(bestPC)
       
        other = copy[0]
        
        if bestPC is not None and self.diffGoal(bestPC):
            
            return bestPC
        elif len(other)== 2 and self.diffGoal(other):
            return other
        else:
            return None
            
        
    def defend (self, obs):
        if obs.ammo > 0:
            bestPC = self.closest_CP(obs.loc , self.camplocs)
            if bestPC is not None and self.diffGoal(self.camplocs[bestPC]):
                return self.camplocs[bestPC]
            else:
                return None
        else:
            return None
    def getAmmo (self, obs):
        spawnedammo = []
        for i in range(0, len(self.Ammospawned)):
            if self.Ammospawned[i] == True:
                spawnedammo.append(self.Ammo[i])
        
        nearestammo = self.closest_ammo(obs.loc, spawnedammo)
       #print ammochoice
        if self.diffGoal(self.Ammo[nearestammo]) and self.Ammospawned[nearestammo] == True:
            return self.Ammo[nearestammo]
        
        else:
            
            return None
    def support (self, obs):
        #see how many foes are in what zone, go there
        #for now, go to closest point
        return self.CPS[self.closest_CP(obs.loc , self.CPS)]
        
        
            
            
            

           
          
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        #update ammo status
        if (obs.step - self.reset1)> 8 and self.set1 == True:
            Agent.AMMO1 = True
            Agent.Ammospawned[0] = True
            Agent.set1 = False
        if (obs.step - self.reset1)> 8 and self.set2 == True:
            Agent.AMMO2 = True
            Agent.Ammospawned[1] = True
            Agent.set2 = False
        if len(obs.objects) >0:
            for c in range (0, len(obs.objects)):
                ammopos = (obs.objects[c][0], obs.objects[c][1])
        else:
            ammopos = (0,0)
        if ammopos == self.ammo1loc:
              Agent.AMMO1 = True
              Agent.Ammospawned[0] = True
        elif ( self.locToZone(obs.loc) == 4):
              Agent.AMMO1 = False
              Agent.Ammospawned[0] = False
              if self.set1 == False:
                Agent.set1 = True
                Agent.reset1 = obs.step
        if ammopos == self.ammo2loc:
              Agent.AMMO2 = True
              Agent.Ammospawned[1] = True
        elif( self.locToZone(obs.loc) == 5):
              Agent.AMMO2 = False
              Agent.Ammospawned[1] = False
              if self.set2 == False:
                Agent.set2 = True
                Agent.reset2 = obs.step

        
              
        cps1 = obs.cps[0]
        cps2 = obs.cps[1]
        # Shoot enemies
        shoot = False
        a =self.attack(obs)
        g =self.getAmmo(obs)
        b =self.defend(obs)
        s =self.support(obs)
        #cap closest uncapped point
        if a is not None:
            self.goal = self.setGoal(a)
            #print 'CHAAAAAAAAAAARRRRGEEEEE!' , self.id
        elif b is not None:
            self.goal = self.setGoal(b)
            
            #print 'DEFENDING FOR THE HOME COUNTRY!' , self.id
            #print 
        elif g is not None:
            self.goal = self.setGoal(g)
            
            #print 'AMMO, AMMO I NEED MORE AMMO!', self.id
        else:
            self.goal = s
            
            
            
            
        
                    
        
                    
    
       #shoot
       
        if (obs.ammo > 0 and obs.foes and point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = obs.foes[0][0:2]
            shoot = True
        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]               
            speed = ( dx ** 2 + dy ** 2 ) ** 0.5         
            turn = angle_fix( math.atan2(dy, dx) - obs.angle )
        if abs(turn) > self.settings.max_turn:
            speed = 0
            self.shoot = False
            
        
        
        
        return (turn,speed,shoot)

    def closest_to_point(self, point):
        best_dist = 1000
        best_id = None
        for agent in self.all_agents:
            dist = real_dist(agent.loc[:2], point[:2])
            if dist < best_dist:
                dist = best_dist
                best_id = agent.id
        return best_id

    def closest_ammo(self, loc, Ammo):
            bestdist = 9999
            best = 0
            for i in range (0, len(Ammo)):
                dist = ((loc[0]-Ammo[i][0]) ** 2 + (loc[1]-Ammo[i][1]) ** 2) ** 0.5
                if dist < bestdist:
                    bestdist = dist
                    best = i
            return best
        
    def closest_CP(self, loc, CPS):
        bestdist = 9999
        best = 0
        for i in range (0, len(CPS)):
            dist = ((loc[0]-CPS[i][0]) ** 2 + (loc[1]-CPS[i][1]) ** 2) ** 0.5
            if dist < bestdist:
                bestdist = dist
                best = i
        if (len(CPS) == 1):
            return 0
        return best

    
        
    def closest_UCP (self, team,  obs):
        closestcp = self.closest_CP(obs.loc, obs.cps)
        if obs.cps[closestcp][2] != team:
            return (obs.cps[closestcp][0],obs.cps[closestcp][1]) 
        elif (len(obs.cps) > 1):
            newCPS = list(obs.cps)
            newCPS.remove(obs.cps[closestcp])
            self.closest_CP(obs.loc,  newCPS)
        
       
        
        
    

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
        
