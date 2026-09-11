# ============================================================
# State of Theology — comparison by religious tradition
# 2025 wave unless noted.  @ithinkisam
# Output 1080 x 1350 (4:5) via ragg. Fonts are self-hosted from
# this repo's Data Explorer chart pipeline
# (scripts/state-of-theology-graphics/fonts/), not assumed to
# be installed on the OS — see "FONTS" below.
# ============================================================
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tibble)
  library(forcats); library(ggtext); library(ragg); library(systemfonts)
})

# ------------------------------------------------------------
# Where this file lives, so paths below work no matter the cwd
# `Rscript post2_tradition_comparison.R` is run from.
# ------------------------------------------------------------
this_file <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) normalizePath(f) else normalizePath("post2_tradition_comparison.R")
}
SCRIPT_DIR <- dirname(this_file())
OUT <- file.path(SCRIPT_DIR, "png")
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

# ============================================================
# DESIGN TOKENS — pulled from the Data Explorer chart pipeline,
# not invented for this post. Canonical source:
# scripts/state-of-theology-graphics/render_chart.py (this repo's
# Python renderer for the same State of Theology survey — same
# 1080x1350 canvas, same fonts, same five-group PALETTE) and
# scripts/chart_style.py.
# ============================================================
ink   <- "#1A1A1A"  # render_chart.py INK   — titles, axis/value labels
paper <- "#FFFFFF"  # render_chart.py PAPER — canvas background. The explorer
                     # deliberately uses pure white here, not the Instagram
                     # scripts' old cream (#F7F5F0) — see that file's own
                     # "Paper is pure white here, deliberately different from
                     # the Instagram scripts' cream" comment.
muted <- "#6E6A63"  # render_chart.py MUTED — subtitle/caption/secondary text
grid  <- "#D9D5CC"  # render_chart.py GRID (== chart_style.py BORDER) — gridlines

# Categorical series palette, in render_chart.py's PALETTE order — only the
# four groups this post keeps (see "Remove two groups" below; "Other" and
# "All U.S. adults" dropped their PALETTE entries here since nothing uses
# them anymore).
amber <- "#C9721C"  # PALETTE["Evangelical"]
moss  <- "#5B7553"  # PALETTE["Black Protestant"]
slate <- "#4E5D80"  # PALETTE["Mainline"]
wine  <- "#8C4A5F"  # PALETTE["Roman Catholic"]

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

# Remove two groups: "Other" and "All U.S. adults" are gone from both the
# data and the palette below — four bars per chart, Evangelical/Black
# Protestant/Mainline/Roman Catholic, in the order the design tokens above
# are listed in.
GROUPS <- c("Evangelical", "Black Protestant", "Mainline", "Roman Catholic")
pal <- c("Evangelical" = amber, "Black Protestant" = moss, "Mainline" = slate,
         "Roman Catholic" = wine)

# ---- data: item, group, pct --------------------------------
d <- tribble(
  ~item,      ~group,             ~pct,
  # Trinity ------------------------------------------------
  "trinity","Evangelical",95, "trinity","Black Protestant",92, "trinity","Mainline",89,
  "trinity","Roman Catholic",89,
  # Arianism (2022) ----------------------------------------
  "arian",  "Evangelical",61, "arian",  "Black Protestant",78, "arian",  "Mainline",61,
  "arian",  "Roman Catholic",71,
  # Religious pluralism ------------------------------------
  "relig",  "Evangelical",49, "relig",  "Black Protestant",81, "relig",  "Mainline",80,
  "relig",  "Roman Catholic",88,
  # Deity of Christ ----------------------------------------
  "teach",  "Evangelical",34, "teach",  "Black Protestant",55, "teach",  "Mainline",52,
  "teach",  "Roman Catholic",50,
  # Holy Spirit --------------------------------------------
  "spirit", "Evangelical",52, "spirit", "Black Protestant",65, "spirit", "Mainline",73,
  "spirit", "Roman Catholic",68,
  # Human nature -------------------------------------------
  "nature", "Evangelical",55, "nature", "Black Protestant",71, "nature", "Mainline",81,
  "nature", "Roman Catholic",82,
  # Abortion -----------------------------------------------
  "abort",  "Evangelical",73, "abort",  "Black Protestant",63, "abort",  "Mainline",50,
  "abort",  "Roman Catholic",55,
  # Biblical authority on sexuality (disagree) -------------
  "homo",   "Evangelical",74, "homo",   "Black Protestant",52, "homo",   "Mainline",50,
  "homo",   "Roman Catholic",41,
  # Sex outside marriage -----------------------------------
  "sex",    "Evangelical",82, "sex",    "Black Protestant",73, "sex",    "Mainline",55,
  "sex",    "Roman Catholic",49,
  # Gender (disagree) --------------------------------------
  "gender", "Evangelical",77, "gender", "Black Protestant",65, "gender", "Mainline",61,
  "gender", "Roman Catholic",53
) |> mutate(group = fct_rev(factor(group, levels = GROUPS)))

