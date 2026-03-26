export interface Source {
  type: "arc" | "tips" | "fragment" | "common" | "miotsukushi" | "meta";
  arc?: string;
  chapter?: string;
  number?: number | string;
  letter?: string;
  section?: string;
  variant?: "omote" | "ura";
}
