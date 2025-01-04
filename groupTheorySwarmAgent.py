def swarm_agent(observation, configuration):
    """ RELEASE THE SWARM!!! """
    s_env = {}
    actions = {}
    adapt_environment(observation, configuration, s_env)

    # Example center of rotation/reflection
    center_x, center_y = 10, 10

    # Apply Dihedral-based translations, rotations, and reflections
    s_env["swarm_ships_coords"] = apply_translation(s_env["swarm_ships_coords"], [1, 1])  # Example translation
    s_env["swarm_ships_coords"] = apply_rotation(s_env["swarm_ships_coords"], [center_x, center_y], k=1, n=6)
    s_env["swarm_ships_coords"] = apply_reflection(s_env["swarm_ships_coords"], [center_x, center_y], k=1, n=6)

    # Apply Cyclic-based movements
    s_env["swarm_ships_coords"] = apply_cyclic_movement(s_env["swarm_ships_coords"], alpha=1, n=6)

    actions_of_ships(actions, s_env)
    actions_of_shipyards(actions, s_env)
    return actions
