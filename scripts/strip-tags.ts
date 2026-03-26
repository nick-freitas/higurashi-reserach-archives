export function stripTags(text: string): string {
  return (
    text
      // Voice tags: @vS##/##/########. (with trailing dot)
      .replace(/@vS\d+\/\d+\/\d+\./g, "")
      // Wait/delay tags: @w###. (with trailing dot)
      .replace(/@w\d+\./g, "")
      // Ruby annotation triplets: @bREADING.@<KANJI@> → keep KANJI
      .replace(/@b[^.]*\.@<([^@]*)@>/g, "$1")
      // @r → newline
      .replace(/@r/g, "\n")
      // @| text effect markers
      .replace(/@\|/g, "")
      // Remove remaining @ tags (@k, @b, etc.)
      .replace(/@[a-zA-Z]/g, "")
      // Remove backtick quotes used in English text
      .replace(/``/g, "")
  );
}
