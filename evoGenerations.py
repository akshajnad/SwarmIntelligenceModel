# amount of generations
generations_amount = 10
# size of the population
population_size = 5
# list of specimens
population = []
# maximum possible amount of memory records
possible_records_amount = 0
# maximum possible amount of patterns in a record
possible_patterns_amount = 0
# number of episodes for fitness evaluation
episodes = 1
# list of possible actions
ea_actions = sp_actions
# list of functions and lists of possible results
ea_funs_and_results = sp_funs_and_results
# best specimen
best_specimen = copy.deepcopy(memory["ships"])
# best specimen fitness
best_specimen_fitness = get_average_halite(evaluate("halite", [swarm_agent],
                            num_episodes=episodes, configuration={"agentExec": "LOCAL"}
                        ))

# create initial population
selection()

# evolve memory of ships with evolutionary algorithm
for i in range(generations_amount):
    mutations()
    fitness("ships")
    selection()

# replace memory of ships with best specimen
memory["ships"] = copy.deepcopy(best_specimen)
print("Best specimen fitness: {0}, best specimen: {1}".format(best_specimen_fitness, best_specimen))
