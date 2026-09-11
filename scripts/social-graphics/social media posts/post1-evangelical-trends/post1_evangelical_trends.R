# ============================================================
# State of Theology carousel  —  @ithinkisam
#
# Fill the NA cells in `dat` as you find them; NA rows are
# dropped automatically, so the script runs at any stage.
# Output 1080 x 1350 (Instagram 4:5) via ragg. Fonts are
# self-hosted from this repo's Data Explorer chart pipeline
# (scripts/state-of-theology-graphics/fonts/), not assumed to
# be installed on the OS — see "FONTS" below.
# ============================================================
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tibble)
  library(forcats); library(ggtext); library(ragg); library(systemfonts)
})

# ------------------------------------------------------------
# Where this file lives, so paths below work no matter the cwd
# `Rscript post1_evangelical_trends.R` is run from.
# ------------------------------------------------------------
this_file <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) normalizePath(f) else normalizePath("post1_evangelical_trends.R")
}
SCRIPT_DIR <- dirname(this_file())
OUT <- file.path(SCRIPT_DIR, "png")
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

# ============================================================
# DESIGN TOKENS — pulled from the Data Explorer chart pipeline,
# not invented for this post. Canonical source:
# scripts/state-of-theology-graphics/render_chart.py (this repo's
# Python renderer for the same State of Theology survey — same
# 1080x1350 canvas, same fonts) and scripts/chart_style.py.
# ============================================================
ink   <- "#1A1A1A"  # render_chart.py INK   — titles, axis/value labels
paper <- "#FFFFFF"  # render_chart.py PAPER — canvas background. The explorer
                     # deliberately uses pure white here, not the Instagram
                     # scripts' old cream (#F7F5F0) — see that file's own
                     # "Paper is pure white here, deliberately different from
                     # the Instagram scripts' cream" comment.
muted <- "#6E6A63"  # render_chart.py MUTED — subtitle/caption/secondary text
grid  <- "#D9D5CC"  # render_chart.py GRID (== chart_style.py BORDER) — gridlines

# Categorical series palette, in render_chart.py's PALETTE order.
# This post only uses two of the five defined groups.
amber <- "#C9721C"  # PALETTE["Evangelical"]
teal  <- "#2C7B8C"  # PALETTE["All U.S. adults"]

EV <- "Evangelicals by affiliation"; US <- "All U.S. adults"
pal <- c(setNames(amber, EV), setNames(teal, US))

# ------------------------------------------------------------
# FONTS — Roboto Condensed (body) + Roboto Slab (titles), the
# same pair scripts/state-of-theology-graphics/render_chart.py
# uses, self-hosted from that pipeline's fonts/ folder rather
# than assumed to be installed system-wide.
# ------------------------------------------------------------
FONTS_DIR <- normalizePath(file.path(SCRIPT_DIR, "..", "..", "..",
                                      "state-of-theology-graphics", "fonts"))
register_font(
  name = "Roboto Condensed",
  plain = file.path(FONTS_DIR, "RobotoCondensed-Regular.ttf"),
  bold = file.path(FONTS_DIR, "RobotoCondensed-Bold.ttf"),
  italic = file.path(FONTS_DIR, "RobotoCondensed-Italic.ttf"),
  bolditalic = file.path(FONTS_DIR, "RobotoCondensed-BoldItalic.ttf"))
register_font(
  # Only the bold cut is bundled — this family is only ever used at
  # face="bold" in this script, so registering both faces to the same
  # file matches actual usage rather than silently falling back to a
  # system substitute for the (unused) plain face.
  name = "Roboto Slab",
  plain = file.path(FONTS_DIR, "RobotoSlab-Bold.ttf"),
  bold = file.path(FONTS_DIR, "RobotoSlab-Bold.ttf"))

