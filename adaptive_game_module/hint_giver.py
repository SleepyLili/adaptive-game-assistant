import yaml  # reads hint configurations from a .yml file

class HintGiver:
    """Class holding all the possible hints for all levels, and giving them
    out when asked for.
    
    Also keeps track of previously given hints, and total given hints in a game."""

    def __init__(self, hint_filename):
        """Create a hint giver from file `filename`."""
        self.total_hints_taken = 0
        self.hints_taken = {} # dict, level : [hint_name, hint_name]
        
        self.read_hint_file(hint_filename)

    def read_hint_file(self, hint_filename): # raises OSError on file problems
        """Read dict of hints from the adaptive game from a YAML file."""

        with open(hint_filename) as f:
            self.hints = yaml.load(f, Loader=yaml.FullLoader)
    
    def show_possible_hints(self, level, branch):
        """Return all possible hints for given `level` and `branch`."""
        return list(self.hints[level][level+branch])

    def take_hint(self, level, branch, hint_name):
        """Show hint text for a specific hint. Add it to hint log and counter."""
        if not level+branch in self.hints_taken:
            self.hints_taken[level+branch] = []
        if hint_name not in self.hints_taken[level+branch]:
            self.total_hints_taken += 1
            self.hints_taken[level+branch].append(hint_name)
        return self.hints[level][level+branch][hint_name]

    def show_taken_hints(self, level, branch):
        """Show all previously taken hints for `level` and `branch`."""
        if not level+branch in self.hints_taken:
            return []
        return self.hints_taken[level+branch]

    def is_hint_name(self, level, branch, hint_name):
        """Check if `hint_name` is a name of a hint for `level` and `branch`."""
        if hint_name in self.hints[level][level+branch]:
            return True
        return False

    def restart_game(self):
        """Reset hint counter and hint log to zero."""
        self.total_hints_taken = 0
        self.hints_taken = {}
    
    def log_to_file(self, filename):
        """Write taken hints to a file."""
        with open(filename, 'a') as f:
            yaml.dump(self, f)