# ============================================================
# PREVIEW ONLY — not part of the regular build.
#
# Shows what a single-series (evangelicals only) version of one
# post1 slide would look like, per the request to see this before
# deciding whether to drop "All U.S. adults" from the whole script.
# Uses the "religions" item ("Many roads") because it's the slide
# whose point depends on the national comparison: evangelicals sit
# 16 points below "All U.S. adults" in 2025 (49% vs 65%).
#
# Not wired into post1_evangelical_trends.R's own run — this is a
# standalone, throwaway rendering of the same data/theme, run with
# `Rscript single_series_preview.R` from this folder.
# ============================================================
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tibble)
  library(forcats); library(ggtext); library(ragg); library(systemfonts)
})

this_file <- function() {
  a <- commandArgs(trailingOnly = FALSE)
  f <- sub("^--file=", "", a[grepl("^--file=", a)])
  if (length(f)) normalizePath(f) else normalizePath("single_series_preview.R")
}
SCRIPT_DIR <- dirname(this_file())
OUT <- file.path(SCRIPT_DIR, "png")
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)

ink <- "#1A1A1A"; paper <- "#FFFFFF"; muted <- "#6E6A63"; grid <- "#D9D5CC"
amber <- "#C9721C"

FONTS_DIR <- normalizePath(file.path(SCRIPT_DIR, "..", "..", "..",
                                      "state-of-theology-graphics", "fonts"))
register_font(name = "Roboto Condensed",
  plain = file.path(FONTS_DIR, "RobotoCondensed-Regular.ttf"),
  bold = file.path(FONTS_DIR, "RobotoCondensed-Bold.ttf"),
  italic = file.path(FONTS_DIR, "RobotoCondensed-Italic.ttf"),
  bolditalic = file.path(FONTS_DIR, "RobotoCondensed-BoldItalic.ttf"))
register_font(name = "Roboto Slab",
  plain = file.path(FONTS_DIR, "RobotoSlab-Bold.ttf"),
  bold = file.path(FONTS_DIR, "RobotoSlab-Bold.ttf"))

# Same numbers as the real "religions" item in post1_evangelical_trends.R —
# evangelicals-by-affiliation series only, "All U.S. adults" dropped.
d <- tribble(
  ~year, ~pct,
  2016, 49, 2018, 53, 2020, 46, 2022, 58, 2025, 49
)

ytop <- ceiling(max(d$pct) / 10) * 10
if (ytop - max(d$pct) < 5) ytop <- ytop + 10

p <- ggplot(d, aes(factor(year), pct)) +
  geom_col(fill = amber, width = .6) +
  geom_text(aes(label = paste0(pct, "%")), vjust = -.55, colour = amber,
            family = "Roboto Condensed", fontface = "bold", size = 8,
            show.legend = FALSE) +
  scale_y_continuous(limits = c(0, ytop), breaks = seq(0, ytop, 10),
                     labels = function(x) paste0(x, "%"),
                     expand = expansion(mult = c(0, .04))) +
  labs(title = "Many roads",
       subtitle = paste0(
         "<i>\"God accepts the worship of all religions, including<br>",
         "Christianity, Judaism, and Islam.\"</i><br>",
         "Share who <b>strongly agree or somewhat agree</b><br><br>",
         "<span style='color:", amber, "'><b>&#9632; Evangelicals by affiliation</b></span>"),
       caption = "Data: The State of Theology survey<br>@ithinkisam") +
  theme_minimal(base_family = "Roboto Condensed", base_size = 15) +
  theme(
    plot.background = element_rect(fill = paper, colour = NA),
    panel.background = element_rect(fill = paper, colour = NA),
    panel.grid.minor = element_blank(),
    panel.grid.major.x = element_blank(),
    panel.grid.major.y = element_line(colour = grid, linewidth = .4),
    plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                              size = 48, colour = ink, lineheight = 1.05,
                              width = unit(7.8, "in"), margin = margin(b = 10)),
    plot.subtitle = element_markdown(size = 16, colour = muted, lineheight = 1.4,
                                     margin = margin(b = 22)),
    plot.caption = element_markdown(size = 11.5, colour = muted, hjust = 0,
                                    lineheight = 1.6, margin = margin(t = 20)),
    plot.caption.position = "plot", plot.title.position = "plot",
    axis.title = element_blank(), legend.position = "none",
    axis.text.x = element_text(size = 17, colour = ink, face = "bold", margin = margin(t = 6)),
    axis.text.y = element_text(size = 12.5, colour = muted),
    plot.margin = margin(28, 30, 20, 28))

ggsave(file.path(OUT, "PREVIEW_single_series_religions.png"), p, device = ragg::agg_png,
       width = 9, height = 11.25, dpi = 120, bg = paper)
cat("done\n")