# ============================================================
# DATA.  NA = still needed.
# ============================================================
dat <- tribble(
  ~item,      ~year, ~group, ~pct,
  # --- 1. Trinity ------------------------------------------
  "trinity",  2016, US, 69,   "trinity",  2016, EV, 94,
  "trinity",  2018, US, 70,   "trinity",  2018, EV, 93,
  "trinity",  2020, US, 72,   "trinity",  2020, EV, 93,
  "trinity",  2022, US, 71,   "trinity",  2022, EV, 92,
  "trinity",  2025, US, 71,   "trinity",  2025, EV, 95,
  # --- 2. Holy Spirit as impersonal force ------------------
  "spirit",   2016, US, 56,   "spirit",   2016, EV, 56,
  "spirit",   2018, US, 59,   "spirit",   2018, EV, 59,
  "spirit",   2020, US, 59,   "spirit",   2020, EV, 51,
  "spirit",   2022, US, 59,   "spirit",   2022, EV, 55,
  "spirit",   2025, US, 57,   "spirit",   2025, EV, 52,
  # --- 3. Arianism (dropped from the 2025 survey) ----------
  "arian",    2016, US, 52,   "arian",    2016, EV, 63,
  "arian",    2018, US, 57,   "arian",    2018, EV, 71,
  "arian",    2020, US, 55,   "arian",    2020, EV, 56,
  "arian",    2022, US, 55,   "arian",    2022, EV, 61,
  # --- 4. God accepts worship of all religions -------------
  "religions",2016, US, 64,   "religions",2016, EV, 49,
  "religions",2018, US, 66,   "religions",2018, EV, 53,
  "religions",2020, US, 64,   "religions",2020, EV, 46,
  "religions",2022, US, 67,   "religions",2022, EV, 58,
  "religions",2025, US, 65,   "religions",2025, EV, 49,
  # --- 5. Most people good by nature -----------------------
  "nature",   2016, US, 65,   "nature",   2016, EV, 53,
  "nature",   2018, US, 66,   "nature",   2018, EV, 55,
  "nature",   2020, US, 65,   "nature",   2020, EV, 47,
  "nature",   2022, US, 66,   "nature",   2022, EV, 55,
  "nature",   2025, US, 66,   "nature",   2025, EV, 55,
  # --- 6. Abortion is a sin --------------------------------
  "abortion", 2016, US, 49,   "abortion", 2016, EV, 76,
  "abortion", 2018, US, 52,   "abortion", 2018, EV, 80,
  "abortion", 2020, US, 51,   "abortion", 2020, EV, 76,
  "abortion", 2022, US, 53,   "abortion", 2022, EV, 74,
  "abortion", 2025, US, 49,   "abortion", 2025, EV, 73,
  # --- 7. Sex outside marriage is a sin --------------------
  "sex",      2016, US, 49,   "sex",      2016, EV, 81,
  "sex",      2018, US, 51,   "sex",      2018, EV, 79,
  "sex",      2020, US, 51,   "sex",      2020, EV, 77,
  "sex",      2022, US, 53,   "sex",      2022, EV, 77,
  "sex",      2025, US, 52,   "sex",      2025, EV, 82,
  # --- 8. Bible's condemnation of homosexual behavior ------
  #        shown as % who DISAGREE (the traditional position)
  # --- 9. Jesus was a great teacher, but not God -----------
  "teacher",  2020, US, 52,   "teacher",  2020, EV, 32,
  "teacher",  2022, US, 53,   "teacher",  2022, EV, 44,
  "teacher",  2025, US, 49,   "teacher",  2025, EV, 34,
  # --- 8. Bible's condemnation, % who DISAGREE -------------
  "homo",     2016, US, 44,   "homo",     2016, EV, 72,
  "homo",     2018, US, 41,   "homo",     2018, EV, 73,
  "homo",     2020, US, 44,   "homo",     2020, EV, 72,
  "homo",     2022, US, 42,   "homo",     2022, EV, 65,
  "homo",     2025, US, 46,   "homo",     2025, EV, 74
) |>
  filter(!is.na(pct)) |>
  mutate(group = fct_relevel(group, EV))

