---
title: "Projects"
author: Abhay
type: page
date: 2026-09-08T09:00:00+00:00
url: /projects/
description: "Things I've built while working through the ideas on this site — local-first AI tools, desktop apps, and the design decisions behind them."
---

Writing about how AI systems behave is one thing. Shipping one is where the ideas get tested.

These are things I've built and use myself. Each page covers what the thing is, how it's put together, and the decisions that turned out to matter — including the ones I got wrong the first time.

## Vox — local voice-to-text

[**Vox**](/projects/vox/) is a cross-platform desktop app for voice dictation. Press a hotkey, speak, and the text appears in whatever app you're focused on.

The whole thing runs **offline**. Transcription happens on your machine via a bundled Whisper model — no cloud API, no account, no audio leaving your laptop. It's a Tauri app: Rust backend, React frontend, targeting macOS, Windows and Linux.

[![Vox settings window, showing the model manager](/images/projects/vox-models.webp)](/projects/vox/)

[Read the design →](/projects/vox/) · [Download →](https://github.com/devops-monk/vox/releases)

**Built with:** Tauri · Rust · React · whisper.cpp
