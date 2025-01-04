#%%writefile submission.py
# for Debug and Evolutionary Algorithm previous line (%%writefile submission.py) should be commented out,
# uncomment to write submission.py

#FUNCTIONS###################################################
def get_map_and_average_halite(obs):
    """
        get average amount of halite per halite source
        and map as two dimensional array of objects and set amounts of halite in each cell
    """
    game_map = []
    halite_sources_amount = 0
    halite_total_amount = 0
    for x in range(conf.size):
        game_map.append([])
        for y in range(conf.size):
            game_map[x].append({
                # value will be ID of owner
                "shipyard": None,
                # value will be ID of owner
                "ship": None,
                # value will be amount of halite
                "ship_cargo": None,
                # amount of halite
                "halite": obs.halite[conf.size * y + x]
            })
            if game_map[x][y]["halite"] > 0:
                halite_total_amount += game_map[x][y]["halite"]
                halite_sources_amount += 1
    average_halite = halite_total_amount / halite_sources_amount
    return game_map, average_halite

def get_swarm_units_coords_and_update_map(s_env):
    """ get lists of coords of Swarm's units and update locations of ships and shipyards on the map """
    # arrays of (x, y) coords
    swarm_shipyards_coords = []
    swarm_ships_coords = []
    # place on the map locations of units of every player
    for player in range(len(s_env["obs"].players)):
        # place on the map locations of every shipyard of the player
        shipyards = list(s_env["obs"].players[player][1].values())
        for shipyard in shipyards:
            x = shipyard % conf.size
            y = shipyard // conf.size
            # place shipyard on the map
            s_env["map"][x][y]["shipyard"] = player
            if player == s_env["obs"].player:
                swarm_shipyards_coords.append((x, y))
        # place on the map locations of every ship of the player
        ships = list(s_env["obs"].players[player][2].values())
        for ship in ships:
            x = ship[0] % conf.size
            y = ship[0] // conf.size
            # place ship on the map
            s_env["map"][x][y]["ship"] = player
            s_env["map"][x][y]["ship_cargo"] = ship[1]
            if player == s_env["obs"].player:
                swarm_ships_coords.append((x, y))
    return swarm_shipyards_coords, swarm_ships_coords

def get_c(c):
    """ get coordinate, considering donut type of the map """
    return c % conf.size

def clear(x, y, player, game_map):
    """ check if cell is safe to move in """
    # if there is no shipyard, or there is player's shipyard
    # and there is no ship
    if ((game_map[x][y]["shipyard"] == player or game_map[x][y]["shipyard"] == None) and
            game_map[x][y]["ship"] == None):
        return True
    return False

def move_ship(actions, s_env, ship):
    """ move ship in the direction """
    # if ship has to move out from current position
    if ships_data[ship["key"]]["direction_to_move"] != "HERE":
        actions[ship["key"]] = ships_data[ship["key"]]["direction_to_move"]
        for d in directions_list:
            if d["direction"] == ships_data[ship["key"]]["direction_to_move"]:
                x = d["x"](ship["x"])
                y = d["y"](ship["y"])
        ships_data[ship["key"]]["direction_to_move"] = "HERE"
        # apply changes to game_map, to avoid collisions of player's ships next turn
        s_env["map"][ship["x"]][ship["y"]]["ship"] = None
        s_env["map"][x][y]["ship"] = s_env["obs"].player
    return actions, s_env

def go_for_halite(s_env, ship):
    """ ship will go to safe cell with enough halite, if it is found """
    # if current cell has enough halite
    if (s_env["map"][ship["x"]][ship["y"]]["halite"] > s_env["low_amount_of_halite"] and
            not hostile_ship_near(ship["x"], ship["y"], s_env["obs"].player, s_env["map"], ship["cargo"])):
        most_halite = s_env["map"][ship["x"]][ship["y"]]["halite"]
    else:
        # biggest amount of halite among scanned cells
        most_halite = s_env["low_amount_of_halite"]
    direction = None
    for d in range(len(directions_list)):
        x = directions_list[d]["x"](ship["x"])
        y = directions_list[d]["y"](ship["y"])
        # if cell is safe to move in
        if (clear(x, y, s_env["obs"].player, s_env["map"]) and
                not hostile_ship_near(x, y, s_env["obs"].player, s_env["map"], ship["cargo"])):
            # if current cell has more than biggest amount of halite
            if s_env["map"][x][y]["halite"] > most_halite:
                most_halite = s_env["map"][x][y]["halite"]
                direction = directions_list[d]["direction"]
                direction_x = x
                direction_y = y
    # if cell is safe to move in and has substantial amount of halite
    if most_halite > s_env["low_amount_of_halite"] and direction != None:
        ships_data[ship["key"]]["direction_to_move"] = direction
        return True
    # if current cell has biggest amount of halite
    elif most_halite == s_env["map"][ship["x"]][ship["y"]]["halite"]:
        ships_data[ship["key"]]["direction_to_move"] = "HERE"
        return True
    return ""

