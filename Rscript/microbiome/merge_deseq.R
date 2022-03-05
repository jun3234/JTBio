#!/usr/bin/env Rscript
# Title     : merge_deseq.r
# Author    : JuntingFeng
# Email     : 651407541@qq.com
# Created by: 65140
# Created on: 2022/1/26

#load the packages
library("argparse")

#parser the parameters
parser <- ArgumentParser(description='plot beta diversity heatmap')
parser$add_argument( "-c", "--csv", type="character",required=T,
    help="input deseq2 output table,[required]",
    metavar="filepath")
parser$add_argument( "-s", "--sample_metadata", type="character",required=T,
    help="input sample-metadata file path,[required]",
    metavar="filepath")
parser$add_argument( "-t", "--rarefy_table_with_taxonomy", type="character",required=T,
    help="input rarefy count table file path,[required]",
    metavar="filepath")
parser$add_argument( "-o", "--order", type="character",nargs='+',required=F,
    help="input order, table column will order according the id [required]",
    metavar="group")
parser$add_argument( "-d", "--outdir", type="character", default=getwd(),
    help="output file directory [default cwd]",
    metavar="path")

#collect the parameter, otherwise print help
result <- tryCatch(
    { opt <- parser$parse_args() },
    warning = function(w) { parser$print_help(); quit() },
    error = function(e) { parser$print_help(); quit() },
    finally = { }
)

#check output dir, otherwise create the one
if( !file.exists(opt$outdir) ){
    if( !dir.create(opt$outdir, showWarnings = FALSE, recursive = TRUE) ){
        stop(paste("dir.create failed: outdir=",opt$outdir,sep=""))
    }
}


#read table
dif_csv <- read.csv(opt$csv, header=T)
rarefy_table <- read.table(opt$rarefy_table_with_taxonomy, skip=1, header=T, sep="\t", comment.char = "")
sample_metadata <- read.table(opt$sample_metadata, header=T, sep="\t")

# merge dif_csv and rarefy_table
rarefy_table_subset <- rarefy_table[match(dif_csv$X, rarefy_table$X.OTU.ID),]
mer1 <- cbind(dif_csv, rarefy_table_subset)

# order rarefy_table column according treat
order_sample <- sample_metadata[order(sample_metadata[, opt$order]),]
# only sort columns in mer1 according order_sample's sample.id
mer1_names <- colnames(mer1)
having_col_sort_acc_metadata <- na.omit(mer1_names[match(order_sample$sample.id, mer1_names)])
new_mer1_names <- c(mer1_names[1:8], having_col_sort_acc_metadata, mer1_names[length(mer1_names)])
new_mer1 <- mer1[, new_mer1_names]

# merge sample_metadata in new_mer1
order_sample_subset <- order_sample[order_sample$sample.id %in% having_col_sort_acc_metadata, ]
num <- nrow(t(order_sample_subset))
tmp <- as.data.frame(matrix(rep("NA", 8*num), ncol=8, nrow=num))
header <- cbind(tmp,t(order_sample_subset), A=tmp[,1])

# write csv data
rfname <- substr(opt$csv, 1, (nchar(opt$csv) - 4))
write.table(header, paste0(opt$outdir, "/", rfname, "_composite.csv" ),
            sep=",", col.names=FALSE, row.names=FALSE, quote=FALSE)
write.table(new_mer1, paste0(opt$outdir, "/", rfname, "_composite.csv" ),
            append=TRUE, sep=",", col.names=TRUE, row.names=FALSE, quote=FALSE)