if "swarm_agent" in globals():
    # reset variables
    ships_data = {}
    movement_tactics_index = 0

    # Play as first position against random agent.
    trainer = env.train([None, "random"])

    observation = trainer.reset()

    while not env.done:
        my_action = swarm_agent(observation, env.configuration)
        print("Step: {0}, My Action: {1}".format(observation.step, my_action))
        observation, reward, done, info = trainer.step(my_action)
        # env.render(mode="ipython", width=100, height=90, header=False, controls=False)
    env.render()
