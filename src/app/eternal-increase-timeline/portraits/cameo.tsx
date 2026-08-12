/**
 * Cartoon side-profile cameos in engraved gilt/walnut frames, for the
 * portrait hall on the eternal-increase timeline.
 *
 * The hex values in this file are illustration pigments, not UI colors: the
 * portraits are content artwork (like a study's preview image), drawn in a
 * fixed sepia-and-gilt palette that reads correctly on both the light and
 * dark page grounds. Page chrome around the portraits uses tokens as usual.
 * The two exceptions deliberately reach back into the theme: the hanging
 * cord/nail follow `--muted` so they recede like rules do, and the frame mat
 * follows `--surface` so the sheet inside the frame matches the site's cards.
 */

const SKIN = "#e7c096";
const SKIN_SHADE = "#d3a877";
const LINE = "#3a2a1c";

const HAIR_COLORS = {
  brown: "#5b4630",
  darkbrown: "#3c2d1c",
  auburn: "#6b4a2a",
  gray: "#918a7f",
  silver: "#c4beb2",
  white: "#e9e4d8",
} as const;

export type HairStyle = "sweep" | "receding" | "fringe" | "parted" | "slick" | "bald";
export type BeardStyle = "none" | "chincurtain" | "full" | "long";
export type GlassesStyle = "round" | "pince" | "rimless";
export type CollarStyle = "cravat" | "suit" | "bowtie";

export type Face = {
  hair: HairStyle;
  hairColor: keyof typeof HAIR_COLORS;
  beard?: BeardStyle;
  beardColor?: keyof typeof HAIR_COLORS;
  mustache?: boolean;
  glasses?: GlassesStyle;
  collar: CollarStyle;
  coat?: string;
  browHeavy?: boolean;
  smile?: boolean;
};

const HAIR_PATHS: Record<Exclude<HairStyle, "bald">, { d: string; extra?: { d: string; opacity?: number }[] }> = {
  sweep: {
    d: "M61,76 C57,42 80,24 101,26 C132,29 145,58 144,96 C139,72 129,60 113,54 C120,48 118,42 112,40 C104,50 78,48 68,66 C65,70 62,72 61,76 Z",
  },
  receding: {
    d: "M92,33 C112,30 130,44 138,64 C143,78 144,98 143,142 C136,138 128,132 124,124 C118,112 116,96 110,84 C104,72 96,60 88,52 C86,44 88,37 92,33 Z",
  },
  fringe: {
    d: "M124,66 C136,78 142,96 143,116 L143,150 C136,148 128,144 122,138 C114,130 110,118 110,106 C110,90 115,76 124,66 Z",
  },
  parted: {
    d: "M64,62 C68,38 86,27 103,28 C130,30 144,56 143,96 C138,70 127,58 110,53 C96,49 76,50 64,62 Z",
    extra: [{ d: "M106,52 C124,58 134,72 138,88", opacity: 0.45 }],
  },
  slick: {
    d: "M66,58 C72,38 90,28 104,29 C130,31 144,58 143,98 C139,72 128,58 110,52 C96,47 78,49 66,58 Z",
    extra: [{ d: "M78,48 C98,40 120,46 132,62", opacity: 0.45 }],
  },
};

const BEARD_PATHS: Record<Exclude<BeardStyle, "none">, string> = {
  chincurtain:
    "M113,120 C119,140 115,162 100,172 C84,181 64,175 56,160 C52,152 52,145 55,140 C60,151 70,159 82,159 C93,159 102,150 104,138 C106,130 107,126 107,120 Z",
  full:
    "M114,112 C122,130 122,156 108,170 C94,183 68,182 55,168 C46,158 44,142 48,130 C50,124 53,120 57,118 C60,124 65,128 71,129 C78,130 84,128 88,124 C94,128 102,127 106,122 C110,119 113,116 114,112 Z",
  long:
    "M114,112 C124,132 126,160 120,184 C115,203 100,214 86,210 C74,206 66,196 64,184 C56,176 50,162 50,148 C49,136 52,126 57,118 C60,124 65,128 71,129 C78,130 84,128 88,124 C94,128 102,127 106,122 C110,119 113,116 114,112 Z",
};