def standard_patrol(s_env, ship):
    """
        ship will move in expanding circles clockwise or counterclockwise
        until reaching maximum radius, then radius will be minimal again
    """
    directions = ships_data[ship["key"]]["directions"]
    # set index of direction
    i = ships_data[ship["key"]]["directions_index"]
    direction_found = False
    for j in range(len(directions)):
        x = directions[i]["x"](ship["x"])
        y = directions[i]["y"](ship["y"])
        # if cell is ok to move in
        if (clear(x, y, s_env["obs"].player, s_env["map"]) and
                (s_env["map"][x][y]["shipyard"] == s_env["obs"].player or
                not hostile_ship_near(x, y, s_env["obs"].player, s_env["map"], ship["cargo"]))):
            ships_data[ship["key"]]["moves_done"] += 1
            # if it was last move in this direction
            if ships_data[ship["key"]]["moves_done"] >= ships_data[ship["key"]]["ship_max_moves"]:
                ships_data[ship["key"]]["moves_done"] = 0
                ships_data[ship["key"]]["directions_index"] += 1
                # if it is last direction in a list
                if ships_data[ship["key"]]["directions_index"] >= len(directions):
                    ships_data[ship["key"]]["directions_index"] = 0
                    ships_data[ship["key"]]["ship_max_moves"] += 1
                    # if ship_max_moves reached maximum radius expansion
                    if ships_data[ship["key"]]["ship_max_moves"] > max_moves_amount:
                        ships_data[ship["key"]]["ship_max_moves"] = 1
            ships_data[ship["key"]]["direction_to_move"] = directions[i]["direction"]
            direction_found = True
            break
        else:
            # loop through directions
            i += 1
            if i >= len(directions):
                i = 0
    # if ship is not on shipyard and hostile ship is near
    if (not direction_found and s_env["map"][ship["x"]][ship["y"]]["shipyard"] == None and
            hostile_ship_near(ship["x"], ship["y"], s_env["obs"].player, s_env["map"], ship["cargo"])):
        # if there is enough halite to convert
        if ship["cargo"] >= conf.convertCost:
            return "conv"
        else:
            for i in range(len(directions)):
                x = directions[i]["x"](ship["x"])
                y = directions[i]["y"](ship["y"])
                # if it is opponent's shipyard
                if s_env["map"][x][y]["shipyard"] != None:
                    ships_data[ship["key"]]["direction_to_move"] = directions[i]["direction"]
                    return True
            for i in range(len(directions)):
                x = directions[i]["x"](ship["x"])
                y = directions[i]["y"](ship["y"])
                # if it is empty place
                if s_env["map"][x][y]["ship"] == None:
                    ships_data[ship["key"]]["direction_to_move"] = directions[i]["direction"]
                    return True
    return True

def get_directions(i0, i1, i2, i3):
    """ get list of directions in a certain sequence """
    return [directions_list[i0], directions_list[i1], directions_list[i2], directions_list[i3]]

def hostile_ship_near(x, y, player, m, cargo):
    """ check if hostile ship is in one move away from game_map[x][y] and has less or equal halite """
    # m = game map
    n = get_c(y - 1)
    e = get_c(x + 1)
    s = get_c(y + 1)
    w = get_c(x - 1)
    if (
            (m[x][n]["ship"] != player and m[x][n]["ship"] != None and m[x][n]["ship_cargo"] <= cargo) or
            (m[x][s]["ship"] != player and m[x][s]["ship"] != None and m[x][s]["ship_cargo"] <= cargo) or
            (m[e][y]["ship"] != player and m[e][y]["ship"] != None and m[e][y]["ship_cargo"] <= cargo) or
            (m[w][y]["ship"] != player and m[w][y]["ship"] != None and m[w][y]["ship_cargo"] <= cargo)
        ):
        return True
    return False

