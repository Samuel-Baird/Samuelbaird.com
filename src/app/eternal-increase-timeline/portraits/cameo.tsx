/**
 * Engraved side-profile cameos in gilt/walnut frames, for the portrait hall
 * on the eternal-increase timeline.
 *
 * The figure is drawn as a stack of layers, back to front: backdrop, hair
 * mass, silhouette, modelling shadows, features, hair locks, facial hair,
 * clothing. Everything is built from one set of landmarks (brow 90, eye 101,
 * nose tip 132, mouth 148, chin 162, jaw 178) so a beard drawn against the
 * jawline meets the jawline.
 *
 * The hex values here are illustration pigments, not UI colors: the portraits
 * are content artwork, drawn in a fixed sepia palette that reads on both the
 * light and dark page grounds. Page chrome around them uses tokens as usual.
 * Two exceptions deliberately reach back into the theme — the frame mat
 * follows `--surface` so the sheet inside the frame matches the site's cards,
 * and the hanging nail follows `--muted` so it recedes like a rule.
 */

const SKIN = "#e8c49c";
const SKIN_SHADE = "#cfa274";
const SKIN_DEEP = "#b8875a";
const SKIN_LIGHT = "#f5ddbd";
const LINE = "#3a2a1c";
const LINE_SOFT = "#6b503a";
const LIP = "#b9705c";

type Tone = { base: string; dark: string; light: string };

const HAIR_COLORS: Record<string, Tone> = {
  brown: { base: "#5b4630", dark: "#392a19", light: "#7f6644" },
  darkbrown: { base: "#3c2d1c", dark: "#231909", light: "#5b4630" },
  auburn: { base: "#6b4a2a", dark: "#472c13", light: "#8f6940" },
  gray: { base: "#918a7f", dark: "#6a635a", light: "#b5aea3" },
  silver: { base: "#c4beb2", dark: "#968f83", light: "#e0dbd1" },
  white: { base: "#e9e4d8", dark: "#b6ae9d", light: "#f8f5ee" },
};

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

/**
 * Sits the figure in the frame's oval as a head-and-shoulders crop: the whole
 * drawing is authored at full size, then scaled back so the crown clears the
 * top of the oval and the shoulders reach its bottom edge.
 */
const FIGURE_TRANSFORM = "translate(14,17) scale(0.84)";

/** Head, neck and shoulders, facing left. Landmarks in the file header. */
const SILHOUETTE =
  "M100,26 C74,28 59,46 56,68 C55,77 54,84 53,90 C52,94 50,96 49,99 " +
  "C51,102 52,105 53,108 C50,113 46,119 43,124 C41,127 41,130 44,132 " +
  "C47,134 51,134 54,135 C53,138 52,140 53,142 C55,143 57,143 58,144 " +
  "C56,146 55,147 56,149 C58,150 59,150 60,151 C57,155 55,158 57,162 " +
  "C59,167 64,171 71,174 C76,176 81,177 86,178 C87,188 86,197 85,207 " +
  "L85,222 L143,222 C142,204 140,192 140,178 C143,166 146,152 147,136 " +
  "C149,108 148,76 139,56 C131,38 118,26 100,26 Z";

/**
 * Hair sits *over* the skull, so the mass's outer edge traces the silhouette
 * exactly (same control points, reversed) and its inner edge is the hairline.
 * Styles differ only in where that hairline falls. Locks and a sheen ride on
 * top; a sideburn is drawn in front of the ear where the style has one.
 */
/**
 * The skull edge pushed outward, so hair has thickness and overhangs the brow
 * instead of reading as paint on the scalp.
 */
const SKULL_EDGE =
  "M52,66 C55,40 73,20 100,20 C121,20 137,33 146,53 C156,76 158,108 156,137 " +
  "C155,154 151,169 147,179";

/** Nape → in front of the ear: where hair meets neck and sideburn. */
const NAPE_TO_SIDEBURN = " C138,168 126,153 117,136 C113,124 112,114 111,104";

const HAIR_STYLES: Record<
  Exclude<HairStyle, "bald">,
  { mass: string; locks: string[]; sheen?: string; sideburn?: string; part?: string }
