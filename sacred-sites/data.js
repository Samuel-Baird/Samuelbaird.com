// Source: Google Sheet "Temple and Church tracking" (tab: Temple log).
// NOTE: the sheet's "Longitude"/"Latitude" headers are swapped — the first number is latitude.
// Payson and Manti coordinates in the sheet pointed at Orem/Logan; corrected here.
const PHOTO = "https://photos.google.com/share/AF1QipOIdxUxqxNW28GH9YOg2tEyrgmnIA0dFRqdHO_SX2NkQqYpMxc4BNhGOR4OcGWN2g/photo/";
const KEY = "?key=SkVJdXRTZUc2WVJUNkQxYWNzXzBUd3B6bmdoY2xR";
const YT = "https://www.youtube.com/watch?v=";
const LIST = "&list=PLG-KprIGehTCRMddNiVkEtJOJSyrpd7cB&index=";
const P = (id) => PHOTO + id + KEY;
const V = (id, i) => YT + id + LIST + i;

const PLACES = {
  jr: ["Jordan River Utah Temple", "LDS", "South Jordan", "Utah", 40.56621903, -111.9312639],
  or: ["Orem Utah Temple", "LDS", "Orem", "Utah", 40.27099245, -111.7197097],
  oq: ["Oquirrh Mountain Utah Temple", "LDS", "South Jordan", "Utah", 40.55158546, -111.9872696],
  bc: ["Brigham City Utah Temple", "LDS", "Brigham City", "Utah", 41.50578839, -112.0163514],
  lg: ["Logan Utah Temple", "LDS", "Logan", "Utah", 41.73464394, -111.827697],
  py: ["Payson Utah Temple", "LDS", "Payson", "Utah", 40.0436, -111.7311],
  pc: ["Provo City Center Temple", "LDS", "Provo", "Utah", 40.23302813, -111.6593384],
  bo: ["Bountiful Utah Temple", "LDS", "Bountiful", "Utah", 40.88318871, -111.8468992],
  ss: ["Saratoga Springs Utah Temple", "LDS", "Saratoga Springs", "Utah", 40.3443595, -111.9325555],
  tv: ["Taylorsville Utah Temple", "LDS", "Taylorsville", "Utah", 40.66699239, -111.9545262],
  dr: ["Draper Utah Temple", "LDS", "Draper", "Utah", 40.49588793, -111.8406412],
  mn: ["Manti Utah Temple", "LDS", "Manti", "Utah", 39.273392, -111.633402],
  mt: ["Mount Timpanogos Utah Temple", "LDS", "American Fork", "Utah", 40.39312304, -111.7703787],
  og: ["Ogden Utah Temple", "LDS", "Ogden", "Utah", 41.2277996, -111.9712937],
  dp: ["Deseret Peak Utah Temple", "LDS", "Tooele", "Utah", 40.572634, -112.313923],
  sy: ["Syracuse Utah Temple", "LDS", "Syracuse", "Utah", 41.099097, -112.075279],
  ly: ["Layton Utah Temple", "LDS", "Layton", "Utah", 41.061631, -111.937784],
  if: ["Idaho Falls Idaho Temple", "LDS", "Idaho Falls", "Idaho", 43.500275, -112.041701],
  ve: ["Vernal Utah Temple", "LDS", "Vernal", "Utah", 40.453244, -109.536636],
  sg: ["St. George Utah Temple", "LDS", "St. George", "Utah", 37.101225, -113.578094],
  rc: ["Red Cliffs Utah Temple", "LDS", "St. George", "Utah", 37.082341, -113.518732],
  cc: ["Cedar City Utah Temple", "LDS", "Cedar City", "Utah", 37.671341, -113.09637],
  mo: ["Monticello Utah Temple", "LDS", "Monticello", "Utah", 37.877613, -109.347073],
  li: ["Lindon Utah Temple", "LDS", "Lindon", "Utah", 40.337243, -111.694798],
  rx: ["Rexburg Idaho Temple", "LDS", "Rexburg", "Idaho", 43.810224, -111.779237],
  sda: ["West Jordan Seventh-day Adventist Church", "SDA", "West Jordan", "Utah", 40.587188, -111.946699],
  ang: ["St John's Anglican", "Anglican", "Cottonwood Heights", "Utah", 40.621629, -111.844695],
  epi: ["St Mary's Episcopal Church", "Episcopalian", "Provo", "Utah", 40.236819, -111.66007],
  mad: ["Cathedral of the Madeleine", "Catholic", "Salt Lake City", "Utah", 40.770047, -111.881326],
  jw: ["Jehovah's Witnesses (Utah County area)", "Jehovah's Witnesses", "Lehi", "Utah", 40.429081, -111.884516],
  sjb: ["St John the Baptist Catholic Church", "Catholic", "Draper", "Utah", 40.53606, -111.8814],
  uvu: ["UVU Mass", "Catholic", "Orem", "Utah", 40.279797, -111.7154],
  zl: ["Zion Lutheran Church ELCA", "Lutheran", "Salt Lake City", "Utah", 40.745705, -111.831571],
  go: ["Prophet Elias Greek Orthodox Church", "Greek Orthodox", "Salt Lake City", "Utah", 40.65385, -111.833431],
};

