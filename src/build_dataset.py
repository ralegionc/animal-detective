"""
Step 0: Build the dataset.

Every animal below is described by simple yes/no facts that a curious ten year old
could check at a zoo. 1 means yes, 0 means no. "legs" is just a count.

The last three columns are different in kind. They are not clues the sorting model
is allowed to use. They exist so we can ask a second, harder question later on:
not "what kind of animal is this" but "how long will it live".

Columns
-------
hair             does it have hair or fur?
feathers         does it have feathers?
eggs             does it lay eggs?
milk             does it feed its babies milk?
airborne         can it fly?
aquatic          does it live in or on water?
predator         does it hunt and eat other animals?
toothed          does it have teeth?
backbone         does it have a spine?
breathes         does it breathe air?
venomous         can it poison or sting?
fins             does it have fins?
legs             how many legs?
tail             does it have a tail?
domestic         do people commonly keep it?
catsize          is it about the size of a cat or bigger?
weight_kg        what a typical adult weighs
lifespan_years   how long a healthy one tends to live
diet             meat, plants or both
group            the answer we want the computer to learn
"""

import csv
from pathlib import Path

COLUMNS = [
    "animal", "hair", "feathers", "eggs", "milk", "airborne", "aquatic",
    "predator", "toothed", "backbone", "breathes", "venomous", "fins",
    "legs", "tail", "domestic", "catsize",
    "weight_kg", "lifespan_years", "diet", "group",
]

