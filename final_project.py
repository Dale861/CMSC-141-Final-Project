class State:
    def __init__(self, name):
        self.name = name
        self.next = {}

    def delta(self, symbol):
        return self.next.get(symbol, [])

    def setNext(self, mapping):
        for sym in mapping:
            self.next[sym] = mapping[sym]


class NTM:
    def __init__(self, states, final_states, input_symbols, start_state_name, blank="B"):
        self.q = list(states)
        self.f = list(final_states)
        self.sigma = list(input_symbols)
        self.start_state = start_state_name
        self.blank = blank
        self.current_configs = []
        self.steps = 0

    def _initialize_tape(self, w):
        tape = [self.blank, self.blank]
        for ch in w:
            tape.append(ch)
        tape.append(self.blank)
        tape.append(self.blank)
        head = 2
        return tape, head

    def reset(self, w):
        name_to_state = {}
        for s in self.q:
            name_to_state[s.name] = s
        tape, head = self._initialize_tape(w)
        start_state = name_to_state[self.start_state]
        self.current_configs = [(start_state, tape, head)]
        self.steps = 0
        return True

    def step(self):
        if len(self.current_configs) == 0:
            return False
        new_configs = []
        for (state, tape, head) in self.current_configs:
            symbol = tape[head]
            trans_list = state.delta(symbol)
            if len(trans_list) == 0:
                continue
            for (next_state, write_symbol, direction) in trans_list:
                new_tape = [c for c in tape]
                new_tape[head] = write_symbol
                new_head = head + (1 if direction == "R" else -1)
                if new_head < 0:
                    new_tape = [self.blank] + new_tape
                    new_head = 0
                elif new_head >= len(new_tape):
                    new_tape.append(self.blank)
                new_configs.append((next_state, new_tape, new_head))
        self.current_configs = new_configs
        self.steps += 1
        return len(new_configs) > 0

    def accepts(self):
        for (state, tape, head) in self.current_configs:
            if state.name in self.f:
                return True
        return False

    def run(self, w, max_steps=20):
        self.reset(w)
        return self._debug_run(max_steps)

    def _debug_run(self, max_steps):
        print(f"\n{'='*80}")
        print(f"NTM EXECUTION TRACE: Input = '{''.join(self.current_configs[0][1])[2:-4]}'")
        print(f"{'='*80}")

        state0, tape0, head0 = self.current_configs[0]
        self._print_config(0, state0, tape0, head0)

        while self.steps < max_steps:
            if self.accepts():
                print(f"\nACCEPTED at step {self.steps}")
                return True

            print(f"\n{'-'*80}")
            print(f"STEP {self.steps}: Processing {len(self.current_configs)} configuration(s)")

            for i, (state, tape, head) in enumerate(self.current_configs):
                symbol = tape[head]
                moves = state.delta(symbol)
                print(f"  Branch {i+1}: {state.name} (head={head}) reads '{symbol}' -> {len(moves)} transition(s)")
                for j, (nstate, write, d) in enumerate(moves):
                    print(f"    Transition {j+1}: {nstate.name}, write='{write}', direction={d}")

            if not self.step():
                print(f"\nREJECTED at step {self.steps}: All branches terminated")
                return False

            for i, (state, tape, head) in enumerate(self.current_configs):
                self._print_config(self.steps, state, tape, head, f"Branch {i+1}")

        print(f"\nEXECUTION TERMINATED: Maximum steps {max_steps} reached")
        return False

    def _print_config(self, step, state, tape, head, label=""):
        if label:
            print(f"\n  {label}:")
        print(f"    {state.name} at step {step}")
        display = ""
        start = max(0, head - 5)
        end = min(len(tape), head + 6)
        for i in range(start, end):
            if i == head:
                display += f"[{tape[i]}]"
            else:
                display += f" {tape[i]} "
        print(f"    Tape: ...{display}...")
        print(f"    Head position: {head}")


if __name__ == "__main__":
    blank = "B"

    q0 = State("q0")   # start
    q1 = State("q1")
    q2 = State("q2")
    qf = State("qf")   # final

    q0.setNext({
        "0": [(q1, "0", "R")],
        "1": [(q2, "1", "R")],
        "B": []
    })

    q1.setNext({
        "0": [(q1, "0", "R")],
        "1": [(q2, "1", "R"), (q1, "1", "R")], # or then and
        ":": [(q1, ":", "R")],
        "=": [(q1, "=", "R")],
        "B": [(qf, "0", "R")]
    })
    q2.setNext({
        "0": [(q2, "0", "R"),(q1, "0","R")], # or then and
        "1": [(q2, "1", "R")],
        ":": [(q2, ":", "R")],
        "=": [(q2, "=", "R")],
        "B": [(qf, "1", "R")],
    })

    qf.setNext({})

    states = [q0, q1, q2, qf]
    final_states = ["qf"]          
    input_symbols = ["0", "1", "B", ":", "="]

    ntm = NTM(states, final_states, input_symbols, "q0", blank="B")  

    while True:
        user_input = input("\nEnter binary string (or 'quit'): ").strip()

        if user_input.lower() in ["quit", "q", "exit"]:
            print("Execution terminated.")
            break

        if not all(set(user_input)):
            print("Invalid input")
            continue

        result = ntm.run(user_input, max_steps=50)
