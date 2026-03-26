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
npm run dev
```

This starts both the Express API server and the Vite dev server. The app will be available at `http://localhost:4737`.

## Project structure

```
src/           React frontend
server/        Express API (indexer, search, arc browser)
game_text/     Bilingual JSON dialogue files
py_scripts/    Python translation and scoring scripts
tests/         Test files
data/          Runtime data (annotations)
```

## License

The source code in this repository is licensed under the [MIT License](LICENSE).

The game text data in `game_text/` originates from the [HigurashiENX-texts](https://github.com/masagrator/HigurashiENX-texts) repository by masagrator and is **excluded** from this license — see `LICENSE` and `THIRD_PARTY_NOTICES` for details.
