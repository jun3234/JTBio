MakeBetaTable<-function(root, PC=c(1))
{
  for(i in 1:length(PC))
  {
    print(paste0(root, "..", PC[i], ".egwas"))
    if (!fCheck(paste0(root, "..", PC[i], ".egwas")))
    {
      print(paste0("File '", root, "..", PC[i], ".egwas", "' does not exist."))
      return()
    }
    ef=read.table(paste0(root, "..", PC[i], ".egwas"), as.is = T, header = T)
    if (i == 1)
    {
      bTab=as.data.frame(matrix(0, nrow=nrow(ef), ncol=length(PC)+2))
      colnames(bTab)= c("SNP", "RefAllele", paste0("Beta", PC))
      bTab$SNP = ef$SNP
      bTab$RefAllele = ef$RefAllele
      bTab[,3] = ef$Beta
    } else {
      bTab[,2+i] = ef$Beta
    }
  }
  return(bTab)
}

AIM<-function(root, PC, pcutoff = "bonferroni", GCcorrection = T)
{
  if(!fCheck(paste0(root, "..", PC, ".egwas")))
  {
    return()
  }

  for (i in 1:length(PC)) {
    d=read.table(paste0(root, "..", PC[i], ".egwas"), as.is = T, header = T)
    if (!("CHR" %in% names(d) & "BP" %in% names(d) & "P" %in% names(d))) stop("Make sure your data frame contains columns CHR, BP, and P")

    gc = qchisq(median(d$P), 1, lower.tail = F)/qchisq(0.5, 1, lower.tail = F)
    dp = pchisq(qchisq(d$P, 1, lower.tail = F)/gc, 1, lower.tail = F)
    if(GCcorrection)
    {
      d$logp = -log10(dp)
    } else {
      d$logp = -log10(d$P)
    }

    if(pcutoff=="bonferroni" | missing(pcutoff))
    {
      h=-log10(0.05/nrow(d))
    } else {
      h=-log10(pcutoff)
    }

    d$logp[which(d$logp < h)]=NA

    if(length(which(!is.na(d$logp) > 0)))
    {
      manhattan2(d, cex=0.5, pch=16, title=paste("PC",PC[i]))
    }
  }
}

manhattan2 <- function(dataframe, colors=c("gray10", "gray50"), ymax="max", limitchromosomes=1:23, suggestiveline=-log10(1e-5), genomewideline=NULL, title="",  ...) {

  d=dataframe
  if (!("CHR" %in% names(d) & "BP" %in% names(d) & "P" %in% names(d))) stop("Make sure your data frame contains columns CHR, BP, and P")
  if (any(limitchromosomes)) d=d[d$CHR %in% limitchromosomes, ]

  d$pos=NA
  ticks=NULL
  lastbase=0
  colors <- rep(colors,max(d$CHR))[1:max(d$CHR)]
  if (ymax=="max") ymax<-ceiling(max(d$logp[which(!is.na(d$logp))]))
  if (ymax<8) ymax<-8
  numchroms=length(unique(d$CHR))
  if (numchroms==1) {
    d$pos=d$BP
    ticks=floor(length(d$pos))/2+1
  } else {
    for (i in unique(d$CHR)) {
      if (i==1) {
        d[d$CHR==i, ]$pos=d[d$CHR==i, ]$BP
      } else {
        lastbase=lastbase+tail(subset(d,CHR==i-1)$BP, 1)
        d[d$CHR==i, ]$pos=d[d$CHR==i, ]$BP+lastbase
      }
      ticks=c(ticks, d[d$CHR==i, ]$pos[floor(length(d[d$CHR==i, ]$pos)/2)+1])
    }
  }
  if (numchroms==1) {
    with(d, plot(main=title, pos, logp, ylim=c(0,ymax), ylab=expression(-log[10](italic(p))), xlab=paste("Chromosome",unique(d$CHR),"position"), frame.plot = F, ...))
  }  else {
    with(d, plot(main=title, pos, logp, ylim=c(0,ymax), ylab=expression(-log[10](italic(p))), xlab="Chromosome", xaxt="n", type="n", frame.plot = F, ...))
    axis(1, at=ticks, lab=unique(d$CHR), ...)
    icol=1
    for (i in unique(d$CHR)) {
      with(d[d$CHR==i, ],points(pos, logp, col=colors[icol], ...))
      icol=icol+1
    }
  }

}

