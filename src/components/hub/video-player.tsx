"use client";

export function VideoPlayer({
  youtubeVideoId,
  start,
}: {
  youtubeVideoId: string;
  start: number;
}) {
  const embedSrc = `https://www.youtube-nocookie.com/embed/${youtubeVideoId}?start=${start}&rel=0`;
  const watchUrl = `https://www.youtube.com/watch?v=${youtubeVideoId}&t=${start}s`;

  return (
    <div>
      <div className="relative aspect-video w-full overflow-hidden rounded-[var(--radius)] border border-[color:var(--border)] bg-black">
        {/* key={start} forces the iframe to reload at the new start offset —
            there is no postMessage seek API on the no-cookie embed, so a
            fresh embed is the reliable way to jump. */}
        <iframe
          key={start}
          src={embedSrc}
          title="Video player"
          className="absolute inset-0 h-full w-full"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>
      <a
        href={watchUrl}
        target="_blank"
        rel="noreferrer noopener"
        className="mt-2 inline-block text-xs text-[color:var(--accent)] hover:underline"
      >
        Open on YouTube ↗ — use this if the embed above is disabled
      </a>
    </div>
  );
}
