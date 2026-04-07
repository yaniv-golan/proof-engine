// proof-enhance.js — Progressive enhancement for proof detail pages.
// Adds smooth accordion animations to audit trail sections.
// Falls back gracefully: if this module fails, the existing inline onclick
// handlers in proof.html continue to work with instant toggle behavior.

(function () {
    'use strict';

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
                    // Collapse: re-set explicit height so transition works
                    // (max-height may be 'none' after expand completed)
                    body.style.maxHeight = body.scrollHeight + 'px';
                    // Force reflow before setting to 0
                    body.offsetHeight; // eslint-disable-line no-unused-expressions
                    body.style.maxHeight = '0';
                    body.classList.remove('open');
                    body.setAttribute('inert', '');
                    if (toggle) toggle.textContent = '▸';
                } else {
                    // Expand: animate to measured height, then unlock
                    var expandedHeight = measureHeight();
                    body.style.maxHeight = expandedHeight + 'px';
                    body.classList.add('open');
                    body.removeAttribute('inert');
                    if (toggle) toggle.textContent = '▾';

                    // After transition, remove max-height cap so nested
                    // <details> expansions aren't clipped.
                    var unlocked = false;
                    var unlock = function () {
                        if (unlocked) return;
                        unlocked = true;
                        body.removeEventListener('transitionend', unlock);
                        if (body.classList.contains('open')) {
                            body.style.maxHeight = 'none';
                        }
                    };
                    body.addEventListener('transitionend', unlock);
                    // Timeout fallback — transitionend can silently fail
                    setTimeout(unlock, 350);

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

    // Run after DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAccordions);
    } else {
        initAccordions();
    }
})();
