class State:
    """
    Generic State class.

    Variables:
    - name: state name (string)
    - next: transition row (dict). For NTM:
        key   = read symbol
        value = list of (next_state, write_symbol, direction)

    Functions:
    - delta(symbol): returns list of transitions on that symbol.
    - setNext(mapping): sets transitions for this state.
    """

    def __init__(self, name):
        self.name = name
        self.next = {}  # symbol -> list of (next_state, write_symbol, dir)

    def delta(self, symbol):
        # [State] delta(symbol) − returns the next state(s) given the symbol. [file:1]
        return self.next.get(symbol, [])

    def setNext(self, mapping):
        # void setNext([symbol: [State]]) – generalized for TM transitions. [file:1]
        # mapping: {symbol: [(next_state, write_symbol, direction), ...]}
        for sym in mapping:
            self.next[sym] = mapping[sym]


class NTM:
    """
    Nondeterministic Turing Machine

    Same idea as DTM on VIII: we keep
    - sigma: list of alphabet / tape symbols
    - q: list of State objects
    - f: list of final state names

    plus:
    - start_state: name of the start state
    - current_states: list of configurations (state, tape, head) to model nondeterminism
    """

    def __init__(self, states, final_states, input_symbols, start_state_name, blank="_"):
        # q − list of State
        self.q = list(states)

        # f − list of final state names
        self.f = list(final_states)

        # sigma − alphabet symbols
        self.sigma = list(input_symbols)

        # start state name
        self.start_state = start_state_name

        # blank symbol on tape
        self.blank = blank

        # list of current configurations: (state, tape, head)
        self.current_configs = []

        # step counter (optional)
        self.steps = 0

    def _initialize_tape(self, w):
        # Around two blanks per end to simulate infinite tape. [file:1]
        tape = [self.blank, self.blank]
        for ch in w:
            tape.append(ch)
        tape.append(self.blank)
        tape.append(self.blank)
        head = 2  # first symbol of input
        return tape, head

    def reset(self, w):
        # Map names to State objects
        name_to_state = {}
        for s in self.q:
            name_to_state[s.name] = s

        tape, head = self._initialize_tape(w)
        start_state = name_to_state[self.start_state]

        # one initial configuration
        self.current_configs = [(start_state, tape, head)]
        self.steps = 0

    def step(self):
        # One nondeterministic step over all current configurations
        if len(self.current_configs) == 0:
            return False  # no configs -> dead

        new_configs = []

        for (state, tape, head) in self.current_configs:
            # if already in final state, we could stop earlier in run()
            symbol = tape[head]
            trans_list = state.delta(symbol)

            if len(trans_list) == 0:
                # this branch cannot continue
                continue

            # branch for each possible transition
            for (next_state, write_symbol, direction) in trans_list:
                # copy tape
                new_tape = []
                for c in tape:
                    new_tape.append(c)

                # write
                new_tape[head] = write_symbol

                # move head
                if direction == "R":
                    new_head = head + 1
                else:  # "L"
                    new_head = head - 1

                # expand tape if needed
                if new_head < 0:
                    new_tape = [self.blank] + new_tape
                    new_head = 0
                elif new_head >= len(new_tape):
                    new_tape.append(self.blank)

                new_configs.append((next_state, new_tape, new_head))

        self.current_configs = new_configs
        self.steps += 1
        return len(self.current_configs) > 0

    def accepts(self):
        # Any config in a final state?
        for (state, tape, head) in self.current_configs:
            if state.name in self.f:
                return True
        return False

    def run(self, w, max_steps=100):
        # set up tape and initial configuration
        self.reset(w)

        # simulate up to max_steps
        while self.steps < max_steps:
            if self.accepts():
                # find one accepting branch and show its tape
                for (state, tape, head) in self.current_configs:
                    if state.name in self.f:
                        tape_str = ""
                        for c in tape:
                            tape_str += c
                        # strip blanks at both ends
                        tape_str = tape_str.strip(self.blank)
                        return True, "Accept, Tape: " + tape_str

            if not self.step():
                # no more moves
                if len(self.current_configs) > 0:
                    # one rejecting branch to display
                    state, tape, head = self.current_configs[0]
                    tape_str = ""
                    for c in tape:
                        tape_str += c
                    tape_str = tape_str.strip(self.blank)
                    return False, "Reject, Tape: " + tape_str
                else:
                    return False, "Reject (no configurations)"

        # safety cutoff
        if len(self.current_configs) > 0:
            state, tape, head = self.current_configs[0]
            tape_str = ""
            for c in tape:
                tape_str += c
            tape_str = tape_str.strip(self.blank)
            return False, "Max steps, Tape: " + tape_str
        return False, "Max steps"


# -------------------- main / example setup (outside classes) --------------------
if __name__ == "__main__":
    blank = "_"

    # Example NTM similar to your transitions dict:
    # Here: {0,1}*1 (strings ending in 1). You can replace with your own. [web:24]
    q0 = State("q0")
    q1 = State("q1")
    qf = State("qf")

    # Build transitions in State.next instead of a separate dict.
    # q0: read 0 or 1, move right; nondeterministically guess "this 1 is last"
    q0.setNext({
        "0": [(q0, "0", "R")],
        "1": [(q0, "1", "R"), (q1, "1", "R")],
        blank: [(qf, blank, "L")]  # if we never guessed, but hit end, accept as a simple example
    })

    # q1: after guessed last 1, just move right over 0/1
    q1.setNext({
        "0": [(q1, "0", "R")],
        "1": [(q1, "1", "R")],
        blank: [(qf, blank, "L")]
    })

    qf.setNext({})  # final, no outgoing transitions

    states = [q0, q1, qf]
    finals = ["qf"]
    sigma = ["0", "1", blank]

    ntm = NTM(states, finals, sigma, start_state_name="q0", blank=blank)

    while True:
        s = input("Enter string to test (or 'quit'): ")
        if s == "quit":
            break
        accepted, msg = ntm.run(s, max_steps=100)
        print(f"Input: '{s}' -> {msg}")