def spawn_ship(actions, s_env, shipyard):
    """ spawn ship """
    s_env["swarm_halite"] -= conf.spawnCost
    actions[shipyard["key"]] = "SPAWN"
    s_env["map"][shipyard["x"]][shipyard["y"]]["ship"] = s_env["obs"].player
    s_env["ships_amount"] += 1
    return actions, s_env

def sd_swarm_halite_amount(s_env, shipyard):
    """ evaluate amount of Swarm's halite """
    if s_env["swarm_halite"] >= conf.spawnCost:
        return ">=snc"
    return ""

def sd_ships_amount(s_env, shipyard):
    """ evaluate amount of ships in the Swarm """
    if s_env["ships_amount"] < s_env["ships_max_amount"]:
        return "<spma"
    return ""

def shipyard_clear(s_env, shipyard):
    """ check if this shipyard is clear """
    if clear(shipyard["x"], shipyard["y"], s_env["obs"].player, s_env["map"]):
        return True
    return ""

def record_found(s_env, unit, patterns):
    """ check if every pattern's result matches data returned from that pattern's function """
    for pattern in patterns:
        if pattern["fun"](s_env, unit) != pattern["result"]:
            return False
    return True

def this_is_new_ship(s_env, i):
    """ add this ship to ships_data """
    global movement_tactics_index
    ships_data[s_env["ships_keys"][i]] = {
        "moves_done": 0,
        "ship_max_moves": 1,
        "directions": movement_tactics[movement_tactics_index]["directions"],
        "directions_index": 0,
        "direction_to_move": "HERE"
    }
    movement_tactics_index += 1
    if movement_tactics_index >= movement_tactics_amount:
        movement_tactics_index = 0
    return s_env

def this_is_last_step(s_env, ship):
    """ check if it is last step """
    if s_env["obs"].step == (conf.episodeSteps - 2) and ship["cargo"] >= conf.convertCost:
        return True
    return ""

def convert_ship(actions, s_env, ship):
    """ convert ship into shipyard """
    actions[ship["key"]] = "CONVERT"
    s_env["map"][ship["x"]][ship["y"]]["ship"] = None
    s_env["shipyards_amount"] += 1
    s_env["swarm_halite"] = s_env["swarm_halite"] + ship["cargo"] - conf.convertCost
    return actions, s_env

def no_shipyards(s_env, ship):
    """ check if there is no shipyard and conversion of ship is possible """
    shipyards_amount = len(s_env["shipyards_keys"])
    if (s_env["shipyards_amount"] == 0 and
            not hostile_ship_near(ship["x"], ship["y"], s_env["obs"].player, s_env["map"], ship["cargo"]) and
            (s_env["swarm_halite"] + ship["cargo"]) >= convert_threshold):
        return True
    return ""

def to_spawn_or_not_to_spawn(s_env):
    """ to spawn, or not to spawn, that is the question """
    # get ships_max_amount to decide whether to spawn new ships or not
    ships_max_amount = 9
    # if ships_max_amount is less than minimal allowed amount of ships in the Swarm
    if ships_max_amount < ships_min_amount or s_env["obs"].step >= spawn_stop_step:
        ships_max_amount = ships_min_amount
    return ships_max_amount

def define_some_globals(configuration):
    """ define some of the global variables """
    global conf
    global convert_threshold
    global max_moves_amount
    global spawn_stop_step
    global globals_not_defined
    conf = configuration
    convert_threshold = conf.convertCost + conf.spawnCost * 2
    max_moves_amount = 3
    spawn_stop_step = conf.episodeSteps - 150
    globals_not_defined = False

