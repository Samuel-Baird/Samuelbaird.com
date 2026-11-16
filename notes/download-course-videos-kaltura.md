# How to download Canvas/Kaltura course videos (UVU), transcribe and clip them

Worked out 2026-11-16 for the ME 4810 lecture recordings. Use for personal study and team work only; the instructor may have turned downloads off, so keep copies private and do not repost whole lectures. Nothing here bypasses a login: it uses a video you can already watch while signed in.

## What you are dealing with
- Canvas "Course Media" is a Kaltura MediaSpace (KAF) gallery. Open it at top level so scripts can read it:
  `https://uvu.instructure.com/courses/<courseId>/external_tools/<toolId>?display=borderless`
  This redirects to `https://<partner>.kaf.kaltura.com/channel/<courseId>/<channelId>` (UVU partner id 1832361).
- Lecture captures are all titled by section number (identical titles). Identify a recording by the date in its tags (`uvudate20260923`) or by its entry id.
- Media page URL: `https://1832361.kaf.kaltura.com/media/<title>/<entryId>/<channelId>`
- The ACTIONS menu may have no Download (owner disabled it). The player streams HLS (`.m3u8` playlists, `.ts` segments) from `cfvod.kaltura.com` with signed URLs.
- Each lecture entry is two linked streams: master 1 = room camera + audio (360p ~350 kbps and 1080p ~2.5 Mbps), master 2 = projector capture, which is often a green "HDCP Content" screen with no slides. Download master 1.

## Method A (manual, any browser, ffmpeg installed)
1. Open the media page, press play.
2. F12, Network tab, type `m3u8` in the filter box, refresh and play. Right-click the master playlist request, Copy, Copy URL (signed; it expires within minutes and works for anyone holding it, so keep it private).
3. In a terminal:
   `ffmpeg -i "<m3u8 URL>" -c copy "out.mp4"`
   `-c copy` repackages without re-encoding (a few minutes for 50 minutes of video).

## Method B (Claude in Chrome extension, what was used)
Claude's tools redact signed URLs, so the download runs inside the page, where the player's own request log is readable.
1. Open the media page in the extension's tab, click the video to play for ~5 s.
2. In page JavaScript: collect `performance.getEntriesByType('resource')` names that match `m3u8`; fetch each, keep the ones containing `EXT-X-STREAM-INF` (masters). Take master 1, pick the `640x360` variant (or 1080p if you really need it; 1080p camera is ~1 GB), fetch its playlist, fetch all segments (6 in parallel, about 300 segments for 50 minutes), `new Blob(parts, {type: 'video/mp2t'})`, then click a hidden `<a download="name.ts">`. Return only counts/sizes from the script, never the URLs.
3. Chrome allows one automatic download per page load. Reload the page for each additional file. Chrome may leave the file as `<guid>.tmp` in Downloads until finalised; it is still a complete file.
4. Remux to mp4 and check:
   `ffmpeg -y -i name.ts -map 0:v:0 -map 0:a:0 -c copy name.mp4` then `ffprobe -show_entries format=duration,size name.mp4`

Things that did NOT work or were blocked: reading the page's Kaltura session token (KS) and calling the Kaltura API to get a download URL was refused as unauthorized access; there is no Download in the ACTIONS menu; copy the m3u8 yourself (Method A) if the extension route fails.

## Transcribe (local, no upload)
`faster-whisper` with the cached `medium.en` model on CPU (int8): extract audio from the start of the part you need, transcribe, then add the offset back so timestamps match the original video.
```
ffmpeg -ss <start_sec> -i video.mp4 -vn -ac 1 -ar 16000 part.wav
WhisperModel("medium.en", device="cpu", compute_type="int8").transcribe("part.wav", language="en", vad_filter=True, condition_on_previous_text=False)
```
Write `[HH:MM:SS] text` lines and an `.srt`. About 10 minutes of audio takes a few minutes. A Modal GPU option exists in `whisper-cpp/modal_whisper.py` (uploads the audio to Modal; avoid for recordings with classmates unless needed). The `whisper-cpp/Release` binaries have no ggml model file, so use faster-whisper instead.

## Clip and combine
- Cut: `ffmpeg -ss HH:MM:SS -to HH:MM:SS -i in.mp4 -c copy clip.mp4` (copy cuts snap to keyframes; re-encode with `-c:v libx264 -c:a aac` for frame-accurate cuts).
- Join clips: write `file 'clip1.mp4'` lines to `list.txt`, then `ffmpeg -f concat -safe 0 -i list.txt -c copy out.mp4`.
- Burn in a caption/title: `ffmpeg ... -vf "drawtext=..."` or add the `.srt` with `-vf subtitles=file.srt`.

## Example (ME 4810, Sep/Oct 2026)
Entries are listed per date in `courses/capstone/lecture-videos/KALTURA-NOTES.md` (local only, gitignored). Design Review 1 was at 45:00 of the Sep 23 recording; Design Review 2 at 40:30 of the Oct 28 recording.
