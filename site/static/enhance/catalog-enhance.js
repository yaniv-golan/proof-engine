// catalog-enhance.js — Progressive enhancement for the proof catalog.
// Works ALONGSIDE catalog.js: creates a new #proof-list-enhanced container
// with virtualized scrolling, hides the original #proof-list, and wires
// filters via addEventListener (both handlers fire, but catalog.js
// harmlessly updates a hidden container).
// If anything fails: remove #proof-list-enhanced, unhide #proof-list.

import { estimateCardHeight } from './pretext-measure.js';
import { Virtualizer, elementScroll, observeElementRect, observeElementOffset, measureElement } from '../vendor/tanstack-virtual-core.esm.min.js';

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
    var filteredProofs = [];
    var cardHeights = {}; // slug -> height
    var virtualizer = null;
    var cleanupMount = null;
    var originalList = null;   // #proof-list (catalog.js's container, never modified)
    var enhancedList = null;   // #proof-list-enhanced (our container)
    var innerContainer = null;
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

    function estimateAllCards(proofs, containerWidth) {
        var estimated = {};
        for (var i = 0; i < proofs.length; i++) {
            var p = proofs[i];
            var key = p.slug || i;
            var height = estimateCardHeight(p, containerWidth);
            if (height === null) return null; // Pretext failed
            estimated[key] = height;
        }
        return estimated;
    }

    function getCardHeight(index) {
        var p = filteredProofs[index];
        var key = p.slug || index;
        // Use Pretext estimate as initial size; TanStack will correct
        // with actual DOM measurement via measureElement after render
        return cardHeights[key] || 100;
    }

    function updateResultCount() {
        if (resultCountEl) {
            resultCountEl.textContent = 'showing ' + filteredProofs.length +
                ' of ' + allProofs.length + ' proofs';
        }
    }

    function applyFilters() {
        var search = document.getElementById('search');
        var verdictFilter = document.getElementById('verdict-filter');
        var tagFilter = document.getElementById('tag-filter');

        var query = search ? search.value.toLowerCase() : '';
        var verdict = verdictFilter ? verdictFilter.value : '';
        var tag = tagFilter ? tagFilter.value : '';

        filteredProofs = allProofs.filter(function (p) {
            var matchesSearch = !query || p.claim.toLowerCase().indexOf(query) !== -1;
            var matchesVerdict = !verdict || p.verdict_filter === verdict;
            var matchesTag = !tag || (p.tags && p.tags.indexOf(tag) !== -1);
            return matchesSearch && matchesVerdict && matchesTag;
        });

        updateResultCount();

        if (filteredProofs.length === 0) {
            enhancedList.innerHTML = '<p class="empty-state">No proofs match your filters.</p>';
            innerContainer = null;
            virtualizer = null;
            return;
        }

        // Rebuild virtualizer with new items
        setupVirtualizer();
    }

    function renderVirtualItems() {
        if (!virtualizer) return;

        virtualizer._willUpdate();

        var items = virtualizer.getVirtualItems();
        var totalHeight = virtualizer.getTotalSize();
        innerContainer.style.height = totalHeight + 'px';
        innerContainer.style.position = 'relative';

        // Clear and re-render visible items
        while (innerContainer.firstChild) {
            innerContainer.removeChild(innerContainer.firstChild);
        }

        items.forEach(function (item) {
            var div = document.createElement('div');
            div.className = 'virtual-item';
            div.style.top = item.start + 'px';
            div.setAttribute('data-index', item.index);
            div.innerHTML = renderCard(filteredProofs[item.index]);
            innerContainer.appendChild(div);
        });
    }

    // Tear down the enhanced container and restore catalog.js visibility
    function teardown() {
        if (cleanupMount) {
            cleanupMount();
            cleanupMount = null;
        }
        if (enhancedList && enhancedList.parentNode) {
            enhancedList.parentNode.removeChild(enhancedList);
        }
        if (resultCountEl && resultCountEl.parentNode) {
            resultCountEl.parentNode.removeChild(resultCountEl);
        }
        if (originalList) {
            originalList.style.display = '';
        }
        virtualizer = null;
        enhancedList = null;
        innerContainer = null;
        resultCountEl = null;
    }

    function setupVirtualizer() {
        if (!enhancedList) return;

        try {
            // Clean up previous mount if re-setting up
            if (cleanupMount) {
                cleanupMount();
                cleanupMount = null;
            }

            // Build inner container
            enhancedList.innerHTML = '';
            innerContainer = document.createElement('div');
            enhancedList.appendChild(innerContainer);

            // TanStack Virtual Core is framework-agnostic and requires DOM adapter
            // functions for scroll observation. We use the exported implementations
            // that framework packages (react-virtual, etc.) normally supply.
            //
            // estimateSize gives Pretext's pre-computed estimate for initial layout.
            // measureElement corrects with actual DOM height after render, so
            // approximate estimates don't cause drift or overlap.
            virtualizer = new Virtualizer({
                count: filteredProofs.length,
                getScrollElement: function () { return enhancedList; },
                estimateSize: function (index) { return getCardHeight(index); },
                measureElement: measureElement,
                overscan: 5,
                onChange: renderVirtualItems,
                scrollToFn: elementScroll,
                observeElementRect: observeElementRect,
                observeElementOffset: observeElementOffset,
            });

            // Set container height for scrolling
            var viewportHeight = window.innerHeight;
            var listTop = enhancedList.getBoundingClientRect().top;
            var availableHeight = viewportHeight - listTop - 48; // 48px buffer for footer
            enhancedList.style.height = Math.max(400, availableHeight) + 'px';

            // Apply styles for virtual scrolling
            enhancedList.style.overflowY = 'auto';
            enhancedList.style.position = 'relative';

            // TanStack lifecycle: mount after scroll element is in DOM
            cleanupMount = virtualizer._didMount();

            renderVirtualItems();
        } catch (e) {
            // Virtualizer failed — tear down enhanced container, unhide original
            console.warn('catalog-enhance: Virtualizer failed, restoring fallback', e);
            teardown();
        }
    }

    function init() {
        originalList = document.getElementById('proof-list');
        if (!originalList) return;

        // Wait for catalog.js to finish rendering cards
        var checkInterval = setInterval(function () {
            var existingCards = originalList.querySelectorAll('.proof-card');
            if (existingCards.length > 0 || originalList.querySelector('.empty-state')) {
                clearInterval(checkInterval);
                enhance();
            }
        }, 50);

        // Timeout after 5 seconds — don't wait forever
        setTimeout(function () { clearInterval(checkInterval); }, 5000);
    }

    function enhance() {
        // Fetch index.json independently (don't reuse catalog.js's data)
        var jsonUrl = window.CATALOG_JSON_URL;
        if (!jsonUrl) return;

        fetch(jsonUrl)
            .then(function (r) { return r.json(); })
            .then(function (data) {
                allProofs = data.proofs || [];
                if (allProofs.length === 0) return;

                // Measure all card heights using originalList's width
                var containerWidth = originalList.offsetWidth;
                var measured = estimateAllCards(allProofs, containerWidth);
                if (measured === null) return; // Pretext failed, keep catalog.js rendering

                cardHeights = measured;
                filteredProofs = allProofs.slice();

                // Create the enhanced container as a sibling AFTER #proof-list
                enhancedList = document.createElement('div');
                enhancedList.id = 'proof-list-enhanced';
                originalList.parentNode.insertBefore(enhancedList, originalList.nextSibling);

                // Hide the original list (catalog.js keeps working, just invisible)
                originalList.style.display = 'none';

                // Add result count element before the enhanced container
                resultCountEl = document.createElement('div');
                resultCountEl.className = 'result-count';
                enhancedList.parentNode.insertBefore(resultCountEl, enhancedList);
                updateResultCount();

                // Wire filter handlers on the SAME filter elements using addEventListener.
                // Both handlers fire, but catalog.js harmlessly updates the hidden #proof-list.
                var search = document.getElementById('search');
                var verdictFilter = document.getElementById('verdict-filter');
                var tagFilter = document.getElementById('tag-filter');

                if (search) search.addEventListener('input', applyFilters);
                if (verdictFilter) verdictFilter.addEventListener('change', applyFilters);
                if (tagFilter) tagFilter.addEventListener('change', applyFilters);

                // Set up virtualization in the new container
                setupVirtualizer();

                // Handle resize with debounce
                var resizeTimer;
                window.addEventListener('resize', function () {
                    clearTimeout(resizeTimer);
                    resizeTimer = setTimeout(function () {
                        var newWidth = enhancedList.offsetWidth;
                        var remeasured = estimateAllCards(allProofs, newWidth);
                        if (remeasured) {
                            cardHeights = remeasured;
                            setupVirtualizer();
                        }
                    }, 150);
                });
            })
            .catch(function () {
                // Fetch or measurement failed — tear down anything we created
                teardown();
            });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
