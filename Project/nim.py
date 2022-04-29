# %%
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

# %%
def Initialize():
    global policy
    global value
    global Q
    policy = copy.deepcopy(Policy_Template) #replaced .copy with a deepcopy
    value = copy.deepcopy(Value_Template)
    Q = copy.deepcopy(Q_Template)

    return


def New_Game():
    global state
    state = copy.deepcopy(newGame)

    return


# %%
"""
A function for setting the policy for a given state
    r1: Number of sticks in row 1
    r2: Number of sticks in row 2
    r3: Number of sticks in row 3
    r4: Number of sticks in row 4
    count: Total number of sticks left
"""
def setPolicy(r1, r2, r3, r4, count):
    policy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(r1):
        policy[0 + i] = 1.0/count
    for i in range(r2):
        policy[1 + i] = 1.0/count
    for i in range(r3):
        policy[4 + i] = 1.0/count
    for i in range(r4):
        policy[9 + i] = 1.0/count
    return policy

"""
Generates a new policy for NIM
"""
def newPolicy():
    for r1 in range(2):
        for r2 in range(4):
            for r3 in range(6):
                for r4 in range(8):
                    print((r1, r2, r3, r4), end='')
                    print(" : ", end='')
                    print(setPolicy(r1, r2, r3, r4, r1 + r2 + r3 + r4), end='')
                    print(",")

# %%
"""
Observes the current state space, and makes a random legal action
"""
def genRandomAction(state):
    while True: # it randomly chooses actions until it finds one that is legal
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
    #for x in Policy_Template[state]:
    for x in policy[state]:
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
    if new_state[row - 1] < nSticks: # simple error check
        print("Attempting to remove more sticks than possible, this shouldn't be possible!")
        quit()
    else:
        new_state[row - 1] -= nSticks # removes specified stick #

    # print(new_state)
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
Plays the game by taking random legal moves

Depreciated :(
"""
def genEpisodeRandomly():
    New_Game()
    print(state)
    while (tuple(state) != win):
        genRandomAction()
        print("action taken")
        print(state)

# %%
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

"""
Helper function that takes in an action tuple and returns what it's index in the Actions dict would be
"""
def actionIndex(tuple):
    for i in range(16):
        if Actions[i] == tuple:
            return i


"""
For each state, for the the action taken, the corresponding Q value has the reward for that state/action combo added
"""

def MC_Q_Evaluate():
    global Q
    (States, Actions_chosen, Reward, Return) = Gen_Episode()
    for state in States:
        if state != (0, 0, 0, 0):  # added condition since Q value does not consider end state
            Q[state][actionIndex(Actions_chosen[States.index( # Actions_chosen[States.index(state)] was giving tuple when int was needed. Added helper function "actionIndex" to create desired functionality
                state)])] += Return[States.index(state)] # replace Reward[States.index(state)] with Return[States.index(state)]
        #Q[r][c][Actions.index(a)] += Return[States.index((r, c))] <- original midterm code!

"""
Examines the Q table for each state and action pair. The action with the highest score for a given state will set the policy.
"""
def MC_find_policy(maxiter):
    for w in range(maxiter):
        MC_Q_Evaluate()


    for index in Q:
        # initializes policy to first legal action. Needed for situations where only possible move results in loss
        optimal = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(16):
            if Q[index][i] != 0:
                max = Q[index][i]
                maxIndex = i
                break


        for i in range(16):
            if Q[index][i] > max and Q[index][i] != 0:
                max = Q[index][i]
                maxIndex = i
        optimal[maxIndex] = 1
        policy[index] = optimal     

def policyPlay(maxiter):
    wins = 0
    losses = 0
    for i in range(maxiter):
        s, a, rew, ret = Gen_Episode()
        if ret[0] < 0:
            losses += 1
        else:
            wins += 1
    print("with {} matches, the RL AI has {} wins and {} losses".format(maxiter, wins, losses))
    print("Win rate: {}%".format(wins/maxiter * 100))



# %%
def main():
    Initialize()

    #example run below
    s, a, rew, ret = Gen_Episode()
    for i in range(len(s)):
        print(f"Time: {i}")
        print(f"State: {s[i]}")
        print(f"Action: {a[i]}")
        print(f"Reward: {rew[i]}")
        print(f"Return: {ret[i]}\n")
        
    # garrett testing (he should delete this part before uploading to git)
    #MC_Q_Evaluate()
    policyPlay(1000)

    MC_find_policy(1000000)
    
    #print out Q table and Policy for each state
    if False:
        for x in policy:
            print(x)
            print(Q[x])
            print(policy[x])

    #actual run after policy found
    print("training completed")
    policyPlay(1000)

if __name__ == "__main__":
    main()


# %%
import sys

"""
Takes in user input in form "row sticks" and does it. Has some basic error checking
"""
def playerMove(state):
    while True:
        print("Enter your move in form 'row sticks' or 'quit'\n>>> ", end='')
        sys.stdout.flush()

        inp = input()
        sys.stdout.flush() # strategically placed flush

        #print(inp)
        if inp == "quit":
            quit()

        action = list(map(int, inp.split()))
        print()

        row = action[0] # there is totally a better way to do this, but it is 11:45pm
        nSticks = action[1]



        if row > 5 or row <= 0:
            print("Ensure the row number is either 1, 2, 3 or 4")

        elif state[row - 1] < nSticks: # simple error check
            print("Attempting to remove more sticks than possible!")

        else:
            state[row - 1] -= nSticks
            break
"""
Sort of like Env but only returns the new state. Takes in action tuple and state tuple
"""
def playableEnv(a, state): # ugly hack but whatever it's 12:08am
    row, nSticks = a
    new_state = list(state)
    if new_state[row - 1] < nSticks: # simple error check
        print("Attempting to remove more sticks than possible, this shouldn't be possible!")
        quit()
    else:
        new_state[row - 1] -= nSticks # removes specified stick #

    return tuple(new_state)



def playNim():
    state = copy.deepcopy(newGame)
    print("New state:")
    print(state)
    while True:
        #AI doing its thing
        state = list(playableEnv(genAction(tuple(state)), tuple(state)))
        print("State after AI move:")
        print(state)
        if state == [0, 0, 0, 0]:
            print("AI wins!")
            break

        #player playing (12:50am fuck you bed time)
        playerMove(state)
        print("State after your move:")
        print(state)
        if state == [0, 0, 0, 0]:
            print("user wins!")
            break

def playNimForever():
    while True:
        playNim()
        sys.stdout.flush() # strategically placed flush





playNimForever()


