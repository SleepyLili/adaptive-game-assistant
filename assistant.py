#!/usr/bin/env python3

import subprocess
import os
import time

import yaml  # reads level configurations from a .yml file


class NoLevelFoundError(Exception):
    """Error thrown by the Game class when a nonexistant level is selected."""

    def __init__(self, message):
        self.message = message


class Game:
    """Class representing the adaptive game, its progress, setup+solving times.

    An object of the class will remember the possible branching of the game,
    it will keep track of the level and branch the player is on,
    and it will save loading times and solving times of the player."""

    def __init__(self, mapping_file, game_directory, 
                 level_number=0, levelBranch=''):
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
        self.branch = ''

    def read_mapping(self, file):
        """Read a mapping of levels for the adaptive game from a .yml file."""

        with open(file) as f:
            self.level_mapping = yaml.load(f, Loader=yaml.FullLoader)

    def start_game(self):
        """Start a new game, if there isn't one already in progress."""
        if (self.level != 0):
            return False
        self.level = 1
        self.level_log.append("level1") #add level 1
        start_time = time.time()
        subprocess.run(["vagrant", "up"], cwd=self.game_directory,
                       env=dict(os.environ, ANSIBLE_ARGS='--tags \"setup\"'))
        end_time = time.time()
        load_time = int(end_time - start_time)
        self.load_times.append(load_time)
        self.level_start_time = time.time()
        self.game_start_time = time.time()
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
        
        Throws NoLevelFoundError if there is no such level present.
        next_branch_input == '' is understood as no branch selected, a level
        without possible branching."""
        next_branch = ""
        if (self.level == 0):
            raise NoLevelFoundError("Can't continue, (S)tart the game first!")
        if (not self.next_level_exists()):
            raise NoLevelFoundError("No next level found! Perhaps you already finished the game?")
        if (self.next_level_is_forked()):
            next_branch = self.next_level_branch_check(next_branch_input)
            # throws NoLevelFoundError
        elif (next_branch_input != ""):
            raise NoLevelFoundError("Next level has no branch, but branch was given.")
        self.solving_times.append(int(time.time() - self.level_start_time))
        self.level += 1
        self.branch = next_branch
        self.levelname = "level" + str(self.level) + self.branch
        self.level_log.append(self.levelname)
        self.boxes = self.level_mapping["level" + str(self.level)][self.levelname]
        start_time = time.time()
        subprocess.run(["vagrant", "up"] + self.boxes + ["--provision"], 
                       cwd=self.game_directory,
                       env=dict(os.environ, ANSIBLE_ARGS='--tags \"' + self.levelname + '\"'))
        end_time = time.time()
        load_time = int(end_time - start_time)
        self.load_times.append(load_time)
        self.level_start_time = time.time()

    def abort_game(self):
        """Abort game and reset attributes to their default state."""

        subprocess.run(["vagrant", "destroy", "-f"], cwd=self.game_directory)
        self.load_times = []
        self.solving_times = []
        self.level_log = []
        self.game_start_time = 0
        self.level_start_time = 0
        self.level = level_number
        self.branch = ''

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

        if (load_time < 60):
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

        if (self.level == 0):
            print("Game is not in progress.")
        else:
            print("Game in progress. Level:{} Branch:{}".format(self.level, self.branch))
            print("Total time elapsed: ", end="")
            self.print_time(int(time.time() - self.game_start_time), True)
            if self.level_log:
                print("Levels traversed so far:")
                for level in self.level_log:
                    print("{} ".format(level), end="")
                print("")
            print("Setup times:")
            for i in range(len(self.load_times)):
                if (i == 0):
                    print("Setup + ", end="")
                print("{}: ".format(self.level_log[i]), end="")
                self.print_time(self.load_times[i], True)
            if self.solving_times:
                print("Solving times:")
                for i in range(len(self.solving_times)):
                    print("{}: ".format(self.level_log[i]), end="")
                    self.print_time(self.solving_times[i], True)


def print_help():
    """Print list of arguments that game_loop accepts."""

    print("Functions that control the game:")
    print("(A)bort - destroys all VMs, resets progress to level 0.")
    print("(E)xit  - aborts run, then exits the assistant.")
    print("(S)tart - starts a new run of the adaptive game, if one isn't in progress.")
    print("(N)ext  - advances to the next level. Asks for branch when applicable.")
    print("(I)nfo  - displays info about current run - Level number and name.")
    print("Helper functions:")
    print("(H)elp  - explains all commands on the screen.")
    print("(C)heck - checks if prerequisites to run the game are installed.")


def check_prerequisites():
    """Check for the right version of required tools and print the result.

    VirtualBox check fails on windows even when VirtualBox is present."""

    print("checking Python version:")
    found = True
    try:
        version = subprocess.run(["python", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        found = False
        print("NOK, Python not found.")
    if found:
        version_number = version.stdout.split(" ", 1)[1].split(".")
        if (version_number[0] == "3"):
            if (int(version_number[1]) > 7):
                print("OK, Python version higher than 3.7.")
            else:
                print("NOK, Python version lower than 3.7.")
                print("assistant may not function correctly.")
        else:
            print("NOK, Python 3 not detected.")

    found = True
    print("checking Vagrant version:")
    try:
        version = subprocess.run(["vagrant", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        found = False
        print("NOK, Vagrant not found.")
    if found:
        version_number = version.stdout.split(" ", 1)[1].split(".")
        if (version_number[0] == "2"):
            if (int(version_number[1]) > 1):
                print("OK, Vagrant version higher than 2.2.")
            else:
                print("NOK, Vagrant version lower than 2.2.")
        else:
            print("NOK, Vagrant 2 not detected.")

    found = True
    print("checking Virtualbox version:")
    try:
        version = subprocess.run(["vboxmanage", "--version"], capture_output=True, text=True)
    except FileNotFoundError:
        found = False
        print("Virtualbox not found.")
        print("If you are on Windows, this is probably OK.")
        print("(You can double check VirtualBox version yourself to be sure)")
        print("If you are on Linux, you don't have VirtualBox installed, NOK.")
    if found:
        version_number = version.stdout.split(".")
        if (int(version_number[0]) > 5):
            print("OK, VirtualBox version higher than 5 detected.")
        else:
            print("NOK, VirtualBox version lower than 6 detected.")


def game_loop():
    """Interactively assist the player with playing the game.

    Transform inputs from user into method calls.
    
    Possible inputs
    ---------------
    Functions that control the game:
    (A)bort - destroys all VMs, resets progress to level 0.
    (E)xit  - aborts run, then exits the assistant.
    (S)tart - starts a new run of the adaptive game, if one isn't in progress.
    (N)ext  - advances to the next level. Asks for branch when applicable.
    (I)nfo  - displays info about current run - Level number and name.
    Helper functions:
    (H)elp  - explains all commands on the screen.
    (C)heck - checks if prerequisites to run the game are installed.
    """

    game = Game("levels.yml", "../game")
    print("Welcome to the adaptive game assistant.")
    print("Basic commands are:")
    print("(S)tart, (N)ext, (H)elp, (C)heck, (E)xit")
    while(True):
        print("Waiting for next input:")
        command = input()
        command = command.lower()
        if ((command == "a") or (command == "abort")):
            print("Aborting game, deleting all VMs.")
            game.abort_game()
            print("Game aborted, progress reset, VMs deleted.")
        elif ((command == "e") or (command == "exit")):
            print("Going to exit assistant, abort game and delete VMs.")
            game.abort_game()
            print("Exiting...")
            return
        elif ((command == "s") or (command == "start")):
            print("Trying to start the game.")
            print("The initial setup may take a while, up to 20 minutes.")
            if (game.start_game()):
                print("If you do not see any error messages above,")
                print("then the game was started succesfully!")
                print("You can start playing now.")
            else:
                print("Game was not started, it's already in progress!")
                print("To start over, please run `abort` first.")
        elif ((command == "n") or (command == "next")):
            try:
                if game.level == 0:
                    print("Can't continue, (S)tart the game first!")
                elif game.next_level_exists():
                    print("Going to set up level {}".format(game.level + 1))
                    if game.next_level_is_forked():
                        print("Next level is forked.")
                        game.print_next_level_fork_names()
                        print("Choose level's branch:")
                        branch = input()
                        branch = branch.lower()
                        game.next_level(branch)
                    else:
                        game.next_level()
                    print("Level deployed.")
                    print("If you don't see any errors above, you can continue playing.")
                    if (game.level == 5):
                        print("This is the last level of the game.")
                else:
                    print("No next levels found -- you finished the game!")
                    # print("Remember to save your gamefile idk")            
            except NoLevelFoundError as err:
                print("Error encountered: {}".format(err))
            
        elif ((command == "i") or (command == "info")):
            game.print_info()
        elif ((command == "h") or (command == "help")):
            print_help()
        elif ((command == "c") or (command == "check")):
            check_prerequisites()
        else:
            print("Unknown command. Enter another command or try (H)elp.")


if __name__ == "__main__":
    game_loop()
