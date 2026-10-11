"""
Build the interactive demo page.

The page carries the finished model and the whole animal book inside it, so it
works by opening the file. No server, no internet, no Python.

Two things live on the page:

  1. The key. Describe a creature and the trained tree names its family.
  2. The game. You think of an animal and the page works out which one, by
     choosing each question the same way the tree was built: take whichever
     question splits the animals still in play most evenly.

The look borrows from a naturalist's specimen sheet, because the thing the model
produced has a real name in biology: a dichotomous key.
"""

import json

import pandas as pd

from common import ASK, CLUES, COLOURS, DATA, OUTPUTS, ROOT

# Animals offered as one click presets. The zorblax is not real, which is the point.
PRESETS = ["lion", "penguin", "platypus", "shark", "honeybee", "octopus", "frog"]
ZORBLAX = dict(zip(
    CLUES,
    [1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 8, 1, 0, 1],
))

LEG_CHOICES = [0, 2, 4, 5, 6, 8]

PAGE = """<title>The Animal Detective</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Mono:wght@400;500&family=Public+Sans:wght@400;500;600&display=swap">
<style>
  :root {
    --paper: #ecefe9;
    --card: #f9fbf7;
    --sunk: #e3e8df;
    --ink: #1b211c;
    --soft: #67736a;
    --line: #d3dbd0;
    --accent: #46684f;
    --accent-ink: #ffffff;
    --shadow: 0 1px 1px rgba(27,33,28,.04), 0 10px 26px rgba(27,33,28,.07);

    --display: "Fraunces", Georgia, "Times New Roman", serif;
    --body: "Public Sans", -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #131714;
      --card: #1c211d;
      --sunk: #171c18;
      --ink: #e7ece7;
      --soft: #96a298;
      --line: #2c332e;
      --accent: #8fb897;
      --accent-ink: #131714;
      --shadow: 0 1px 1px rgba(0,0,0,.4), 0 10px 26px rgba(0,0,0,.3);
    }
  }
  :root[data-theme="dark"] {
    --paper: #131714;
    --card: #1c211d;
    --sunk: #171c18;
    --ink: #e7ece7;
    --soft: #96a298;
    --line: #2c332e;
    --accent: #8fb897;
    --accent-ink: #131714;
    --shadow: 0 1px 1px rgba(0,0,0,.4), 0 10px 26px rgba(0,0,0,.3);
  }

  body {
    background: var(--paper);
    color: var(--ink);
    font-family: var(--body);
    font-size: 15px;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }
  .sheet { max-width: 1080px; margin: 0 auto; padding: 46px 24px 72px; }

  .eyebrow {
    font-family: var(--mono);
    font-size: 11.5px;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--soft);
  }

  header { border-bottom: 2px solid var(--ink); padding-bottom: 22px; }
  h1 {
    font-family: var(--display);
    font-optical-sizing: auto;
    font-weight: 600;
    font-size: clamp(34px, 5.6vw, 54px);
    line-height: 1.02;
    letter-spacing: -.018em;
    text-wrap: balance;
    margin: 10px 0 12px;
  }
  header p { margin: 0; color: var(--soft); max-width: 63ch; }
  header p strong { color: var(--ink); font-weight: 500; }

  /* ---- the two modes ---- */
  .modes { display: flex; gap: 0; margin: 26px 0 30px; border-bottom: 1px solid var(--line); }
  .mode {
    font-family: var(--body); font-size: 15px; color: var(--soft);
    background: transparent; border: none; border-bottom: 2px solid transparent;
    padding: 9px 2px; margin-right: 26px; cursor: pointer;
  }
  .mode.on { color: var(--ink); border-bottom-color: var(--accent); font-weight: 600; }
  .mode:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; }

  .presets {
    display: flex; flex-wrap: wrap; gap: 7px;
    align-items: baseline; margin: 0 0 28px;
  }
  .presets .eyebrow { margin-right: 6px; }
  .chip {
    font-family: var(--body); font-size: 13.5px; color: var(--ink);
    background: transparent; border: 1px solid var(--line);
    padding: 5px 13px; cursor: pointer; border-radius: 2px;
    transition: border-color .15s, color .15s;
  }
  .chip:hover { border-color: var(--accent); color: var(--accent); }
  .chip.invented { border-style: dashed; color: var(--soft); }
  .chip:focus-visible, .toggle:focus-visible, .legs button:focus-visible {
    outline: 2px solid var(--accent); outline-offset: 2px;
  }

  .columns {
    display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(0, 1fr);
    gap: 30px; align-items: start;
  }
  @media (max-width: 840px) { .columns { grid-template-columns: 1fr; gap: 26px; } }

  .col > .eyebrow { display: block; padding-bottom: 9px; border-bottom: 1px solid var(--ink); }

  /* ---- the trait checklist, set like a field form ---- */
  .trait {
    display: flex; align-items: center; justify-content: space-between;
    gap: 14px; padding: 8px 0; border-bottom: 1px solid var(--line);
  }
  .trait label { cursor: pointer; flex: 1; }
  .toggle {
    appearance: none; margin: 0; flex: none; cursor: pointer;
    width: 42px; height: 23px; border-radius: 2px;
    background: var(--sunk); border: 1px solid var(--line);
    position: relative; transition: background .16s, border-color .16s;
  }
  .toggle::after {
    content: ""; position: absolute; inset: 2px auto 2px 2px;
    width: 17px; background: var(--soft); border-radius: 1px;
    transition: transform .16s, background .16s;
  }
  .toggle:checked { background: var(--accent); border-color: var(--accent); }
  .toggle:checked::after { transform: translateX(19px); background: var(--accent-ink); }

  .legs { display: flex; gap: 4px; }
  .legs button {
    font-family: var(--mono); font-size: 12.5px;
    width: 28px; height: 26px; cursor: pointer; border-radius: 2px;
    background: transparent; color: var(--soft); border: 1px solid var(--line);
  }
  .legs button.on {
    background: var(--accent); border-color: var(--accent); color: var(--accent-ink);
  }

  /* ---- the determination ---- */
  .determination {
    padding: 26px 24px 24px; border-radius: 3px; margin-bottom: 26px;
    color: #fff; transition: background .25s;
  }
  .determination .eyebrow { color: rgba(255,255,255,.78); }
  .determination .name {
    font-family: var(--display); font-weight: 700;
    font-size: 44px; line-height: 1.02; letter-spacing: -.02em;
    margin: 6px 0 10px; text-transform: lowercase;
  }
  .determination .basis {
    font-size: 14px; color: rgba(255,255,255,.9); max-width: 42ch;
    font-variant-numeric: tabular-nums;
  }

  ol.key { list-style: none; padding: 0; margin: 0; counter-reset: rung; }
  ol.key li {
    position: relative; padding: 11px 0 11px 36px;
    border-bottom: 1px solid var(--line); font-size: 14.5px;
  }
  ol.key li::before {
    counter-increment: rung; content: counter(rung);
    position: absolute; left: 0; top: 12px;
    font-family: var(--mono); font-size: 12px; color: var(--soft);
  }
  .verdict-word { font-family: var(--mono); font-size: 13px; font-weight: 500; }
  .verdict-word.yes { color: var(--accent); }
  .verdict-word.no { color: var(--soft); }

  /* ---- the guessing game ---- */
  .game { display: grid; grid-template-columns: minmax(0,1.1fr) minmax(0,1fr); gap: 30px; align-items: start; }
  @media (max-width: 840px) { .game { grid-template-columns: 1fr; gap: 26px; } }

  .ask {
    background: var(--card); border: 1px solid var(--line); border-radius: 3px;
    padding: 30px 26px 26px; box-shadow: var(--shadow);
  }
  .ask .counter { font-family: var(--mono); font-size: 12px; color: var(--soft); letter-spacing: .08em; }
  .ask .question {
    font-family: var(--display); font-weight: 600;
    font-size: clamp(24px, 3.4vw, 32px); line-height: 1.16;
    letter-spacing: -.015em; text-wrap: balance; margin: 10px 0 22px;
  }
  .answers { display: flex; flex-wrap: wrap; gap: 9px; }
  .answers button {
    font-family: var(--body); font-size: 15px; cursor: pointer;
    padding: 10px 24px; border-radius: 2px;
    border: 1px solid var(--accent); background: transparent; color: var(--accent);
    transition: background .14s, color .14s;
  }
  .answers button:hover { background: var(--accent); color: var(--accent-ink); }
  .answers button:focus-visible { outline: 2px solid var(--ink); outline-offset: 2px; }
  .answers button.quiet { border-color: var(--line); color: var(--soft); }
  .answers button.quiet:hover { background: var(--sunk); color: var(--ink); }

  .narrowing { margin-top: 24px; }
  .bar { height: 7px; background: var(--sunk); border-radius: 2px; overflow: hidden; }
  .bar span { display: block; height: 100%; background: var(--accent); transition: width .3s; }
  .remaining {
    margin-top: 12px; font-size: 13.5px; color: var(--soft); line-height: 1.75;
  }
  .remaining b { color: var(--ink); font-weight: 600; }

  .asked { list-style: none; padding: 0; margin: 0; }
  .asked li {
    display: flex; justify-content: space-between; gap: 14px;
    padding: 9px 0; border-bottom: 1px solid var(--line); font-size: 14px;
  }
  .asked .cut { font-family: var(--mono); font-size: 12px; color: var(--soft); flex: none; }

  footer {
    margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--line);
    color: var(--soft); font-size: 14px; max-width: 72ch;
  }
  footer strong { color: var(--ink); font-weight: 600; }
  code {
    font-family: var(--mono); font-size: .9em;
    background: var(--sunk); padding: 1px 5px; border-radius: 2px;
  }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { transition: none !important; }
  }
</style>

<div class="sheet">
  <header>
    <span class="eyebrow">A dichotomous key, written by a machine</span>
    <h1>The Animal Detective</h1>
    <p>
      A computer read a book of <strong>__COUNT__ animals</strong> described only by yes
      and no facts, and worked out its own set of questions for telling them apart.
      Nobody wrote those questions. It found them by counting.
    </p>
  </header>

  <div class="modes">
    <button class="mode on" id="mode-key">Describe an animal</button>
    <button class="mode" id="mode-game">Let it guess yours</button>
  </div>

  <!-- ==================== mode 1: the key ==================== -->
  <div id="panel-key">
    <div class="presets" id="presets"><span class="eyebrow">Start from</span></div>

    <div class="columns">
      <div class="col">
        <span class="eyebrow">The specimen</span>
        <div id="traits"></div>
      </div>

      <div class="col">
        <div class="determination" id="determination">
          <span class="eyebrow">Determination</span>
          <div class="name" id="answer">mammal</div>
          <div class="basis" id="basis"></div>
        </div>
        <span class="eyebrow">The key it followed</span>
        <ol class="key" id="key"></ol>
      </div>
    </div>

    <footer id="note"></footer>
  </div>

  <!-- ==================== mode 2: the game ==================== -->
  <div id="panel-game" hidden>
    <div class="game">
      <div>
        <div class="ask">
          <span class="counter" id="g-counter">QUESTION 1</span>
          <div class="question" id="g-question">Think of an animal.</div>
          <div class="answers" id="g-answers"></div>

          <div class="narrowing">
            <div class="bar"><span id="g-bar" style="width:100%"></span></div>
            <div class="remaining" id="g-remaining"></div>
          </div>
        </div>
        <footer id="g-note" style="margin-top:26px"></footer>
      </div>

      <div class="col">
        <span class="eyebrow">What it asked</span>
        <ul class="asked" id="g-asked"></ul>
      </div>
    </div>
  </div>
</div>

<script>
const TREE = __TREE__;
const CLUES = __CLUES__;
const ASK = __ASK__;
const COLOURS = __COLOURS__;
const PRESETS = __PRESETS__;
const LEGS = __LEGS__;
const BOOK = __BOOK__;

/* ============================ mode switching ============================ */
const panels = { key: document.getElementById('panel-key'), game: document.getElementById('panel-game') };
const tabs = { key: document.getElementById('mode-key'), game: document.getElementById('mode-game') };
Object.keys(tabs).forEach(which => {
  tabs[which].addEventListener('click', () => {
    Object.keys(tabs).forEach(other => {
      tabs[other].classList.toggle('on', other === which);
      panels[other].hidden = other !== which;
    });
    if (which === 'game') newGame();
  });
});

/* ============================== mode 1: key ============================== */
const state = Object.assign({}, PRESETS['lion'].values);

const traitBox = document.getElementById('traits');
CLUES.forEach(clue => {
  const row = document.createElement('div');
  row.className = 'trait';
  const id = 'c_' + clue;

  const label = document.createElement('label');
  label.setAttribute('for', id);
  label.textContent = ASK[clue];
  row.appendChild(label);

  if (clue === 'legs') {
    const group = document.createElement('div');
    group.className = 'legs';
    LEGS.forEach(n => {
      const b = document.createElement('button');
      b.type = 'button';
      b.textContent = n;
      b.dataset.legs = n;
      b.setAttribute('aria-label', n + ' legs');
      b.addEventListener('click', () => { state.legs = n; render(); });
      group.appendChild(b);
    });
    row.appendChild(group);
  } else {
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.className = 'toggle';
    box.id = id;
    box.addEventListener('change', e => {
      state[clue] = e.target.checked ? 1 : 0;
      render();
    });
    row.appendChild(box);
  }
  traitBox.appendChild(row);
});

const chips = document.getElementById('presets');
Object.keys(PRESETS).forEach(name => {
  const b = document.createElement('button');
  b.className = 'chip' + (PRESETS[name].real ? '' : ' invented');
  b.textContent = name;
  b.addEventListener('click', () => {
    Object.assign(state, PRESETS[name].values);
    render();
  });
  chips.appendChild(b);
});

function walk(specimen) {
  let node = TREE;
  const rungs = [];
  while (!node.leaf) {
    const value = specimen[node.clue];
    const yes = value > node.threshold;
    rungs.push({ question: node.question, said: node.clue === 'legs' ? String(value) : (yes ? 'yes' : 'no'), yes: yes });
    node = yes ? node.yes : node.no;
  }
  return { rungs: rungs, leaf: node };
}

function render() {
  CLUES.forEach(clue => {
    if (clue === 'legs') {
      document.querySelectorAll('[data-legs]').forEach(b => {
        b.classList.toggle('on', Number(b.dataset.legs) === state.legs);
      });
    } else {
      document.getElementById('c_' + clue).checked = state[clue] === 1;
    }
  });

  const out = walk(state);
  const answer = out.leaf.answer;
  const total = Object.values(out.leaf.counts).reduce((a, b) => a + b, 0);
  const agreed = out.leaf.counts[answer];
  const sure = Math.round(100 * agreed / total);

  document.getElementById('determination').style.background = COLOURS[answer];
  document.getElementById('answer').textContent = answer;
  document.getElementById('basis').textContent =
    sure + '% sure. ' + total + ' animals in the book answered these questions the same way, and '
    + agreed + ' of them ' + (agreed === 1 ? 'was' : 'were') + ' a ' + answer + '.';

  const list = document.getElementById('key');
  list.innerHTML = '';
  out.rungs.forEach(r => {
    const li = document.createElement('li');
    li.textContent = r.question + ' ';
    const said = document.createElement('span');
    said.className = 'verdict-word ' + (r.yes ? 'yes' : 'no');
    said.textContent = r.said;
    li.appendChild(said);
    list.appendChild(li);
  });

  const skipped = CLUES.length - out.rungs.length;
  document.getElementById('note').innerHTML =
    'It settled on that after <strong>' + out.rungs.length + ' question'
    + (out.rungs.length === 1 ? '' : 's') + '</strong>, and never asked about the other '
    + skipped + '. That is the entire model: no neural network, no server, no internet. '
    + 'About forty lines of logic reading a 2 KB file called <code>tree.json</code>.';
}

render();

/* ============================= mode 2: game ============================= */
let alive = [];
let asked = [];
let finished = false;

function spread(pool, clue) {
  /* Expected number still standing after this question. Lower is a better split. */
  const buckets = {};
  pool.forEach(a => {
    const v = a.v[CLUES.indexOf(clue)];
    buckets[v] = (buckets[v] || 0) + 1;
  });
  let total = 0;
  Object.values(buckets).forEach(n => { total += n * n; });
  return total / pool.length;
}

function bestQuestion(pool, used) {
  let pick = null, score = Infinity;
  CLUES.forEach(clue => {
    if (used.indexOf(clue) !== -1) return;
    const values = new Set(pool.map(a => a.v[CLUES.indexOf(clue)]));
    if (values.size < 2) return;          /* everyone agrees, so it tells us nothing */
    const s = spread(pool, clue);
    if (s < score) { score = s; pick = clue; }
  });
  return pick;
}

function newGame() {
  alive = BOOK.slice();
  asked = [];
  finished = false;
  step();
}

function step() {
  const counter = document.getElementById('g-counter');
  const question = document.getElementById('g-question');
  const answers = document.getElementById('g-answers');
  const bar = document.getElementById('g-bar');
  const remaining = document.getElementById('g-remaining');
  const note = document.getElementById('g-note');

  bar.style.width = Math.max(1.2, 100 * alive.length / BOOK.length) + '%';
  answers.innerHTML = '';

  const names = alive.slice(0, 14).map(a => a.n);
  remaining.innerHTML = alive.length === 0
    ? 'No animal in the book matches all of that. It has run out of ideas.'
    : '<b>' + alive.length + '</b> of ' + BOOK.length + ' animals still fit'
      + (alive.length <= 14 ? ': ' + names.join(', ') : '.');

  const used = asked.map(a => a.clue);
  const next = alive.length > 1 ? bestQuestion(alive, used) : null;

  if (alive.length === 1 || next === null || asked.length >= 20) {
    finished = true;
    counter.textContent = 'MY GUESS';
    if (alive.length === 0) {
      question.textContent = 'I give up.';
      note.innerHTML = 'Nothing in the book answers the way you did, which means your animal '
        + 'is either not in it or is described differently. A model can only ever know what '
        + 'it was shown.';
    } else {
      question.textContent = 'Is it ' + article(alive[0].n) + ' ' + alive[0].n + '?';
      const others = alive.length - 1;
      note.innerHTML = 'Found in <strong>' + asked.length + ' question'
        + (asked.length === 1 ? '' : 's') + '</strong> out of a possible ' + CLUES.length + '. '
        + 'Each one was chosen by the same rule that built the tree on the other tab: try every '
        + 'question still available, and keep whichever one splits the survivors most evenly. '
        + (others > 0
            ? 'It cannot get closer than this, because ' + others + ' other animal'
              + (others === 1 ? '' : 's') + ' in the book answer every question identically.'
            : 'Nothing else in the book answers all of those the same way.');
    }
    const again = document.createElement('button');
    again.className = 'quiet';
    again.textContent = 'Play again';
    again.addEventListener('click', newGame);
    answers.appendChild(again);
    return;
  }

  counter.textContent = 'QUESTION ' + (asked.length + 1);
  question.textContent = ASK[next];
  note.innerHTML = 'Think of any animal and answer honestly. The page has no idea what you '
    + 'picked. It only knows which animals are still consistent with what you have said.';

  const column = CLUES.indexOf(next);
  if (next === 'legs') {
    const offered = [...new Set(alive.map(a => a.v[column]))].sort((x, y) => x - y);
    offered.forEach(n => {
      const b = document.createElement('button');
      b.textContent = n;
      b.addEventListener('click', () => answer(next, column, v => v === n, String(n)));
      answers.appendChild(b);
    });
  } else {
    [['Yes', 1], ['No', 0]].forEach(pair => {
      const b = document.createElement('button');
      b.textContent = pair[0];
      b.addEventListener('click', () => answer(next, column, v => v === pair[1], pair[0].toLowerCase()));
      answers.appendChild(b);
    });
  }
}

function answer(clue, column, keep, said) {
  const before = alive.length;
  alive = alive.filter(a => keep(a.v[column]));
  asked.push({ clue: clue, said: said, before: before, after: alive.length });

  const list = document.getElementById('g-asked');
  list.innerHTML = '';
  asked.forEach(a => {
    const li = document.createElement('li');
    const text = document.createElement('span');
    text.innerHTML = ASK[a.clue] + ' <span class="verdict-word '
      + (a.said === 'no' ? 'no' : 'yes') + '">' + a.said + '</span>';
    const cut = document.createElement('span');
    cut.className = 'cut';
    cut.textContent = a.before + ' -> ' + a.after;
    li.appendChild(text);
    li.appendChild(cut);
    list.appendChild(li);
  });

  step();
}

function article(word) {
  return 'aeiou'.indexOf(word[0]) === -1 ? 'a' : 'an';
}
</script>
"""


