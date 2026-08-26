"use client";

import { ArrowLeft, ArrowRight } from "lucide-react";
import { useState } from "react";
import {
  BIRTH_DECADE_OPTIONS,
  COUNTRY_OPTIONS,
  DEMOGRAPHICS_DISCLOSURE,
  DEMOGRAPHICS_PROVENANCE,
  EDUCATION_OPTIONS,
  GENDER_OPTIONS,
  HISPANIC_OPTIONS,
  MARITAL_OPTIONS,
  RACE_OPTIONS,
  RELIGION_OPTIONS_BY_GROUP,
  STATE_OPTIONS,
  US_COUNTRY_SLUG,
  validateDemographics,
  type Demographics,
} from "@/lib/evangelical-quiz/demographics";

/**
 * The optional demographic intake, shown once before question 1. Every
 * field is optional and the whole screen is skippable; nothing here feeds
 * the score or appears on the results screen - it exists so results can
 * be analyzed in aggregate (e.g. self-reported religion vs. the tradition
 * the scoring assigns).
 *
 * The questions, their wording, and their answer lists are Pew Research
 * Center's Religious Landscape Study instrument - see
 * src/lib/evangelical-quiz/demographics.ts and
 * docs/datasets/pew-rls-2023-24/.
 */
export function DemographicsScreen({
  onSubmit,
  onSkip,
  onBack,
}: {
  onSubmit: (d: Demographics) => void;
  onSkip: () => void;
  onBack: () => void;
}) {
  const [birthDecade, setBirthDecade] = useState("");
  const [gender, setGender] = useState("");
  const [hispanic, setHispanic] = useState("");
  const [race, setRace] = useState("");
  const [education, setEducation] = useState("");
  const [maritalStatus, setMaritalStatus] = useState("");
  const [country, setCountry] = useState("");
  const [state, setState] = useState("");
  const [religionSlug, setReligionSlug] = useState("");

  // The state question is for the U.S. only. It stays visible but disabled
  // until the reader says they're in the U.S., so the dependency is
  // apparent rather than a field that appears out of nowhere.
  const stateApplies = country === US_COUNTRY_SLUG;

  function changeCountry(next: string) {
    setCountry(next);
    // Moving off the U.S. abandons any state already picked, so the form
    // can't submit a contradiction. (validateDemographics enforces the same
    // rule server-side; this is just to keep the UI honest.)
    if (next !== US_COUNTRY_SLUG) setState("");
  }

  function submit() {
    onSubmit(
      validateDemographics({
        birthDecade: birthDecade || null,
        gender: gender || null,
        hispanic: hispanic || null,
        race: race || null,
        education: education || null,
        maritalStatus: maritalStatus || null,
        country: country || null,
        state: state || null,
        religionSlug: religionSlug || null,
      }),
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={onBack}
        className="inline-flex min-h-9 items-center gap-1.5 rounded-[var(--radius)] px-1 text-xs font-medium text-[color:var(--accent)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
      >
        <ArrowLeft aria-hidden="true" size={13} />
        Back
      </button>

      <h2 className="serif mt-4 text-2xl font-semibold leading-snug tracking-tight sm:text-3xl">
        A few optional questions first
      </h2>
      <p className="mt-3 max-w-xl text-sm leading-relaxed text-[color:var(--muted)]">
        {DEMOGRAPHICS_DISCLOSURE}
      </p>
      <p className="mt-2 max-w-xl text-sm leading-relaxed text-[color:var(--muted)]">
        {DEMOGRAPHICS_PROVENANCE}
      </p>

      <div className="mt-8 max-w-2xl">
        <Field
          id="eq-religion"
          label="Which of these best describes your religion?"
        >
          <select
            id="eq-religion"
            value={religionSlug}
            onChange={(e) => setReligionSlug(e.target.value)}
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
          <Field id="eq-birth-decade" label="In what decade were you born?">
            <OptionSelect
              id="eq-birth-decade"
              value={birthDecade}
              onChange={setBirthDecade}
              options={BIRTH_DECADE_OPTIONS}
            />
          </Field>

          <Field
            id="eq-gender"
            label="Do you describe yourself as a man, a woman, or in some other way?"
          >
            <OptionSelect
              id="eq-gender"
              value={gender}
              onChange={setGender}
              options={GENDER_OPTIONS}
            />
          </Field>

          <Field
            id="eq-hispanic"
            label="Are you of Hispanic, Latino, or Spanish origin?"
          >
            <OptionSelect
              id="eq-hispanic"
              value={hispanic}
              onChange={setHispanic}
              options={HISPANIC_OPTIONS}
            />
          </Field>

          <Field id="eq-race" label="What is your race?">
            <OptionSelect
              id="eq-race"
              value={race}
              onChange={setRace}
              options={RACE_OPTIONS}
            />
          </Field>

          <Field
            id="eq-education"
            label="What is the highest level of school you have completed?"
          >
            <OptionSelect
              id="eq-education"
              value={education}
              onChange={setEducation}
              options={EDUCATION_OPTIONS}
            />
          </Field>

          <Field id="eq-marital" label="What is your marital status?">
            <OptionSelect
              id="eq-marital"
              value={maritalStatus}
              onChange={setMaritalStatus}
              options={MARITAL_OPTIONS}
            />
          </Field>

          <Field id="eq-country" label="What country do you live in?">
            <OptionSelect
              id="eq-country"
              value={country}
              onChange={changeCountry}
              options={COUNTRY_OPTIONS}
            />
          </Field>

          <Field id="eq-state" label="What state do you live in?">
            <OptionSelect
              id="eq-state"
              value={state}
              onChange={setState}
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
      </div>

      <div className="mt-8 flex flex-wrap items-center gap-4">
        <button
          type="button"
          onClick={submit}
          className="inline-flex min-h-11 items-center gap-2 rounded-[var(--radius)] bg-[color:var(--accent)] px-6 text-sm font-medium text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          Continue
          <ArrowRight aria-hidden="true" size={15} />
        </button>
        <button
          type="button"
          onClick={onSkip}
          className="text-sm font-medium text-[color:var(--muted)] hover:text-[color:var(--foreground)] hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[color:var(--accent)]"
        >
          Skip — go to question 1
        </button>
      </div>

      <p className="mt-6 max-w-xl text-xs leading-relaxed text-[color:var(--muted)]">
        These answers never affect your score and are never shown with your result.
      </p>
    </div>
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
  value: string;
  onChange: (value: string) => void;
  options: readonly { slug: string; label: string }[];
  disabled?: boolean;
  placeholder?: string;
}) {
  return (
    <select
      id={id}
      value={value}
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
