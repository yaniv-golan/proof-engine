// catalog-enhance.js — Progressive enhancement for the proof catalog.
// Works ALONGSIDE catalog.js: creates a new #proof-list-enhanced container,
// hides the original #proof-list, renders all cards with animated filtering.
// If anything fails: remove #proof-list-enhanced, unhide #proof-list.
//
// Approach: render all cards as normal DOM nodes (not virtualized).
// On filter change, hide non-matching cards with CSS transitions
// (max-height → 0, opacity → 0). Remaining cards smoothly collapse
// together. For 106 proofs this is fast; virtualization can be added
// later when the catalog grows to 500+.

(function () {
    'use strict';

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

    var allProofs = [];
    var cardElements = {}; // slug -> wrapper element
    var originalList = null;
    var enhancedList = null;
    var resultCountEl = null;

    function escapeHtml(s) {
        var d = document.createElement('div');
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    function renderCard(p) {
        var tags = (p.tags || []).map(function (t) {
            return '<span class="tag">' + escapeHtml(t) + '</span>';
        }).join(' ');
        var badgeClass = BADGE_CLASSES[p.verdict_category] || 'badge-undetermined';
        var sourceHtml = '';
        if (p.source_names && p.source_names.length > 0) {
            var extra = p.source_names_extra > 0 ? ' +' + p.source_names_extra + ' more' : '';
            sourceHtml = '<div class="source-line">Sources: ' + p.source_names.map(escapeHtml).join(', ') + extra + '</div>';
        } else if (p.has_citations === false) {
            sourceHtml = '<div class="source-line">Pure computation — no external sources</div>';
        }
        return '<a href="' + escapeHtml(p.url) + '" class="card-link">' +
            '<div class="proof-card"><h3>' + escapeHtml(p.claim) + '</h3>' +
            '<div class="meta"><span class="badge ' + badgeClass + '">' + escapeHtml(p.verdict) + '</span> ' +
            tags + ' <span class="date">' + escapeHtml(p.date) + '</span></div>' +
            sourceHtml + '</div></a>';
    }

    function updateResultCount(count) {
        if (resultCountEl) {
            resultCountEl.textContent = 'showing ' + count +
                ' of ' + allProofs.length + ' proofs';
        }
    }

    function applyFilters() {
        var search = document.getElementById('search');
        var verdictFilter = document.getElementById('verdict-filter');
        var tagFilter = document.getElementById('tag-filter');

        var queryRaw = search ? search.value.toLowerCase().trim() : '';
        var queryWords = queryRaw ? queryRaw.split(/\s+/) : [];
        var verdict = verdictFilter ? verdictFilter.value : '';
        var tag = tagFilter ? tagFilter.value : '';

        var matchCount = 0;

        allProofs.forEach(function (p) {
            var slug = p.slug;
            var wrapper = cardElements[slug];
            if (!wrapper) return;

            var claimLower = p.claim.toLowerCase();
            var matchesSearch = queryWords.length === 0 || queryWords.every(function (w) {
                return claimLower.indexOf(w) !== -1;
            });
            var matchesVerdict = !verdict || p.verdict_filter === verdict;
            var matchesTag = !tag || (p.tags && p.tags.indexOf(tag) !== -1);
            var matches = matchesSearch && matchesVerdict && matchesTag;

            if (matches) {
                matchCount++;
                if (wrapper.classList.contains('card-hidden')) {
                    wrapper.classList.remove('card-hidden');
                    // Clear inline collapse styles, restore height
                    wrapper.style.opacity = '';
                    wrapper.style.marginBottom = '';
                    wrapper.style.maxHeight = wrapper.scrollHeight + 'px';
                }
            } else {
                if (!wrapper.classList.contains('card-hidden')) {
                    // Snapshot current height as inline style
                    wrapper.style.maxHeight = wrapper.scrollHeight + 'px';
                    // Force reflow so browser registers the starting value
                    wrapper.offsetHeight; // eslint-disable-line no-unused-expressions
                    // Now collapse to 0 via inline style (not CSS class,
                    // because inline styles override class styles)
                    wrapper.style.maxHeight = '0';
                    wrapper.style.opacity = '0';
                    wrapper.style.marginBottom = '0';
                    wrapper.classList.add('card-hidden');
                }
            }
        });

        updateResultCount(matchCount);

        // Show/hide empty state
        var emptyMsg = enhancedList.querySelector('.empty-state');
        if (matchCount === 0) {
            if (!emptyMsg) {
                emptyMsg = document.createElement('p');
                emptyMsg.className = 'empty-state';
                emptyMsg.textContent = 'No proofs match your filters.';
                enhancedList.appendChild(emptyMsg);
            }
        } else if (emptyMsg) {
            emptyMsg.parentNode.removeChild(emptyMsg);
        }
    }

    function teardown() {
        if (enhancedList && enhancedList.parentNode) {
            enhancedList.parentNode.removeChild(enhancedList);
        }
        if (resultCountEl && resultCountEl.parentNode) {
            resultCountEl.parentNode.removeChild(resultCountEl);
        }
        if (originalList) {
            originalList.style.display = '';
        }
        enhancedList = null;
        resultCountEl = null;
        cardElements = {};
    }

    function buildCards() {
        allProofs.forEach(function (p) {
            var wrapper = document.createElement('div');
            wrapper.className = 'card-wrapper';
            wrapper.innerHTML = renderCard(p);
            enhancedList.appendChild(wrapper);
            cardElements[p.slug] = wrapper;
        });
        // After all cards are in DOM, set max-height to actual height
        // so collapse animation is proportional to real card size
        requestAnimationFrame(function () {
            allProofs.forEach(function (p) {
                var wrapper = cardElements[p.slug];
                if (wrapper) {
                    wrapper.style.maxHeight = wrapper.scrollHeight + 'px';
                }
            });
        });
    }

    function init() {
        originalList = document.getElementById('proof-list');
        if (!originalList) return;

        var checkInterval = setInterval(function () {
            var existingCards = originalList.querySelectorAll('.proof-card');
            if (existingCards.length > 0 || originalList.querySelector('.empty-state')) {
                clearInterval(checkInterval);
                enhance();
            }
        }, 50);

        setTimeout(function () { clearInterval(checkInterval); }, 5000);
    }

    function enhance() {
        var jsonUrl = window.CATALOG_JSON_URL;
        if (!jsonUrl) return;

        fetch(jsonUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                allProofs = data.proofs || [];
                if (allProofs.length === 0) return;

                // Create the enhanced container
                enhancedList = document.createElement('div');
                enhancedList.id = 'proof-list-enhanced';
                originalList.parentNode.insertBefore(enhancedList, originalList.nextSibling);

                // Hide the original
                originalList.style.display = 'none';

                // Add result count
                resultCountEl = document.createElement('div');
                resultCountEl.className = 'result-count';
                enhancedList.parentNode.insertBefore(resultCountEl, enhancedList);
                updateResultCount(allProofs.length);

                // Render all cards
                buildCards();

                // Wire filter handlers
                var search = document.getElementById('search');
                var verdictFilter = document.getElementById('verdict-filter');
                var tagFilter = document.getElementById('tag-filter');

                if (search) search.addEventListener('input', applyFilters);
                if (verdictFilter) verdictFilter.addEventListener('change', applyFilters);
                if (tagFilter) tagFilter.addEventListener('change', applyFilters);
            })
            .catch(function () {
                teardown();
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
