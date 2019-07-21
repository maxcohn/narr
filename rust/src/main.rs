use std::fs::File;
use std::io::{BufReader, BufRead, Result};
use std::collections::HashSet;
use regex::Regex;
#[macro_use]
extern crate lazy_static;

const EPSILON: char = 1 as char;



/// A transition between states
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

    #[allow(dead_code)]
    fn simulate(&self, s: &str) -> bool {
        true
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

        lazy_static! {
            static ref match_re: Regex = Regex::new(r"(\d+)=(\w)?>(\d+)").unwrap();
        }

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

                // break out of reading loop because we are done
                break;

            } else if first_char == Some('#') {
                // this line is a comment, so we ignore it
                continue;
            }

            // capture each part of the transition
            let caps = match_re.captures(line.trim())
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

    for v in nfa.states {
        for x in v {
            println!("{} -> {}", x.trans_char, x.next_state);
        }
    }
}
