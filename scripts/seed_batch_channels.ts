/**
 * One-off: bulk-insert channel metadata rows with channel_type set.
 * Usage: npx tsx scripts/seed_batch_channels.ts
 */
import { config as loadEnv } from "dotenv";
loadEnv({ path: ".env.local" });

import { Client } from "pg";

const APOLOGETICS = [
  "UCT9gbDOQjYH8CQSG7-IMkTQ","UC8kOn6wIHfSo3Kj7l7hHhiQ","UCnmsAFGrFuGe0obW6tkEY6w",
  "UCh1W-CtmEfxf0bS_aChaKlw","UCzw5uctKtdaFtKDfw8jr8Jw","UCDbi7lv_CSHUfH4KZQe4zow",
  "UCyonqqzDFxw0p--8pe3ivlg","UCZ_kURL6ICI7Q3XFdKT1w6g","UCCVNFLUX8St8pSF1-kStOGQ",
  "UCqr90jZVfxOX53u7QiQ6lIw","UCeHZUUGlHZdi9P6NfVwdLcg","UCBjPnxnaw6DKhNUqsPa7csg",
  "UCD9dBPDSDvwkajmC0fPW3CQ","UC1qrw8ZQU9ZuRFXVmEValvQ","UCoLAowawEfrtrxvnQQAx2yw",
  "UC7gSP30IlaFEn6UQhBFSKZg","UCiVblqPv8HIAJxe-qDdXvDQ","UCpQxtFsUI9fKAgKNBlbsylA",
  "UC4sNdkh6GygZLbyqSxveCjw","UCcG4mSbsU4I1Snf1hK8N0Eg","UCkkRgJabQ7xL6VY6TvsLwAQ",
  "UCJKm1bBzdogI3b3DBbfGeCw","UCc1_qgYXADqNH5nJsbtUaZA","UCT7LM6-A0IkIlnDTq9C4tKg",
  "UCJJ4TYPZCKbZonuWVpA5XLg","UC-3WFOCWkUFQcX_1W3NjqAQ","UCVFMSQbMVD4wyiDZsQrLZ5g",
  "UC2LBmYIOq6Eu_ZC14i_YkIg","UCIzcrTP1x8GvrKQK46CYvXw","UCSFheLzrWf6LHrUNyqiNrCA",
  "UCJgEls1xaRLC-np8xiwI1yA","UC-WoTmY6w80FaTpWEgLYlvw","UCqtKadDOHIbx_Zjq9BhxQYg",
  "UCAaWdZ6LYYKY9lURNrBxuCQ","UC0zJ_9NzLAqlyf-QRim05DA","UC8xx0ALy8DyV-7GX_pPBUCg",
  "UCI5hNbazORioXly79uuPUFA","UCF0FQrYUOOBGkBVOfIIVX_A","UCUDevjpQ36aJaKJn9Zz62dw",
  "UCh280X-ZB7Vf12udX_7kZ0Q","UCFNi-bt0oFbPvWvv5UmmAVQ","UCZTD9FOk2-VMbJBSIOwsuzw",
  "UCRR4XHgl-G2u9fIE7POiz3g","UCAvoBmmoOI3I_trHm7UIhFg","UCYV6w3DfdL90Kx25eny2jew",
  "UC2nLd_yrneAOeTQvnx-OaNw","UC86Rjr7VBtXPoqMyjHVQz1Q","UCRt2kSddLmesnU7gG2PsDxQ",
  "UC3OdeG58hgWje8FfdN1ck8A","UCTAixq9yB2NP_T6L0W_9GXg","UChz8peIisHw9bIyb4l25ScA",
  "UCFf7vzrJ2LNWmp1Kl-c6K9Q","UC6UQzUW0-xY36oxWzXL6gBw","UCenBG7hxMzeq7jyWv9fSncA",
  "UCmUkJ1wrz5ld86GeLbo-L9g","UCuDPPEamDRNyzkJWiSO2Cvg","UCpumfWNEXE5YbL5QMjg5agA",
  "UCsx7zfda1Hlwy_9mUYeIgNg","UCbD1Pm0TOcRK2zaCrwgcTTg","UCKjvrCvP8hp74Ai94jkhBLQ",
  "UCDIA7na0zrI-NtdnXPE1yhg","UCu5C5cITg74Pan5NnT9a9PA","UCRTON3i5doZi00TRs2rBbRA",
  "UCn7_03Sk-bdzyq3aRQ-ziRg","UCIdNtWgTZXoiwhV6QhuAm8g","UCzGKo16QKpZqVu8HVwzFhsw",
  "UC1Zm16hQTOaT5xmgLnYMAsg","UCRpLQ76COpXkaOEc3Oo6NoQ","UCET8noj3W3b9mZc4c7cDzxw",
  "UCn5VMWkt48I4xZLqWZ8E0fw","UCWkVSgQolt8Af-nw2w1MekQ","UCSsrx8lFpeuBjNIE7FNm2CQ",
  "UCocFtIzP_6VWXgGWVRPzPeQ","UCRzH2MHEh5QXkN6aGq763Dg","UC6nQ1HxVl0Ky7LtlT0G2iyA",
  "UC8PPvHzJ9TPad5qWHAYmJHA","UCksFY6uP8K5UEMghFue7AWA","UCirRJVkv7FQs5S20b9WsaHA",
  "UC_-q-lIBnzzyB0BKISrmcCQ","UCamanbyoscF7bKArqwtUpBw","UC5Njt-96Uor0p-jhnoZHwMQ",
  "UCTNK6LIS0Ke0ofBWIUmWPNg","UC-7D_sWzEZ1D-PsEFF-Nb9A","UCbTVVfCZhRYSpG6P1G-Zj3w",
  "UCwJySRiyFIE2w99_bHvfmRA",
];

