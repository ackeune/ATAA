from random import choice
import math

class Brigadier():
    '''

    '''

    NUM_AMMO = 2

    # The most important variable:
    orders = {}

    # Worldspecific vars
    cps = []             # Controlpoints (x,y,owner)
    ammopacks = set()    # Ammopoints (x,y,present)
    targets = {}         # All seen foes by agentid:
                         #   {id: {(x,y,angle) : agent_angle}} 

    # TODO: We already know positions of the ammo
    # ammo_locs = set([( , ), ( , )])

    # When initialized.. do other stuff
    initial_step = True

    def __init__(self, all_agents):
        self.all_agents = all_agents
        self.settings = self.all_agents[0].settings
        self.team = self.all_agents[0].team
        self.orders = {0: None, 1: None, 2: None}

    def __del__(self):
        pass

    def observe(self):
        '''
        All agent observations are present!
        '''
        if self.initial_step:
            self.first_observation()
            self.initial_step = False
        
        self.cps = self.all_agents[0].observation.cps

        # Local vars for efficiency
        ammopacks = set()
        targets = {}
        foes = set()

        for agent in self.all_agents:
            obs = agent.observation
            
            # Seen foes, indexed by agentid, values are dicts:
            # {foe : angle_needed_for_kill}
            targets[agent.id] = agent.visible_targets()
            
            # Present ammopacks
            ammopacks |= set([x[:2] for x in filter(lambda x : x[2] == "Ammo", obs.objects)])
            # Present foes
            foes |= set(obs.foes)
        
        self.targets = targets
        self.ammopacks = ammopacks
        self.foes = foes

    def plan(self, gamestate, ammo_times):
        ''' 
        Plan actions for all agents
        '''
        orders = self.orders
        all_agents = self.all_agents
        cps = self.cps
        team = self.team

        # used functions
        cp_attack = self.cp_attack
        cp_defend = self.cp_defend
        get_ammo = self.get_ammo
        kill_foe = self.kill_foe

        # HACKS
        if gamestate == -2:
            for i in range(2):
                orders[all_agents[i].id] = (cp_attack, cps[i])      
            orders[2] = (get_ammo, None)
            return
 
        # Go for controlpoints with the closest agent preferably
        cps_to_get = [cp for cp in cps if cp[2] != team]
        cps_to_defend = [cp for cp in cps if cp[2] == team]

        # Determine new goals
        for agent in all_agents:
            id = agent.id
            other_agents = [a for a in all_agents if a is not agent]

            # Reach your goal
            # TODO describe goalreached at metalevel?
            if agent.goal_reached():
                orders[id]= None
                
            # Closest agent -> goto cp
            for cp_to_get in cps_to_get:
                if id == self.closest_to_point(cp_to_get):
                    orders[id] = (cp_attack, cp_to_get)
                    break
            
            if not orders[id]:
                if not agent.ammo:
                    orders[id] = (get_ammo, None) 
                elif cps_to_defend:
                    orders[id] = (cp_defend, cps_to_defend.pop())
                else:
                    orders[id] = (cp_attack, [cp for cp in cps if cp[2] != team][0])

    def action(self):
        for agent in self.all_agents:
            # Execute the found command
            (command, goal) = self.orders[agent.id]
            command(agent, goal)
            
            # Always get close ammo though
            self.get_ammo_en_route(agent)

    def hardest_cp(self):
        for cp in self.cps:
            # uncaptured + unattacked
            if cp[2] != self.team and not (self.cp_defend, cp) in self.orders.values():
                return cp
        return None

    def kill_foe(self, agent, foe=None):
        foe = foe if foe else self.closest_foe(agent)
        # 'Agent {0}: kill {1}'.format(agent.id, foe)
        if foe:
            agent.goal = foe
        else:
            self.get_ammo(agent)

    def cp_defend(self, agent, cp=None):
        if not agent.ammo:
            return self.get_ammo(agent)
        
        cp = cp if cp else self.closest_cp(agent)
        #print 'Agent {0}: defend {1}'.format(agent.id, cp)
        agent.goal = cp[:2]

    def cp_attack(self, agent, cp=None):
        cp = cp if cp else self.closest_cp(agent)
        #print 'Agent {0}: attack {1}'.format(agent.id, cp )
        agent.goal = cp[:2]

    def get_ammo(self, agent, ammo_loc=None):
        #print 'Agent {0}: get ammo'.format(agent.id)
        if not self.get_ammo_en_route(agent, 30):
            # for now, just make it walk somewhere else
            agent.goal = self.cps[0]
    
    def kill_en_route(self, agent):
        if self.foes and agent.ammo:
            closest_foe = self.closest_foe(agent) 
            if agent.can_shoot(closest_foe):
                agent.goal = closest_foe
                agent.shoot = True

    def get_ammo_en_route(self, agent, maxdist=3):
        closest_ammopack = self.closest_ammopack(agent)
        if closest_ammopack and real_dist(agent.loc, closest_ammopack) < maxdist * self.settings.tilesize and not agent.ammo:
            agent.goal = closest_ammopack
            return True
        return False

    def closest_object(self, agent, objectlist):
        best_dist = 1000
        best_object = None
        for o in objectlist:
            dist = real_dist(agent.loc, o[:2])
            if dist < best_dist:
                dist = best_dist
                best_object = o
        return best_object

    def closest_foe(self, agent):
        return self.closest_object(agent, self.foes)

    def closest_ammopack(self, agent): 
        return self.closest_object(agent, self.ammopacks)
    
    def closest_cp(self, agent):
        return self.closest_object(agent, self.cps)

    def closest_to_point(self, point):
        best_dist = 1000
        best_id = None
        for agent in self.all_agents:
            dist = real_dist(agent.loc[:2], point[:2])
            if dist < best_dist:
                dist = best_dist
                best_id = agent.id
        return best_id

    def __str__(self):
       items = sorted(self.__dict__.items())
       maxlen = max(len(k) for k,v in items)
       return "== BRIGADIER ==\n" + "\n".join(('%s : %r'%(k.ljust(maxlen), v)) for (k,v) in items)

    def first_observation(self):
        ''' 
        Decompose the very first observation
        '''
        self.cps = self.all_agents[0].observation.cps      

