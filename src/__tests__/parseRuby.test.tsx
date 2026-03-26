import { describe, it, expect } from "vitest";
import { renderToString } from "react-dom/server";
import { parseRuby } from "../utils/parseRuby";
import { createElement } from "react";

function render(node: ReturnType<typeof parseRuby>): string {
  return renderToString(createElement("span", null, node));
}

describe("parseRuby", () => {
  it("returns plain text when no ruby markup", () => {
    expect(parseRuby("hello world")).toBe("hello world");
  });

  it("converts [漢字]{かんじ} to ruby elements", () => {
    const html = render(parseRuby("[漢字]{かんじ}"));
    expect(html).toContain("<ruby>");
    expect(html).toContain("漢字");
    expect(html).toContain("<rt>かんじ</rt>");
  });

  it("handles mixed text and ruby", () => {
    const html = render(parseRuby("これは[漢字]{かんじ}です"));
    expect(html).toContain("これは");
    expect(html).toContain("<ruby>");
    expect(html).toContain("です");
  });

  it("handles multiple ruby in one string", () => {
    const html = render(
      parseRuby("[店内]{てんない}に[響]{ひび}いた")
    );
    expect(html).toContain("てんない");
    expect(html).toContain("ひび");
  });
});
