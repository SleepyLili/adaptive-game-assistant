import yaml  # reads hint configurations from a .yml file

class LevelSelector:
    def __init__(self, tool_list_filename):
        self.read_level_requirements(filename)
        self.read_tool_list(filename)
        self.known_tools = []

    def read_level_requirements(self, filename):  
        with open(filename) as f:
            self.level_requirements = yaml.load(f, Loader=yaml.FullLoader)

    def read_tool_list(self, filename):
        with open(filename) as f:
            self.tool_list = yaml.load(f, Loader=yaml.FullLoader)

    def add_known_tool(self, tool):
        if tool in self.known_tools:
            return
        self.known_tools.append(tool)

    def next_level(self, current_level, current_time):
        next_levels = self.level_requirements[level]
        if len(next_levels) == 1:
            return next_levels[0][0]
        candidate_level = None
        for {level, requirements} in next_levels:
            if requirements is None:
                candidate_level = level
            elif ((requirements[0] < current_time) and (requirements[1] in self.known_tools)):
                candidate_level = level
            else:
                pass
        return candidate_level