# Slide 9: evangelicals by affiliation, 2022 wave only. Every bar is now the
# TRADITION-CONSISTENT response, not always "agree" - which direction counts
# as tradition-consistent depends on what kind of statement it is:
#   - orthodox social statements (the two Ethics rows below): agree.
#   - morally liberal statements (the homo row): disagree.
#   - heterodox theology statements (all five Doctrine rows - each one
#     states a historic heresy, e.g. Arianism, Pelagianism, denial of the
#     Trinity/Christ's deity): disagree. (There's no orthodox-theology row
#     in this set - a statement that stated the orthodox position directly,
#     e.g. the Trinity statement, would use agree instead - but if one is
#     ever added here, it belongs in this comment's fourth category.)
# Doctrine rows' pct switched from % agree to % disagree accordingly - see
# ../../evangelical-quiz/README.md-style sourcing note below for where the
# disagree numbers came from, since the workbook/data.json only carry each
# item's agree-side 2022 number.
#
# Disagree percentages for the four Doctrine items that AREN'T `arian`
# (which already had a 2022 disagree% in data.json/render_chart.py's own
# source) were computed the same way build_data.py's `arian_wave_reference`
# validates arian's own number: WT-weighted response distribution among
# RELTRAD==1 (Evangelical) rows in the State of Theology 2022 respondent
# microdata (https://thestateoftheology.com/assets/data/us/responses-2022.csv),
# summing the strongly_disagree + somewhat_disagree weight shares. Column
# per item, per the 2022 report's own item numbering (Ligonier State of
# Theology 2022 Full Report PDF): all_religions=Q21_3, jesus_not_god=Q22_3,
# spirit_force=Q23_1, good_by_nature=Q24_1. Cross-checked two ways: the
# recomputed agree% for all five items lands within 1pt of this script's own
# existing (unchanged) 2022 agree numbers, and the recomputed spirit_force
# disagree% (34%) matches the 2022 Full Report's own published bullet
# ("Evangelicals are the mostly likely to Disagree (34%)") exactly.
dirword_cap <- function(d) if (d == "agree") "Agree" else "Disagree"
scorecard <- tribble(
  ~statement,                                                  ~pct, ~kind,     ~dir,
  "Sex outside of traditional marriage is a sin",                77, "Ethics",   "agree",
  "Abortion is a sin",                                           74, "Ethics",   "agree",
  "The Bible's condemnation of homosexual behavior\ndoesn't apply today", 65, "Ethics", "disagree",
  "Jesus is the first and greatest being created by God",        30, "Doctrine", "disagree",
  "God accepts the worship of all religions",                    35, "Doctrine", "disagree",
  "The Holy Spirit is a force but is not a personal being",      34, "Doctrine", "disagree",
  "Everyone sins a little, but most people are good by nature",  40, "Doctrine", "disagree",
  "Jesus was a great teacher, but he was not God",               53, "Doctrine", "disagree"
) |> filter(!is.na(pct))

# ============================================================
# SLIDE COPY
# ============================================================
# Footnote: handle only, muted, small — no sponsor/fielder/method/
# panel-size/margin-of-error block, no per-slide notes.
SRC <- paste0(
  "<b>Data: The State of Theology survey</b><br>",
  "<b>@ithinkisam</b>")

items <- list(
  trinity = list(n = 1, file = "1_nicaea_won.png", title = "Nicaea won", star = NA,
    quote = "There is one true God in three persons:<br>God the Father, God the Son, and God the Holy Spirit.",
    series = c(EV, US), lead = NULL),

  spirit = list(n = 3, file = "3_one_god_two_persons.png", title = "One God, two persons", star = NA,
    quote = "The Holy Spirit is a force but is not a personal being.",
    series = c(EV, US), lead = NULL),

  arian = list(n = 2, file = "2_nicaea_lost.png", title = "Nicaea lost", star = NA,
    quote = "Jesus is the first and greatest being created by God.",
    series = c(EV, US), lead = NULL),

  religions = list(n = 4, file = "4_many_roads.png", title = "Many roads", star = NA,
    quote = "God accepts the worship of all religions, including<br>Christianity, Judaism, and Islam.",
    series = c(EV, US), lead = NULL),

  nature = list(n = 5, file = "5_pelagius_undefeated.png", title = "Pelagius, still at large", star = NA,
    quote = "Everyone sins a little, but most people are good by nature.",
    series = c(EV, US), lead = NULL),

  abortion = list(n = 6, file = "6_abortion.png", title = "Abortion is a sin", star = NA,
    quote = "Abortion is a sin.",
    series = c(EV, US), lead = NULL),

  sex = list(n = 7, file = "7_sex_outside_marriage.png", title = "Sex outside traditional marriage", star = NA,
    quote = "Sex outside of traditional marriage is a sin.",
    series = c(EV, US), lead = NULL),

  homo = list(n = 8, file = "8_condemnation.png",
    title = "Biblical authority on sexuality", star = NA,
    quote = "The Bible's condemnation of homosexual behavior<br>doesn't apply today.",
    series = c(EV, US), direction = "disagree", lead = NULL),

  teacher = list(n = 9, file = "jesus_not_god.png",
    title = "Great teacher, not God", star = NA,
    quote = "Jesus was a great teacher, but he was not God.",
    series = c(EV, US), lead = NULL)
)

