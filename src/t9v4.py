import os, sys
##sys.path.append("%s%s%s" % (os.getcwd(), os.sep, "waard"))
##from waard_functionality import WaardFunctionality

class Agent(object):
    
    NAME = "Awesome Asimo"
    
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
        self.role = None
        self.shoot = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        # Current map has the following ammo pack locations:
        self.ammo_location = [(312, 136), (152, 136)]
        
        # Read the binary blob, we're not using it though
        if blob is not None:
            print "Agent %s received binary blob of %s" % (
               self.callsign, type(pickle.loads(blob.read())))
            # Reset the file so other agents can read it.
            blob.seek(0) 
        
        # Recommended way to share variables between agents.
        if id == 0:
            # All agents: probably not needed in the future
            self.all_agents = self.__class__.all_agents = []
            # Create a shared decision tree
            self.decision_tree = self.__class__.decision_tree = WaardDecisionTree(self)
            self.func = self.__class__.func = self.decision_tree.func
        else:
            self.decision_tree.add_agent(self)

        #probably not needed anymore
        self.all_agents.append(self)
    
    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        # Empty shared observations if this is the first agent
        # Not sure if this is needed: maybe keep old information about the world
        self.decision_tree.process_observation(observation)

        if id == 0:
            self.all_observations = []
        self.observation = observation
        self.selected = observation.selected
        if observation.selected:
            print observation
        self.decision_tree.set_agent_goal(self)
                    
    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        path = find_path(self.observation.loc, self.goal, self.mesh, self.grid, self.settings.tilesize)
        if path:
            dx = path[0][0] - self.observation.loc[0]
            dy = path[0][1] - self.observation.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - self.observation.angle)
            if turn > self.settings.max_turn or turn < -self.settings.max_turn:
                self.shoot = False
            speed = (dx**2 + dy**2)**0.5
        else:
            turn = 0
            speed = 0
        if(self.selected):
            print "point dist: %f, turn: %f" % (point_dist(self.observation.loc, path[0]), turn)
        # Fix for the lame shizzle with close targets
        if(point_dist(self.observation.loc, path[0]) < 35 and turn > 0):
            print "setting speed to 0"
            speed = 0

        return (turn,speed,self.shoot)
        
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

class WaardFunctionality:
    """ A class with actions robots can do. If a goal is set by an action, it returns true. """
    def __init__(self, agent):
        """
        Initialize the functionality for this agent. The first agent needs to be
        specified in order to initialize the settings. Also the first agent will
        be put in self.agents
        """
        # Now using maartens Shared init:
        self.agents = []
        # Add initializing agent as first agent
        self.add_agent(agent)
        self.settings = agent.settings
        #print """settings %s: max_turn %d, max_range: %d""" % (
        #    settings, settings.max_turn, settings.max_range)

        # list of ammo locations we should parse a new each time the map
        # updates
        self.ammo_locations = [(152, 136), (312, 136)]

        # list of enemy locations and the time they were spotted
        # the list contains lists of [x, y, angle, steps_ago], with steps_ago
        # indicating how many steps have passed since the enemy was spotted
        # there
        self.enemies = []

        # time step to enemy locations and the like
        self.step = 1

        # Add own team:
        self.team = agent.team

    def add_agent(self, agent):
        """ Agents should add themselves
        in the constructor so the id matches
        the index in the self.agents list (from maartens Shared)"""
        self.agents.append(agent)

    def process_observation(self, observation):
        """ Processes the observation (from maartens Shared)"""

        if self.step != observation.step:
            self.step = observation.step
            self.update_ammo()
            #self.update_enemies()

       
        #for foe in observation.foes:
        #    self.enemies.append([foe[0], foe[1], foe[2], self.step])
        if(len(observation.foes) > 0):
            self.enemies.append(observation.foes)
        # code to filter the ammo from the observations, we might
        # want to actually parse these from the map
        ammo_packs = filter(lambda x: x[2] == "Ammo", observation.objects)
        #print ammo_packs
        if ammo_packs:
            for ammo in ammo_packs:
                if ammo[0:2] not in self.ammo_locations:
                    self.ammo_locations.append(ammo[0:2])

    def update_ammo(self):
        pass

    def update_enemies(self):
        # TODO: remove enemies that have been spotted too long ago to be
        #   relevant
        """
        for i in range(len(self.enemies)):
            enemy = self.enemies[i]
            self.enemies[i] = [enemy[0], enemy[1], enemy[2], enemy[3] + 1]
        """
        pass

    def set_goal_to_ammo(self, id):
        """ Sets the goal to the closest ammo spawn point. This ignores whether it's filled or not """
        self.agents[id].goal = self.get_closest(self.ammo_locations, id)
        return True
        print "agent %d setting destination to %s to find ammo" % (id, str(self.agents[id].goal))

    def set_goal_to_point(self, id, point):
        """ Sets the goal to the closest enemy (or neutral) control point """
        self.agents[id].goal = point
        return True

    def set_goal_to_control_point(self, id):
        """ Sets the goal to the closest enemy (or neutral) control point """
        enemy_cps = []
        for cp in self.agents[id].observation.cps:
            if cp[2] != self.team:
                enemy_cps.append(cp[0:2])
        # Find closest non-owned CP
        if len(enemy_cps) > 0:
            self.agents[id].goal = self.get_closest(enemy_cps, id)
            print "agent %d setting destination to %s to capture cp" % (id, str(self.agents[id].goal))
            return True
        return False
    
    def set_goal_to_close_ammo(self, id):
        ammopacks = filter(lambda x: x[2] == "Ammo", self.agents[id].observation.objects)
        if ammopacks:
            self.agents[id].goal = ammopacks[0][0:2]
            return True
        return False

    def set_goal_to_shoot(self, id):
        self.agents[id].shoot = False
        if (self.agents[id].observation.ammo > 0 and 
            self.agents[id].observation.foes and 
            point_dist(self.agents[id].observation.foes[0][0:2], self.agents[id].observation.loc) < self.agents[id].settings.max_range and
            not line_intersects_grid(self.agents[id].observation.loc, self.agents[id].observation.foes[0][0:2], self.agents[id].grid, self.agents[id].settings.tilesize)):
            # Check if an ally is in the way
            print "bot %s shooting enemy %s" % (self.agents[id].id, self.agents[id].observation.foes[0])
            # Don't shoot friends!
            for friend in self.agents[id].observation.friends:
                if(line_intersects_circ(self.agents[id].observation.loc, self.agents[id].observation.foes[0][0:2], friend, 6)):
                    return False
            self.agents[id].goal = self.agents[id].observation.foes[0][0:2]
            self.agents[id].shoot = True
            return True
        return False
    
    def set_goal_to_finest_enemy(self, id):
        # Select last 3 viewed enemies:
        enemies = self.enemies[-3:len(self.enemies)]
        enemies = [item for inner_list in enemies 
               for item in inner_list ]

        # Find closest of those
        enemy = self.get_closest(enemies, id)
        enemy = (enemy[0], enemy[1])
        self.agents[id].goal = enemy
        print "Bot %d will murder enemy %s" % (id, str(enemy))
        return True
        return False

    def get_closest(self, points_list, id):
        """ Returns the closest point to the agent in "list"
        """
        previous_dist = 1000000
        for item in points_list:
            dist = point_dist(item, self.agents[id].observation.loc)
            if dist < previous_dist:
                previous_dist = dist
                selected_item = item  
        if previous_dist != 1000000:
            return selected_item
        else:
            print "No closest point was found! This should not be possible! returning ammo pack 0 to prevent errors"
            return self.ammo_locations[0]
        
