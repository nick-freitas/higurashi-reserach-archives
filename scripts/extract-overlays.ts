import fs from "node:fs";
import path from "node:path";

/**
 * Extract overlay data (our custom fields) from game_text/ JSON files
 * into separate overlay files in overlays/.
 *
 * Overlay fields (not in upstream source):
 *   - TextENGNew  (on MSGSET/LOGSET entries)
 *   - ENGNew      (on SAVEINFO entries)
 *   - significantChanges
 *   - changeReason
 *   - changeScore
 */

const OVERLAY_FIELDS = [
  "TextENGNew",
  "ENGNew",
  "significantChanges",
  "changeReason",
  "changeScore",
] as const;

const GAME_TEXT_DIR = path.resolve(
  import.meta.dirname ?? __dirname,
  "..",
  "game_text"
);
const OVERLAYS_DIR = path.resolve(
  import.meta.dirname ?? __dirname,
  "..",
  "overlays"
);

function main() {
  const startTime = Date.now();

  // Ensure output directory exists
  fs.mkdirSync(OVERLAYS_DIR, { recursive: true });

  // Read all JSON files
  const files = fs
    .readdirSync(GAME_TEXT_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  console.log(`Scanning ${files.length} JSON files in game_text/`);

  let filesCreated = 0;
  let totalOverlayEntries = 0;

  for (const file of files) {
    const filePath = path.join(GAME_TEXT_DIR, file);
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as any[];

    const overlayEntries: Record<string, any>[] = [];

    for (let i = 0; i < raw.length; i++) {
      const entry = raw[i];

      // Check if this entry has any overlay fields
      const hasOverlay = OVERLAY_FIELDS.some(
        (field) => field in entry && entry[field] != null
      );
      if (!hasOverlay) continue;

      // Build overlay object: always include index
      const overlay: Record<string, any> = { index: i };

      // Include MessageID when present (for verification)
      if ("MessageID" in entry && entry.MessageID != null) {
        overlay.MessageID = entry.MessageID;
      }

      // Include all overlay fields that exist and are non-null
      for (const field of OVERLAY_FIELDS) {
        if (field in entry && entry[field] != null) {
          overlay[field] = entry[field];
        }
      }

      overlayEntries.push(overlay);
    }

    // Skip files with no overlay data
    if (overlayEntries.length === 0) continue;

    // Write overlay file
    const outputPath = path.join(OVERLAYS_DIR, file);
    fs.writeFileSync(outputPath, JSON.stringify(overlayEntries, null, 2) + "\n");

    filesCreated++;
    totalOverlayEntries += overlayEntries.length;
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  console.log(`\nDone in ${elapsed}s`);
  console.log(`Files created: ${filesCreated}`);
  console.log(`Total overlay entries: ${totalOverlayEntries}`);
}

main();