# ============================================================
# THEME
# ============================================================
theme_burge <- function() {
  theme_minimal(base_family = "Roboto Condensed", base_size = 15) +
    theme(
      plot.background   = element_rect(fill = paper, colour = NA),
      panel.background  = element_rect(fill = paper, colour = NA),
      panel.grid.minor  = element_blank(),
      # 34 -> 48pt: bigger titles, matching the Data Explorer chart
      # pipeline's own bump from 26/27pt to 32pt for the same reasoning
      # (legible at Instagram's scaled-down feed size) taken further,
      # per this rollout's explicit target. element_textbox_simple (not
      # plain element_text) so a long title wraps to a second line at
      # the canvas's real width instead of running off it.
      plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                                size = 40, colour = ink, lineheight = 1.05,
                                width = unit(7.8, "in"), margin = margin(b = 10)),
      plot.subtitle = element_markdown(family = "Roboto Condensed", size = 22,
                                       colour = ink, lineheight = 1.4,
                                       margin = margin(b = 22)),
      plot.caption = element_markdown(family = "Roboto Condensed", size = 16,
                                      colour = ink, hjust = 0, lineheight = 1.6,
                                      margin = margin(t = 20)),
      plot.caption.position = "plot", plot.title.position = "plot",
      axis.title = element_blank(), legend.position = "none",
      plot.margin = margin(28, 30, 20, 28))
}

save_slide <- function(p, file) {
  ggsave(file.path(OUT, file), p, device = ragg::agg_png,
         width = 9, height = 11.25, dpi = 120, bg = paper)
}

# ============================================================
# SLIDES 1-8  (vertical grouped bars by year)
# ============================================================
make_chart <- function(k) {
  it <- items[[k]]
  d <- filter(dat, item == k)
  if (!nrow(d)) return(invisible(NULL))
  d <- mutate(d, lab = if_else(!is.na(it$star) & year == it$star,
                               paste0(pct, "%*"), paste0(pct, "%")))
  yrs <- sort(unique(d$year))
  xlabs <- if (is.na(it$star)) as.character(yrs) else
    ifelse(yrs == it$star, paste0(yrs, "*"), as.character(yrs))
  lsize <- if (length(yrs) >= 6) 5.8 else if (length(yrs) >= 5) 6.4 else
           if (length(yrs) >= 4) 7 else 8

  dirword <- if (!is.null(it$direction)) it$direction else "agree"
  # zero-based always; ceiling sits just above this chart's own data
  ytop <- ceiling(max(d$pct) / 10) * 10
  if (ytop - max(d$pct) < 5) ytop <- ytop + 10
  ystep <- if (ytop >= 80) 20 else 10
  legend <- if (length(it$series) == 2)
    paste0("<span style='font-size:22pt;color:", amber, "'><b>&#9632; Evangelicals by affiliation</b></span>",
           "<span style='color:", grid, "'> &#124; </span>",
           "<span style='font-size:22pt;color:", teal, "'><b>&#9632; All U.S. adults</b></span>")
  else paste0("<span style='font-size:22pt;color:", teal, "'><b>&#9632; All U.S. adults</b></span>")

  # Title IS the survey statement (see "Titles: accurate, not editorial"
  # in scripts/state-of-theology-graphics/STYLE.md) — no separate quote
  # line in the subtitle duplicating it. Manual <br> breaks in `quote`
  # were tuned for the old, narrower subtitle placement; strip them here
  # and let element_textbox_simple's own auto-wrap handle the title box.
  title_text <- paste0("“", gsub("<br>", " ", it$quote), "”")
  title_size <- if (nchar(title_text) > 95) 30 else if (nchar(title_text) > 65) 34 else 40

  sub <- paste0(
    "Share who strongly <b>", dirword, "</b> or somewhat <b>", dirword, "</b>",
    if (!is.null(it$lead)) paste0("<br>", it$lead) else "",
    "<br><br>", legend)

  p <- ggplot(d, aes(factor(year), pct, fill = group)) +
    geom_col(position = position_dodge2(width = .85, preserve = "single"), width = .78) +
    geom_text(aes(label = lab, colour = group),
              position = position_dodge2(width = .78, preserve = "single"),
              vjust = -.55, family = "Roboto Condensed", fontface = "bold",
              size = lsize, show.legend = FALSE) +
    scale_fill_manual(values = pal) + scale_colour_manual(values = pal) +
    scale_x_discrete(labels = xlabs) +
    scale_y_continuous(limits = c(0, ytop), breaks = seq(0, ytop, ystep),
                       labels = function(x) paste0(x, "%"),
                       expand = expansion(mult = c(0, .04))) +
    labs(title = title_text, subtitle = sub, caption = SRC) +
    theme_burge() +
    theme(panel.grid.major.x = element_blank(),
          panel.grid.major.y = element_line(colour = grid, linewidth = .4),
          plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                                    size = title_size, colour = ink, lineheight = 1.05,
                                    width = unit(7.8, "in"), margin = margin(b = 10)),
          axis.text.x = element_text(size = 19, colour = ink, face = "bold",
                                     margin = margin(t = 6)),
          axis.text.y = element_text(size = 14, colour = muted))
  save_slide(p, it$file)
}