def real_dist(a, b):
    '''
    Should compute the real length of the path. For now, 
    equals real_dist.
    '''
    return ((a[0]-b[0]) ** 2 + (a[1]-b[1]) ** 2) ** 0.5

def point_dist(a, b):
    return ((a[0]-b[0]) ** 2 + (a[1]-b[1]) ** 2) ** 0.5

class Fieldmarshal():

    # gamestates
    INIT = -2
    LOSING = -1
    EVEN = 0
    WINNING = 1

    NUM_AMMO = 2
    NUM_AGENTS = 3

    # Dynamic world variables
    ammo_times = {}
    cps = []
    ammos = []

    def __init__(self, brigadier, mesh):
        self.brigadier = brigadier
        self.all_agents = self.brigadier.all_agents
        self.team = self.brigadier.team
        self.settings = self.brigadier.settings
        self.cps = self.brigadier.cps

        self.state = self.INIT
        self.ammos = [0] * self.NUM_AGENTS
        self.mesh = self.init_mesh(mesh)       

    def strategize(self):
        self.brigadier.observe()
        self.update_mesh()
        self.update_state()
        self.brigadier.plan(self.state, self.ammo_times)
        self.brigadier.action()

    def update_state(self):
        cps = self.brigadier.cps

        cps_foe = len([cp for cp in cps if cp[2] != self.team and cp[2] != 2])
        cps_friend = len([cp for cp in cps if cp[2] == self.team])
        cps_even = len(cps) - cps_foe - cps_friend        
        
        if cps_even == len(cps):
            self.state = self.INIT
        elif cps_foe > cps_friend:
            self.state = self.LOSING
        elif cps_foe == cps_friend:
            self.state = self.EVEN
        elif cps_foe < cps_friend:
            self.state = self.WINNING

        # if an ammopack is visible, update timer
        for ammopack in self.brigadier.ammopacks:
            self.ammo_times[ammopack] = 0
        # TODO Check if ammo should be visible but isnt
        
        # Update properties for all agents
        for agent in self.all_agents:
            # Check if agent collected ammo
            if agent.ammo > self.ammos[agent.id]:
                # ammo collected
                self.ammo_times[self.brigadier.closest_ammopack(agent)] = 16
            # Update ammo for each agent
            self.ammos[agent.id] = agent.ammo
        

        # Update ammo timers
        for ammopack in self.ammo_times:
            self.ammo_times[ammopack] -= 1

    def reward(self):
        return self.state
 
    def init_mesh(self, mesh):
        ''' 
        Mesh is a dict of dicts mesh[(x1,y1)][(x2,y2)] = nr_of_turns

        NOTE nr_of_turns does not include turning of the agent
        '''
        
        # TODO Add interesting nodes    
        # Nodes are given equal cost if in same movement range
        for node1 in mesh:
            for node2 in mesh[node1]:
                # Get the old movement cost
                cost = math.ceil(mesh[node1][node2] / float(self.settings.max_speed))
                mesh[node1][node2] = cost * self.settings.max_speed
        return mesh

    def update_mesh(self):
        '''
        Add places of interest to mesh, based on observation.
        '''
        # Add ammopack locations, if still unknown
        if len(self.ammo_times) < self.NUM_AMMO:
            for ammopack in self.brigadier.ammopacks:
                if ammopack not in self.ammo_times:
                    self.ammo_times[ammopack] = 0
                    # add ammo_loc to mesh with large bonus
                    self.add_to_mesh(ammopack, 40)

    def add_to_mesh(self, node, bonus):
        '''
        Add one node to the mesh, connect to every possible present node,
        give it bonus (so agents have an incentive to reach it).

        NOTE overrides previous values completely.
        '''
        mesh = self.mesh
        tilesize = self.settings.tilesize
        max_speed = self.settings.max_speed
        grid = self.all_agents[0].grid
        
        # Add nodes!
        mesh[node] = dict([(n, math.ceil(point_dist(node,n) / float(max_speed)) * max_speed - bonus) for n in mesh if not line_intersects_grid(node,n,grid,tilesize)])




