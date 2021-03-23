import yaml  # reads hint configurations from a .yml file

class HintGiver:
    def __init__(self, hint_filename):
        self.total_hints_taken = 0
        self.hints_taken = {} # dict, level : [hint_name, hint_name]
        
        self.read_hint_file(hint_filename)

    def read_hint_file(self, hint_filename): # raises OSError on file problems
        """Read dict of hints from the adaptive game from a YAML file."""

        with open(hint_filename) as f:
            self.hints = yaml.load(f, Loader=yaml.FullLoader)
    
    def show_possible_hints(self, level, branch):
        return list(self.hints[level][level+branch])

    def take_hint(self, level, branch, hint_name):
        if not level+branch in self.hints_taken:
            self.hints_taken[level+branch] = []
        if hint_name not in self.hints_taken[level+branch]:
            self.total_hints_taken += 1
            self.hints_taken[level+branch].append(hint_name)
        return self.hints[level][level+branch][hint_name]

    def show_taken_hints(self, level, branch):
        return self.hints_taken[level+branch]

    def is_hint_name(self, level, branch, hint_name):
        if hint_name in self.hints[level][level+branch]:
            return True
        return False