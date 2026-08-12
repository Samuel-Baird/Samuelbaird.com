import type { ReactNode } from "react";
import type { TagInk } from "@/components/tag";
import type { Face } from "./cameo";

/**
 * The ten most-cited speakers in this timeline's sources (plus Joseph Smith),
 * profiled from the timeline's graded quotes and from each speaker's published
 * books via the Gospel Scholar Archive. Citation counts are computed from
 * sources.json at render time, not stored here, so they stay honest as the
 * dataset grows.
 *
 * The `deseret` strings are hand-verified phonemic transliterations
 * (codepoint-checked against the 1859 chart), unlike the decorative
 * per-letter mapping in src/lib/deseret.ts. They are always paired with the
 * Latin name wherever they render.
 */

export type Stance = {
  /** Chip answer, a few words. */
  answer: string;
  /** Which Tag ink family the answer belongs to. */
  ink: TagInk;
};

export type Speaker = {
  id: string;
  name: string;
  deseret: string;
  dates: string;
  role: string;
  era: string;
  frame: "gilt" | "walnut";
  face: Face;
  stances: { father: Stance; man: Stance; increase: Stance };
  summary: string;
  beliefs: string[];
  quotes: { text: string; source: string; url: string }[];
  books: ReactNode;
  fun: string;
};

function Src({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-[color:var(--accent)] underline underline-offset-2 hover:no-underline"
    >
      {children}
    </a>
  );
}

