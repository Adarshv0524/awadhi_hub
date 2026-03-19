// src/lib/submissions.ts
import { api } from "./api";

/**
 * createSubmission: posts to /submissions
 * body shape based on backend `submissions` model (see openapi)
 *
 * Minimal required fields:
 *  - content_type (string)
 *  - main_text (string)
 *  - contributor_id is handled server-side via auth
 *
 * Optional:
 *  - meaning, is_classical, author_slug, work_slug, chapter_slug,
 *    number_in_chapter, external_references (object), status, visibility
 */
export async function createSubmission(payload: Record<string, any>) {
  return await api("/submissions", { method: "POST", body: payload });
}

export async function listMySubmissions(params?: {
  status?: string;
  content_type?: string;
  offset?: number;
  limit?: number;
}) {
  const queryParams = new URLSearchParams();
  if (params?.status) queryParams.set("status", params.status);
  if (params?.content_type) queryParams.set("content_type", params.content_type);
  if (params?.offset !== undefined) queryParams.set("offset", String(params.offset));
  if (params?.limit !== undefined) queryParams.set("limit", String(params.limit));
  
  const queryString = queryParams.toString();
  return await api(`/submissions/me${queryString ? `?${queryString}` : ""}`);
}

// Authors / Works / Chapters helpers (use existing backend routes)
export async function listAuthors() {
  return await api("/authors");
}

export async function listWorksForAuthor(authorSlug: string) {
  return await api(`/authors/${encodeURIComponent(authorSlug)}/works`);
}

export async function listChaptersForWork(authorSlug: string, workSlug: string) {
  return await api(
    `/authors/${encodeURIComponent(authorSlug)}/works/${encodeURIComponent(workSlug)}/chapters`
  );
}

/**
 * Delete a submission (soft delete)
 * Backend: DELETE /submissions/{id}
 * Only allowed for the submission owner (contributor)
 */
export async function deleteSubmission(submissionId: number | string) {
  return await api(`/submissions/${submissionId}`, { method: "DELETE" });
}