// [date, place, type, language, notes, video, photos]
const VISITS = [
  ["2025-01-10", "jr", "Baptism & Confirmation", "English"],
  ["2025-01-17", "or", "Initiatory", "English"],
  ["2025-04-30", "oq", "Endowment", "English"],
  ["2025-05-01", "bc", "Baptism & Confirmation", "English"],
  ["2025-05-01", "lg", "Baptism & Confirmation", "English"],
  ["2025-05-03", "py", "Endowment", "Portuguese"],
  ["2025-05-10", "pc", "Sealing", "English"],
  ["2025-05-13", "bo", "Initiatory", "English"],
  ["2025-05-15", "ss", "Sealing", "English"],
  ["2025-05-23", "tv", "Sealing", "English"],
  ["2025-05-30", "dr", "Initiatory", "English"],
  ["2025-05-31", "mn", "Initiatory", "English"],
  ["2025-06-06", "mt", "Endowment", "English"],
  ["2025-06-07", "og", "Endowment", "English"],
  ["2025-06-14", "dr", "Endowment", "English"],
  ["2025-06-14", "dr", "Initiatory", "English"],
  ["2025-06-21", "dp", "Sealing", "English"],
  ["2025-06-28", "sy", "Sealing", "English"],
  ["2025-07-05", "ss", "Sealing", "English"],
  ["2025-07-12", "ly", "Endowment", "English"],
  ["2025-07-19", "mn", "Endowment", "English"],
  ["2025-07-26", "if", "Endowment", "English"],
  ["2025-08-16", "ve", "Endowment", "English"],
  ["2025-08-22", "or", "Baptism & Confirmation", "English"],
  ["2025-08-23", "jr", "Initiatory", "English"],
  ["2025-08-30", "tv", "Endowment", "English"],
  ["2025-09-06", "or", "Endowment", "English"],
  ["2025-09-13", "or", "Sealing", "English"],
  ["2025-10-08", "or", "Endowment", "English"],
  ["2025-10-18", "or", "Endowment", "English"],
  ["2025-10-31", "or", "Sealing", "Spanish"],
  ["2025-11-06", "or", "Endowment", "English"],
  ["2025-11-15", "oq", "Sealing", "English"],
  ["2025-11-26", "sg", "Endowment", "English"],
  ["2025-11-29", "rc", "Initiatory", "English"],
  ["2025-11-29", "cc", "Sealing", "English"],
  ["2025-12-26", "mo", "Endowment", "English"],
  ["2026-01-02", "or", "Endowment", "English"],
  ["2026-01-31", "sda", "Worship Service", "English", "", V("Yokn4bc1Eqw", 5), P("AF1QipOBDbUkCbbqTlB0WLpcJQLsmwIOPUUXKjWPUcq6")],
  ["2026-02-06", "or", "Baptism & Confirmation", "English"],
  ["2026-02-07", "oq", "Initiatory", "English"],
  ["2026-02-18", "ang", "Feast/Holiday", "English", "Ash Wednesday", V("sEC1SoJJY04", 4), P("AF1QipNanyaCh83CNiBx9w-Cu9qB99t-TvS949zdrdr-")],
  ["2026-03-21", "og", "Endowment", "English"],
  ["2026-03-22", "epi", "Worship Service", "English", "", V("Vq7SxPrWgP4", 3), P("AF1QipPWFAdjb4G1Pn7ecg9t3Cwr1NDCl2njWknCQ6_3")],
  ["2026-03-29", "mad", "Feast/Holiday", "English", "Palm Sunday", V("HBe6fQVyDfs", 2), P("AF1QipPLERPEjpdwHZN3Dh2Y69qtMt3pPeVMlIMz_ClD")],
  ["2026-04-01", "or", "Endowment", "English"],
  ["2026-04-02", "jw", "Feast/Holiday", "English", "Memorial", V("hytiJ7ttQN4", 1), P("AF1QipPkglcl8zfWBV8H2HF4DKBlgCMlU7U4fXsxgW0N")],
  ["2026-04-04", "sjb", "Feast/Holiday", "English", "Easter Vigil", "", P("AF1QipMqOes1ychXiWfZupELj6uVX2iXLmNbhD0Jobqa")],
  ["2026-04-06", "li", "Temple Open House", "English", "Visited with my lovely wife :)", "", P("AF1QipMV6z1YZvcCb0OuTKtV8cm5NzWBbSekJf6LALzG")],
  ["2026-04-08", "li", "Temple Open House", "English", "Visited with Brock, JD, Joey, and Raymond", YT + "Ni5rlPGYviM&list=PLG-KprIGehTBOO22Zo87C2bdRWCbca_NO&index=1", P("AF1QipPhd-U5BsQVHnOfcJI1tmZEjl20QjbExZNTyZIj")],
  ["2026-04-23", "uvu", "Worship Service", "English", "On campus mass during finals week"],
  ["2026-05-15", "if", "Initiatory", "English"],
  ["2026-05-16", "rx", "Sealing", "English"],
  ["2026-05-31", "zl", "Worship Service", "English", "", "", P("AF1QipP8MpIpuwT_uHBwy9jrXLUSN4X8zYC55DRvuASp")],
  ["2026-06-13", "dp", "Sealing", "English"],
  ["2026-06-14", "go", "Worship Service", "English", "Baptism of a friend of a friend", "", P("AF1QipOg6DbnBkwvlg2HqnL2RFFhu7qmBD35_GtKcQeu")],
  ["2026-06-20", "li", "Initiatory", "English"],
];

