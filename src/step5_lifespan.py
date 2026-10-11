"""
Step 5: A different kind of question.

Everything so far has been sorting: put this animal in one of seven boxes. This
step asks for a number instead. Given what an animal looks like, how long is it
likely to live?

This is the same machinery pointed at a harder target, and it fails in a much
more interesting way.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.metrics import r2_score

from common import (
    CLUES, COLOURS, GROUPS, OUTPUTS, SEED, banner, caption, load, save,
)

FOLDS = KFold(n_splits=5, shuffle=True, random_state=SEED)


def folded(series):
    """Work in steps of ten, because a mayfly and a whale do not share a ruler."""
    return np.log10(series)


def size_alone(df):
    """The oldest idea in the field: big things live long."""
    X = folded(df[["weight_kg"]])
    y = folded(df["lifespan_years"])
    guess = cross_val_predict(LinearRegression(), X, y, cv=FOLDS)
    return guess, r2_score(y, guess)


def size_plus_clues(df):
    """Now hand it the sixteen yes and no answers as well."""
    X = pd.concat([folded(df[["weight_kg"]]), df[CLUES]], axis=1)
    y = folded(df["lifespan_years"])
    model = RandomForestRegressor(n_estimators=500, random_state=SEED, min_samples_leaf=2)
    guess = cross_val_predict(model, X, y, cv=FOLDS)
    model.fit(X, y)
    return guess, r2_score(y, guess), model


def guess_against_truth(df, guess, score):
    real = df["lifespan_years"].to_numpy()
    said = 10 ** guess

    fig, ax = plt.subplots(figsize=(8.6, 7.4))
    edge = [0.06, 140]
    ax.plot(edge, edge, color="#9aa3ab", linestyle="--", linewidth=1.3, zorder=1)
    ax.fill_between(edge, [e / 2 for e in edge], [e * 2 for e in edge],
                    color="#9aa3ab", alpha=0.11, zorder=0)

    for group in GROUPS:
        mask = (df["group"] == group).to_numpy()
        ax.scatter(real[mask], said[mask], s=58, c=COLOURS[group], label=group,
                   edgecolors="white", linewidths=0.9, alpha=0.9, zorder=3)

    ratio = said / real
    for i in np.argsort(np.abs(np.log10(ratio)))[-7:]:
        ax.annotate(df["animal"].iat[i], (real[i], said[i]),
                    xytext=(7, 4), textcoords="offset points",
                    fontsize=9, color="#3a3a3a", zorder=4)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(*edge)
    ax.set_ylim(*edge)
    ax.set_xlabel("how long it really lives, in years")
    ax.set_ylabel("how long the model guessed")
    ax.set_title("Guessing a number instead of a name")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.11))
    ax.grid(alpha=0.2, which="both")
    ax.set_axisbelow(True)
    caption(
        fig,
        "Every animal, guessed by a model that never saw it. The dashed line is a perfect "
        "answer and the shaded band is being wrong by up to a factor of two, which for "
        f"lifespans is close enough to be useful. It lands inside that band for most of the "
        "book, and the animals it names are the ones it cannot explain.",
        y=-0.17,
    )
    return save(fig, "18_guessing_a_lifespan.png")


def longer_than_their_size(df, guess):
    """Who outlives the prediction, and who dies young?"""
    real = folded(df["lifespan_years"]).to_numpy()
    gap = real - guess
    order = np.argsort(gap)
    picked = np.concatenate([order[:8], order[-8:]])

    labels, values, colours = [], [], []
    for i in picked:
        years = df["lifespan_years"].iat[i]
        said = 10 ** guess[i]
        labels.append(f"{df['animal'].iat[i]}   {years:g}y vs {said:.3g}y guessed")
        values.append(10 ** gap[i])
        colours.append(COLOURS[str(df["group"].iat[i])])

    fig, ax = plt.subplots(figsize=(9.6, 6.6))
    ax.barh(range(len(picked)), values, color=colours, height=0.7)
    ax.axvline(1, color="#6b6b6b", linewidth=1.3)
    ax.set_yticks(range(len(picked)), labels, fontsize=9.5)
    ax.set_xscale("log")
    ax.set_xlabel("how many times longer it lives than the model expected")
    ax.set_title("The animals that break the size rule")
    ax.grid(axis="x", alpha=0.25, which="both")
    ax.set_axisbelow(True)
    caption(
        fig,
        "Bars to the right of the line live longer than anything their size and shape should. "
        "Bars to the left die young. The right hand side is roughly a list of animals that "
        "are hard to eat: they are venomous, armoured, cave dwelling or simply very slow.",
        y=-0.05,
    )
    save(fig, "19_breaking_the_size_rule.png")
    return [(df["animal"].iat[i], 10 ** gap[i]) for i in picked[::-1][:6]]


def what_helped(model, columns):
    weight = model.feature_importances_
    order = np.argsort(weight)[-10:]
    pretty = {"weight_kg": "how heavy it is"}

    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    ax.barh(range(len(order)), weight[order] * 100, height=0.66,
            color=[COLOURS["amphibian"] if columns[i] == "weight_kg" else "#c8cfc9"
                   for i in order])
    ax.set_yticks(
        range(len(order)),
        [pretty.get(columns[i], columns[i].replace("_", " ")) for i in order],
        fontsize=10,
    )
    ax.set_xlabel("share of the decision, in percent")
    ax.set_title("What the lifespan model actually leans on")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "Weight does most of the work on its own. The yes and no clues fill in the rest by "
        "standing in for things nobody measured directly, like whether an animal has a shell "
        "or spends its life in cold water.",
        y=-0.07,
    )
    return save(fig, "20_what_helped_the_lifespan_model.png")


def main():
    df = load().reset_index(drop=True)

    banner("Step 5: guessing a number, not a name")
    print(f"  Lifespans in the book run from {df['lifespan_years'].min():g} years "
          f"to {df['lifespan_years'].max():g}.")

    plain, plain_score = size_alone(df)
    rich, rich_score, model = size_plus_clues(df)

    print(f"\n  Using weight alone, it explains {plain_score * 100:.0f}% of the differences.")
    print(f"  Adding the 16 clues takes that to {rich_score * 100:.0f}%.")

    ratio = 10 ** np.abs(folded(df["lifespan_years"]).to_numpy() - rich)
    within2 = (ratio <= 2).mean() * 100
    print(f"  Typical guess is off by a factor of {np.median(ratio):.2f}, and "
          f"{within2:.0f}% of animals land within a factor of two of the truth.")

    guess_against_truth(df, rich, rich_score)
    outliers = longer_than_their_size(df, rich)
    columns = ["weight_kg"] + CLUES
    what_helped(model, columns)

    print("\n  Living far longer than their size and shape suggest:")
    for name, times in outliers:
        print(f"    {name:<16} {times:.1f} times longer than expected")

    (OUTPUTS / "lifespan_scores.txt").write_text(
        "Predicting how long an animal lives\n"
        "===================================\n"
        f"animals            {len(df)}\n"
        f"weight only        {plain_score * 100:.1f}% of the variation explained\n"
        f"weight + 16 clues  {rich_score * 100:.1f}%\n"
        f"median error       a factor of {np.median(ratio):.2f}\n"
        f"within 2x          {within2:.1f}% of animals\n",
        encoding="utf-8",
    )
    print()


if __name__ == "__main__":
    main()
