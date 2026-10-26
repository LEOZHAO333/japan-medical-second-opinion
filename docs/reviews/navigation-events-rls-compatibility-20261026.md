# Anonymous navigation tracking fix — 2026-10-26

## Verified database observation
Read-only SQL against the connected Supabase project:
- `public.jmai_site_events`: RLS enabled, anon role has INSERT, the current INSERT policy allows `knowledge_intent` and `second_opinion_click`, but **not** `internal_link_click`.
- The website's `assets/jmai-analytics.js` generic `[data-jmai-track]` handler previously emitted `internal_link_click` for each navigational CTA. Such events do not satisfy the published site table INSERT policy and are therefore liable to 403/42501 rejections. Recent 30-day site event counts confirmed no `internal_link_click` rows.
- `public.jmai_second_opinion_events` does allow `wechat_click`/`email_click`/`second_opinion_click`; no permissions change is needed. Their absence as event names over 30 days in that table is not proof of RLS blocking.

## Patch (only one frontend JS file, no database change)
The existing internal navigation event listener now maps:
- Relative `/second-opinion/*` destinations → existing permitted `second_opinion_click`;
- Other tagged internal navigation destinations → existing permitted `knowledge_intent`.

Preserve the safe metadata whitelist `kind`, `cta_id`, `cta_position`, limited to fixed allowlisted token formats, plus existing anonymous session/UTM attribution. No disease names, filenames, selected symptoms, form fields or patient contact information are sent. No extension to `anon` database privileges or RLS event allowlists.

## Validation
- Test route matching: `/second-opinion/`, `/second-opinion/#contact`, `/second-opinion/?utm_source=x`, `/second-opinion/cancer/` should be counted as second-opinion navigations; `/second-opinion-other/` should not.
- Existing `[data-jmai-track]` events from knowledge hubs are counted as `knowledge_intent`.
- The existing `second_opinion_intent` event from homepage may coexist with `second_opinion_click`; keep them distinct and avoid summing both as two actual people.
- Preview check: Vercel + S0 + mobile click (real network response must be 201/204 and no console error).
- After release, perform controlled test clicks that do not involve PHI; confirm anonymized records and correct CTA IDs in Supabase. Do not claim verified production event storage until that test succeeds.

## Review gates
Claude code security review, JS static lint/syntax, existing analytics privacy invariants and browser preview; Founder approval before merge. The change is safe against the current database policy but expands front-end event recording for existing tracked links and should be reviewed as an analytics behavior change.