import imp
import copy
from libs.astar import astar

class Agent(object):
    NAME = "dumbbot"
    
    def __init__(self, id, team, settings=None, field_rects=None, field_grid=None, nav_mesh=None, blob=None):
        """ Each agent is initialized at the beginning of each game.
            The first agent (id==0) can use this to set up global variables.
            Note that the properties pertaining to the game field might not be
            given for each game.
        """
        self.id = id
        self.team = team
        self.grid = field_grid
        self.corners = get_corners(field_grid)
        self.settings = settings
        self.goal = None
        self.callsign = '%s-%d'% (('BLU' if team == TEAM_BLUE else 'RED'), id)
        self.relocate = True     

        # Read the binary blob, we're not using it though
        #if blob is not None:
        #    print "Agent %s received binary blob of %s" % (
        #       self.callsign, type(pickle.loads(blob.read())))
        #    # Reset the file so other agents can read it.
        #    blob.seek(0) 
        
        # Recommended way to share variables between agents.
        if id == 0:
            self.all_agents = self.__class__.all_agents = [self]
            self.brigadier = self.__class__.brigadier = Brigadier(self.all_agents)
            self.fieldmarshal = self.__class__.fieldmarshal = Fieldmarshal(self.brigadier, nav_mesh)
        else:
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

        self.loc = self.observation.loc + (self.observation.angle,)
        self.ammo = self.observation.ammo
        self.shoot = False

        if observation.selected:
            print observation

        # All agent observations are present
        if self.id == len(self.all_agents) - 1:
            self.fieldmarshal.strategize()

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        obs = self.observation 

        # Always go for targets!
        target = self.brigadier.targets[self.id]
        if self.ammo and target:
            turn = target.values()[0]
            # TODO adapt speed based on current goal
            newloc = self.loc[:2] + (angle_fix(self.loc[2] + turn),)
            speed = math.cos(angle_fix( get_rel_angle(newloc, self.goal)))
            shoot = True
            print 'Turning {0}'.format(turn)
            return turn, speed, shoot

            
        path = self.find_optimal_path()
        if path:
            dx = path[0][0] - obs.loc[0]
            dy = path[0][1] - obs.loc[1]
            
            speed = ( dx ** 2 + dy ** 2 ) ** 0.5
            
            turn = angle_fix( math.atan2(dy, dx) - obs.angle )
            if abs(turn) > self.settings.max_turn + 0.3:
                speed = 0
                self.shoot = False
        else:
            turn = 0
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
       
    def __str__(self):
        return "Agent " + self.id

    def find_optimal_path(self):
        ''' 
        Pathplanning! 
        '''

        # Define current and goal location
        loc = self.loc
        start = self.loc[:2]
        goal = self.goal
        end = self.goal[:2]

        # For readability and perhaps even speed
        grid = self.grid
        tilesize = self.settings.tilesize
        max_speed = self.settings.max_speed
        max_turn = self.settings.max_turn

        # If there is a straight line, just return the end point
        if not line_intersects_grid(loc[:2], goal[:2], grid, tilesize):
            return [goal]
        
        # Copy mesh so we can add temp nodes
        mesh = copy.deepcopy(self.fieldmarshal.mesh)
        # Add temp nodes for start
        mesh[start] = dict([(n, point_dist(start,n)) for n in mesh if not line_intersects_grid(start,n,grid,tilesize)])
        # Add temp nodes for end:
        if end not in mesh:
            endconns = [(n, point_dist(end,n)) for n in mesh if not line_intersects_grid(end,n,grid,tilesize)]
            for n, dst in endconns:
                mesh[n][end] = dst
        
        # NOTE TO SELF:
        # We're currently faking that the rotated node is a neighbour 
        # as well by implicitly representing the cost of its movement
        # through extra cost
        neighbours = lambda n: [n2 + (get_angle(n,n2),) for n2 in mesh[n[:2]].keys()]
        # cost is meshcost + number of steps turns needed
        cost = lambda n1, n2 : mesh[n1[:2]][n2[:2]] + abs(math.floor(get_rel_angle(n1, n2) / max_turn)) * 40
        goal       = lambda n: n[:2] == end[:2]
        heuristic  = lambda n: ((n[0]-end[0]) ** 2 + (n[1]-end[1]) ** 2) ** 0.5
        nodes, length = astar(loc, neighbours, goal, 0, cost, heuristic)
        return nodes

    def visible_targets(self):
        """ Determine foes that can be hit in this turn.

            Return a list of foes and correct angles
        """
        loc = self.loc
        obs = self.observation
        visible_targets = {}
        max_turn = self.settings.max_turn
        agent_radius = 7

        # Foes are possible targets if in range and in turnrange
        foes_in_range = [(foe, angles_plus_dist(loc, foe, agent_radius, max_turn)) for foe in obs.foes if point_dist(loc[:2], foe[:2]) < self.settings.max_range + agent_radius and abs(get_rel_angle(loc, foe)) < max_turn + 0.1]
       
        # Stop if no foes in range found
        if not foes_in_range or not self.ammo:
            return visible_targets
 
        # Same goes for friends
        friends_in_range = [angles_plus_dist(loc, friend, agent_radius, max_turn) for friend in obs.friends if point_dist(loc[:2], friend[:2]) < self.settings.max_range + agent_radius and abs(get_rel_angle(loc, friend)) < max_turn + 0.2]
    
        # Take corners into account as well
        wall_corners = corners_in_range(self.corners, loc)
        # Now a list [(a1, a1, dist, type), ...]
        wall_corners = [angles_plus_dist(loc, c[:2], 0, max_turn) + c[:-3:-1] for c in wall_corners]

        # obstacles is now a list of tuples for each object:
        # (rel_angle_left, rel_angle_right, distance, [cornertype])
        obstacles = friends_in_range + wall_corners

        # Check if foe-angles overlap with friend-angles or grid-angles
        for foe_loc, foe in foes_in_range:
            foe_a1, foe_a2, foe_d = foe

            # Alter shot if an object is in front of the foe, or if another
            # foe is in front of it
            for obstacle in ([o for o in obstacles if o[2] < foe_d] + [f for l,f in foes_in_range if f != foe]):

                # if this is a wall, check the type
                if len(obstacle) == 4:
                    if obstacle[2] < 2:
                        obstacle = (obstacle[0],
                                    obstacle[1] + max_turn,
                                    obstacle[3])
                    else:
                        obstacle = (obstacle[0] - max_turn,
                                    obstacle[1],
                                    obstacle[3])

                obst_a1, obst_a2, obst_dist = obstacle
                # Multiple cases for overlapping
                # - right-of-obstacle overlaps 
                # - left-of-obstacle overlaps
                # - entire overlap
                if foe_a1 < obst_a2 < foe_a2:
                    foe_a1 = obst_a2
                elif foe_a1 < obst_a1 < foe_a2:
                    foe_a2 = obst_a1
                elif foe_a1 > obst_a1 and foe_a2 < obst_a2:
                    foe_a1 = None
                    foe_a2 = None
                
            
            if foe_a1 is not None and foe_a1 < foe_a2 and abs(foe_a1 - foe_a2) > 0.025 and not line_intersects_grid(loc[:2], foe_loc[:2], self.grid, self.settings.tilesize):
               visible_targets[foe_loc] = (foe_a1 + foe_a2) / 2.0

        return visible_targets

    def can_shoot(self, foe):
        '''
        Check if possible to shoot the enemy
        '''      
        # Shoot enemies at all times
        return foe in self.visible_targets()
        
    def goal_reached(self):
        return self.goal is not None and point_dist(self.goal, self.loc) < self.settings.tilesize
   

