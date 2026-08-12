"use client";

import { useState } from "react";
import { VideoPlayer } from "@/components/hub/video-player";
import { ClaimsList } from "@/components/hub/claims-list";
import type { HubClaim } from "@/lib/types";

// Owns the seek position so a claim's timestamp button can jump the player
// above it — the two need to share state, so they're composed here rather
// than each fetching independently.
export function VideoPanel({
  youtubeVideoId,
  claims,
}: {
  youtubeVideoId: string;
  claims: HubClaim[];
}) {
  const [start, setStart] = useState(0);

  return (
    <div>
      <VideoPlayer youtubeVideoId={youtubeVideoId} start={start} />
      <div className="mt-8">
        <h2 className="serif text-xl font-semibold tracking-tight">
          Claims
        </h2>
        <div className="mt-4">
          <ClaimsList claims={claims} onSeek={setStart} />
        </div>
      </div>
    </div>
  );
}
