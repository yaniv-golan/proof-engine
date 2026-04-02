import { autoFitFontSize, FONT_SERIF } from './pretext-measure.js';

(function () {
    'use strict';

    var STEPS = [
        { icon: '?', label: 'claim', key: 'claim' },
        { icon: '\u2315', label: 'fetch sources', key: 'sources' },
        { icon: '\u2713', label: 'verify quotes', key: 'citations' },
        { icon: '\u25B6', label: 'run proof.py', key: 'code' },
        { icon: '\u220E', label: 'verdict', key: 'verdict' }
    ];

    var AUTO_CYCLE_DELAY = 2000;
    var STEP_DURATION = 3000;

    function escapeHtml(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    function buildExpandedContent(key, data) {
        if (!data) return '';
        switch (key) {
            case 'claim':
                return '<div class="pipeline-claim-text">\u201C' +
                    escapeHtml(data.claim_natural) + '\u201D</div>' +
                    (data.claim_formal_summary
                        ? '<div class="pipeline-formal">' + escapeHtml(data.claim_formal_summary) + '</div>'
                        : '');
            case 'sources':
                return (data.sources || []).map(function (s) {
                    return '<div>' + escapeHtml(s.source_name) +
                        '<span class="source-badge">' + escapeHtml(s.source_type) + '</span></div>';
                }).join('');
            case 'citations':
                return (data.citations || []).slice(0, 3).map(function (c) {
                    return '<div class="cit-row"><span class="fact-id">' +
                        escapeHtml(c.fact_id) + '</span> ' +
                        escapeHtml(c.source_name) + ' — ' +
                        '<span class="badge badge-' +
                        (c.status === 'verified' ? 'proved' : 'partial') +
                        '">' + escapeHtml(c.status) + '</span>' +
                        (c.quote_snippet
                            ? '<div style="font-size:11px;color:var(--text-muted);margin-top:2px;">\u201C' +
                              escapeHtml(c.quote_snippet) + '\u2026\u201D</div>'
                            : '') +
                        '</div>';
                }).join('');
            case 'code':
                return data.code_example && data.code_example.snippet
                    ? '<pre><code>' + escapeHtml(data.code_example.snippet) + '</code></pre>'
                    : '<p style="color:var(--text-muted);">Computation details in proof script.</p>';
            case 'verdict':
                return '<span class="badge badge-' +
                    (data.verdict ? data.verdict.category : 'undetermined') + '">' +
                    escapeHtml(data.verdict ? data.verdict.raw : '') + '</span>' +
                    (data.verdict && data.verdict.summary
                        ? '<p style="margin-top:8px;font-size:13px;">' +
                          escapeHtml(data.verdict.summary) + '</p>'
                        : '') +
                    '<a href="' + escapeHtml(data.proof_url || '') +
                    '" style="display:block;margin-top:8px;font-size:12px;color:var(--accent);">\u2192 read full proof</a>';
            default:
                return '';
        }
    }

    function init() {
        var staticEl = document.getElementById('pipeline-static');
        var interactiveEl = document.getElementById('pipeline-interactive');
        var data = window.PIPELINE_EXAMPLE_DATA;
        if (!staticEl || !interactiveEl || !data) return;

        var currentOpen = -1;
        var cycleTimer = null;
        var userInteracted = false;

        var accordion = document.createElement('div');
        accordion.className = 'pipeline-accordion';

        var rows = [];
        var contents = [];

        STEPS.forEach(function (step, i) {
            var row = document.createElement('div');
            row.className = 'pipeline-step-row';
            row.setAttribute('role', 'button');
            row.setAttribute('tabindex', '0');
            row.setAttribute('aria-expanded', 'false');
            row.innerHTML =
                '<div class="pipeline-icon">' + step.icon + '</div>' +
                '<div><div class="pipeline-label">' + escapeHtml(step.label) + '</div></div>' +
                '<span class="pipeline-chevron">\u25B8</span>';

            var content = document.createElement('div');
            content.className = 'pipeline-step-content';
            content.innerHTML = buildExpandedContent(step.key, data);

            row.addEventListener('click', function () { userInteracted = true; toggle(i); });
            row.addEventListener('keydown', function (e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    userInteracted = true;
                    toggle(i);
                }
            });
            row.addEventListener('pointerenter', function () { userInteracted = true; });

            accordion.appendChild(row);
            accordion.appendChild(content);
            rows.push(row);
            contents.push(content);
        });

        function toggle(index) {
            if (cycleTimer) { clearTimeout(cycleTimer); cycleTimer = null; }
            if (currentOpen === index) {
                close(index);
                currentOpen = -1;
            } else {
                if (currentOpen >= 0) close(currentOpen);
                open(index);
                currentOpen = index;
            }
        }

        function open(index) {
            rows[index].setAttribute('aria-expanded', 'true');
            contents[index].setAttribute('data-open', 'true');

            if (index === 0 && data.claim_natural) {
                var claimEl = contents[0].querySelector('.pipeline-claim-text');
                if (claimEl) {
                    var w = claimEl.clientWidth - 10;
                    var size = autoFitFontSize(data.claim_natural, FONT_SERIF, w, 1.4, { minFont: 14, maxFont: 24, targetLines: 2 });
                    if (size) {
                        claimEl.style.fontSize = size + 'px';
                        claimEl.style.lineHeight = '1.4';
                    }
                }
            }
        }

        function close(index) {
            rows[index].setAttribute('aria-expanded', 'false');
            contents[index].removeAttribute('data-open');
        }

        interactiveEl.appendChild(accordion);

        staticEl.hidden = true;
        interactiveEl.hidden = false;

        function autoCycle(step) {
            if (userInteracted || step >= STEPS.length) return;
            toggle(step);
            cycleTimer = setTimeout(function () { autoCycle(step + 1); }, STEP_DURATION);
        }
        cycleTimer = setTimeout(function () { autoCycle(0); }, AUTO_CYCLE_DELAY);
    }

    function initMythCards() {
        var cards = document.querySelectorAll('.myth-card');
        if (!cards.length) return;

        var proofs = window.FEATURED_PROOFS_DATA || [];
        var disproved = proofs.filter(function (p) {
            return p.filter_value === 'disproved';
        });
        var quizMode = disproved.length >= 3;

        cards.forEach(function (card) {
            var filterVal = card.getAttribute('data-filter-value');
            if (quizMode && filterVal !== 'disproved') {
                card.style.display = 'none';
                return;
            }

            if (!quizMode) return;

            card.classList.add('myth-enhanced');
            var revealed = false;

            function reveal() {
                if (revealed) return;
                revealed = true;
                card.classList.add('myth-revealed');
            }

            card.addEventListener('pointerenter', reveal);
            card.addEventListener('focusin', reveal);
            card.addEventListener('click', function (e) {
                if (e.target.closest('.myth-card-link')) return;
                if (!revealed) { reveal(); return; }
                var url = card.getAttribute('data-proof-url');
                if (url) window.location.href = url;
            });

            var claimEl = card.querySelector('.myth-card-claim');
            if (claimEl) {
                var w = claimEl.clientWidth - 4;
                var size = autoFitFontSize(claimEl.textContent, FONT_SERIF, w, 1.4, { minFont: 14, maxFont: 20, targetLines: 2 });
                if (size) {
                    claimEl.style.fontSize = size + 'px';
                    claimEl.style.lineHeight = '1.4';
                    claimEl.style.fontFamily = "Georgia, 'Times New Roman', serif";
                }
            }
        });

        var visible = Array.from(cards).filter(function (c) { return c.style.display !== 'none'; });
        for (var i = 4; i < visible.length; i++) {
            visible[i].style.display = 'none';
        }
    }

    function start() {
        init();
        initMythCards();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }
})();
