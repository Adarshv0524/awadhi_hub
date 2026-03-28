import * as v from "valibot";

const baseSchema = v.object({
  content_type: v.string(),
  main_text: v.optional(v.string()),
  meaning: v.optional(v.string()),
  title: v.optional(v.string()),
  idiom_text_roman: v.optional(v.string()),
  dictionarySenses: v.optional(
    v.array(
      v.object({
        definition: v.optional(v.string()),
      })
    )
  ),
});

export type SubmissionValidationInput = v.InferInput<typeof baseSchema>;

export function validateSubmissionPayload(input: SubmissionValidationInput): string | null {
  const parsed = v.safeParse(baseSchema, input);
  if (!parsed.success) {
    return "Invalid submission payload.";
  }

  const contentType = String(input.content_type || "").trim();

  if (contentType === "idiom") {
    if (!String(input.main_text || "").trim()) {
      return "Idiom submissions require main text.";
    }
    if (!String(input.idiom_text_roman || "").trim()) {
      return "Idiom submissions require Romanized Text (text_roman).";
    }
  }

  if (contentType === "dictionary") {
    const senses: Array<{ definition?: string }> = Array.isArray(input.dictionarySenses) ? input.dictionarySenses : [];
    const senseCount = senses.filter((sense: { definition?: string }) => String(sense?.definition || "").trim()).length;
    if (senseCount < 1) {
      return "Dictionary submissions require at least one sense/definition.";
    }
  }

  if (contentType === "article") {
    if (!String(input.title || "").trim()) {
      return "Article submissions require a title.";
    }
  }

  return null;
}