function Glasses({ style: s }: { style: GlassesStyle }) {
  if (s === "round") {
    return (
      <g fill="none" stroke="#4a3a26" strokeWidth={2.6}>
        <circle cx={74} cy={97} r={11} fill="rgba(255,255,255,.16)" />
        <path d="M85,95 L112,108" />
        <path d="M63,94 C58,96 55,100 54,104" />
      </g>
    );
  }
  if (s === "pince") {
    return (
      <g fill="none" stroke="#4a3a26" strokeWidth={2.2}>
        <circle cx={76} cy={96} r={10} fill="rgba(255,255,255,.16)" />
        <path d="M78,106 C76,120 84,130 82,144" strokeWidth={1.2} />
      </g>
    );
  }
  return (
    <g fill="none" stroke="#6a5c48" strokeWidth={1.8}>
      <path d="M62,90 L88,90 L86,104 L64,104 Z" fill="rgba(255,255,255,.18)" />
      <path d="M88,92 L112,106" />
    </g>
  );
}

function Collar({ style: s, coat }: { style: CollarStyle; coat?: string }) {
  const coatPath =
    "M42,242 C48,214 70,201 100,198 C130,195 154,203 162,213 C170,223 174,232 176,242 Z";
  if (s === "cravat") {
    return (
      <g>
        <path d={coatPath} fill="#33291d" stroke={LINE} strokeWidth={2.5} />
        <path d="M84,203 L100,197 L112,203 L108,226 L88,226 Z" fill="#f1e8d4" stroke={LINE} strokeWidth={2} />
        <path d="M88,206 C94,212 104,212 108,206 C110,214 104,222 98,222 C92,222 88,214 88,206 Z" fill="#d8cdb2" stroke={LINE} strokeWidth={1.6} />
      </g>
    );
  }
  if (s === "bowtie") {
    return (
      <g>
        <path d={coatPath} fill={coat ?? "#2e2b26"} stroke={LINE} strokeWidth={2.5} />
        <path d="M86,202 L100,197 L112,202 L108,214 L90,214 Z" fill="#f1e8d4" stroke={LINE} strokeWidth={1.8} />
        <path d="M99,208 L86,201 L86,216 Z M101,208 L114,201 L114,216 Z" fill="#5c1f1c" stroke={LINE} strokeWidth={1.8} />
        <circle cx={100} cy={208} r={3.4} fill="#5c1f1c" stroke={LINE} strokeWidth={1.4} />
      </g>
    );
  }
  return (
    <g>
      <path d={coatPath} fill={coat ?? "#3a3730"} stroke={LINE} strokeWidth={2.5} />
      <path d="M88,202 L100,197 L110,202 L104,216 L94,216 Z" fill="#f1e8d4" stroke={LINE} strokeWidth={1.8} />
      <path d="M94,216 L104,216 L100,232 Z" fill="#5c1f1c" stroke={LINE} strokeWidth={1.6} />
      <path d="M70,206 L92,238" fill="none" stroke={LINE} strokeWidth={1.6} opacity={0.6} />
      <path d="M132,204 L112,238" fill="none" stroke={LINE} strokeWidth={1.6} opacity={0.6} />
    </g>
  );
}

