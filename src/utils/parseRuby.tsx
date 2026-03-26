import type { ReactNode } from "react";

const RUBY_PATTERN = /\[(.+?)\]\{(.+?)\}/g;

export function parseRuby(text: string): ReactNode {
  const parts: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  RUBY_PATTERN.lastIndex = 0;

  while ((match = RUBY_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }

    const [, kanji, kana] = match;
    parts.push(
      <ruby key={match.index}>
        {kanji}
        <rp>(</rp>
        <rt>{kana}</rt>
        <rp>)</rp>
      </ruby>
    );

    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  if (parts.length === 0) return text;
  if (parts.length === 1) return parts[0];
  return <>{parts}</>;
}