# ============================================================
# SLIDE 9  (horizontal scorecard, evangelicals 2022)
# ============================================================
make_scorecard <- function() {
  d <- scorecard |>
    mutate(statement = fct_reorder(statement, pct),
           kind = fct_relevel(kind, "Ethics"))

  p <- ggplot(d, aes(pct, statement, fill = kind)) +
    geom_col(width = .68) +
    # Label now names the direction ("Agree"/"Disagree") alongside the
    # value, since bars mix both directions - see the tribble's own
    # top-of-block comment for which statement uses which.
    geom_text(aes(label = paste0(pct, "% ", vapply(dir, dirword_cap, character(1))),
                  colour = kind),
              hjust = -0.06, family = "Roboto Condensed",
              fontface = "bold", size = 8, show.legend = FALSE) +
    scale_fill_manual(values = c(Ethics = amber, Doctrine = teal)) +
    scale_colour_manual(values = c(Ethics = amber, Doctrine = teal)) +
    # 118 -> 260: the longer "NN% Disagree"/"NN% Agree" labels are ~3x the
    # width of the old bare "NN%" labels. 200 still left the longest labels
    # touching the plot margin with zero breathing room (reads as clipped
    # even though it technically wasn't) - widened further so every label
    # clears with visible margin.
    scale_x_continuous(limits = c(0, 260), expand = expansion(mult = c(0, 0))) +
    labs(
      # The old punchy title ("Firmer, but not firm") is gone - the title
      # now names what EVERY bar measures now that direction varies by row:
      # not "% who agree" but "% giving the response consistent with the
      # tradition's own historic teaching" (agree for the orthodox social
      # statements, disagree for the heterodox theology ones and the one
      # morally liberal statement) - see the tribble's own comment above.
      title = "Share of evangelicals giving the tradition-consistent response, 2022",
      subtitle = paste0(
        "<span style='color:", amber, "'><b>&#9632; Contested moral issues</b></span>",
        "<span style='color:", grid, "'> &#124; </span>",
        "<span style='color:", teal, "'><b>&#9632; Ancient heresies</b></span>"),
      caption = SRC) +
    theme_burge() +
    theme(panel.grid.major.y = element_blank(),
          panel.grid.major.x = element_line(colour = grid, linewidth = .4),
          axis.text.x = element_blank(),
          axis.text.y = element_text(size = 18, colour = ink, face = "bold",
                                     hjust = 1, lineheight = 1.1),
          # This title is a plain description, not a short punchy claim or
          # a short quoted statement — same >65-char step-down `make_chart`
          # uses for a long quoted title, applied here for the same reason.
          plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                                    size = 34, colour = ink, lineheight = 1.05,
                                    width = unit(7.8, "in"), margin = margin(b = 10)))
  save_slide(p, "9_scorecard.png")
}

