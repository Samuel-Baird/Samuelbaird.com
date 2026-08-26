# ============================================================
# State of Theology — comparison by religious tradition
# 2025 wave unless noted.  @ithinkisam
# Output 1080 x 1350 (4:5) via ragg + system fonts.
# ============================================================
suppressPackageStartupMessages({
  library(ggplot2); library(dplyr); library(tibble)
  library(forcats); library(ggtext); library(ragg)
})

OUT <- "/mnt/user-data/outputs/post2"
dir.create(OUT, showWarnings = FALSE)

ink <- "#1A1A1A"; paper <- "#F7F5F0"; grid <- "#D9D5CC"; muted <- "#6E6A63"
amber <- "#C9721C"   # Evangelical      (unchanged)
teal  <- "#2C7B8C"   # All U.S. adults  (unchanged)
wine  <- "#8C4A5F"   # Roman Catholic
moss  <- "#5B7553"   # Black Protestant
slate <- "#4E5D80"   # Mainline
gray  <- "#8E8B84"   # Other

GROUPS <- c("Evangelical", "Black Protestant", "Mainline",
            "Roman Catholic", "Other", "All U.S. adults")
pal <- c("Evangelical" = amber, "Black Protestant" = moss, "Mainline" = slate,
         "Roman Catholic" = wine, "Other" = gray, "All U.S. adults" = teal)

