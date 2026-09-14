# Screen Ruler

Measure anything on screen in pixels. The window itself is the ruler - transparent with a bright edge and real tick marks - or switch to clicking two points anywhere on screen for distance, components and angle.

A feature for [Mavis AI](https://www.mavis-ai.com) — a desktop voice assistant.

```
You: "open screen ruler"
```

Mavis opens it and stands its own panels down so they are not in your way. Say *"show the interface"* to bring them back.

## Install

From the Mavis Appstore — find **Screen Ruler** and click Install.

Or install it directly:

```python
from utils.feature_install import install_from_github
install_from_github("https://github.com/keefng8/screen-ruler")
```

## What you can say

- *"open screen ruler"*
- *"measure something on screen"*
- *"how many pixels is that"*
- *"check the size of this"*

These are not matched word for word. Mavis gives them to its language model as examples of intent, so close variations work too.

## How it works

Transparent with a bright edge, because seeing through it is the entire trick and is why this cannot be a web page. Aspect ratios reduce only when that says something: the cutoff is 64 rather than something tidier because 64:27 is every ultrawide monitor, and a tighter limit prints '2.37:1' - correct, useless, and it looks like the tool does not recognise a standard screen.

## Requirements

None. A single HTML file — it runs in your browser, offline, and nothing leaves your machine.

## Building your own

See [Building features for Mavis](https://github.com/keefng8/mavis-feature-docs) — a feature is just a GitHub repository with a `mavis.json`.

## License

MIT — see [LICENSE](LICENSE).
