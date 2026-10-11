"""
Step 1: Look at the animals before teaching anything.

Nothing clever happens here. We just count what we have and draw what each
family of animals usually looks like, so that later on we can tell whether the
computer learned something real or just got lucky.
"""

import numpy as np
import matplotlib.pyplot as plt

from common import CLUES, COLOURS, GROUPS, QUESTIONS, banner, caption, load, save

YES_NO = [c for c in CLUES if c != "legs"]


def how_many_of_each(df):
    counts = df["group"].value_counts().reindex(GROUPS)

    fig, ax = plt.subplots(figsize=(8, 4.6))
    bars = ax.bar(
        counts.index.astype(str),
        counts.to_numpy(),
        color=[COLOURS[g] for g in counts.index],
        width=0.68,
    )
    for bar, value in zip(bars, counts.to_numpy()):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + 1.2,
            str(value),
            ha="center",
            fontsize=11,
            fontweight="bold",
        )
    ax.set_title("How many animals of each kind are in the book")
    ax.set_ylabel("number of animals")
    ax.set_ylim(0, counts.max() * 1.18)
    ax.tick_params(axis="x", rotation=18)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "Mammals are the biggest pile. That matters later: a lazy guesser could say "
        '"mammal" every time and still be right about a third of the time.',
        y=-0.06,
    )
    return save(fig, "01_how_many_of_each.png")


def trait_fingerprints(df):
    """For every family, what share of its members answers yes to each clue?"""
    table = df.groupby("group", observed=True)[YES_NO].mean().reindex(GROUPS) * 100

    fig, ax = plt.subplots(figsize=(11, 4.8))
    im = ax.imshow(table.to_numpy(), cmap="YlGnBu", vmin=0, vmax=100, aspect="auto")

    ax.set_xticks(range(len(YES_NO)))
    ax.set_xticklabels([QUESTIONS[c].replace("it ", "") for c in YES_NO],
                       rotation=40, ha="right", fontsize=9)
    ax.set_yticks(range(len(GROUPS)))
    ax.set_yticklabels(GROUPS, fontsize=10)

    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            value = table.iat[i, j]
            if value >= 1:
                ax.text(j, i, f"{value:.0f}", ha="center", va="center", fontsize=7.5,
                        color="white" if value > 55 else "#333333")

    ax.set_title("The fingerprint of each animal family")
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    bar = fig.colorbar(im, ax=ax, shrink=0.8, pad=0.015)
    bar.set_label("% of that family answering yes", fontsize=9)
    caption(
        fig,
        "Read one row at a time. Mammals are a wall of milk and hair. Fish are the only "
        "row that does not breathe air. Insects and invertebrates are the only rows with "
        "no spine.",
        y=-0.30,
    )
    return save(fig, "02_family_fingerprints.png")


def the_oddballs(df):
    """Which animals look least like the rest of their own family?"""
    typical = df.groupby("group", observed=True)[YES_NO].mean()
    scores = []
    for _, row in df.iterrows():
        family = typical.loc[row["group"]]
        # how many traits disagree with what is normal for that family
        odd = float(np.abs(row[YES_NO].to_numpy(dtype=float) - (family >= 0.5).to_numpy(dtype=float)).sum())
        scores.append((row["animal"], str(row["group"]), odd))

    scores.sort(key=lambda t: t[2], reverse=True)
    top = scores[:14][::-1]
    names = [f"{n}  ({g})" for n, g, _ in top]
    values = [v for _, _, v in top]
    colors = [COLOURS[g] for _, g, _ in top]

    fig, ax = plt.subplots(figsize=(8.4, 6))
    ax.barh(names, values, color=colors, height=0.68)
    for y, value in enumerate(values):
        ax.text(value + 0.08, y, f"{value:.0f}", va="center", fontsize=9.5,
                fontweight="bold")
    ax.set_title("The animals that break their own family rules")
    ax.set_xlabel("number of traits that disagree with a typical member of its family")
    ax.set_xlim(0, max(values) * 1.16)
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "These are the animals that will trip up any rule based guesser. A platypus is a "
        "mammal that lays eggs. A whale is a mammal with no hair and fins. A penguin is a "
        "bird that cannot fly.",
        y=-0.05,
    )
    save(fig, "03_the_oddballs.png")
    return scores


def size_and_age(df):
    """The two extra facts, plotted against each other on a folded scale."""
    fig, ax = plt.subplots(figsize=(9.6, 6.8))

    for group in GROUPS:
        part = df[df["group"] == group]
        ax.scatter(part["weight_kg"], part["lifespan_years"], s=62,
                   c=COLOURS[group], label=group, edgecolors="white",
                   linewidths=0.9, alpha=0.9, zorder=3)

    for name in ["whale", "elephant", "tortoise", "mayfly", "hummingbird",
                 "olm", "aphid", "coral", "ostrich", "mouse", "greenland"]:
        hit = df[df["animal"] == name]
        if not hit.empty:
            row = hit.iloc[0]
            ax.annotate(name, (row["weight_kg"], row["lifespan_years"]),
                        xytext=(6, 5), textcoords="offset points",
                        fontsize=8.5, color="#3a3a3a", zorder=4)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("weight in kilograms (each step is ten times heavier)")
    ax.set_ylabel("typical lifespan in years")
    ax.set_title("Bigger animals live longer, mostly")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.13))
    ax.grid(alpha=0.2, which="both")
    ax.set_axisbelow(True)
    caption(
        fig,
        "Both scales are folded, so each step along an axis means ten times more. A mayfly "
        "and a blue whale differ by about eleven of those steps in weight. The upward drift "
        "is real but loose, and the animals sitting well above the crowd, like the tortoise "
        "and the olm, are the interesting ones.",
        y=-0.19,
    )
    return save(fig, "13_size_and_age.png")


def main():
    df = load()
    banner("Step 1: looking at the animals")
    print(f"  {len(df)} animals, {len(CLUES)} clues each, {df['group'].nunique()} families")

    how_many_of_each(df)
    trait_fingerprints(df)
    size_and_age(df)
    scores = the_oddballs(df)

    print("\n  Most unusual animals in the book:")
    for name, family, odd in scores[:5]:
        print(f"    {name:<14} ({family}) breaks {odd:.0f} of its family rules")


if __name__ == "__main__":
    main()
