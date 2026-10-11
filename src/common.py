"""Shared settings so every step looks and behaves the same way."""

import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "animals.csv"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"

# The clues. Everything except the animal name and the answer.
CLUES = [
    "hair", "feathers", "eggs", "milk", "airborne", "aquatic", "predator",
    "toothed", "backbone", "breathes", "venomous", "fins", "legs", "tail",
    "domestic", "catsize",
]

# Facts we know about each animal but deliberately keep away from the sorting model.
# They are there for a different question: how long does this animal live?
EXTRAS = ["weight_kg", "lifespan_years", "diet"]

# The seven groups, always in this order so colours never shuffle between charts.
GROUPS = [
    "mammal", "bird", "fish", "reptile", "amphibian", "insect", "invertebrate",
]

COLOURS = {
    "mammal": "#b5485d",
    "bird": "#e8963c",
    "fish": "#2f7fa8",
    "reptile": "#4fa06b",
    "amphibian": "#8a6bbf",
    "insect": "#6d4c33",
    "invertebrate": "#8b95a1",
}

# Plain English for each clue, used in charts and in the written rules.
QUESTIONS = {
    "hair": "it has hair or fur",
    "feathers": "it has feathers",
    "eggs": "it lays eggs",
    "milk": "it feeds its babies milk",
    "airborne": "it can fly",
    "aquatic": "it lives in water",
    "predator": "it hunts other animals",
    "toothed": "it has teeth",
    "backbone": "it has a spine",
    "breathes": "it breathes air",
    "venomous": "it is venomous",
    "fins": "it has fins",
    "legs": "how many legs it has",
    "tail": "it has a tail",
    "domestic": "people keep it as a pet or on farms",
    "catsize": "it is at least as big as a cat",
}

# The same clues again, but phrased as questions you would actually ask out loud.
ASK = {
    "hair": "Does it have hair or fur?",
    "feathers": "Does it have feathers?",
    "eggs": "Does it lay eggs?",
    "milk": "Does it feed its babies milk?",
    "airborne": "Can it fly?",
    "aquatic": "Does it live in water?",
    "predator": "Does it hunt other animals?",
    "toothed": "Does it have teeth?",
    "backbone": "Does it have a spine?",
    "breathes": "Does it breathe air?",
    "venomous": "Is it venomous?",
    "fins": "Does it have fins?",
    "legs": "How many legs does it have?",
    "tail": "Does it have a tail?",
    "domestic": "Is it kept as a pet or a farm animal?",
    "catsize": "Is it at least as big as a cat?",
}

SEED = 7

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "axes.edgecolor": "#c9c9c9",
    "axes.labelcolor": "#333333",
    "axes.titlesize": 15,
    "axes.titleweight": "bold",
    "axes.titlepad": 14,
    "text.color": "#333333",
    "xtick.color": "#555555",
    "ytick.color": "#555555",
    "font.size": 10,
    "figure.dpi": 130,
    "savefig.bbox": "tight",
    "axes.spines.top": False,
    "axes.spines.right": False,
})


def load() -> pd.DataFrame:
    """Read the animal table and put the groups in a fixed order."""
    df = pd.read_csv(DATA)
    df["group"] = pd.Categorical(df["group"], categories=GROUPS, ordered=True)
    return df


def save(fig, name: str) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  saved {path.relative_to(ROOT)}")
    return path


def caption(fig, text: str, y: float = -0.06, width: int = 104) -> None:
    """A grey note under a chart, wrapped so it never runs off the page."""
    fig.text(
        0.5, y, textwrap.fill(text, width),
        ha="center", va="top", fontsize=9, color="#666666", linespacing=1.5,
    )


def banner(text: str) -> None:
    print()
    print(text)
    print("=" * len(text))
