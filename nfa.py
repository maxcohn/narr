""" README

Why?

I like esoteric languages

I needed to learn NFA simulation

"""

"""
TODO

Add comments ---- #?

build out examples/tests

add support for epsilon transitions
    Maybe done?


Comment so it is clear on the nfa simulations process

Have a clear version and a raw version
    Compare speeds

Make some example nfas

Make a program that generates the input for this interpreter from a regular expression


In clean version
    NFA object
    Transition object
    Good error reporting


"""


"""
0=a>1
0=b>2
1=a>2
2=b>1

"""
import re

EPSILON = 'ε'

# input string
s = "aba"

#TODO add checking of duplicate transitions
#TODO but this might not cause a problem because of the use of sets and their unique value propterty


# list of list of transitions (trans_char, next_state) where the index in the list represents the start state for each list of transitions
states = [[]]

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
split = re.compile('(\d+)=(\w)?>(\d+)')


with open("a.a") as f:
    cur_index = 0
    for line in f:
        if line.strip()[0] == "$":
            # accepting states list
            final_states = set([int(x) for x in line[1:].split(',')])

            # exit loop as we are done adding final states
            break
        start, trans_char, next = parts(split.match(line.strip()))
        
        if start == cur_index:
            states[cur_index].append(trans(trans_char, next))
        elif start == cur_index +1:
            cur_index += 1
            states.append([trans(trans_char, next)])
        else:
            print("indexing skip error")
            quit()
        
        #print(f"state {start} transitions with {trans} to {next}")

def has_trans(i: int, c: str):
    # where i is the state idnex and c is the transition character
    
    transitions = []
    
    # go through all transition tuples associated with the current state
    for t, n in states[i]:

        # if the current transition uses the given given character, add it to the transitions list 
        if c == t:
            transitions.append(n)
        
        # if the current transition is an epsilon transition, add it no matter what
        #elif t == EPSILON:
        #    transitions.append(n)
    
    return transitions

def all_epsilon(s):
    # where s is a set of the states to each for epsilon transitions in
    #TODO doesn't affect performance,but should change to a set
    epsilon_trans = []

    # check every transition that exits for an epsilon transiton
    for i in s:
        for t,n in states[i]:
            if t == EPSILON:
                epsilon_trans.append(n)
    
    return epsilon_trans


#states.append(trans("a",1))

active_states = set()
active_states.add(0)

#print(active_states)

#print(has_trans(0, "b"))

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
            new_states.add(p)###CHANGE

    # set the active states to be the new_states now
    active_states = new_states


# print wheter the given string matches
print( "In langauge" if len(active_states.intersection(final_states)) != 0 else "Not in language")

print(states)
print(active_states)