items <- list(
  trinity = list(file="1_trinity.png",  title="Nearly everyone confesses it",
    quote="There is one true God in three persons: God the Father,<br>God the Son, and God the Holy Spirit.", dir="agree", year="2025"),
  arian   = list(file="2_arian.png",    title="A majority also deny the Trinity",
    quote="Jesus is the first and greatest being created by God.", dir="agree", year="2022"),
  teach   = list(file="3_teacher.png", title="In most traditions, half say he isn't God",
    quote="Jesus was a great teacher, but he was not God.", dir="agree", year="2025"),
  spirit  = list(file="4_spirit.png",   title="Surprisingly binitarian",
    quote="The Holy Spirit is a force but is not a personal being.", dir="agree", year="2025"),
  relig   = list(file="5_relig.png",    title="Most say God accepts every religion",
    quote="God accepts the worship of all religions, including<br>Christianity, Judaism, and Islam.", dir="agree", year="2025"),
  nature  = list(file="6_nature.png",   title="Pelagius, still at large",
    quote="Everyone sins a little, but most people are good by nature.", dir="agree", year="2025"),
  abort   = list(file="7_abortion.png", title="Abortion is a sin",
    quote="Abortion is a sin.", dir="agree", year="2025"),
  sex     = list(file="8_sex.png",      title="Sex outside traditional marriage",
    quote="Sex outside of traditional marriage is a sin.", dir="agree", year="2025"),
  homo    = list(file="9_homo.png",     title="Biblical authority on sexuality",
    quote="The Bible's condemnation of homosexual behavior<br>doesn't apply today.", dir="disagree", year="2025"),
  gender  = list(file="10_gender.png",   title="Most reject choosing one's gender",
    quote="People should be able to choose their gender<br>regardless of their biological sex.", dir="disagree", year="2025")
)

# Footnote: handle only, muted, small — no sponsor/fielder/method/panel-size/
# margin-of-error block, no per-slide notes.
SRC <- paste0(
  "Data: The State of Theology survey<br>",
  "@ithinkisam")

