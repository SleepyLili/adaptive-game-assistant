
import subprocess
import os
import time

import yaml  # reads level configurations from a .yml file


class NoLevelFoundError(Exception):
    """Error raised by the Game class when a nonexistant level is selected."""

    def __init__(self, message):
        self.message = message


class Game:
    """Class representing the adaptive game, its progress, setup+solving times.

    An object of the class will remember the possible branching of the game,
    it will keep track of the level and branch the player is on,
    and it will save loading times and solving times of the player."""

    def __init__(self, mapping_file, game_directory,
                 level_number=0, level_branch=''):
        """Create an object of class Game.

        The game itself is NOT started at this point. To start it, call
        self.start_game() next.

        Parameters
        ----------
        mapping_file
            location of the .yml file with level mappings.
        game_directory
            directory with the game files (Vagrantfile, etc.)
        levelNumber
            number of level to start on
            (useful when continuing a running game)
        levelBranch
            branch of level being started on
            (useful when continuing a running game)"""
        self.game_directory = game_directory
        self.read_mapping(mapping_file)

        self.load_times = []
        self.solving_times = []
        self.level_log = []

        self.game_start_time = 0
        self.level_start_time = 0

        self.level = level_number
        self.branch = level_branch

        self.game_in_progress = False
        self.game_finished = False
        self.game_end_time = 0

    def start_game(self):
        """Start a new game, if there isn't one already in progress."""
        if (self.game_in_progress or self.game_finished):
            return False
        self.game_in_progress = True
        self.level = 1
        self.level_log.append("level1")  # add level 1 to log
        start_time = time.time()
        subprocess.run(["vagrant", "up"], cwd=self.game_directory,
                       env=dict(os.environ, ANSIBLE_ARGS='--tags \"setup\"'))
        end_time = time.time()
        load_time = int(end_time - start_time)
        self.load_times.append(load_time)
        self.level_start_time = time.time()
        self.game_start_time = time.time()
        return True

    def finish_game(self):
        """Mark game as not in progress and log end time, if on the last level.

        Return false if prerequisites were not met, true otherwise."""
        if (self.next_level_exists() or not self.game_in_progress):
            return False
        self.solving_times.append(int(time.time() - self.level_start_time))
        self.game_end_time = time.time()
        self.game_in_progress = False
        self.game_finished = True
        return True

    def next_level_exists(self):
        """Return true if next level exists."""

        next_level = "level" + str(self.level + 1)
        return next_level in self.level_mapping

    def next_level_is_forked(self):
        """Return true if next level is forked."""

        next_level = "level" + str(self.level + 1)
        if next_level in self.level_mapping:
            if len(self.level_mapping[next_level]) > 1:
                return True
        return False

    def next_level_branch_check(self, input_text):
        """Check if `input_text` is a branch of next level, return next level branch name.

        `input_text` can be a full level name, partial level name or just
        a branch letter. Ex. "level4a", "4a" and "a" are all fine."""
        next_level = "level" + str(self.level + 1)
        if "level" + str(self.level + 1) + input_text in self.level_mapping[next_level]:
            return input_text
        if "level" + input_text in self.level_mapping[next_level]:
            return input_text[1:]
        if input_text in self.level_mapping[next_level]:
            return input_text[6:]
        raise NoLevelFoundError("No branch called {} found.".format(input_text))

    def next_level(self, next_branch_input=""):
        """Advance the game to next level with branch `next_branch_input`.
        Because `next_branch_input` can be supplied by user, perform check
        if it is real first.

        Raise NoLevelFoundError if there is no such level present.
        next_branch_input == '' is understood as no branch selected, a level
        without possible branching."""
        next_branch = ""
        if not self.game_in_progress:
            raise NoLevelFoundError("Can't continue, (S)tart the game first!")
        if not self.next_level_exists():
            raise NoLevelFoundError("No next level found! Perhaps you already finished the game?")
        if self.next_level_is_forked():
            next_branch = self.next_level_branch_check(next_branch_input)
            # raises NoLevelFoundError
        elif next_branch_input != "":
            raise NoLevelFoundError("Next level has no branch, but branch was given.")
        self.solving_times.append(int(time.time() - self.level_start_time))
        self.level += 1
        self.branch = next_branch
        level_name = "level" + str(self.level) + self.branch
        self.level_log.append(level_name)
        boxes = self.level_mapping["level" + str(self.level)][level_name]
        start_time = time.time()
        subprocess.run(["vagrant", "up"] + boxes + ["--provision"], cwd=self.game_directory,
                       env=dict(os.environ, ANSIBLE_ARGS='--tags \"' + level_name + '\"'))
        end_time = time.time()
        load_time = int(end_time - start_time)
        self.load_times.append(load_time)
        self.level_start_time = time.time()

    def abort_game(self):
        """Abort game and reset attributes to their default state.

        If a /logs subfolder exists, also logs the current game log
        to a file before aborting."""
        try:
            if os.path.isdir("logs"):
                self.log_to_file("logs/aborted_game" + str(time.time()))
        except OSError as err:
            # print("Failed to save game log.")
            # print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
            pass
        subprocess.run(["vagrant", "destroy", "-f"], cwd=self.game_directory)
        self.load_times = []
        self.solving_times = []
        self.level_log = []
        self.game_start_time = 0
        self.level_start_time = 0
        self.game_in_progress = False
        self.game_finished = False
        self.level = 0
        self.branch = ''
    # # # METHODS THAT WORK WITH FILES # # #
    def read_mapping(self, filename): # raise OSError when file can't be opened
        """Read a mapping of levels for the adaptive game from a YAML file."""

        with open(filename) as f:
            self.level_mapping = yaml.load(f, Loader=yaml.FullLoader)

    def log_to_file(self, filename): # raise OSError when file can't be opened
        """Log the current game state and logs into a YAML file."""
        with open(filename, 'w') as f:
            yaml.dump(self, f)

    # # # METHODS THAT OUTPUT INTO STDOUT # # #
    def print_next_level_fork_names(self):
        """Print names of next level forks."""

        next_level = "level" + str(self.level + 1)
        print("Next level branches are:")
        if next_level in self.level_mapping:
            for branch in self.level_mapping[next_level]:
                print(branch, end="  ")
        print("")

    def print_time(self, load_time, concise=False):
        """Print time in minutes and seconds.

        If concise is True, prints only numbers and letters."""

        if load_time < 60:
            if concise:
                print("{}s".format(load_time))
            else:
                print("Time elapsed: {} seconds.".format(load_time))
        else:
            minutes = load_time // 60
            seconds = load_time % 60
            if concise:
                print("{}m{}s".format(minutes, seconds))
            else:
                print("Time elapsed: {} minutes, {} seconds.".format(minutes, seconds))

    def print_info(self):
        """Print info about the game in a human-readable way."""

        if not self.game_in_progress and not self.game_finished:
            print("Game is not yet started.")
        else:
            if self.game_in_progress:  # in progress implies not finished
                if self.branch:
                    print("Game in progress. Level:{} Branch:{}".format(self.level, self.branch))
                else:
                    print("Game in progress. Level:{}".format(self.level))
                print("Total time elapsed: ", end="")
                self.print_time(int(time.time() - self.game_start_time), True)
            else:
                print("Game succesfully finished.")
                print("Total time played: ", end="")
                self.print_time(int(self.game_end_time - self.game_start_time), True)

            if self.level_log:
                print("Levels traversed:")
                for level in self.level_log:
                    print("{} ".format(level), end="")
                print("")
            print("Loading times:")
            for i in range(len(self.load_times)):
                if i == 0:
                    print("Setup + ", end="")
                print("{}: ".format(self.level_log[i]), end="")
                self.print_time(self.load_times[i], True)
            if self.solving_times:
                print("Solving times:")
                for i in range(len(self.solving_times)):
                    print("{}: ".format(self.level_log[i]), end="")
                    self.print_time(self.solving_times[i], True)
