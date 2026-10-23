/*
 * pagify default theme — client-side search.
 *
 * The build writes search-index.json next to the pages: one small JSON file
 * with each page's title, URL and text. This reads it once, lazily, the first
 * time the reader types. That keeps search working on any static host with no
 * server-side support and no build step for the frontend.
 *
 * The search box is a plain input in the generated markup; without this file
 * it simply does nothing, and the sidebar still navigates the whole site.
 *
 * Features:
 * - Trigram-based fuzzy search for typo tolerance
 * - Snippet extraction with highlighted matches
 * - Local search analytics (privacy-first, localStorage only)
 */

(function () {
  "use strict";

  var MIN_QUERY = 2;
  var MAX_RESULTS = 20;
  var SNIPPET_LENGTH = 160;
  var TRIGRAM_MIN_LEN = 3;

  function init() {
    var input = document.querySelector("[data-search]");
    var panel = document.querySelector("[data-search-panel]");
    var results = document.querySelector("[data-search-results]");
    var status = document.querySelector("[data-search-status]");
    if (!input || !panel || !results || !status) {
      return;
    }

    var source = input.getAttribute("data-search-index") || "/assets/search-index.json";
    var pages = null;
    var trigramIndex = null;
    var loading = null;

    function load() {
      if (pages) {
        return Promise.resolve(pages);
      }
      if (!loading) {
        loading = fetch(source)
          .then(function (response) {
            return response.ok ? response.json() : { documents: [] };
          })
          .then(function (index) {
            pages = (index.documents || []).map(function (doc) {
              return {
                title: doc.title || "",
                url: doc.url || "/",
                body: (doc.body || "").toLowerCase(),
                originalBody: doc.body || "",
              };
            });
            // Load trigram index if available (v2+ index format)
            if (index.trigramIndex) {
              trigramIndex = index.trigramIndex;
            }
            return pages;
          })
          .catch(function () {
            pages = [];
            trigramIndex = null;
            return pages;
          });
      }
      return loading;
    }

    function getTrigrams(text) {
      var trigrams = [];
      var words = text.toLowerCase().split(/\s+/);
      for (var i = 0; i < words.length; i++) {
        var word = words[i];
        if (word.length < TRIGRAM_MIN_LEN) continue;
        for (var j = 0; j <= word.length - TRIGRAM_MIN_LEN; j++) {
          trigrams.push(word.slice(j, j + 3));
        }
      }
      return trigrams;
    }

    function fuzzySearch(query) {
      var matches = [];
      var queryTrigrams = getTrigrams(query);

      pages.forEach(function (page, docID) {
        var score = 0;
        var title = page.title.toLowerCase();
        var body = page.body;

        // Exact title match (highest score)
        if (title === query) {
          score = 100;
        }
        // Title prefix match
        else if (title.indexOf(query) === 0) {
          score = 80;
        }
        // Title contains query
        else if (title.indexOf(query) >= 0) {
          score = 50;
        }
        // Body exact match
        else if (body.indexOf(query) >= 0) {
          score = 30;
        }
        // Fuzzy match via trigrams
        else if (trigramIndex && queryTrigrams.length > 0) {
          var matchCount = 0;
          for (var i = 0; i < queryTrigrams.length; i++) {
            var trigram = queryTrigrams[i];
            var docIDs = trigramIndex[trigram];
            if (docIDs && docIDs.indexOf(page.id) >= 0) {
              matchCount++;
            }
          }
          if (matchCount > 0) {
            // Score based on percentage of matched trigrams
            score = 10 + Math.floor((matchCount / queryTrigrams.length) * 20);
          }
        }

        if (score > 0) {
          matches.push({ page: page, score: score, id: page.id });
        }
      });

      matches.sort(function (a, b) {
        return b.score - a.score || a.page.title.localeCompare(b.page.title);
      });
      return matches;
    }

    function exactSearch(query) {
      var matches = [];
      pages.forEach(function (page) {
        var title = page.title.toLowerCase();
        var body = page.body;
        var inTitle = title.indexOf(query);
        if (inTitle < 0 && body.indexOf(query) < 0) {
          return;
        }
        var score = 1;
        if (inTitle === 0) {
          score = 4;
        } else if (inTitle > 0) {
          score = 3;
        }
        matches.push({ page: page, score: score });
      });
      matches.sort(function (a, b) {
        return b.score - a.score || a.page.title.localeCompare(b.page.title);
      });
      return matches;
    }

    function search(query) {
      // Use fuzzy search if query is long enough for trigrams, otherwise exact
      if (query.length >= TRIGRAM_MIN_LEN && trigramIndex) {
        return fuzzySearch(query);
      }
      return exactSearch(query);
    }

    function extractSnippet(body, query) {
      var lowerBody = body.toLowerCase();
      var lowerQuery = query.toLowerCase();
      var index = lowerBody.indexOf(lowerQuery);

      if (index < 0) {
        // Try to find partial matches
        var words = query.toLowerCase().split(/\s+/).filter(function(w) { return w.length > 1; });
        for (var i = 0; i < words.length; i++) {
          index = lowerBody.indexOf(words[i]);
          if (index >= 0) break;
        }
      }

      if (index < 0) {
        return body.slice(0, SNIPPET_LENGTH);
      }

      var start = Math.max(0, index - SNIPPET_LENGTH / 2);
      var end = Math.min(body.length, start + SNIPPET_LENGTH);

      // Adjust to word boundaries
      if (start > 0) {
        var space = body.indexOf(" ", start);
        if (space >= 0 && space < start + 20) start = space + 1;
      }
      if (end < body.length) {
        var space = body.lastIndexOf(" ", end);
        if (space >= 0 && space > end - 20) end = space;
      }

      return body.slice(start, end);
    }

    function show(matches, query) {
      results.textContent = "";
      if (matches.length === 0) {
        status.textContent = 'No matches for "' + query + '".';
        return;
      }
      status.textContent = matches.length + (matches.length === 1 ? " match" : " matches");
      matches.slice(0, MAX_RESULTS).forEach(function (match) {
        results.appendChild(resultItem(match, query));
      });
    }

    function trackSearch(query, resultCount) {
      // Privacy-first local analytics - stored only in localStorage
      try {
        var analyticsKey = "pagify:search-analytics";
        var data = JSON.parse(localStorage.getItem(analyticsKey) || "{}");
        var today = new Date().toISOString().slice(0, 10);

        if (!data[today]) {
          data[today] = { queries: {}, total: 0 };
        }
        data[today].total++;
        data[today].queries[query] = (data[today].queries[query] || 0) + 1;

        // Keep only last 30 days
        var keys = Object.keys(data).sort();
        if (keys.length > 30) {
          delete data[keys[0]];
        }

        localStorage.setItem(analyticsKey, JSON.stringify(data));
      } catch (e) {
        // Ignore storage errors (private browsing, quota exceeded, etc.)
      }
    }

    function show(matches, query) {
      results.textContent = "";
      if (matches.length === 0) {
        status.textContent = 'No matches for "' + query + '".';
        return;
      }
      status.textContent = matches.length + (matches.length === 1 ? " match" : " matches");
      trackSearch(query, matches.length);
      matches.slice(0, MAX_RESULTS).forEach(function (match) {
        results.appendChild(resultItem(match, query));
      });
    }

    input.addEventListener("input", function () {
      var query = input.value.trim().toLowerCase();
      if (query.length < MIN_QUERY) {
        panel.hidden = true;
        return;
      }
      load().then(function () {
        show(search(query), query);
        panel.hidden = false;
      });
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hidden) {
        input.value = "";
        panel.hidden = true;
        input.blur();
      }
    });

    // Keyboard navigation for results
    input.addEventListener("keydown", function (event) {
      if (event.key === "ArrowDown" && !panel.hidden) {
        event.preventDefault();
        var firstLink = results.querySelector("a");
        if (firstLink) firstLink.focus();
      }
    });
  }

  function resultItem(match, query) {
    var item = document.createElement("li");
    var link = document.createElement("a");
    link.href = match.page.url;

    var title = document.createElement("strong");
    // The title comes from the author's own frontmatter, so it is inserted as
    // text with the matching term marked, never as raw markup.
    title.appendChild(markMatch(document.createTextNode(match.page.title), match.page.title, query));

    var snippet = document.createElement("span");
    snippet.className = "search__snippet";
    var snippetText = extractSnippet(match.page.originalBody, query);
    snippet.appendChild(markMatch(document.createTextNode(snippetText), snippetText, query));

    link.appendChild(title);
    link.appendChild(snippet);
    item.appendChild(link);
    return item;
  }

  /* Splits a text node into plain and <mark> pieces around every match. */
  function markMatch(node, text, query) {
    var fragment = document.createDocumentFragment();
    var lower = text.toLowerCase();
    var offset = 0;
    var index = lower.indexOf(query.toLowerCase());

    while (index >= 0) {
      fragment.appendChild(document.createTextNode(text.slice(offset, index)));
      var mark = document.createElement("mark");
      mark.textContent = text.slice(index, index + query.length);
      fragment.appendChild(mark);
      offset = index + query.length;
      index = lower.indexOf(query.toLowerCase(), offset);
    }
    fragment.appendChild(document.createTextNode(text.slice(offset)));
    return fragment;
  }

  function extractSnippet(body, query) {
    var lowerBody = body.toLowerCase();
    var lowerQuery = query.toLowerCase();
    var index = lowerBody.indexOf(lowerQuery);

    if (index < 0) {
      var words = query.toLowerCase().split(/\s+/).filter(function(w) { return w.length > 1; });
      for (var i = 0; i < words.length; i++) {
        index = lowerBody.indexOf(words[i]);
        if (index >= 0) break;
      }
    }

    if (index < 0) {
      return body.slice(0, SNIPPET_LENGTH);
    }

    var start = Math.max(0, index - SNIPPET_LENGTH / 2);
    var end = Math.min(body.length, start + SNIPPET_LENGTH);

    if (start > 0) {
      var space = body.indexOf(" ", start);
      if (space >= 0 && space < start + 20) start = space + 1;
    }
    if (end < body.length) {
      var space = body.lastIndexOf(" ", end);
      if (space >= 0 && space > end - 20) end = space;
    }

    return body.slice(start, end);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();