# Vendored Library API Notes

Generated 2026-04-01 during Task 2 (discovery gate).

## Package Versions

- `@chenglou/pretext` v0.0.3
- `@tanstack/virtual-core` v3.13.23

Both bundled with esbuild into single ESM files (no external imports).

---

## Pretext (`pretext.esm.min.js`)

### Exports

```
clearCache, layout, layoutNextLine, layoutWithLines, prepare,
prepareWithSegments, profilePrepare, setLocale, walkLineRanges
```

### Core API (the two functions we need)

```ts
prepare(text: string, font: string, options?: PrepareOptions): PreparedText
```

- `text` — the string to measure
- `font` — CSS font shorthand, e.g. `"16px Inter"` (used with canvas `measureText`)
- `options` — optional `{ whiteSpace?: 'normal' | 'pre-wrap' }` (default: `'normal'`)
- Returns an opaque `PreparedText` token (branded type). Internally caches
  segment metrics keyed on the font string.

```ts
layout(prepared: PreparedText, maxWidth: number, lineHeight: number): LayoutResult
```

- `prepared` — the token from `prepare()`
- `maxWidth` — available width in CSS pixels
- `lineHeight` — line height in CSS pixels (total height = lineCount * lineHeight)
- Returns `{ lineCount: number, height: number }`

### Additional functions

```ts
prepareWithSegments(text: string, font: string, options?): PreparedTextWithSegments
```
Like `prepare` but retains segment strings, needed for `layoutWithLines`, `walkLineRanges`, and `layoutNextLine`.

```ts
layoutWithLines(prepared: PreparedTextWithSegments, maxWidth: number, lineHeight: number): LayoutLinesResult
```
Returns `{ lineCount, height, lines: LayoutLine[] }` where each `LayoutLine` has
`{ text, width, start: LayoutCursor, end: LayoutCursor }`.

```ts
walkLineRanges(prepared: PreparedTextWithSegments, maxWidth: number, onLine: (line) => void): number
```
Calls `onLine` for each line range; returns line count. Lower-level than `layoutWithLines`.

```ts
layoutNextLine(prepared: PreparedTextWithSegments, start: LayoutCursor, maxWidth: number): LayoutLine | null
```
Incremental line iteration.

```ts
profilePrepare(text: string, font: string, options?): PrepareProfile
```
Returns timing info: `{ analysisMs, measureMs, totalMs, analysisSegments, preparedSegments, breakableSegments }`.

```ts
clearCache(): void       // clears measurement + analysis caches
setLocale(locale?: string): void  // sets Intl.Segmenter locale
```

### Key types

```ts
type PreparedText = { readonly [brand]: true }     // opaque
type LayoutResult = { lineCount: number; height: number }
type LayoutCursor = { segmentIndex: number; graphemeIndex: number }
type LayoutLine = { text: string; width: number; start: LayoutCursor; end: LayoutCursor }
```

### Important implementation notes

- Uses **CanvasRenderingContext2D.measureText** internally (needs canvas in the
  environment — works in browsers and OffscreenCanvas workers).
- Caches segment metrics per font string — first `prepare()` call for a font is
  slower; subsequent calls reuse the cache.
- No DOM dependency at all — purely canvas-based.

---

## TanStack Virtual Core (`tanstack-virtual-core.esm.min.js`)

### Exports

```
Virtualizer, approxEqual, debounce, defaultKeyExtractor, defaultRangeExtractor,
elementScroll, measureElement, memo, notUndefined, observeElementOffset,
observeElementRect, observeWindowOffset, observeWindowRect, windowScroll
```

### Core API

```ts
class Virtualizer<TScrollElement extends Element | Window, TItemElement extends Element> {
  constructor(opts: VirtualizerOptions<TScrollElement, TItemElement>)
  // ...
}
```

### Constructor options (VirtualizerOptions)

