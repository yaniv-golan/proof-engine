// 404.js — infers the URL the user tried to reach, renders it into the
// "proof trace" exhibit, stamps a trace_id, and wires up hint chips.
// A small Levenshtein pass against /search-index.json computes the
// "nearest slugs" count shown in the trace.

(function () {
    "use strict";

    // Priority:
    //   1. ?path= / ?p= / ?from= query param
    //   2. same-origin document.referrer
    //   3. location.pathname (skipping self-referrals to /404.html)
    //   4. placeholder
    function pickRequestedPath() {
        try {
            var params = new URLSearchParams(location.search);
            var qp = params.get("path") || params.get("p") || params.get("from");
            if (qp) return qp.charAt(0) === "/" ? qp : "/" + qp;

            if (document.referrer) {
                var ref = new URL(document.referrer);
                if (ref.origin === location.origin) {
                    var refPath = ref.pathname + ref.search;
                    if (refPath && !/\/404(\.html)?\/?$/.test(ref.pathname)) return refPath;
                }
            }

            var here = location.pathname;
            if (!/\/404(\.html)?\/?$/.test(here) && here !== "/") return here;
        } catch (_) { /* fall through */ }
        return "/unknown-slug";
    }

    function midTrunc(s, max) {
        if (s.length <= max) return s;
        var keep = Math.floor((max - 1) / 2);
        return s.slice(0, keep) + "…" + s.slice(-keep);
    }

    function setText(id, text) {
        var el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    var rawPath = pickRequestedPath();
    var pathShort = midTrunc(rawPath, 44);
    var pathBar = midTrunc(rawPath, 56);
    var host = (location.host || "proofengine.info").replace(/^www\./, "");
    var fetchDisplay = midTrunc(host + rawPath, 60);

    setText("path-url", pathBar);
    setText("claim-url", pathShort);
    setText("fetch-url", fetchDisplay);

    // Trace ID — deterministic hash of the requested path, 8 hex chars.
    var hash = 2166136261 >>> 0;
    for (var i = 0; i < rawPath.length; i++) {
        hash = ((hash * 31) + rawPath.charCodeAt(i)) >>> 0;
    }
    setText("trace-id", "404-" + hash.toString(16).padStart(8, "0"));

    // Hint chips → submit as search query against the catalog.
    var hints = document.getElementById("hints");
    if (hints) {
        hints.addEventListener("click", function (e) {
            var s = e.target.closest("span[data-q]");
            if (!s) return;
            var base = window.CATALOG_PATH || "/proofs/";
            location.href = base + "?q=" + encodeURIComponent(s.dataset.q);
        });
    }

    // Levenshtein-lite nearest-slug count. Lazy-load search index.
    function slugFromPath(p) {
        var m = p.match(/\/proofs\/([^\/\?#]+)/);
        return m ? m[1] : (p.replace(/^\/+|\/+$/g, "").split("/").pop() || "");
    }

    function levenshtein(a, b) {
        if (a === b) return 0;
        if (!a.length) return b.length;
        if (!b.length) return a.length;
        var v0 = new Array(b.length + 1);
        var v1 = new Array(b.length + 1);
        for (var i = 0; i <= b.length; i++) v0[i] = i;
        for (var i = 0; i < a.length; i++) {
            v1[0] = i + 1;
            for (var j = 0; j < b.length; j++) {
                var cost = a.charCodeAt(i) === b.charCodeAt(j) ? 0 : 1;
                v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
            }
            var tmp = v0; v0 = v1; v1 = tmp;
        }
        return v0[b.length];
    }

    var target = slugFromPath(rawPath).toLowerCase();
    if (target && window.SEARCH_INDEX_URL) {
        fetch(window.SEARCH_INDEX_URL, { credentials: "omit" })
            .then(function (r) { return r.ok ? r.json() : []; })
            .then(function (entries) {
                if (!Array.isArray(entries) || entries.length === 0) return;
                // Count slugs within an edit-distance threshold proportional to target length.
                var threshold = Math.max(2, Math.floor(target.length * 0.35));
                var near = 0;
                for (var i = 0; i < entries.length; i++) {
                    var slug = (entries[i].slug || "").toLowerCase();
                    if (!slug) continue;
                    if (slug === target) continue; // exact match = existing proof, skip
                    if (Math.abs(slug.length - target.length) > threshold) continue;
                    if (levenshtein(slug, target) <= threshold) near++;
                    if (near >= 99) break;
                }
                var label = near === 1 ? "1 candidate" : near + " candidates";
                setText("near-count", label);
            })
            .catch(function () { /* keep placeholder */ });
    }
})();
