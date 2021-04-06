#!/usr/bin/env python3

from adaptive_game_module.adaptive_game import Game, NoLevelFoundError
from adaptive_game_module.hint_giver import HintGiver
from adaptive_game_module.level_selector import LevelSelector
from adaptive_game_module.flag_checker import FlagChecker

import subprocess
import os
import time

def print_help():
    """Print list of arguments that game_loop accepts."""
    print("Functions that control the game:")
    print("(A)bort  - destroys all VMs, resets progress to level 0.")
    print("(E)xit   - aborts run, then exits the assistant.")
    print("(S)tart  - starts a new run of the adaptive game, if one isn't in progress.")
    print("(N)ext   - advances to the next level.")
    print("(F)inish - when on the last level, finishes the game and logs end time.")
    print("hin(T)   - ask for hints, read previously given hints.")
    print("(I)nfo   - displays info about current game - levels traversed, times...")
    print("(L)og    - log (save) the information about the game into a file.")
    print("Helper functions:")
    print("(H)elp   - explains all commands on the screen.")
    print("(C)heck  - checks if prerequisites to run the game are installed.")


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
        if version_number[0] == "3":
            if int(version_number[1]) >= 7:
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
        if version_number[0] == "2":
            if int(version_number[1]) > 1:
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
        if int(version_number[0]) > 5:
            print("OK, VirtualBox version higher than 5 detected.")
        else:
            print("NOK, VirtualBox version lower than 6 detected.")

def write_log(filename, game, hint_giver, flag_checker):
    """Write log from `game` and `hint_giver` to file `filename`
    Calls logging methods, which are just yaml dumps."""
    try:
        game.log_to_file(filename)
        hint_giver.log_to_file(filename)
        flag_checker.log_to_file(filename)
    except OSError:
        print("Error encountered while saving game data:")
        print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        print("Double check that location {} for the file exists and can be written to.".format(filename))

def give_hint(game, hint_giver):
    """Recap previously given hints, and give player another hint if they want."""
    if not game.game_in_progress:
        print("Game not started, can't give hints.")
        return
    if hint_giver.show_taken_hints("level" + str(game.level), game.branch) != []:
        print("Hints taken in current level:")
        for hint in hint_giver.show_taken_hints("level" + str(game.level), game.branch):
            print("{}: {}".format(hint, hint_giver.take_hint("level" + str(game.level), game.branch, hint)))
    print("Choose which hint to take (Write a number):")
    print("0: (cancel, take no hint)")
    i = 1
    possible_hints = hint_giver.show_possible_hints("level" + str(game.level), game.branch)
    for hint in possible_hints:
        print("{}: {}".format(i, hint))
        i += 1
    hint = input()
    try:
        hint = int(hint)
        if hint == 0:
            print("0 selected, no hint taken.")
        elif hint >= i:
            print("Number too high selected, no hint taken.")
        else:
            print("{}: {}".format(hint, hint_giver.take_hint(
                        "level" + str(game.level), game.branch, possible_hints[hint-1])))
    except ValueError:
        print("Invalid input, no hint taken.")

def starting_quiz(level_selector):
    """Ask the player a few questions, saving known tools to level selector."""
    print("Please answer 'yes' if you have ever used a tool or skill before,")
    print("or 'no' if you haven't.")
    for tool in level_selector.tool_list:
        unanswered = True
        while (unanswered):
            print("Are you familiar with {}?".format(tool))
            command = input()
            command = command.lower()
            if command in ("y", "yes"):
                level_selector.add_known_tool(tool)
                unanswered = False
            elif command in ("n", "no"):
                unanswered = False
            elif command in ("exit", "stop"):
                return False
            else:
                print("Answer has to be 'yes' or 'no' (or 'exit')")
                unanswered = True
    return True

def start_game(game, level_selector):
    """Start the game through the game object after doing a starting quiz."""
    print("Before the game starts, please fill in a little quiz.")
    print("It will help better decide what levels you will play.")
    confirmation = starting_quiz(level_selector)
    if not confirmation:
        print("Game not started, quiz not filled in.")
        return
    print("Quiz filled in!")
    print("Starting the game.")
    print("The initial setup may take a while, up to 20 minutes.")
    if game.start_game():
        print("If you do not see any error messages above,")
        print("then the game was started succesfully!")
        print("You can start playing now.")
    else:
        print("Game was not started, it's already in progress!")
        print("To start over, please run `abort` first.")

def abort_game(game, hint_giver, flag_checker):
    """Abort the game and reset all progress, log current game in a file."""
    try:
        if os.path.isdir("logs"):
            write_log("logs/aborted_game" + str(time.time()), game, hint_giver, flag_checker)
    except OSError as err:
        # print("Failed to save game log.")
        # print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        pass    
    print("Aborting game, deleting all VMs.")
    game.abort_game()
    hint_giver.restart_game()
    print("Game aborted, progress reset, VMs deleted.")

def player_logging(game, hint_giver, flag_checker):
    """Player-initiated log of the game. Always saves to logs/game_log.yml"""
    if os.path.exists("logs/game_log.yml"):
        print("It appears that there is already a saved game log.")
        print("Write 'yes' to overwrite it.")
        confirmation = input()
        confirmation = confirmation.lower()
        if (confirmation == "yes"):
            print("Overwriting file...")
            with open("logs/game_log.yml", 'w'): 
                pass
            write_log("logs/game_log.yml", game, hint_giver, flag_checker)
        else:
            print("File not overwritten.")
    else:
        print("Writing file...")
        write_log("logs/game_log.yml", game, hint_giver, flag_checker)

