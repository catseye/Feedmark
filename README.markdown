Feedmark
========

*Version 0.0, very much work-in-progress and subject to change*

Feedmark is a format for embedding entities in Markdown files with
accompanying metadata in a way which is both human-readable and
machine-extractable.  Feedmark is a subset of Markdown.

To this end, it is not dissimilar to [Falderal][], however it has
different goals.  It is more oriented for "curational" tasks.
[The Dossier] is (nominally) written in Feedmark format.

Informally, the format says that every `h3`-level heading in the
Markdown file gives the title of an entity, and may be followed
immediately by the entity's "plaque", which is a bullet list
where every item is prefixed by an identifier and a colon.

This repository contains a Python program, `feedmark`, which is an
implementation of an extractor for the Feedmark format.  It is
currently able to convert a Feedmark document to an Atom feed.

Example Feedmark documents can be found in the `eg/` directory.

[Falderal]: http://catseye.tc/node/Falderal
[The Dossier]: https://github.com/catseye/The-Dossier/

Example Usage
-------------

    bin/feedmark "eg/Recent Llama Sightings.md" feed.xml
    python -m SimpleHTTPServer 7000 &
    python -m webbrowser http://localhost:7000/feed.xml
