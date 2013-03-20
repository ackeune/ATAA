import domination

class Agent(object):

    SAFE_MOVE = False

    # the goal is an (x, y) tuple that the agents moves toward
    goal = None

    NAME = "PAVLO"

    def __init__(self, id, team, settings=None, field_rects=None,
                    field_grid=None, nav_mesh=None, blob=None, matchinfo=None):
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

        # initiate the shared object for the communication between the agents
        if id == 0:
            self.shared = self.__class__.shared = Shared(settings)
        self.shared.add_agent(self)
        self.role_methods = {self.shared.ROLE_NONE:self.role_none,
                                self.shared.ROLE_HUNTER:self.role_hunter,
                                self.shared.ROLE_CP1:self.role_cp,
                                self.shared.ROLE_CP2:self.role_cp}

    def observe(self, observation):
        """ Each agent is passed an observation using this function,
            before being asked for an action. You can store either
            the observation object or its properties to use them
            to determine your action. Note that the observation object
            is modified in place.
        """
        self.observation = observation
        self.shared.process_observation(observation)

        #if self.id == 2:
            #self.shared.determine_roles()

    def action(self):
        """ This function is called every step and should
            return a tuple in the form: (turn, speed, shoot)
        """
        #print "action of agent id %d" % self.id

        # default values; do nothin'!
        turn = 0
        speed = 0
        shoot = False

        path = False

        self.role = self.shared.get_role(self)
        #print "agent with role %d" % self.role

        self.role_methods[self.role]()

        # if there is an enemy in range we might want to act on that
        (turn, speed, shoot) = self.determine_shoot()
        # if we do not shoot we want to override the behavior???
        if not(shoot):
            path = self.find_path_to_goal()

        # if a path has been found we want to go to there
        if path:
            (turn, speed) = path

        # if we are gonna fire our last bullet we will want to recalculate
        # the roles
        if shoot and self.observation.ammo == 1:
            for agent in self.shared.agents:
                agent.role = self.shared.ROLE_NONE


        if self.id == 2:
            self.shared.clear_roles()

        return (turn, speed, shoot)

    def debug(self, surface):
        """ Allows the agents to draw on the game UI,
            Refer to the pygame reference to see how you can
            draw on a pygame.surface. The given surface is
            not cleared automatically. Additionally, this
            function will only be called when the renderer is
            active, and it will only be called for the active team.
        """
        import pygame


        color_line = (00, 00, 00)
        color_fov = (255, 00, 229, 100)
        color_grid  = (120,180,120)


        # First agent clears the screen
        if self.id == 0:
            surface.fill((0,0,0,0))
        if self.goal is not None:
            # rectangle of what the bot sees, always convenient
            rect = pygame.Rect(
                self.observation.loc[0] - (self.settings.max_see/2),
                self.observation.loc[1] - (self.settings.max_see/2),
                    70, 70)
            pygame.draw.rect(surface, color_fov, rect)

            # line to goal, always convenient
            pygame.draw.line(surface, color_line,
                self.observation.loc, self.goal)


        # print the mesh grid because we can
        if self.id == 2:
            for n1 in self.mesh:
                for n2 in self.mesh[n1]:
                    pygame.draw.line(surface,color_grid, n1, n2, 2)
                    pygame.draw.circle(surface, color_grid, n1, 3)

    def finalize(self, interrupted=False):
        """ This function is called after the game ends, 
            either due to time/score limits, or due to an
            interrupt (CTRL+C) by the user. Use it to
            store any learned variables and write logs/reports.
        """
        pass


    def determine_shoot(self):
        """ Determines if the agent should attempt to shoot another agent
            and calculates the `turn' value if the result of this consideration
            is postive. Assumes the enemy is within range.
            returns (turn, 0, True) if the agent should shoot
            return (0, 0, False) if the agent should not shoot """
        if (self.observation.ammo > 0):
            # loop for each foe
            for foe_tuple in self.observation.foes:
                #print "foe: %s" % str(foe_tuple)
                foe = foe_tuple[0:2]

                # check if the hostile fellow is within range
                if (point_dist(self.observation.loc, foe) >
                        self.settings.max_range):
                    break;

                # check for friendly fire
                wont_hit_friendly = True
                for friend in self.observation.friends:
                    if(line_intersects_circ(self.observation.loc, foe, 
                            friend, 6)):
                        wont_hit_friendly = False
                        break

                if wont_hit_friendly:
                    # calculate the turn
                    turn = self.calculate_turn_to_point(foe)

                    # check if we can make the turn
                    if abs(turn) <= self.shared.settings.max_turn:
                        # check if there is no wall in between motherfuckers 
                        if not(line_intersects_grid(self.observation.loc,
                            foe[0:2],
                            self.grid, self.settings.tilesize)):
                            # then finally shoot
                            return (turn, 0, True)
        # if anything fails, we shall return NOTHING!
        return (0, 0, False)




    def find_path_to_goal(self):
        """ calculates the path to a goal
            goal is a (x, y) tuple
            returns (turn, speed) tuple when a path has been found
            returns false when no path has been found
        """
        path = find_path(self.observation.loc, self.goal,
            self.mesh, self.grid) 

        if path:
            dx = path[0][0] - self.observation.loc[0]
            dy = path[0][1] - self.observation.loc[1]
            turn = angle_fix(math.atan2(dy, dx) - self.observation.angle)
            speed = (dx**2 + dy**2)**0.5

            # a random threshhold to determine if we wanna just go for it
            # or rotate safely to the intended angle if we can't reach it
            # at once
            if abs(turn) > self.settings.max_turn:
                if speed < 50:
                    speed = 0

            if self.SAFE_MOVE and abs(turn) > self.settings.max_turn:
                speed = 0
            return (turn, speed)
        return False


    def calculate_turn_to_point(self, point):
        """ calculates a turn value that is required should
        the robot want to turn to a point) """
        dx = point[0] - self.observation.loc[0]
        dy = point[1] - self.observation.loc[1]
        return angle_fix(float(math.atan2(dy, dx)) -
            float(self.observation.angle))
        


    def role_hunter(self):
        """ behavior for the hunter role """
        turn = 0
        speed = 0
        shoot = False

        # if we have ammo
        if self.observation.ammo > 0:
            enemy_location = self.shared.get_finest_enemy(self)
            self.goal = (enemy_location[0], enemy_location[1])
            if not(self.goal):
                self.goal = self.observation.cps[0][0:2]
        # or gather ammo
        else:
            self.goal = self.shared.get_finest_ammo(self)
            #print "ammo location: %s" % str(self.goal)
            if not(self.goal):
                self.goal = self.observation.loc

    def role_cp(self):
        self.goal  = self.shared.get_finest_cp(self)

    def role_none(self):
        pass



