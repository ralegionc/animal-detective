"""
Step 2: Teach the computer, then make it explain itself.

The idea is the game of twenty questions. Show the computer part of the animal
book, let it work out which questions are worth asking, then hand it animals it
has never seen and check how often it gets them right.
"""

import json
import textwrap

import numpy as np
import matplotlib.pyplot as plt
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from common import (
    ASK, CLUES, COLOURS, GROUPS, OUTPUTS, QUESTIONS, SEED, banner, caption, load, save,
)

MAX_DEPTH = 5


# --------------------------------------------------------------------------
# turning a trained tree into sentences a person can read
# --------------------------------------------------------------------------

def leg_phrase(threshold: float, went_left: bool) -> str:
    """The leg count question, written out in words."""
    cut = int(np.floor(threshold))
    if went_left:
        return f"it has {cut} legs or fewer"
    return f"it has more than {cut} legs"


def rules_in_english(model, classes) -> list[str]:
    tree = model.tree_
    lines: list[str] = []

    def walk(node: int, depth: int, trail: list[str]) -> None:
        pad = "    " * depth
        if tree.children_left[node] == -1:
            counts = tree.value[node][0] * tree.n_node_samples[node]
            answer = classes[int(np.argmax(counts))]
            total = counts.sum()
            share = counts.max() / total * 100 if total else 0
            lines.append(
                f"{pad}=> say {answer.upper()}   "
                f"({int(round(total))} animals landed here, {share:.0f}% of them are {answer})"
            )
            return

        feature = CLUES[tree.feature[node]]
        threshold = tree.threshold[node]
        cut = int(np.floor(threshold))
        if feature == "legs":
            yes_label, no_label = f"MORE THAN {cut}", f"{cut} OR FEWER"
        else:
            yes_label, no_label = "YES", "NO"

        lines.append(f"{pad}{ASK[feature]}")
        lines.append(f"{pad}  {yes_label} ->")
        walk(tree.children_right[node], depth + 2, trail + [yes_label])
        lines.append(f"{pad}  {no_label} ->")
        walk(tree.children_left[node], depth + 2, trail + [no_label])

    walk(0, 0, [])
    return lines


def tree_to_dict(model, classes) -> dict:
    """A compact copy of the tree so the web demo can walk it without Python."""
    tree = model.tree_

    def node(i: int) -> dict:
        counts = (tree.value[i][0] * tree.n_node_samples[i]).round().astype(int)
        if tree.children_left[i] == -1:
            return {
                "leaf": True,
                "answer": classes[int(np.argmax(counts))],
                "n": int(tree.n_node_samples[i]),
                "counts": {c: int(v) for c, v in zip(classes, counts) if v},
            }
        return {
            "leaf": False,
            "clue": CLUES[tree.feature[i]],
            "question": ASK[CLUES[tree.feature[i]]],
            "threshold": float(tree.threshold[i]),
            "n": int(tree.n_node_samples[i]),
            "no": node(int(tree.children_left[i])),
            "yes": node(int(tree.children_right[i])),
        }

    return node(0)


def trace(model, classes, row) -> list[str]:
    """The exact questions the tree asked about one animal."""
    tree = model.tree_
    steps, node = [], 0
    while tree.children_left[node] != -1:
        feature = CLUES[tree.feature[node]]
        threshold = tree.threshold[node]
        value = float(row[feature])
        went_right = value > threshold
        if feature == "legs":
            said = leg_phrase(threshold, went_left=not went_right)
            steps.append(f"How many legs does it have? {int(value)}, so {said}")
        else:
            steps.append(f"{ASK[feature]} {'yes' if went_right else 'no'}")
        node = tree.children_right[node] if went_right else tree.children_left[node]
    counts = tree.value[node][0]
    steps.append(f"answer: {classes[int(np.argmax(counts))]}")
    return steps


# --------------------------------------------------------------------------
# charts
# --------------------------------------------------------------------------

