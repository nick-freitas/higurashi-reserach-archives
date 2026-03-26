import { describe, it, expect, beforeEach } from "vitest";
import { loadAnnotations, saveAnnotation } from "../db";

describe("annotations (localStorage)", () => {
  beforeEach(() => localStorage.clear());

  it("returns empty object when no annotations exist", () => {
    expect(loadAnnotations()).toEqual({});
  });

  it("saves and loads an annotation", () => {
    saveAnnotation("file.json:123", { notes: "test note" });
    expect(loadAnnotations()["file.json:123"]).toEqual({ notes: "test note" });
  });

  it("merges annotation fields", () => {
    saveAnnotation("key", { notes: "a" });
    saveAnnotation("key", { editedENG: "b" });
    expect(loadAnnotations()["key"]).toEqual({ notes: "a", editedENG: "b" });
  });

  it("handles corrupted localStorage gracefully", () => {
    localStorage.setItem("higurashi-annotations", "not valid json{{{");
    expect(loadAnnotations()).toEqual({});
  });

  it("returns the updated map from saveAnnotation", () => {
    const result = saveAnnotation("a", { notes: "hello" });
    expect(result).toEqual({ a: { notes: "hello" } });
  });
});
