// proof-enhance.js — Progressive enhancement for proof detail pages.
// Adds smooth accordion animations to audit trail sections.
// Falls back gracefully: if this module fails, the existing inline onclick
// handlers in proof.html continue to work with instant toggle behavior.

(function () {
    'use strict';

    function initVerdictFlow() {
        var title = document.querySelector('.proof-title');
        var banner = document.querySelector('.verdict-banner');
        if (!title || !banner) return;

        var badge = banner.querySelector('.badge');
        var info = banner.querySelector('.verdict-info');
        if (!badge) return;

        // Create floating verdict container (hidden initially).
        // Use <span> not <div> — .proof-title is an <h1>, and putting a
        // block element inside an h1 is invalid HTML. We use display:block
        // via the .verdict-float CSS class to get block layout from a span.
        var floater = document.createElement('span');
        floater.className = 'verdict-float';
        floater.appendChild(badge.cloneNode(true));
        if (info) {
            floater.appendChild(info.cloneNode(true));
        }

        // State: is the float currently active?
        var floatActive = false;

        function activateFloat() {
            if (floatActive) return;
            title.insertBefore(floater, title.firstChild);
            banner.style.display = 'none';
            // Add class to parent so .proof-meta gets clear:both
            title.parentNode.classList.add('verdict-float-active');
            floatActive = true;
        }

        function deactivateFloat() {
            if (!floatActive) return;
            if (floater.parentNode) floater.parentNode.removeChild(floater);
            banner.style.display = '';
            title.parentNode.classList.remove('verdict-float-active');
            floatActive = false;
        }

        // Use matchMedia so we respond to resize properly
        var mql = window.matchMedia('(min-width: 641px)');
        function handleViewport(e) {
            if (e.matches) {
                activateFloat();
            } else {
                deactivateFloat();
            }
        }
        mql.addEventListener('change', handleViewport);
        handleViewport(mql); // apply initial state
    }

    function initAccordions() {
        var sections = document.querySelectorAll('.audit-section');
        if (!sections.length) return;

        sections.forEach(function (section) {
            var header = section.querySelector('.audit-header');
            var body = section.querySelector('.audit-body');
            if (!header || !body) return;

            // Measure the expanded height by briefly rendering off-screen
            function measureHeight() {
                if (body.dataset.expandedHeight) {
                    return parseInt(body.dataset.expandedHeight, 10);
                }
                // Temporarily make visible but off-screen to measure
                body.classList.remove('animated');
                body.style.display = 'block';
                body.style.visibility = 'hidden';
                body.style.position = 'absolute';
                body.style.width = section.offsetWidth + 'px';
                body.style.padding = '14px';

                var height = body.scrollHeight;

                // Reset
                body.style.display = '';
                body.style.visibility = '';
                body.style.position = '';
                body.style.width = '';
                body.style.padding = '';
                body.classList.add('animated');

                body.dataset.expandedHeight = height;
                return height;
            }

            // Switch to animated mode: start closed.
            // Set inert attribute so collapsed content is excluded from
            // tab order and assistive technology (accessibility fix).
            var wasOpen = body.classList.contains('open');
            body.classList.remove('open');
            body.classList.add('animated');
            if (!wasOpen) body.setAttribute('inert', '');

            if (wasOpen) {
                // If it was already open (shouldn't happen on load, but defensive)
                var h = measureHeight();
                body.style.maxHeight = h + 'px';
                body.classList.add('open');
            }

            // Replace the inline onclick with our animated version.
            // cloneNode(true) copies the onclick attribute, so we must
            // explicitly remove it to prevent double-toggle.
            var newHeader = header.cloneNode(true);
            newHeader.removeAttribute('onclick');
            header.parentNode.replaceChild(newHeader, header);

            newHeader.addEventListener('click', function () {
                var toggle = newHeader.querySelector('.toggle');
                var isOpen = body.classList.contains('open');

                if (isOpen) {
                    // Collapse
                    body.style.maxHeight = '0';
                    body.classList.remove('open');
                    body.setAttribute('inert', '');
                    if (toggle) toggle.textContent = '▸';
                } else {
                    // Expand
                    var expandedHeight = measureHeight();
                    body.style.maxHeight = expandedHeight + 'px';
                    body.classList.add('open');
                    body.removeAttribute('inert');
                    if (toggle) toggle.textContent = '▾';

                    // Fire GA event (preserve existing analytics)
                    var sectionName = newHeader.querySelector('span');
                    if (sectionName && typeof gtag === 'function') {
                        gtag('event', 'audit_expand', {
                            section_name: sectionName.textContent
                        });
                    }
                }
            });
        });

        // Invalidate cached heights on resize (content reflows at new width)
        var resizeTimer;
        window.addEventListener('resize', function () {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function () {
                sections.forEach(function (section) {
                    var body = section.querySelector('.audit-body');
                    if (!body) return;
                    delete body.dataset.expandedHeight;
                    // If currently open, re-measure and update max-height
                    if (body.classList.contains('open')) {
                        body.classList.remove('animated');
                        body.style.display = 'block';
                        body.style.visibility = 'hidden';
                        body.style.position = 'absolute';
                        body.style.width = section.offsetWidth + 'px';
                        body.style.padding = '14px';
                        var height = body.scrollHeight;
                        body.style.display = '';
                        body.style.visibility = '';
                        body.style.position = '';
                        body.style.width = '';
                        body.style.padding = '';
                        body.classList.add('animated');
                        body.dataset.expandedHeight = height;
                        body.style.maxHeight = height + 'px';
                    }
                });
            }, 200);
        });
    }

    function init() {
        initVerdictFlow();
        initAccordions();
    }

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