// Visit categories come from the visit type (see lib.js). Add a visit with type "Grounds Visit" or
// "Historic Site" to record those kinds of stops; every place below is in COUNTRY unless listed.
const COUNTRY = "USA";

// Photos from the shared Google Photos album, matched to sites by the date taken.
// Each entry: [token, width, height, date]; full URL = PHOTO_BASE + token + "=w800".
const PHOTO_BASE = "https://lh3.googleusercontent.com/pw/";
const PHOTOS = {"jr":[["AP1GczM1flVLlkx7dJxmGjLZy0tXFzDEske9vwOzs0Dtf-KRkjqpPk-t_jw1u5HQJaKiOyc0w6mR2Nr_YDJJOzpcC8nrEatztSgltNJAd5zexxJivAu6fWgn",2862,4032,"2025-01-10"]],"or":[["AP1GczPwQ8xqJSck9wX70IuXPUtSgw0OwZM2EWR_HULGqMoIwA7TtXOo0ceZSr_gOrc1l24xENgO3AfL7-1TD0CRuQvG3aDlhlkN9vE9W3dzy0rp0m4aw-n9",4032,3024,"2025-01-17"]],"oq":[["AP1GczM-wIr2seutUwMy7AoW1T2Wm5BFIEvaQBb8wdqy2tAICHiYGvLFmtkXGxwI65f_MOxhovB9Rd_vaO8aI2zGDgTQ97Mtl9mhTn8P1v7L7rzLy4SZKTqo",2316,3088,"2025-04-30"]],"py":[["AP1GczMOuL5VqDjqWGANERcNoZNYyb3notxSVY0To6j4hTtclFP5okyM_FIW9tHBoLFqJ3emjPKWbstNAbI3-vETT2s4DYOGG2t3UFhUT4EyjmmcAFooLYpD",2316,3088,"2025-05-03"]],"pc":[["AP1GczNki-U7nAz7gvyGRaMQDi7s_b-KfWtiAzXFylSx1Gw50r8qQkLl0AUCSXwTJ5z-ZwgdIMJr4kzF6oLaK1xJjrtOw8O11Al9IhVsErddzDP-sixAAVAw",4032,3024,"2025-05-10"]],"ss":[["AP1GczPn-u3vv2RiEKVj-guxhWGTIw7pq0LnVSnWW-UURFSviLZk9r91A8DTvYjQSlsrTRBYJfEbyRUqZbsFdGucKRq4Ndqd2Ntkcov2yLxM4puo6UORpb0U",2316,3088,"2025-05-15"],["AP1GczOYHpaZKEJba1XdHTBYAonuh6yVu8LLNddzReu34MY9ZWVwnyKx5H4msI7-UH-7FUhiZkRRkFeNpHBGgyimowCpHcYVD3VJ4ZouTfQrHNNfIBo4VKxw",4032,3024,"2025-07-05"]],"tv":[["AP1GczO0rbEXeGc4WxatEECcgORFaIidR5ar-LEBiSJhSf9tCKjpZ7woAkOdUwLUAvnRI0CQvyE94xPDXXXPJ5N30ZM2LCLi91pzPK8AHtUBq0U-La1JeaPS",2316,3088,"2025-05-23"]],"dr":[["AP1GczM1Oi3KdAcfQouHBObH-uul9ePUZmzhjOwbhA6ElsROrbfQeuM1O0fnYYq__Z5kjdhWGZGFhS52ulf3r9ipBBJ9IUSrjsa1pOoL8MLZ4-z74zN6xNTP",2316,3088,"2025-05-30"],["AP1GczNR7PzsYZ10E10aXfDOcRNJ4cpzY43JcK9qteQYT92P1QB5oKa9hud7Idyn5SmVmq-FG_foWp8fvU2CrXNdlQFWyt4PLNvk1MuGI-ZZijpN43lPBJdk",4032,3024,"2025-06-14"]],"mn":[["AP1GczOB4ZATpJNETUhHrEA74_MwgJwWJJa7sostPfo5B6nk-4PoaDrft4W-e5EoAnv2nBWGS5XB1FzhoJfdMUynYLGeFDjV2IrGl200dKflJvr_1KQACiEp",4032,3024,"2025-05-31"],["AP1GczMhJc-GPzNjXMaqqZ--xbKDFnV8WGLy0ccZWvjDXbhnZN0W3DY7kBnw587FozqajqZ8NITsRZh8V50uZtiF7yoIBsdCSd5aUMbPSM9ajm-fP8BzzON3",4032,3024,"2025-05-31"]],"og":[["AP1GczN-6Wg0edvsqVxhk7OjsBjAKXaFXF4wu1PYMbHEuVZfZstUbDg04XmN8SE95iSqvgf7Y1yBFit50Yzc-ccjxW2kc-ElyfPtqI8vbYW_eTpyKju1ROIc",4032,3024,"2025-06-07"]],"dp":[["AP1GczMGHL_L20zSzTzqFj1mJRAi2Lc7KqXitGT8DNpWwSrapbbCfeuM8TXAj3veglM0QUixm-0JXhuJDz2bPYOJYmrPJEeemD7LS8DHDc47XC7HQgCiMm3O",2316,3088,"2025-06-21"]],"sy":[["AP1GczNCl1uQ4OVXksj9uCwMSa2yy0lIATv1QEJ5V8hcKjsY3z_3GToocP4ofMTr4CjiTqJn9a64uXzoZHhsasXHsyRf7hIdUa7XEhKjSU6U5MgO4waXrXu1",2316,3088,"2025-06-28"]],"ly":[["AP1GczO9Nrsx4_kzoKX75oFAUjPEN0FJV_pySJnGbQpjQs8YoMzmZo6RgCXo9GY4ViOeleK3h6M5svpHK7ZNjNLkZ-yIm_kyLMRLBV5BwtGG3zEUu45X-K84",2316,3088,"2025-07-12"]],"ve":[["AP1GczP4n_w-TXV4D9PYNcqnJiPqS5jiUaMkWHIuOI2pO0F7DV4GPQW9zfzP91NqSYttFZTxAUt5pt6iAetLdFa6bc4VQbaZyScBJ_F2z725xKXI06DgVkNi",4032,3024,"2025-08-16"]],"sg":[["AP1GczMD4mq1s-FVQTlSSOGiSiccgXEpvX4qaArX9512UF6vsX1BCOBFf9MwKD_0Tc0ybtUrUgEsueXvjc2U95dWDotDusNzervs_xEUGpQ60tWtOdjRzHP0",2736,3648,"2025-11-26"],["AP1GczNtXHi-fHVduZulb3ujb0NV8qOgK710XEVEbFkTtvtowOeX1AoVUAXHh5wY1g2WAWfU8B0Y7UN8rHE_aOQcb1Lv7qM6eBqH_21Nh9YeRVL7Nc2VIkT5",3648,2736,"2025-11-26"],["AP1GczNrfkTjd8JrvgsI4coXOpR4Js5cJUuSXiHUXGMhCUdkUwx6qEer-yom6lsgwHc3Kb0zXfYyUSW_xs-VUgQTi6YdfDhpLz9l97CPunX1XInhRCEZ1f_g",4080,3072,"2025-11-26"]],"rc":[["AP1GczPn08JICXWGqA3sV5wIORoPJ_LMzYGYe5rVX_IhVw1SuMGFWcMpmO2J1hLCIaeZf3DFG17GcZQU3gaCQjrPF8wfZjBhJwSs2uF1ddKLEo1r_1Y4tiyv",2736,3648,"2025-11-29"],["AP1GczNkZKp-bz-YKcRu_Ir2_7M604KOBi00b5vLRvDLD4U0eX_-1uUBbwkne3DvYVIR-QUOac9E3je5Md9OYq6rz1uCPc6Im_jF6NxL0ro6jtePdTwW9_je",2736,3648,"2025-11-29"]],"sda":[["AP1GczNI4HViUPeeBwdYTP2481KTIbEReQi4QavksiKvGy6tvBlRLXFmjUuYZ9mxyK0GJwQ5HqUdoq38ABmHgJC_48FUMbLuILoi94EmmwhSRnADb5yLGXY8",3072,4080,"2026-01-31"],["AP1GczMGO2fQwP0FSCTTg4mvu0i0RjC6sQBpFtEvjrA-up2213ey-mT8ZE-UNvM0A88U67fQaJeqVEqy_nxMg5RHecAAznzG2ZQDPXDA1qL1QAJZbucr4XCJ",3072,4080,"2026-01-31"],["AP1GczN8FxbD_dXHzhOJkfDVX6NFr5Ca3HMK21xgFuX8tVAvroYVPrDJx9kQwTwDqNOpNtiE8r058G2Yn5bw148X0uSVc6FIPtkmRQiJp4tD0cWdVvmqOJCg",4080,3072,"2026-01-31"],["AP1GczN5_dr6efAZJEe-mAuzEl-By9NcpWksa2UGKiPrugtj8NzczWUcfMMUxoewSW4E_bPLlpBXMDvWKFyFyamLhEWrXTzYs-5heh2R1IhukXfQeO92ccEi",3072,4080,"2026-01-31"],["AP1GczPormkvT5z68uPC3ZZSrRqcZCSeg9imHcnLbS4yFF3R-3aHSJ8WzLzdHB5hOQnUzTFV8Q6wNKIisFZ2WESwWj9tZqgW-r36RyOUT9ShnIrMA2f0NJiE",3072,4080,"2026-01-31"]],"ang":[["AP1GczPSML-WZt5xLT423As12Su5YIiXpOmYJCPW91qHMBW5YsvejeGq0aWjK4piKIL7wWbDEATplKMpBq3hmMCarm1yJrz5BNCAXTL1yuwX2-yXQaQo1pNj",4080,3072,"2026-02-18"],["AP1GczMwUhy3yI6ZoAEXbEQFYXmEDKW6083PHIaQf9pPAmTc8XYJV_jB-4zr-Jab1Ghp2NfiNu14F7a2uQ_7wirhtQi9T1RcgpERIOJc_s-xSLNXs-TZyzGq",4080,3072,"2026-02-18"],["AP1GczOvqzJGFjMpLbbCLin8EqxD6BmXOuw98QGBq0gDM7dmdCBOmSsKNlAuObuAebYtMTW4VQOjOG_5RSf1D2-ngNlYWLe7L75GVBA-_ZOMP8bIZ2P-ajKC",4080,3072,"2026-02-18"],["AP1GczMt97jcqZi41DyaMP_hdZyhAATJ-u3Xi26VctlkmAZDIhjvKb9oW-h5s15n7Sme77K8jotQn-AFjNL8GRcQ6qkfQ99lKyDuDQf7I6Tfor3nDStElW-j",4080,3072,"2026-02-18"],["AP1GczOauwEQETFHLKLGEraXJgPhhF6fzjBjZlFW671OxXbA4CXAzWWWi72bZHo6qOa1K5fnfSdsPxvt_WLO0hBtgV5sPHRsq_OWYPWCCqCVBpeaFWNzAg5I",4080,3072,"2026-02-18"],["AP1GczMUKyvf7XTnSZCx7qDQZsw67GUrYUHyV-Mwgh79He6rXqIHp4kinI0GjBpYFi8IusNjej3e1-h8Q700kmwDtGRnNipiWgsewuFHw_tAmsA3vXYJ-Zcg",4080,3072,"2026-02-18"],["AP1GczN3ERT-qIj_v9li0r4ddqP5LzX4LmIUE6-b_oA-Tjp0dGa8wYKCW5Dlwc53S8-A8t8U4feoqpllBtq5kvJVlvSMwCVvObuIVmIjFxb821DQMFpkUSff",3072,4080,"2026-02-18"],["AP1GczMrnNDzL2JwztKNTJyA4O2OFk_XJ4DyI-63Ghuz666-eBhWK-6NwizniYeNOnonYlbBmJrf7HLLe-cJEahrzXkFODDrlmfU4df55AijF4_O0SmQK2R-",2736,3648,"2026-02-18"]],"epi":[["AP1GczNwrMYjdm2ferpDh85LxbGRI4ghM2Zvpu298F2-4SJxix69LkjVagevyHelRkAIxdDwNsK82t4X6c68ST9fZwMOQrogPLtlTZDFPBMH1wvqdR6zn2uB",4080,3072,"2026-03-22"],["AP1GczNDUrI338-KB0z3j4l4S6DAjsW4PWavbB_f_o9wh8TwAa0s3L2lfVGhMutCMrdAHN5rdfVnJ4L5gqwiuiJZDFrjG_V3-2d48zwmaHwJwL6k153I22Jh",4080,3072,"2026-03-22"],["AP1GczPHNqKyczhuKJjwePalCLUPVWSgwLr_-wMGQAxe7xwmE032dDqNZqiEcq2FJnE_Slse_vBlpuuson55JaECxa7BMoGCL1lFr3kQl0xXSOIzY9vYV7Xt",4080,3072,"2026-03-22"],["AP1GczPDM8vr6QE-3_0Q7JxkCOqUBSvqiiE_FXfC0mxoH_2knWEy1QrHaD6kuXV_Mwo792IOit5g8mWT7QJgvfDx3mLiJy9EB_Pp-fJYP0HQcj9Kyml7yO2M",4080,3072,"2026-03-22"],["AP1GczPLG1AFyslg0vznvh4p4Uwwx57bXWqHnZsMXTnnGQsiwORj9CJFnvseKPKAQzsoKq0JSEM7mW1SuYWGJ2qbvabKMHEVFXczQDxXftkTXmIWdW-Gepah",4080,3072,"2026-03-22"]],"mad":[["AP1GczOO-FXsDjYAaEPtItpUqjCl89RUMqKePEp3QYwVpXBWd2PMZd-4phg8KxLb3OfL3gGvNcdPfYfnU2F-U3JQ-oB5UlW31kAcqBRu6WUE2l_ft-rxMNq3",4080,3072,"2026-03-29"],["AP1GczPx-WE1nQa2lE-1Fy211DmAie3i9sS9tN89-T0VJfiFzi9OMDziNcYKH6hZpWGsRkl2CE_kpA_4kD1cGdWHw6L8X4Hij2DM05kD-hiRDFMUKt0MFiim",3072,4080,"2026-03-29"]],"jw":[["AP1GczOlKvJoH4271MaHbF7CiUXFtlBToJGluc9jbYWPoSSrH0y0OFXFIomDzKsW2oiP5edSpgcMIbgKWdCMifYvm-1HuqAaK8xu8Lz2iSe64ihINFNFm958",4080,3072,"2026-04-02"]],"sjb":[["AP1GczMlN3u36KeU2gxo_rWDkRMvALWW5G-PHodbtj0bAE849Dy1EV0AZV2xw9bRtre4eirglZZ7VnxqY6EsfyLfLMJC-LiahuIGbblUTAoUaloZTjwjrqxo",3072,4080,"2026-04-04"],["AP1GczObuxMNIhw62fkXJmOj-XCJGMns-GZ0zm9f73wcc9Qi0oBz9iv-xFrtu3jnfhJndtBqS6Xvt0HVGnVsl8XAK25KkLWnzqWJzFW0Ne14e3c70K0KsImU",4080,3072,"2026-04-04"]],"li":[["AP1GczPSDdlsb_b57BlQHEk02aVScBvqPMolVsWqk1l5e3pCiNeJrhgyRSaSGJ6p5EQO0qjJsIUtPJ0V4-5RYXS1mJJ_I_7oObIcvGz-XQJWLa9GWogGbvGN",3072,4080,"2026-04-06"],["AP1GczO5tNDlHmeMHfnPLrCwlarw2W9aTQ4Z2v1EsGbhkBw_RyTEfURa9Ex93HM4KLluli7wPA-VtITd24cx4g0Nzm5usIV0crH_oC-EC_I2tGIRipGFGgVc",3072,4080,"2026-04-08"],["AP1GczONTbQV1oUK7oMDvmBvpUW5itKDCs7OPcUEVnWuIsi5sbMz0wCu0gIzHjKhqSmQRj7FKUEsBuC-206MBmue-1ILTb8oDWjStCRXS1PldfHDdh6CCCe6",3072,4080,"2026-04-08"],["AP1GczMHUYyo2YFeUCvtymKmjwR4Zj1Ya-7wBPdqrq3LyNDrOBO3GzUaU2cDi9FNyiGv_NpkCUNZRL1VUcASHLd26rS8RFeGNOKuIeTzgJli2m5pv-X0GFoK",3072,4080,"2026-04-08"]],"zl":[["AP1GczMwnUCJQLp8qZ9MzW6ihIXk_9897VrzIa3WF9PUFkmJlDcgP38nDVCJBW8UwpIfCeGpKDiq-OI3LsYwX3qSZdXclCL7R_CnElpNn5BdmiYvXDKHUkzT",4080,3072,"2026-05-31"],["AP1GczMAz7eFGW-6FoIxPb7a7isZxR2BLxlCb5aRtQKhqGB-qWRT6OyHGcRxlvCoUxfc3fvAFii5pAXHihVnZ-LgJKRloxLKj9auEa4fv1GBWEJfnwmuFwrp",4080,3072,"2026-05-31"],["AP1GczOjg_EDWutkIA3V12yGD1irXrroOWujTZxOueT3YCB14yBjl9JkU5Lzb-G4xgQL4OemOS8TtpkFgewbiHLjCYqN_MrBEVpdPfN8FiM1mQgUnFkMt_s8",3072,4080,"2026-05-31"],["AP1GczPXsKmb1lMFyr83wKDDNekyjkTKoZl_n3tCdygHh1ptgUZtcy-WUY5ao02Nitsm3lWep4YcPFYpnoNGsk9fSmK_HtBobA7QDCU714scy0l1l2xsprUQ",2736,3648,"2026-05-31"],["AP1GczP7MvHSF8QbkFrtBYp0USJ8-BuPkxbUVyflLANL8LKMr2i0iDcyO4Jtxa_oTF1fjJI_xaksG4-_ANesyQ5a2pEkOsuAY2ZVpi_kDOcIwYseYEkPwuQ6",3648,2736,"2026-05-31"]],"go":[["AP1GczOK9GaoQ-eqKFn35gropGDmkyUsTK5ZX2xnIHovHM4jKOcwxrGmnR7nao2Qzaog6FH5cG8UavcvJ--FxtuUuFDkCMFx_MMXUXRE_bgWKYD-2INB3d45",3072,4080,"2026-06-14"],["AP1GczMhfBhoNIpaPrfzR_GzBQElDRtzYwRFGX-ys5jxn9FtCSWrRYncNc2MuVxWktT_jnPA4wy1e1pNTegad8kfXJyCW9SG_ltiHiU8u-P4StXRIQ-rIBgp",3072,4080,"2026-06-14"],["AP1GczOIvft1GGg3cZh4JaMbqbes-os6pQjC2y_wviBJaPLQF-w1HX3ecA_65TfPUMBmNIadl1TZv9CQ7fYNBSk73gIxXQ76sqY7XCBvFbJuPHUhKQkhMS8G",3072,4080,"2026-06-14"],["AP1GczORUj4y8yPkPc7_qnp038bBdV662RiceA_8jTakYXIgLMYCTP7FgIlpbIYmmAainR9VckaYoOfzv2Wvfcryqn5M26UpnFjamXw8V3l4QtBOF6TMyaI4",3072,4080,"2026-06-14"],["AP1GczO8QY8Ob0WwokOkf6ZH5INyvIJ6_kBlG3-rhVWELX4NbqslFGUl-7hKY-hbwYpFSchhJyippcaj20-DqH4lZWG7Jj7csN2le6TYkmZwCF3ZPEoiwFKz",3072,4080,"2026-06-14"],["AP1GczNAQZbR3-SF_bwx2IjlmplOfhas7GDWZ3FzCMc7doMfNcP4naiDZ_bC9Hfaq5TYxTut2JZFTCkiz__6z4G89TDXDejwau78Ek-zyxl1Y-mDHRAQxpfE",3072,4080,"2026-06-14"],["AP1GczOackxv8xOTAPYSnrMiyJBMKzdygmJas-9sHWMS6AbNUj_8njR3J7cxt81FikUTdPQQcKNfx1KZXkuiFA6syqSTfL1ia1wyiu6V_MhAUA6rUx0vCWcA",3072,4080,"2026-06-14"],["AP1GczOpAuxz6MVqUsTJ-29twaeTM6e0rGQjGYL_l6d_wrw6ywRLOkI_GWuEukqjUoOVjSN3SzKms3xzUoIx5qdIfkVybE1_NQa7ouSG12xQp_pjpvVEW_Jj",3072,4080,"2026-06-14"],["AP1GczNSk67I1nSZ4EKbnAWXvifmeMz755_GbGYOZ3Zw-pToRxOfxMXOOptmSidavoaoqCSeNqczS4W4gkVt1hxO_bzzc1GwiWj1eveKI3ZDvxt5sR8gPnyh",3072,4080,"2026-06-14"],["AP1GczMixFrm6AycSN41GjrdbHiLZKrTKHkLlRM9ijTAWs47B6nu1EryacfZsFeOUK6eSY_arsuz9GzZYHFK_PrCz9pCtxBS0e6jHqEQMXOVzF7lL4cr3Cma",4080,3072,"2026-06-14"],["AP1GczPOB8Of_4_8ZtWwNYgg8mv9wW6pJIi-26SQ0pruLGOGL5MrVhNCdPFSlOcWd-AhPYCWyS0Px3Ntv4hwD-FaMpWckriv2_QTTzrwQrUfDVUIoMGScVcf",2736,3648,"2026-06-14"]]};

