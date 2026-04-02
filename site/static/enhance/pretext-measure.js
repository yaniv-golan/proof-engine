// pretext-measure.js — Shared Pretext wrapper for the Proof Engine site.
// Initializes Pretext with the site's font stacks and exposes measurement helpers.
// All enhance modules import from this file.
//
// IMPORTANT: After vendoring in Task 2, verify the actual Pretext API exports
// against this code. The published API uses prepare() + layout() with CSS font
// shorthand strings like "14px Georgia". If the API differs from what's coded
// here, update this module before committing.

import { prepare, layout, prepareWithSegments, layoutWithLines } from '../vendor/pretext.esm.min.js';

// Site font stacks (must match style.css :root variables)
var FONT_SERIF = "Georgia, 'Times New Roman', serif";
var FONT_MONO = "'JetBrains Mono', ui-monospace, SFMono-Regular, 'SF Mono', Menlo, monospace";
var FONT_SYSTEM = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif";

/**
 * Measure text dimensions without DOM rendering.
 *
 * Pretext API: prepare(text, font) prepares a specific text+font pair.
 * layout(prepared, maxWidth, lineHeight) returns { height, lineCount }.
 * Note: prepare() takes the TEXT as first arg, font as second — not just font.
 * This means we cannot cache by font alone; each unique text must be prepared.
 *
 * @param {string} text - The text to measure
 * @param {string} font - CSS font-family string
 * @param {number} fontSize - Font size in pixels (used to build font shorthand)
 * @param {number} maxWidth - Container width for line wrapping
 * @param {number} lineHeight - Line height multiplier (default 1.5)
 * @returns {{ width: number, height: number, lines: number }}
 */
export function measureText(text, font, fontSize, maxWidth, lineHeight) {
    lineHeight = lineHeight || 1.5;
    // Pretext's layout() expects lineHeight in absolute CSS pixels,
    // not as a multiplier. Convert: 14px font × 1.5 multiplier = 21px.
    var lineHeightPx = fontSize * lineHeight;
    var cssFont = fontSize + 'px ' + font;
    try {
        var prepared = prepare(text, cssFont);
        var result = layout(prepared, maxWidth, lineHeightPx);
        // layout() returns { height: number, lineCount: number }
        return {
            width: maxWidth,
            height: result.height,
            lines: result.lineCount
        };
    } catch (e) {
        // Pretext unavailable or failed — return null so callers fall back
        return null;
    }
}

/**
 * Estimate a proof card's height from its data.
 *
 * Uses Pretext for the variable part (claim text line count) and
 * estimation for fixed parts (padding, gaps). This is an ESTIMATE
 * for TanStack Virtual's estimateSize callback — TanStack will
 * correct it with actual DOM measurements via measureElement after
 * the card renders. The estimate just needs to be close enough to
 * avoid visible jumping during initial scroll.
 *
 * @param {{ claim: string, verdict: string, tags: string[], source_names: string[], has_citations: boolean }} cardData
 * @param {number} containerWidth - Card inner width (container minus padding)
 * @returns {number|null} Estimated height in pixels, or null if Pretext unavailable
 */
export function estimateCardHeight(cardData, containerWidth) {
    var PADDING_Y = 16 + 16; // top + bottom padding
    var BORDER_Y = 1 + 1; // border: 1px solid (top + bottom)
    var GAP_CLAIM_META = 8; // margin-bottom on h3

    // Claim text — the only truly variable part, measured by Pretext
    var innerWidth = containerWidth - 36; // card padding 18px * 2
    var claimResult = measureText(
        cardData.claim,
        FONT_SERIF,
        14, // .proof-card h3 font-size
        innerWidth,
        1.5 // .proof-card h3 line-height
    );
    if (!claimResult) return null;

    // Meta row: flexbox with wrap. Estimate based on content.
    // Badge (~80px) + tags (~80px each) + date (~70px) with 8px gaps.
    var tags = cardData.tags || [];
    var metaItemsWidth = 80 + (tags.length * 88) + 70 + (tags.length * 8);
    var metaRows = Math.ceil(metaItemsWidth / innerWidth);
    var metaHeight = metaRows * 22; // ~22px per row (11px font + padding + gap)

    // Source line: may wrap on narrow containers or with many source names
    var hasSource = (cardData.source_names && cardData.source_names.length > 0) ||
                    cardData.has_citations === false;
    var sourceHeight = 0;
    if (hasSource) {
        var sourceText = (cardData.source_names || []).join(', ');
        if (sourceText.length === 0) sourceText = 'Pure computation — no external sources';
        var sourceResult = measureText(sourceText, FONT_MONO, 11, innerWidth, 1.5);
        sourceHeight = 8 + (sourceResult ? sourceResult.height : 18); // 8px margin-top
    }

    return PADDING_Y + BORDER_Y + claimResult.height + GAP_CLAIM_META +
           metaHeight + sourceHeight + 12; // 12px margin-bottom on .proof-card
}

/**
 * Estimate heights for an array of proof card data objects.
 * @param {Array} cardDataArray - Array of proof card data
 * @param {number} containerWidth - Card container width
 * @returns {number[]|null} Array of estimated heights, or null if Pretext unavailable
 */
export function estimateCardHeights(cardDataArray, containerWidth) {
    var heights = [];
    for (var i = 0; i < cardDataArray.length; i++) {
        var h = estimateCardHeight(cardDataArray[i], containerWidth);
        if (h === null) return null; // Pretext unavailable, abort
        heights.push(h);
    }
    return heights;
}

/**
 * Split text into individual lines at a given width.
 * Returns an array of line strings, or null if Pretext unavailable.
 *
 * @param {string} text
 * @param {string} font - CSS font-family string
 * @param {number} fontSize - in px
 * @param {number} maxWidth
 * @param {number} lineHeight - CSS multiplier (e.g. 1.4)
 * @returns {string[]|null}
 */
export function getTextLines(text, font, fontSize, maxWidth, lineHeight) {
    lineHeight = lineHeight || 1.5;
    var lineHeightPx = fontSize * lineHeight;
    var cssFont = fontSize + 'px ' + font;
    try {
        var prepared = prepareWithSegments(text, cssFont);
        var result = layoutWithLines(prepared, maxWidth, lineHeightPx);
        return result.lines.map(function (l) { return l.text; });
    } catch (e) {
        return null;
    }
}

// Re-export font constants for use by enhance modules
export { FONT_SERIF, FONT_MONO, FONT_SYSTEM };