def finish_game(game):
    """Mark game as finished, inform player if that's impossible."""
    if game.finish_game():
        print("Game finished, total time saved!")
    elif (not game.game_in_progress and not game.game_finished):
        print("Can't finish game, game was not started yet.")
    elif (not game.game_in_progress and game.game_finished):
        print("Can't finish game, game was already finished earlier.")
    else:
        print("Could not finish game.")
        print("Make sure you are on the last level!")

def try_next_level(game, level_selector):
    if game.next_level_exists():
        print("Going to set up level {}".format(game.level + 1))
        if game.next_level_is_forked():
            next_level = level_selector.next_level(game.level, game.running_time())
            print("Setting up next level: {}".format(next_level))
            game.next_level(next_level)
        else:
            game.next_level()
        print("Level deployed.")
        print("If you don't see any errors above, you can continue playing.")
        if game.level == 5:  # TODO: maybe remove hardcode
            print("This is the last level of the game.")
    else:
        print("No next levels found -- you finished the game!")
        print("Make sure to run (F)inish and (L)og your progress before exiting.")

def check_flag(level, flag_checker):
    print("To continue, please enter the flag you found:")
    print("(case sensitive)")
    flag = input()
    if flag_checker.check_flag("level"+str(level), flag):
        print("Flag is correct!")
        return True
    print("Flag is incorrect.")
    print("Double check your spelling, or use hints if you don't know how to proceed.")
    return False

def game_loop():
    """Interactively assist the player with playing the game.

    Transform inputs from user into method calls.

    Possible inputs
    ---------------
    Functions that control the game:
    (A)bort  - destroys all VMs, resets progress to level 0.
    (E)xit   - aborts run, then exits the assistant.
    (S)tart  - starts a new run of the adaptive game, if one isn't in progress.
    (N)ext   - advances to the next level.
    hin(T)   - ask for hints, read previously given hints.
    (F)inish - when on the last level, finishes the game and logs end time.
    (I)nfo   - displays info about current game - levels traversed, times...
    (L)og    - log (save) the information about the game into a file.
    Helper functions:
    (H)elp   - explains all commands on the screen.
    (C)heck  - checks if prerequisites to run the game are installed.
    """
    if not os.path.isdir("logs"):
        try:
            os.mkdir("logs")
        except FileExistsError:
            pass #directory already exists, all OK
        except OSError as err:
            print("Error encountered while creating the /logs subfolder for save data:")
            print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
            print("If not fixed, saving game data might not be possible.")
    try:
        game = Game("resources/levels.yml", "../game")
    except OSError as err:
        print("Error encountered while setting up the game object.")
        print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        print("(Most likely, `resources/levels.yml` file couldn't be read.")
        print("Make sure it is in the folder, and readable.")
    try:
        hint_giver = HintGiver("resources/hints.yml")
    except OSError as err:
        print("Error encountered while setting up the hint giver.")
        print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        print("(Most likely, `resources/hints.yml` file couldn't be read.")
        print("Make sure it is in the folder, and readable.")
    try:
        level_selector = LevelSelector("resources/tools.yml", "resources/level_requirements.yml")
    except OSError as err:
        print("Error encountered while setting up the level selector.")
        print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        print("(Most likely, `resources/level_requirements.yml` file couldn't be read.")
        print("Make sure it is in the folder, and readable.")
    try:
        flag_checker = FlagChecker("resources/level_keys.yml")
    except OSError as err:
        print("Error encountered while setting up the flag checker.")
        print("Error number: {}, Error text: {}".format(err.errno, err.strerror))
        # print("(Most likely, `resources/level_requirements.yml` file couldn't be read.")
        # print("Make sure it is in the folder, and readable.")


    print("Welcome to the adaptive game assistant.")
    print("Basic commands are:")
    print("(S)tart, (N)ext, (H)elp, (C)heck, (E)xit")
    while True:
        print("Waiting for your input:")
        command = input()
        command = command.lower()
        if command in ("a", "abort", "(a)bort"):
            abort_game(game, hint_giver, flag_checker)
        elif command in ("e", "exit"):
            abort_game(game, hint_giver, flag_checker)
            print("Exiting...")
            return
        elif command in ("s", "start", "(s)tart"):
            start_game(game, level_selector)
        elif command in ("n", "next", "(n)ext"):
            try:
                if game.level == 0:
                    print("Can't continue, (S)tart the game first!")
                elif game.level == 5:
                    print("Can't continue, you are on the last level!")
                    print("Make sure to run (F)inish and (L)og your progress before exiting.")
                else:
                    if check_flag(game.level, flag_checker):
                        try_next_level(game, level_selector)
            except NoLevelFoundError as err:
                print("Error encountered: {}".format(err))
        elif command in ("f", "finish", "(f)inish"):
            if (not game.game_in_progress and not game.game_finished):
                print("Can't finish game, game was not started yet.")
            elif (not game.game_in_progress and game.game_finished):
                print("Can't finish game, game was already finished earlier.")
            else:
                if check_flag(game.level, flag_checker):
                    finish_game(game)
        elif command in ("i", "info", "information", "(i)nfo", "(i)nformation"):
            game.print_info()
        elif command in ("h", "help", "(h)elp"):
            print_help()
        elif command in ("c", "check", "(c)heck"):
            check_prerequisites()
        elif command in ("l", "log", "(l)og"):
            player_logging(game, hint_giver, flag_checker)
        elif command in ("t", "hint", "hin(t)"):
            give_hint(game, hint_giver)
        else:
            print("Unknown command. Enter another command or try (H)elp.")


if __name__ == "__main__":
    game_loop()
