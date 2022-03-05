#!/usr/bin/env Rscript
initial.options <- commandArgs(trailingOnly = FALSE)
file.arg.name <- "--file="
script.name <- sub(file.arg.name, "", initial.options[grep(file.arg.name, initial.options)])
script.basename <- dirname(script.name)
other.name <- paste(sep="/", script.basename, script.name)


argv <- commandArgs(TRUE)
if(length(argv)<2){
  print("[Usage]:",quote=F)
  print(paste0("        Rscript ",other.name," step1 "," PC proportion bred"),quote=F)
  print("The first two parameters are required.")
  q(save="no")
}

## map argv to file
fpref=argv[1];
PC=argv[2];
prop=argv[3];
bred=argv[4];

# parameters
froot <- paste(getwd(), "/step1", sep = "") #当前路径
PC = as.integer(PC) #输入的初始PCA的数量
proportion = ifelse(!is.na(prop), prop, 0.6)
bred = ifelse(!is.na(bred), "inbred", "outbred")

# Load packages ----
library(shiny)
library(bsplus)

# Source helpers ----
source('/home/smrtanalysis/JTBio/Rscript/EigenGWAS_Friends.R')

# read table
nn<-nrow(read.table(paste0(froot, ".fam"), as.is = T, header = F, colClasses = c("character","NULL","NULL","NULL","NULL","NULL")))
mm<-nrow(read.table(paste0(froot,'.bim'), as.is = T, header=F, colClasses = c("character","NULL","NULL","NULL","NULL","NULL")))

# EigenGWAS
print(" collecting MAF info  ... ")
fq=read.table(paste0(froot, ".frq"), as.is = T, header = T)

print(" collecting PCA info ... ")
evalF=read.table(paste0(froot, ".eigenval"), as.is = T)
pcF=read.table(paste0(froot, ".eigenvec"), as.is = T)
evalF = as.numeric(evalF[,1])
names(evalF) = c(1:PC)

print(" collecting GRM info ... ")
gz=gzfile(paste0(froot, ".grm.gz"))
grm=read.table(gz, as.is = T)
diagnol = grm[grm[,1]==grm[,2],4]
off_diagnol = grm[grm[,1]!=grm[,2], 4]
sc=ifelse(bred == 'inbred', 2, 1)
Ne=-1/mean(off_diagnol/sc)
Me=1/var(off_diagnol/sc)

print(" collecting Eigenscan info ... ")
GC = array(0, dim=PC)
tophit = data.frame()
for (i in 1:PC){
  eg = read.table(paste0(froot, "_pca", i, ".assoc.linear"), as.is = T, header = T, colClasses = c("numeric","character","numeric","NULL","NULL","NULL","NULL","numeric","numeric"))
  GC[i] = qchisq(median(eg$P, na.rm = T), 1, lower.tail = F)/qchisq(0.5, 1, lower.tail = F)

  eg = eg[which(!is.na(eg$P)),]
  eg$Praw = eg$P
  gc = GC[i]
  eg$P = pchisq((eg$STAT)^2/gc, 1, lower.tail = F)
  eg = eg[which(!is.na(eg$P)),]
  assign(paste0("EgResDT",i),eg)

  eg_sig = eg[eg$P<=0.05,]
  eg_no_sig = eg[eg$P>0.05,]
  eg_com = rbind(eg_sig,eg_no_sig[sample(1:nrow(eg_no_sig),0.6*nrow(eg_no_sig)),])
  assign(paste0("EgResPlot",i),eg_com)

  eg$Espace = rep(i,dim(eg)[1])
  tophit = rbind(tophit, eg[order(eg$P),][c(1:10),c("Espace","CHR","SNP","BP","P","Praw")])
}
tophit[,c(5,6)] = format(tophit[,c(5,6)],digits = 4)

egc=matrix(c(evalF[1:PC]/sc, GC), PC, 2, byrow = F)
rownames(egc)=seq(1, PC)
print(" Analysis complete. ")

##Output
print(paste0("Minor allele frequencies for the ", mm," markers included for analysis."))
png(filename = paste0(getwd(),'/MAF','.png'),width = 480,height = 480)
hist(fq$MAF, main="Minor allele frequency", xlab="MAF", xlim=c(0, 0.5), breaks = 50)
dev.off()


#output top three pca
print("Plot the first three pca...")
png(filename = paste0(getwd(),'/PCA','.png'),width = 960,height = 960,res = 120)
layout(matrix(c(1,2,3,4), 2,2))
barplot(evalF/sc, border = F, main="Eigenvalue",ylim = c(0,max(evalF/sc)*1.2),xlab = 'Eigenspace')
abline(h=1, lty=2, col="black")
#pca,1vs2
input_pcx = 1; input_pcy = 2
plot(main=paste0("Eigen space ", input_pcx, " vs ", input_pcy), pcF[,input_pcx+2], pcF[,input_pcy+2], xlab=paste0("Eigen space ", input_pcx), 
     ylab=paste0("Eigen space ", input_pcy), bty='n', pch=16, cex=0.8, col=ifelse(pcF[,input_pcx+2]<0, "red", "blue"))
