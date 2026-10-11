"""
Step 4: Put the detective to work.

Now the computer studies all 131 animals, and we hand it creatures that were
never in the book at all. Then we do something more interesting: we lie to it,
one clue at a time, and watch which single lie makes it change its mind.
"""

import json

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

from common import ASK, CLUES, COLOURS, OUTPUTS, QUESTIONS, SEED, banner, caption, load, save
from step2_learn import MAX_DEPTH, trace, tree_to_dict

# Real animals kept out of the book on purpose, plus one creature that does not exist.
# name, hair, feathers, eggs, milk, airborne, aquatic, predator, toothed,
# backbone, breathes, venomous, fins, legs, tail, domestic, catsize, truth
MYSTERIES = [
    ("snow leopard",   1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 4, 1, 0, 1, "mammal"),
    ("okapi",          1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 4, 1, 0, 1, "mammal"),
    ("kookaburra",     0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 2, 1, 0, 0, "bird"),
    ("roadrunner",     0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 2, 1, 0, 0, "bird"),
    # Both of these are fish that gulp air at the surface, which is meant to be a trap.
    ("electric eel",   0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, "fish"),
    ("arapaima",       0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, "fish"),
    ("thorny devil",   0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 4, 1, 0, 0, "reptile"),
    ("boomslang",      0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, "reptile"),
    # A toothless frog that carries its young in its back.
    ("surinam toad",   0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 4, 0, 0, 0, "amphibian"),
    ("atlas moth",     1, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 0, 6, 0, 0, 0, "insect"),
    ("water strider",  0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 6, 0, 0, 0, "insect"),
    ("vampire squid",  0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 8, 0, 0, 0, "invertebrate"),
    # Not a real animal. A furry, feathered, flying, egg laying thing with eight legs.
    ("the zorblax",    1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 8, 1, 0, 1, "does not exist"),
]


def confidence_chart(names, truths, guesses, probabilities, classes):
    ok = [g == t for g, t in zip(guesses, truths)]
    fig, ax = plt.subplots(figsize=(9.4, 5.6))

    y = np.arange(len(names))[::-1]
    for i, (name, guess, probs) in enumerate(zip(names, guesses, probabilities)):
        share = probs.max() * 100
        ax.barh(y[i], share, color=COLOURS.get(guess, "#9b9b9b"), height=0.62,
                alpha=0.92)
        ax.text(share + 1.5, y[i], f'"{guess}"  {share:.0f}% sure',
                va="center", fontsize=9.5)

    labels = [
        f"{n}  {'ok' if good else 'MISS'}" for n, good in zip(names, ok)
    ]
    ax.set_yticks(y, labels, fontsize=10)
    for tick, good in zip(ax.get_yticklabels(), ok):
        tick.set_color("#3a7d44" if good else "#b23a48")
    ax.set_xlim(0, 150)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("how sure the detective was")
    ax.set_title("Ten creatures the detective had never seen")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "The zorblax is not a real animal. The detective still answers with total "
        "confidence, because nothing in its training ever taught it to say "
        '"I have no idea". That is worth remembering about every model of this kind.',
        y=-0.05,
    )
    return save(fig, "11_mystery_creatures.png")


def what_if_we_lied(model, df, classes, animal="lion"):
    """Flip one clue at a time and see whether the answer survives."""
    row = df.loc[df["animal"] == animal].iloc[0]
    base = row[CLUES].to_frame().T.astype(float)
    original = model.predict(base)[0]

    flipped_to, changed = [], []
    for i, clue in enumerate(CLUES):
        altered = base.copy()
        altered.iloc[0, i] = 6 if clue == "legs" else 1 - altered.iloc[0, i]
        answer = model.predict(altered)[0]
        flipped_to.append(answer)
        changed.append(answer != original)

    order = np.argsort(changed)
    fig, ax = plt.subplots(figsize=(9.4, 5.8))
    fig.subplots_adjust(bottom=0.05, top=0.92)
    y = np.arange(len(CLUES))
    for pos, i in enumerate(order):
        clue = CLUES[i]
        did_change = changed[i]
        ax.barh(pos, 1, height=0.66,
                color=COLOURS.get(flipped_to[i], "#d8d8d8") if did_change else "#e8e8e8")
        text = (f'now says "{flipped_to[i]}"' if did_change
                else f'still says "{original}"')
        ax.text(0.02, pos, text, va="center", fontsize=9.5,
                color="white" if did_change else "#777777",
                fontweight="bold" if did_change else "normal")

    ax.set_yticks(y, [QUESTIONS[CLUES[i]] for i in order], fontsize=9.5)
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.set_title(f'One lie at a time: what breaks the "{animal}" answer?')
    ax.spines[:].set_visible(False)
    caption(
        fig,
        f"Sixteen copies of a {animal}, each with exactly one fact changed. Grey means the "
        "detective did not even blink. Only the coloured rows matter to it, and everything "
        "else is decoration.",
        y=-0.03,
    )
    save(fig, "12_one_lie_at_a_time.png")
    return original, [CLUES[i] for i in range(len(CLUES)) if changed[i]]


