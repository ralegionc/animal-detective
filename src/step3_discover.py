"""
Step 3: Hide the answers and see what the computer comes up with on its own.

In step 2 we told the computer which animal was a bird and which was a fish.
Here we tell it nothing at all. It only sees the sixteen yes and no columns,
with the family names torn off. The question is whether it rebuilds the
animal kingdom anyway.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, fcluster, linkage
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import adjusted_rand_score
from sklearn.preprocessing import StandardScaler

from common import CLUES, COLOURS, GROUPS, SEED, banner, caption, load, save

# A few animals worth pointing at on the map.
WORTH_LABELLING = [
    "platypus", "whale", "dolphin", "penguin", "ostrich", "bat", "fruit bat",
    "seahorse", "tarantula", "scorpion", "jellyfish", "octopus", "earthworm",
    "sea turtle", "python", "frog", "honeybee", "lion", "eagle", "shark",
]


def draw_map(df, coords, variance):
    fig, ax = plt.subplots(figsize=(10, 7.4))

    for group in GROUPS:
        mask = (df["group"] == group).to_numpy()
        ax.scatter(
            coords[mask, 0], coords[mask, 1],
            s=95, c=COLOURS[group], label=group,
            edgecolors="white", linewidths=1.1, alpha=0.92, zorder=3,
        )

    for i, name in enumerate(df["animal"]):
        if name in WORTH_LABELLING:
            ax.annotate(
                name, (coords[i, 0], coords[i, 1]),
                xytext=(7, 6), textcoords="offset points",
                fontsize=8.5, color="#3a3a3a", zorder=4,
            )

    ax.set_title("Every animal placed on one map, by how similar they are")
    ax.set_xlabel(f"direction 1 ({variance[0] * 100:.0f}% of the differences)")
    ax.set_ylabel(f"direction 2 ({variance[1] * 100:.0f}% of the differences)")
    ax.legend(frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    ax.grid(alpha=0.2)
    ax.set_axisbelow(True)
    caption(
        fig,
        "Sixteen columns squashed down to two so it fits on a page. Animals that answered "
        "the same way sit close together. Nobody told the computer the colours: those were "
        "painted on afterwards to check the seating plan.",
        y=-0.16,
    )
    return save(fig, "08_the_animal_map.png")


def draw_family_tree(df, scaled):
    links = linkage(scaled, method="ward")

    fig, ax = plt.subplots(figsize=(9.5, 17))
    # Every branch the same neutral grey, so the only colour on the chart is the
    # real family of each animal. That is what makes the blocks readable.
    dendrogram(
        links,
        labels=df["animal"].tolist(),
        orientation="right",
        link_color_func=lambda _: "#a8b0b6",
        ax=ax,
    )
    lookup = dict(zip(df["animal"], df["group"].astype(str)))
    for label in ax.get_ymajorticklabels():
        label.set_color(COLOURS[lookup[label.get_text()]])
        label.set_fontsize(8.5)

    ax.set_title("The family tree the computer drew\nwithout being told any families",
                 fontsize=15, pad=16)
    ax.set_xlabel("how different two branches are")
    ax.spines[:].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    caption(
        fig,
        "Name colours are the real answer, added afterwards. Blocks of one colour mean the "
        "computer found a real family purely from yes and no answers.",
        y=0.055,
    )
    save(fig, "09_computer_family_tree.png")
    return links


def compare(df, labels, name, filename, note):
    """Cross tabulate what the computer invented against the real answer."""
    table = (
        df.assign(cluster=labels)
        .pivot_table(index="group", columns="cluster", aggfunc="size",
                     fill_value=0, observed=True)
        .reindex(GROUPS)
        .fillna(0)
        .astype(int)
    )

    fig, ax = plt.subplots(figsize=(8, 5.4))
    ax.imshow(table.to_numpy(), cmap="Purples")
    ax.set_xticks(range(table.shape[1]), [f"pile {c + 1}" for c in table.columns])
    ax.set_yticks(range(len(GROUPS)), GROUPS)
    ax.set_xlabel("the piles the computer made up", labelpad=10)
    ax.set_ylabel("the real family", labelpad=10)
    ax.set_title(name)

    peak = table.to_numpy().max()
    for i in range(table.shape[0]):
        for j in range(table.shape[1]):
            value = table.iat[i, j]
            if value:
                ax.text(j, i, value, ha="center", va="center", fontsize=12,
                        fontweight="bold",
                        color="white" if value > peak * 0.55 else "#333333")
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    caption(fig, note, y=-0.05)
    save(fig, filename)
    return table


def closest_relatives(df, scaled):
    """For each animal, which other animal answered most like it?"""
    gaps = ((scaled[:, None, :] - scaled[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(gaps, np.inf)
    nearest = gaps.argmin(1)

    names = df["animal"].tolist()
    families = df["group"].astype(str).tolist()
    pairs = [(names[i], names[j], families[i], families[j], gaps[i, j])
             for i, j in enumerate(nearest)]

    crossed = [p for p in pairs if p[2] != p[3]]
    crossed.sort(key=lambda p: p[4])
    same_family = sum(1 for p in pairs if p[2] == p[3]) / len(pairs) * 100

    show = crossed[:12][::-1]
    labels = [f"{a}  ->  {b}" for a, b, _, _, _ in show]

    fig, ax = plt.subplots(figsize=(9, 5.8))
    for pos, (_, _, fa, fb, _) in enumerate(show):
        ax.barh(pos, 0.5, height=0.66, color=COLOURS[fa], left=0)
        ax.barh(pos, 0.5, height=0.66, color=COLOURS[fb], left=0.5)
        ax.text(0.25, pos, fa, ha="center", va="center", color="white",
                fontsize=9.5, fontweight="bold")
        ax.text(0.75, pos, fb, ha="center", va="center", color="white",
                fontsize=9.5, fontweight="bold")
    ax.set_yticks(range(len(show)), labels, fontsize=10)
    ax.set_xticks([])
    ax.set_xlim(0, 1)
    ax.set_title("Animals whose closest match is in a different family")
    ax.spines[:].set_visible(False)
    caption(
        fig,
        f"For every animal we found the one that answered the sixteen questions most like "
        f"it. {same_family:.0f}% of the time that partner is in the same real family, which "
        "nobody told the computer. These are the pairs where it is not, and each one is a "
        "case of evolution arriving at the same shape twice.",
        y=-0.04,
    )
    save(fig, "17_closest_relatives.png")
    return same_family, crossed


def main():
    df = load()
    scaled = StandardScaler().fit_transform(df[CLUES])

    banner("Step 3: taking the answers away")
    print("  The computer now sees 16 columns of yes and no, and nothing else.")

    flat = PCA(n_components=2, random_state=SEED)
    coords = flat.fit_transform(scaled)
    draw_map(df, coords, flat.explained_variance_ratio_)

    links = draw_family_tree(df, scaled)

    # Seven piles, because there are seven real families. The computer is not told that.
    kmeans = KMeans(n_clusters=7, n_init=25, random_state=SEED).fit(scaled)
    tree_cut = fcluster(links, t=7, criterion="maxclust") - 1

    kmeans_score = adjusted_rand_score(df["group"].astype(str), kmeans.labels_)
    cut_score = adjusted_rand_score(df["group"].astype(str), tree_cut)

    compare(
        df, kmeans.labels_,
        "Did it rediscover the animal kingdom?",
        "10_did_it_rediscover_biology.png",
        "One tight block per row would be a perfect rediscovery. The blur is where "
        "biology and yes-or-no answers disagree.",
    )

    print(f"\n  Agreement with real biology (1.0 would be perfect, 0.0 would be random):")
    print(f"    making 7 piles by similarity   {kmeans_score:.2f}")
    print(f"    cutting the family tree at 7   {cut_score:.2f}")

    # Which real family gets split up or merged the most?
    table = (
        df.assign(cluster=kmeans.labels_)
        .pivot_table(index="group", columns="cluster", aggfunc="size",
                     fill_value=0, observed=True)
        .reindex(GROUPS).fillna(0)
    )
    same_family, crossed = closest_relatives(df, scaled)
    print(f"\n  Nearest neighbour check: {same_family:.0f}% of animals have their closest "
          f"match inside their own real family.")
    print("  The closest matches that cross a family line:")
    for a, b, fa, fb, _ in crossed[:5]:
        print(f"    {a} ({fa}) looks most like {b} ({fb})")

    print("\n  How cleanly each family survived:")
    for group in GROUPS:
        row = table.loc[group].to_numpy()
        cleanest = row.max() / row.sum() * 100
        piles = int((row > 0).sum())
        print(f"    {group:<13} {cleanest:5.0f}% of them ended up together, "
              f"spread over {piles} pile(s)")
    print()


if __name__ == "__main__":
    main()
