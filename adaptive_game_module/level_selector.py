import yaml

class LevelSelector:
    """Class handling selection of next level to play, in player's place.
    
    Needs a file with level requirements, and a file with possibly mastered tools.
    If a player knows a tool, and is under time limit, they are eligible for that level.
    
    Levels with None requirements are a "default" that anyone can take."""
    def __init__(self, tool_list_filename, level_requirements_filename):
        self.read_level_requirements(level_requirements_filename)
        self.read_tool_list(tool_list_filename)
        self.known_tools = []

    def read_level_requirements(self, filename):
        """Reads level requirements from file `filename`."""
        with open(filename) as f:
            self.level_requirements = yaml.load(f, Loader=yaml.FullLoader)

    def read_tool_list(self, filename):
        """Reads list of tools from file `filename`."""
        with open(filename) as f:
            self.tool_list = yaml.load(f, Loader=yaml.FullLoader)

    def add_known_tool(self, tool):
        """Add tool `tool` to list of known tools."""
        if tool in self.known_tools:
            return
        self.known_tools.append(tool)

    def next_level(self, current_level, current_time):
        """Select what the next level should be after `current_level`."""
        next_levels = self.level_requirements["level" + str(current_level+1)]
        if len(next_levels) == 1:
            return next_levels[0][0]
        candidate_level = None
        for level, requirements in next_levels:
            if requirements is None:
                candidate_level = level
            elif ((requirements[0] > current_time) and (requirements[1] in self.known_tools)):
                candidate_level = level
            else:
                pass
        return candidate_level

