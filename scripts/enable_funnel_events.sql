-- Additive event support. Preserve anonymous insert-only access and all existing events.
-- Apply once as a reviewed Supabase migration before deploying the new clients.
BEGIN;
ALTER TABLE public.jw_weight_events DROP CONSTRAINT jw_weight_events_event_name_check;
ALTER TABLE public.jw_weight_events ADD CONSTRAINT jw_weight_events_event_name_check CHECK (
  event_name IN ('landing_view','quiz_started','quiz_completed','profile_generated',
    'summary_copied','whatsapp_intent','wechat_intent','email_intent','contact_section_viewed',
    'library_intent','medical_tool_view','share_intent','share_link_copied','invite_landing',
    'buddy_compare_generated','share_card_generated','share_card_downloaded','challenge_opened',
    'challenge_started','daily_checkin_completed','daily_task_completed','challenge_completed',
    'result_viewed','next_step_clicked')
);
ALTER POLICY public_weight_event_insert ON public.jw_weight_events WITH CHECK (
  event_name IN ('landing_view','quiz_started','quiz_completed','profile_generated',
    'summary_copied','whatsapp_intent','wechat_intent','email_intent','contact_section_viewed',
    'library_intent','medical_tool_view','share_intent','share_link_copied','invite_landing',
    'buddy_compare_generated','share_card_generated','share_card_downloaded','challenge_opened',
    'challenge_started','daily_checkin_completed','daily_task_completed','challenge_completed',
    'result_viewed','next_step_clicked')
  AND char_length(COALESCE(source,'')) <= 100
  AND char_length(COALESCE(country_region,'')) <= 100
  AND char_length(COALESCE(profile_type,'')) <= 100
  AND char_length(COALESCE(goal,'')) <= 150
  AND jsonb_typeof(event_data) = 'object'
);
ALTER POLICY anon_insert_second_opinion_events ON public.jmai_second_opinion_events WITH CHECK (
  char_length(session_id) BETWEEN 8 AND 100
  AND event_name IN ('landing_view','quiz_started','quiz_completed','result_generated',
    'summary_copied','consult_intent','library_intent','main_site_intent',
    'result_viewed','next_step_clicked')
);
COMMIT;