export function Cameo({ face, id }: { face: Face; id: string }) {
  const hairColor = HAIR_COLORS[face.hairColor];
  const beardColor = HAIR_COLORS[face.beardColor ?? face.hairColor];
  const hair = face.hair === "bald" ? null : HAIR_PATHS[face.hair];
  const gradientId = `cameo-vignette-${id}`;

  return (
    <svg viewBox="0 0 200 240" role="img" aria-hidden="true" focusable="false">
      <defs>
        <radialGradient id={gradientId} cx="46%" cy="38%" r="75%">
          <stop offset="0%" stopColor="#f3e3bd" />
          <stop offset="62%" stopColor="#dcc394" />
          <stop offset="100%" stopColor="#a8845a" />
        </radialGradient>
      </defs>
      <rect width={200} height={240} fill={`url(#${gradientId})`} />
      {/* head + neck */}
      <path
        d="M97,32 C72,34 60,54 61,74 C61.5,82 60,86 60.5,91 C61,95 57,100 53,107 C50,113 49.5,117 51.5,119 C53.5,121.5 58,121.5 61,122.5 C59,126.5 58.5,130 62.5,132 C58.5,137 58.5,142 63.5,144 C60.5,150 63,158 71,161 C80,168 93,173 105,174 C106,187 105,196 100,204 L146,204 C144,178 143,150 143,120 C143,62 131,29 97,32 Z"
        fill={SKIN}
        stroke={LINE}
        strokeWidth={2.5}
        strokeLinejoin="round"
      />
      <path
        d="M105,174 C106,187 105,196 100,204 L112,204 C110,193 110,183 110,175 Z"
        fill={SKIN_SHADE}
        opacity={0.55}
      />
      {/* ear */}
      <path
        d="M112,110 c10,-7 17,1 12,11 c-3,6 -9,7 -13,3 c-2,-2 -2,-6 1,-9"
        fill={SKIN}
        stroke={LINE}
        strokeWidth={2.2}
      />
      <Collar style={face.collar} coat={face.coat} />
      {face.beard && face.beard !== "none" && (
        <path
          d={BEARD_PATHS[face.beard]}
          fill={beardColor}
          stroke={LINE}
          strokeWidth={2.4}
          strokeLinejoin="round"
        />
      )}
      {face.mustache && (
        <path
          d="M54,122 C60,115 72,114 79,119 C86,114 98,115 103,122 C98,129 87,130 79,125 C71,130 59,129 54,122 Z"
          fill={beardColor}
          stroke={LINE}
          strokeWidth={2}
          strokeLinejoin="round"
        />
      )}
      {hair && (
        <g>
          <path d={hair.d} fill={hairColor} stroke={LINE} strokeWidth={2.5} strokeLinejoin="round" />
          {hair.extra?.map((e, i) => (
            <path key={i} d={e.d} fill="none" stroke={LINE} strokeWidth={1.4} opacity={e.opacity ?? 0.5} />
          ))}
        </g>
      )}
      {/* eye, brow, mouth, cheek */}
      <ellipse cx={76} cy={97} rx={4.6} ry={3} fill={LINE} />
      <path
        d="M67,88 q9,-6 19,-3"
        fill="none"
        stroke={LINE}
        strokeWidth={face.browHeavy ? 5 : 3}
        strokeLinecap="round"
      />
      {face.smile && (
        <path d="M63,146 q6,4 12,2" fill="none" stroke={LINE} strokeWidth={2.2} strokeLinecap="round" />
      )}
      <ellipse cx={84} cy={126} rx={9} ry={6} fill="#c96f5e" opacity={0.18} />
      {face.glasses && <Glasses style={face.glasses} />}
    </svg>
  );
}

const GILT = { hi: "#f4e5a8", md: "#c8a24d", dk: "#8a6420" };
const WALNUT = { hi: "#7a5636", md: "#54371e", dk: "#331e0c" };

function Rosette({ x, y, wood }: { x: number; y: number; wood: typeof GILT }) {
  return (
    <g transform={`translate(${x},${y})`}>
      <circle r={9} fill={wood.md} stroke={wood.dk} strokeWidth={1.5} />
      <circle r={4} fill={wood.hi} />
      {[0, 60, 120, 180, 240, 300].map((a) => (
        <ellipse
          key={a}
          rx={3}
          ry={7}
          transform={`rotate(${a}) translate(0,-8)`}
          fill={wood.hi}
          stroke={wood.dk}
          strokeWidth={0.8}
        />
      ))}
    </g>
  );
}

/** Usable engraving width inside the nameplate. */
const PLAQUE_MAX_WIDTH = 138;

