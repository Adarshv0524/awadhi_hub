export type UserRole = "registered" | "moderator" | "admin";

export interface AuthUser {
  id: number;
  email: string;
  username: string | null;
  role: UserRole;
  permissions: number;
}

export const submissionSchemas = {
  dictionary: {
    label: "Dictionary",
    fields: ["lemma_devanagari", "lemma_roman", "meaning"],
  },
  doha: {
    label: "Doha",
    fields: ["main_text", "meaning"],
  },
  idiom: {
    label: "Idiom",
    fields: ["main_text", "meaning", "usage_example"],
  },
  article: {
    label: "Article",
    fields: ["title", "content", "excerpt"],
  },
};
