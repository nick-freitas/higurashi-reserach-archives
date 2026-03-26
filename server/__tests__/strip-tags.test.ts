import { describe, it, expect } from "vitest";
import { stripTags } from "../strip-tags";

describe("stripTags", () => {
  it("converts @r to newline", () => {
    expect(stripTags("Hello@rWorld")).toBe("Hello\nWorld");
  });

  it("removes @k click-waits", () => {
    expect(stripTags("だから、@k嘘は言ってない")).toBe("だから、嘘は言ってない");
  });

  it("removes @b tags", () => {
    expect(stripTags("text@bmore")).toBe("textmore");
  });

  it("removes voice tags @vS##/##/###.", () => {
    expect(
      stripTags("Hello@vS01/09/120900002.World")
    ).toBe("HelloWorld");
  });

  it("removes inline voice tags within dialogue", () => {
    expect(
      stripTags(
        "圭一くんはまだ引っ越してきて日が浅いんだそうだね。@k@vS01/08/120800003.他の子たちと"
      )
    ).toBe("圭一くんはまだ引っ越してきて日が浅いんだそうだね。他の子たちと");
  });

  it("removes @w wait/delay tags with duration", () => {
    expect(stripTags("一度。@w800.……二度。")).toBe("一度。……二度。");
  });

  it("removes @| text effect markers", () => {
    expect(stripTags("text@|more")).toBe("textmore");
  });

  it("removes @b ruby annotation triplets", () => {
    expect(stripTags("@bやごうち.@<谷河内@>")).toBe("谷河内");
  });

  it("handles text with no tags", () => {
    expect(stripTags("clean text")).toBe("clean text");
  });

  it("handles empty string", () => {
    expect(stripTags("")).toBe("");
  });

  it("removes backtick quotes from English text", () => {
    expect(stripTags("``Hello, Keiichi-kun.``")).toBe("Hello, Keiichi-kun.");
  });
});
