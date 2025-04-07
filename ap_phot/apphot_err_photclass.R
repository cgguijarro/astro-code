# sky background and its standard deviation for empty apertures - PHOTOMETRY CLASS VERSION

library(FITSio)
library(genefilter)
library(MASS)

args <- commandArgs(trailingOnly=TRUE) # fetch command line arguments
data <- read.table(args[1], header = FALSE) # opening the table
scidata <- data$V1 # opening the data

sky.mode <- half.range.mode(scidata[!is.na(scidata)], beta = 0.5) # sky mode calculated using the half-range method
sky.dist <- c(scidata[which(scidata<sky.mode)], -scidata[which(scidata<sky.mode)] + 2*sky.mode) # sky distribution
output <- fitdistr(sky.dist,"normal") # fit the sky distribution to normal
cat(output$estimate[1], output$estimate[2]) # output bkg and sigma of the bkg