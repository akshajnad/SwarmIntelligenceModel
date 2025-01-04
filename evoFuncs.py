import random
import copy

def get_average_halite(results):
    """ get average halite of agent from results of evaluated episodes """
    halite_sum = 0
    for r in results:
        halite_sum += r[0]
    return halite_sum / len(results)

def set_possible_records_and_patterns_amounts():
    """ set maximum possible amounts of memory records and patterns in those records """
    global possible_records_amount
    global possible_patterns_amount
    possible_records_amount = len(ea_actions) * len(ea_funs_and_results)
    possible_patterns_amount = len(ea_funs_and_results)
    for fun in ea_funs_and_results:
        possible_records_amount *= len(fun["results"])
        possible_patterns_amount *= len(fun["results"])
    possible_records_amount -= 1
    possible_patterns_amount -= 1

def mutations():
    """ mutate each specimen of the population """
    for specimen in population:
        # remove some records from specimen
        records_to_remove = random.randint(0, len(specimen) - 1)
        for i in range(records_to_remove):
            specimen.pop(random.randint(0, len(specimen) - 1))
        # clone some records within specimen
        records_to_clone = random.randint(0, len(specimen))
        for i in range(records_to_clone):
            specimen.append(copy.deepcopy(specimen[random.randint(0, len(specimen) - 1)]))
        # mutate some actions in existing records
        actions_to_mutate = random.randint(0, len(specimen))
        for i in range(actions_to_mutate):
            record_index = random.randint(0, len(specimen) - 1)
            new_action_index = random.randint(0, len(ea_actions) - 1)
            specimen[record_index]["action_key"] = ea_actions[new_action_index]["key"]
            specimen[record_index]["action"] = ea_actions[new_action_index]["action"]
        # mutate some lists of patterns in existing records
        patterns_lists_to_mutate = random.randint(0, len(specimen) - 1)
        for i in range(patterns_lists_to_mutate):
            # remove some patterns from a record's list of patterns
            patterns_to_remove = random.randint(0, len(specimen[i]["patterns"]) - 1)
            for j in range(patterns_to_remove):
                specimen[i]["patterns"].pop(random.randint(0, len(specimen[i]["patterns"]) - 1))
            # clone some patterns within record
            patterns_to_clone = random.randint(0, len(specimen[i]["patterns"]))
            for j in range(patterns_to_clone):
                specimen[i]["patterns"].append(
                    copy.deepcopy(specimen[i]["patterns"][random.randint(0, len(specimen[i]["patterns"]) - 1)]))
            # mutate some patterns in a record's list of patterns
            patterns_to_mutate = random.randint(0, len(specimen[i]["patterns"]))
            for j in range(patterns_to_mutate):
                # p_i -> pattern index
                p_i = random.randint(0, len(specimen[i]["patterns"]) - 1)
                # n_p_i -> new pattern index
                n_p_i = random.randint(0, len(ea_funs_and_results) - 1)
                specimen[i]["patterns"][p_i]["key"] = ea_funs_and_results[n_p_i]["key"]
                specimen[i]["patterns"][p_i]["fun"] = ea_funs_and_results[n_p_i]["fun"]
                results_index = random.randint(0, len(ea_funs_and_results[n_p_i]["results"]) - 1)
                specimen[i]["patterns"][p_i]["result"] = ea_funs_and_results[n_p_i]["results"][results_index]

def fitness(memory_key):
    """ evaluate each specimen's fitness """
    global best_specimen
    global best_specimen_fitness
    for specimen in population:
        # replace memory of unit with specimen
        memory[memory_key] = specimen
        specimen_fitness = get_average_halite(evaluate("halite", [swarm_agent],
                                num_episodes=episodes, configuration={"agentExec": "LOCAL"}
                           ))
        if specimen_fitness > best_specimen_fitness:
            best_specimen_fitness = specimen_fitness
            best_specimen = copy.deepcopy(specimen)

def selection():
    """ select specimens for next generation """
    global population
    population = []
    for i in range(population_size):
        population.append(copy.deepcopy(best_specimen))