> = {
  sweep: {
    // High wavy hairline with a forelock breaking forward onto the temple.
    mass:
      SKULL_EDGE +
      NAPE_TO_SIDEBURN +
      " C108,72 96,48 78,45 C67,43 56,52 52,66 Z",
    locks: [
      "M68,60 C86,48 110,50 126,66",
      "M64,66 C84,55 108,57 128,76",
      "M80,42 C98,34 118,38 136,56",
      "M132,104 C136,128 138,152 139,172",
    ],
    sheen: "M86,40 C102,33 118,38 130,50",
  },
  receding: {
    // Deep temple recession: the hairline starts well back on the crown.
    mass:
      "M86,26 C92,22 96,20 100,20 C121,20 137,33 146,53 C156,76 158,108 156,137 " +
      "C155,154 151,169 147,179" +
      NAPE_TO_SIDEBURN +
      " C108,78 98,50 86,26 Z",
    locks: [
      "M94,44 C112,60 124,82 130,106",
      "M102,40 C118,54 129,74 134,96",
      "M134,116 C137,138 138,158 139,172",
    ],
    sheen: "M98,38 C112,50 122,64 128,80",
  },
  fringe: {
    // Bald over the crown; hair survives above and behind the ear only.
    mass:
      "M147,90 C156,108 159,142 147,179 C138,168 126,153 117,136 C112,121 111,105 115,93 " +
      "C123,83 139,82 147,90 Z",
    locks: [
      "M130,94 C135,116 138,140 137,162",
      "M120,102 C123,122 127,142 131,160",
      "M140,100 C145,120 146,142 144,160",
    ],
    sideburn: "M104,98 C102,112 103,124 107,132 C111,129 113,118 113,107 C113,100 109,97 104,98 Z",
  },
  parted: {
    // A defined part, hairline lower and squarer than the sweep.
    mass:
      SKULL_EDGE +
      NAPE_TO_SIDEBURN +
      " C106,72 88,46 68,50 C60,53 54,59 52,66 Z",
    locks: [
      "M70,60 C92,52 114,60 128,78",
      "M66,66 C88,60 112,68 130,88",
      "M102,32 C120,34 133,44 140,60",
      "M132,108 C136,132 138,154 139,172",
    ],
    sheen: "M100,36 C116,34 128,42 137,54",
    part: "M94,31 C90,42 91,52 96,60",
    sideburn: "M105,98 C103,112 104,124 108,132 C112,129 114,118 114,107 C114,100 110,97 105,98 Z",
  },
  slick: {
    // Combed flat back off a low, straight hairline.
    mass:
      SKULL_EDGE +
      NAPE_TO_SIDEBURN +
      " C108,76 90,48 68,53 C60,55 54,60 52,66 Z",
    locks: [
      "M64,64 C86,56 110,62 128,80",
      "M68,55 C90,47 114,52 134,70",
      "M78,45 C98,37 118,42 140,60",
      "M132,108 C136,132 138,154 139,172",
    ],
    sheen: "M82,40 C100,34 116,40 130,50",
  },
};

/**
 * Facial hair, drawn over the face: the upper edge is where hair meets skin
 * (running back from below the mouth across the cheek to the sideburn) and the
 * lower edge hangs past the jaw, so the beard reshapes the profile as it should.
 */
const BEARDS: Record<Exclude<BeardStyle, "none">, { mass: string; texture: string[] }> = {
  chincurtain: {
    mass:
      "M111,106 C107,128 96,146 78,153 C71,156 65,158 61,159 " +
      "C52,168 51,180 58,189 C70,203 94,203 106,188 C114,178 117,160 116,140 " +
      "C115,126 113,114 111,106 Z",
    texture: [
      "M66,166 C72,180 84,190 98,190",
      "M104,160 C108,170 108,180 103,188",
      "M84,158 C86,170 88,180 88,190",
    ],
  },
  full: {
    mass:
      "M112,104 C110,128 100,146 84,152 C74,155 65,156 59,155 " +
      "C48,164 45,180 52,192 C64,212 96,214 110,196 C119,184 121,162 119,140 " +
      "C117,124 115,112 112,104 Z",
    texture: [
      "M60,166 C66,184 80,198 98,201",
      "M54,172 C58,188 68,200 82,206",
      "M110,158 C114,174 113,188 106,198",
    ],
  },
  long: {
    mass:
      "M112,104 C110,128 100,146 84,152 C74,155 65,156 59,155 " +
      "C46,166 42,188 48,208 C55,230 84,240 102,224 C116,211 122,180 120,150 " +
      "C118,130 115,114 112,104 Z",
    texture: [
      "M58,170 C62,194 72,216 88,230",
      "M112,158 C118,182 118,208 108,226",
      "M84,176 C86,198 88,216 90,232",
    ],
  },
};

