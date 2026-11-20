# Chapter 01

State: pages 01-08 reviewed, English dialogue final, live in the private reader on build 2.05.
Pages 09-20 are not drawn yet; the script stops at page_08 and nothing past it is invented here.

## Page set in the reader

| Page | Reader file | Dialog | Review |
|---|---|---|---|
| p01 | `assets/panels/ch01/p01.jpg` | EN final | reviewed |
| p02 | `assets/panels/ch01/p02.jpg` | EN final | reviewed |
| p03 | `assets/panels/ch01/p03.jpg` | EN final | reviewed |
| p04 | `assets/panels/ch01/p04.jpg` | EN final | reviewed |
| p05 | `assets/panels/ch01/p05.jpg` | EN final | reviewed |
| p06 | `assets/panels/ch01/p06.jpg` | EN final | reviewed |
| p07 | `assets/panels/ch01/p07.jpg` | EN final | reviewed |
| p08 | `assets/panels/ch01/p08.jpg` | EN final | reviewed |

Insert panels `05A` and `05B` belong inside page 05's beat. They are mapped, not separate
reader pages.

## Release queue (the gate before a slot can run)

So a weekly upload does not fall behind, pages are stocked ahead of time. A page that has art
but no slot yet goes in with `"status": "queued"` plus an `"air_date": "YYYY-MM-DD"`. The reader
never renders a queued page; when the slot comes, flip `status` to `reviewed` and rebuild.

```json
{ "page": "p09", "file": "assets/panels/ch01/p09.jpg",
  "dialog": "en-final", "status": "queued", "air_date": "2026-11-23" }
```

`python3 build_reader.py --chapter 1 --check` reports the queue and exits non-zero while fewer
than 4 pages are stocked or any queued page is missing a valid air date. Today: 0 stocked.

## Not decided here

Chapter-level canon calls (final climax panel, headband term, character name changes) stay
open until ACC. This folder records state; it does not settle canon.
