import yaml

class FlagChecker:
    def __init__(self, filename):
        self.wrong_flags = {}
        self.read_keys(filename)

    def read_keys(self, filename):
        with open(filename) as f:
            self.flags = yaml.load(f, Loader=yaml.FullLoader)

    def check_flag(self, level, flag):
        if self.flags[level] == flag:
            return True
        else:
            if not level in self.wrong_flags:
                self.wrong_flags[level] = []
            self.wrong_flags[level].append(flag)
            return False

    def log_to_file(self, filename):
        with open(filename, 'a') as f:
            yaml.dump(self.wrong_flags, f)