function Glasses({ style: s }: { style: GlassesStyle }) {
  if (s === "round") {
    return (
      <g fill="none" stroke="#4a3a26" strokeLinecap="round">
        <circle cx={68} cy={101} r={13} fill="#f4f1e6" fillOpacity={0.22} strokeWidth={2.4} />
        <path d="M81,98 C92,102 102,106 112,110" strokeWidth={2.2} />
        <path d="M55,99 C51,101 49,104 48,108" strokeWidth={2} />
        <path d="M60,94 C63,91 68,90 72,91" strokeWidth={1} opacity={0.55} stroke="#ffffff" />
      </g>
    );
  }
  if (s === "pince") {
    return (
      <g fill="none" stroke="#4a3a26" strokeLinecap="round">
        <circle cx={68} cy={100} r={11} fill="#f4f1e6" fillOpacity={0.22} strokeWidth={2.2} />
        <path d="M69,111 C67,126 76,137 74,152" strokeWidth={1} />
        <path d="M61,94 C64,91 68,90 71,91" strokeWidth={1} opacity={0.55} stroke="#ffffff" />
      </g>
    );
  }
  return (
    <g fill="none" stroke="#6a5c48" strokeLinecap="round">
      <path d="M54,92 L82,92 L80,109 L56,109 Z" fill="#f4f1e6" fillOpacity={0.24} strokeWidth={1.8} />
      <path d="M82,95 C93,100 103,105 112,110" strokeWidth={1.8} />
      <path d="M58,95 L76,95" strokeWidth={1} opacity={0.5} stroke="#ffffff" />
    </g>
  );
}

function Collar({ style: s, coat }: { style: CollarStyle; coat?: string }) {
  const shell = coat ?? (s === "cravat" ? "#33291d" : "#33322e");
  // Runs well past the bottom of the cameo box so the shoulders fill the
  // frame's oval rather than stopping in mid-air.
  const body =
    "M-34,300 C-28,244 6,214 56,202 C76,197 94,195 112,195 C130,195 148,197 168,202 " +
    "C218,214 252,244 258,300 Z";
  const linen = "#f2ead6";
  const linenShade = "#d9cfb5";
  return (
    <g>
      <path d={body} fill={shell} stroke={LINE} strokeWidth={2.4} strokeLinejoin="round" />
      {/* cloth folds */}
      <g fill="none" stroke="#000000" strokeOpacity={0.22} strokeWidth={1.4} strokeLinecap="round">
        <path d="M52,220 C62,238 70,256 74,276" />
        <path d="M176,222 C168,240 160,258 156,278" />
      </g>
      {s === "cravat" ? (
        <>
          <path
            d="M94,200 L112,193 L130,200 L126,224 L98,224 Z"
            fill={linen}
            stroke={LINE}
            strokeWidth={1.8}
            strokeLinejoin="round"
          />
          <path
            d="M98,206 C104,215 120,215 126,206 C130,220 122,234 112,234 C102,234 95,220 98,206 Z"
            fill={linenShade}
            stroke={LINE}
            strokeWidth={1.6}
            strokeLinejoin="round"
          />
          <g fill="none" stroke={LINE} strokeWidth={0.9} strokeOpacity={0.5}>
            <path d="M104,214 C108,220 116,220 120,214" />
          </g>
        </>
      ) : s === "bowtie" ? (
        <>
          <path
            d="M92,200 L112,193 L132,200 L128,216 L96,216 Z"
            fill={linen}
            stroke={LINE}
            strokeWidth={1.8}
            strokeLinejoin="round"
          />
          <path
            d="M109,208 L92,199 L92,220 Z M115,208 L132,199 L132,220 Z"
            fill="#5c1f1c"
            stroke={LINE}
            strokeWidth={1.8}
            strokeLinejoin="round"
          />
          <circle cx={112} cy={208} r={4} fill="#7a2c28" stroke={LINE} strokeWidth={1.4} />
        </>
      ) : (
        <>
          <path
            d="M96,200 L112,193 L128,200 L124,222 L100,222 Z"
            fill={linen}
            stroke={LINE}
            strokeWidth={1.8}
            strokeLinejoin="round"
          />
          <path d="M100,222 L124,222 L118,270 L106,270 Z" fill="#5c1f1c" stroke={LINE} strokeWidth={1.6} />
          {/* lapels */}
          <path d="M86,201 L108,268 L78,268 Z" fill={shell} stroke={LINE} strokeWidth={1.6} strokeLinejoin="round" />
          <path d="M138,199 L118,268 L150,268 Z" fill={shell} stroke={LINE} strokeWidth={1.6} strokeLinejoin="round" />
        </>
      )}
    </g>
  );
}

