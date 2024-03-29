# Adaptive game assistant

> [!WARNING]
> As of 2024, I'm archiving this repository and removing the adaptive game try-out section from the README.md.
> The information in this README.md was correct as of 2022, but as Vagrant, VirtualBox, Ansible and the applications
> used in individual games change, I can't guarantee that things will continue to work the way they did.

> [!NOTE]
> If you're a lector or an assistant of the PA197 course, you're probably looking for the the PA197 resources in the
> university Gitlab instead of this repository.

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

## Game requirements
### Ansible tags
The assistant expects some things of the Ansible playbooks.
- All tasks should be tagged
- Tasks for game setup and the first level are tagged `setup`
- Tasks for level past the first are in the format `level + [number] + [branch, optional]` i.e. "level3", "level4a"

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

## Troubleshooting
All known common problems are in the [troubleshooting](https://github.com/SleepyLili/adaptive-game-assistant/wiki/Troubleshooting) doc on the repository wiki.

## Possible improvements
Since the assistant needed to be ready and functional by a deadline,
there are some features that would have been nice to have, but weren't necessary
at the moment. Those features include:

- **A "manual mode" where the user gets to decide next level**

This would be similar to the original assistant prototype, where the user had the
teacher tell them what branch they were choosing. It would also simplify some testing
scenarios.

- **A "dry run mode" for testing**

Sometimes, it'd be nice to turn off the assistant's underlying calls to Vagrant,
to speed up testing of features, config files, etc.

- **The ability to turn off certain modules**

In a game without flags, or where flag checking isn't important, the flag
checker could be turned off, for example.

- **Better support for branching levels -- arbitrary names, shorter and longer playthroughs**

The assistant as it is right now expects the levels to have a naming convention, and it also expects that for every possible playthrough, there will always be the same number of levels.
Removing these constraints would make it possible to support games of variable length, or with entire "replacement" branches, etc.