def how_wrong_can_you_be(model, df, rounds=200):
    """Corrupt a few facts at random and see when the detective falls over."""
    truth = df["group"].astype(str).to_numpy()
    base = df[CLUES].to_numpy(dtype=float)
    rng = np.random.default_rng(SEED)
    flippable = [i for i, c in enumerate(CLUES) if c != "legs"]

    lies = list(range(0, 9))
    means, spreads = [], []
    for how_many in lies:
        runs = []
        for _ in range(rounds if how_many else 1):
            spoiled = base.copy()
            for row in range(len(spoiled)):
                for col in rng.choice(flippable, size=how_many, replace=False):
                    spoiled[row, col] = 1 - spoiled[row, col]
            frame = pd.DataFrame(spoiled, columns=CLUES)
            runs.append((model.predict(frame) == truth).mean())
        means.append(np.mean(runs) * 100)
        spreads.append(np.std(runs) * 100)

    means_arr, spreads_arr = np.array(means), np.array(spreads)
    cost_of_one = means[0] - means[1]

    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.fill_between(lies, means_arr - spreads_arr, means_arr + spreads_arr,
                    color=COLOURS["mammal"], alpha=0.16, zorder=1)
    ax.plot(lies, means_arr, color=COLOURS["mammal"], linewidth=2.4, zorder=3)
    ax.scatter(lies, means_arr, s=42, color=COLOURS["mammal"], zorder=4,
               edgecolors="white", linewidths=1.2)
    ax.axhline(31, color="#8a8a8a", linestyle="--", linewidth=1.2, zorder=0)
    ax.text(0.1, 33, 'guessing "mammal" every time', fontsize=9, color="#777777")

    ax.set_xticks(lies)
    ax.set_ylim(0, 102)
    ax.set_xlabel("how many of the fifteen yes-or-no facts were wrong")
    ax.set_ylabel("% still identified correctly")
    ax.set_title("How much can you get wrong before it stops working?")
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        f"Every animal in the book, with facts flipped at random before handing it over. "
        f"Getting a single one of the fifteen wrong costs {cost_of_one:.0f} points. Three "
        "wrong and it is barely better than a coin flip. This is the bill for a model that "
        "only asks five questions: it has no spare evidence to fall back on, so damaging "
        "any question it relies on is close to fatal.",
        y=-0.07,
    )
    save(fig, "21_how_wrong_can_you_be.png")
    return lies, means, cost_of_one


def main():
    df = load()
    X, y = df[CLUES], df["group"].astype(str)

    banner("Step 4: the detective goes to work")

    detective = DecisionTreeClassifier(max_depth=MAX_DEPTH, random_state=SEED)
    detective.fit(X, y)
    classes = list(detective.classes_)
    print(f"  Studied all {len(df)} animals in the book.")

    names = [m[0] for m in MYSTERIES]
    truths = [m[-1] for m in MYSTERIES]
    features = pd.DataFrame([m[1:-1] for m in MYSTERIES],
                            columns=CLUES, dtype=float)

    guesses = detective.predict(features)
    probabilities = detective.predict_proba(features)

    print("\n  Creatures that were never in the book:")
    for name, truth, guess in zip(names, truths, guesses):
        mark = "correct" if guess == truth else f"said {guess}, really a {truth}"
        print(f"    {name:<17} -> {guess:<13} {mark}")

    hits = sum(g == t for g, t in zip(guesses, truths))
    real = sum(t != "does not exist" for t in truths)
    print(f"\n  {hits} out of {real} real newcomers identified correctly.")

    confidence_chart(names, truths, guesses, probabilities, classes)

    print("\n  Watching it reason about the zorblax, which is not a real animal:")
    zorblax = df.iloc[0].copy()
    for clue, value in zip(CLUES, MYSTERIES[-1][1:-1]):
        zorblax[clue] = value
    for step in trace(detective, classes, zorblax):
        print(f"    - {step}")

    verdict, breakers = what_if_we_lied(detective, df, classes, animal="lion")
    print(f"\n  A lion is called a {verdict}. Of the 16 facts we have about it, only "
          f"{len(breakers)} can change that answer on its own:")
    for clue in breakers:
        print(f"    - {ASK[clue]}")
    print("  Every other fact could be a lie and the detective would not notice.")

    lies, survived, cost_of_one = how_wrong_can_you_be(detective, df)
    print("\n  Feeding it deliberately corrupted facts:")
    for n in [0, 1, 2, 3, 5, 8]:
        print(f"    {n} facts wrong -> {survived[lies.index(n)]:5.1f}% still correct")
    print(f"  One wrong answer out of fifteen already costs it {cost_of_one:.0f} points. "
          f"A short tree is easy to read and easy to break.")

    (OUTPUTS / "tree.json").write_text(
        json.dumps(tree_to_dict(detective, classes), indent=1), encoding="utf-8"
    )
    print("\n  saved outputs/tree.json (the finished detective, used by the web demo)")
    print()


if __name__ == "__main__":
    main()