export const SPEAKERS: Speaker[] = [
  {
    id: "joseph-smith",
    name: "Joseph Smith",
    deseret: "𐐖𐐬𐑆𐐲𐑁 𐐝𐑋𐐮𐑃",
    dates: "1805–1844",
    role: "Founding prophet & first President",
    era: "The founding vision",
    frame: "gilt",
    face: { hair: "sweep", hairColor: "brown", beard: "none", collar: "cravat" },
    stances: {
      father: { answer: "Yes — by 1844", ink: "honey" },
      man: { answer: "Yes — King Follett", ink: "honey" },
      increase: { answer: "Yes, mechanism unsaid", ink: "ink" },
    },
    summary:
      "Started with an unchanging God and ended, in the last ten weeks of his life, teaching that God was once a man and that the Father himself had a Father — a conclusion he reached by Bible exegesis, not reported vision. He promised the exalted “a continuation of the seeds forever,” yet taught that intelligence is uncreated and cannot be made: organization, not begetting. The literal spirit-birth chain his successors preached was their link, not his.",
    beliefs: [
      "His teaching on the divine past moved a very long way in fourteen years. The 1830 Book of Moses presents a single divine speaker who creates “worlds without number” — plurality of worlds, but one originator standing outside the series, with “no end to my works.” The circa-1834 Lectures on Faith goes further in the classical direction: faith itself is said to require a God whose attributes “are unchangeable, being the same yesterday, to-day, and forever… for God never changes.” Nothing in the early corpus hints that God has a history.",
      "The turn comes in Nauvoo. A 30 January 1842 discourse (hearsay grade C — the scribe was away and likely worked from someone else’s notes) already has the whole engine: the Father “was once the same as the Son… but having redeemed a world became the eternal God of that world,” and so on for the Holy Ghost and all the Saints — “Gods many & Lords many.” The same year, the Book of Abraham introduced eternal, uncreated intelligences and plural organizing Gods, and the July 1843 marriage revelation promised the exalted “a continuation of the seeds forever and ever.”",
      "The two famous 1844 sermons then split the claim into its halves. The King Follett Discourse (7 April 1844, a funeral sermon at general conference, hearsay B — four longhand witnesses, no verbatim text) establishes the Father’s mortality: “Going to tell you how God came to be God. We have imagined that God was God from all eternity…” — refuted, on Smith’s telling, by the fact that the Father once dwelt on an earth as Jesus did. The backward step — that the Father himself had a Father — arrives ten weeks later, in the Sermon in the Grove (16 June 1844), and it arrives as exegesis of Revelation 1:6, not as vision: “where was there ever a Son without a Father?” He was dead within two weeks of preaching it.",
      "Two internal tensions matter. First, the familiar chain proof-text “the same as all Gods have done before you” rests on a single witness (Clayton); Bullock has the weaker “same as all have done,” and Richards and Woodruff have no comparison clause at all. Second, Smith simultaneously taught that “the mind of man… is coequal with God himself” and that “God never did have power to create the spirit of man at all” — organization of eternal intelligences, not begetting. The viviparous spirit-birth doctrine that Young and Pratt later built on his foundation is not actually in his recorded words; that link was supplied by his successors.",
    ],
    quotes: [
      {
        text: "God himself was once as one of us and was on a planet as Jesus was in the flesh.",
        source: "King Follett Discourse, 7 Apr 1844 (hearsay B — four longhand witnesses)",
        url: "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-thomas-bullock/3",
      },
      {
        text: "If John discovered that God the Father of Jesus Christ had a Father, you may suppose that he had a Father also — where was there ever a Son without a Father?",
        source: "Sermon in the Grove, 16 Jun 1844",
        url: "https://www.josephsmithpapers.org/paper-summary/discourse-16-june-1844-a-as-reported-by-thomas-bullock/3",
      },
      {
        text: "The God & father of our Lord Jesus Christ was once the same as the Son… having redeemed a world became the eternal God of that world… so there would be Gods many & Lords many.",
        source: "Discourse, 30 Jan 1842 (hearsay C)",
        url: "https://www.josephsmithpapers.org/paper-summary/discourse-30-january-1842/2",
      },
      {
        text: "God never did have power to create the spirit of man at all. He could not create himself — Intelligence exists upon a self-existent principle.",
        source: "King Follett Discourse, 7 Apr 1844",
        url: "https://www.josephsmithpapers.org/paper-summary/discourse-7-april-1844-as-reported-by-thomas-bullock/3",
      },
    ],
    books: (
      <>
        The archive confirms both poles of the trajectory:{" "}
        <Src href="https://corpus.noahairmet.com/b/lectures-on-faith-ce7e/50">Lectures on Faith</Src>{" "}
        (Lecture 4) teaching that God’s attributes “remain forever the same” — the static register the
        Nauvoo sermons would overturn — and the amalgamated King Follett text (“is an exalted man”)
        quoted everywhere from{" "}
        <Src href="https://corpus.noahairmet.com/b/roberts-mormon-doctrine-of-deity-d496/22">
          B. H. Roberts’s Mormon Doctrine of Deity
        </Src>{" "}
        to Talmage and both editions of{" "}
        <Src href="https://corpus.noahairmet.com/b/mcconkie-mormon-doctrine-2nd-edition-9c13/413">
          Mormon Doctrine
        </Src>{" "}
        — showing how thoroughly the amalgam, not the four witnesses, became the canonical text.
      </>
    ),
    fun: "The most-quoted sentence he ever “said” — “God himself was once as we are now, and is an exalted man” — appears in none of the four surviving eyewitness reports. It is an 1850s editorial amalgam (later canonized by Teachings of the Prophet Joseph Smith and a 1971 Ensign), stitched together from notes taken in longhand at an outdoor funeral sermon preached to thousands.",
  },
  {
    id: "brigham-young",
    name: "Brigham Young",
    deseret: "𐐒𐑉𐐮𐑀𐐲𐑋 𐐏𐐲𐑍",
    dates: "1801–1877",
    role: "2nd President, 1847–1877",
    era: "The Basin kingdom",
    frame: "gilt",
    face: { hair: "receding", hairColor: "auburn", beard: "chincurtain", beardColor: "gray", collar: "cravat" },
    stances: {
      father: { answer: "Yes — “no beginning”", ink: "honey" },
      man: { answer: "Yes — still progressing", ink: "honey" },
      increase: { answer: "Yes — literal birth", ink: "honey" },
    },
    summary:
      "Preached the boldest chain-of-Gods doctrine any Church President has delivered — Gods without beginning, spirits literally begotten and born in the celestial world, a God who “is progressing eternally” — but his sharpest regress statements sit inside the Adam–God frame, and the day after his cleanest chain statement he told the Saints to stop inquiring after the origin of the Gods. Nearly all of it survives only as unreviewed shorthand.",
    beliefs: [
      "Young preached the endless-progression theme from the first general conference he ever presided over (April 1845, ten months after the King Follett Discourse): a man keeps receiving “until he obtains to the fulness of the Godhead,” and even after “millions of worlds, it is eternity still before them” (hearsay C — a scribe’s abbreviated summary, not his sentences). Over thirty years he built Joseph Smith’s late Nauvoo hints into the most explicit chain-of-Gods teaching any Church President has delivered.",
      "His backward statements come with a complication the quotes rarely carry: the Adam–God frame. In his first public Adam–God discourse (9 April 1852) he identified Adam as “our Father and our God, and the only God with whom we have to do,” then said that Father “was begotten by his Father in heaven… and so on in succession.” The famous 1854 grandfather argument — “Could you have a father without having a grandfather?” — belongs to the same project, a sermon delivered in part as a rebuttal of Orson Pratt. Citing the grandfather sentence as a freestanding regress proof-text, without that frame, is the single most common handling error attached to it.",
      "His cleanest chain statement is 8 October 1859: “there never was a time when there were not Gods and worlds, and when men were not passing through the same ordeals that we are now passing through.” Yet the very next day he preached the earliest official discouragement of the question: “Instead of inquiring after the origin of the Gods… let them seek to know the object of their present existence.” The most explicit chain language and the earliest caution against it came from the same pulpit on consecutive days.",
      "On the forward side he is equally explicit and equally physiological: “Our Father in Heaven begat all the spirits that ever were” (1852), and in 1876, from the conference stand, spirits “were begotten, born and educated in the celestial world, and were brought forth by celestial bodies” — gestation and parturition offered as his own gloss on scripture. He rejected adoption (“we are his children by a legal inheritance”) and taught that exaltation “by no means lessens” the power to propagate.",
      "His dispute with Orson Pratt gives the tradition its sharpest internal fault line. Pratt held that Gods, having all knowledge, cannot progress; Young answered by name in 1867: “Brother Orson Pratt has in theory bounded the capacity of God… but the God that I serve is progressing eternally, and so are his children.” Caveat over everything: nearly all of this is Journal of Discourses material — contemporaneous shorthand edited for publication, never reviewed by Young — graded C throughout the timeline. Evidence of the claims, not of his sentence construction.",
    ],
    quotes: [
      {
        text: "There never was a time when there were not Gods and worlds, and when men were not passing through the same ordeals that we are now passing through.",
        source: "Tabernacle, 8 Oct 1859 (JoD 7:333)",
        url: "https://www.churchofjesuschrist.org/study/manual/teachings-brigham-young/chapter-4",
      },
      {
        text: "Could you have a father without having a grandfather; or a grandfather without having a great grandfather?",
        source: "General conference, 8 Oct 1854 — inside his most explicit Adam–God sermon",
        url: "https://corpus.noahairmet.com/b/2-1853-1856-d4c5/255",
      },
      {
        text: "Spirits were begotten, born and educated in the celestial world, and were brought forth by celestial bodies.",
        source: "General conference, 8 Oct 1876 (JoD 18:257–264)",
        url: "https://contentdm.lib.byu.edu/digital/collection/JournalOfDiscourses3/id/6884",
      },
      {
        text: "Brother Orson Pratt has in theory bounded the capacity of God… but the God that I serve is progressing eternally, and so are his children.",
        source: "Tabernacle, 13 Jan 1867 (JoD 11:286)",
        url: "https://contentdm.lib.byu.edu/digital/collection/JournalOfDiscourses3/id/4477",
      },
    ],
    books: (
      <>
        Young published no books; his canon is the Journal of Discourses and Widtsoe’s 1925
        compilation, which kept the 1859 chain statement verbatim (
        <Src href="https://corpus.noahairmet.com/b/widtsoe-discourses-of-brigham-young-c328/52">
          Discourses of Brigham Young, p. 52
        </Src>
        ) — while the 1852 Adam–God identification survives only in histories and studies like Givens’{" "}
        <Src href="https://corpus.noahairmet.com/b/givens-wrestling-the-angel-foundations-of-88a3/153">
          Wrestling the Angel
        </Src>
        , Arrington’s{" "}
        <Src href="https://corpus.noahairmet.com/b/arrington-brigham-young-american-moses-669e/290">
          American Moses
        </Src>
        , and Bergera’s{" "}
        <Src href="https://corpus.noahairmet.com/b/bergera-conflict-in-the-quorum-orson-pratt-a8b2/213">
          Conflict in the Quorum
        </Src>
        , which documents the 1860 proceedings against Pratt in which Young’s side condemned the idea
        that God cannot progress.
      </>
    ),
    fun: "Wilford Woodruff called the October 1854 “grandfather” sermon — Young’s most explicit Adam–God statement, aimed squarely at Orson Pratt — “the greatest sermon that ever was Delivered to the Latter Day Saints since they have been a People.” A hundred and twenty-two years later, Spencer W. Kimball repudiated its central doctrine from the same conference pulpit.",
  },
  {
    id: "orson-pratt",
    name: "Orson Pratt",
    deseret: "𐐃𐑉𐑅𐐲𐑌 𐐑𐑉𐐰𐐻",
    dates: "1811–1881",
    role: "Apostle & chief systematizer",
    era: "The Basin kingdom",
    frame: "walnut",
    face: { hair: "fringe", hairColor: "gray", beard: "full", beardColor: "gray", collar: "suit", coat: "#2f2a24", browHeavy: true },
    stances: {
      father: { answer: "Persons yes — God no", ink: "oxblood" },
      man: { answer: "Yes (the person)", ink: "honey" },
      increase: { answer: "Yes — maximal", ink: "honey" },
    },
    summary:
      "Split God in two: divine persons regress forever — “The Father of our spirits has only been doing that which His Progenitors did before Him” — but the true eternal God is the attribute-set of light, truth, and knowledge, which never began and, crucially, never learns. He is the corpus’s most explicit voice on the forward chain, and the metaphysics behind his backward one got him censured in 1860 and formally repudiated in 1865.",
    beliefs: [
      "Pratt was the movement’s system-builder, and his system runs on a distinction nobody else drew: persons versus attributes. In The Seer (1853–54) and the pamphlet Great First Cause (1851) he taught that the ultimate eternal reality is not any divine person but the self-existent attributes — light, truth, knowledge — diffused through eternal particles of intelligent substance, which he called “the Great First Causes of all things.” Divine persons, including the Father, are organized results of that substance.",
      "So Pratt could affirm a genealogy of persons — “The Father of our spirits has only been doing that which His Progenitors did before Him” — while holding that “God,” properly speaking, names one attribute-set numerically identical wherever it dwells: “the tabernacles are many… but when reference is made to the temples in which this knowledge dwells, the number of Gods is infinite” (1855). His infinity of Gods is a simultaneous multiplicity, not a backward chain — the essential control case against reading every 1850s “many Gods” passage as regress evidence. Notably, he always runs the chain forward from the pulpit; the regress lives in his written works.",
      "Forward, he is the most explicit voice in the entire corpus. His 1852 “Celestial Marriage” discourse — the first public defense of plural marriage — argues by analogy that spirits are “formed by generation,” and that restored couples “will continue to increase and multiply to all ages of eternity,” their offspring “destined… to become not only sons of God, but Gods themselves,” with infinite worlds deduced arithmetically as housing for infinite posterity. By 1871 the full loop fits in one sentence: beget children, form worlds, send forth spirit children, “the same as we were sent here.”",
      "The consequence of his metaphysics was the fight of his life. If God just is the complete attribute-set of knowledge, there is nothing left for God to learn — so Pratt wrote that the Father and Son “do not progress in knowledge… because they already know all things.” Brigham Young took this as bounding God. In January 1860 Pratt was pressed to recant before the Twelve, and that summer the First Presidency published a detailed condemnation quoting The Seer and Great First Cause. In 1865 the First Presidency and Twelve formally repudiated both works wholesale — the first official doctrinal retraction in the timeline’s dataset. Pratt submitted, kept his apostleship, and kept teaching the forward doctrine.",
      "Hearsay caveat, inverted: his sermons are Journal of Discourses shorthand (grade C), but his distinctive positions are A-grade — The Seer and the pamphlets are his own pen. That is precisely why they, unlike Young’s spoken Adam–God teaching, could be and were formally repudiated.",
    ],
    quotes: [
      {
        text: "The Father of our spirits has only been doing that which His Progenitors did before Him.",
        source: "The Seer §113, p. 184 (1853–54, his own pen)",
        url: "https://archive.org/details/TheSeer18531854",
      },
      {
        text: "The tabernacles are many and without number… but when reference is made to the temples in which this knowledge dwells, the number of Gods is infinite.",
        source: "Temple Block discourse, 18 Feb 1855 (JoD 2:345)",
        url: "https://archive.org/details/per_utah-and-the-mormons_journal-of-discourses-_brigham-young-_1855_2/page/n341",
      },
      {
        text: "They will continue to increase and multiply to all ages of eternity… destined… to become not only sons of God, but Gods themselves.",
        source: "“Celestial Marriage,” 29 Aug 1852 (JoD 1:53–66)",
        url: "https://contentdm.lib.byu.edu/digital/collection/JournalOfDiscourses3/id/1858",
      },
      {
        text: "So will we rise immortal… and beget children, and, in our turn, form and create worlds, and send forth our spirit children… the same as we were sent here.",
        source: "New Tabernacle, 20 Aug 1871 (JoD 14:241)",
        url: "https://contentdm.lib.byu.edu/digital/collection/JournalOfDiscourses3/id/5294",
      },
    ],
    books: (
      <>
        The archive carries the primary artifacts of his censure: Bergera’s{" "}
        <Src href="https://corpus.noahairmet.com/b/bergera-conflict-in-the-quorum-orson-pratt-a8b2/213">
          Conflict in the Quorum
        </Src>{" "}
        reproduces the 1860 First Presidency answer verbatim, quoting The Seer (“The Father and the Son
        do not progress in knowledge and wisdom, because they already know all things”) and Great First
        Cause before rejecting both with Joseph Smith’s quip: “It is not true.” McMurrin’s{" "}
        <Src href="https://corpus.noahairmet.com/b/mcmurrin-the-theological-foundations-of-the-07d2/63">
          Theological Foundations
        </Src>{" "}
        treats Great First Cause as serious philosophy, and The Seer’s “Progenitors” sentence circulates
        even in devotional works like Brown’s{" "}
        <Src href="https://corpus.noahairmet.com/b/brown-the-gate-of-heaven-insights-on-the-fd66/15">
          The Gate of Heaven
        </Src>
        .
      </>
    ),
    fun: "The theology war doubled as a book-debt war. Censuring Pratt in 1860, Young also blamed him for the British Mission’s crushing “Book debt” and ordered: “Now stop publishing & getting your portraits taken & fill[ing] the kingdom with them.” Pratt protested he had used his own means; Young shot back, “It all come out of the poor Saints, just as much as tho he had begged it.”",
  },
  {
    id: "george-q-cannon",
    name: "George Q. Cannon",
    deseret: "𐐖𐐫𐑉𐐾 𐐗𐐰𐑌𐐲𐑌",
    dates: "1827–1901",
    role: "First Counselor to three Presidents",
    era: "The Basin kingdom",
    frame: "gilt",
    face: { hair: "fringe", hairColor: "white", beard: "full", beardColor: "white", mustache: true, collar: "suit", coat: "#3a332b" },
    stances: {
      father: { answer: "One link, then silence", ink: "muted" },
      man: { answer: "Leaning yes, hedged", ink: "ink" },
      increase: { answer: "Emphatic yes", ink: "honey" },
    },
    summary:
      "The great theologian of the forward direction: God’s glory is the size of his posterity, procreation survives death and peoples the worlds, and exalted Abraham will have to “emigrate” for want of room. Backward, he extends the chain exactly one link past the Son — “Jesus received it as the Father received it” — asks whether other Gods were born of woman, and never names a Father of the Father.",
    beliefs: [
      "Cannon preached eternal increase across thirty years (1869–1899) not as a reward attached to godhood but as its very substance: “the glory of God consists in the number of his posterity” (1871), and a newborn infant “may become, in the eternity of our God, a God… the father of unnumbered millions” (1884). He named the mechanism with a bluntness almost no one matched — the power of procreation, “the greatest power that man possesses on the earth,” promised to the faithful in the resurrection, the same principle “by which the worlds are peopled” (April 1899, printed Conference Report, hearsay A). He anticipated the charge of materialism from the pulpit and embraced it: “I want to be materialistic in this sense.”",
      "He also worked out the arithmetic. Generations fill the earth, so “other worlds will be rolled into existence” for the overflow (1871); exalted man will form worlds for his posterity — “that very same thing” the Father did for us — and Abraham “will want to emigrate after awhile from this earth” because there will not be room for his innumerable posterity (1892). The comparative clause is never run backwards: Cannon says the stars are God’s creations peopled by God’s children, and says nothing about God’s own ancestry.",
      "On the backward questions he hedged where he was explicit going forward. His April 1889 sermon packs the Snow couplet (“the true theory of evolution”), literal divine descent (“I do not mean in a spiritual sense”), a Heavenly Mother assumed without argument, and the born-of-woman generalization — “if one God was born of woman, may not others be also? To say they could not is not logical” — into a single page, none of it argued at length, with the “others” left ambiguous as to whether it reaches the Father. His strongest attainment claim came in his last conference (April 1899): the Saints shall receive the fulness “as Jesus received it: and Jesus received it as the Father received it” — the Father placed inside the grace-for-grace chain, with no word on from whom.",
      "He is also the corpus’s earliest boundary-drawer. In his May 1895 Juvenile Instructor editorial “The Worship of Female Deities” (hearsay A, his own pen) he condemned deifying “our mother in heaven” as approaching “rank idolatry” — while calling her “our mother,” unhedged, in the same breath. The sanction fell on worship and Godhead membership, never on her existence or on the generative doctrine, which he preached without hedge four years later.",
      "Hearsay caveats: most Cannon sermon material is grade C — contemporaneous shorthand or newspaper reports he never reviewed, including both the 1889 and 1892 Deseret Weekly discourses. The April 1899 statements and the 1895 editorial are grade A.",
    ],
    quotes: [
      {
        text: "His glory consisted of this; and the glory of God consists in the number of his posterity… other worlds will be rolled into existence.",
        source: "Salt Lake City discourse, 8 Apr 1871 (JoD 14:122–129)",
        url: "https://archive.org/details/per_utah-and-the-mormons_journal-of-discourses-_brigham-young-_1872_14/page/n129",
      },
      {
        text: "That little puling infant may become, in the eternity of our God, a God, to sway power and dominion in the eternal worlds, to be the father of unnumbered millions.",
        source: "General conference, 5 Oct 1884 (JoD 25:325)",
        url: "https://archive.org/details/per_utah-and-the-mormons_journal-of-discourses-_brigham-young-_1885_25/page/n327",
      },
      {
        text: "He was born of a woman. And if one God was born of woman, may not others be also? To say they could not is not logical.",
        source: "General conference, 7 Apr 1889 (Deseret Weekly, hearsay C)",
        url: "https://newspapers.lib.utah.edu/details?id=23178000",
      },
      {
        text: "The power of procreation is promised — the greatest power that man possesses on the earth… By it, and through that principle the worlds are peopled.",
        source: "Conference Report, 6 Apr 1899, p. 20 (hearsay A)",
        url: "https://archive.org/details/conferencereport1899a/page/n18",
      },
    ],
    books: (
      <>
        His compiled discourses circulate as Gospel Truth, a standard reference across the archive.
        Dialogue reprints his 1895 conclusion that putting “the feminine element… as part of the
        Godhead” on the word of God “is false and erroneous” (
        <Src href="https://corpus.noahairmet.com/b/v51n02-051d/35">Dialogue 51.2</Src>); Kline’s Element
        study notes his eternal plural marriage allowed for multiple Mothers in Heaven (
        <Src href="https://corpus.noahairmet.com/b/volume-5-issue-2-fall-2009-0f18/58">Element 5.2</Src>);
        and Buerger records Cannon privately reflecting, after Young’s death, that some brethren felt
        Young “transcended the bounds of the authority which he legitimately held” in promulgating
        doctrine (<Src href="https://corpus.noahairmet.com/b/v15n01-31f8/36">Dialogue 15.1</Src>).
      </>
    ),
    fun: "The hymn he shot down in his famous 1895 “rank idolatry” editorial — “Our Mother in Heaven” — had been published a year earlier in the Juvenile Instructor, the very magazine Cannon himself edited. He was, in effect, correcting himself in his own magazine, signed “The Editor.”",
  },
  {
    id: "charles-w-penrose",
    name: "Charles W. Penrose",
    deseret: "𐐕𐐪𐑉𐑊𐑆 𐐑𐐯𐑌𐑉𐐬𐑆",
    dates: "1832–1925",
    role: "First Presidency counselor, 1911–1925",
    era: "Defining the doctrine",
    frame: "walnut",
    face: { hair: "fringe", hairColor: "white", beard: "long", beardColor: "white", mustache: true, collar: "suit", coat: "#262624" },
    stances: {
      father: { answer: "No chain needed", ink: "oxblood" },
      man: { answer: "Yes — his plainest", ink: "honey" },
      increase: { answer: "Yes — “perpetual”", ink: "honey" },
    },
    summary:
      "Backward mortality without regress: the Father was once mortal and “fought his way from the depths… by His own exertions,” but eternality sits in an impersonal, beginningless spirit of intelligence, so no divine ancestry is ever asserted in either direction. On increase he is unhedged — resurrected couples are “parents of children… endless, perpetual increase” — and he spent his last decades demolishing Adam–God without ever naming Brigham Young.",
    beliefs: [
      "Penrose is the corpus’s clearest case of backward-mortality-without-regress. His 1884 Tabernacle discourse “The Personality of God” (delivered while he was merely a newspaper editor) stages the objection itself — if God is an organized being, “there must have been a time when that being was organized” — and answers it not with a chain of ancestors but with an impersonal solvent: the “eternal, beginningless, endless spirit of intelligence” that pervades all things never had a beginning, while the personages who embody it come and go. God “has fought his way from the depths up to the position He now occupies… won that position by His own exertions.” That is godhood by self-conquest, structurally Orson Pratt’s abstract Great God rather than Brigham Young’s genealogy, and in ten pages he asserts no divine parentage anywhere.",
      "He held the mortal-Father claim all his life and stated it most flatly from the First Presidency in April 1916: the Father “was an exalted man who had passed through all things that Jesus Christ, His Beloved Son, afterwards passed through. It was a repetition of the things that had been done from remote, eternal ages” — a repeated plan of salvation, which comes as near an infinite regress as he ever gets and deliberately stops short: a recurring plan, not a line of Gods begetting one another. The same 1916 address is mostly devoted to demolishing Adam–God, blamed on “letters” and a stubborn Scotchman, never on Brigham Young by name. By 1921 he hedged even the exalted-man claim: “We do not say that God is a man; he is a perfected man.”",
      "On increase he is the great definer — and re-definer. He glossed “eternal lives” three times across twenty years: “endless increase in power, dominion and glory forever” (1901), “which means endless increase” (1914), and its only posterity-naming version, “perpetual increase of posterity, worlds without end” (1921) — one speaker glossing the same scriptural phrase for two decades without ever fixing its content. His most explicit statement is October 1911: resurrected husband and wife “come forth… to be parents of children, to have the gift of endless, perpetual increase.” Post-Manifesto, official, and unhedged — standing evidence that the early twentieth century softened the vocabulary of deification, not the doctrine of increase.",
      "On spirit origins he oscillates without ever reconciling. In 1915: Christ was “begotten of the Father, and therefore the attributes of the Father came to Him by generation, and so to us.” In April 1921: “He begat us in our original being… verily and literally and truly.” Yet six months later, in his last recorded address, the elements of our spirits “have no beginning” and what we received was an “organized spiritual existence” — begetting and organization side by side, nothing retracted. Hearsay: the 1884 discourse is grade C; everything from 1901 onward is grade A printed Conference Reports.",
    ],
    quotes: [
      {
        text: "He has fought his way from the depths up to the position He now occupies… He has won that position by His own exertions.",
        source: "“The Personality of God,” Tabernacle, 16 Nov 1884 (JoD 26:23)",
        url: "https://corpus.noahairmet.com/b/volume-26-5299/23",
      },
      {
        text: "In the resurrection they shall come forth to be husband and wife, to be parents of children, to have the gift of endless, perpetual increase.",
        source: "Conference Report, 7 Oct 1911 (hearsay A)",
        url: "https://archive.org/details/conferencereport1911sa/page/n48",
      },
      {
        text: "He was an exalted man who had passed through all things that Jesus Christ, His Beloved Son, afterwards passed through.",
        source: "Conference Report, 6 Apr 1916, as First Presidency counselor",
        url: "https://archive.org/details/conferencereport1916a/page/n11",
      },
      {
        text: "We do not say that God is a man; he is a perfected man… He begat us in our original being, as his sons and daughters, verily and literally and truly.",
        source: "Conference Report, 3 Apr 1921",
        url: "https://archive.org/details/conferencereport1921a/page/n10",
      },
    ],
    books: (
      <>
        His two famous popular works — “Mormon” Doctrine, Plain and Simple (1882) and the twelve Rays
        of Living Light tracts — were among the Church’s basic proselyting pamphlets into the twentieth
        century (
        <Src href="https://corpus.noahairmet.com/b/alexander-mormonism-in-transition-a-history-of-41a5/251">
          Alexander, Mormonism in Transition
        </Src>
        ). Widtsoe quotes{" "}
        <Src href="https://corpus.noahairmet.com/b/widtsoe-joseph-smith-as-scientist-bf3d/25">
          Rays of Living Light No. 2
        </Src>{" "}
        as an authority on the divine nature — an embodied personal God whose omnipresence sits in an
        impersonal Spirit, the 1884 move packaged for missionaries — and Buerger singles out Plain and
        Simple as an influential book containing no hint of Adam–God (
        <Src href="https://corpus.noahairmet.com/b/v15n01-31f8/37">Dialogue 15.1</Src>). Nothing in the
        archive suggests his books press a divine ancestry: the perfected-man God, without a genealogy.
      </>
    ),
    fun: "The fullest statement of generative exaltation in the April 1901 conference came from a man holding no Church office at all — a 69-year-old newspaper editor speaking as an ordinary elder. He became an apostle at 72, entered the First Presidency at 79, served until his death at 93 — and wrote the hymns “O Ye Mountains High” and “School Thy Feelings.”",
  },
  {
    id: "orson-f-whitney",
    name: "Orson F. Whitney",
    deseret: "𐐃𐑉𐑅𐐲𐑌 𐐎𐐮𐐻𐑌𐐨",
    dates: "1855–1931",
    role: "Apostle, 1906–1931; poet of the Twelve",
    era: "Defining the doctrine",
    frame: "gilt",
    face: { hair: "parted", hairColor: "darkbrown", mustache: true, glasses: "pince", collar: "suit", coat: "#3b3430" },
    stances: {
      father: { answer: "Unsaid — edge pressed", ink: "muted" },
      man: { answer: "Yes — Mother too", ink: "honey" },
      increase: { answer: "Yes, formulaic", ink: "ink" },
    },
    summary:
      "Pressed the boundary harder than any peer without ever asserting a Father of the Father: God “found himself” among pre-existing, uncreatable intelligences; our eternal Father and Mother “were once man and woman in mortality” (said at a suffrage rally, in print, by name); and his 5,700-line epic Elias set “the chain whereby the Gods perpetuate their reign” in heroic verse.",
    beliefs: [
      "Whitney’s distinctive move is the symmetry inference, stated outright rather than left implicit. In May 1895, speaking at a Tabernacle woman-suffrage meeting, he began from the forward claim (we may become like our heavenly Parents), treated it as established, and ran it backwards as an entailment: “if this be true, it teaches that there was a time when… our eternal Father and Mother were once man and woman in mortality.” It is the rarest datum in the Heavenly Mother corpus — her past mortality asserted in print, by name, on the same terms as the Father. Caveat: the venue was the Woman’s Exponent (independently produced, never-official), an unsigned report of remarks a month old. When the same man, as an apostle in general conference (1907, 1920, 1928), made the Heavenly Mother argument again, he kept her and dropped the mortality half entirely.",
      "He is the Twelve’s most persistent Heavenly Mother apologist across four decades — from Genesis 1:27 exegesis (“This is equivalent to saying… we have a Mother as well as a Father in heaven,” 1920) to “the gospel of common sense” (“what more reasonable than the conclusion…?”, 1928) — always reached by reason and scriptural inference rather than revelation, never through Eliza Snow’s hymn.",
      "On God’s own past, his signature text is Joseph Smith’s condensed saying, which he put at the center of a 1908 conference address: “In the beginning, God, finding Himself in the midst of spirits and glory, because He was more intelligent, saw proper to institute laws whereby the rest might advance like Himself.” He returned to the “found himself” framing in his own voice in 1925 and 1927: the lesser intelligences are already there when the Great Creator arrives, and only afterwards “became his sons and daughters, first in the spirit and afterwards in the flesh” — a three-tier staging (intelligence → spirit child → mortal) whose transition verb is always “became,” never “begotten,” making him the era’s most explicit conference-pulpit denier of creation ex nihilo for intelligences. Yet the same 1928 address that says “spirit is uncreatable” also affirms literal divine parenthood, unharmonised — a tension he never noticed aloud.",
      "On increase he is more restrained than Cannon or Penrose: “endless increase” appears as a settled formula conferred by embodiment (“souls, capable of endless increase and everlasting progression”), with what increases never named from the pulpit. His book Gospel Themes (1914) goes a step further than his sermons: rebirth “in the similitude of those other begettings and births” is the condition of regaining “our eternal Father and Mother.” He also enumerated, with all reverence, things even God cannot do — make something from nothing; be personally omnipresent — divine limitation preached six months before Joseph F. Smith blasted “learned fools” for limiting God.",
    ],
    quotes: [
      {
        text: "If this be true, it teaches that there was a time when… our eternal Father and Mother were once man and woman in mortality.",
        source: "Tabernacle remarks, 12 May 1895 (Woman’s Exponent 24:2)",
        url: "https://archive.org/details/exponent1895/page/n40",
      },
      {
        text: "In the beginning, God, finding Himself in the midst of spirits and glory, because He was more intelligent, saw proper to institute laws whereby the rest might advance like Himself.",
        source: "Quoting Joseph Smith — Conference Report, 5 Apr 1908",
        url: "https://archive.org/details/conferencereport1908a/page/n86",
      },
      {
        text: "The all-creating, all-controlling chain / Whereby the Gods perpetuate their reign / Whereby the higher, bending, lift the lower.",
        source: "Elias: An Epic of the Ages (1904), 68–69",
        url: "https://corpus.noahairmet.com/b/v44n01-2132/48",
      },
      {
        text: "What more reasonable than the conclusion that we have a Mother as well as a Father in Heaven, in whose likeness we are, male and female?",
        source: "Conference Report, 6 Oct 1928",
        url: "https://archive.org/details/conferencereport1928sa/page/n60",
      },
    ],
    books: (
      <>
        All three major works surface in the archive: Samuel Brown reads Elias’s chain passage as
        Joseph Smith’s graded, familial cosmos of plural Gods set in heroic verse (
        <Src href="https://corpus.noahairmet.com/b/v44n01-2132/47">Dialogue 44.1</Src>), and BYU
        Studies still calls Elias “Mormonism’s true epic poem” (
        <Src href="https://corpus.noahairmet.com/b/57-3-81cc/194">BYU Studies 57.3</Src>). The
        Paulsen–Pulido Mother in Heaven survey preserves Gospel Themes’ begetting language (
        <Src href="https://corpus.noahairmet.com/b/50-1-0c17/97">BYU Studies 50.1</Src>), and Saturday
        Night Thoughts is cited as a doctrinal standard, abbreviated “SNT” alongside Teachings of the
        Prophet Joseph Smith (
        <Src href="https://corpus.noahairmet.com/b/ludlow-a-companion-to-your-study-of-the-22eb/22">
          Ludlow’s Companion
        </Src>
        ).
      </>
    ),
    fun: "His strongest theological claim — a once-mortal Heavenly Mother — was delivered as a supporting argument at a woman-suffrage rally, after “the eloquent ladies who have already addressed you,” and printed in a women-run periodical. And Elias, his Latter-day Saint answer to Paradise Lost, was written by a man who wanted to be a Shakespearean actor until a dream of watching Gethsemane redirected him.",
  },
  {
    id: "joseph-fielding-smith",
    name: "Joseph Fielding Smith",
    deseret: "𐐖𐐬𐑆𐐲𐑁 𐐙𐐨𐑊𐐼𐐮𐑍 𐐝𐑋𐐮𐑃",
    dates: "1876–1972",
    role: "10th President; mid-century doctrinal arbiter",
    era: "The systematizers",
    frame: "gilt",
    face: { hair: "slick", hairColor: "white", glasses: "round", collar: "bowtie" },
    stances: {
      father: { answer: "“A reasonable thought”", ink: "honey" },
      man: { answer: "Yes — a mystery", ink: "ink" },
      increase: { answer: "Yes — spirit birth", ink: "honey" },
    },
    summary:
      "The timeline’s most-cited voice, and its signature is affirm-then-police: he printed “our Father had a Father and so on” as “a reasonable thought,” affirmed the exalted-man Father and literal spirit birth from a Heavenly Mother — while ruling that God’s only progression is more kingdoms, never more knowledge, and answering the direct question with “we will leave that until we receive further knowledge.”",
    beliefs: [
      "Joseph Fielding Smith was the mid-century Church’s chief doctrinal systematizer, and his signature move was to affirm the classic Nauvoo cosmology while policing what could be inferred from it. In Doctrines of Salvation vol. 1 (1954, compiled by his son-in-law Bruce R. McConkie), the section “GOD IS AN EXALTED MAN” squarely faces the King Follett Sermon: “our Father in heaven at one time passed through a life and death and is an exalted man. This is one of the mysteries.” A page later he prints the Sermon in the Grove regress — the Father of Jesus Christ had a Father, “and so on” — and calls it “a reasonable thought,” resolving “from everlasting to everlasting” as one eternal round: spirit existence, probation, exaltation.",
      "Yet the same chapter, roughly a page earlier, carries the heading “HOW GOD DOES NOT PROGRESS”: belief that “God increases in knowledge as time goes on” is “very dangerous” — a still-learning God might, “like a chemist who mixes certain elements and blows himself up,” discover some hidden law that would shatter all. His considered position, made a First Presidency message in May 1971, is that God’s progression “consists not in gaining more knowledge or power… but in the increase and multiplying of his kingdoms.” The pair is the cleanest demonstration anywhere that divine ancestry and divine progression are independent questions: he affirmed the backward chain while denying forward growth in attributes.",
      "On eternal increase he was relentless but characteristically euphemistic from the pulpit. Across three decades of conference sermons (1941, 1946, 1951, 1965) he glossed D&C 132’s “continuation of the seeds” as “eternal increase… the crowning glory” — almost always in the negative, as “the deaths,” the thing forfeited by those who marry outside the temple. Asked pastorally in 1954, he was plainer: “Eternal lives means eternal increase,” and the damned “do not continue through posterity.” In 1960 he supplied the mechanism the sermons withheld: “how did we become such, if we had no mother to give us spirit birth?” — literal viviparous spirit birth from a Mother in Heaven, argued from “good common sense” rather than revelation. By 1967 he could tell general conference the exalted may have “the opportunity of building worlds and peopling them” — hedged with a “perhaps.”",
      "The internal tensions are real and documented. In 1958, a member asked him to reconcile the Snow couplet with the Book of Mormon’s everlasting God; he granted that “the Son was doing what the Father had done before him,” then declined: “so far as the Father is concerned, we will leave that until we receive further knowledge” — and answered the whole question about Christ instead. Answering another member who had located the regress passage in Doctrines of Salvation, he reprinted three pages of the Sermon in the Grove — and the “had a Father” sentence falls exactly inside his ellipsis; the regress sentence appears nowhere in all five volumes of Answers to Gospel Questions. And in 1966, asked how an embodied Father begot spirits, he answered: “This question the Lord has not fully explained” — six years after his confident spirit-birth argument.",
    ],
    quotes: [
      {
        text: "The Prophet taught that our Father had a Father and so on. Is not this a reasonable thought, especially when we remember that the promises are made to us that we may become like him?",
        source: "Doctrines of Salvation 1:12 (1954)",
        url: "https://corpus.noahairmet.com/b/doctrines-of-salvation-sermons-and-writings-of-3fff/11",
      },
      {
        text: "Eternal lives means eternal increase—the continuation, as the revelation says, of the seeds forever.",
        source: "Answers to Gospel Questions vol. 4 (stake conference answer, 31 Oct 1954)",
        url: "https://corpus.noahairmet.com/b/answers-to-gospel-questions-joseph-fielding-39e3/415",
      },
      {
        text: "However, so far as the Father is concerned, we will leave that until we receive further knowledge, when and if we become glorified in his kingdom.",
        source: "Answers to Gospel Questions vol. 2, “As Man Is, God Once Was” (1958)",
        url: "https://corpus.noahairmet.com/b/answers-to-gospel-questions-joseph-fielding-39e3/183",
      },
      {
        text: "His progression consists not in gaining more knowledge or power, not in further perfecting his godly attributes, but in the increase and multiplying of his kingdoms.",
        source: "First Presidency message, Ensign, May 1971",
        url: "https://www.churchofjesuschrist.org/study/ensign/1971/05/the-most-important-knowledge",
      },
    ],
    books: (
      <>
        The archive holds Doctrines of Salvation (3 vols.) and Answers to Gospel Questions (5 vols.) in
        full, confirming the famous juxtaposition at page level: “GOD IS AN EXALTED MAN,” “HOW GOD DOES
        NOT PROGRESS,” the chemist who blows himself up, and “had a Father and so on” all share one
        spread (
        <Src href="https://corpus.noahairmet.com/b/doctrines-of-salvation-sermons-and-writings-of-3fff/10">
          DoS pp. 10–11
        </Src>
        ). A phrase-search for “our Father had a Father” across ~3.2 million pages returns exactly one
        hit: that page. Man: His Origin and Destiny and The Way to Perfection are not full-text in the
        archive.
      </>
    ),
    fun: "He practiced the increase he preached. At the October 1965 conference, aged 89: “I am the father of eleven children… They will belong to me forever and are the foundation stones of my kingdom. My posterity reaches today over the one-hundred mark” — his grandchildren offered from the pulpit as the down payment on an eternal dominion.",
  },
  {
    id: "spencer-w-kimball",
    name: "Spencer W. Kimball",
    deseret: "𐐝𐐹𐐯𐑌𐑅𐐲𐑉 𐐗𐐮𐑋𐐺𐐲𐑊",
    dates: "1895–1985",
    role: "12th President, 1973–1985",
    era: "The systematizers",
    frame: "walnut",
    face: { hair: "fringe", hairColor: "silver", glasses: "round", collar: "suit", coat: "#4a4238", smile: true },
    stances: {
      father: { answer: "Never engaged", ink: "muted" },
      man: { answer: "Yes — the couplet", ink: "honey" },
      increase: { answer: "Yes — devotional", ink: "ink" },
    },
    summary:
      "Godhood as destiny, preached in the devotional register: “gods in embryo,” 225,000 potential gods counted in one priesthood session, “no parent has ever yet on this earth been the parent of a spirit.” The destination stays loud while the mechanism goes quiet — and the backward question is never engaged at all, though he quoted the couplet as President and retired Adam–God by name.",
    beliefs: [
      "Kimball is the great mid-century voice of godhood-as-destiny. From his first decade in the Twelve he speaks of exaltation as a list of concrete endowments — “immortality and everlasting life, eternal growth, divine leadership, eternal increase, perfection, and with it all — Godhood” (1952) — a series, not an argument. He never defines mechanisms and never engages regress questions; the destination is preached, the metaphysics assumed. His signature phrase, “gods in embryo,” runs through his sermons and through The Miracle of Forgiveness (1969), where man carries “the seeds of godhood neatly tucked away in him.”",
      "The forward axis gets its fullest treatment in “Our Great Potential” (April 1977, priesthood session), his strongest timeline entry: he reads Brigham Young’s “we will then receive authority to produce both spirit and body” approvingly, then in his own voice welds the two axes together — “no parent has ever yet on this earth been the parent of a spirit,” followed at once by the Snow couplet as warrant. The “yet” carries the whole promise. Hearsay caveat: the two inner Brigham Young quotes are Journal of Discourses shorthand (grade C, speaker-unreviewed) carried inside an official grade-A address — and he quotes the drifted popular variant of the couplet, not Snow’s published wording.",
      "Yet even Kimball shows the century’s quieting of the mechanism. In October 1975 he counts a priesthood session — “225,000 of you may become gods… worlds for all of us, for every one of us 225,000” — the plainest plural-godhood statement by a sitting President in the hosted modern archive, and it says nothing about spirit offspring. In October 1973 he reads D&C 132’s “continuation of the seeds forever and ever” into the record without a word of gloss. The destination stays loud; the begetting goes quiet, except for the 1977 outlier.",
      "Two boundary notes. In October 1976 he warned from the pulpit against “doctrines… alleged to have been taught by some of the General Authorities of past generations — such, for instance, is the Adam-God theory”: a repudiation aimed at Adam–God, not at increase or the couplet, but it established the vocabulary later used to retire speculative theogony. And in 1977–78 he became the modern high-water mark for Heavenly Mother: “They gave your eternal intelligence spirit form” (Oct 1978) and “that doctrinal hymn and anthem of affection, ‘O My Father’” (Apr 1978) — always parent-affirming, always mechanism-unstated.",
    ],
    quotes: [
      {
        text: "The blessings of eternity… bring to men immortality and everlasting life, eternal growth, divine leadership, eternal increase, perfection, and with it all — Godhood.",
        source: "Conference Report, 4 Apr 1952",
        url: "https://archive.org/details/conferencereport1952a/page/n20",
      },
      {
        text: "Brethren, 225,000 of you are here tonight. I suppose 225,000 of you may become gods. There seems to be plenty of space out there in the universe.",
        source: "Priesthood session, Oct 1975",
        url: "https://www.churchofjesuschrist.org/study/general-conference/1975/10/the-privilege-of-holding-the-priesthood?lang=eng",
      },
      {
        text: "But no parent has ever yet on this earth been the parent of a spirit… “As man is, God once was; and as God is, man may become.”",
        source: "“Our Great Potential,” Apr 1977",
        url: "https://www.churchofjesuschrist.org/study/general-conference/1977/04/our-great-potential?lang=eng",
      },
      {
        text: "We are gods in embryo, and the Lord demands perfection of us.",
        source: "The Miracle of Forgiveness (1969), p. 141",
        url: "https://corpus.noahairmet.com/b/kimball-miracle-of-forgiveness-91f4/141",
      },
    ],
    books: (
      <>
        The archive shows The Miracle of Forgiveness — a book about sin and repentance — framed end to
        end by godhood: eleven “godhood” passages, from “exaltation — eternal life with godhood” (
        <Src href="https://corpus.noahairmet.com/b/kimball-miracle-of-forgiveness-91f4/5">p. 5</Src>)
        through “repentance and forgiveness are part of the glorious climb toward godhood” to the
        close, where he reprints his own 1952 conference peroration (
        <Src href="https://corpus.noahairmet.com/b/kimball-miracle-of-forgiveness-91f4/154">p. 154</Src>
        ). The embryo image is native to the book — “a god in embryo with the seeds of godhood neatly
        tucked away in him” — deployed, characteristically, as an argument against despair after sin,
        not as cosmology.
      </>
    ),
    fun: "“Gods in embryo” was his comeback in a real conversation: a man protested that fully forgiving an enemy “takes a superman.” Kimball: “Yes — but we are commanded to be supermen… We are gods in embryo, and the Lord demands perfection of us.” Divine potential, deployed as a rebuttal about grudges.",
  },
  {
    id: "bruce-r-mcconkie",
    name: "Bruce R. McConkie",
    deseret: "𐐒𐑉𐐭𐑅 𐐣𐐲𐐿𐐪𐑍𐐿𐐨",
    dates: "1915–1985",
    role: "Apostle, 1972–1985; the last encyclopedist",
    era: "The systematizers",
    frame: "gilt",
    face: { hair: "receding", hairColor: "darkbrown", collar: "suit", coat: "#2b2f36", browHeavy: true },
    stances: {
      father: { answer: "Yes — “God of Gods”", ink: "honey" },
      man: { answer: "By entailment", ink: "ink" },
      increase: { answer: "Yes — most explicit", ink: "honey" },
    },
    summary:
      "Mormon Doctrine states the full two-directional chain more literally than any other twentieth-century source — the Father is “a God of Gods,” spirits are “actually born,” exalted couples multiply “their race without end” — while heresy number one of his Seven Deadly Heresies damns any God who learns: kingdoms may grow, attributes may not. The Father’s mortality rides on a single adjective, “resurrected,” never argued.",
    beliefs: [
      "McConkie was the Church’s last great encyclopedist, and his Mormon Doctrine (1958; 2nd ed. 1966) states the full two-directional chain more literally than any other twentieth-century source. The “Spirit Children”/“Spirit Birth” entries predicate the same begetting of the Father’s past and the exalted’s future in identical words: spirits are “actually born as the offspring of a Heavenly Father, a glorified and exalted Man,” and “will be born in a future eternity to future exalted beings.” The “God of Gods” entry quotes Joseph Smith’s Sermon in the Grove regress in full, and the “Eternity to Eternity” entry describes an “eternal, unending repetition” in which today’s spirit children become tomorrow’s exalted parents, “multiplying their race without end.”",
      "Simultaneously, he is the tradition’s fiercest enemy of divine progression in attributes. Mormon Doctrine’s “Eternal Progression” entry rules: “God is not progressing in knowledge, truth, virtue, wisdom… But he is progressing in the sense that his creations increase, his dominions expand, his spirit offspring multiply” — a formula sourced to Doctrines of Salvation, his father-in-law Joseph Fielding Smith’s teachings, which McConkie himself had compiled in 1954. The Seven Deadly Heresies fireside (BYU, 1 June 1980) made heresy number one the idea that God learns new truths: “This is false—utterly, totally, and completely. There is not one sliver of truth in it.” Note the trap in quoting him: the fireside affirms “God progresses” and instantly redefines it as expansion of kingdoms. Adam–God was heresy six, and the fireside triggered the famous McConkie–Eugene England correspondence (1981).",
      "His pulpit register evolved into deliberate euphemism. From “Salvation Is a Family Affair” (1970) on, the generative doctrine appears as “eternal family units patterned after his eternal family” — everything the older sources said except the word children. The one place he broke cover in the correlated era is the April 1982 priesthood session, glossing his own euphemism: the patriarchal order “assures its members of eternal increase, or in other words of spirit children in the resurrection” — the timeline calls it the most explicit forward statement in the modern general conference corpus.",
      "Tensions to note: he affirmed of Christ, in general conference (October 1982), exactly the attainment vocabulary he denied the Father — the Firstborn “advanced and progressed until he became like unto God” over “long ages and eons.” He described the Father as “resurrected” from his earliest conference address (1947) through his 1977 creed, yet never once argued the Father’s mortality — it rides on a single adjective each time. Hearsay grades are clean (all A, his own published words), but status varies: Mormon Doctrine was never official, drew First Presidency concern on publication, and was quietly let go out of print in 2010; the Seven Deadly Heresies is a fireside, never official.",
    ],
    quotes: [
      {
        text: "Hence, the Father, who shall continue to all eternity as the God of exalted beings, is a God of Gods… both the Father and the Son, as also all exalted beings, are now or in due course will become Gods of Gods.",
        source: "Mormon Doctrine, “God of Gods” (2nd ed., p. 230)",
        url: "https://corpus.noahairmet.com/b/mcconkie-mormon-doctrine-2nd-edition-9c13/527",
      },
      {
        text: "This is false—utterly, totally, and completely… God progresses in the sense that his kingdoms increase and his dominions multiply—not in the sense that he learns new truths.",
        source: "The Seven Deadly Heresies, BYU fireside, 1 Jun 1980",
        url: "https://speeches.byu.edu/talks/bruce-r-mcconkie/seven-deadly-heresies/",
      },
      {
        text: "An order that prevails in the highest heaven of the celestial world, an order that assures its members of eternal increase, or in other words of spirit children in the resurrection.",
        source: "“The Doctrine of the Priesthood,” general conference, Apr 1982",
        url: "https://www.churchofjesuschrist.org/study/general-conference/1982/04/the-doctrine-of-the-priesthood?lang=eng",
      },
      {
        text: "Those who become gods will then be from eternity to eternity, everlastingly the same, always possessing the fullness of all things and multiplying their race without end.",
        source: "Mormon Doctrine, “Eternity to Eternity” (2nd ed., p. 175)",
        url: "https://corpus.noahairmet.com/b/mcconkie-mormon-doctrine-2nd-edition-9c13/179",
      },
    ],
    books: (
      <>
        The archive shelves both editions of Mormon Doctrine plus the Doctrinal New Testament
        Commentary and the Messiah trilogy. A page-read closed a verification gap the timeline had
        flagged: “multiplying their race without end” is verbatim in the 1958 first edition (
        <Src href="https://corpus.noahairmet.com/b/mcconkie-mormon-doctrine-1st-edition-426f/223">
          p. 223
        </Src>
        ) and the 1966 second (
        <Src href="https://corpus.noahairmet.com/b/mcconkie-mormon-doctrine-2nd-edition-9c13/179">
          p. 179
        </Src>
        ). The same page-read shows the “Eternal Progression” entry adding a limit usually missed: for
        everyone below exaltation, “their progression is not eternal and unlimited… There will be
        truths such persons never learn, powers they never possess.”
      </>
    ),
    fun: "The circle of authority here is a family circle: McConkie married Joseph Fielding Smith’s daughter Amelia in 1937, compiled his father-in-law’s sermons into Doctrines of Salvation (1954), then cited that compilation throughout Mormon Doctrine as the proof-text for the anti-progression doctrine — which the Church’s manuals later sourced back to Joseph Fielding Smith. Son-in-law canonized father-in-law, and each man’s authority thereafter rested partly on the other’s book.",
  },
  {
    id: "dallin-h-oaks",
    name: "Dallin H. Oaks",
    deseret: "𐐔𐐰𐑊𐐮𐑌 𐐄𐐿𐑅",
    dates: "b. 1932",
    role: "First Counselor in the First Presidency",
    era: "The correlated present",
    frame: "gilt",
    face: { hair: "fringe", hairColor: "silver", glasses: "rimless", collar: "suit", coat: "#333a44", smile: true },
    stances: {
      father: { answer: "Silent", ink: "muted" },
      man: { answer: "Silent", ink: "muted" },
      increase: { answer: "Euphemism only", ink: "oxblood" },
    },
    summary:
      "The correlated present in one career: theology “begins with heavenly parents,” yet a full sermon on the nature of the Father contains no couplet, no King Follett, no origin — the space filled instead by “the Supreme Being, the Creator and Ruler of the universe.” “Eternal increase” quietly becomes children born in mortality, and his boundary rule — teach only what meets the standards of official doctrine — would retire most of this hall.",
    beliefs: [
      "Oaks is the architect of the modern correlated reframe: exaltation restated as family. His most-quoted sentence pair — “Our theology begins with heavenly parents. Our highest aspiration is to be like them” (“Apostasy and Restoration,” April 1995) — makes plural divine parentage the first premise of the theology while never naming, describing, or defending the Mother anywhere in the address. The same talk names deification in patristic vocabulary (“the ancient Christian doctrine of… deification or apotheosis”) and immediately domesticates it: “eternal life is not a mystical union with an incomprehensible spirit-god. Eternal life is family life.”",
      "His April 2017 “The Godhead and the Plan of Salvation” is the timeline’s clearest negative datapoint: a full apostolic address on the nature of God the Father — opening “It all begins with God the Father. While we know comparatively little about Him…” — containing no Snow couplet, no King Follett, no Heavenly Mother, no divine progression, no origin. He quotes the 1909 First Presidency statement only for two Christological titles, omitting that document’s own claims that man is the literal offspring of heavenly parents and that the Father was once as man now is. What fills the space is McConkie’s maximal monotheizing formulation, “the Supreme Being, the Creator and Ruler of the universe” — which does not deny a chain so much as make it unaskable.",
      "On increase, Oaks reaches the old language exactly once, in October 2019: “Eternal life includes the creative powers inherent in the combination of male and female—what modern revelation describes as the ‘continuation of the seeds forever and ever’” — the scriptural code phrase carrying the whole content, the final noun (spirit children) left unstated. A year earlier he had performed the semantic shift the other direction: “Children are our most precious gift from God—our eternal increase” (Oct 2018) — a term that for a century named the posterity of the exalted, re-applied to mortal childbearing in the opening line of a demographic argument. The timeline’s caveat: nothing suggests a conscious operation on the older usage; the tag records the shift, not an intention.",
      "Finally, Oaks supplies the boundary rule itself. “Trust in the Lord” (Oct 2019) disqualifies personal visions of the next life as doctrine, endorses the standard that doctrine is what all fifteen apostles teach, and instructs: wondering is permitted privately, “but let us not teach or use as official doctrine what does not meet the standards of official doctrine.” Scope caution: the talk’s explicit target is the postmortal spirit world and next-life sealings — but the rule as stated is general, and applied backward it would disqualify most of the twentieth-century material on this subject.",
    ],
    quotes: [
      {
        text: "Our theology begins with heavenly parents. Our highest aspiration is to be like them.",
        source: "“Apostasy and Restoration,” Apr 1995",
        url: "https://www.churchofjesuschrist.org/study/general-conference/1995/04/apostasy-and-restoration?lang=eng",
      },
      {
        text: "Eternal life includes the creative powers inherent in the combination of male and female—what modern revelation describes as the “continuation of the seeds forever and ever.”",
        source: "“Two Great Commandments,” Oct 2019",
        url: "https://www.churchofjesuschrist.org/study/general-conference/2019/10/35oaks",
      },
      {
        text: "Children are our most precious gift from God—our eternal increase.",
        source: "“Parents and Children,” Oct 2018",
        url: "https://www.churchofjesuschrist.org/study/general-conference/2018/10/parents-and-children",
      },
      {
        text: "But let us not teach or use as official doctrine what does not meet the standards of official doctrine.",
        source: "“Trust in the Lord,” Oct 2019",
        url: "https://www.churchofjesuschrist.org/study/general-conference/2019/10/17oaks",
      },
    ],
    books: (
      <>
        No Oaks doctrinal monograph is shelved, but Turley’s authorized biography shows the
        conference-pulpit fence operating in private pastoral correspondence: “It is true that we don’t
        know everything about this subject, but we do know that plural marriage is not necessary for
        exaltation… People take the circumstances of mortality and try to translate them, unchanged,
        into the next life, which causes some problems” (
        <Src href="https://corpus.noahairmet.com/b/turley-in-the-hands-of-the-lord-the-life-of-c4e9/313">
          In the Hands of the Lord, p. 313
        </Src>
        ). The archive also documents his reach: the “heavenly parents” pair is quoted across at least
        nine separate volumes — Dialogue, BYU Studies, FAIR, Scripture Central (
        <Src href="https://corpus.noahairmet.com/b/50-1-0c17/96">e.g. BYU Studies 50.1</Src>) — making
        his sentence the standard modern citation for the doctrine.
      </>
    ),
    fun: "In 1981, Justice Oaks made Time and Newsweek’s shortlists for the U.S. Supreme Court seat that went to Sandra Day O’Connor — and Antonin Scalia personally phoned to ask whether Oaks wanted the D.C. Circuit vacancy before pursuing it himself. Oaks passed and offered to put in a word; Scalia took the seat and rode it to the Supreme Court in 1986. Oaks’s verdict on the high court: “Only a fool would aspire to it, but no one would turn it down.”",
  },
];