make <- function(k) {
  it <- items[[k]]
  dd <- filter(d, item == k)
  xtop <- ceiling(max(dd$pct)/10)*10; if (xtop - max(dd$pct) < 6) xtop <- xtop + 10

  # Title IS the survey statement (see "Titles: accurate, not editorial"
  # in scripts/state-of-theology-graphics/STYLE.md) — no separate quote
  # line in the subtitle duplicating it. Manual <br> breaks in `quote`
  # were tuned for the old subtitle placement; strip them and let
  # element_textbox_simple's own auto-wrap handle the title box.
  title_text <- paste0("“", gsub("<br>", " ", it$quote), "”")
  title_size <- if (nchar(title_text) > 95) 34 else if (nchar(title_text) > 65) 40 else 48

  p <- ggplot(dd, aes(pct, group, fill = group)) +
    geom_col(width = .70) +
    geom_text(aes(label = paste0(pct, "%"), colour = group), hjust = -0.22,
              family = "Roboto Condensed", fontface = "bold", size = 8.5,
              show.legend = FALSE) +
    scale_fill_manual(values = pal) + scale_colour_manual(values = pal) +
    scale_x_continuous(limits = c(0, xtop * 1.14), expand = expansion(mult = c(0, 0))) +
    labs(title = title_text,
         subtitle = paste0("Share who <b>strongly ", it$dir, " or somewhat ", it$dir,
                           "</b>, ", it$year),
         caption = SRC) +
    theme_minimal(base_family = "Roboto Condensed", base_size = 15) +
    theme(
      plot.background = element_rect(fill = paper, colour = NA),
      panel.background = element_rect(fill = paper, colour = NA),
      panel.grid = element_blank(),
      # Wrap width trimmed from 8.1in so the wider glyphs at the largest
      # size still clear the canvas's right margin; `title_size` above
      # steps down for a long quoted statement so it wraps to at most a
      # few lines instead of crowding the chart below it.
      plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                                size = title_size, colour = ink, lineheight = 1.05,
                                width = unit(7.8, "in"), margin = margin(b = 10)),
      plot.subtitle = element_markdown(size = 18, colour = muted, lineheight = 1.4,
                                       margin = margin(b = 34)),
      plot.caption = element_markdown(size = 16, colour = ink, hjust = 0,
                                      lineheight = 1.6, margin = margin(t = 34)),
      plot.title.position = "plot", plot.caption.position = "plot",
      axis.title = element_blank(), axis.text.x = element_blank(),
      # 20 -> 24pt (MIN.LEGEND): matches the site-wide convention that
      # y-axis group/identity labels render at the same size as a chart
      # legend key — see state-of-theology-graphics/STYLE.md's
      # "At-a-glance legibility and mobile floors".
      axis.text.y = element_text(size = 24, colour = ink, hjust = 1, face = "bold"),
      legend.position = "none",
      plot.margin = margin(28, 30, 20, 28))
  ggsave(file.path(OUT, it$file), p, device = ragg::agg_png,
         width = 9, height = 11.25, dpi = 120, bg = paper)
}
card <- function(file, title, body, caption_override = NULL) {
  p <- ggplot() +
    geom_richtext(aes(x = 0, y = 1, label = body), hjust = 0, vjust = 1,
                  family = "Roboto Condensed", lineheight = 1.5,
                  fill = NA, label.colour = NA, label.padding = unit(0, "pt")) +
    scale_x_continuous(limits = c(0,1)) + scale_y_continuous(limits = c(0,1)) +
    labs(title = title, caption = if (is.null(caption_override)) SRC else caption_override) +
    theme_void(base_family = "Roboto Condensed") +
    theme(plot.background = element_rect(fill = paper, colour = NA),
          plot.title = element_markdown(family = "Roboto Slab", face = "bold", size = 48,
                                        colour = ink, lineheight = 1.15,
                                        margin = margin(b = 46)),
          plot.caption = element_markdown(size = 16, colour = ink, hjust = 0,
                                          lineheight = 1.6, margin = margin(t = 40)),
          plot.title.position = "plot", plot.caption.position = "plot",
          plot.margin = margin(60, 40, 30, 40))
  ggsave(file.path(OUT, file), p, device = ragg::agg_png,
         width = 9, height = 11.25, dpi = 120, bg = paper)
}

card("0_intro.png", "Evangelicals won", paste0(
  "<span style='font-size:27pt;color:", ink, "'>",
  "Last week&#8217;s numbers looked bad.<br><br>",
  "Compared to every other Christian<br>",
  "tradition in the survey, they are<br>",
  "the strongest in the country.",
  "</span>"))

card("11_closing.png", paste0(
  "<span style='font-size:52pt'>Still the beam</span>"), paste0(
  "<span style='font-size:30pt;color:", ink, "'>",
  "Across the four Christian traditions here:<br><br>",
  "<b>89&#8211;95%</b> confess the Trinity.<br>",
  "<b style='color:", wine, "'>61&#8211;78%</b> say Jesus was created.<br>",
  "<b style='color:", wine, "'>52&#8211;73%</b> say the Spirit is not a person.<br>",
  "<b style='color:", wine, "'>34&#8211;55%</b> say Jesus was not God.",
  "</span><br><br><br>",
  "<span style='font-size:22pt;color:", ink, "'>",
  "Last week the numbers made evangelicals look bad. This<br>",
  "week they&#8217;re the best in the country, and it still isn&#8217;t good.<br><br>",
  "The tradition with the strictest catechism and the<br>",
  "tradition with none at all fail the same way. No one in<br>",
  "this survey is positioned to correct anyone else before<br>",
  "working on themselves.",
  "</span>"),
  caption_override = paste0("<span style='font-size:16pt;color:", ink, "'>", SRC, "</span>"))

invisible(lapply(names(items), make))
cat("done\n")
