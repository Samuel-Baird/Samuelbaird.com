# Script — Is the Mormon Church Secretly a Hedge Fund?

**Slug:** `church-corporate-landlord` | **Estimated runtime: ~245s — OVER the 60-180s budget by ~65s** | **Source time:** 51.0s (~21% of the new total)

**Hook (title/description only, not shown on screen):** "They got fined by the SEC for hiding $32 billion. Here's what they didn't tell you."

**Revised 2026-09-12 with new material from the user.** Five new beats added: an endowment/demographic rationale for why the reserve exists (`n04c`/`n04d`), an operational-vs-investment real estate distinction (`n05b`), and a per-member-math + non-member-aid closer (`n10a`/`n10b`). All feed the positive-case half of the apologetics-playbook six-step structure (steps 4-6: give the LDS position, positive evidence, compare explanatory power) — this project was previously mostly steps 1-3 (state the claim, test it, concede what's actually settled), and was thin on ever affirmatively arguing why the reserve makes sense, not just why it isn't as bad as the clip implies.

**This pushes the script to ~245s, well past the 180s ceiling — flagging rather than cutting anything to force it under budget**, per `script-format.md`: "if a topic doesn't fit in 180s while doing it justice, split into two slugs rather than compress. Do not shorten evidence coverage just to hit the ceiling." Recommended split, marked below with a `— SPLIT HERE —` line:

- **Part 1 — portfolio/investment strategy** (`c01` through `n04d`, ~130s): Palantir, TKO, the screening-consistency gap, fund size, endowment framing, and the new demographic reserve rationale. A complete, self-contained argument on its own.
- **Part 2 — real estate and the concealment scandal** (`c04` through `n99`, ~126s): the Blackstone comparison, the real-estate operational/investment distinction, the settled SEC concealment finding (unchanged, not softened), and the new per-member-math/non-member-aid closer.

**Three sourcing gaps, flagged rather than fabricated (see `docs/saint-capybara/common-issues/church-finances.md`'s 2026-09-12 addition for the full writeup of each):**
1. `n04c`'s demographic claim (slowing Western growth vs. fast-growing convert baptisms in Africa/Latin America/Asia) needs the Church's own general-conference statistical report as a source — not pulled yet.
2. `n05b`'s operational-vs-investment real estate split needs a source on Property Reserve Inc./Deseret Management Corporation's holdings — not pulled yet, and note it's a different entity from Ensign Peak.
3. `n10a`'s "$300 billion" is an explicit hypothetical ceiling, not a claimed real total (see the narration itself) — but "roughly seventeen million members" needs the Church's current published membership statistic to replace the rough figure before Gate A.

**Don't approve this for Gate A as-is** — reply either "split it" (I'll create a second slug and separate `beats.yaml`/`research/` for Part 2) or tell me what to trim instead, plus whatever you want done about the three sourcing gaps above.

Edit this file with `DROP` / `SPLIT` / `MOVE AFTER Bxx` directives or plain-language notes (see docs/saint-capybara/script-format.md) and return it -- do not edit beats.yaml directly unless you're comfortable with the YAML.

## 01. `c01` (clip, ~7.0s)
- **Original Video Transcript:** What does the Mormon Church have to do with Palantir? They own over $168 million worth of Palantir stock.
- **Pose:** skeptical
- **Clip:** Source video, 0.0s–7.0s @ speed 1.0
- **Notes:** 

## 02. `n01` (narration, ~12.5s)
- **Original Video Transcript:** What does the Mormon Church have to do with Palantir? They own over $168 million worth of Palantir stock.
- **Pose:** source
- **Narration:** That figure is real: a hundred sixty eight million dollars in Palantir. But that's about a quarter of one percent of the fund's sixty billion dollar portfolio -- roughly Palantir's own weight in the S and P 500. If you hold basically any total-market index fund, you already own a slice of Palantir too.
- **Sources:** sec-13f-ensignpeak-2026q2-infotable, sp-press-palantir-addition, pltr-sp500-weight-slickcharts
- **Notes:** 

## 03. `c02` (clip, ~11.0s)
- **Original Video Transcript:** They don't have caffeine, alcohol, tobacco, and gambling companies. But there's a ton of data center related companies, crypto, oil companies, and a whole lot of weapons makers. Because missiles and church. And for some reason, TKO, which owns a WWE and UFC.
- **Pose:** thoughtful
- **Clip:** Source video, 30.0s–41.0s @ speed 1.0
- **Notes:** 

## 04. `n02` (narration, ~13.4s)
- **Original Video Transcript:** They don't have caffeine, alcohol, tobacco, and gambling companies. But there's a ton of data center related companies, crypto, oil companies, and a whole lot of weapons makers. Because missiles and church. And for some reason, TKO, which owns a WWE and UFC.
- **Pose:** source
- **Narration:** TKO is trivial: one point six million dollars, a few thousandths of one percent. Both joined the S and P 500 in the last two years, and Palantir's size is close to its own index weight -- consistent with broad exposure, though this fund does pick its own stocks.
- **Sources:** sec-13f-ensignpeak-2026q2-infotable, sp-press-tko-addition
- **Notes:** 

## 05. `n03` (narration, ~12.8s)
- **Original Video Transcript:** They don't have caffeine, alcohol, tobacco, and gambling companies. But there's a ton of data center related companies, crypto, oil companies, and a whole lot of weapons makers. Because missiles and church. And for some reason, TKO, which owns a WWE and UFC.
- **Pose:** concerned
- **Narration:** This is factually incorrect, they do own stock in alcohol, tobacco, and gambling through the Vanguard S&P 500 ETF. Yet again, normal investments.
- **Sources:** sec-13f-ensignpeak-2026q2-infotable
- **Notes:** 

## 06. `c03` (clip, ~9.0s)
- **Original Video Transcript:** That's right, the Mormon Church's investment wing has over $124 billion in assets. And half of that is in stocks like Palantir. And even though they make billions of dollars, they're still a tax exempt non-profit.
- **Pose:** listening
- **Clip:** Source video, 8.0s–17.0s @ speed 1.0
- **Notes:** 

## 07. `n04` (narration, ~14.2s)
- **Original Video Transcript:** That's right, the Mormon Church's investment wing has over $124 billion in assets. And half of that is in stocks like Palantir. And even though they make billions of dollars, they're still a tax exempt non-profit.
- **Pose:** source
- **Narration:** That number traces to a 2019 whistleblower complaint, which actually cited around a hundred billion -- not audited either way. Ensign Peak's own disclosed holdings are around sixty one billion today. But this isn't a company making profit for owners -- it's a non-profit reserve, the same category as a university endowment.
- **Sources:** nielsen-irs-complaint-ensign-peak-100b, wikipedia-ensign-peak-advisors, sec-ensign-peak-settlement-2023
- **Notes:** 

## 08. `n04b` (narration, ~13.1s)
- **Original Video Transcript:** That's right, the Mormon Church's investment wing has over $124 billion in assets. And half of that is in stocks like Palantir. And even though they make billions of dollars, they're still a tax exempt non-profit.
- **Pose:** teaching
- **Narration:** Tax-exempt status turns on one rule: no profit to private individuals, money used for the mission -- not the fund's size. In 2018, over a year before this became news, the Church was already saying the reserve exists to sustain future growth. Same purpose a college endowment serves.
- **Sources:** irs-501c3-exemption-requirements, newsroom-2018-church-finances-growing-global-faith
- **Notes:** 

## 09. `n04c` (narration, ~18.1s) — NEW
- **Original Video Transcript:** That's right, the Mormon Church's investment wing has over $124 billion in assets. And half of that is in stocks like Palantir. And even though they make billions of dollars, they're still a tax exempt non-profit.
- **Pose:** teaching
- **Narration:** And a reserve like this isn't just banked for someday -- it's aimed at a real shift already happening. Birth rates are falling in the U.S. and Europe, and membership growth there has slowed to a crawl. Meanwhile the fastest growth in convert baptisms is happening in Africa, Latin America, and parts of Asia -- places that need meetinghouses and temples built now, not decades from now.
- **Sources:** NEEDS SOURCE -- Church's own general-conference statistical report by area (not pulled yet, see note above script)
- **Notes:** 

## 10. `n04d` (narration, ~10.6s) — NEW
- **Original Video Transcript:** That's right, the Mormon Church's investment wing has over $124 billion in assets. And half of that is in stocks like Palantir. And even though they make billions of dollars, they're still a tax exempt non-profit.
- **Pose:** encouraging
- **Narration:** That's not a business chasing profit for owners. It's an institution funding its own expansion into exactly the places its own membership is actually growing -- the same long-game logic as an endowment, just applied globally.
- **Sources:** irs-501c3-exemption-requirements, newsroom-2018-church-finances-growing-global-faith
- **Notes:** 

## — SPLIT HERE — (recommended break into a second slug; Part 1 ends at ~130s)

## 11. `c04` (clip, ~6.0s)
- **Original Video Transcript:** The real estate wing property reserve has offices, apartments, they even have a parking business. This is somehow still a non-profit. Is the Mormon Church the new Blackstone BlackRock? Why do they work so hard to keep it a secret?
- **Pose:** surprised
- **Clip:** Source video, 87.0s–93.0s @ speed 1.0
- **Notes:** 

## 12. `n05` (narration, ~12.3s)
- **Original Video Transcript:** The real estate wing property reserve has offices, apartments, they even have a parking business. This is somehow still a non-profit. Is the Mormon Church the new Blackstone BlackRock? Why do they work so hard to keep it a secret?
- **Pose:** teaching
- **Narration:** It is still a non-profit -- legally, not in dispute. But calling it the next Blackstone misses the structure: Blackstone manages money for investors who want a return. Ensign Peak has no outside investors -- everything it holds already belongs to the institution it serves.
- **Sources:** wikipedia-ensign-peak-advisors, irs-501c3-exemption-requirements
- **Notes:** 

## 13. `n05b` (narration, ~16.1s) — NEW
- **Original Video Transcript:** The real estate wing property reserve has offices, apartments, they even have a parking business. This is somehow still a non-profit. Is the Mormon Church the new Blackstone BlackRock? Why do they work so hard to keep it a secret?
- **Pose:** explaining_quote
- **Narration:** Not all of that real estate is investment property, either. Meetinghouses, temples, and welfare facilities are operational property -- run at a cost to serve people, not for a return. The investment side -- commercial property, farmland, that parking business -- is a separate slice, managed by a different Church entity than the one that holds the stock portfolio.
- **Sources:** NEEDS SOURCE -- Property Reserve Inc./Deseret Management Corporation holdings breakdown (not pulled yet, see note above script)
- **Notes:** 

## 14. `n06` (narration, ~13.1s)
- **Original Video Transcript:** The real estate wing property reserve has offices, apartments, they even have a parking business. This is somehow still a non-profit. Is the Mormon Church the new Blackstone BlackRock? Why do they work so hard to keep it a secret?
- **Pose:** solemn
- **Narration:** Why would they publish it? They are not legally obligated to disclose the information, and people will use any information they can to criticize the Church. 
- **Sources:** sec-order-2023-96951
- **Notes:** 

## 15. `c05` (clip, ~9.0s)
- **Original Video Transcript:** And that's probably due to the fact that the church failed to properly fill out their 13F forms for over 22 years. 1997 to 2019, they were supposed to file just one 13F, but instead they filed as 13 different shell companies.
- **Pose:** concerned
- **Clip:** Source video, 46.0s–55.0s @ speed 1.0
- **Notes:** 

## 16. `n07` (narration, ~11.2s)
- **Original Video Transcript:** And that's probably due to the fact that the church failed to properly fill out their 13F forms for over 22 years. 1997 to 2019, they were supposed to file just one 13F, but instead they filed as 13 different shell companies.
- **Pose:** source
- **Narration:** That part is exactly right, and the SEC's order says why: leaders adopted the shell-company structure specifically to keep the fund's size from becoming public. Settled fact -- the Church accepted it by settling. I'm not going to argue that away. (remove this clip)
- **Sources:** sec-order-2023-96951, sec-2023-35-press-release
- **Notes:** 

## 17. `c06` (clip, ~9.0s)
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** disappointed
- **Clip:** Source video, 58.0s–67.0s @ speed 1.0
- **Notes:** 

## 18. `n08` (narration, ~11.5s)
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** thoughtful
- **Narration:** So why not just disclose it, like I just did? The Church's own 2023 statement says it relied on legal counsel to keep the portfolio private -- a real answer, not a good one. Wanting reserves and hiding them are different questions. (remove this line as well)
- **Sources:** sec-order-2023-96951, church-newsroom-sec-statement-2023
- **Notes:** 

## 19. `n09` (narration, ~6.3s)
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** encouraging
- **Narration:** What the clip leaves out: this ended. Since 2019, one honest report every year, and the SEC's full penalty, paid. Concealed, caught, corrected. (remove this line)
- **Sources:** church-news-2023-compliance-since-2019, sec-2023-35-press-release
- **Notes:** 

## 20. `n10a` (narration, ~10.6s) — NEW
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** teaching
- **Narration:** One more sanity check on the headline numbers: even a wildly generous estimate -- three hundred billion, well above anything actually disclosed -- divided across the Church's roughly seventeen million members comes out to about seventeen thousand dollars a person.
- **Sources:** NEEDS SOURCE -- current published membership figure (not pulled yet, see note above script; "$300 billion" is stated on screen as a hypothetical ceiling, not a claimed total, and needs no source for that reason)
- **Notes:** 

## 21. `n10b` (narration, ~11.1s) — NEW
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** encouraging
- **Narration:** And Church humanitarian aid already goes to non-members as a matter of policy, not exception. A reserve that size isn't a war chest -- it's what you'd want on hand to help everyone, member or not, if something genuinely catastrophic happened.
- **Sources:** NEEDS SOURCE -- Church humanitarian aid non-member policy (likely already sourced elsewhere in the pipeline's common-issues docs; not attached to this project yet)
- **Notes:** 

## 22. `n99` (narration, ~9.5s)
- **Original Video Transcript:** They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies. When in reality, by 2018, they already had $32 billion. Because they thought if people really knew how much money they had, there'd be a negative reaction.
- **Pose:** encouraging
- **Narration:** So: not a hedge fund and not Blackstone. A non-profit reserve, honestly justified. God bless.
- **Notes:** 

## Full source transcript

Every line of the source video, timestamped, for checking each response beat above against the full context -- not just the clip spans quoted from it.

- `[00:00.00–00:02.64]` What does the Mormon Church have to do with Palantir?
- `[00:02.78–00:07.02]` They own over $168 million worth of Palantir stock.
- `[00:07.22–00:12.20]` That's right, the Mormon Church's investment wing has over $124 billion in assets.
- `[00:12.40–00:15.12]` And half of that is in stocks like Palantir.
- `[00:15.30–00:19.02]` And even though they make billions of dollars, they're still a tax exempt non-profit.
- `[00:19.26–00:21.88]` Their portfolio has over 1,700 different stocks in it.
- `[00:21.94–00:24.92]` The top 25 stocks equal about 50% of the fun.
- `[00:25.12–00:25.78]` $30 billion.
- `[00:26.40–00:27.30]` The portfolio is interesting.
- `[00:27.30–00:30.14]` They don't have caffeine, alcohol, tobacco, and gambling companies.
- `[00:30.30–00:35.64]` But there's a ton of data center related companies, crypto, oil companies, and a whole lot of weapons makers.
- `[00:35.88–00:37.42]` Because missiles and church.
- `[00:37.74–00:40.78]` And for some reason, TKO, which owns a WWE and UFC.
- `[00:41.08–00:44.60]` What's also interesting is most of my childhood Mormon friends didn't even know this fund existed.
- `[00:44.76–00:50.60]` And that's probably due to the fact that the church failed to properly fill out their 13F forms for over 22 years.
- `[00:50.84–00:56.98]` 1997 to 2019, they were supposed to file just one 13F, but instead they filed as 13 different shell companies.
- `[00:56.98–01:00.92]` They tried to hide the fact that they had a lot of money, so they split it up into 13 different companies.
- `[01:01.04–01:04.26]` When in reality, by 2018, they already had $32 billion.
- `[01:04.92–01:08.54]` Because they thought if people really knew how much money they had, there'd be a negative reaction.
- `[01:08.82–01:10.08]` I can't imagine why.
- `[01:10.38–01:14.54]` And Boomba just came out with a report on the Mormon Church's massive expansion of their real estate portfolio.
- `[01:14.88–01:20.08]` They currently own over 2.4 million acres across the US worth $20 billion, and that's just what we know.
- `[01:20.22–01:23.20]` And they're currently working on over 40,000 homes.
- `[01:23.20–01:27.34]` The real estate wing property reserve has offices, apartments, they even have a parking business.
- `[01:27.34–01:28.96]` This is somehow still a non-profit.
- `[01:29.14–01:31.64]` Is the Mormon Church the new Blackstone BlackRock?
- `[01:31.84–01:33.30]` Why do they work so hard to keep it a secret?
- `[01:33.48–01:35.20]` Let me know what you guys think and make sure you follow me for more.