def adapt_environment(observation, configuration):
    """ adapt environment for the Swarm """
    s_env = {}
    s_env["obs"] = observation
    if globals_not_defined:
        define_some_globals(configuration)
    s_env["map"], s_env["average_halite"] = get_map_and_average_halite(s_env["obs"])
    s_env["low_amount_of_halite"] = s_env["average_halite"] * 0.75
    s_env["swarm_halite"] = s_env["obs"].players[s_env["obs"].player][0]
    s_env["swarm_shipyards_coords"], s_env["swarm_ships_coords"] = get_swarm_units_coords_and_update_map(s_env)
    s_env["ships_keys"] = list(s_env["obs"].players[s_env["obs"].player][2].keys())
    s_env["ships_values"] = list(s_env["obs"].players[s_env["obs"].player][2].values())
    s_env["shipyards_keys"] = list(s_env["obs"].players[s_env["obs"].player][1].keys())
    s_env["ships_max_amount"] = to_spawn_or_not_to_spawn(s_env)
    s_env["ships_amount"] = len(s_env["ships_keys"])
    s_env["shipyards_amount"] = len(s_env["shipyards_keys"])
    return s_env

def actions_of_ships(s_env):
    """ actions of every ship of the Swarm """
    actions = {}
    for i in range(len(s_env["ships_keys"])):
        # if this is a new ship
        if s_env["ships_keys"][i] not in ships_data:
            s_env = this_is_new_ship(s_env, i)
        ship = {
            "x": s_env["swarm_ships_coords"][i][0],
            "y": s_env["swarm_ships_coords"][i][1],
            "key": s_env["ships_keys"][i],
            "cargo": s_env["ships_values"][i][1]
        }
        # find first suitable record in memory
        for record in memory["ships"]:
            if record_found(s_env, ship, record["patterns"]):
                # perform action of suitable record
                actions, s_env = record["action"](actions, s_env, ship)
                break
    return actions

def actions_of_shipyards(actions, s_env):
    """ actions of every shipyard of the Swarm """
    # spawn ships from every shipyard, if possible
    for i in range(len(s_env["shipyards_keys"])):
        shipyard = {
            "x": s_env["swarm_shipyards_coords"][i][0],
            "y": s_env["swarm_shipyards_coords"][i][1],
            "key": s_env["shipyards_keys"][i]
        }
        # find first suitable record in memory
        for record in memory["shipyards"]:
            if record_found(s_env, shipyard, record["patterns"]):
                # perform action of suitable record
                actions, s_env = record["action"](actions, s_env, shipyard)
                break
    return actions


#GLOBAL_VARIABLES#############################################
conf = None
# max amount of moves in one direction before turning
max_moves_amount = None
# threshold of harvested by a ship halite to convert
convert_threshold = None
# no ship spawning above ships_min_amount after this step
spawn_stop_step = None
# object with ship ids and their data
ships_data = {}
# initial movement_tactics index
movement_tactics_index = 0
# minimum amount of ships that should be in the Swarm at any time
ships_min_amount = 3
# not all global variables are defined
globals_not_defined = True

# list of directions
directions_list = [
    {
        "direction": "NORTH",
        "x": lambda z: z,
        "y": lambda z: get_c(z - 1)
    },
    {
        "direction": "EAST",
        "x": lambda z: get_c(z + 1),
        "y": lambda z: z
    },
    {
        "direction": "SOUTH",
        "x": lambda z: z,
        "y": lambda z: get_c(z + 1)
    },
    {
        "direction": "WEST",
        "x": lambda z: get_c(z - 1),
        "y": lambda z: z
    }
]

# list of movement tactics
movement_tactics = [
    # N -> E -> S -> W
    {"directions": get_directions(0, 1, 2, 3)},
    # S -> E -> N -> W
    {"directions": get_directions(2, 1, 0, 3)},
    # N -> W -> S -> E
    {"directions": get_directions(0, 3, 2, 1)},
    # S -> W -> N -> E
    {"directions": get_directions(2, 3, 0, 1)},
    # E -> N -> W -> S
    {"directions": get_directions(1, 0, 3, 2)},
    # W -> S -> E -> N
    {"directions": get_directions(3, 2, 1, 0)},
    # E -> S -> W -> N
    {"directions": get_directions(1, 2, 3, 0)},
    # W -> N -> E -> S
    {"directions": get_directions(3, 0, 1, 2)},
]
movement_tactics_amount = len(movement_tactics)