# AUX FUNCTIONS
def get_corners(walls, tilesize=16):
    """Yield indices of all wall corners and the type.
    types:

        0:  X _     1:  _X
            _ _         __

        2:  _ _     3:  _ _
            X _         _ X

    format: (x, y, type)
    """
    corners = []
    for i in xrange(len(walls) - 1):
        for j in xrange(len(walls[0]) - 1):
            a = walls[i][j]
            b = walls[i + 1][j]
            c = walls[i][j + 1]
            d = walls[i + 1][j + 1]
            if a + b + c + d == 1:
                cornertype = b + 2 * c + 3 * d
                corners.append((tilesize * (i + 1), 
                                tilesize * (j + 1), cornertype))
    return corners

def corners_in_range(corners, loc, rng=60):
    for corner in corners:
        dx = corner[0] - loc[0]
        dy = corner[1] - loc[1]
        dist = (dx**2 + dy**2) ** 0.5
        if (dx > 0 and dy > 0) or (dx < 0 and dy < 0):
            cornertypes = (1,2)
        else:
            cornertypes = (0,3)
        if dist <= rng and corner in cornertypes:
            yield corner + (dist,)

def get_rel_angle(a1, a2):
    """ Positive angle indicates a right turn. Relative call.
    """
    return angle_fix(math.atan2(a2[1]-a1[1], a2[0]-a1[0]) - a1[2])

def get_angle(a1, a2): 
    """ Absolute call.
    """
    return math.atan2(a2[1]-a1[1], a2[0]-a1[0])

def angles_plus_dist(a1, a2, r, max_turn):
    """ Calculate angle relative to a1s orientation to the sides of 
        a2, where a2 is a circle with radius r.
    """
    dist = point_dist(a1, a2)
    angle = get_rel_angle(a1, a2)
    angle_rel = math.asin(r / dist)
    left = max(angle - angle_rel, -max_turn)
    right = min(angle + angle_rel, max_turn)
    return (left, right, dist)
