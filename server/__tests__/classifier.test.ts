import { describe, it, expect } from "vitest";
import { classifyFilename } from "../classifier";

describe("classifyFilename", () => {
  it("classifies tips files", () => {
    expect(classifyFilename("tips_042.json")).toEqual({
      type: "tips",
      number: 42,
    });
  });

  it("classifies fragment files", () => {
    expect(classifyFilename("fragment_j3.json")).toEqual({
      type: "fragment",
      letter: "J",
      number: "3",
    });
  });

  it("classifies fragment files with letter suffix", () => {
    expect(classifyFilename("fragment_l1b.json")).toEqual({
      type: "fragment",
      letter: "L",
      number: "1b",
    });
  });

  it("classifies common files", () => {
    expect(classifyFilename("common_day2_1.json")).toEqual({
      type: "common",
      section: "day2_1",
    });
  });

  it("classifies miotsukushi omote files", () => {
    expect(classifyFilename("miotsukushi_omote_12.json")).toEqual({
      type: "miotsukushi",
      variant: "omote",
      chapter: "12",
    });
  });

  it("classifies miotsukushi ura files", () => {
    expect(classifyFilename("miotsukushi_ura_05.json")).toEqual({
      type: "miotsukushi",
      variant: "ura",
      chapter: "05",
    });
  });

  it("classifies chapternames as meta", () => {
    expect(classifyFilename("chapternames.json")).toEqual({
      type: "meta",
    });
  });

  it("classifies arc files with numeric chapter", () => {
    expect(classifyFilename("onikakushi_05.json")).toEqual({
      type: "arc",
      arc: "onikakushi",
      chapter: "05",
    });
  });

  it("classifies arc files with _end suffix", () => {
    expect(classifyFilename("onikakushi_end.json")).toEqual({
      type: "arc",
      arc: "onikakushi",
      chapter: "end",
    });
  });

  it("classifies arc files with _badend1 suffix", () => {
    expect(classifyFilename("yoigoshi_badend1.json")).toEqual({
      type: "arc",
      arc: "yoigoshi",
      chapter: "badend1",
    });
  });

  it("classifies arc files with _afterparty suffix", () => {
    expect(classifyFilename("himatsubushi_afterparty.json")).toEqual({
      type: "arc",
      arc: "himatsubushi",
      chapter: "afterparty",
    });
  });

  it("classifies book files with compound prefix", () => {
    expect(classifyFilename("book_01_prologue.json")).toEqual({
      type: "arc",
      arc: "book_01",
      chapter: "prologue",
    });
  });

  it("classifies miotsukushi bad end files", () => {
    expect(classifyFilename("miotsukushi_omote_badend1.json")).toEqual({
      type: "miotsukushi",
      variant: "omote",
      chapter: "badend1",
    });
  });
});