RunEigenGWAS <- function(dataName, PC, inbred=F, gearPath)
{
  if(missing(gearPath))
  {
    gear=paste("java -jar", paste0(" ./gear.jar"))
  } else {
    gear=paste("java -jar", gearPath)
  }

  if (inbred==F)
  {
    EigenGWAS=paste(gear, "eigengwas", "--bfile", dataName, "--ev", PC,  "--out", dataName)
  }
  else
  {
    EigenGWAS=paste(gear, "eigengwas", "--inbred", "--bfile", dataName, "--ev", PC,  "--out", dataName)
  }

  system(EigenGWAS)
}

fCheck <- function(fn)
{
  if (!file.exists(fn))
  {
    print(fn, " does not exist.")
    return(F)
  } else {
    return(T)
  }
}

EigenQQPlot <- function(root, pc)
{
  if(!fCheck(paste0(root, "..", pc, ".egwas")))
  {
    return()
  }
  layout(matrix(1,1,1))
  
  eg = read.table(paste0(root, "..", pc, ".egwas"), as.is = T, header = T)

  gc = qchisq(median(eg$P), 1, lower.tail = F)/qchisq(0.5, 1)
  thchi = rchisq(which(!is.na(eg$P)), 1)
  qqplot(main="", thchi, eg$Chi, xlab=expression(paste("Theoretical ", chi[1]^2)), ylab=expression(paste("EigenGWAS ", chi[1]^2)), frame.plot=F, pch=16, cex=0.5, col="grey")
  points(sort(thchi), sort(eg$Chi[!is.na(eg$Chi)]/gc), pch=1, cex=0.7)
  abline(a=0, b=1, col="red", lty=2)
  legend("topleft", legend = c(paste0("LambdaGC=", format(gc, digits=3, nsmall=2))), bty='n')
}

grmStats <- function(root)
{
  grm=grmReader(root)
  grmS=grm[col(grm) > row(grm)]
  ne=-1/mean(grmS)
  me=1/var(grmS)
  hist(grmS, xlab="GRM scores", main ="GRM distribution", breaks=25)
  legend("topright", legend = c(paste0("ne=", format(ne, digits=3, nsmall=2)), paste0("me=", format(me, digits=3, nsmall=2))), bty='n')
}

grmReader <- function(root)
{
  if(!fCheck(paste0(root, ".grm.gz")))
  {
    return()
  }
  layout(matrix(1,1,1))
  
  grmFile = gzfile(paste0(root, ".grm.gz"))
  grm = read.table(grmFile)

  idFile = read.table(paste0(root, ".grm.id"), as.is=T)

  mat=matrix(0, nrow(idFile), nrow(idFile))
  for(i in 1:nrow(idFile))
  {
    idx1 = i * (i-1)/2 + 1
    idx2 = i * (i+1)/2
    mat[i, 1:i] = grm[idx1:idx2, 4]
    mat[1:i, i] = grm[idx1:idx2, 4]
  }
  return(mat)
}

