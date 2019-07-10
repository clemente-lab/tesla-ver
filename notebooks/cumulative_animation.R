# set working directory to the directory of current script

install.packages("rstudioapi")
library(rstudioapi)

# the following line is for getting the path of your current open file
current_path <- getActiveDocumentContext()$path 

# The next line set the working directory to the relevant one:
setwd(dirname(current_path ))

install.packages("plotly")

Sys.setenv("plotly_username"="willntsre")
Sys.setenv("plotly_api_key"="NBMD9KWspCE2lmJ5g2hx")

library(plotly)

mydata = read.delim(file = "../data/WB_birth_rate_raw_clustered_short.csv", header=TRUE, sep="\t")
read.delim(file = "../data/WB_birth_rate_raw_clustered_short.csv", header=TRUE, sep="\t")

accumulate_by <- function(dat, var) {
  var <- lazyeval::f_eval(var, dat)
  lvls <- plotly:::getLevels(var)
  dats <- lapply(seq_along(lvls), function(x) {
    cbind(dat[var %in% lvls[seq(1, x)], ], frame = lvls[[x]])
  })
  dplyr::bind_rows(dats)
}

myvars <- c("Short.Name", "X", "Y")
newdata <- mydata[myvars]

newdata[,'X'] <- as.character(newdata[,'X'])
newdata[,'Y'] <- as.character(newdata[,'Y'])

s <- strsplit(newdata$X, split = ",")
r <- strsplit(newdata$Y, split = ",")

final_data <- data.frame(Short.Name = rep(newdata$Short.Name, sapply(s, length)), X = unlist(s), Y = unlist(r))

final_data$X = as.numeric(as.character(final_data$X))
final_data$X

options(digits=5)
final_data$Y = as.numeric(as.character(final_data$Y))

final_data

final_data <- final_data[order(final_data$X),]


final_data

rownames(final_data) <- 1:nrow(final_data)

d <- final_data %>%
  accumulate_by(~X)
d

p <- d %>%
  plot_ly(
    x = ~X, 
    y = ~Y,
    split = ~Short.Name,
    frame = ~frame, 
    type = 'scatter',
    mode = 'lines', 
    line = list(simplyfy = F)
  ) %>% 
  layout(
    xaxis = list(
      title = "Year",
      zeroline = F
    ),
    yaxis = list(
      title = "Median",
      zeroline = F
    )
  ) %>% 
  animation_opts(
    frame = 100, 
    transition = 0, 
    redraw = FALSE
  ) %>%
  animation_slider(
    currentvalue = list(
      prefix = "Day "
    )
  )

# This shorter version also works
# p <- plot_ly(d,
#   x = ~X, 
#   y = ~Y,
#   split = ~Short.Name,
#   frame = ~frame, 
#   type = 'scatter',
#   mode = 'lines', 
#   line = list(simplyfy = F)
# )

# Create a shareable link to your chart
# Set up API credentials: https://plot.ly/r/getting-started
chart_link = api_create(p, filename="birth_rates_full")
chart_link