**Required:**
- `count: number` — total number of items
- `getScrollElement: () => TScrollElement | null` — returns the scroll container
- `estimateSize: (index: number) => number` — estimated height (or width) per item
- `scrollToFn` — scroll implementation (use exported `elementScroll` for DOM elements)
- `observeElementRect` — rect observer (use exported `observeElementRect`)
- `observeElementOffset` — scroll offset observer (use exported `observeElementOffset`)

**Common optional:**
- `overscan?: number` — items to render beyond visible area (default: 1)
- `onChange?: (instance, sync: boolean) => void` — called when virtual items change
- `measureElement?: (element, entry, instance) => number` — dynamic measurement
- `horizontal?: boolean` — horizontal mode (default: false)
- `paddingStart?: number`
- `paddingEnd?: number`
- `gap?: number` — gap between items
- `initialRect?: Rect` — `{ width, height }` before first DOM measurement
- `getItemKey?: (index: number) => Key`
- `rangeExtractor?: (range: Range) => number[]`
- `scrollMargin?: number`
- `lanes?: number` — for masonry/multi-column
- `enabled?: boolean`
- `isRtl?: boolean`
- `initialOffset?: number | (() => number)`

### Key instance methods

```ts
setOptions(opts: VirtualizerOptions): void
getVirtualItems(): VirtualItem[]
getTotalSize(): number
scrollToIndex(index: number, options?: ScrollToIndexOptions): void
scrollToOffset(offset: number, options?: ScrollToOffsetOptions): void
scrollBy(delta: number, options?): void
measureElement(node: TItemElement | null): void
resizeItem(index: number, size: number): void
measure(): void   // force re-measure
_didMount(): () => void   // call after mount, returns cleanup
_willUpdate(): void       // call before each render
```

### Key types

```ts
interface VirtualItem {
  key: Key;
  index: number;
  start: number;     // offset from top of container
  end: number;       // start + size
  size: number;      // measured or estimated height
  lane: number;      // for multi-lane layouts
}

interface Rect { width: number; height: number }
```

### DOM adapter functions (exported, pass to constructor)

For standard DOM element scroll containers:
- `observeElementRect` — uses ResizeObserver on scroll element
- `observeElementOffset` — uses scroll event listener
- `elementScroll` — calls `scrollElement.scrollTo()`
- `measureElement` — uses `element.getBoundingClientRect()` + ResizeObserver

For window-based scrolling:
- `observeWindowRect`, `observeWindowOffset`, `windowScroll`

### Lifecycle

1. Create: `new Virtualizer({ ... })`
2. Mount: `const cleanup = virtualizer._didMount()`
3. Each render: `virtualizer._willUpdate()` then `virtualizer.getVirtualItems()`
4. Unmount: `cleanup()`

---

## Plan Assumptions vs Actual API

### Pretext — MATCHES

The plan assumed:
- `prepare(text, cssFont)` -> prepared token
- `layout(prepared, maxWidth, lineHeight)` -> `{ height, lineCount }`

**Actual API matches exactly.** The function signatures are:
- `prepare(text, font, options?)` -> `PreparedText`
- `layout(prepared, maxWidth, lineHeight)` -> `{ lineCount, height }`

No changes needed in Tasks 3-6.

### TanStack Virtual Core — MATCHES with notes

The plan assumed:
- `new Virtualizer({ count, getScrollElement, estimateSize, measureElement, overscan, onChange, scrollToFn, observeElementRect, observeElementOffset })`

**Actual API matches.** All those options exist. Additional notes:
- `scrollToFn`, `observeElementRect`, and `observeElementOffset` are **required**
  (not optional). The library exports ready-made implementations (`elementScroll`,
  `observeElementRect`, `observeElementOffset`) to pass in directly.
- Lifecycle: must call `_didMount()` after attaching to DOM, and `_willUpdate()`
  before each render pass. The plan should account for this.
- `measureElement` IS supported as an option for dynamic sizing.

No blocking API differences. Tasks 3-6 can proceed as planned.