def draw_tree(model, classes):
    """A hand drawn version of the tree, without any of the usual jargon."""
    tree = model.tree_
    nodes, leaf_slot = {}, [0]

    def layout(i, depth):
        if tree.children_left[i] == -1:
            x = leaf_slot[0]
            leaf_slot[0] += 1
        else:
            left = layout(int(tree.children_left[i]), depth + 1)
            right = layout(int(tree.children_right[i]), depth + 1)
            x = (left + right) / 2
        nodes[i] = (x, -depth)
        return x

    layout(0, 0)
    depth = max(-y for _, y in nodes.values())
    width = leaf_slot[0]

    fig, ax = plt.subplots(figsize=(2.15 * width + 3, 1.75 * depth + 3.2))

    def draw(i):
        x, y = nodes[i]
        if tree.children_left[i] == -1:
            counts = tree.value[i][0] * tree.n_node_samples[i]
            answer = classes[int(np.argmax(counts))]
            share = counts.max() / counts.sum() * 100
            label = f"{answer.upper()}\n{int(round(counts.sum()))} animals"
            if share < 99:
                label += f"\n{share:.0f}% of them"
            ax.text(x, y, label, ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color="white", zorder=3,
                    bbox=dict(boxstyle="round,pad=0.55", facecolor=COLOURS[answer],
                              edgecolor="none"))
            return

        clue = CLUES[tree.feature[i]]
        cut = int(np.floor(tree.threshold[i]))
        text = textwrap.fill(ASK[clue], 17)
        ax.text(x, y, text, ha="center", va="center", fontsize=10.5, zorder=3,
                color="#2c2c2c",
                bbox=dict(boxstyle="round,pad=0.55", facecolor="white",
                          edgecolor="#9aa3ab", linewidth=1.3))

        for child, label in (
            (int(tree.children_right[i]), "YES" if clue != "legs" else f"> {cut}"),
            (int(tree.children_left[i]), "NO" if clue != "legs" else f"<= {cut}"),
        ):
            cx, cy = nodes[child]
            ax.annotate(
                "", xy=(cx, cy + 0.30), xytext=(x, y - 0.30),
                arrowprops=dict(arrowstyle="-", color="#b9c0c6", linewidth=1.6,
                                shrinkA=6, shrinkB=6,
                                connectionstyle="arc3,rad=0"),
                zorder=1,
            )
            ax.text((x + cx) / 2, (y + cy) / 2, label, ha="center", va="center",
                    fontsize=9, fontweight="bold", color="#5a6570", zorder=2,
                    bbox=dict(boxstyle="round,pad=0.22", facecolor="white",
                              edgecolor="none"))
            draw(child)

    draw(0)
    ax.set_xlim(-0.8, width - 0.2)
    ax.set_ylim(-depth - 0.7, 0.7)
    ax.axis("off")
    ax.set_title("The questions the computer decided to ask, in order", fontsize=16,
                 pad=6)

    # The tree leans to one side, so the free corner becomes the reading guide.
    ax.text(
        0.015, 0.97,
        "How to read this\n\n"
        "Start at the box in the top corner.\n"
        "Answer the question about your\n"
        "animal, follow YES or NO, and keep\n"
        "going until you reach a coloured box.\n"
        "That box is the answer.\n\n"
        "Nobody wrote these questions. The\n"
        "computer tried all sixteen clues at\n"
        "every step and kept whichever one\n"
        "split the remaining animals most\n"
        "cleanly. It only needed five.",
        transform=ax.transAxes, va="top", ha="left", fontsize=11.5,
        color="#4a5560", linespacing=1.6,
        bbox=dict(boxstyle="round,pad=0.9", facecolor="#f4f6f7", edgecolor="#dde2e5"),
    )
    return save(fig, "04_the_question_tree.png")


