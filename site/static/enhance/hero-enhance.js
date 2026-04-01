// hero-enhance.js — Progressive enhancement for the landing page hero.
// Transforms the hero into a live proof demo with the pipeline icons
// as a vertical column and a random featured proof flowing beside it.
// Falls back to current layout if this module fails.

(function () {
    'use strict';

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

    function pickRandom(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    }

    function init() {
        var container = document.getElementById('hero-demo-container');
        var proofs = window.FEATURED_PROOFS_DATA;
        if (!container || !proofs || proofs.length === 0) return;

        var proof = pickRandom(proofs);

        // Build pipeline column
        var pipelineHtml = '<div class="hero-pipeline-vertical">';
        PIPELINE_STEPS.forEach(function (step, i) {
            if (i > 0) {
                pipelineHtml += '<div class="pipeline-arrow-down">\u2193</div>';
            }
            var iconClass = step.isVerdict ? 'pipeline-icon verdict-icon' : 'pipeline-icon';
            pipelineHtml += '<div class="' + iconClass + '" title="' + escapeHtml(step.label) + '">' + step.icon + '</div>';
        });
        pipelineHtml += '</div>';

        // Build proof demo
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

        var proofHtml = '<div class="hero-demo-proof">' +
            '<div class="hero-demo-claim">' +
            '<span class="hero-demo-label">LIVE PROOF</span>' +
            '\u201C' + escapeHtml(proof.claim) + '\u201D' +
            '</div>' +
            '<div class="hero-demo-meta">' +
            '<span class="badge ' + badgeClass + '">' + escapeHtml(proof.verdict) + '</span> ' +
            tags +
            '</div>' +
            sourceHtml +
            '<a href="' + escapeHtml(proof.url) + '" class="hero-demo-link">\u2192 read full proof</a>' +
            '</div>';

        container.innerHTML = '<div class="hero-demo">' + pipelineHtml + proofHtml + '</div>';

        // Hide the horizontal pipeline section (it's now redundant)
        var horizontalPipeline = document.querySelector('.pipeline');
        var pipelineHeading = horizontalPipeline ?
            horizontalPipeline.previousElementSibling : null;
        if (horizontalPipeline) horizontalPipeline.style.display = 'none';
        if (pipelineHeading && pipelineHeading.classList.contains('section-heading')) {
            pipelineHeading.style.display = 'none';
        }

        // Note: The hero layout uses CSS flexbox for text beside the pipeline.
        // CSS handles this well without Pretext. Pretext's value is in the
        // catalog (Task 5) where it enables virtualization via pre-measured
        // heights. Here the layout is a single claim, not worth the import.
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
