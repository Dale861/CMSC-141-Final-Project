class State:
    def __init__(self, name, input_str=""):
        self.name = name
        self.tape = ['_'] * 500 + list(input_str) + ['_'] * 500
        self.head = 500
        self.is_final = False

class NTM:
    def __init__(self, transitions, start_state, final_states):
        self.transitions = transitions
        self.start_state = start_state
        self.final_states = final_states
        self.current_states = []
        self.steps = 0
    
    def reset(self, input_str):
        self.current_states = [State(self.start_state, input_str)]
        self.steps = 0
    
    def step(self):
        if not self.current_states:
            return False
        next_states = []
        for state in self.current_states:
            sym = state.tape[state.head]
            key = (state.name, sym)
            if key not in self.transitions:
                continue
            for next_name, write, direction in self.transitions[key]:
                new_state = State(next_name)
                new_state.tape = state.tape.copy()
                new_state.head = state.head
                new_state.tape[new_state.head] = write
                if direction == 'R': new_state.head += 1
                elif direction == 'L': new_state.head -= 1
                next_states.append(new_state)
        self.current_states = next_states
        self.steps += 1
        return True
    
    def accepts(self):
        return any(s.name in self.final_states for s in self.current_states)
    
    def run(self, max_steps=100):
        while self.steps < max_steps:
            if self.accepts():
                # Print tape of accepting branch
                for s in self.current_states:
                    if s.name in self.final_states:
                        tape_str = ''.join(s.tape).strip('_')
                        return True, f"Accept, Output: {tape_str}"
                return True, "Accept"
            if not self.step():
                # No more moves → reject, but still show tape
                if self.current_states:
                    # Show tape of one rejecting branch
                    s = self.current_states[0]
                    tape_str = ''.join(s.tape).strip('_')
                    return False, f"Reject, Tape: {tape_str}"
                else:
                    return False, "Reject (no states left)"
        # Safety cutoff
        if self.current_states:
            s = self.current_states[0]
            tape_str = ''.join(s.tape).strip('_')
            return False, f"Max steps, Tape: {tape_str}"
        return False, "Max steps"

    
    def test_ntm(self):
        while True:
            input_str = input("Enter string to test: ")
            self.reset(input_str)
            accepts, result = self.run()
            print(f"Input: '{input_str}' -> {result}")

# Example: {a,b}*b (strings ending with b)
trans = {
    # q0: flip bits (1's complement) while scanning right
    ('q0','0'): [('q0','1','R')],
    ('q0','1'): [('q0','0','R'), ('q1','1','R')],  # nondeterministic guess: keep flipping OR switch to retain

    # q1: after the guessed rightmost 1, retain all bits
    ('q1','0'): [('q1','0','R')],
    ('q1','1'): [('q1','1','R')],

    # halt at blank (end of input)
    ('q0','_'): [('qf','_','L')],
    ('q1','_'): [('qf','_','L')],
}


ntm = NTM(trans, 'q0', {'qf'})
ntm.test_ntm()