def report_card(truth, guess, classes):
    matrix = confusion_matrix(truth, guess, labels=classes)
    fig, ax = plt.subplots(figsize=(7.4, 6.2))
    im = ax.imshow(matrix, cmap="Blues")

    ax.set_xticks(range(len(classes)), classes, rotation=35, ha="right")
    ax.set_yticks(range(len(classes)), classes)
    ax.set_xlabel("what the computer said", labelpad=10)
    ax.set_ylabel("what the animal really was", labelpad=10)
    ax.set_title("The report card")

    peak = matrix.max()
    for i in range(len(classes)):
        for j in range(len(classes)):
            if matrix[i, j]:
                ax.text(j, i, matrix[i, j], ha="center", va="center", fontsize=12,
                        fontweight="bold",
                        color="white" if matrix[i, j] > peak * 0.55 else "#333333")
    ax.spines[:].set_visible(False)
    ax.tick_params(length=0)
    caption(
        fig,
        "Numbers on the diagonal are correct answers. Anything off the diagonal is a "
        "mistake, and the position tells you exactly what it was confused with.",
        y=-0.02,
    )
    return save(fig, "05_report_card.png")


def which_clues_matter(model, forest):
    tree_score = model.feature_importances_
    forest_score = forest.feature_importances_
    order = np.argsort(forest_score)

    labels = [QUESTIONS[CLUES[i]] for i in order]
    y = np.arange(len(order))

    fig, ax = plt.subplots(figsize=(9, 6.4))
    ax.barh(y + 0.19, forest_score[order], height=0.38, color="#337ca0",
            label="a forest of 400 trees")
    ax.barh(y - 0.19, tree_score[order], height=0.38, color="#c1666b",
            label="the single tree above")
    ax.set_yticks(y, labels)
    ax.set_xlabel("how much this clue helped")
    ax.set_title("Which clues actually carry the answer")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "A single tree can only ask a handful of questions, so it leans hard on a few "
        "clues. Four hundred trees spread the credit around and give a fairer picture.",
        y=-0.04,
    )
    return save(fig, "06_which_clues_matter.png")


def best_first_question(X, y):
    """Score every clue on its own, as if it were the only question allowed."""
    scores = []
    for clue in CLUES:
        stump = DecisionTreeClassifier(max_depth=1, random_state=SEED)
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
        hit = cross_val_score(stump, X[[clue]], y, cv=folds).mean()
        scores.append((clue, hit * 100))

    scores.sort(key=lambda t: t[1])
    labels = [ASK[c] for c, _ in scores]
    values = [v for _, v in scores]
    best = scores[-1][0]

    fig, ax = plt.subplots(figsize=(9.2, 6.6))
    colours = ["#c8cfc9"] * len(scores)
    colours[-1] = COLOURS["mammal"]
    bars = ax.barh(labels, values, color=colours, height=0.68)
    for bar, value in zip(bars, values):
        ax.text(value + 0.7, bar.get_y() + bar.get_height() / 2, f"{value:.0f}%",
                va="center", fontsize=9.5)
    ax.axvline(31.0, color="#8a8a8a", linestyle="--", linewidth=1.2, zorder=0)
    ax.text(31.6, -0.9, 'guessing "mammal"', fontsize=9, color="#777777")
    ax.set_xlim(0, max(values) * 1.16)
    ax.set_xlabel("correct if this were the only question you were allowed")
    ax.set_title("If you could ask one question and nothing else")
    ax.grid(axis="x", alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        f"Every clue, scored alone. The winner is {ASK[best].lower()[:-1]}, and it is not "
        "close. This is exactly the calculation the computer runs at the top of the tree, "
        "and then it runs it again inside every pile it creates.",
        y=-0.04,
    )
    save(fig, "14_best_first_question.png")
    return scores


