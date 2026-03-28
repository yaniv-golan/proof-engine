(function () {
    var search = document.getElementById("search");
    var verdictFilter = document.getElementById("verdict-filter");
    var tagFilter = document.getElementById("tag-filter");
    var list = document.getElementById("proof-list");
    var proofs = [];

    var BADGE_CLASSES = {
        "proved": "badge-proved",
        "proved-qualified": "badge-proved-qualified",
        "disproved": "badge-disproved",
        "disproved-qualified": "badge-disproved-qualified",
        "partial": "badge-partial",
        "undetermined": "badge-undetermined",
    };

    function renderCard(p) {
        var tags = (p.tags || []).map(function (t) {
            return '<span class="tag">' + escapeHtml(t) + '</span>';
        }).join(" ");
        var badgeClass = BADGE_CLASSES[p.verdict_category] || "badge-undetermined";
        return '<a href="' + escapeHtml(p.url) + '" style="text-decoration:none;color:inherit;">' +
            '<div class="proof-card"><h3>' + escapeHtml(p.claim) + '</h3>' +
            '<div class="meta"><span class="badge ' + badgeClass + '">' + escapeHtml(p.verdict) + '</span> ' +
            tags + ' <span class="date">' + escapeHtml(p.date) + '</span></div></div></a>';
    }

    function escapeHtml(s) {
        var d = document.createElement("div");
        d.appendChild(document.createTextNode(s));
        return d.innerHTML;
    }

    function applyFilters() {
        var query = search.value.toLowerCase();
        var verdict = verdictFilter.value;
        var tag = tagFilter.value;

        var filtered = proofs.filter(function (p) {
            var matchesSearch = !query || p.claim.toLowerCase().indexOf(query) !== -1;
            var matchesVerdict = !verdict || p.verdict_filter === verdict;
            var matchesTag = !tag || (p.tags && p.tags.indexOf(tag) !== -1);
            return matchesSearch && matchesVerdict && matchesTag;
        });

        list.innerHTML = filtered.map(renderCard).join("");
        if (filtered.length === 0) {
            list.innerHTML = '<p style="color:var(--text-secondary);">No proofs match your filters.</p>';
        }
    }

    function populateTagFilter(allProofs) {
        var tags = {};
        allProofs.forEach(function (p) {
            (p.tags || []).forEach(function (t) { tags[t] = true; });
        });
        Object.keys(tags).sort().forEach(function (t) {
            var opt = document.createElement("option");
            opt.value = t;
            opt.textContent = t;
            tagFilter.appendChild(opt);
        });
    }

    fetch(window.CATALOG_JSON_URL)
        .then(function (r) { return r.json(); })
        .then(function (data) {
            proofs = data.proofs || [];
            populateTagFilter(proofs);
            applyFilters();
        })
        .catch(function () {
            list.innerHTML = '<p style="color:var(--text-secondary);">Failed to load proofs.</p>';
        });

    search.addEventListener("input", applyFilters);
    verdictFilter.addEventListener("change", applyFilters);
    tagFilter.addEventListener("change", applyFilters);
})();
