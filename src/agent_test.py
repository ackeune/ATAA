from random import randrange

class Agent(object):

    blobdict = {}
    lastaction = -1
    laststate = ()
    goal0 = (0,0)
    goal1 = (0,0)
    goal2 = (0,0)
    cps1loc = (216, 56)
    cps2loc = (248, 216)
    ammo1loc = (9.5*16, 8*16)
    ammo2loc = (19.5*16, 8*16)

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
        if (laststate[1] == self.team and state[1] != self.team):
            reward-=5
        if (laststate[2] == self.team and state[2] != self.team):
            reward-=5
        if ((state == 2 and laststate == 2 )or(state == 3 and laststate == 3)):
            reward+=2
            if obs.ammo > 0 :
                reward+=9
        if(laststate[3]< state[3] ):
            reward +=3
            if laststate[3] ==0:
                reward+=3         
        return reward
        
        
        
        
    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        cps1 = obs.cps[0]
        cps2 = obs.cps[1]
        action = -1
        ammo = False
        if(obs.ammo > 0):
            ammo = True
        foes = False
        if(len(obs.foes) > 0):
            foes = True
        state = (self.locToZone(obs.loc), cps1[2], cps2[2], ammo, self.AMMO1, self.AMMO2, foes)
        reward = self.getReward(self.laststate, state, obs)
        if not str(state) in self.blobdict:
            #[cap nearest, get ammo, hunt] camp points/control zone
            Agent.blobdict[str(state)] = '[10, 10, 10]'
            action = randrange(0,2)
        else:
            values = eval(self.blobdict[str(state)])
            action = max( (v, i) for i, v in enumerate(values) )[1]
        self.lastaction = action

        
        if obs.respawn_in == -1:
            if cps1[2] != self.team and self.diffGoal(self.cps1loc) == True:
                    self.goal = self.cps1loc
                    self.setGoal(self.cps1loc)
            elif cps2[2] != self.team and self.diffGoal(self.cps2loc):
                    self.goal = self.cps2loc
                    self.setGoal(self.cps2loc)
            elif self.diffGoal(self.ammo1loc):
                self.goal = self.ammo1loc
                self.setGoal(self.ammo1loc)
            elif self.diffGoal(self.ammo2loc):
                self.goal = self.ammo2loc
                self.setGoal(self.ammo2loc)
        else:
            self.setGoal((200, 200))
            self.goal = (200, 200)
            
        # Shoot enemies
        shoot = False
        if (obs.ammo > 0 and 
            obs.foes and 
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = obs.foes[0][0:2]
            shoot = True

        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - obs.angle)
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                shoot = False
                speed = 0.5*(dx**2 + dy**2)**0.5
            else:
                speed = (dx**2 + dy**2)**0.5
        else:
            turn = 0
            speed = 0
        
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
        pickle.dump(self.blobdict, open('../src/agent_test_blob', 'wb'))
        pass
        
