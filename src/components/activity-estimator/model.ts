export type Scenario = "low" | "mid" | "high";
export const SCENARIOS: Scenario[] = ["low", "mid", "high"];

export type Attendance = Record<Scenario, number>;
export type Assumptions = { ward: Attendance; branch: Attendance };

export type CountryUnits = {
  members: number;
  wards: number;
  branches: number;
  source_url: string;
};

export type Estimate = Record<Scenario, { active: number; rate: number }>;

export const PRESETS: Record<string, Assumptions> = {
  "Handbook minimum": {
    ward: { low: 100, mid: 100, high: 100 },
    branch: { low: 20, mid: 20, high: 20 },
  },
  Default: {
    ward: { low: 80, mid: 130, high: 200 },
    branch: { low: 15, mid: 35, high: 60 },
  },
  Generous: {
    ward: { low: 150, mid: 200, high: 250 },
    branch: { low: 30, mid: 50, high: 80 },
  },
};

export function estimate(c: CountryUnits, a: Assumptions): Estimate {
  const out = {} as Estimate;
  for (const s of SCENARIOS) {
    const active = c.wards * a.ward[s] + c.branches * a.branch[s];
    out[s] = { active, rate: c.members > 0 ? active / c.members : 0 };
  }
  return out;
}

export function totals(
  rows: { units: CountryUnits; est: Estimate }[],
): { members: number; est: Estimate } {
  const members = rows.reduce((n, r) => n + r.units.members, 0);
  const est = {} as Estimate;
  for (const s of SCENARIOS) {
    const active = rows.reduce((n, r) => n + r.est[s].active, 0);
    est[s] = { active, rate: members > 0 ? active / members : 0 };
  }
  return { members, est };
}

/** Keep low <= mid <= high after editing one scenario. */
export function setScenario(a: Attendance, s: Scenario, v: number): Attendance {
  const n = { ...a, [s]: v };
  if (s === "low") {
    n.mid = Math.max(n.mid, v);
    n.high = Math.max(n.high, n.mid);
  } else if (s === "mid") {
    n.low = Math.min(n.low, v);
    n.high = Math.max(n.high, v);
  } else {
    n.mid = Math.min(n.mid, v);
    n.low = Math.min(n.low, n.mid);
  }
  return n;
}