# list of ships functions and lists of possible results
sp_funs_and_results = [
    {
        "key": "this_is_last_step",
        "fun": this_is_last_step,
        "results": [
            True
        ]
    },
    {
        "key": "no_shipyards",
        "fun": no_shipyards,
        "results": [
            True
        ]
    },
    {
        "key": "go_for_halite",
        "fun": go_for_halite,
        "results": [
            True
        ]
    },
    {
        "key": "standard_patrol",
        "fun": standard_patrol,
        "results": [
            True,
            # conv -> CONVERT
            "conv"
        ]
    }
]

# list of possible actions of ships
sp_actions = [
    {
        "key": "convert_ship",
        "action": convert_ship
    },
    {
        "key": "move_ship",
        "action": move_ship
    }
]

# list of shipyards functions and lists of possible results
sd_funs_and_results = [
    {
        "key": "sd_swarm_halite_amount",
        "fun": sd_swarm_halite_amount,
        "results": [
            # snc -> spawn cost
            ">=snc"
        ]
    },
    {
        "key": "sd_ships_amount",
        "fun": sd_ships_amount,
        "results": [
            # spma -> ships max amount
            "<spma"
        ]
    },
    {
        "key": "shipyard_clear",
        "fun": shipyard_clear,
        "results": [
            True
        ]
    }
]

# list of possible actions of shipyards
sd_actions = [
    {
        "key": "spawn_ship",
        "action": spawn_ship
    }
]

# memory of units
memory = {
    # ships list of memory records
    "ships": [
        {
            "patterns": [
                {
                    "key": sp_funs_and_results[0]["key"],
                    "fun": sp_funs_and_results[0]["fun"],
                    "result": sp_funs_and_results[0]["results"][0]
                }
            ],
            "action_key": sp_actions[0]["key"],
            "action": sp_actions[0]["action"]
        },
        {
            "patterns": [
                {
                    "key": sp_funs_and_results[1]["key"],
                    "fun": sp_funs_and_results[1]["fun"],
                    "result": sp_funs_and_results[1]["results"][0]
                }
            ],
            "action_key": sp_actions[0]["key"],
            "action": sp_actions[0]["action"]
        },
        {
            "patterns": [
                {
                    "key": sp_funs_and_results[3]["key"],
                    "fun": sp_funs_and_results[3]["fun"],
                    "result": sp_funs_and_results[3]["results"][1]
                }
            ],
            "action_key": sp_actions[0]["key"],
            "action": sp_actions[0]["action"]
        },
        {
            "patterns": [
                {
                    "key": sp_funs_and_results[2]["key"],
                    "fun": sp_funs_and_results[2]["fun"],
                    "result": sp_funs_and_results[2]["results"][0]
                }
            ],
            "action_key": sp_actions[1]["key"],
            "action": sp_actions[1]["action"]
        },
        {
            "patterns": [
                {
                    "key": sp_funs_and_results[3]["key"],
                    "fun": sp_funs_and_results[3]["fun"],
                    "result": sp_funs_and_results[3]["results"][0]
                }
            ],
            "action_key": sp_actions[1]["key"],
            "action": sp_actions[1]["action"]
        }
    ],
    # shipyards list of memory records
    "shipyards": [
        {
            "patterns": [
                {
                    "key": sd_funs_and_results[0]["key"],
                    "fun": sd_funs_and_results[0]["fun"],
                    "result": sd_funs_and_results[0]["results"][0]
                },
                {
                    "key": sd_funs_and_results[1]["key"],
                    "fun": sd_funs_and_results[1]["fun"],
                    "result": sd_funs_and_results[1]["results"][0]
                },
                {
                    "key": sd_funs_and_results[2]["key"],
                    "fun": sd_funs_and_results[2]["fun"],
                    "result": sd_funs_and_results[2]["results"][0]
                }
            ],
            "action_key": sd_actions[0]["key"],
            "action": sd_actions[0]["action"]
        }
    ]
}


#THE_SWARM####################################################
def swarm_agent(observation, configuration):
    """ RELEASE THE SWARM!!! """
    s_env = adapt_environment(observation, configuration)
    actions = actions_of_ships(s_env)
    actions = actions_of_shipyards(actions, s_env)
    return actions