def how_many_questions(X, y):
    """Let the tree ask 1 question, then 2, then 3, and watch the curve flatten."""
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    depths = list(range(1, 13))
    means, spreads = [], []
    for depth in depths:
        hits = cross_val_score(
            DecisionTreeClassifier(max_depth=depth, random_state=SEED), X, y, cv=folds
        )
        means.append(hits.mean() * 100)
        spreads.append(hits.std() * 100)

    means_arr, spreads_arr = np.array(means), np.array(spreads)
    enough = next(d for d, m in zip(depths, means) if m >= max(means) - 1)

    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.fill_between(depths, means_arr - spreads_arr, means_arr + spreads_arr,
                    color=COLOURS["fish"], alpha=0.16, zorder=1)
    ax.plot(depths, means_arr, color=COLOURS["fish"], linewidth=2.4, zorder=3)
    ax.scatter(depths, means_arr, s=42, color=COLOURS["fish"], zorder=4,
               edgecolors="white", linewidths=1.2)
    ax.axvline(enough, color="#8a8a8a", linestyle="--", linewidth=1.2, zorder=0)
    ax.annotate(f"{enough} questions is\nas good as it gets",
                xy=(enough, means[enough - 1]), xytext=(enough + 1.4, means[0] + 12),
                fontsize=10, color="#555555",
                arrowprops=dict(arrowstyle="->", color="#999999"))

    ax.set_xticks(depths)
    ax.set_xlabel("how many questions the tree is allowed to ask")
    ax.set_ylabel("% correct on animals it had never seen")
    ax.set_title("How many questions do you actually need?")
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        f"A single question already gets you {means[0]:.0f}% right, because one question is "
        f"enough to pull out every mammal. By the fifth it is at {means[4]:.0f}% and the climb "
        "is over. Letting it ask twelve buys nothing, and every extra question is one more "
        "chance to memorise a quirk of this particular book instead of learning biology.",
        y=-0.07,
    )
    save(fig, "15_how_many_questions.png")
    return enough


def how_many_animals(X, y):
    """How much of the book does it need to read before it is any good?"""
    sizes = np.linspace(0.12, 1.0, 12)
    means, spreads = [], []
    for share in sizes:
        runs = []
        for seed in range(12):
            if share < 1.0:
                X_part, _, y_part, _ = train_test_split(
                    X, y, train_size=share, random_state=seed, stratify=y
                )
            else:
                X_part, y_part = X, y
            folds = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
            runs.append(cross_val_score(
                DecisionTreeClassifier(max_depth=MAX_DEPTH, random_state=SEED),
                X_part, y_part, cv=folds,
            ).mean())
        means.append(np.mean(runs) * 100)
        spreads.append(np.std(runs) * 100)

    counts = (sizes * len(X)).astype(int)
    means_arr, spreads_arr = np.array(means), np.array(spreads)

    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.fill_between(counts, means_arr - spreads_arr, means_arr + spreads_arr,
                    color=COLOURS["reptile"], alpha=0.16, zorder=1)
    ax.plot(counts, means_arr, color=COLOURS["reptile"], linewidth=2.4, zorder=3)
    ax.scatter(counts, means_arr, s=42, color=COLOURS["reptile"], zorder=4,
               edgecolors="white", linewidths=1.2)
    ax.set_xlabel("how many animals it was allowed to study")
    ax.set_ylabel("% correct on animals it had never seen")
    ax.set_title("How much of the book does it need to read?")
    ax.grid(alpha=0.25)
    ax.set_axisbelow(True)
    caption(
        fig,
        "Shaded band is the spread over twelve different random draws. Most of the learning "
        "happens early. Doubling the book from 140 animals to 277 moves the line by only a "
        "few points, which tells you the limit here is the sixteen clues, not the page count.",
        y=-0.07,
    )
    save(fig, "16_how_many_animals.png")
    return counts, means


def model_scoreboard(results):
    names = list(results)
    values = [results[n] * 100 for n in names]
    palette = ["#b0b0b0", "#c1666b", "#e09f3e", "#337ca0"]

    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    bars = ax.bar(names, values, color=palette[: len(names)], width=0.62)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 1.5, f"{value:.0f}%",
                ha="center", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 108)
    ax.set_ylabel("correct on animals it had never seen")
    ax.set_title("Does the clever method actually beat the dumb one?")
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.tick_params(axis="x", rotation=10)
    caption(
        fig,
        'The grey bar is the honest baseline: always answer "mammal". Any method that '
        "cannot beat it has learned nothing worth having.",
        y=-0.09,
    )
    return save(fig, "07_scoreboard.png")


# --------------------------------------------------------------------------