pcMatPlot <- function(root, PC=c(1,2), COL="grey", ma=0.3)
{
  if(!fCheck(paste0(root, ".eigenvec")))
  {
    return()
  }

  pc=length(PC)
  Evec=read.table(paste0(root, ".eigenvec"), as.is = T)
  par(mai=c(ma, ma, ma, ma))
  nt=pc*(pc-1)/2
  mat=matrix(nt+pc+1, pc, pc)
  mat[col(mat) < row(mat)] = 1:nt
  diag(mat)=(nt+1):(nt+pc)
  layout(mat)
  for(i in 1:(pc-1))
  {
    for(j in (i+1):pc)
    {
      plot(Evec[,PC[i]+2],Evec[, PC[j]+2], cex=0.5, pch=16, col=COL, xlim=1.2*range(Evec[,PC[i]+2]), ylim=1.2*range(Evec[,PC[j]+2]), bty="l", axes = F)
      abline(h=0, v=0, col="grey70", lty=2)
    }
  }
  for(i in 1:pc)
  {
    if (i== 1)
    {
      plot(x=NULL, y=NULL, xlim=1.2*range(Evec[,PC[i]+2]), ylim=1.2*range(Evec[,PC[i]+2]), bty="l")
    } else if (i == pc)
    {
      plot(x=NULL, y=NULL, xlim=1.2*range(Evec[,PC[i]+2]), ylim=1.2*range(Evec[,PC[i]+2]), bty="l")
    } else {
      plot(x=NULL, y=NULL, xlim=1.2*range(Evec[,PC[i]+2]), ylim=1.2*range(Evec[,PC[i]+2]), bty="l")
    }
    text(mean(1.2*range(Evec[,PC[i]+2])), mean(1.2*range(Evec[,PC[i]+2])),labels = paste("EV", PC[i]))
  }
}

EigenValuePlot <- function(root, PC = 1)
{
  if (!fCheck(paste0(root, ".eigenval")))
  {
    return()
  }

  Evev=read.table(paste0(root, ".eigenval"), as.is = T)
  GC=array(0, dim=PC)

  for(i in 1:PC)
  {
    if (!fCheck(paste0(root, "..", i, ".egwas")))
    {
      return()
    }
  }

  for(i in 1:PC)
  {
    eg = read.table(paste0(root, "..", i, ".egwas"), as.is = T, header = T)
    GC[i] = qchisq(median(eg$P), 1, lower.tail = F)/qchisq(0.5, 1)
  }

  egc=matrix(c(Evev[1:PC,1], GC), PC, 2, byrow = F)
  rownames(egc)=seq(1, PC)
  barplot(t(egc), beside = T, border = F)
  legend("topright", legend = c("Eigenvalue", expression(paste(lambda[gc]))), pch=15, col=c("black", "grey"), bty='n')
}

DeepEigenValuePlot <- function(root, PC, qcut=c(0.25, 0.5, 0.75))
{
  if (!fCheck(paste0(root, ".eigenval")))
  {
    return()
  }
  layout(matrix(1,1,1))
  
  Evev=read.table(paste0(root, ".eigenval"), as.is = T)
  GC=matrix(0, nrow=1, ncol=length(qcut)+1)
  GC[1]=Evev[PC,1]
  eg = read.table(paste0(root, "..", PC, ".egwas"), as.is = T, header = T)

  GC[1, 2:(1+length(qcut))] = qchisq(sort(eg$P)[ceiling(qcut*nrow(eg))], 1, lower.tail = F)/qchisq(qcut, 1, lower.tail = F)
  colnames(GC)=c("EV", qcut)
  par(las=2)
  barplot(GC, ylim=c(0, max(GC)*1.3), beside = T, border = F, col=c("black", rep("grey", length(qcut))))
  legend("topright", legend = c("Eigenvalue", expression(paste(lambda[gc]))), pch=15, col=c("black", "grey"), bty='n')
}

EigenGWASPlot <- function(root, pc)
{
  if(!fCheck(paste0(root, "..", pc, ".egwas")))
  {
    return()
  }

  eg=read.table(paste0(root, "..", pc, ".egwas"), as.is = T, header = T)

  layout(matrix(1:3, 3, 1))

  eg=eg[,-which(colnames(eg)=="P")]
  colnames(eg)[which(colnames(eg)=="PGC")]="P"
  manhattan(eg, pch=16, cex=0.5, bty='l')
  FstPlot(eg, pch=16, cex=0.5, bty='l')
  plot(eg$Chi, eg$Fst, xlab=expression(chi[1]^2), ylab=expression(paste(italic("F")[italic("ST")])), pch=16, cex=0.5, frame.plot = F)
  rsq=cor(eg$Chi, eg$Fst, use="pairwise.complete.obs")^2
  legend("topright", legend = c(paste("Rsq=", format(rsq, digits = 4, nsmall = 3))), bty='n')
}

