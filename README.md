<div align="center">
    <div>
        <h2>Breakout and Pong</h2>
        <em>made in pygame for <a href="https://boot.dev">boot.dev</a> personal project</em>
        <h4>literally just a mashup of pong and breakout</h4>
    </div>
    <div>
        <img src="screenshots/gameplay.png" alt="gameplay screenshot" width="600">
    </div>
    <div>
        <img  src="screenshots/settings.png" alt="settings screenshot" width="600">
    </div>
</div>

## Play

**[▶ Play in your browser](https://Markbu8.github.io/breakoutpong/)**

Or download the latest `.exe` from [Releases](../../releases), or run from source (below).

## Controls

| Action | Key |
| --- | --- |
| Left paddle up / down | W / S |
| Right paddle up / down | I / K |
| Pause / resume | Esc |
| Reset to menu | Space |
| Click buttons / drag sliders | Mouse |

## Install

Requires Python 3.10+ and Pygame 2.6.1+

```
git clone https://github.com/Markbu8/breakoutpong
cd breakoutpong
uv sync
uv run python main.py
```

## Build for web

The web version is built with [pygbag](https://github.com/pygame-web/pygbag) and deployed via GitHub Pages.

```
uv run pygbag --build webroot
cp -r webroot/build/web docs
```
Then in GitHub: **Settings → Pages → Branch: `web` /docs → Save**
