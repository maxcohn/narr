use std::fs::File;
use std::io::{BufReader, BufRead};
use std::collections::HashSet;
use regex::Regex;
#[macro_use]
extern crate lazy_static;

const EPSILON: char = 1 as char;

lazy_static! {
    static ref TRANS_RE: Regex = Regex::new(r"(\d+)=(\w)?>(\d+)").unwrap();
}



/// A transition between states
#[derive(Debug)]
struct Transition {
    /// The character that triggers the transition
    trans_char: char,

    /// The index in the adjacency list of the state to transition to
    next_state: usize
}

impl Transition {

    /// Creates a new Transition
    ///
    /// # Arguments
    ///
    /// * `trans_char` - The character that triggers the transition
    /// * `next_state` - Index in the adjacency list of the state to transition to
    fn new(trans_char: char, next_state: usize) -> Transition {
        Transition{
            trans_char,
            next_state
        }
    }
}

struct NFA {
    /// Adjacency list representation of the NFA
    states: Vec::<Vec::<Transition>>,

    /// List of states that are accepting in the NFA
    accepting_states: HashSet::<usize>
}

impl NFA {

    /// Simulates the NFA based on the given input, returning whether it would
    /// be accepted by the NFA
    ///
    /// # Arguments
    /// * `input` - String to check if NFA accepts
    fn simulate(&self, input: &str) -> bool {
        // set of currently active states in the NFA, with starting state included
        let mut active_states = HashSet::new();
        active_states.insert(0);

        // loop over all input characters
        for c in input.chars() {
            // set of states that we're active in after this current set of moves
            let mut new_states = HashSet::new();

            // loop through each active state and state that could be active
            // due to epsilon transitions
            for cur_state in active_states.union(&self.all_epsilon(&active_states)) {
                // get a list of all the potential states we could go to with the
                // current input char from the current state
                let potential_states = self.get_trans_for_char(cur_state.clone(), c);

                for s in potential_states {
                    new_states.insert(s);
                }
            }

            // the active states for the next round
            active_states = new_states;
        }

        // get intersection of active_states and accepting states after simulation
        let state_intersect = active_states.intersection(&self.accepting_states)
            .collect::<Vec<&usize>>();

        // if there are any states in the intersec, that means the string is matched
        return state_intersect.len() != 0;

    }

    /// Returns a vector of states that can be transitioned to from the given
    /// state with the given character
    ///
    /// # Arguments
    /// * `state` - Starting state of transitions
    /// * `c` - Character that triggers transition
    fn get_trans_for_char(&self, state: usize, c: char) -> Vec<usize>{
        let mut possible_trans = Vec::new();

        for trans in self.states[state].iter() {
            if trans.trans_char == c {
                possible_trans.push(trans.next_state);
            }
        }

        return possible_trans;
        
    }

    /// Returns a set of all epsilon transitions from the currently active states
    ///
    /// # Arguments
    /// * `active_states` - Reference to a HashSet of the currently active states
    fn all_epsilon(&self, active_states: &HashSet<usize>) -> HashSet<usize> {
        let mut trans = HashSet::new();

        // loop through all active states and check if they have any epsilon transitions
        for s in active_states.iter().cloned() {
            for i in self.get_trans_for_char(s, EPSILON) {
                trans.insert(i);
            }
        }
        return trans;
    }

    /// Adds a transition to the NFA
    ///
    /// # Arguments
    ///
    /// * `s` - Start state of the transition (index of state in the adjacency list)
    /// * `t` - Transition type to be added
    fn add_transition(&mut self, s: usize, t: Transition) {
        self.states[s].push(t);
    }

    /// Constructs a new NFA from a given file
    ///
    /// # Arguments
    ///
    /// * `file_name` - Name of the file to read in NFA description from
    ///
    /// # Panics
    ///
    /// Any problems with reading the given file will result in a panic
    fn new(file_name: &str) -> NFA {
        let mut nfa = NFA {
            states: Vec::new(),
            accepting_states: HashSet::new()
        };

        let file = File::open(file_name).unwrap();
        
        // go through each line in the file
        for line in BufReader::new(file).lines() {
            let line = line.unwrap();

            // check for empty line, and if so, ignore
            if line.trim() == "" {
                continue
            }

            // check for accepting states or comments
            let first_char = line.trim().chars().next();
            if first_char == Some('$') {
                // this line lists the accepting states
                nfa.accepting_states = line.trim()
                    .split(|c| c == ',' || c == '$' || c == ' ')
                    .filter(|s| s != &"")
                    .map(|s| s.parse::<usize>().expect("Accepting state list ill formatted"))
                    .collect();

                // check if any of the given states don't exist as indicies in the vector
                for s in nfa.accepting_states.iter().cloned() {
                    while s >= nfa.states.len() {
                        nfa.states.push(Vec::new());
                    }
                }

                // break out of reading loop because we are done
                break;
            } else if first_char == Some('#') {
                // this line is a comment, so we ignore it
                continue;
            }

            // capture each part of the transition
            let caps = TRANS_RE.captures(line.trim())
                .unwrap_or_else(|| panic!("The given transiton is ill formatted {}", line));

            let start_state = caps[1].parse::<usize>()
                .expect("Failed to parse start state to int.");;
            // check if we have an epsilon transition
            let trans_char = caps.get(2)
                .map_or(EPSILON, |c| c.as_str().chars().nth(0).unwrap());
            //let trans_char = 'a';
            let next_state = caps[3].parse::<usize>()
                .expect("Failed to parse next state to int.");;

            // if we are adding a transition for a state that doesn't exist in
            // the vector, add new states (vectors) to our main vector until we
            // can add the new transition
            while nfa.states.len() <= start_state {
                nfa.states.push(Vec::new());
            }

            // add transition to it's respective state in the NFA
            nfa.add_transition(start_state, Transition::new(trans_char, next_state));
        }

        return nfa
    }
}

fn main() {

    let args: Vec<String> = std::env::args().collect();


    let nfa = NFA::new(&args[1]);

    let input = &args[2];

    let res = nfa.simulate(input);

    println!("{}", res);

}
