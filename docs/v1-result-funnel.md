# V1 result-page handoff · 2026-10-06

Task: P0-20261006-RESULTS. Owner: GPT-2. Scope: existing tools, no new tool.

## Behavior

- Second opinion: explain what self-selected records mean, three preparation steps,
  one primary CTA opening a copyable records checklist. Summary/contact are optional.
- Weight: explain the nonclinical result, three small next steps, one primary CTA
  opening the existing type's seven habit prompts. Profile/share controls are optional.
- Weight changes cover Simplified Chinese, Traditional Chinese and English.
- Checklists work without registration, contact information or record upload.
- Clipboard denial reveals selected text in the page instead of losing the action in a dialog.

## Measurement

Existing tables remain insert-only for anonymous clients. Do not add a public dashboard.
`scripts/enable_funnel_events.sql` was applied on 2026-10-06 as
`v1_result_funnel_event_support_20261006`: both a CHECK constraint and
RLS policy restricted event names. The expansion adds only `result_viewed`
and `next_step_clicked`, preserving previous restrictions.

`landing_view`, `quiz_started`, `quiz_completed`, `result_viewed`, `next_step_clicked`
use the same browser-tab/tool session and first-source label. Refresh within 30 minutes
keeps that session; 30 minutes without a tracked action starts another. This is not a
person count, and separate tabs/devices cannot be reliably deduplicated.

Results are counted only when visible in the viewport. Every new event carries
`event_data.page_version=v1-next-step-20261006` and locale. A restored result can generate
exposure without a new completion; do not divide CTA by quiz completions.

CTA rate = distinct sessions clicking the primary next step / distinct sessions seeing
the result, within the same period, tool and page version. Zero denominator is N/A.
Consultations require anonymized manual confirmation, not a click or uploaded record.

Local/preview hosts, recognized automation and `?jmai_qa=1` send no analytics rows.
The QA marker persists in sessionStorage in that tab. `?jmai_qa=0` clears the marker,
but does not override preview/automation exclusion. Do not use a campaign containing
`test` to infer self-testing: a genuine promotion test can use that word.

New telemetry excludes answers, result types, medical summaries, contacts and raw
referrer queries. Use non-sensitive UTM identifiers only (e.g. v1_geo_01, cta_records_v1).
Locale/source does not establish domestic or overseas market: leave market unknown
unless an independent non-sensitive record supports it.

Known limits: browser bot detection is partial; unmarked human self-tests cannot be
recovered automatically; storage denial prevents reliable session persistence. Older
events lack version/exposure fields and must not be treated as the new baseline.

## Review and release

This change contains product/process copy, not treatment recommendations or patient
cases. No L4 article, WordPress file, publishing workflow or content queue is changed.
Existing 2026-10-05 GEO source links match the correct PMDA document and JHN002 PMID
33186684. It still needs professional medical review and a verified next-step link
before any new outward distribution under V1.3.

Production release remains separate from the code review. Revert the code commit to
roll back; the additive event-name support is compatible with older clients.

## Validation receipt

- Five Node tests passed: test exclusion, tab/session persistence and idle rotation,
  payload privacy, storage denial, and deduplication with failed-write retry.
- Eight Chromium checks passed: 390px and 1440px viewports for second opinion,
  weight Simplified Chinese, Traditional Chinese and English. Completed the test,
  opened the checklist, denied clipboard permission and verified visible copy text.
- All three weight versions retained `1/7` after reload; the completed-day button
  stayed disabled. Challenge invite remained visible and copyable after clipboard denial.
- The Simplified Chinese challenge-invite handler had a missing DOM binding;
  fixed it. Localized invitation URLs now consistently include an explicit invite kind.
- No JavaScript errors or horizontal overflow were detected in these checks.
  Local/preview QA sent zero Supabase POST requests.
- Database checks inserted both new event names as `anon` inside a rolled-back
  transaction. Unknown events were rejected. RLS remained enabled and `anon`
  SELECT remained denied on both tables. No fixture events were retained.
- These are software checks, not evidence of medical review, mainland access,
  mobile native-share support, real-user conversion or consultation counts.

Review receipt: task `P0-20261006-RESULTS`; known unresolved P0 = 0; production
release = HOLD pending code review and release decision. Claude-3 review has not
been received. There is no new L4 treatment article in this patch.

## 2026-10-08 follow-up

Continue PR #58; do not open a duplicate. Founder accepted proceeding with the
two proposed primary CTA labels. Simplified Chinese now uses
`获取我的资料准备清单` and `获取我的7天轻量行动清单`.
The destination stays an in-page copyable checklist, with no contact gate.

Read-only inspection on 2026-10-08 confirmed both production INSERT policies
already allow `result_viewed` and `next_step_clicked`; no additional schema or
policy change was performed. Five Node tests passed again. The previous eight
Chromium checks above are dated 2026-10-06: do not describe them as fresh checks.
The retained local Chromium executables were truncated and could not launch;
fresh hosted-preview interaction checks are tracked separately below.

Hosted preview verification on 2026-10-08: the browser reached Vercel login,
and the connected Vercel protected-fetch tool returned 403 at
`read_protection_bypass`. The current connection does not authorize this
deployment/project/team. No login, access-control change or protection disable
was attempted. Therefore fresh hosted-preview UI verification is blocked,
not passed. The source and database capability checks do not prove deployment.

### Claude-3 review handoff

- Task: P0-20261006-RESULTS / PR #58.
- Scope: result-page explanations, three next steps, one primary checklist CTA,
  shared funnel events, clipboard fallback, existing challenge invite repair.
- Review: event privacy and session attribution; restored-result denominator;
  visible-result exposure; clipboard/mobile behavior; anonymous insert-only RLS.
- Source: PR diff and this document. If private links cannot be read, use the
  full diff; never infer behavior from filenames or the PR title.
- Requested receipt: task ID, P0/P1/P2 counts, blocking reasons, review head SHA,
  and any Founder decision. No Claude review or Approved status is claimed.
- Release: HOLD until the outstanding review/release decision is recorded.

This is a software/product change. The October 5 medical article remains
pending professional review; its status is unaffected by this PR.
