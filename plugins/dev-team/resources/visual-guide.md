# Visual guide (dev-team HTML pages)

The reader understands by seeing. Every human-facing page (spec, report, documentation, summary) should show its main idea visually before explaining it in text. Text explains the picture; it doesn't replace it.

All building blocks below are styled by the shared template `<style>` block and adapt to light and dark mode. Use only these classes; never add `style` attributes with colours, `<style>` blocks, scripts or external resources.

## Pick the right visual

| You want to show | Use |
|---|---|
| Who calls whom, in what order (requests, webhooks, events) | SVG sequence diagram |
| Components and how they connect | SVG box-and-arrow diagram |
| States and transitions (order status, payment status) | SVG state diagram (boxes + labelled arrows) |
| A decision or branching logic | SVG flowchart, or a table of condition → outcome |
| Comparing options, fields, or before/after | `<table>` |
| Payload shapes | Side-by-side `<table>` (field · type · meaning) or `<pre><code>` JSON |
| Key facts at a glance (counts, verdicts, owners) | `.cards` grid |
| Something the reader must not miss | `.callout` (`.warn`, `.bad`, `.ok`) |
| Status of an item (Met, Failed, Open) | `.badge` (`.ok`, `.bad`, `.warn`) |
| Long evidence or detail | `<details><summary>…</summary>…</details>` |

Minimum: a report or documentation page has at least one diagram of the main flow or structure, and a `.cards` row at the top of its summary section. A spec has a diagram in `#context` when the task touches more than one component.

## SVG rules

- Wrap every diagram: `<figure><svg class="diagram" viewBox="0 0 W H" role="img">` + `<title>` first + shapes + `</svg><figcaption>…</figcaption></figure>`.
- The `<title>` is required: `section.py` summarises the diagram as `[diagram: <title>]`, so the title must say what the diagram shows.
- Colours come from classes only: `box` (neutral node), `focus` (the node that matters), `line` (arrows), `life` (sequence lifelines), `ok` / `bad` / `warn` (outcome arrows), `text.muted` (secondary labels).
- Keep it legible: width 640–860, nodes ≥ 120 wide, labels ≤ 4 words, at most ~8 nodes. Split larger flows into several diagrams.
- Label every arrow with what travels (endpoint, event, payload name). Put file references in the figcaption, not the diagram.
- Close every tag.

### Sequence diagram skeleton

```html
<figure>
<svg class="diagram" viewBox="0 0 760 260" role="img">
  <title>Datatrans webhook to checkout authorization</title>
  <defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>
  <rect class="box" x="20" y="10" width="140" height="36" rx="6"/><text x="90" y="33" text-anchor="middle">Datatrans</text>
  <rect class="focus" x="310" y="10" width="140" height="36" rx="6"/><text x="380" y="33" text-anchor="middle">pspgateway</text>
  <rect class="box" x="600" y="10" width="140" height="36" rx="6"/><text x="670" y="33" text-anchor="middle">checkout</text>
  <line class="life" x1="90" y1="46" x2="90" y2="250"/><line class="life" x1="380" y1="46" x2="380" y2="250"/><line class="life" x1="670" y1="46" x2="670" y2="250"/>
  <line class="line" x1="90" y1="90" x2="376" y2="90" marker-end="url(#arrow)"/><text x="233" y="82" text-anchor="middle">POST webhook</text>
  <line class="line" x1="380" y1="150" x2="666" y2="150" marker-end="url(#arrow)"/><text x="523" y="142" text-anchor="middle">POST /v2/order/authorize</text>
  <line class="line ok" x1="670" y1="200" x2="384" y2="200" marker-end="url(#arrow)"/><text x="527" y="192" text-anchor="middle" class="muted">status, orderId</text>
</svg>
<figcaption>pspgateway <code>CheckoutClient.java:19</code> → checkout <code>OrderController.java:53</code></figcaption>
</figure>
```

### Box-and-arrow skeleton

```html
<figure>
<svg class="diagram" viewBox="0 0 760 120" role="img">
  <title>Components in the authorization path</title>
  <defs><marker id="arrow2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z"/></marker></defs>
  <rect class="box" x="20" y="40" width="160" height="44" rx="6"/><text x="100" y="67" text-anchor="middle">pspgateway</text>
  <rect class="focus" x="300" y="40" width="160" height="44" rx="6"/><text x="380" y="67" text-anchor="middle">checkout</text>
  <rect class="box" x="580" y="40" width="160" height="44" rx="6"/><text x="660" y="67" text-anchor="middle">order service</text>
  <line class="line" x1="180" y1="62" x2="296" y2="62" marker-end="url(#arrow2)"/>
  <line class="line" x1="460" y1="62" x2="576" y2="62" marker-end="url(#arrow2)"/>
</svg>
<figcaption>Each arrow is one synchronous HTTP call.</figcaption>
</figure>
```

Marker ids must be unique within a page (`arrow`, `arrow2`, …).

## Other building blocks

```html
<div class="cards">
  <div class="card"><strong>4 / 4</strong>questions answered</div>
  <div class="card"><strong>pspgateway → checkout</strong>call direction</div>
</div>

<p class="callout warn"><strong>Heads-up:</strong> a failed call to checkout is not handled in pspgateway.</p>

<span class="badge ok">Met</span> <span class="badge bad">Not met</span> <span class="badge warn">Open</span>

<details><summary>Evidence (6 locations)</summary><ul><li><code>repo/path:line</code> — …</li></ul></details>
```