class WaardDecisionTree:

    def __init__(self, agent):
        self.DEFENDER = 0
        self.ATTACKER = 1
        self.func = WaardFunctionality(agent)
        self.settings = agent.settings
        # Roles
        self.roles = []
        # A role looks like this: 
        # (id, self.DEFENDER/self.ATTACKER, cp_location/0)
        self.defended_cps = []

    def assign_role(self, agent):
        # First assign cp defender roles
        if(len(self.defended_cps) != len(agent.observation.cps)):
            undefended_cps = []
            for cp in agent.observation.cps:
                if cp not in self.defended_cps:
                    undefended_cps.append(cp)
            if(len(undefended_cps) > 0):
                cp = self.func.get_closest(undefended_cps, agent.id)
                print "assigning defender role of cp %s to agent %d" % (str(cp), agent.id)
                self.defended_cps.append(cp)
                role = (agent.id, self.DEFENDER, cp[0:2])
        else:
            # If cp's are defended, assign attacker role:
            role = (agent.id, self.ATTACKER, 0)
            print "assigning attacker role to agent %d" % (agent.id)
        agent.role = role
        self.roles.append(role)
              
    def add_agent(self, agent):
        self.func.add_agent(agent)

    def process_observation(self, observation):
        self.func.process_observation(observation)
    
    def set_agent_goal(self, agent):
        """ 
        Specifies the decision tree of our robot, using the actions in
        WaardFunctionality 
        
        Will contain 2 roles:
        - defender#: will defend cp # (as many defenders as cp's should always
          be available)
        - attacker: All other tanks are attackers
        """

        if(agent.role == None):
            self.assign_role(agent)
            print "Assigned role %s to agent %d" % (str(agent.role), agent.id)
        # Defender decision tree:
        if(agent.role[1] == self.DEFENDER):
            self.func.set_goal_to_point(agent.id, agent.role[2])
        # Atacker decision tree:
        elif(agent.role[1] == self.ATTACKER):
            if(agent.observation.ammo > 0):
                print "ammo > 0"
                if not(self.func.set_goal_to_shoot(agent.id)):
                    if(self.func.set_goal_to_finest_enemy(agent.id)):
                        return
            if not(self.func.set_goal_to_shoot(agent.id)):
                if not(self.func.set_goal_to_close_ammo(agent.id)):
                    #if not(self.func.set_goal_to_control_point(agent.id)):
                    self.func.set_goal_to_ammo(agent.id)
        if self.func.agents[agent.id].goal == None:
            print "falling back to set goal to ammo"
            self.func.set_goal_to_ammo(agent.id)