const CRITICAL = [
  "UCx6OgmoqJbOVRq-Lv1P7SzA","UCqrqFLPh4cRM1VomUzG24sQ","UC5n_8_6j00PSeju0hu2CFXQ",
  "UClQi5XklqD5HOAnVGz9_JsQ","UCo-6l1g27GdDb4riutS8I0w","UCPtTcNoYMEvKLKNI-7DcJ2A",
  "UCSI97UEpfnr80eWZLOcGJlA","UCEWF8CXx2-wRkfARfs1m6gg","UCj_3LxWyGAlX6fmOqn3J99A",
  "UCD71coYl-mS5LIBPPikICsA","UCAib1bMCLZh9Ln0Uq62xxjw","UC3Y4j05DDAXv7vCedrOQ9FQ",
  "UC2xfXE3HPcSjXHHIsDHqsBA","UCbwyMfNeCgJDaYLQkhRhLzg","UCQQAByHVqmp2DGkMk5SsOZw",
  "UC1ICXUC92McH31ZuvGNhxBw","UCePmBRQ7vPuYfA6jF1ATZtw","UCQsBbbNPfJG8GEVwyWHyNzg",
  "UCgJ7wMNvURkv8kwrRuwgKHw","UCAUvfqc4emuJG03XRPNxnhw","UCRHJfvdaHvEeIlyRi-QO7fQ",
  "UCzWWabJJpxQpfuVe5c-oclg","UCycge7lcqO57GcWNSnuNJew","UCE7-EZ_ANHRkYHv7wCUTt0Q",
  "UC85XrFXOO0zR6gpXG0XPL0w","UCwiPYUcQrYaxEdM9VjH4-rA","UCLSlObU_g5072-SWG92hMBA",
  "UCp8hDx_oDMWhbnNqAltCPoQ","UCPRHv273jr1IntJmn2q2qdw","UC8hNoLAnIxT7PIvRkrghDHw",
  "UCbx5SvNIhx17OEG2KjYe4IA","UCAMfNTlHdJk1x7pKJFB4kRA","UCnImnqtzoFNsZzqhmuMogUA",
  "UCvWDr2xEBhIpc_Kb97cPdCQ","UCZIIEsoqMxzCY_mTKvQUeMw","UCUx25TIZ2s2vAd5A1bihipw",
  "UC-D_X70BAr9n3Y9VwJac5oA","UCgWaba_7ge2qP0MRAfGwcjg","UC3BfXdVCswUEeN079DYBAXQ",
  "UC2VfKbAwaQ7RrHGuv2gXr2g","UCx5yNRufseSR_JxYC8GJ2iA","UCopxTiqSmR9YUCTKXURvPtA",
  "UCEfPXVNd7OEb59hHfb03Uiw","UCNYIeulcLs85NLINDyxzHQQ","UCLESyNtVAdYF52HVt5Cu-Ew",
  "UChGtUIlEr_pS4ZnEk4uBEaQ","UCyEs326admEf6ymfk5knRkw","UCSlmU_LBLolo-9n85PTfCwA",
  "UCVVt1NOMv-nZRdwdN0YawXw","UCtGm9BMgK6tDRwj6ReQcPZw","UCNYun19DjvHSJjrn2HiS8nw",
  "UCicTb-Z1c7xeutxkHM-xy6w","UCmugDAfPv3uysim0HmQe85A",
];

async function main() {
  const ref = process.env.SUPABASE_PROJECT_REF!;
  const password = process.env.SUPABASE_DB_PASSWORD!;
  const host =
    process.env.SUPABASE_POOLER_HOST ?? "aws-1-us-east-1.pooler.supabase.com";
  const pg = new Client({
    connectionString: `postgresql://postgres.${ref}:${encodeURIComponent(
      password,
    )}@${host}:5432/postgres`,
    ssl: { rejectUnauthorized: false },
  });
  await pg.connect();

  // Apologetics wins over Critical if a channel appears in both lists.
  const apologetics = [...new Set(APOLOGETICS)];
  const apoSet = new Set(apologetics);
  const critical = [...new Set(CRITICAL)].filter((id) => !apoSet.has(id));

  let inserted = 0;
  let updated = 0;
  try {
    for (const [type, ids] of [
      ["Apologetics", apologetics] as const,
      ["Critical", critical] as const,
    ]) {
      for (const id of ids) {
        const { rows } = await pg.query<{ inserted: boolean }>(
          `insert into public.channels (youtube_channel_id, slug, is_active, channel_type)
           values ($1, $1, true, $2)
           on conflict (youtube_channel_id) do update
             set channel_type = excluded.channel_type
           returning (xmax = 0) as inserted;`,
          [id, type],
        );
        if (rows[0]?.inserted) inserted++;
        else updated++;
      }
    }
    console.log(
      `Done. Inserted ${inserted} new, updated ${updated} existing. ` +
        `Apologetics=${apologetics.length}, Critical=${critical.length}.`,
    );
    console.log("Next: hit /admin/refresh to pull YouTube data.");
  } finally {
    await pg.end();
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