def main():
    df = load()
    X = df[CLUES]
    y = df["group"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=SEED, stratify=y
    )

    banner("Step 2: teaching the computer")
    print(f"  studied  {len(X_train)} animals")
    print(f"  tested on {len(X_test)} animals it had never seen")

    tree = DecisionTreeClassifier(max_depth=MAX_DEPTH, random_state=SEED)
    tree.fit(X_train, y_train)
    classes = list(tree.classes_)

    forest = RandomForestClassifier(n_estimators=400, random_state=SEED)
    forest.fit(X_train, y_train)

    linear = make_pipeline(
        StandardScaler(), LogisticRegression(max_iter=2000, random_state=SEED)
    )
    linear.fit(X_train, y_train)

    dummy = DummyClassifier(strategy="most_frequent")
    dummy.fit(X_train, y_train)

    contenders = {
        'always say "mammal"': dummy,
        f"one tree, {MAX_DEPTH} questions deep": tree,
        "a forest of 400 trees": forest,
        "a weighted score card": linear,
    }
    results = {}
    for name, model in contenders.items():
        results[name] = accuracy_score(y_test, model.predict(X_test))
        print(f"  {name:<34} {results[name] * 100:5.1f}% correct")

    # A single split can be lucky. Reshuffle five times and see if it holds.
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv = cross_val_score(
        DecisionTreeClassifier(max_depth=MAX_DEPTH, random_state=SEED), X, y, cv=folds
    )
    print(f"\n  Reshuffling the book 5 different ways, the tree scores "
          f"{cv.mean() * 100:.1f}% give or take {cv.std() * 100:.1f}")

    guess = tree.predict(X_test)

    draw_tree(tree, classes)
    report_card(y_test, guess, classes)
    which_clues_matter(tree, forest)
    model_scoreboard(results)

    single = best_first_question(X, y)
    print(f"\n  Best single question on its own: {ASK[single[-1][0]]} "
          f"({single[-1][1]:.0f}% correct with nothing else to go on)")
    print(f"  Worst single question:           {ASK[single[0][0]]} "
          f"({single[0][1]:.0f}%)")

    enough = how_many_questions(X, y)
    print(f"\n  Allowed more and more questions, it stops improving after {enough}.")

    counts, curve = how_many_animals(X, y)
    print(f"  Having read only {counts[0]} animals it already scores {curve[0]:.0f}%. "
          f"All {counts[-1]} gets it to {curve[-1]:.0f}%.")

    # ---- write out the human readable pieces ----
    OUTPUTS.mkdir(parents=True, exist_ok=True)

    lines = rules_in_english(tree, classes)
    rules_path = OUTPUTS / "the_rules_in_plain_english.txt"
    rules_path.write_text(
        "What the computer worked out, written as a game of twenty questions\n"
        "===================================================================\n"
        "Start at the top. Answer each question about your animal and follow the\n"
        "branch. Where the arrow appears, that is the computer's answer.\n\n"
        + "\n".join(lines) + "\n",
        encoding="utf-8",
    )
    print(f"\n  saved {rules_path.relative_to(rules_path.parents[1])}")

    (OUTPUTS / "tree_measured.json").write_text(
        json.dumps(tree_to_dict(tree, classes), indent=1), encoding="utf-8"
    )
    print("  saved outputs/tree_measured.json (the tree these scores describe)")

    (OUTPUTS / "detailed_scores.txt").write_text(
        classification_report(y_test, guess, zero_division=0), encoding="utf-8"
    )

    # ---- show the reasoning on a few famous troublemakers ----
    print("\n  Watching it think:")
    for name in ["platypus", "penguin", "whale", "tarantula"]:
        row = df.loc[df["animal"] == name].iloc[0]
        steps = trace(tree, classes, row)
        verdict = steps[-1].split(": ")[1]
        mark = "correct" if verdict == row["group"] else f"WRONG, it is a {row['group']}"
        print(f"\n    {name} ({mark})")
        for step in steps[:-1]:
            print(f"      - {step}")

    print()


if __name__ == "__main__":
    main()
