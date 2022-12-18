# ChocoCheat

This is a small python program to help people exploit/cheat with the Chocobo World of Final Fantasy VIII. Possible
rewards include all Ultimate Weapons, GF Doomtrain on disc 2, maxing out your character's stats, and receive items in 
quantities that can refine to 100x every magic except Meteor trivially. 

Additionally, this repository contains the [droptables](./docs/droplist.md) for items received from the chocobo world.

# Requirements

- Python 3.7 or later.

# Installation

Install like any other github repository:
```bash
pip install git+https://github.com/Gloweye/chococheat.git
```

# Usage

After installation, the CLI becomes available:
```bash
python -m chococheat [command] [--help]
```
Use the `--help` CLI option to navigate between options.

Typical usage:
```bash
# Initialize a cheatfile with recommended settings
python -m chococheat init --auto
python -m chococheat run 
```

The `run` command will keep replacing the chocoworld save file with a cheated version, letting you repeatedly import
the items, without even switching out of the game.

The rewards can be seen in the droptables. If you want a different droptable, save your game, load the save, and
resume importing. I generally find it more than sufficient to import each table about 7-10 times. At about four seconds
per import, and perhaps a few more to scroll through all rewards, this is very fast. 

Merely importing A-class items and selling them gives about 20% of the maximum amount of Gil you can have.

The only situation needing more imports is when you want to maximise your characters stats. At 2 or 3 of every Up item
per 64-B-class-item import, that should still not take more than an hour. 
