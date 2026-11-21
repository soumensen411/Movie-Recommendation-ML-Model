
(() => {
  "use strict";

  // Movies, recommendations and poster URLs all come from server.py.
  // The TMDB key stays on the server.

  const nf = new Intl.NumberFormat("en-US");
  const $ = (sel) => document.querySelector(sel);
  const reduceMotion = window.matchMedia(
    "(prefers-reduced-motion: reduce)"
  ).matches;

  function el(tag, cls, text) {
    const node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  // ----------------------------------------------------------------
  // DATA
  // ----------------------------------------------------------------

  let options = [];
  let byLower = new Map();
  let selected = null;

  async function api(path) {
    const res = await fetch(path);

    if (!res.ok) {
      throw new Error(`${res.status}`);
    }

    return res.json();
  }

  // ----------------------------------------------------------------
  // POSTERS
  // ----------------------------------------------------------------

  const posterCache = new Map();

  function fetchPoster(id) {
    if (posterCache.has(id)) {
      return posterCache.get(id);
    }

    const job = api(`/api/poster/${id}`)
      .then((j) => j.url)
      .catch(() => {
        posterCache.delete(id);
        return null;
      });

    posterCache.set(id, job);

    return job;
  }

  function posterBox(title, id) {
    const box = el("div", "poster");

    const initial = el(
      "span",
      "initial",
      (title.trim()[0] || "?").toUpperCase()
    );

    initial.setAttribute("aria-hidden", "true");
    box.append(initial);

    fetchPoster(id).then((url) => {
      if (!url) return;

      const img = new Image();

      img.alt = `Poster for ${title}`;
      img.decoding = "async";

      img.onload = () => {
        box.append(img);

        requestAnimationFrame(() => {
          img.classList.add("in");
        });
      };

      img.src = url;
    });

    return box;
  }

  // ----------------------------------------------------------------
  // SEARCH / AUTOCOMPLETE
  // ----------------------------------------------------------------

  const input = $("#movie");
  const list = $("#listbox");
  const form = $("#finder");
  const msg = $("#msg");

  const MAX_SHOWN = 50;

  const CHECK = `
    <svg width="16" height="16"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true">
      <path d="M20 6 9 17l-5-5"/>
    </svg>
  `;

  let shown = [];
  let active = -1;

  function filterOptions(query) {
    const q = query.trim().toLowerCase();

    if (!q) {
      return {
        items: options.slice(0, MAX_SHOWN),
        total: options.length,
        q
      };
    }

    const starts = [];
    const inside = [];

    for (const o of options) {
      const at = o.lower.indexOf(q);

      if (at === 0) {
        starts.push(o);
      } else if (at > 0) {
        inside.push(o);
      }
    }

    const all = starts.concat(inside);

    return {
      items: all.slice(0, MAX_SHOWN),
      total: all.length,
      q
    };
  }

  function optionNode(o, i, q) {
    const li = el("li", "opt");

    li.id = `opt-${i}`;
    li.setAttribute("role", "option");
    li.setAttribute("aria-selected", String(o === selected));

    const label = el("span");

    const at = q ? o.lower.indexOf(q) : -1;

    if (at >= 0) {
      label.append(o.title.slice(0, at));

      label.append(
        el("mark", null, o.title.slice(at, at + q.length))
      );

      label.append(o.title.slice(at + q.length));
    } else {
      label.textContent = o.title;
    }

    li.append(label);
    li.insertAdjacentHTML("beforeend", CHECK);

    return li;
  }

  function renderList() {
    const { items, total, q } = filterOptions(
      input.dataset.typed ? input.value : ""
    );

    shown = items;
    active = q && items.length ? 0 : -1;

    list.replaceChildren(
      ...items.map((o, i) => optionNode(o, i, q))
    );

    if (!items.length) {
      list.append(
        el("li", "listbox-note", "No matching titles")
      );
    } else if (total > items.length) {
      list.append(
        el(
          "li",
          "listbox-note",
          `Showing ${items.length} of ${nf.format(total)}, keep typing to narrow`
        )
      );
    }

    setActive(active);
  }

  function setActive(i) {
    const prev = list.querySelector(".is-active");

    if (prev) {
      prev.classList.remove("is-active");
    }

    active = i;

    if (i < 0 || !shown.length) {
      input.removeAttribute("aria-activedescendant");
      return;
    }

    const node = list.children[i];

    node.classList.add("is-active");

    input.setAttribute(
      "aria-activedescendant",
      node.id
    );

    node.scrollIntoView({
      block: "nearest"
    });
  }

  function openList() {
    renderList();

    list.hidden = false;

    input.setAttribute("aria-expanded", "true");
  }

  function closeList() {
    list.hidden = true;

    input.setAttribute("aria-expanded", "false");

    input.removeAttribute("aria-activedescendant");
  }

  function choose(o) {
    selected = o;
    input.value = o.title;

    delete input.dataset.typed;

    clearMessage();
    closeList();
  }

  // Accepts the text in the box if it is an exact title.
  function commitText() {
    const hit = byLower.get(
      input.value.trim().toLowerCase()
    );

    if (!hit) return false;

    selected = hit;
    input.value = hit.title;

    return true;
  }

  function clearMessage() {
    msg.textContent = "";
  }

  // Search focus
  input.addEventListener("focus", () => {
    input.select();

    delete input.dataset.typed;

    openList();
  });

  // Search input
  input.addEventListener("input", () => {
    input.dataset.typed = "1";

    clearMessage();
    openList();
  });

  // Keyboard navigation
  input.addEventListener("keydown", (e) => {
    const isOpen = !list.hidden;

    if (
      e.key === "ArrowDown" ||
      e.key === "ArrowUp"
    ) {
      e.preventDefault();

      if (!isOpen) {
        openList();
        return;
      }

      if (!shown.length) return;

      const step = e.key === "ArrowDown" ? 1 : -1;

      setActive(
        (active + step + shown.length) % shown.length
      );

    } else if (
      e.key === "Enter" &&
      isOpen &&
      active >= 0
    ) {
      e.preventDefault();

      choose(shown[active]);

    } else if (
      e.key === "Escape" &&
      isOpen
    ) {
      e.preventDefault();

      closeList();

      if (!commitText()) {
        input.value = selected.title;
      }
    }
  });

  // Close suggestions when input loses focus
  input.addEventListener("blur", () => {
    closeList();

    if (!commitText()) {
      input.value = selected.title;
    }

    delete input.dataset.typed;
  });

  // Select suggestion before blur closes the list
  list.addEventListener("mousedown", (e) => {
    e.preventDefault();

    const li = e.target.closest(".opt");

    if (li) {
      choose(shown[Number(li.id.slice(4))]);
    }
  });

  // Mouse navigation
  list.addEventListener("mousemove", (e) => {
    const li = e.target.closest(".opt");

    if (!li) return;

    const i = Number(li.id.slice(4));

    if (i !== active) {
      setActive(i);
    }
  });

  // ----------------------------------------------------------------
  // RECOMMENDATION RESULTS
  // ----------------------------------------------------------------

  function scoreBar(rec, i) {
    const bar = el("div", "bar");

    const fill = document.createElement("i");

    fill.style.setProperty("--s", rec.score / 100);

    bar.append(fill);

    bar.setAttribute("role", "img");

    bar.setAttribute(
      "aria-label",
      `${rec.score}% match`
    );

    return bar;
  }

  // Featured recommendation
  function featureCard(rec) {
    const card = el("li", "card feature");

    card.style.setProperty("--i", 0);

    const body = el("div", "feature-body");

    const name = el("h3", "name", rec.title);

    const figure = el("div", "figure");

    figure.append(
      el("b", null, `${rec.score}%`),
      el("span", null, "match")
    );

    const head = el("div", "feature-head");

    head.append(
      el("p", "eyebrow", "Closest match"),
      name
    );

    const foot = el("div", "feature-foot");

    foot.append(
      figure,
      scoreBar(rec, 0)
    );

    body.append(head, foot);

    card.append(
      posterBox(rec.title, rec.id),
      body
    );

    return card;
  }

  // Standard recommendation card
  function smallCard(rec, i) {
    const card = el("li", "card");

    card.style.setProperty("--i", i);

    const name = el("h3", "name", rec.title);

    name.title = rec.title;

    const meta = el("div", "meta");

    const score = el(
      "span",
      "score",
      `${rec.score}%`
    );

    score.append(
      el("small", null, " match")
    );

    meta.append(
      el(
        "span",
        "rank",
        String(i + 1).padStart(2, "0")
      ),
      score
    );

    card.append(
      posterBox(rec.title, rec.id),
      name,
      meta,
      scoreBar(rec, i)
    );

    return card;
  }

  // Render recommendation results
  function render(data) {
    const sel = data.selected;

    document.body.dataset.state = "results";

    $("#results").hidden = false;

    $("#because-title").textContent = sel.title;

    const cards = data.results.map((rec, i) => {
      return i === 0
        ? featureCard(rec)
        : smallCard(rec, i);
    });

    $("#grid").replaceChildren(...cards);

    // Selected movie
    $("#source-poster").replaceChildren(
      posterBox(sel.title, sel.id)
    );

    $("#source-title").textContent = sel.title;

    $("#source-desc").textContent =
      "Your selection is the starting point. The five films above share the most with it across plot overview, genres, keywords, cast and director.";

    // Recommendation information
    const facts = [
      [
        "Method",
        "Cosine similarity on word counts"
      ],
      [
        "Vocabulary",
        `${nf.format(data.vocabulary)} most frequent terms`
      ],
      [
        "Compared with",
        `${nf.format(data.compared_with)} films`
      ]
    ].map(([k, v]) => {
      const row = document.createElement("div");

      row.append(
        el("dt", null, k),
        el("dd", null, v)
      );

      return row;
    });

    $("#facts").replaceChildren(...facts);

    // Scroll to results
    $("#results").scrollIntoView({
      behavior: reduceMotion ? "auto" : "smooth",
      block: "start"
    });
  }

  // ----------------------------------------------------------------
  // FORM SUBMISSION
  // ----------------------------------------------------------------

  const goBtn = form.querySelector(".go");

  let requestId = 0;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    if (!selected) return;

    if (!commitText()) {
      msg.textContent = "Choose a title from the list";

      input.focus();

      return;
    }

    clearMessage();
    closeList();

    const mine = ++requestId;

    goBtn.disabled = true;

    goBtn.querySelector("span").textContent = "Finding";

    try {
      const data = await api(
        `/api/recommend?title=${encodeURIComponent(selected.title)}`
      );

      if (mine === requestId) {
        render(data);
      }

    } catch {
      msg.textContent =
        "Could not reach the recommendation server";

    } finally {
      if (mine === requestId) {
        goBtn.disabled = false;

        goBtn.querySelector("span").textContent =
          "Find similar films";
      }
    }
  });

  // ----------------------------------------------------------------
  // INITIALIZE APPLICATION
  // ----------------------------------------------------------------

  async function start() {
    input.disabled = true;
    goBtn.disabled = true;

    input.placeholder = "Loading movies";

    try {
      const titles = await api("/api/movies");

      options = titles.map((title) => ({
        title,
        lower: title.toLowerCase()
      }));

      byLower = new Map(
        options.map((o) => [o.lower, o])
      );

      // Start with the first movie
      selected = options[0];

      input.value = selected.title;

      input.placeholder = "Search";

      input.disabled = false;
      goBtn.disabled = false;

    } catch {
      input.placeholder = "Search";

      msg.textContent =
        "Could not reach the recommendation server. Start it with python server.py";
    }
  }

  // ----------------------------------------------------------------
  // POSTER WALL
  // ----------------------------------------------------------------

  async function buildWall() {
    if (
      !window.matchMedia("(min-width: 1024px)").matches
    ) {
      return;
    }

    let items;

    try {
      items = await api("/api/sample?n=18");
    } catch {
      return;
    }

    const wall = $("#wall");

    const cols = [
      el("div", "wall-col"),
      el("div", "wall-col"),
      el("div", "wall-col")
    ];

    let loaded = 0;

    items.forEach((m, i) => {
      const tile = el("button", "tile");

      tile.type = "button";

      tile.setAttribute(
        "aria-label",
        `Find movies similar to ${m.title}`
      );

      cols[i % 3].append(tile);

      fetchPoster(m.id).then((url) => {
        if (!url) {
          tile.remove();
          return;
        }

        const img = new Image();

        img.alt = "";

        img.onload = () => {
          tile.append(img);

          requestAnimationFrame(() => {
            img.classList.add("in");
          });

          if (++loaded === 3) {
            wall.classList.add("ready");
          }
        };

        img.onerror = () => tile.remove();

        img.src = url;
      });

      // Click a poster to get recommendations
      tile.addEventListener("click", () => {
        const o = byLower.get(
          m.title.toLowerCase()
        );

        if (!o) return;

        choose(o);

        form.requestSubmit();
      });
    });

    wall.replaceChildren(...cols);
  }

  // ----------------------------------------------------------------
  // KEYBOARD SHORTCUT
  // Press "/" to focus search
  // ----------------------------------------------------------------

  document.addEventListener("keydown", (e) => {
    if (
      e.key !== "/" ||
      e.metaKey ||
      e.ctrlKey ||
      e.altKey
    ) {
      return;
    }

    const t = e.target;

    if (
      t instanceof HTMLElement &&
      (
        t.isContentEditable ||
        /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName)
      )
    ) {
      return;
    }

    e.preventDefault();

    if (!input.disabled) {
      input.focus();
    }
  });

  // Start application
  start().then(buildWall);

})();
