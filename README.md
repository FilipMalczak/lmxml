# lmxml

**A serialization format readable for both LLMs and humans.**

I found that structured prompting yields great results. Instead of feeding the model a wall of text (possibly formatted
with Markdown or sprinkled with pseudo-XML tags), you can write your prompt in-memory as an object (anything JSON-like),
serialize it, and use it as a system or user prompt.

In my (non-benchmarked, but battle-tested) experience, models understand your intent much better that way — especially
the smaller ones.

---

## Why lmxml?

What do you use to serialize the prompts, though?

JSON is a first-class citizen in the world of tool-capable models, so why not that?

Because you might end up with a single-line prompt that’s hard to read and even harder to debug. You *can* pretty-print
it, but once you introduce multi-line text fields, you’re parsing `\n` in your own head — and mine started hurting the
first time I tried.

So, maybe YAML?

It *is* nicely formatted for human ingestion and supports `|`-style multi-line strings.  
Well… yes, but have fun configuring YAML serializers to reliably emit that flavor.

There’s TOON as well, but it’s optimized for token usage, not human readability.  
Let’s not even talk about INI or TOML — I think you already see how that won’t do us any good here.

But hey — every prompting guide tells you that XML-like `<tags>` make models understand structure better.  
So… maybe XML?

I liked that idea best, but the `eXtensible` part turns out to be a curse, not a feature, for this use case. There’s no
simple `xml.dumps(...)` in major XML libraries, so you’re forced to decide:

- which values become attributes
- how lists are represented
- whether to use CDATA
- how much whitespace matters

That’s basically what I’ve done.

`lmxml` stands for **Language Model XML** and is an *opinionated* way to produce XML-like text from JSON-ish data.

> Yes, I know that if you expand the acronym, you technically get  
> **Language Model eXtensible Modelling Language**.  
> I figure that “XML” is a proper noun these days (like YAML), so I’m willing to pay this silly price for a cute name.

---

## Core design principles

- **Indentation is mandatory and deterministic**
- **No attributes**, except one permitted attribute: `index` on `<item>` inside `<list>`
- **Everything is a tag** — most leaves are single-line: `<tag>value</tag>`
- **Multiline strings are supported**, but not indented:
  - opening and closing tags are indented
  - inner lines are raw (no leading spaces)
- **Collections:** only lists are first-class (tuples and sets are silently converted to lists)
- **Top-level primitives** are emitted as raw values (no wrapping `<None>` tag)
- **Primitives** are serialized using Python `str()` semantics (`True`, `False`, `42`, `3.14`)

The goal is not expressiveness — it’s *predictability*.

---

## Usage

As simple as this (which is the whole API surface btw):

```python
import lmxml

data = {
    "user": {
        "id": 42,
        "name": "Ada",
        "bio": "Researcher\nLoves coffee"
    },
    "tags": ["ml", "nlp"]
}

print(lmxml.dumps(data))
```

That snippet prints:

```
<user>
  <id>42</id>
  <name>Ada</name>
  <bio>
Researcher
Loves coffee
  </bio>
</user>
<tags>
  <list>
    <item index="0">ml</item>
    <item index="1">nlp</item>
  </list>
</tags>
```

### Pydantic support

If `pydantic` is importable, then you can feed any instance of `BaseModel` to `lmxml.dumps`. Following is an invariant:

```
x: pydantic.BaseModel
lmxml.dumps(x) == lmxml.dumps(x.model_dump(mode="json"))
```

---

## Where's the deserializer?

There isn’t one.

This is not a data transport format. It’s a way to take structured concepts and feed them to a model reliably, while
preserving both human readability and structural cues.

You can run the output through a standard XML parser, but you won’t get the original structure back out-of-the-box.
That’s intentional.

Unless you serialized a primitive (which is emitted as raw `str()`), parsing should always succeed — as in no
exceptions should be raised. 

There are some minor gotchas (HTML escaping, no CDATA for multi-line strings, XML character restrictions), but you’re
unlikely to hit them in normal prompting scenarios. If you do, 
[open an issue](https://github.com/FilipMalczak/lmxml/issues) — we’ll figure out whether it’s a bug or a feature.

---

## lmxml is intentionally boring.

If you need schemas, validation, round-tripping, or extensibility — use something else.

If you want prompts that are easy to read, hard to break, and easy for models to follow — lmxml is for you.

---

## Disclaimer for the AI age

I admit, this has been vibe-slapped together. ChatGPT can do surprisingly good job when writing code, although I did
that by chatting and copying its snippets. Anyway, even though most of the code has been conjured via LLM magic, it has
all been reviewed by yours truly (not like there was lots to review).