// Wishlist: sacred sites to visit. Hidden on the map until "Show wishlist" is turned on.
// STARTER EXAMPLES, not confirmed picks: edit freely. Coordinates are approximate.
// [id, name, denomination, city, region, country, lat, lon, note]
const WISHLIST = [
  ["w-stpeters", "St. Peter's Basilica", "Catholic", "Vatican City", "", "Vatican City", 41.9022, 12.4539, "Heart of the Catholic Church"],
  ["w-sagrada", "Sagrada Família", "Catholic", "Barcelona", "Catalonia", "Spain", 41.4036, 2.1744, ""],
  ["w-canterbury", "Canterbury Cathedral", "Anglican", "Canterbury", "England", "United Kingdom", 51.28, 1.083, "Mother church of the Anglican Communion"],
  ["w-holysepulchre", "Church of the Holy Sepulchre", "Greek Orthodox", "Jerusalem", "", "Israel", 31.7785, 35.2296, ""],
  ["w-westernwall", "Western Wall", "Jewish", "Jerusalem", "", "Israel", 31.7767, 35.2345, ""],
  ["w-hagiasophia", "Hagia Sophia", "Other", "Istanbul", "", "Turkey", 41.0086, 28.9802, ""],
  ["w-sacredgrove", "Sacred Grove", "LDS", "Palmyra", "New York", "USA", 43.016, -77.235, "Historic site"],
  ["w-kirtland", "Kirtland Temple", "LDS", "Kirtland", "Ohio", "USA", 41.634, -81.364, "Historic site"],
];