SWEigenGWASPlot <- function(root, pc, kb=5)
{
  if(!fCheck(paste0(root, "..", pc, ".egwas")))
  {
    return()
  }

  eg=read.table(paste0(root, "..", pc, ".egwas"), as.is = T, header = T)
  eg=subset(na.omit(eg[order(eg$CHR, eg$BP, na.last = NA), ]))
  eg=subset(eg, !is.na(eg$P) & eg$P >0 & eg$P <=1 & !is.na(eg$Chi) & eg$Chi >= 0 )
  lgc=qchisq(median(eg$P), 1, lower.tail = F)/qchisq(0.5, 1)
  CHR=names(table(eg$CHR))
  for(i in 1:length(CHR))
  {
    egs=eg[which(eg$CHR == CHR[i]),]
    rg=range(egs$BP)
    meg=matrix(0, nrow(egs), 5)

    for(j in 1:nrow(meg))
    {
      idx=which((egs$BP >= egs$BP[j] - kb*1000) & (egs$BP <= egs$BP[j] + kb * 1000))
      meg[j, 1] = egs$CHR[j]
      meg[j, 2] = egs$BP[j]
      meg[j, 3] = mean(egs$Fst[idx])
      meg[j, 4] = pchisq(mean(egs$Chi[idx]/lgc), 1, lower.tail = F)
      meg[j, 5] = mean(egs$Chi[idx])
    }

    if(i == 1)
    {
      Meg = meg
    }
    else {
      Meg = rbind(Meg, meg)
    }
  }
  DMeg=as.data.frame(Meg)
  colnames(DMeg)=c("CHR", "BP", "Fst", "P", "Chi")

  layout(matrix(1:3, 3, 1))

  manhattan(DMeg, cex=0.5, pch=16, bty="l")
  FstPlot(DMeg, pch=16, cex=0.5, bty="l")
  plot(DMeg$Chi, DMeg$Fst, xlab=expression(chi[1]^2), ylab=expression(paste(italic("F")[italic("ST")])), pch=16, cex=0.5, frame.plot = F)
  rsq=cor(DMeg$Chi, DMeg$Fst, use="pairwise.complete.obs")^2
  legend("topright", legend = c(paste("Rsq=", format(rsq, digits = 4, nsmall = 3))), bty='n')

}

