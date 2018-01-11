Feedmark
========

*Version 0.5-PRE.  Subject to change in backwards-incompatible ways without notice.*

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

Example Feedmark documents can be found in the `eg/` directory.
Further examples can be found in [The Dossier][].

Implementation
--------------

This repository contains a Python program, `feedmark`, which is a
reference implementation of a processor for the Feedmark format.
It is currently able to do the following things:

### Parse Feedmark documents

which will check that they are minimally well-formed.

    bin/feedmark eg/*.md

### Archive all web objects linked to from the documents

    bin/feedmark --archive-links-to=downloads eg/Recent\ Llama\ Sightings.md

If it is only desired that the links be checked, `--check-links` will
make `HEAD` requests and will not save any of the responses.

### Convert Feedmark documents to an Atom (née RSS) feed

    bin/feedmark "eg/Recent Llama Sightings.md" --output-atom=feed.xml
    python -m SimpleHTTPServer 7000 &
    python -m webbrowser http://localhost:7000/feed.xml

### Check entries against a schema

A Feedmark schema is simply another Feedmark document, one in which
each entry describes a property that entries should have.

    bin/feedmark eg/*Sightings*.md --check-against=eg/schema/Llama\ sighting.md

Note that this facility is still under development.

### Rewrite documents in-place

They will be parsed as Feedmark, and then output as Markdown, to the
same files that were read in as input.  (Note!  This is destructive;
it is recommended that the original files be under version control such
as `git`, which will easily allow the changes to be reverted.)

    bin/feedmark --rewrite-markdown eg/*.md

### Interlink documents

Markdown supports "reference-style" links, which are not inline
with the text.

`feedmark` can rewrite reference-style links that match the name of
an entry in a previously-created "refdex", so that they
can be kept current and point to the canonical document in which the
entry exists, since it may exist in multiple, or be moved over time.

    bin/feedmark eg/*.md --output-refdex >refdex.json
    bin/feedmark --input-refdex=refdex.json --rewrite-markdown eg/*.md

### Write out to miscellaneous formats

Output entries as JSON, indexed by entry, or by property, or by
publication date

    bin/feedmark --output-json eg/*.md
    bin/feedmark --by-property eg/*.md
    bin/feedmark --by-publication-date eg/*.md

Output entries as Markdown, or HTML.  In the latter case, `h3` headings
will get `id` attributes which let them serve as link anchors.

    bin/feedmark --output-markdown eg/*.md
    bin/feedmark --output-html eg/*.md

Motivation
----------

Why is Feedmark desirable?  Because if your structured data format is
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

Handle redirects (301, 302) better when archiving external links.

"common" properties on document which all entries within inherit.

Sub-entries.  Somehow.  For individual games in a series, implementations
or variations on a programming language, etc.

Allow trailing `###` on h3-level headings.

Index creation from refdex, for permalinks.

[Falderal]: http://catseye.tc/node/Falderal
[The Dossier]: https://github.com/catseye/The-Dossier/