class Shared:
    """ shared object in which the agents can add information
    about the world and the stuff they observe """


    ROLE_NONE = 0
    ROLE_CP1 = 1
    ROLE_CP2 = 2
    ROLE_HUNTER = 3

    starting_roles = [ROLE_CP1, ROLE_HUNTER, ROLE_CP2]
    roles = None 

    def __init__(self, settings):
        # lists of the agents I recon we might want to use
        self.agents = []
        self.settings = settings
        print """settings %s: max_turn %d, max_range: %d""" % (
            settings, settings.max_turn, settings.max_range)

        # list of ammo locations
        self.ammo_locations = [(152, 136), (312, 136)]

        # list of control points
        self.cps = [(216, 56), (248, 216)]


        # list of enemy locations and the time they were spotted
        # the list contains lists of [x, y, angle, steps_ago], with steps_ago
        # indicating how many steps have passed since the enemy was spotted
        # there
        self.enemies = []

        # time step to enemy locations and the like
        self.step = 1

    def add_agent(self, agent):
        """ Agents should add themselves
        in the constructor so the id matches
        the index in the self.agents list"""
        #if len(self.agents) == 0:
            #print "%s" % str(agent.mesh)
            #self.re_init_mesh(agent)
            #print "%s" % str(agent.mesh)

        self.agents.append(agent)
        agent.role = self.starting_roles[agent.id]


    def process_observation(self, observation):
        """ Processes the observation"""

        if self.step != observation.step:
            self.step = observation.step
            self.update_ammo()
            #self.update_enemies(observation)
        if(len(observation.foes) > 0):
            self.enemies.append(observation.foes)
       
        #for foe in observation.foes:
        #    self.enemies.append([foe[0], foe[1], foe[2], self.step])

        # code to filter the ammo from the observations, we might
        # want to actually parse these from the map
        ammo_packs = filter(lambda x: x[2] == "Ammo", observation.objects)
        #print ammo_packs
        if ammo_packs:
            for ammo in ammo_packs:
                if ammo[0:2] not in self.ammo_locations:
                    self.ammo_locations.append(ammo[0:2])

    def determine_roles(self):
        """ Calculates the role for each agent. Do this once per round. """
        pass

        #self.roles = [0, 0, 0, 0]

        ## we want to know how many agents are alive at this time and
        ## which roles are covered
        #roles_covered = [0, 0, 0, 0]
        #agents_alive = [] # list with livin' agents (parameter agent excluded)
        #for agent_it in self.agents:
        #    if agent_it.observation.respawn_in == -1:
        #        roles_covered[agent_it.role] = 1
        #        agents_alive.append(agent_it)
        #agents_alive_count = len(agents_alive)

        ## if just this agent is alive we shall hunt them DOWN!
        ## the idea is that things must be goin' really crappy... 
        #if agents_alive_count == 1:
        #    self.roles[agents_alive[0].id] = self.ROLE_HUNTER
                
                


    def get_role(self, agent):
        """ Determines a role for an agent. This bad boy is basically the
        whole high level brains for the entire operation. """
        #return self.roles[agent.id]


        # if the agent is dead, fuck that!
        if agent.observation.respawn_in > -1:
            return self.ROLE_NONE

        # else we want to find a role for the agent requesting it
        roles_covered = [0, 0, 0, 0]
        agents_alive = [] # list with livin' agents (parameter agent excluded)
        for agent_it in self.agents:
            if agent_it.observation.respawn_in == -1:
                roles_covered[agent_it.role] += 1
                if agent.id != agent_it.id:
                    agents_alive.append(agent_it)

        agents_alive_count = len(agents_alive) + 1

        # if just this agent is alive we shall hunt them DOWN!
        # the idea is that things must be goin' really crappy... 
        if agents_alive_count == 1:
            return self.ROLE_HUNTER

        # if there are two agents alive, check which one goes for what
        if agents_alive_count == 2:
            #if not(self.roles):
                
            other_role = agents_alive[0].role
            if other_role == self.ROLE_HUNTER:
                if agent.role == self.ROLE_NONE:
                    return self.get_finest_cp_role(agent)
                return agent.role
            ## if both agents have CPX roles we want one to switch to
            ## a hunter role. This calculation is deterministic so
            ## we can assume the next agent calculates the same thing
           
            ## we want to calculate awesomely which agent is better suited
            ## as hunter, but for now just assign the first one the hunter role
            return self.ROLE_HUNTER 
            
        # if we are all alive, things must be goin' smooth
        if agents_alive_count == 3: 
            #print "before roles: %s" % str(self.roles)
            if self.roles == None:
                #print "reeeeeeeeeeeeeeecalculating"
                self.calculate_roles()

            #print "after roles: %s" % str(self.roles)
            
            return self.roles[agent.id]

            #if agent.role == self.ROLE_NONE:
            #    # check which role is uncovered and take that one
            #    return self.get_finest_cp_role(agent, roles_covered)
            #return agent.role


    def calculate_roles(self):
        role_matrix = []
        for agent in self.agents:
            role_matrix.append(self.role_suitability_for_agent(agent))

        #print "role_matrix: %s" % role_matrix

        m = Munkres()
        indexes = m.compute(role_matrix)
        #print_matrix(role_matrix, msg='Lowest cost through this matrix:')

        self.roles = [-1, -1, -1]
        for agent_id, role in indexes:
            #value = role_matrix[agent_id][role]
            #print '(agent %d, role %d) -> %d' % (agent_id, role, value)
            self.roles[agent_id] = role + 1


    def role_suitability_for_agent(self, agent):
        cp1_distance = domination.utilities.point_dist(agent.observation.loc,
            self.cps[0])
        cp2_distance = domination.utilities.point_dist(agent.observation.loc,
            self.cps[1])
        ammo_distance = domination.utilities.point_dist(agent.observation.loc,
            self.get_finest_ammo(agent))

        return [cp1_distance, cp2_distance, ammo_distance]

        #role_list = [(self.ROLE_CP1, cp1_distance),
        #            (self.ROLE_CP2, cp2_distance),
        #            (self.ROLE_HUNTER, ammo_distance)]
        #role_list.sort(cmp=self.compare_role_distance_tuple)
        #return role_list

    def compare_role_distance_tuple(self, r1, r2):
        #print "compare role distance tuple called"
        if r1[1] < r2[1]:
            return -1
        elif r1[1] > r2[1]:
            return 1
        return 0

    def clear_roles(self):
        self.roles = None

    def get_finest_cp(self, agent):
        """ determines the best cp to capture/hold"""
        if agent.role == self.ROLE_CP1 or agent.role == self.ROLE_CP2:
            return self.cps[agent.role -1]
        print "THIS SHOULD NOT HAPPEN IN shared.get_finest_cp(self, agent)"
        return self.cps[0]

    def get_finest_cp_role(self, agent):
        """ determines the best cp to capture/hold"""

        #return roles_covered[1:len(roles_covered)].index(0) + 1

        if (domination.utilities.point_dist(agent.observation.loc,
                self.cps[0]) < domination.utilities.point_dist(
                                agent.observation.loc, self.cps[1])):
            return self.ROLE_CP1
        return self.ROLE_CP2
        

    def get_finest_ammo(self, agent):
        """ Returns an (x, y) tuple that is the best location
            presumably containing ammo. 
            returns False when no ammo location can be found"""
        # TODO: incorperate ammo spotted time to guess the best ammo spot

        shortest_distance = 999999
        best_index = -1
        for i in range(len(self.ammo_locations)):
            dist = domination.utilities.point_dist(agent.observation.loc, 
                self.ammo_locations[i])
            if shortest_distance > dist:
                shortest_distance = dist
                best_index = i
   
        # this should never happen! 
        if best_index < 0:
            return False
       
        #return self.ammo_locations[0] 
        return self.ammo_locations[best_index]

    def get_finest_enemy(self, agent):
        """ calculates the position for the agent to go to and
            shoot some mofos
            returns False when no location has been found
            returns (x, y) tuple when a soab has to be murdered"""
        #if len(self.enemies) == 0:
        #    return False
        ## for now just return the latest spotted foe
        ## TODO: select the foe based on a combination of spotted time, 
        ##   distance and current enemy
        #return self.enemies[-1][0:2]

        enemies = self.enemies[-2:len(self.enemies)]
        enemies = [item for inner_list in enemies 
               for item in inner_list ]

    

        dis = 99999999
        best_enemy = None
        for enemy in enemies:
            dist = domination.utilities.point_dist(agent.observation.loc, 
                    (enemy[0], enemy[1]))
            if dist < dis:
                dis = dist
                best_enemy = enemy

        if best_enemy != None:
            return (best_enemy[0], best_enemy[1])
        return agent.observation.loc

    def update_ammo(self):
        pass

    def update_enemies(self, observation):
        # TODO: remove enemies that have been spotted too long ago to be
        #   relevant
        ##for i in range(len(self.enemies)):
        ##    enemy = self.enemies[i]
        ##    self.enemies[i] = [enemy[0], enemy[1], enemy[2], enemy[3] + 1]
        for i in range(len(self.enemies)):
            self.enemies.append(observation.foes)

    
    def re_init_mesh(self, agent):
        """ Adds more points to the mesh, such as ammo and control points """

        additional_points = [] 
        additional_points.extend(self.ammo_locations)
        additional_points.extend(self.cps)

        #print agent.grid
        walls = domination.utilities.rects_merge(agent.grid)
        #print "WALLLLLLLLLLLLLLLLLS %s" % str(walls)
        #print additional_points 
        #agent.mesh = domination.utilities.make_nav_mesh(domination.utilities.rects_merge(agent.grid))
            #add_points=additional_points)

