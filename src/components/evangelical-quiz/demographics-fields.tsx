"use client";

import {
  BIRTH_DECADE_OPTIONS,
  COUNTRY_OPTIONS,
  EDUCATION_OPTIONS,
  GENDER_OPTIONS,
  HISPANIC_OPTIONS,
  MARITAL_OPTIONS,
  RACE_OPTIONS,
  RELIGION_OPTIONS_BY_GROUP,
  STATE_OPTIONS,
  US_COUNTRY_SLUG,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";

/**
 * The demographic questions themselves - the whole battery, controlled by
 * one Demographics value. Shared so the quiz's intake screen and the
 * account's editor ask exactly the same nine questions in exactly the same
 * words; two copies of this would drift within a release.
 *
 * The questions, their wording, and their answer lists are Pew Research
 * Center's Religious Landscape Study instrument, except for country of
 * residence and the 2010s/2020s cohorts. See
 * src/lib/evangelical-quiz/demographics.ts and
 * docs/datasets/pew-rls-2023-24/.
 */
export function DemographicsFields({
  value,
  onChange,
  idPrefix = "eq",
}: {
  value: Demographics;
  onChange: (next: Demographics) => void;
  /** Distinguishes the inputs when two of these are ever on one page. */
  idPrefix?: string;
}) {
  const id = (name: string) => `${idPrefix}-${name}`;

  function set<K extends keyof Demographics>(key: K, next: Demographics[K]) {
    onChange({ ...value, [key]: next });
  }

  // The state question is for the U.S. only. It stays visible but disabled
  // until the reader says they're in the U.S., so the dependency is
  // apparent rather than a field that appears out of nowhere.
  const stateApplies = value.country === US_COUNTRY_SLUG;

  function changeCountry(next: string) {
    // Moving off the U.S. abandons any state already picked, so the form
    // can't submit a contradiction. validateDemographics enforces the same
    // rule server-side; this only keeps the UI honest.
    onChange({
      ...value,
      country: next || null,
      state: next === US_COUNTRY_SLUG ? value.state : null,
    });
  }

  return (
    <>
      <Field id={id("religion")} label="Which of these best describes your religion?">
        <select
          id={id("religion")}
          value={value.religionSlug ?? ""}
          onChange={(e) => set("religionSlug", e.target.value || null)}
          className={SELECT_CLASS}
        >
          <option value="">Optional — choose one</option>
          {RELIGION_OPTIONS_BY_GROUP.map(({ group, options }) =>
            // A single-option group reads better flat than as a heading
            // with one child under it.
            options.length === 1 ? (
              <option key={options[0].slug} value={options[0].slug}>
                {options[0].label}
              </option>
            ) : (
              <optgroup key={group} label={group}>
                {options.map((o) => (
                  <option key={o.slug} value={o.slug}>
                    {o.label}
                  </option>
                ))}
              </optgroup>
            ),
          )}
        </select>
      </Field>

      <div className="mt-6 grid gap-6 sm:grid-cols-2">
        <Field id={id("birth-decade")} label="In what decade were you born?">
          <OptionSelect
            id={id("birth-decade")}
            value={value.birthDecade}
            onChange={(v) => set("birthDecade", v || null)}
            options={BIRTH_DECADE_OPTIONS}
          />
        </Field>

        <Field
          id={id("gender")}
          label="Do you describe yourself as a man, a woman, or in some other way?"
        >
          <OptionSelect
            id={id("gender")}
            value={value.gender}
            onChange={(v) => set("gender", v || null)}
            options={GENDER_OPTIONS}
          />
        </Field>

        <Field id={id("hispanic")} label="Are you of Hispanic, Latino, or Spanish origin?">
          <OptionSelect
            id={id("hispanic")}
            value={value.hispanic}
            onChange={(v) => set("hispanic", v || null)}
            options={HISPANIC_OPTIONS}
          />
        </Field>

        <Field id={id("race")} label="What is your race?">
          <OptionSelect
            id={id("race")}
            value={value.race}
            onChange={(v) => set("race", v || null)}
            options={RACE_OPTIONS}
          />
        </Field>

        <Field
          id={id("education")}
          label="What is the highest level of school you have completed?"
        >
          <OptionSelect
            id={id("education")}
            value={value.education}
            onChange={(v) => set("education", v || null)}
            options={EDUCATION_OPTIONS}
          />
        </Field>

        <Field id={id("marital")} label="What is your marital status?">
          <OptionSelect
            id={id("marital")}
            value={value.maritalStatus}
            onChange={(v) => set("maritalStatus", v || null)}
            options={MARITAL_OPTIONS}
          />
        </Field>

        <Field id={id("country")} label="What country do you live in?">
          <OptionSelect
            id={id("country")}
            value={value.country}
            onChange={changeCountry}
            options={COUNTRY_OPTIONS}
          />
        </Field>

        <Field id={id("state")} label="What state do you live in?">
          <OptionSelect
            id={id("state")}
            value={value.state}
            onChange={(v) => set("state", v || null)}
            options={STATE_OPTIONS}
            disabled={!stateApplies}
            placeholder={
              stateApplies ? "Optional — choose one" : "Choose the United States first"
            }
          />
          {!stateApplies && (
            <p className="mt-1.5 text-xs text-[color:var(--muted)]">
              Asked only of readers in the United States.
            </p>
          )}
        </Field>
      </div>
    </>
  );
}

const SELECT_CLASS =
  "mt-1.5 h-11 w-full rounded-[var(--radius)] border border-[color:var(--border)] bg-white px-4 text-sm focus:border-[color:var(--accent)] focus:outline-none";

function Field({
  id,
  label,
  children,
}: {
  id: string;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      {children}
    </div>
  );
}

function OptionSelect({
  id,
  value,
  onChange,
  options,
  disabled = false,
  placeholder = "Optional — choose one",
}: {
  id: string;
  value: string | null;
  onChange: (value: string) => void;
  options: readonly { slug: string; label: string }[];
  disabled?: boolean;
  placeholder?: string;
}) {
  return (
    <select
      id={id}
      value={value ?? ""}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className={`${SELECT_CLASS} ${
        disabled ? "cursor-not-allowed text-[color:var(--muted)] opacity-60" : ""
      }`}
    >
      <option value="">{placeholder}</option>
      {options.map((o) => (
        <option key={o.slug} value={o.slug}>
          {o.label}
        </option>
      ))}
    </select>
  );
}
