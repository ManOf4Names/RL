from policy import *
import numpy as np
import random
import copy

newGame = [1, 3, 5, 7]

win = (0, 0, 0, 0)

Gamma = 0.9

# Reward values for win and loss conditions
win_reward = 100
lose_reward = -50

# episode length
gameRunning = True


def Initialize():
    global policy
    global value
    global Q
    policy = copy.deepcopy(Policy_Template)  # replaced .copy with a deepcopy
    value = copy.deepcopy(Value_Template)
    Q = copy.deepcopy(Q_Template)

    return


def New_Game():
    global state
    state = copy.deepcopy(newGame)

    return

"""
Observes the current state space, and makes a random legal action
"""
def genRandomAction(state):
    while True:  # it randomly chooses actions until it finds one that is legal
        action = random.randint(0, 15)
        if Policy_Template[tuple(state)][action] != 0:
            break
    #print(Policy_Template[tuple(state)]) # here in case we need more debugging
    return Actions[action]


"""
Determines which action to take based upon the PDF in Actions
"""
def genAction(state):
    actionChance = random.uniform(0, 1)
    action = 0
    sum = 0
    for x in Policy_Template[state]:
        sum += x
        if sum > actionChance:
            break
        else:
            action += 1
    return Actions[action]


"""
Takes in a row (1, 2, 3 or 4) and removes the specified number of sticks.
If it needs to remove more sticks than what the row contains, it terminates the program
"""
def Env(a, state):
    row, nSticks = a
    new_state = list(state)
    if new_state[row - 1] < nSticks:  # simple error check
        print("Attempting to remove more sticks than possible, this shouldn't be possible!")
        quit()
    else:
        new_state[row - 1] -= nSticks  # removes specified stick #

    if (tuple(new_state) == win):
        gameRunning == False
        return (tuple(new_state), win_reward)

    row, nSticks = genRandomAction(new_state)
    if new_state[row - 1] < nSticks:  # simple error check
        print("Attempting to remove more sticks than possible, this shouldn't be possible!")
        quit()
    else:
        new_state[row - 1] -= nSticks  # removes specified stick #

    if (tuple(new_state) == win):
        gameRunning == False
        return (tuple(new_state), lose_reward)
    else:
        return (tuple(new_state), 0)

"""
play the game for on episode:
    return States, Actions_choses, Reward, Returns

do for maxrun many times
    generate action according to policy
    add to Actions chosen
    Play the action - i.e., call the env to get next state and reward
    add new state and reward to the lists
compute Returns - comulative discounted return 
    traverse returns backward, multiply by gamma and add the next (lower index) number
"""
def Gen_Episode():
    States = []
    Actions_chosen = []
    Reward = []
    Return = []
    
    # Set initial values for state and action
    States.append((1, 3, 5, 7))
    Actions_chosen.append(genAction((1, 3, 5, 7)))
    Reward.append(0)
    Return.append(0)

    # Do for maxrun steps
    t = 0
    while(gameRunning):
        # Generate a reward and new state
        next_state, rew = Env(Actions_chosen[t], States[t])
        Reward.append(rew)
        
        # Assign current state to States[t]
        States.append(next_state)
        Return.append(0)
        # Choose an action based on the current state
        if (next_state != win):
            Actions_chosen.append(genAction(next_state))
        else:
            Actions_chosen.append((0, 0))
            break
        # Increment the time variable
        t += 1


    # After intial loop, set initial return for last step
    Return[-1] = Reward[-1]
    # Then iterate backwards and assign rewards for each stage.
    for r in range(t, -1, -1):
        Return[r] = Reward[r] + Gamma * Return[r + 1]
    return (States, Actions_chosen, Reward, Return)


def main():
    Initialize()
    s, a, rew, ret = Gen_Episode()
    for i in range(len(s)):
        print(f"Time: {i}")
        print(f"State: {s[i]}")
        print(f"Action: {a[i]}")
        print(f"Reward: {rew[i]}")
        print(f"Return: {ret[i]}\n")


if __name__ == "__main__":
    main()