# ============================================================
# SLIDE 10  (text card)
# ============================================================
make_textcard <- function() {
  body <- paste0(
    "<span style='font-size:40pt;color:", ink, "'>",
    "<b style='color:", amber, "'>92%</b> of evangelicals confess<br>",
    "one God in three persons.<br><br>",
    "<b style='color:", teal, "'>61%</b> say Jesus was created.<br>",
    "<b style='color:", teal, "'>55%</b> say the Spirit is a force.<br>",
    "<b style='color:", teal, "'>44%</b> say Jesus is not God.",
    "</span><br><br><br><br>",
    "<span style='font-size:28pt;color:", ink, "'>",
    "Some of the most vocal evangelical<br>",
    "apologists spend their time telling other<br>",
    "traditions they've departed from historic<br>",
    "Christianity. This is what that accusation<br>",
    "looks like turned around.<br><br><br>",
    "No tradition's members hold its teaching<br>",
    "perfectly. Matthew 7 tells us what to do<br>",
    "about that: the beam in our own eye before<br>",
    "the mote in our brother's.",
    "</span>")

  p <- ggplot() +
    geom_richtext(aes(x = 0, y = 1, label = body), hjust = 0, vjust = 1,
                  family = "Roboto Condensed", lineheight = 1.55,
                  fill = NA, label.colour = NA, label.padding = unit(0, "pt")) +
    scale_x_continuous(limits = c(0, 1)) + scale_y_continuous(limits = c(0, 1)) +
    labs(title = "Words without weight", caption = SRC) +
    theme_void(base_family = "Roboto Condensed") +
    theme(
      plot.background = element_rect(fill = paper, colour = NA),
      # Title moved up (margin(b=..) shrunk from 46 to 30) and the bigger
      # body text/wider paragraph gaps above fill the whitespace that used
      # to sit empty at the bottom of the canvas.
      plot.title = element_markdown(family = "Roboto Slab", face = "bold", size = 40,
                                    colour = ink, lineheight = 1.15,
                                    margin = margin(b = 30)),
      plot.caption = element_markdown(size = 16, colour = ink, hjust = 0,
                                      lineheight = 1.6, margin = margin(t = 40)),
      plot.title.position = "plot", plot.caption.position = "plot",
      plot.margin = margin(30, 40, 30, 40))
  save_slide(p, "10_thesis.png")
}

# ============================================================
make_hook <- function(file, big, lines, kicker = NULL) {
  body <- paste0(
    "<span style='font-size:96pt;color:", teal, "'><b>", big, "</b></span><br>",
    # Subtitle line ("lines") sized at roughly half the headline stat
    # (96pt / 2 = 48pt) per this rollout's explicit target — was 34pt.
    "<span style='font-size:48pt;color:", ink, "'>", lines, "</span>",
    if (!is.null(kicker))
      paste0("<br><br><br><span style='font-size:36pt;color:", ink, "'>", kicker, "</span>")
    else "")
  p <- ggplot() +
    geom_richtext(aes(x = 0, y = 1, label = body), hjust = 0, vjust = 1,
                  family = "Roboto Condensed", lineheight = 1.45,
                  fill = NA, label.colour = NA, label.padding = unit(0, "pt")) +
    scale_x_continuous(limits = c(0, 1)) + scale_y_continuous(limits = c(0, 1)) +
    labs(caption = SRC) +
    theme_void(base_family = "Roboto Condensed") +
    theme(plot.background = element_rect(fill = paper, colour = NA),
          plot.caption = element_markdown(size = 16, colour = ink, hjust = 0,
                                          lineheight = 1.6, margin = margin(t = 40)),
          plot.caption.position = "plot",
          plot.margin = margin(90, 40, 30, 40))
  save_slide(p, file)
}

make_hook("hook_a_created.png", "61%",
  "of American evangelicals<br>say Jesus was <b>created</b>.",
  "They also say they believe<br>in the Trinity.")

make_hook("hook_b_not_god.png", "44%",
  "of American evangelicals<br>say Jesus was <b>not God</b>.",
  "They also say they believe<br>in the Trinity.")

make_hook("hook_c_combined.png", "92%",
  paste0("of American evangelicals<br>say they believe in<br>the Trinity.<br><br>",
         "<span style='font-size:36pt;color:", ink, "'>",
         "<b style='color:", teal, "'>61%</b> say Jesus was created.<br>",
         "<b style='color:", teal, "'>44%</b> say Jesus was not God.<br>",
         "<b style='color:", teal, "'>55%</b> say the Spirit is a force.</span>"))

invisible(lapply(names(items), make_chart))
make_scorecard()
make_textcard()
cat("done\n")
