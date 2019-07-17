import re
import sys

# constant representing epsilon for epsilon transitions
EPSILON = 'ε'

"""
Steps involved in this interpreter:

Create array of states
    (states are identified by their numbers which are also their index in array)
    
    This is an adjacency list representation of the NFA

Read the file
    Parse each line for the start state, the transition character, and the next state
    
    Add the new transiton to the adjacency list for the respective state

    We also need to account for accepting states, which we do by checking for lines that
    start with '$'
    
Simulate NFA
    We create a new, empty set of active states, we'll add to this to keep track
    of the states we're active in after processing each character in the input

    Before looping through each active state, we need to account for the epsilon
    transitions, which occur before each character is read
        To do this, we make a set of each possible state we can be in due to
        epsilon transitions and then union it with the active states. This gives
        us the full set of states we need to try and apply our transition character to

        Then we loop through each active state and check if there are any transitions we
        can make with our current input character. We collect all of these into a list and
        then add them all to our new_states set.

        After all the new active states are found, we set active_states to new_states and
        continue our next interation of our loop on our next input character

Checking for existence in language
    For a string to be accepted, at least one of the active states must be in the accepting
    states list when we finish

    If we do have an active state that is also an accepting state, the string exists in the
    language that our NFA accepts.



Other notes:
    Sets are very helpful here because we can't have multiple instances in the same
    state, so sets take care of the unique existence of each state in the active_states set
"""

# get string from user
file_name = sys.argv[1]
user_input = sys.argv[2]

# list of list of transitions (trans_char, next_state) where the index in the
# list represents the start state for each list of transitions
states = [[] for i in range(100)]

# set of accepting states
final_states = set()

# returns a tuple representing the transition that is (c -> next)
def trans(c: str, next: int):
    # where c is the character needed to transition to next, the index of the next state

    return (c, next)

# takes a match of a transition string and returns the important pieces
def parts(m: re.Match):
    return int(m.group(1)), m.group(2) if m.group(2) is not None else EPSILON, int(m.group(3))

# regex for splitting the transition string
split = re.compile(r'(\d+)=(\w)?>(\d+)')

with open(file_name) as f:
    for line in f:
        if line.strip()[0] == "$":
            # accepting states list
            final_states = set([int(x) for x in line[1:].split(',')])

            # exit loop as we are done adding final states
            break
        elif line.strip()[0] == "#":
            # line is a comment, so ignore it
            continue

        start, trans_char, next = parts(split.match(line.strip()))
        states[start].append(trans(trans_char, next))

def has_trans(i: int, c: str):
    # where i is the state idnex and c is the transition character
    transitions = []
    
    # go through all transition tuples associated with the current state
    for t, n in states[i]:
        # if the current transition uses the given given character, add it to the transitions list 
        if c == t:
            transitions.append(n)
    
    return transitions

def all_epsilon(s: set):
    # where s is a set of the states to each for epsilon transitions in
    epsilon_trans = set()

    # check every transition that exits for an epsilon transiton
    for i in s:
        for t,n in states[i]:
            if t == EPSILON:
                epsilon_trans.add(n)
    
    return epsilon_trans

# create the active_states set and add the starting state
active_states = set()
active_states.add(0)

# loop through all input characters
for c in user_input:
    # create a new set to represent the possible states we can transition to from the current active states
    new_states = set()

    # before checking for character based transitions, check for epsilon transitions and apply them
    # we do this because all possible epsilon transitions occur before the next character is processed

    # we union the two sets because we have the 
    active_states = active_states.union(all_epsilon(active_states))

    for a in active_states:
        
        # get list of all possible transition from state a with the input c
        potential_states = has_trans(a, c)

        # add them all to the new states list
        for p in potential_states:
            new_states.add(p)

    # set the active states to be the new_states now
    active_states = new_states


# print wheter the given string matches
print(len(active_states.intersection(final_states)) != 0)
