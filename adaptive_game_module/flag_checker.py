import yaml

class FlagChecker:
    """Class that checks if flags are correct, and also remembers wrong flags.

    Needs a file with the flags to levels written in."""
    def __init__(self, filename):
        self.wrong_flags = {}
        self.read_keys(filename)

    def read_keys(self, filename):
        """Reads levels and flags from file `filename`"""
        with open(filename) as f:
            self.flags = yaml.load(f, Loader=yaml.FullLoader)

    def check_flag(self, level, flag):
        """Checks if `flag` is a correct flag for `level`.

        If it isn't, it adds `flag` to the list of incorrect flags."""
        if self.flags[level] == flag:
            return True
        else:
            if not level in self.wrong_flags:
                self.wrong_flags[level] = []
            self.wrong_flags[level].append(flag)
            return False

    def log_to_file(self, filename):
        """Logs everything to a file."""
        with open(filename, 'a') as f:
            yaml.dump(self.wrong_flags, f)