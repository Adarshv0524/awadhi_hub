// src/lib/interactions.ts
// API helpers for user interactions (likes, bookmarks, shares, reports)

import { api } from "./api";

export type InteractionType = "like" | "bookmark";

/**
 * Toggle a like or bookmark for content
 * @returns {active: boolean, likes_count: number, bookmarks_count: number}
 */
export async function toggleInteraction(
  content_type: string,
  content_id: number,
  interaction: InteractionType
) {
  return api("/interactions/toggle", {
    method: "POST",
    body: {
      content_type,
      content_id,
      interaction,
      metadata: {
        user_agent: navigator.userAgent,
        timestamp: new Date().toISOString(),
      },
    },
  });
}

/**
 * Record a share event
 * @param channel - 'link', 'twitter', 'facebook', etc.
 * @returns {shares_count: number}
 */
export async function shareContent(
  content_type: string,
  content_id: number,
  channel: string
) {
  return api("/interactions/share", {
    method: "POST",
    body: {
      content_type,
      content_id,
      metadata: { 
        channel,
        user_agent: navigator.userAgent,
      },
    },
  });
}

/**
 * Report content for moderation
 * @param reason - 'spam', 'abuse', 'copyright', 'other'
 * @returns {report_id: number, status: string}
 */
export async function reportContent(
  content_type: string,
  content_id: number,
  reason: string,
  note?: string
) {
  return api("/interactions/report", {
    method: "POST",
    body: {
      content_type,
      content_id,
      reason,
      note,
      metadata: {
        user_agent: navigator.userAgent,
      },
    },
  });
}

/**
 * Get user's bookmarked content
 * @returns {count: number, results: Array}
 */
export async function getUserBookmarks(
  userId: number,
  limit = 20,
  offset = 0
) {
  return api(
    `/interactions/users/${userId}/bookmarks?limit=${limit}&offset=${offset}`
  );
}

/**
 * Get user's liked content
 * @returns {total_count: number, results: Array}
 */
export async function getUserLikes(
  userId: number,
  limit = 20,
  offset = 0
) {
  return api(
    `/interactions/users/${userId}/likes?limit=${limit}&offset=${offset}`
  );
}