SWPhenoEigenGWASPlot <- function(phe, root, pc, kb=5)
{
  if (!fCheck(paste0(root, "..", pc, ".egwas")))
  {
    return()
  }
  if (!fCheck(phe))
  {
    return()
  }

  eg=read.table(paste0(root, "..", pc, ".egwas"), as.is = T, header = T)
  gw=read.table(phe, as.is = T, header = T)

  lgc=qchisq(median(eg$P), 1, lower.tail = F)/qchisq(0.5, 1)
  CHR=names(table(eg$CHR))
  for(i in 1:length(CHR))
  {
    egs=eg[which(eg$CHR == CHR[i]),]
    rg=range(egs$BP)
    meg=matrix(0, nrow(egs), 6)

    for(j in 1:nrow(meg))
    {
      idx=which((egs$BP >= egs$BP[j] - kb*1000) & (egs$BP <= egs$BP[j] + kb * 1000))
      meg[j, 1] = egs$CHR[j]
      meg[j, 2] = egs$BP[j]
      meg[j, 3] = mean(egs$Fst[idx])
      meg[j, 4] = pchisq(mean(egs$Chi[idx]/lgc), 1, lower.tail = F)
      meg[j, 5] = mean(egs$Chi[idx])
      meg[j, 6] = pchisq(mean(qchisq(gw$P[idx], 1, lower.tail = F)), 1, lower.tail = F)
    }

    if(i == 1)
    {
      Meg = meg
    }
    else {
      Meg = rbind(Meg, meg)
    }
  }
  DMeg=as.data.frame(Meg)
  DMegE=DMeg[,c(1:5)]
  DMegG=DMeg[,c(1:2, 6)]
  colnames(DMegE)=c("CHR", "BP", "Fst", "P", "Chi")
  colnames(DMegG)=c("CHR", "BP", "P")

  layout(matrix(1:3, 3, 1))

  manhattan(DMegE, cex=0.5, pch=16)
  manhattan(DMegG, cex=0.5, pch=16)

  plot(-log10(DMegE$P), -log10(DMegG$P), xlab=expression(paste(-log[10](italic(p)), "[EigenGWAS]")), ylab=expression(paste(-log[10](italic(p)), "[GWAS]")), pch=16, cex=0.5, frame.plot = F)

  rsq=cor(-log10(DMegE$P), -log10(DMegG$P), use="pairwise.complete.obs")^2
  legend("topright", legend = c(paste("Rsq=", format(rsq, digits = 4, nsmall = 3))), bty='n')
}

manhattan <- function(dataframe, colors=c("gray10", "gray50"), ymax="max", limitchromosomes=NULL, suggestiveline=-log10(1e-5), genomewideline=NULL, title="", annotate=NULL, ...) {

  d=dataframe
  if (!("CHR" %in% names(d) & "BP" %in% names(d) & "P" %in% names(d))) stop("Make sure your data frame contains columns CHR, BP, and P")
  if (!is.null(limitchromosomes)) {
    d=d[d$CHR %in% limitchromosomes, ]
  }

  d=subset(na.omit(d[order(d$CHR, d$BP, na.last = NA), ]))
  d=subset(na.omit(d[order(d$CHR, d$BP), ]), (P>0 & P<=1)) # remove na's, sort, and keep only 0<P<=1
  d$logp = -log10(d$P)
  d$pos=NA
  ticks=NULL
  lastbase=0 #  colors <- rep(colors,max(d$CHR))[1:max(d$CHR)]
  colors <- rep(colors,max(d$CHR))[1:length(unique(d$CHR))]

  if (ymax=="max") ymax<-ceiling(max(d$logp))
  if (ymax<8) ymax<-8
  numchroms=length(unique(d$CHR))
  if (numchroms==1) {
    d$pos=d$BP
    ticks=floor(length(d$pos))/2+1
  } else {
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      if (i==1) {
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP
      } else {
        lastbase=lastbase+tail(subset(d, CHR==Uchr[i-1])$BP, 1)
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP+lastbase
      }
      ticks=c(ticks, d[d$CHR==Uchr[i], ]$pos[floor(length(d[d$CHR==Uchr[i], ]$pos)/2)+1])
    }
  }
  if (numchroms==1) {
    with(d, plot(main=title, pos, logp, ylim=c(0,ymax), ylab=expression(-log[10](italic(p))), xlab=paste("Chromosome",unique(d$CHR),"position"), ...))
  } else {
    with(d, plot(main=title, pos, logp, ylim=c(0,ymax), ylab=expression(-log[10](italic(p))), xlab="Chromosome", xaxt="n", type="n", ...))
    axis(1, at=ticks, lab=unique(d$CHR), ...)
    icol=1
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      with(d[d$CHR==Uchr[i], ], points(pos, logp, col=colors[icol], ...))
      icol=icol+1
    }
  }
  if (!is.null(annotate)) {
    d.annotate=d[which(d$SNP %in% annotate), ]
    with(d.annotate, points(pos, logp, col="green3", ...))
  }
  #  if (suggestiveline) abline(h=suggestiveline, col="blue")
  if (!is.null(genomewideline)) {
    abline(h=genomewideline, col="gray")
  } else {
    abline(h=-log10(0.05/nrow(d)), col="gray")
  }
}

