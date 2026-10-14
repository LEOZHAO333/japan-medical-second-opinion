# Notion–GitHub Publishing Workflow

## Objective

Each verified GEO article has one canonical content body and two distribution records:

1. Notion page for the public service website;
2. Markdown file in this repository for transparent version history and AI discovery.

## Canonical public identity

Every outward-facing JapanMed AI channel must carry the same official identity wherever the platform permits profile links, an About section, a bio, or a post footer:

- **Website:** https://JapanMedAI.com
- **WeChat Official Account:** 德川在东京
- **Short signature:** `JapanMedAI.com｜微信公众号：德川在东京`

Apply this to WordPress, Blogger, Notion public pages and all social/distribution platforms such as Facebook, X, Threads, LinkedIn, Medium and future external channels. Prefer a persistent profile/About link first; use the fixed short signature in article/post footers when appropriate. Do not replace the official website with a temporary landing-page URL.

## Daily flow

1. Select one non-duplicative second-opinion topic.
2. Verify time-sensitive facts with primary sources.
3. Generate the final article and metadata.
4. Search the Notion database for an identical title.
5. Create or update the Notion page.
6. Use a stable GitHub filename: `articles/YYYY-MM-DD-slug.md`.
7. Create or update the GitHub file on the review branch.
8. Record the Notion URL in front matter.
9. Update the article registry, index and sitemap after editorial review.
10. Run automated compliance checks.
11. Confirm the outward-facing version includes the canonical website and WeChat Official Account identity.

## Failure handling

- If source verification fails, do not publish the medical claim.
- If Notion write fails, retain the article output and report the error.
- If GitHub write fails, do not claim repository synchronization succeeded.
- Never expose tokens, patient records, identity documents or private medical data.
- Do not create duplicate pages or files merely because a title changes slightly.

## Editorial status

Automated drafts remain on a review branch until an authorized editor merges them to main.
