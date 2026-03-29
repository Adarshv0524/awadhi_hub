export type UserRole = "registered" | "moderator" | "admin";

export interface AuthUser {
  id: number;
  name: string | null;
  bio: string | null;
  email: string;
  username: string | null;
  role: UserRole;
  created_at?: string;
  email_verified?: boolean;
  pending_email?: string | null;
  permissions: number;
  permission_scopes?: unknown;
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
