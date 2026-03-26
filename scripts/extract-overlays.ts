import fs from "node:fs";
import path from "node:path";

/**
 * Extract overlay data (our custom fields) from game_text/ JSON files
 * into separate overlay files in overlays/, keyed against UPSTREAM structure.
 *
 * This ensures overlays use upstream file positions (filename + array index)
 * rather than game_text positions, which may have shuffled content in some
 * tips files.
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

const scriptDir = import.meta.dirname ?? __dirname;

const GAME_TEXT_DIR = path.resolve(scriptDir, "..", "game_text");
const SOURCE_DIR = path.resolve(
  process.env.SOURCE_DIR ?? path.join(scriptDir, "..", "upstream")
);
const OVERLAYS_DIR = path.resolve(scriptDir, "..", "overlays");

interface UpstreamLocation {
  filename: string;
  index: number;
}

function main() {
  const startTime = Date.now();

  if (!fs.existsSync(SOURCE_DIR)) {
    console.error(`Upstream directory not found: ${SOURCE_DIR}`);
    console.error(`Set SOURCE_DIR env var or clone upstream repo to ./upstream`);
    process.exit(1);
  }

  // Ensure output directory exists
  fs.mkdirSync(OVERLAYS_DIR, { recursive: true });

  // ── Step 1: Build global MessageID -> {filename, index} map from upstream ──

  console.log(`Building MessageID map from upstream: ${SOURCE_DIR}`);

  const upstreamFiles = fs
    .readdirSync(SOURCE_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  // MessageID -> upstream location
  const messageIdMap = new Map<number, UpstreamLocation>();
  // Cache of upstream file data: filename -> entries[]
  const upstreamCache = new Map<string, any[]>();

  for (const file of upstreamFiles) {
    const filePath = path.join(SOURCE_DIR, file);
    const entries = JSON.parse(fs.readFileSync(filePath, "utf-8")) as any[];
    upstreamCache.set(file, entries);

    for (let i = 0; i < entries.length; i++) {
      const entry = entries[i];
      if (entry.MessageID != null) {
        if (messageIdMap.has(entry.MessageID)) {
          console.warn(
            `Duplicate MessageID ${entry.MessageID} in upstream: ${file}[${i}] and ${messageIdMap.get(entry.MessageID)!.filename}[${messageIdMap.get(entry.MessageID)!.index}]`
          );
        }
        messageIdMap.set(entry.MessageID, { filename: file, index: i });
      }
    }
  }

  console.log(
    `Indexed ${messageIdMap.size} MessageIDs from ${upstreamFiles.length} upstream files`
  );

  // ── Step 2: Read game_text files and extract overlays keyed to upstream ──

  const gameTextFiles = fs
    .readdirSync(GAME_TEXT_DIR)
    .filter((f) => f.endsWith(".json"))
    .sort();

  console.log(`\nScanning ${gameTextFiles.length} JSON files in game_text/`);

  // Accumulate overlays per upstream filename
  const overlaysByFile = new Map<string, Record<string, any>[]>();

  let totalOverlayEntries = 0;
  let remappedToOtherFile = 0;
  let remappedWithinFile = 0;
  let unmatchedMessageIds = 0;
  let saveinfosMatched = 0;

  for (const file of gameTextFiles) {
    const filePath = path.join(GAME_TEXT_DIR, file);
    const raw = JSON.parse(fs.readFileSync(filePath, "utf-8")) as any[];

    for (let i = 0; i < raw.length; i++) {
      const entry = raw[i];

      // Check if this entry has any overlay fields
      const hasOverlay = OVERLAY_FIELDS.some(
        (field) => field in entry && entry[field] != null
      );
      if (!hasOverlay) continue;

      // Build overlay data (fields only, no index/file yet)
      const overlayData: Record<string, any> = {};

      // Include all overlay fields that exist and are non-null
      for (const field of OVERLAY_FIELDS) {
        if (field in entry && entry[field] != null) {
          overlayData[field] = entry[field];
        }
      }

      // Determine the correct upstream file and index
      let targetFile: string;
      let targetIndex: number;

      if (entry.MessageID != null) {
        // MSGSET with MessageID: look up in upstream map
        const location = messageIdMap.get(entry.MessageID);
        if (!location) {
          console.warn(
            `MessageID ${entry.MessageID} from game_text/${file}[${i}] not found in any upstream file — skipping`
          );
          unmatchedMessageIds++;
          continue;
        }

        targetFile = location.filename;
        targetIndex = location.index;

        if (targetFile !== file) {
          remappedToOtherFile++;
        } else if (targetIndex !== i) {
          remappedWithinFile++;
        }
      } else {
        // SAVEINFO/LOGSET without MessageID: match by array index in same file
        // Verify the upstream file exists and has this index
        const upstreamEntries = upstreamCache.get(file);
        if (!upstreamEntries) {
          console.warn(
            `game_text/${file} has no corresponding upstream file — skipping SAVEINFO at index ${i}`
          );
          continue;
        }
        if (i >= upstreamEntries.length) {
          console.warn(
            `game_text/${file}[${i}] index out of bounds in upstream (${upstreamEntries.length} entries) — skipping`
          );
          continue;
        }

        targetFile = file;
        targetIndex = i;
        saveinfosMatched++;
      }

      // Build the final overlay entry
      const overlay: Record<string, any> = { index: targetIndex };

      // Include MessageID for verification when present
      if (entry.MessageID != null) {
        overlay.MessageID = entry.MessageID;
      }

      // Add overlay fields
      Object.assign(overlay, overlayData);

      // Accumulate into the correct file
      if (!overlaysByFile.has(targetFile)) {
        overlaysByFile.set(targetFile, []);
      }
      overlaysByFile.get(targetFile)!.push(overlay);
      totalOverlayEntries++;
    }
  }

  // ── Step 3: Write overlay files, sorted by index ──

  let filesCreated = 0;

  for (const [file, entries] of overlaysByFile) {
    // Sort by index for consistent output
    entries.sort((a, b) => a.index - b.index);

    const outputPath = path.join(OVERLAYS_DIR, file);
    fs.writeFileSync(outputPath, JSON.stringify(entries, null, 2) + "\n");
    filesCreated++;
  }

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

  console.log(`\nDone in ${elapsed}s`);
  console.log(`Files created: ${filesCreated}`);
  console.log(`Total overlay entries: ${totalOverlayEntries}`);
  console.log(`  - SAVEINFO/non-MessageID entries matched by index: ${saveinfosMatched}`);
  console.log(`  - Entries remapped to different upstream file: ${remappedToOtherFile}`);
  console.log(`  - Entries remapped to different index (same file): ${remappedWithinFile}`);
  if (unmatchedMessageIds > 0) {
    console.warn(`  - MessageIDs not found in upstream (skipped): ${unmatchedMessageIds}`);
  }
}

main();
