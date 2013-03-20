from random import choice
class Planner():
    CPS= [(216, 56), (248, 216)]
    orders = []
    ammpoints = [(9.5*16, 8.5*16),(19.5*16, 8.5*16) ]
    UCPS = CPS
    spawnedammo =[True, True]
    campspots = ((12.5*16 , 4.5*16), (16.5*16, 12.5*16))
    campedspots = []

    def __init__(self, all_agents):
        self.all_agents = all_agents
        self.team = self.all_agents[0].team
        self.orders = {0: None, 1: None, 2: None}
        

    def closestagent(self, goal):
        best_dist = 1000
        best_id = None
        for agent in self.all_agents:
            dist = ((agent.loc[0]-CPS[i][0]) ** 2 + (agent.loc[1]-CPS[i][1]) ** 2) ** 0.5
            if dist < best_dist:
                dist = best_dist
                best_id = agent.id
        return best_id

    def closest_point(self, loc, points):
        best_dist = 99999
        best_object = None
        for i in points:
            dist = ((loc[0]-CPS[i][0]) ** 2 + (loc[1]-CPS[i][1]) ** 2) ** 0.5
            if dist < best_dist:
                dist = best_dist
                best_object = i
        return i

    def update(self, obs):
        pass
        
                

    def plan(self):
        for agent in all_agents:
            id = agent.id
            if agent.goal_reached():
                orders[id]= None
                
            #cap nearest uncapped point
            for uncapped in UCPS:
                if id == self.closestagent(uncapped):
                    if not uncapped[:2] in orders:
                        orders[id] = uncapped[:2]                    
                        break
            
            if not orders[id]:
                if not agent.ammo:
                    #cap nearest spawned ammo
                    for sa in spawnedammo:
                        if id == self.closestagent(sa):
                            orders[id] = (sa)
                    #defend a capped point needs improvement
                else:
                    orders[id] = choice(CPS)
                    
                        
        

    





class Agent(object):
    
    NAME = "agent_anna"
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None):
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
        #if blob is not None:
        #    print "Agent %s received binary blob of %s" % (
        #       self.callsign, type(pickle.loads(blob.read())))
        #    # Reset the file so other agents can read it.
        #    blob.seek(0) 
        
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = []
                
        self.all_agents.append(self)
        self.planner = self.__class__.planner = Planner(self.all_agents)
    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.selected = observation.selected
        self.planner.plan()

        if observation.selected:
            print observation
                    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation
        
        
        # Shoot enemies
        shoot = False
        if (obs.ammo > 0 and 
            obs.foes and 
            point_dist(obs.foes[0][0:2], obs.loc) < self.settings.max_range and
            not line_intersects_grid(obs.loc, obs.foes[0][0:2], self.grid, self.settings.tilesize)):
            self.goal = obs.foes[0][0:2]
            shoot = True
        self.goal = self.planner.orders[self.id]
        print self.id
        print self.goal

        # Compute path, angle and drive
        path = find_path(obs.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
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
        
