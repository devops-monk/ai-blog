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

## Lector — local text-to-speech

[**Lector**](/projects/lector/) is Vox pointed the other way. Select text anywhere — an article, a PDF, a pull request — press a hotkey, and hear it read aloud. Or import a book and have it read to you, with the words highlighted as they are spoken.

Also fully **offline**, and with no Python: the speech engine links statically into the binary, so there is no interpreter, no sidecar and no port to bind. 181 voices across twelve models, each auditionable before you commit to it, and around 75,000 free books searchable from inside the app.

[![Lector reading The Jungle Book, the sentences already spoken highlighted and the rest waiting](/images/projects/lector-reading.webp)](/projects/lector/)

[Read the design →](/projects/lector/) · [Download →](https://github.com/devops-monk/lector/releases)

**Built with:** Tauri · Rust · sherpa-onnx · Kokoro &amp; Piper

## Vox — local voice-to-text

[**Vox**](/projects/vox/) is a cross-platform desktop app for voice dictation. Press a hotkey, speak, and the text appears in whatever app you're focused on.

The whole thing runs **offline**. Transcription happens on your machine via a bundled Whisper model — no cloud API, no account, no audio leaving your laptop. It's a Tauri app: Rust backend, React frontend, targeting macOS, Windows and Linux.

[![Vox settings window, showing the model manager](/images/projects/vox-models.webp)](/projects/vox/)

[Read the design →](/projects/vox/) · [Download →](https://github.com/devops-monk/vox/releases)

**Built with:** Tauri · Rust · React · whisper.cpp
