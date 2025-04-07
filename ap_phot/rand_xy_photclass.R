# random selection of coordinates in a XY plane - PHOTOMETRY CLASS VERSION

options(digits=6) # print function displays up to 6 digits

args <- commandArgs(trailingOnly=TRUE) # fetch command line arguments
args <- as.numeric(args) # convert to numerics
num <- 10000 # number of random positions to be generated
min.x <- args[1] # minimum value of X
max.x <- args[2] # maximum value of X
min.y <- args[3] # maximum value of Y
max.y <- args[4] # maximum value of Y
radius <- args[5] # aperture radius (pix)
OUTPUT <- "rand_xy.txt" # output table name

x <- runif(num, min.x+radius, max.x-radius) # X coordinate
y <- runif(num, min.y+radius, max.y-radius) # Y coordinate
xy <- data.frame(x,y)

write.table(file = OUTPUT, xy, col.names=FALSE, row.names=FALSE) # writing to output file