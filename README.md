# Adaptive game assistant
The adaptive game assistant is a Python program allowing easy deployment and playing of adaptive cybersecurity games.

The assistant was made as a part of my [bachelor's thesis]() for the university's KYPO lab.
The version of the assistant included in the thesis appendix required 
that the player get some help from an instructor while playing.

This improved version allows for the player to play through the game completely on their own.

The games the assistant can help with must be made with Vagrant and Ansible (as other games for
the KYPO Cyber Range). The Ansible playbooks need to have all tasks tagged, and
there need to be game-specific config files in the `resources` subfolder.

## Usage
The adaptive game assistant is ran by running `./assistant.py` or `python assistant.py` in the project folder.
It automatically runs Vagrant commands to prepare levels of the game,
checks flags when player completes level and provides hints when needed.

Basic assistant commands:
- (S)tart - starts the game from level 1.
- (N)ext  - continues the game to the next level.
- (E)xit  - properly ends the game and exits the assistant.
- (C)eck  - checks versions of all required apps.
- (H)elp  - displays a full list of commands.
- hin(T)  - displays hints, offers new hints.
- (L)og   - saves data from the game into a file.

The project's wiki also has a detailed user guide with examples: [How to use the assistant]()
## Requirements
The assistant requires Python 3.7 or higher to run.

It also requires the PyYAML package of version 5.1 or higher.
(You can install it with `pip install -r python-requirements.txt`)

The game the assistant sets up will require Vagrant and VirtualBox to be installed.
Virtualbox 6.0 or higher and Vagrant 2.2.5 or higher are recommended. 
(The exact requirements of individual games may differ.)

## Python module structure
The main file, `assistant.py`, wraps around several classes the `adaptive_game_module` folder,
and transforms the user's commands into method calls on the objects.
The adaptive game module contains:
- `adaptive_game.py`. The `Game` object from this file represents the game itself.
- `flag_checker.py`. The `FlagChecker` class checks if flags are correct.
- `hint_giver.py`. The `HintGiver` class keeps tracks of taken hints and gives new ones.
- `level_selector.py`. The `LevelSelector` class helps decide which level to go to next.

### Game config files
The assistant is written with modularity in mind, so it should support other adaptive games,
as long as config files for those are written. `assistant.py` looks for config files in the
`resources/` folder.

The needed files are:
- `levels.yml`
- `hints.yml`
- `level_keys.yml`
- `level_requirements.yml`
- `tools.yml`

All of the files should be in YAML. There are sample config files present in the `resources/` folder already.
(These are the files I created for the game I used in my thesis.)
#### levels.yml
`levels.yml` tells the Game object what possible levels are in the game, what Ansible tags
are needed for that level, and what machines need changes done.

Each line of the file should be in the the following format:

`level_name: {branch_name: [machines_to_provision]}`

`branch_name` is not just the name of the branch, but also the Ansible tag used to provision the level.
#### level_keys.yml
`level_keys.yml` is a dictionary of the level flags for the flag checker.

The keys should be in the following format:
`level_name: flag`
#### level_requirements.yml
`level_requirements.yml` is the list of requirements for the level selector.
The requirements should be in the following format:

`level_name: [[branch_name, requirements]]`

where `requirements` is either `null` or `[time, tool]`

e.g. `level2: [[level2a, null], [level2b, [10, "SQL injection"]]]`
`null` requirement means that this is the "default" version of the level.
`[time, tool]` means that the player must know `tool` and have time less than `time`.

The `tools` are expected to also be listed in `tools.yml`.
#### tools.yml
`tools.yml` is a list of tools that the assistant will ask the player about before they play the game.

If the player is familiar with a tool, they may be sent to a harder version of a level by the level selector.

This file may also contain tools that do not appear in the game.

#### hints.yml
`hints.yml` contains all the hints the player can receive, and should have the following format:

`level_name: level+branch name: hint title: hint text`

As hints are usually long, the sample file uses indentation to make the file better readable.

## I want to try out the assistant, but I don't have an adaptive game.
The simplest way to try the assistant out with no access to another adaptive game is:

1. Download the [thesis archive]() of my Adaptive Cybersecurity Games thesis.
2. In the archive, replace the `assistant/` folder with the folder of this repository.
(The assistant included with the thesis is an earlier version.)
3. Make sure that the sample files in the `resources/` subfolder are present.

The assistant should run the game included with my thesis using the sample resources files.
The level instructions for that game are included in the `wiki/` subfolder of the thesis archive you downloaded.

## Troubleshooting
All known common problems are in the [Troubleshooting doc]() on the repository wiki.
