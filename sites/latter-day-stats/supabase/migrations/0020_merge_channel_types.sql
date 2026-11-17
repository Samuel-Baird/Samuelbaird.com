-- Merge Anti-Church → Critical; merge BYUradio Podcast → BYU
UPDATE public.channels SET channel_type = 'Critical',  updated_at = now() WHERE channel_type = 'Anti-Church';
UPDATE public.channels SET channel_type = 'BYU',       updated_at = now() WHERE channel_type = 'BYUradio Podcast';
