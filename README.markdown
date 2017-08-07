Feedmark
========

*Version 0.2-PRE.  Subject to change in backwards-incompatible ways without notice.*

Feedmark is a format for embedding entities in Markdown files with
accompanying metadata in a way which is both human-readable and
machine-extractable.  Feedmark is a subset of Markdown.

To this end, it is not dissimilar to [Falderal][], however it has
different goals.  It is more oriented for "curational" tasks.
[The Dossier][] is written in Feedmark format.

Informally, the format says that every `h3`-level heading in the
Markdown file gives the title of an entity, and may be followed
immediately by the entity's "plaque", which is a bullet list
where every item is prefixed by an identifier and a colon.

This repository contains a Python program, `feedmark`, which is an
implementation of an extractor for the Feedmark format.  It is
currently able to:

*   parse a set of Feedmark documents and extract entries from them
*   check that that the entries conform to a given schema
*   transform the entries in various ways (index by property, etc)
*   output the entries in other formats, including JSON,
    HTML, and Atom (née RSS) feeds
*   archive locally all the web objects linked to in the entries

Example Feedmark documents can be found in the `eg/` directory.
Further examples can be found in [The Dossier][].

[Falderal]: http://catseye.tc/node/Falderal
[The Dossier]: https://github.com/catseye/The-Dossier/

Example Usage
-------------

    bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml
    python -m SimpleHTTPServer 7000 &
    python -m webbrowser http://localhost:7000/feed.xml

Motivation
----------

Why is this desirable?  Because if your structured data format is
a subset of Markdown, the effort to format it into something
nicely human-readable is very small.  YAML and Markdown are both
fairly easy to read as raw text, but Github, for example,
automatically formats Markdown as HTML, making it that much nicer.

Or, if you like the transitivity: in the same way that a Markdown
file is still a readable text file, which is nice, a Feedmark file
is still a readable Markdown file, which is still a readable text
file, which is nice.

TODO
----

"common" properties on document which all entries within inherit.

Sub-entries.  Somehow.  For individual games in a series, implementations
or variations on a programming language, etc.

Finish schema checking - finer options, better example, etc.

Allow trailing `###` on h3-level headings.

### Interlink strategy

"Master Index" creation.

Preserve reference-style links in extracted sections.

Rewrite reference-style links that match a certain pattern, e.g.
the link text starts with `^`, so that they always go to the
canonical document in which the entry exists, since it may exist
in multiple.