def main() -> None:
    tree = json.loads((OUTPUTS / "tree.json").read_text(encoding="utf-8"))
    df = pd.read_csv(DATA)
    indexed = df.set_index("animal")

    presets = {}
    for name in PRESETS:
        row = indexed.loc[name]
        presets[name] = {"real": True, "values": {c: int(row[c]) for c in CLUES}}
    presets["the zorblax"] = {"real": False, "values": ZORBLAX}

    # The whole book, for the guessing game to narrow down live.
    book = [
        {"n": row["animal"], "g": row["group"], "v": [int(row[c]) for c in CLUES]}
        for _, row in df.iterrows()
    ]

    page = (
        PAGE.replace("__TREE__", json.dumps(tree))
        .replace("__CLUES__", json.dumps(CLUES))
        .replace("__ASK__", json.dumps(ASK))
        .replace("__COLOURS__", json.dumps(COLOURS))
        .replace("__PRESETS__", json.dumps(presets))
        .replace("__LEGS__", json.dumps(LEG_CHOICES))
        .replace("__BOOK__", json.dumps(book, separators=(",", ":")))
        .replace("__COUNT__", str(len(df)))
    )

    demo = ROOT / "demo"
    demo.mkdir(parents=True, exist_ok=True)

    # The page as published: no wrapper, since the host supplies one.
    (demo / "page.html").write_text(page, encoding="utf-8")

    # The same page as a file you can double click.
    title, rest = page.split("\n", 1)
    (demo / "index.html").write_text(
        '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<style>*{box-sizing:border-box}body{margin:0}[hidden]{display:none!important}"
        "img{max-width:100%}</style>\n"
        f"{title}\n</head>\n<body>\n{rest}\n</body>\n</html>\n",
        encoding="utf-8",
    )

    print(f"  wrote demo/index.html  ({len(book)} animals baked in, open in a browser)")
    print("  wrote demo/page.html   (the same page, without the html wrapper)")


if __name__ == "__main__":
    main()
