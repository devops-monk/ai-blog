---
title: "{{ replace .Name "-" " " | title }}"
image: /images/articles/{{ .Name }}.webp
toc: true
date: {{ .Date }}
description: "One sentence that sells the article. This is what the RSS feed, the search index, the OpenGraph card and the JSON-LD all use — not decoration."
tags: ["llm"]
categories: ["Deep Dives"]
url: /{{ now.Format "2006/01" }}/{{ .Name }}/
series: "Part 1 — Foundations"
series_order: 1
draft: true
---