# ---- data: item, group, pct --------------------------------
d <- tribble(
  ~item,      ~group,             ~pct,
  # Trinity ------------------------------------------------
  "trinity","Evangelical",95, "trinity","Black Protestant",92, "trinity","Mainline",89,
  "trinity","Roman Catholic",89, "trinity","Other",45,          "trinity","All U.S. adults",71,
  # Arianism (2022) ----------------------------------------
  "arian",  "Evangelical",61, "arian",  "Black Protestant",78, "arian",  "Mainline",61,
  "arian",  "Roman Catholic",71, "arian",  "Other",41,          "arian",  "All U.S. adults",55,
  # Religious pluralism ------------------------------------
  "relig",  "Evangelical",49, "relig",  "Black Protestant",81, "relig",  "Mainline",80,
  "relig",  "Roman Catholic",88, "relig",  "Other",59,          "relig",  "All U.S. adults",65,
  # Deity of Christ ----------------------------------------
  "teach",  "Evangelical",34, "teach",  "Black Protestant",55, "teach",  "Mainline",52,
  "teach",  "Roman Catholic",50,"teach",  "Other",56,          "teach",  "All U.S. adults",49,
  # Holy Spirit --------------------------------------------
  "spirit", "Evangelical",52, "spirit", "Black Protestant",65, "spirit", "Mainline",73,
  "spirit", "Roman Catholic",68, "spirit", "Other",52,          "spirit", "All U.S. adults",57,
  # Human nature -------------------------------------------
  "nature", "Evangelical",55, "nature", "Black Protestant",71, "nature", "Mainline",81,
  "nature", "Roman Catholic",82, "nature", "Other",63,          "nature", "All U.S. adults",66,
  # Abortion -----------------------------------------------
  "abort",  "Evangelical",73, "abort",  "Black Protestant",63, "abort",  "Mainline",50,
  "abort",  "Roman Catholic",55, "abort",  "Other",32,          "abort",  "All U.S. adults",49,
  # Biblical authority on sexuality (disagree) -------------
  "homo",   "Evangelical",74, "homo",   "Black Protestant",52, "homo",   "Mainline",50,
  "homo",   "Roman Catholic",41, "homo",   "Other",31,          "homo",   "All U.S. adults",46,
  # Sex outside marriage -----------------------------------
  "sex",    "Evangelical",82, "sex",    "Black Protestant",73, "sex",    "Mainline",55,
  "sex",    "Roman Catholic",49, "sex",    "Other",34,          "sex",    "All U.S. adults",52,
  # Gender (disagree) --------------------------------------
  "gender", "Evangelical",77, "gender", "Black Protestant",65, "gender", "Mainline",61,
  "gender", "Roman Catholic",53, "gender", "Other",39,          "gender", "All U.S. adults",54
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

SRC <- paste0(
  "<b>The State of Theology survey</b> &#183; sponsored by Ligonier Ministries, ",
  "conducted by Lifeway Research<br>",
  "Groups are religious tradition (denomination and church association).<br>",
  "National online panel &#183; 3,001 U.S. adults &#183; margin of error &#177;1.9%<br>",
  "<span style='color:", amber, "'><b>@ithinkisam</b></span>")

make <- function(k) {
  it <- items[[k]]
  dd <- filter(d, item == k)
  xtop <- ceiling(max(dd$pct)/10)*10; if (xtop - max(dd$pct) < 6) xtop <- xtop + 10

  p <- ggplot(dd, aes(pct, group, fill = group)) +
    geom_col(width = .70) +
    geom_text(aes(label = paste0(pct, "%"), colour = group), hjust = -0.22,
              family = "Roboto Condensed", fontface = "bold", size = 8.5,
              show.legend = FALSE) +
    scale_fill_manual(values = pal) + scale_colour_manual(values = pal) +
    scale_x_continuous(limits = c(0, xtop * 1.14), expand = expansion(mult = c(0, 0))) +
    labs(title = it$title,
         subtitle = paste0("<i>\"", it$quote, "\"</i><br>Share who <b>strongly ",
                           it$dir, " or somewhat ", it$dir, "</b>, ", it$year),
         caption = SRC) +
    theme_minimal(base_family = "Roboto Condensed", base_size = 15) +
    theme(
      plot.background = element_rect(fill = paper, colour = NA),
      panel.background = element_rect(fill = paper, colour = NA),
      panel.grid = element_blank(),
      plot.title = element_textbox_simple(family = "Roboto Slab", face = "bold",
                                size = 34, colour = ink, lineheight = 1.1,
                                width = unit(8.1, "in"), margin = margin(b = 8)),
      plot.subtitle = element_markdown(size = 16, colour = muted, lineheight = 1.4,
                                       margin = margin(b = 34)),
      plot.caption = element_markdown(size = 11.5, colour = muted, hjust = 0,
                                      lineheight = 1.6, margin = margin(t = 34)),
      plot.title.position = "plot", plot.caption.position = "plot",
      axis.title = element_blank(), axis.text.x = element_blank(),
      axis.text.y = element_text(size = 20, colour = ink, hjust = 1, face = "bold"),
      legend.position = "none",
      plot.margin = margin(28, 30, 20, 28))
  ggsave(file.path(OUT, it$file), p, device = ragg::agg_png,
         width = 9, height = 11.25, dpi = 120, bg = paper)
}
card <- function(file, title, body) {
  p <- ggplot() +
    geom_richtext(aes(x = 0, y = 1, label = body), hjust = 0, vjust = 1,
                  family = "Roboto Condensed", lineheight = 1.5,
                  fill = NA, label.colour = NA, label.padding = unit(0, "pt")) +
    scale_x_continuous(limits = c(0,1)) + scale_y_continuous(limits = c(0,1)) +
    labs(title = title, caption = SRC) +
    theme_void(base_family = "Roboto Condensed") +
    theme(plot.background = element_rect(fill = paper, colour = NA),
          plot.title = element_markdown(family = "Roboto Slab", face = "bold", size = 46,
                                        colour = ink, lineheight = 1.15,
                                        margin = margin(b = 46)),
          plot.caption = element_markdown(size = 11.5, colour = muted, hjust = 0,
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

card("11_closing.png", "Still the beam", paste0(
  "<span style='font-size:26pt;color:", ink, "'>",
  "Across the four Christian traditions here:<br><br>",
  "<b>89&#8211;95%</b> confess the Trinity.<br>",
  "<b style='color:", wine, "'>61&#8211;78%</b> say Jesus was created.<br>",
  "<b style='color:", wine, "'>52&#8211;73%</b> say the Spirit is not a person.<br>",
  "<b style='color:", wine, "'>34&#8211;55%</b> say Jesus was not God.",
  "</span><br><br><br>",
  "<span style='font-size:19pt;color:", muted, "'>",
  "Last week the numbers made evangelicals look bad. This week<br>",
  "they&#8217;re the best in the country, and it still isn&#8217;t good.<br><br>",
  "The tradition with the strictest catechism and the tradition with<br>",
  "none at all fail the same way. No one in this survey is positioned<br>",
  "to correct anyone else before working on themselves.",
  "</span>"))

invisible(lapply(names(items), make))
cat("done\n")