FstPlot <- function(dataframe, colors=c("gray10", "gray50"), ymax="max", limitchromosomes=NULL, suggestiveline=NULL, genomewideline=NULL, annotate=NULL, title="", ...) {

    d=dataframe
  if (!("CHR" %in% names(d) & "BP" %in% names(d) & "Fst" %in% names(d))) stop("Make sure your data frame contains columns CHR, BP, and P")
  if (!is.null(limitchromosomes)) {
    d=d[d$CHR %in% limitchromosomes, ]
  }

  d=subset(na.omit(d[order(d$CHR, d$BP, na.last = NA), ]))
  d=subset(na.omit(d[order(d$CHR, d$BP), ]), (Fst>0 & Fst<=1)) # remove na's, sort, and keep only 0<P<=1
  d$logp = d$Fst
  d$pos=NA
  ticks=NULL
  lastbase=0
  colors <- rep(colors,max(d$CHR))[1:max(d$CHR)]
  if (ymax=="max") ymax<-max(d$logp)*1.1
  numchroms=length(unique(d$CHR))
  if (numchroms==1) {
    d$pos=d$BP
    ticks=floor(length(d$pos))/2+1
  } else {
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      if (i==1) {
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP
      } else {
        lastbase=lastbase+tail(subset(d,CHR==Uchr[i-1])$BP, 1)
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP+lastbase
      }
      ticks=c(ticks, d[d$CHR==Uchr[i], ]$pos[floor(length(d[d$CHR==Uchr[i], ]$pos)/2)+1])
    }
  }
  if (numchroms==1) {
    with(d, plot(pos, logp, ylim=c(0,ymax), ylab=expression(paste(italic("F")[italic("ST")])), xlab=paste("Chromosome",unique(d$CHR),"position"), main=title,...))
  }  else {
    with(d, plot(pos, logp, ylim=c(0,ymax), ylab=expression(paste(italic("F")[italic("ST")])), xlab="Chromosome", xaxt="n", type="n", main=title,...))
    axis(1, at=ticks, lab=unique(d$CHR), ...)
    icol=1
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      with(d[d$CHR==Uchr[i], ], points(pos, logp, col=colors[icol], ...))
      icol=icol+1
    }
  }
  if (!is.null(annotate)) {
    d.annotate=d[which(d$SNP %in% annotate), ]
    with(d.annotate, points(pos, logp, col="green3", ...))
  }
  #  if (suggestiveline) abline(h=suggestiveline, col="blue")
  #  if (genomewideline) abline(h=genomewideline, col="red")
}

