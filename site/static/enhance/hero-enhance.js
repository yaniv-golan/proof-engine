// hero-enhance.js — Progressive enhancement for the landing page hero.
// Transforms the hero into a live proof demo with the pipeline icons
// as a vertical column and a random featured proof flowing beside it.
// Uses Pretext to auto-fit the claim text: binary-searches for the
// exact font size that fills the available width in 2-3 lines.
// Falls back to current layout if this module fails.

import { measureText, FONT_SERIF } from './pretext-measure.js';

(function () {
    'use strict';

    // Auto-fit: find the largest font size that keeps text within
    // targetLines lines at the given width. Binary search using Pretext.
    var MIN_FONT = 16;
    var MAX_FONT = 34;
    var TARGET_LINES_MAX = 3;

    function autoFitFontSize(text, maxWidth, lineHeight) {
        // Binary search for the sweet spot
        var lo = MIN_FONT;
        var hi = MAX_FONT;
        var bestSize = MIN_FONT;

        for (var i = 0; i < 20; i++) { // 20 iterations = sub-pixel precision
            var mid = (lo + hi) / 2;
            var result = measureText(text, FONT_SERIF, mid, maxWidth, lineHeight);
            if (!result) return null; // Pretext failed

            if (result.lines <= TARGET_LINES_MAX) {
                // Fits — try larger
                bestSize = mid;
                lo = mid;
            } else {
                // Too many lines — try smaller
                hi = mid;
            }
        }

        return Math.round(bestSize * 10) / 10; // round to 1 decimal
    }

    var PIPELINE_STEPS = [
        { icon: '?', label: 'claim' },
        { icon: '\u2315', label: 'fetch sources' },
        { icon: '\u2713', label: 'verify quotes' },
        { icon: '\u25B6', label: 'run proof.py' },
        { icon: '\u220E', label: 'verdict', isVerdict: true }
    ];

    var BADGE_CLASSES = {
        'proved': 'badge-proved',
        'proved-qualified': 'badge-proved-qualified',
        'disproved': 'badge-disproved',
        'disproved-qualified': 'badge-disproved-qualified',
        'partial': 'badge-partial',
        'undetermined': 'badge-undetermined',
        'supported': 'badge-supported',
        'supported-qualified': 'badge-supported-qualified',
    };

    function escapeHtml(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    var CYCLE_INTERVAL = 4000; // ms between proof changes
    var FADE_DURATION = 500;   // ms for fade transition

    function pickRandom(arr, exclude) {
        if (arr.length <= 1) return arr[0];
        var choice;
        do {
            choice = arr[Math.floor(Math.random() * arr.length)];
        } while (choice === exclude && arr.length > 1);
        return choice;
    }

    function buildProofHtml(proof) {
        var badgeClass = BADGE_CLASSES[proof.verdict_category] || 'badge-undetermined';
        var tags = (proof.tags || []).map(function (t) {
            return '<span class="tag">' + escapeHtml(t) + '</span>';
        }).join(' ');

        var sourceHtml = '';
        if (proof.source_names && proof.source_names.length > 0) {
            var extra = proof.source_names_extra > 0 ? ' +' + proof.source_names_extra + ' more' : '';
            sourceHtml = '<div class="hero-demo-sources">Sources: ' +
                proof.source_names.map(escapeHtml).join(', ') + extra + '</div>';
        }

        return '<div class="hero-demo-claim">' +
            '<span class="hero-demo-label">LIVE PROOF</span>' +
            '\u201C' + escapeHtml(proof.claim) + '\u201D' +
            '</div>' +
            '<div class="hero-demo-meta">' +
            '<span class="badge ' + badgeClass + '">' + escapeHtml(proof.verdict) + '</span> ' +
            tags +
            '</div>' +
            sourceHtml +
            '<a href="' + escapeHtml(proof.url) + '" class="hero-demo-link">\u2192 read full proof</a>';
    }

    function fitClaim(proofEl, claimText) {
        var claimEl = proofEl.querySelector('.hero-demo-claim');
        if (!claimEl) return;
        var availableWidth = claimEl.clientWidth - 14;
        var fittedSize = autoFitFontSize(claimText, availableWidth, 1.4);
        if (fittedSize) {
            claimEl.style.fontSize = fittedSize + 'px';
            claimEl.style.lineHeight = '1.4';
        }
    }

    function init() {
        var container = document.getElementById('hero-demo-container');
        var proofs = window.FEATURED_PROOFS_DATA;
        if (!container || !proofs || proofs.length === 0) return;

        var currentProof = pickRandom(proofs);

        // Build pipeline column (static, doesn't change)
        var pipelineHtml = '<div class="hero-pipeline-vertical">';
        PIPELINE_STEPS.forEach(function (step, i) {
            if (i > 0) {
                pipelineHtml += '<div class="pipeline-arrow-down">\u2193</div>';
            }
            var iconClass = step.isVerdict ? 'pipeline-icon verdict-icon' : 'pipeline-icon';
            pipelineHtml += '<div class="' + iconClass + '" title="' + escapeHtml(step.label) + '">' + step.icon + '</div>';
        });
        pipelineHtml += '</div>';

        // Build initial layout
        container.innerHTML = '<div class="hero-demo">' + pipelineHtml +
            '<div class="hero-demo-proof" style="transition: opacity ' + FADE_DURATION + 'ms ease-out, transform ' + FADE_DURATION + 'ms ease-out;">' +
            buildProofHtml(currentProof) + '</div></div>';

        // Hide the horizontal pipeline section
        var horizontalPipeline = document.querySelector('.pipeline');
        var pipelineHeading = horizontalPipeline ?
            horizontalPipeline.previousElementSibling : null;
        if (horizontalPipeline) horizontalPipeline.style.display = 'none';
        if (pipelineHeading && pipelineHeading.classList.contains('section-heading')) {
            pipelineHeading.style.display = 'none';
        }

        // Auto-fit initial claim
        var proofEl = container.querySelector('.hero-demo-proof');
        requestAnimationFrame(function () {
            fitClaim(proofEl, currentProof.claim);
        });

        // Cycle through proofs with slide + fade
        if (proofs.length > 1) {
            setInterval(function () {
                var nextProof = pickRandom(proofs, currentProof);
                currentProof = nextProof;

                // Slide up + fade out
                proofEl.style.opacity = '0';
                proofEl.style.transform = 'translateY(-30px)';

                setTimeout(function () {
                    // Swap content while invisible
                    proofEl.innerHTML = buildProofHtml(nextProof);

                    // Position below for entrance — disable transition first
                    proofEl.style.transition = 'none';
                    proofEl.style.transform = 'translateY(30px)';
                    proofEl.style.opacity = '0';

                    // Fit new claim text
                    fitClaim(proofEl, nextProof.claim);

                    // Force browser to commit the above state before re-enabling transition.
                    // Double-rAF ensures a paint happens between position reset and animation start.
                    requestAnimationFrame(function () {
                        requestAnimationFrame(function () {
                            proofEl.style.transition = 'opacity ' + FADE_DURATION + 'ms ease-out, transform ' + FADE_DURATION + 'ms ease-out';
                            proofEl.style.opacity = '1';
                            proofEl.style.transform = 'translateY(0)';
                        });
                    });
                }, FADE_DURATION);
            }, CYCLE_INTERVAL);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