abline(v=0, h=0, col="grey", lty=2)
#pca,1vs3
input_pcx = 1; input_pcy = 3
plot(main=paste0("Eigen space ", input_pcx, " vs ", input_pcy), pcF[,input_pcx+2], pcF[,input_pcy+2], xlab=paste0("Eigen space ", input_pcx), 
     ylab=paste0("Eigen space ", input_pcy), bty='n', pch=16, cex=0.8, col=ifelse(pcF[,input_pcx+2]<0, "red", "blue"))
abline(v=0, h=0, col="grey", lty=2)
#pca,2vs3
input_pcx = 2; input_pcy = 3
plot(main=paste0("Eigen space ", input_pcx, " vs ", input_pcy), pcF[,input_pcx+2], pcF[,input_pcy+2], xlab=paste0("Eigen space ", input_pcx), 
     ylab=paste0("Eigen space ", input_pcy), bty='n', pch=16, cex=0.8, col=ifelse(pcF[,input_pcx+2]<0, "red", "blue"))
abline(v=0, h=0, col="grey", lty=2)
dev.off()


##output grm
print("Plot the grm...")
png(filename = paste0(getwd(),'/grm','.png'),width = 960,height = 480,res = 120)
layout(matrix(1:2, 1, 2))
hist(off_diagnol/sc, main="Pairwise relatedness", xlab="Relatedness score", breaks = 50,freq = F)
x=seq(range(off_diagnol/sc)[1],range(off_diagnol/sc)[2],length.out = 100)
y=dnorm(x,-1/nn,sqrt(1/Me))
lines(x,y,col="red",lwd=2)
##
Ne=format(Ne, digits=3, nsmall=2)
Me=format(Me, digits=3, nsmall=2)
legen1 = bquote(italic(n)[e]==.(Ne)(.(nn)))
legen2 = bquote(italic(m)[e]==.(Me)(.(mm)))
legend("topright", legend = c(as.expression(legen1), as.expression(legen2)),bty ='n')
hist(diagnol/sc, main="Self-relatedness", xlab="Relatedness score", breaks = 15)
dev.off()


##Eigenvalue and lambdagc
print("Plot the Eigenvalue and the lambda[GC]...")
png(filename = paste0(getwd(),'/Eigen','.png'),width = 480,height = 480,res = 120)
barplot(t(egc), beside = T, border = F, xlab="Eigen Space", ylim=c(0,max(egc)+2))
abline(h=1, lty=2, lwd=2)
legend("topright", legend = c("Eigenvalue", expression(paste(lambda[gc]))), pch=15, col=c("black", "grey"), bty='n')
dev.off()


#manhatan and qqplot
for (i in 1:PC){
  print(paste0("Plot the PCA", i, " manhattan and QQplot ..."))
  png(filename = paste0(getwd(),'/PCA', i, '.manhatan.png'), width = 1280, height = 480, res = 120)
  layout(matrix(c(1,1,2), 1, 3))
  pcIdx=i
  ##manhattan
  EigenRes = get(paste0("EgResPlot",pcIdx))
  EigenRes$P[which(EigenRes$P==0)] = 1e-300
  qqman::manhattan(EigenRes, suggestiveline = FALSE, genomewideline = -log10(0.05/nrow(eg)), 
                   colorSet = c("grey","darkblue"),title=paste0("ePC",pcIdx))
  
  ##qqplot
  EigenRes = get(paste0("EgResDT",pcIdx))
  EigenRes$P[which(EigenRes$P==0)] = 1e-300
  EigenRes$Praw[which(EigenRes$Praw==0)] = 1e-300
  #qqman::qq(EigenRes$Praw, cex = 0.4)
  qqman::qq(EigenRes$P, cex = 0.4)
  dev.off()
}


#collect params and write
print("Please wait for a mapp.Roment. This gonna takes some time in case of large marker number.")
params <- list(froot = froot,
               proportion = proportion,
               espace = PC,
               sc = sc,
               pcut = 0.05,
               nn = nn,
               mm = mm,
               ne = Ne,
               me = Me,
               GC = GC,
               hitDT = tophit)
write.table(params, paste0(params$froot,"_params",".txt"),quote=FALSE,row.names=TRUE, col.names=TRUE)

##write output
print("Out gwasdata, Please wait for a moment. This gonna takes some time in case of large marker number.")
for (i in 1:PC){
  fname=paste0('FullReport.E',i,'.txt')
  EigenRes = get(paste0("EgResDT",i))
  write.table(EigenRes,fname,quote=F,col.names = T,row.names = F)
}