/**
 * The drawing itself, as a group in a 200×240 box. Kept separate from the
 * `<svg>` wrapper so the frame can place it with an explicit transform — a
 * nested `<svg>` would re-fit the box to the frame and crop the shoulders.
 */
export function CameoFigure({ face, id }: { face: Face; id: string }) {
  const hair = HAIR_COLORS[face.hairColor] ?? HAIR_COLORS.brown;
  const beardTone = HAIR_COLORS[face.beardColor ?? face.hairColor] ?? hair;
  const hairArt = face.hair === "bald" ? null : HAIR_STYLES[face.hair];
  const beardArt = face.beard && face.beard !== "none" ? BEARDS[face.beard] : null;
  const uid = (part: string) => `cameo-${part}-${id}`;

  return (
    <g>
      <defs>
        <radialGradient id={uid("bg")} cx="42%" cy="32%" r="82%">
          <stop offset="0%" stopColor="#f6e8c6" />
          <stop offset="58%" stopColor="#dcc394" />
          <stop offset="100%" stopColor="#a07c52" />
        </radialGradient>
        <linearGradient id={uid("skin")} x1="0" y1="0" x2="1" y2="0.4">
          <stop offset="0%" stopColor={SKIN_LIGHT} />
          <stop offset="46%" stopColor={SKIN} />
          <stop offset="100%" stopColor={SKIN_SHADE} />
        </linearGradient>
        <pattern id={uid("hatch")} width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(35)">
          <line x1="0" y1="0" x2="0" y2="7" stroke="#5a3d1c" strokeWidth="1.1" strokeOpacity="0.07" />
        </pattern>
        <clipPath id={uid("head")}>
          <path d={SILHOUETTE} transform={FIGURE_TRANSFORM} />
        </clipPath>
      </defs>

      <rect width={200} height={240} fill={`url(#${uid("bg")})`} />
      <rect width={200} height={240} fill={`url(#${uid("hatch")})`} />

      <g transform={FIGURE_TRANSFORM}>
        <path d={SILHOUETTE} fill={`url(#${uid("skin")})`} stroke={LINE} strokeWidth={2.4} strokeLinejoin="round" />

        {/* modelling, clipped to the head so nothing spills past the silhouette */}
        <g clipPath={`url(#${uid("head")})`}>
          {/* temple and back-of-cheek falloff */}
          <path
            d="M92,40 C112,60 122,96 118,134 C114,166 100,182 86,190 L150,196 L150,20 Z"
            fill={SKIN_SHADE}
            opacity={0.34}
          />
          {/* under-jaw and throat shadow */}
          <path
            d="M56,163 C64,174 80,181 100,180 C114,179 124,174 132,166 C136,186 132,206 128,224 L82,224 C86,206 86,188 84,178 Z"
            fill={SKIN_DEEP}
            opacity={0.42}
          />
          {/* cheekbone */}
          <path d="M66,106 C78,114 84,126 80,140" fill="none" stroke={SKIN_DEEP} strokeWidth={5} opacity={0.2} strokeLinecap="round" />
          {/* eye socket */}
          <path d="M52,94 C62,88 78,88 86,94 C82,102 68,104 56,101 Z" fill={SKIN_DEEP} opacity={0.24} />
          {/* nostril wing and nose-side shadow */}
          <path d="M54,130 C60,127 67,129 70,135 C66,139 58,138 54,134 Z" fill={SKIN_SHADE} opacity={0.55} />
          {/* nasolabial fold */}
          <path d="M62,133 C67,139 68,145 66,151" fill="none" stroke={SKIN_DEEP} strokeWidth={1.6} opacity={0.4} strokeLinecap="round" />
          {/* forehead and nose-bridge highlight */}
          <path d="M60,52 C56,66 55,78 55,88" fill="none" stroke={SKIN_LIGHT} strokeWidth={4} opacity={0.5} strokeLinecap="round" />
          <path d="M50,110 C47,116 45,120 44,124" fill="none" stroke={SKIN_LIGHT} strokeWidth={2.4} opacity={0.55} strokeLinecap="round" />
          {/* chin and lower-lip shadow */}
          <path d="M57,153 C63,153 68,152 71,150" fill="none" stroke={SKIN_DEEP} strokeWidth={2.2} opacity={0.35} strokeLinecap="round" />
        </g>

        {/* hair rides over the skull; its inner edge is the hairline */}
        {hairArt && (
          <g>
            {hairArt.sideburn && (
              <path d={hairArt.sideburn} fill={hair.base} stroke={LINE} strokeWidth={1.8} strokeLinejoin="round" />
            )}
            <path d={hairArt.mass} fill={hair.base} stroke={LINE} strokeWidth={2.4} strokeLinejoin="round" />
            <g fill="none" strokeLinecap="round">
              {hairArt.locks.map((d, i) => (
                <path key={i} d={d} stroke={hair.dark} strokeWidth={1.7} opacity={0.7} />
              ))}
              {hairArt.part && <path d={hairArt.part} stroke={hair.dark} strokeWidth={2.2} opacity={0.85} />}
              {hairArt.sheen && (
                <path d={hairArt.sheen} stroke={hair.light} strokeWidth={3} opacity={0.5} />
              )}
            </g>
          </g>
        )}

        {/* ear */}
        <g>
          <path
            d="M113,104 C124,100 132,107 131,118 C130,130 124,139 116,140 C111,140 108,136 108,131 C108,122 110,112 113,104 Z"
            fill={SKIN}
            stroke={LINE}
            strokeWidth={2.2}
            strokeLinejoin="round"
          />
          <path
            d="M117,111 C123,108 127,113 125,121 C123,128 119,133 115,134"
            fill="none"
            stroke={LINE_SOFT}
            strokeWidth={1.6}
            strokeLinecap="round"
          />
          <path d="M113,124 C116,123 118,125 118,128" fill="none" stroke={LINE_SOFT} strokeWidth={1.3} strokeLinecap="round" />
        </g>

        {/* brow */}
        <path
          d="M55,90 C62,84 74,83 84,87 C86,88 87,90 86,92 C76,89 64,90 56,94 Z"
          fill={hair.dark}
          stroke={LINE}
          strokeWidth={face.browHeavy ? 2.6 : 1.4}
          strokeLinejoin="round"
        />
        {face.browHeavy && (
          <g fill="none" stroke={hair.dark} strokeWidth={1.6} strokeLinecap="round">
            <path d="M60,89 C64,85 70,84 76,85" />
            <path d="M74,85 C79,85 83,87 86,89" />
          </g>
        )}

        {/* eye: lid line, white, iris, pupil, catchlight, lower lid */}
        <g>
          <path d="M54,101 C58,95 66,93 74,95 C79,96 82,99 83,102 C76,105 64,106 54,101 Z" fill="#f6efe2" stroke={LINE} strokeWidth={1.5} strokeLinejoin="round" />
          <ellipse cx={66} cy={100} rx={4.6} ry={4.8} fill="#5a3f22" />
          <circle cx={65} cy={100} r={2.3} fill="#20150a" />
          <circle cx={63.6} cy={98.2} r={1.2} fill="#ffffff" opacity={0.9} />
          <path d="M53,100 C57,94 66,92 75,94" fill="none" stroke={LINE} strokeWidth={2.4} strokeLinecap="round" />
          <path d="M56,103 C63,106 74,105 82,102" fill="none" stroke={LINE_SOFT} strokeWidth={1.2} strokeLinecap="round" />
        </g>

        {/* nostril */}
        <path d="M52,131 C55,129 59,130 60,133 C57,135 53,134 52,131 Z" fill={LINE} opacity={0.85} />

        {/* mouth */}
        <path
          d={face.smile ? "M55,148 C62,150 70,150 76,146" : "M55,148 C62,149 70,149 76,147"}
          fill="none"
          stroke={LINE}
          strokeWidth={2}
          strokeLinecap="round"
        />
        <path d="M56,145 C62,143 69,143 74,145" fill="none" stroke={LIP} strokeWidth={2.6} opacity={0.4} strokeLinecap="round" />
        <path d="M57,152 C63,153 69,152 73,150" fill="none" stroke={LIP} strokeWidth={2.2} opacity={0.3} strokeLinecap="round" />

        <Collar style={face.collar} coat={face.coat} />

        {beardArt && (
          <g>
            <path d={beardArt.mass} fill={beardTone.base} stroke={LINE} strokeWidth={2.2} strokeLinejoin="round" />
            <g fill="none" stroke={beardTone.dark} strokeWidth={1.5} strokeLinecap="round" opacity={0.75}>
              {beardArt.texture.map((d, i) => (
                <path key={i} d={d} />
              ))}
            </g>
            <path
              d={beardArt.mass}
              fill="none"
              stroke={beardTone.light}
              strokeWidth={1.2}
              opacity={0.35}
              strokeLinejoin="round"
              transform="translate(-1.5,-1.5)"
            />
          </g>
        )}

        {face.mustache && (
          <g>
            <path
              d="M50,140 C57,132 68,130 76,135 C83,131 91,132 95,139 C90,147 79,148 74,143 C66,149 55,148 50,140 Z"
              fill={beardTone.base}
              stroke={LINE}
              strokeWidth={2}
              strokeLinejoin="round"
            />
            <g fill="none" stroke={beardTone.dark} strokeWidth={1.3} strokeLinecap="round" opacity={0.7}>
              <path d="M56,138 C62,136 68,137 72,140" />
              <path d="M80,137 C85,137 89,139 91,142" />
            </g>
          </g>
        )}

        {face.glasses && <Glasses style={face.glasses} />}
      </g>
    </g>
  );
}