function Plaque({ deseret, name, id }: { deseret: string; name: string; id: string }) {
  // Deseret glyphs live in an astral plane: spread to count characters, since
  // .length would count every glyph twice and overshoot the estimate.
  const deseretChars = [...deseret].length;
  const deseretSize = deseretChars > 15 ? 11 : 13;
  const deseretEstimate = deseretChars * deseretSize * 0.68;
  const latin = name.toUpperCase();
  const latinEstimate = latin.length * (8 * 0.66 + 2.2);
  return (
    <g>
      <defs>
        <linearGradient id={`plaque-${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor={GILT.hi} />
          <stop offset="0.55" stopColor={GILT.md} />
          <stop offset="1" stopColor={GILT.dk} />
        </linearGradient>
      </defs>
      <rect x={38} y={232} width={154} height={40} rx={4} fill={`url(#plaque-${id})`} stroke={GILT.dk} strokeWidth={1.6} />
      <rect x={42} y={236} width={146} height={32} rx={2} fill="none" stroke={GILT.dk} strokeWidth={0.8} opacity={0.7} />
      {/* Hand-verified phonemic Deseret transliterations (unlike the decorative
          per-letter mapping in lib/deseret), with the Latin caption below so
          Deseret never carries the name alone. */}
      <text
        x={115}
        y={252}
        textAnchor="middle"
        fontSize={deseretSize}
        fill="#3d2c0e"
        style={{ fontFamily: "var(--font-deseret), sans-serif" }}
        {...(deseretEstimate > PLAQUE_MAX_WIDTH
          ? { textLength: PLAQUE_MAX_WIDTH, lengthAdjust: "spacingAndGlyphs" as const }
          : {})}
      >
        {deseret}
      </text>
      <text
        x={115}
        y={264}
        textAnchor="middle"
        fontSize={8}
        fill="#4d3a13"
        style={{ fontFamily: "var(--font-fraunces), Georgia, serif" }}
        {...(latinEstimate > PLAQUE_MAX_WIDTH
          ? { textLength: PLAQUE_MAX_WIDTH, lengthAdjust: "spacingAndGlyphs" as const }
          : { letterSpacing: 2.2 })}
      >
        {latin}
      </text>
    </g>
  );
}

export function FramedPortrait({
  face,
  frame,
  deseret,
  name,
  id,
}: {
  face: Face;
  frame: "gilt" | "walnut";
  deseret: string;
  name: string;
  id: string;
}) {
  const wood = frame === "walnut" ? WALNUT : GILT;
  const W = 230;
  const H = 292;
  return (
    <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-hidden="true" focusable="false" className="h-auto w-full">
      <defs>
        <linearGradient id={`frame-a-${id}`} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor={wood.hi} />
          <stop offset="0.5" stopColor={wood.md} />
          <stop offset="1" stopColor={wood.dk} />
        </linearGradient>
        <linearGradient id={`frame-b-${id}`} x1="1" y1="1" x2="0" y2="0">
          <stop offset="0" stopColor={wood.hi} />
          <stop offset="0.55" stopColor={wood.md} />
          <stop offset="1" stopColor={wood.dk} />
        </linearGradient>
        <clipPath id={`frame-clip-${id}`}>
          <ellipse cx={115} cy={121} rx={79} ry={96} />
        </clipPath>
      </defs>
      {/* hanging cord + nail follow the theme so they recede like rules */}
      <circle cx={115} cy={-46} r={5} fill="var(--muted)" opacity={0.9} />
      <rect x={3} y={3} width={W - 6} height={H - 6} rx={6} fill={`url(#frame-a-${id})`} stroke={wood.dk} strokeWidth={2} />
      <rect x={14} y={14} width={W - 28} height={H - 28} rx={3} fill={`url(#frame-b-${id})`} stroke={wood.dk} strokeWidth={1.2} />
      <rect x={20} y={20} width={W - 40} height={H - 40} fill="var(--surface)" stroke={wood.dk} strokeWidth={1} />
      <ellipse cx={115} cy={121} rx={84} ry={101} fill="none" stroke={wood.dk} strokeWidth={1} opacity={0.5} />
      <g clipPath={`url(#frame-clip-${id})`}>
        <g transform="translate(15,-4)">
          <Cameo face={face} id={id} />
        </g>
      </g>
      <ellipse cx={115} cy={121} rx={79} ry={96} fill="none" stroke={`url(#frame-a-${id})`} strokeWidth={7} />
      <ellipse cx={115} cy={121} rx={82.5} ry={99.5} fill="none" stroke={wood.dk} strokeWidth={1.4} />
      <ellipse cx={115} cy={121} rx={75.5} ry={92.5} fill="none" stroke={wood.dk} strokeWidth={1.2} />
      <Rosette x={20} y={20} wood={wood} />
      <Rosette x={W - 20} y={20} wood={wood} />
      <Rosette x={20} y={H - 20} wood={wood} />
      <Rosette x={W - 20} y={H - 20} wood={wood} />
      <Plaque deseret={deseret} name={name} id={id} />
    </svg>
  );
}
