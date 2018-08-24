History of Feedmark
===================

0.6
---

*   Uses the `toc` extension that ships with `markdown` to generate
    heading-anchors (instead of a home-rolled function for that.)
*   Heading anchors are generated on all header levels, not just `h3`.

0.5
---

*   Format of JSON written by `--output-json` cleaned up; documents
    are given in a list, sections in a document are also in lists.
*   Functionality for generating a table of contents has been removed.
    Example script that generates a ToC from `feedmark --output-json`
    is provided in the `eg` directory instead.

0.4
---

*   Checking links now works for local files; it checks they are in
    the directory specified as `--article-root`.
*   Archiving targets of links is "more idempotent":
    *   if the file has not changed, it is not changed on disk
    *   if it has changed, the old file is renamed to a datestamped name
    *   `--archive-missing-only` only downloads if not already have it
*   Writing the anchor `id` of `h3` elements is now much faster, as it
    is now done with a Markdown extension instead of BeautifulSoup.
*   `preamble` of a document is now formatted the same way as the `body`
    of each section in the document.
*   HISTORY document.
*   Other small fixes.

0.3
---

*   Output JSON with `--output-json`.  Also `--by-publication-date`.
*   Output links with `--output-links`.
*   Multiple input refdexes can be read with `--input-refdexes`.
*   A prefix can be virtually appended to every filename in the
    input refdexes using `--input-refdex-filename-prefix`.
*   Output a table of contents.
*   Some internal refactoring.
*   Rudimentary test suite.
*   Other small fixes.

0.2
---

*   Check documents against schema.
*   Check, and archive the targets of, links in documents.
*   Output Markdown and HTML from input Feedmark documents.
*   Rewrite Feedmark documents in-place.
*   Create and use a refdex file (reference-style links.)
*   Other small fixes.

0.1
---

*   Initial release.
*   Ability to create an Atom feed from a Markdown document.