/** Standalone cameo, for the round avatar on the catalogue card. */
export function Cameo({ face, id }: { face: Face; id: string }) {
  return (
    <svg viewBox="0 0 200 240" role="img" aria-hidden="true" focusable="false">
      <CameoFigure face={face} id={id} />
    </svg>
  );
}

const GILT = { hi: "#f4e5a8", md: "#c8a24d", dk: "#8a6420" };
const WALNUT = { hi: "#7a5636", md: "#54371e", dk: "#331e0c" };

function Rosette({ x, y, wood }: { x: number; y: number; wood: typeof GILT }) {
  return (
    <g transform={`translate(${x},${y})`}>
      <circle r={9} fill={wood.md} stroke={wood.dk} strokeWidth={1.5} />
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
      <circle r={4} fill={wood.hi} stroke={wood.dk} strokeWidth={0.8} />
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
      {/* hanging nail follows the theme so it recedes like a rule */}
      <circle cx={115} cy={-46} r={5} fill="var(--muted)" opacity={0.9} />
      <rect x={3} y={3} width={W - 6} height={H - 6} rx={6} fill={`url(#frame-a-${id})`} stroke={wood.dk} strokeWidth={2} />
      <rect x={14} y={14} width={W - 28} height={H - 28} rx={3} fill={`url(#frame-b-${id})`} stroke={wood.dk} strokeWidth={1.2} />
      <rect x={20} y={20} width={W - 40} height={H - 40} fill="var(--surface)" stroke={wood.dk} strokeWidth={1} />
      <ellipse cx={115} cy={121} rx={84} ry={101} fill="none" stroke={wood.dk} strokeWidth={1} opacity={0.5} />
      {/* Maps the cameo's 200×240 box onto the oval, overfilling it slightly
          so the backdrop reaches the mount on every side. */}
      <g clipPath={`url(#frame-clip-${id})`}>
        <g transform="translate(33,22) scale(0.82)">
          <CameoFigure face={face} id={id} />
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