# animal, hair, feathers, eggs, milk, airborne, aquatic, predator, toothed,
# backbone, breathes, venomous, fins, legs, tail, domestic, catsize,
# weight_kg, lifespan_years, diet, group
ROWS = [
    # ------------------------------ mammals ------------------------------
    ("aardvark",        1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    60,  23, "meat",   "mammal"),
    ("anteater",        1,0,0,1,0,0,1,0,1,1,0,0,4,1,0,1,    40,  16, "meat",   "mammal"),
    ("antelope",        1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,    50,  15, "plants", "mammal"),
    ("armadillo",       1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     5,  15, "meat",   "mammal"),
    ("baboon",          1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,    25,  30, "both",   "mammal"),
    ("badger",          1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    12,  10, "both",   "mammal"),
    ("bear",            1,0,0,1,0,0,1,1,1,1,0,0,4,0,0,1,   300,  25, "both",   "mammal"),
    ("beaver",          1,0,0,1,0,1,0,1,1,1,0,0,4,1,0,1,    20,  15, "plants", "mammal"),
    ("bison",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   800,  20, "plants", "mammal"),
    ("boar",            1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    80,  12, "both",   "mammal"),
    ("brown bat",       1,0,0,1,1,0,1,1,1,1,0,0,2,1,0,0,  0.01,  20, "meat",   "mammal"),
    ("buffalo",         1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   700,  20, "plants", "mammal"),
    ("camel",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,   600,  45, "plants", "mammal"),
    ("capybara",        1,0,0,1,0,1,0,1,1,1,0,0,4,0,0,1,    55,  10, "plants", "mammal"),
    ("cat",             1,0,0,1,0,0,1,1,1,1,0,0,4,1,1,1,   4.5,  15, "meat",   "mammal"),
    ("cheetah",         1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    55,  12, "meat",   "mammal"),
    ("chimpanzee",      1,0,0,1,0,0,0,1,1,1,0,0,2,0,0,1,    45,  40, "both",   "mammal"),
    ("chinchilla",      1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,0,   0.6,  15, "plants", "mammal"),
    ("cow",             1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,   700,  20, "plants", "mammal"),
    ("coyote",          1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    15,  14, "meat",   "mammal"),
    ("deer",            1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,    70,  15, "plants", "mammal"),
    ("dog",             1,0,0,1,0,0,1,1,1,1,0,0,4,1,1,1,    25,  13, "meat",   "mammal"),
    ("dolphin",         0,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,   200,  40, "meat",   "mammal"),
    ("donkey",          1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,   250,  30, "plants", "mammal"),
    ("echidna",         1,0,1,1,0,0,1,0,1,1,1,0,4,0,0,0,     5,  40, "meat",   "mammal"),
    ("elephant",        1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,  4000,  65, "plants", "mammal"),
    ("ferret",          1,0,0,1,0,0,1,1,1,1,0,0,4,1,1,0,   1.2,   9, "meat",   "mammal"),
    ("fox",             1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     7,   5, "both",   "mammal"),
    ("fruit bat",       1,0,0,1,1,0,0,1,1,1,0,0,2,1,0,0,   0.6,  20, "plants", "mammal"),
    ("giant panda",     1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   110,  20, "plants", "mammal"),
    ("giraffe",         1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,  1200,  25, "plants", "mammal"),
    ("goat",            1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,    60,  15, "plants", "mammal"),
    ("gorilla",         1,0,0,1,0,0,0,1,1,1,0,0,2,0,0,1,   160,  40, "plants", "mammal"),
    ("guinea pig",      1,0,0,1,0,0,0,1,1,1,0,0,4,0,1,0,     1,   6, "plants", "mammal"),
    ("hamster",         1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,0,  0.15,   3, "both",   "mammal"),
    ("hare",            1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,     4,   5, "plants", "mammal"),
    ("hedgehog",        1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,   0.8,   5, "meat",   "mammal"),
    ("hippopotamus",    1,0,0,1,0,1,0,1,1,1,0,0,4,1,0,1,  1500,  45, "plants", "mammal"),
    ("horse",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,   500,  28, "plants", "mammal"),
    ("hyena",           1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    60,  20, "meat",   "mammal"),
    ("jaguar",          1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    90,  14, "meat",   "mammal"),
    ("kangaroo",        1,0,0,1,0,0,0,1,1,1,0,0,2,1,0,1,    65,  22, "plants", "mammal"),
    ("koala",           1,0,0,1,0,0,0,1,1,1,0,0,4,0,0,1,    12,  15, "plants", "mammal"),
    ("lemur",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,   2.5,  18, "plants", "mammal"),
    ("leopard",         1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    60,  15, "meat",   "mammal"),
    ("lion",            1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,   190,  15, "meat",   "mammal"),
    ("llama",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,   150,  20, "plants", "mammal"),
    ("lynx",            1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    22,  14, "meat",   "mammal"),
    ("manatee",         0,0,0,1,0,1,0,1,1,1,0,1,0,1,0,1,   450,  60, "plants", "mammal"),
    ("meerkat",         1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,   0.8,  13, "meat",   "mammal"),
    ("mole",            1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,   0.1,   4, "meat",   "mammal"),
    ("mongoose",        1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     2,  12, "meat",   "mammal"),
    ("moose",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   500,  20, "plants", "mammal"),
    ("mouse",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,  0.02,   2, "both",   "mammal"),
    ("narwhal",         0,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,  1600,  50, "meat",   "mammal"),
    ("opossum",         1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     3,   3, "both",   "mammal"),
    ("orangutan",       1,0,0,1,0,0,0,1,1,1,0,0,2,0,0,1,    75,  45, "plants", "mammal"),
    ("orca",            0,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,  5500,  60, "meat",   "mammal"),
    ("otter",           1,0,0,1,0,1,1,1,1,1,0,0,4,1,0,1,    10,  15, "meat",   "mammal"),
    ("pangolin",        1,0,0,1,0,0,1,0,1,1,0,0,4,1,0,1,    15,  20, "meat",   "mammal"),
    ("pig",             1,0,0,1,0,0,1,1,1,1,0,0,4,1,1,1,   120,  15, "both",   "mammal"),
    ("platypus",        1,0,1,1,0,1,1,0,1,1,1,0,4,1,0,1,   1.5,  17, "meat",   "mammal"),
    ("porcupine",       1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,    12,  18, "plants", "mammal"),
    ("rabbit",          1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,0,     2,   9, "plants", "mammal"),
    ("raccoon",         1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     8,   5, "both",   "mammal"),
    ("rat",             1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,  0.35,   3, "both",   "mammal"),
    ("red panda",       1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,     5,  14, "plants", "mammal"),
    ("reindeer",        1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   120,  15, "plants", "mammal"),
    ("rhinoceros",      1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,  2300,  45, "plants", "mammal"),
    ("sea lion",        1,0,0,1,0,1,1,1,1,1,0,1,0,1,0,1,   300,  25, "meat",   "mammal"),
    ("seal",            1,0,0,1,0,1,1,1,1,1,0,1,0,0,0,1,   130,  30, "meat",   "mammal"),
    ("sheep",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,1,1,    70,  12, "plants", "mammal"),
    ("skunk",           1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,     4,   7, "both",   "mammal"),
    ("sloth",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,     5,  30, "plants", "mammal"),
    ("squirrel",        1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,0,   0.5,  10, "plants", "mammal"),
    ("tasmanian devil", 1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,     8,   6, "meat",   "mammal"),
    ("tiger",           1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,   220,  16, "meat",   "mammal"),
    ("vampire bat",     1,0,0,1,1,0,1,1,1,1,0,0,2,1,0,0,  0.04,  12, "meat",   "mammal"),
    ("walrus",          1,0,0,1,0,1,1,1,1,1,0,1,0,0,0,1,   900,  40, "meat",   "mammal"),
    ("warthog",         1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,    80,  15, "plants", "mammal"),
    ("weasel",          1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,0,   0.2,   5, "meat",   "mammal"),
    ("whale",           0,0,0,1,0,1,1,0,1,1,0,1,0,1,0,1,100000,  80, "meat",   "mammal"),
    ("wolf",            1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    45,  14, "meat",   "mammal"),
    ("wolverine",       1,0,0,1,0,0,1,1,1,1,0,0,4,1,0,1,    15,  12, "meat",   "mammal"),
    ("wombat",          1,0,0,1,0,0,0,1,1,1,0,0,4,0,0,1,    26,  15, "plants", "mammal"),
    ("zebra",           1,0,0,1,0,0,0,1,1,1,0,0,4,1,0,1,   380,  25, "plants", "mammal"),

    # ------------------------------- birds -------------------------------
    ("albatross",       0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,1,     9,  50, "meat",   "bird"),
    ("blue jay",        0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,  0.09,   7, "both",   "bird"),
    ("canary",          0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,  0.02,  10, "plants", "bird"),
    ("chicken",         0,1,1,0,0,0,0,0,1,1,0,0,2,1,1,0,     2,   8, "both",   "bird"),
    ("cockatoo",        0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,   0.9,  60, "plants", "bird"),
    ("condor",          0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,1,    11,  60, "meat",   "bird"),
    ("crane",           0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,1,     5,  30, "both",   "bird"),
    ("crow",            0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,   0.5,  15, "both",   "bird"),
    ("cuckoo",          0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,   0.1,   6, "meat",   "bird"),
    ("dove",            0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,   0.2,  10, "plants", "bird"),
    ("duck",            0,1,1,0,1,1,0,0,1,1,0,0,2,1,0,0,     1,  10, "both",   "bird"),
    ("eagle",           0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,1,     5,  25, "meat",   "bird"),
    ("emu",             0,1,1,0,0,0,0,0,1,1,0,0,2,1,0,1,    40,  20, "plants", "bird"),
    ("falcon",          0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,   0.8,  15, "meat",   "bird"),
    ("finch",           0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,  0.02,   6, "plants", "bird"),
    ("flamingo",        0,1,1,0,1,1,0,0,1,1,0,0,2,1,0,1,   3.5,  40, "both",   "bird"),
    ("goose",           0,1,1,0,1,1,0,0,1,1,0,0,2,1,1,1,     5,  20, "plants", "bird"),
    ("gull",            0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,     1,  20, "both",   "bird"),
    ("hawk",            0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,     1,  20, "meat",   "bird"),
    ("heron",           0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,1,   2.5,  20, "meat",   "bird"),
    ("hummingbird",     0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0, 0.004,   5, "plants", "bird"),
    ("kingfisher",      0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,  0.09,   7, "meat",   "bird"),
    ("kiwi",            0,1,1,0,0,0,1,0,1,1,0,0,2,0,0,0,   2.5,  40, "meat",   "bird"),
    ("lark",            0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,  0.04,   8, "both",   "bird"),
    ("macaw",           0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,1,     1,  60, "plants", "bird"),
    ("magpie",          0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,  0.22,  20, "both",   "bird"),
    ("ostrich",         0,1,1,0,0,0,0,0,1,1,0,0,2,1,0,1,   110,  45, "plants", "bird"),
    ("owl",             0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,   1.5,  20, "meat",   "bird"),
    ("parakeet",        0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,  0.04,  15, "plants", "bird"),
    ("peacock",         0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,1,     5,  20, "both",   "bird"),
    ("pelican",         0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,1,     7,  25, "meat",   "bird"),
    ("penguin",         0,1,1,0,0,1,1,0,1,1,0,0,2,1,0,1,    30,  20, "meat",   "bird"),
    ("pheasant",        0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,   1.2,  12, "both",   "bird"),
    ("pigeon",          0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,   0.3,  15, "plants", "bird"),
    ("puffin",          0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,0,   0.5,  20, "meat",   "bird"),
    ("quail",           0,1,1,0,1,0,0,0,1,1,0,0,2,1,1,0,   0.1,   5, "plants", "bird"),
    ("raven",           0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,1,   1.2,  20, "both",   "bird"),
    ("robin",           0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,  0.02,   6, "both",   "bird"),
    ("sparrow",         0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,  0.03,   5, "both",   "bird"),
    ("stork",           0,1,1,0,1,1,1,0,1,1,0,0,2,1,0,1,   3.5,  30, "meat",   "bird"),
    ("swan",            0,1,1,0,1,1,0,0,1,1,0,0,2,1,0,1,    11,  25, "plants", "bird"),
    ("swift",           0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,0,  0.04,  15, "meat",   "bird"),
    ("toucan",          0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,1,   0.6,  20, "plants", "bird"),
    ("turkey",          0,1,1,0,0,0,0,0,1,1,0,0,2,1,1,1,     8,  10, "both",   "bird"),
    ("vulture",         0,1,1,0,1,0,1,0,1,1,0,0,2,1,0,1,     5,  25, "meat",   "bird"),
    ("woodpecker",      0,1,1,0,1,0,0,0,1,1,0,0,2,1,0,0,   0.1,  11, "meat",   "bird"),

    # -------------------------------- fish -------------------------------
    ("anchovy",         0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,  0.02,   4, "meat",   "fish"),
    ("angelfish",       0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,  0.05,  10, "both",   "fish"),
    ("barracuda",       0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,    10,  14, "meat",   "fish"),
    ("bass",            0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,     2,  10, "meat",   "fish"),
    ("betta",           0,0,1,0,0,1,1,1,1,0,0,1,0,1,1,0, 0.003,   3, "meat",   "fish"),
    ("carp",            0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,     5,  20, "both",   "fish"),
    ("catfish",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,     3,  15, "both",   "fish"),
    ("clownfish",       0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,  0.03,  10, "both",   "fish"),
    ("cod",             0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,     8,  20, "meat",   "fish"),
    ("flounder",        0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,     2,  15, "meat",   "fish"),
    ("goldfish",        0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,   0.1,  15, "both",   "fish"),
    ("grouper",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,    40,  40, "meat",   "fish"),
    ("guppy",           0,0,0,0,0,1,0,1,1,0,0,1,0,1,1,0, 0.001,   2, "both",   "fish"),
    ("haddock",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,     2,  10, "meat",   "fish"),
    ("halibut",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,    30,  30, "meat",   "fish"),
    ("herring",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,   0.3,  12, "meat",   "fish"),
    ("koi",             0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,1,     8,  40, "both",   "fish"),
    ("lionfish",        0,0,1,0,0,1,1,1,1,0,1,1,0,1,0,0,   1.2,  10, "meat",   "fish"),
    ("mackerel",        0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,   0.7,  11, "meat",   "fish"),
    ("manta ray",       0,0,0,0,0,1,0,0,1,0,0,1,0,1,0,1,  1400,  45, "meat",   "fish"),
    ("marlin",          0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,   200,  15, "meat",   "fish"),
    ("minnow",          0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0, 0.005,   3, "both",   "fish"),
    ("moray eel",       0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,    15,  30, "meat",   "fish"),
    ("perch",           0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,   0.5,   9, "meat",   "fish"),
    ("pike",            0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,     8,  15, "meat",   "fish"),
    ("piranha",         0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,   1.5,  10, "meat",   "fish"),
    ("pufferfish",      0,0,1,0,0,1,0,1,1,0,1,1,0,1,0,0,     1,  10, "both",   "fish"),
    ("salmon",          0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,     5,   7, "meat",   "fish"),
    ("sardine",         0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,  0.05,   6, "meat",   "fish"),
    ("seahorse",        0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0, 0.008,   4, "meat",   "fish"),
    ("shark",           0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,   680,  30, "meat",   "fish"),
    ("sole",            0,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,   0.6,  12, "meat",   "fish"),
    ("stingray",        0,0,1,0,0,1,1,1,1,0,1,1,0,1,0,1,    50,  20, "meat",   "fish"),
    ("swordfish",       0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,   200,   9, "meat",   "fish"),
    ("tilapia",         0,0,1,0,0,1,0,1,1,0,0,1,0,1,1,0,   1.5,  10, "plants", "fish"),
    ("trout",           0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,0,     2,   7, "meat",   "fish"),
    ("tuna",            0,0,1,0,0,1,1,1,1,0,0,1,0,1,0,1,   250,  15, "meat",   "fish"),

    # ------------------------------ reptiles -----------------------------
    ("alligator",       0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,1,   360,  50, "meat",   "reptile"),
    ("anaconda",        0,0,0,0,0,1,1,1,1,1,0,0,0,1,0,1,    100,  30, "meat",  "reptile"),
    ("bearded dragon",  0,0,1,0,0,0,1,1,1,1,0,0,4,1,1,0,   0.5,  12, "both",   "reptile"),
    ("boa constrictor", 0,0,0,0,0,0,1,1,1,1,0,0,0,1,0,1,    27,  30, "meat",   "reptile"),
    ("caiman",          0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,1,    40,  40, "meat",   "reptile"),
    ("chameleon",       0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,   0.1,   7, "meat",   "reptile"),
    ("cobra",           0,0,1,0,0,0,1,1,1,1,1,0,0,1,0,1,     6,  20, "meat",   "reptile"),
    ("copperhead",      0,0,0,0,0,0,1,1,1,1,1,0,0,1,0,0,   0.3,  18, "meat",   "reptile"),
    ("crocodile",       0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,1,   500,  70, "meat",   "reptile"),
    ("garter snake",    0,0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,  0.15,   6, "meat",   "reptile"),
    ("gecko",           0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,  0.05,  10, "meat",   "reptile"),
    ("gila monster",    0,0,1,0,0,0,1,1,1,1,1,0,4,1,0,0,   0.7,  20, "meat",   "reptile"),
    ("horned lizard",   0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,  0.04,   8, "meat",   "reptile"),
    ("iguana",          0,0,1,0,0,0,0,1,1,1,0,0,4,1,0,1,     5,  20, "plants", "reptile"),
    ("komodo dragon",   0,0,1,0,0,0,1,1,1,1,1,0,4,1,0,1,    70,  30, "meat",   "reptile"),
    ("monitor lizard",  0,0,1,0,0,0,1,1,1,1,1,0,4,1,0,1,    20,  15, "meat",   "reptile"),
    ("python",          0,0,1,0,0,0,1,1,1,1,0,0,0,1,0,1,    55,  25, "meat",   "reptile"),
    ("rattlesnake",     0,0,0,0,0,0,1,1,1,1,1,0,0,1,0,1,     4,  20, "meat",   "reptile"),
    ("sea snake",       0,0,0,0,0,1,1,1,1,1,1,0,0,1,0,0,   1.5,  10, "meat",   "reptile"),
    ("sea turtle",      0,0,1,0,0,1,1,0,1,1,0,0,4,1,0,1,   140,  70, "both",   "reptile"),
    ("skink",           0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,  0.06,   8, "meat",   "reptile"),
    ("slowworm",        0,0,0,0,0,0,1,1,1,1,0,0,0,1,0,0,  0.02,  30, "meat",   "reptile"),
    ("snapping turtle", 0,0,1,0,0,1,1,0,1,1,0,0,4,1,0,1,    16,  45, "both",   "reptile"),
    ("taipan",          0,0,1,0,0,0,1,1,1,1,1,0,0,1,0,1,     3,  15, "meat",   "reptile"),
    ("terrapin",        0,0,1,0,0,1,1,0,1,1,0,0,4,1,1,0,   0.5,  30, "both",   "reptile"),
    ("tortoise",        0,0,1,0,0,0,0,0,1,1,0,0,4,1,0,1,   150, 100, "plants", "reptile"),
    ("tuatara",         0,0,1,0,0,0,1,1,1,1,0,0,4,1,0,0,     1,  90, "meat",   "reptile"),
    ("viper",           0,0,0,0,0,0,1,1,1,1,1,0,0,1,0,0,   0.5,  15, "meat",   "reptile"),

    # ----------------------------- amphibians ----------------------------
    ("axolotl",         0,0,1,0,0,1,1,1,1,1,0,0,4,1,1,0,   0.1,  12, "meat",   "amphibian"),
    ("bullfrog",        0,0,1,0,0,1,1,1,1,1,0,0,4,0,0,0,   0.5,   9, "meat",   "amphibian"),
    ("caecilian",       0,0,1,0,0,1,1,1,1,1,0,0,0,1,0,0,   0.1,  13, "meat",   "amphibian"),
    ("cane toad",       0,0,1,0,0,1,1,1,1,1,1,0,4,0,0,0,   1.4,  12, "meat",   "amphibian"),
    ("fire salamander", 0,0,1,0,0,1,1,1,1,1,1,0,4,1,0,0,  0.04,  25, "meat",   "amphibian"),
    ("frog",            0,0,1,0,0,1,1,1,1,1,0,0,4,0,0,0,  0.06,   8, "meat",   "amphibian"),
    ("hellbender",      0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,0,     2,  30, "meat",   "amphibian"),
    ("mudpuppy",        0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,0,   0.2,  20, "meat",   "amphibian"),
    ("newt",            0,0,1,0,0,1,1,1,1,1,1,0,4,1,0,0,  0.01,  15, "meat",   "amphibian"),
    ("olm",             0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,0,  0.02, 100, "meat",   "amphibian"),
    ("poison frog",     0,0,1,0,0,1,1,1,1,1,1,0,4,0,0,0, 0.003,  10, "meat",   "amphibian"),
    ("salamander",      0,0,1,0,0,1,1,1,1,1,0,0,4,1,0,0,  0.03,  20, "meat",   "amphibian"),
    ("siren",           0,0,1,0,0,1,1,1,1,1,0,0,2,1,0,0,   0.3,  25, "meat",   "amphibian"),
    ("spadefoot toad",  0,0,1,0,0,1,1,1,1,1,0,0,4,0,0,0,  0.03,  12, "meat",   "amphibian"),
    ("toad",            0,0,1,0,0,1,1,1,1,1,1,0,4,0,0,0,   0.1,  10, "meat",   "amphibian"),
    ("tree frog",       0,0,1,0,0,1,1,1,1,1,0,0,4,0,0,0,  0.01,   8, "meat",   "amphibian"),

    # ------------------------------ insects ------------------------------
    ("ant",             0,0,1,0,0,0,1,0,0,1,0,0,6,0,0,0, 5e-06,   3, "both",   "insect"),
    ("aphid",           0,0,0,0,1,0,0,0,0,1,0,0,6,0,0,0, 1e-06, 0.1, "plants", "insect"),
    ("assassin bug",    0,0,1,0,1,0,1,0,0,1,1,0,6,0,0,0, 3e-05,   1, "meat",   "insect"),
    ("bedbug",          0,0,1,0,0,0,1,0,0,1,0,0,6,0,0,0, 5e-06,   1, "meat",   "insect"),
    ("beetle",          0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.001,   2, "plants", "insect"),
    ("bumblebee",       1,0,1,0,1,0,0,0,0,1,1,0,6,0,0,0, 0.0005,  1, "plants", "insect"),
    ("butterfly",       1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.0005,  1, "plants", "insect"),
    ("cicada",          0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.002,  17, "plants", "insect"),
    ("cockroach",       0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.002,   1, "both",   "insect"),
    ("cricket",         0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.0007,  1, "both",   "insect"),
    ("damselfly",       0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 0.0003,  1, "meat",   "insect"),
    ("dragonfly",       0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 0.001,   1, "meat",   "insect"),
    ("earwig",          0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 0.0001,  1, "both",   "insect"),
    ("fire ant",        0,0,1,0,0,0,1,0,0,1,1,0,6,0,0,0, 6e-06,   5, "both",   "insect"),
    ("firefly",         0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 2e-05,   1, "meat",   "insect"),
    ("flea",            0,0,1,0,0,0,1,0,0,1,0,0,6,0,0,0, 2e-06, 0.3, "meat",   "insect"),
    ("fruit fly",       1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 2e-07, 0.1, "plants", "insect"),
    ("grasshopper",     0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.002,   1, "plants", "insect"),
    ("honeybee",        1,0,1,0,1,0,0,0,0,1,1,0,6,0,1,0, 0.0001,  1, "plants", "insect"),
    ("hornet",          1,0,1,0,1,0,1,0,0,1,1,0,6,0,0,0, 0.0005,  1, "both",   "insect"),
    ("housefly",        1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 1e-05, 0.1, "both",   "insect"),
    ("ladybug",         0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 2e-05,   1, "meat",   "insect"),
    ("locust",          0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.002,   1, "plants", "insect"),
    ("mantis",          0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 0.005,   1, "meat",   "insect"),
    ("mayfly",          0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 2e-05, 0.1, "plants", "insect"),
    ("mosquito",        0,0,1,0,1,0,1,0,0,1,0,0,6,0,0,0, 2e-06, 0.2, "meat",   "insect"),
    ("moth",            1,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.0003,  1, "plants", "insect"),
    ("silverfish",      0,0,1,0,0,0,0,0,0,1,0,0,6,0,0,0, 2e-05,   4, "plants", "insect"),
    ("stick insect",    0,0,1,0,0,0,0,0,0,1,0,0,6,0,1,0, 0.003,   2, "plants", "insect"),
    ("termite",         0,0,1,0,0,0,0,0,0,1,0,0,6,0,0,0, 3e-06,  15, "plants", "insect"),
    ("wasp",            1,0,1,0,1,0,1,0,0,1,1,0,6,0,0,0, 0.0002,  1, "both",   "insect"),
    ("weevil",          0,0,1,0,1,0,0,0,0,1,0,0,6,0,0,0, 0.0001,  1, "plants", "insect"),

    # --------------------------- invertebrates ---------------------------
    ("barnacle",        0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0, 0.005,   8, "meat",   "invertebrate"),
    ("black widow",     0,0,1,0,0,0,1,0,0,1,1,0,8,0,0,0, 0.001,   3, "meat",   "invertebrate"),
    ("brittle star",    0,0,1,0,0,1,1,0,0,0,0,0,5,0,0,0,  0.05,   5, "meat",   "invertebrate"),
    ("clam",            0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,   0.2,  30, "plants", "invertebrate"),
    ("coral",           0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,0,  0.01, 100, "meat",   "invertebrate"),
    ("crab",            0,0,1,0,0,1,1,0,0,0,0,0,4,0,0,0,   0.5,   8, "both",   "invertebrate"),
    ("crayfish",        0,0,1,0,0,1,1,0,0,0,0,0,6,0,0,0,  0.06,   5, "both",   "invertebrate"),
    ("cuttlefish",      0,0,1,0,0,1,1,0,0,0,0,0,8,0,0,1,     3,   2, "meat",   "invertebrate"),
    ("earthworm",       0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0, 0.004,   6, "plants", "invertebrate"),
    ("hermit crab",     0,0,1,0,0,1,0,0,0,0,0,0,8,0,1,0,  0.03,  15, "both",   "invertebrate"),
    ("horseshoe crab",  0,0,1,0,0,1,1,0,0,0,0,0,8,1,0,1,     2,  25, "meat",   "invertebrate"),
    ("jellyfish",       0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,0,     2,   1, "meat",   "invertebrate"),
    ("krill",           0,0,1,0,0,1,0,0,0,0,0,0,6,0,0,0, 0.002,   6, "plants", "invertebrate"),
    ("leech",           0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0, 0.002,   3, "meat",   "invertebrate"),
    ("limpet",          0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,  0.01,  15, "plants", "invertebrate"),
    ("lobster",         0,0,1,0,0,1,1,0,0,0,0,0,6,0,0,1,     2,  50, "both",   "invertebrate"),
    ("mussel",          0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,  0.03,  50, "plants", "invertebrate"),
    ("nautilus",        0,0,1,0,0,1,1,0,0,0,0,0,8,0,0,0,   1.3,  20, "meat",   "invertebrate"),
    ("octopus",         0,0,1,0,0,1,1,0,0,0,0,0,8,0,0,1,    10,   3, "meat",   "invertebrate"),
    ("oyster",          0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,   0.1,  20, "plants", "invertebrate"),
    ("scallop",         0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,   0.1,  20, "plants", "invertebrate"),
    ("scorpion",        0,0,0,0,0,0,1,0,0,1,1,0,8,1,0,0,  0.03,   8, "meat",   "invertebrate"),
    ("sea anemone",     0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,0,   0.2,  70, "meat",   "invertebrate"),
    ("sea cucumber",    0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,   0.5,  10, "plants", "invertebrate"),
    ("sea urchin",      0,0,1,0,0,1,0,0,0,0,1,0,0,0,0,0,   0.1,  30, "plants", "invertebrate"),
    ("shrimp",          0,0,1,0,0,1,0,0,0,0,0,0,6,0,0,0,  0.01,   3, "both",   "invertebrate"),
    ("slug",            0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,  0.01,   2, "plants", "invertebrate"),
    ("snail",           0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,  0.02,   5, "plants", "invertebrate"),
    ("squid",           0,0,1,0,0,1,1,0,0,0,0,0,8,0,0,1,     1,   2, "meat",   "invertebrate"),
    ("starfish",        0,0,1,0,0,1,1,0,0,0,0,0,5,0,0,0,   0.1,  35, "meat",   "invertebrate"),
    ("tarantula",       1,0,1,0,0,0,1,0,0,1,1,0,8,0,1,0,  0.06,  25, "meat",   "invertebrate"),
    ("tick",            0,0,1,0,0,0,1,0,0,1,0,0,8,0,0,0, 1e-05,   3, "meat",   "invertebrate"),
]


def main() -> None:
    out = Path(__file__).resolve().parents[1] / "data" / "animals.csv"
    out.parent.mkdir(parents=True, exist_ok=True)

    names = [r[0] for r in ROWS]
    duplicates = {n for n in names if names.count(n) > 1}
    assert not duplicates, f"duplicate animal name: {sorted(duplicates)}"
    for row in ROWS:
        assert len(row) == len(COLUMNS), (
            f"{row[0]} has {len(row)} values, expected {len(COLUMNS)}"
        )
        assert row[-2] in {"meat", "plants", "both"}, f"{row[0]} has a strange diet"

    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(COLUMNS)
        writer.writerows(ROWS)

    tally: dict[str, int] = {}
    for row in ROWS:
        tally[row[-1]] = tally.get(row[-1], 0) + 1
    summary = ", ".join(f"{k} {v}" for k, v in sorted(tally.items(), key=lambda t: -t[1]))

    print(f"Wrote {len(ROWS)} animals to {out}")
    print(f"  {summary}")


if __name__ == "__main__":
    main()
