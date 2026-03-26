# Higurashi Archives

A research and analysis tool for studying the nuances between the original Japanese text of *Higurashi: When They Cry* (07th Expansion) and the community-created English translation from the [HigurashiENX](https://github.com/masagrator/HigurashiENX) project.

## Features

- **Bilingual search** — Full-text search across both Japanese and English dialogue with KWIC (keyword-in-context) results
- **Arc browser** — Navigate the story by book, arc, and chapter with paginated reading
- **Side-by-side comparison** — View Japanese and English text together with detailed context
- **Translation change scoring** — Identify and filter significant translation differences
- **Character filtering** — Filter dialogue by speaker
- **Annotations** — Add and view notes on specific dialogue entries

## Getting started

```
npm install
git clone --depth 1 https://github.com/masagrator/HigurashiENX-texts.git upstream
npm run build:wasm
SOURCE_DIR=./upstream npm run build:db
npm run dev
```

The build:db step clones the upstream source text, merges it with the overlay data in `overlays/`, and generates a SQLite database that the app loads client-side.

## Project structure

```
src/           React frontend
scripts/       Build scripts (merge, DB generation, overlay extraction)
overlays/      Our translation analysis data (new translations, scores)
py_scripts/    Python translation and scoring scripts
tests/         Test files
public/        Static assets (generated DB, WASM)
```

## How it works

The upstream game text lives in a [separate repository](https://github.com/masagrator/HigurashiENX-texts). This repo stores only our analysis overlay data (new translations, significance scores, change reasons) in `overlays/`. At build time, a merge script combines them into a SQLite database that the React app queries client-side via sql.js (WASM). No server required — hosted as a static site on GitHub Pages.

## License

The source code in this repository is licensed under the [MIT License](LICENSE).

The overlay data in `overlays/` contains derivative analysis of text from the [HigurashiENX-texts](https://github.com/masagrator/HigurashiENX-texts) repository by masagrator, which has no explicit license — see `LICENSE` and `THIRD_PARTY_NOTICES` for details.