miamiPlot <- function(root, PC=1, P1=NULL, P2=NULL, Log1=TRUE, Log2=TRUE, AnoCol="red", AnoCol1="blue", AnoCol2="yellow", colors=c("gray10", "gray50"), limitchromosomes=NULL, suggestiveline=-log10(1e-5), genomewideline=NULL, title="", annotate=NULL, annotate1=NULL, annotate2=NULL, ...) {

  layout(matrix(1,1,1))
  if (!fCheck(paste0(root, "..", PC, ".egwas")))
  {
    return()
  }

  dataframe = read.table(paste0(root, "..", PC, ".egwas"), as.is = T, header=T)
  
  if(is.null(P1)) {
    P1 = "PGC"
  }
  pidx1=which(colnames(dataframe) == P1)
  
  if(is.null(P2)) {
    P2 = "Fst"
  }
  pidx2 = which(colnames(dataframe) == P2)
  d = dataframe
  if (!("CHR" %in% names(d) & "BP" %in% names(d) & P1 %in% names(d) & P2 %in% names(d))) stop(paste0("Make sure your data frame contains columns CHR, BP, ", P1, " and ", P2, ".."))
  if (!is.null(limitchromosomes)) {
    d=d[d$CHR %in% limitchromosomes, ]
  }

  d=na.omit(d)
  d=d[order(d$CHR, d$BP),]
#  d=subset(na.omit(d[order(d$CHR, d$BP), ]), (!is.na(d[,pidx1]) & !is.na(d[,pidx2]))) # remove na's, sort, and keep only 0<P<=1

  if (Log1)
  {
    d$logp = -log10(d[,pidx1])
  } else {
    d$logp = d[,pidx1]
  }
  
  if (Log2)
  {
    d$logp2 = log10(d[,pidx2])
  } else {
    d$logp2 = -1*d[,pidx2]
  }
  
  ytick = c(format(max(abs(d$logp2)), digits = 3), 0, ceiling(max(abs(d$logp))))
  
  if ( max(d$logp) > abs(max(d$logp2)) )
  {
    d$logp2 = d$logp2 * max(d$logp)/max(abs(d$logp2))
  } else {
    d$logp = d$logp * max(abs(d$logp2))/max(d$logp)
  }
  
  d$pos=NA
  ticks=NULL
  lastbase=0
  colors <- rep(colors,max(d$CHR))[1:max(d$CHR)]
  ymax = 1.2*(max(d$logp))
  ymin = 1.2*(min(d$logp2))

  numchroms=length(unique(d$CHR))
  if (numchroms==1) {
    d$pos=d$BP
    ticks=floor(length(d$pos))/2+1
  } else {
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      if (i==1) {
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP
      } else {
        lastbase=lastbase+tail(subset(d,CHR==Uchr[i-1])$BP, 1)
        d[d$CHR==Uchr[i], ]$pos=d[d$CHR==Uchr[i], ]$BP+lastbase
      }
      ticks=c(ticks, d[d$CHR==Uchr[i], ]$pos[floor(length(d[d$CHR==Uchr[i], ]$pos)/2)+1])
    }
  }
  if (numchroms==1) {
    with(d, plot(main=title, pos, logp, ylim=c(ymin, ymax), xlab=paste("Chromosome", unique(d$CHR), "position"), ylab='n',  axes=F, ...))
  } else {
    with(d, plot(main=title, pos, logp, ylim=c(ymin, ymax), ylab='', xlab="Chromosome", axes=F, type="n", ...))
    axis(1, at=ticks, lab=unique(d$CHR), ...)
    axis(2, at=c(-1*(max(abs(d$logp2))), 0, max(abs(d$logp))), lab=ytick, ...)
    icol=1
    Uchr=unique(d$CHR)
    for (i in 1:length(Uchr)) {
      with(d[d$CHR==Uchr[i], ],points(pos, logp, col=colors[icol], ...))
      with(d[d$CHR==Uchr[i], ],points(pos, logp2, col=colors[icol], ...))
      icol=icol+1
    }
  }
  if (!is.null(annotate)) {
    d.annotate=d[which(d$SNP %in% annotate), ]
    with(d.annotate, points(pos, logp, col=AnoCol, pch=16, ...))
    with(d.annotate, points(pos, logp2, col=AnoCol, pch=16, ...))
  }
  
  if (!is.null(annotate1)) {
    d.annotate=d[which(d$SNP %in% annotate1), ]
    with(d.annotate, points(pos, logp, col=AnoCol1, pch=16))
  }
  
  if (!is.null(annotate2)) {
    d.annotate=d[which(d$SNP %in% annotate2), ]
    with(d.annotate, points(pos, logp2, col=AnoCol2, pch=16))
  }
  
  if (!is.null(genomewideline)) {
    abline(h=genomewideline, col="gray")
    #    abline(h=-1*genomewideline, col="gray")
  } else {
    abline(h=-log10(0.05/nrow(d)), col="gray")
    #    abline(h=log10(0.05/nrow(d)), col="gray")
  }
  abline(h=0, col="white", lwd=2, lty=2)
}
