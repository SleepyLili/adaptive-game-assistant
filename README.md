# Adaptive game assistant
The adaptive game assistant is a Python program allowing easy deployment and playing of adaptive cybersecurity games.

When bundled with a compatible game (and a few config files), the assistant
allows the user to play through the game independently, with no help needed from
a teacher or a supervisor. The assistant automatically runs Vagrant commands to prepare levels 
of the game, checks flags when player completes levels and provides hints.

The assistant was originally made as a part of my [bachelor's thesis](https://is.muni.cz/th/mnrr8/)
for the university's KYPO Lab. It was later improved to be used in a university course.

The games the assistant can run must be made with Vagrant and Ansible (as other games at KYPO).
The Ansible playbooks need to have all tasks tagged, and
there need to be game-specific config files in the `resources/` subfolder.
## Usage
The adaptive game assistant is ran by running `./assistant.py` or `python assistant.py` in the project folder.

Basic commands:
- (S)tart - starts the game from level 1.
- (N)ext  - continues the game to the next level.
- (E)xit  - properly ends the game and exits the assistant.
- (C)eck  - checks versions of all required apps.
- (H)elp  - displays a full list of commands.
- hin(T)  - displays hints, offers new hints.
- (L)og   - saves data from the game into a file.

The project's wiki has a user guide with examples: [Assistant guide](https://github.com/SleepyLili/adaptive-game-assistant/wiki/Assistant-guide)
## Requirements
The assistant requires Python 3.7 or higher to run.

It also requires the PyYAML package of version 5.1 or higher.
(You can install it with `pip install -r python-requirements.txt`)

The game the assistant sets up will require Vagrant and VirtualBox to be installed.
Virtualbox 6.0 or higher and Vagrant 2.2.5 or higher are recommended. 
(The exact requirements of individual games may differ.)

The wiki has an in-depth installation guide: [Installation](https://github.com/SleepyLili/adaptive-game-assistant/wiki/Installation)
## Python module structure
The main file, `assistant.py` makes use of the files from the `adaptive_game_module/` folder,
and transforms the user's commands into method calls on the objects.

The adaptive game module contains:
- `adaptive_game.py`. The `Game` class represents the state of the game.
- `flag_checker.py`. The `FlagChecker` class checks if flags are correct.
- `hint_giver.py`. The `HintGiver` class keeps tracks of taken hints and gives new ones.
- `level_selector.py`. The `LevelSelector` class helps decide which level to go to next.

### Game config files
Besides tagged ansible playbooks, each adaptive game needs a few config files to work.
The config files are mostly YAML lists and dicts.
`assistant.py` looks for config files in the `resources/` folder.

The needed files are:
- `levels.yml`
- `hints.yml`
- `level_keys.yml`
- `level_requirements.yml`
- `tools.yml`

More about the config files and their format is on the wiki: [Config files](https://github.com/SleepyLili/adaptive-game-assistant/wiki/Config-files)
## I want to try out the assistant, but I don't have an adaptive game
The simplest way to try the assistant out with no access to another adaptive game is:

1. Download the [thesis archive](https://is.muni.cz/th/mnrr8/thesis-archive.zip) of my Adaptive Cybersecurity Games thesis.
2. In the archive, replace the `assistant/` folder with the folder of this repository.
(The assistant included with the thesis is an earlier version.)
3. Extract `game.zip` from the archive. (So that you have a `game/` folder.)
4. Make sure that the sample files in the `resources/` subfolder are present.
5. Run the assistant as intended.

The assistant should run the game included with my thesis using the sample resources files.
The level instructions for that game are included in the `wiki/` subfolder of the thesis archive you downloaded.

## Troubleshooting
All known common problems are in the [troubleshooting](https://github.com/SleepyLili/adaptive-game-assistant/wiki/Troubleshooting) doc on the repository wiki.
