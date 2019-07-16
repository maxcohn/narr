""" README

Why?

I like esoteric languages

I needed to learn NFA simulation

"""

"""
TODO

Comment so it is clear on the nfa simulations process

Have a clear version and a raw version
    Compare speeds

Make a program that generates the input for this interpreter from a regular expression


In clean version
    NFA object
    Transition object
    Good error reporting


"""
import re

EPSILON = 'ε'

# input string
s = "aaaabb"

#TODO add checking of duplicate transitions
#TODO but this might not cause a problem because of the use of sets and their unique value propterty


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

with open("examples/even-as-2-bs.nfa") as f:
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

active_states = set()
active_states.add(0)

# loop through all input characters
for c in s:
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
print( "In langauge" if len(active_states.intersection(final_states)) != 0 else "Not in language")
