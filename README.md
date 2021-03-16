# Adaptive game assistant
This adaptive assistant was written for the remote testing of the adaptive version of the Captain Slovakistan game. It is licensed under MIT license.

It requires Python version at least 3.7, and the Python yaml package (`pip install -r python-requirements.txt`) to run. The cybersecurity game the assistant runs requires Vagrant and VirtualBox. Full instructions for installing are in the the [installation guide](../wiki/installation-guide.md).

The assistant loads configuration from the `levels.yml` file.

## Assistant usage
The adaptive game assistant is ran by running `./assistant.py` or `python assistant.py` in the project folder.
Essentially, it automatically runs the commands listed below in manual usage,
but all the user has to specify is that they want to advance to the next level.

Basic commands:
- (S)tart - starts the game from level 1.
- (N)ext - continues the game to the next level.
- (E)xit - properly ends the game and exits the assistant.
- (C)eck - Checks versions of all required apps.
- (H)elp - displays a full list of commands.

For more information about the game, including the levels' instructions, see the [game text](../wiki/game-text.md).

## Structure
The assistant consists of a `Game` class, that represents the game itself, and a `game_loop()` function, which keeps an instance of a `Game` and translates inputs from the command line into method calls on the `Game` object.

The assistant is written with modularity in mind, so it should support other adaptive games, as long as they provide a correct `levels.yml` file, and has complete tagging in the Ansible playbooks.

### levels.yml
`levels.yml` is the configuration file that tells the assistant what possible levels are in the game, what tags to run to set up that level, and what machines need to be provisioned for that level.

Every line in the file represents a level, and each line must have the following format:

`level_name: {branch_name: [machines_to_provision]}`

## Manual usage without assistant
How to play the game without using the adaptive game assistant.
1. Run `ANSIBLE_ARGS='--tags "setup"' vagrant up`.
During the instantiation of `br` machine, you will be prompted for network 
interface which connects you to internet (usually the first or second in the list).
2. When the player finishes a level, it's time to prepare the next one. 
Some levels have multiple versions (level2a, level2b), some levels have only one version (level3).
The file `levels.yml` lists all possible levels, 
along with the vagrant boxes that need an update for the level to be ran.
To prepare the next level, run `ANSIBLE_ARGS='--tags "<level>"' vagrant up <boxes> --provision`, 
where `<level>` is a key from levels.yml, and `<boxes>` is the corresponding value from the same file. 
(Examples: `ANSIBLE_ARGS='--tags "level2a"' vagrant up web attacker --provision`, 
`ANSIBLE_ARGS='--tags "level3"' vagrant up web --provision`)
3. After the game is finished, run `vagrant destroy` to remove the game components and virtual machines.
The game can be reran after this step.

## Troubleshooting
### Set-up hangs on provisioning machine `br`
```
==> br: Running provisioner: ansible_local...
```
On Windows, the setup of the game rarely hangs on provisioning of the `br` machine.
When playing via the assistant, you will have to exist by pressing `Ctrl+C`. Then, you should kill the stuck process in the task manager (usually called similarly to `Ruby interpreter` or `Vagrant`)
Then you can resume the game by launching the assistant again, running `abort`, and then `start` again. (You can also attempt to make the assistant pick up where it ended before it got stuck, by not running `abort`, and running `start` only.)
