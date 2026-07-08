#install.packages('dplyr')
#install.packages('metaSEM')
#install.packages('metafor')
#install.packages('clubSandwich')
#install.packages('tibble')
#install.packages('ggplot2')
#install.packages('cowplot')

library(dplyr)
library("metaSEM")
library(metafor)
library('clubSandwich')
library(tibble)
library(ggplot2)
library(cowplot)
library(robumeta)
library(weightr)

setwd("C:/Users/sweis/OneDrive/Old Desktop/GT Info")
data1 <- read.csv("Final_AutoData.csv", as.is=TRUE)
dataS <- subset(data1, Specific == 1)
dataC <- subset(data1, Categoric == 1)

#*****3-LEVEL MODEL(intercept is average ES)*****
Model4S <- rma.mv(g, varg, random =~ 1|ID/Meas, data=dataS, method = "ML")
summary(Model4S)
coef_test(Model4S, vcov = "CR2")

Model4C <- rma.mv(g, varg, random =~ 1|ID/Meas, data=dataC, method = "ML")
summary(Model4C)
coef_test(Model4C, vcov = "CR2")

#*****Moderator Analyses*****
#Depressed Group Age
model5S <- rma.mv(g ~ cbind(ageDep), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
summary(model5S)
coef_test(model5S, vcov = "CR2")

model5C <- rma.mv(g ~ cbind(ageDep), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
summary(model5C)
coef_test(model5C, vcov = "CR2")

#Published versus unpublished
model6S <- rma.mv(g ~ cbind(Published), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model6S
coef_test(model6S, vcov = "CR2")
model6C <- rma.mv(g ~ cbind(Published), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model6S
coef_test(model6C, vcov = "CR2")
#Depression Diagnosis
model7S <- rma.mv(g ~ cbind(DiagStatus), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model7S
coef_test(model7S, vcov = "CR2")
model7C <- rma.mv(g ~ cbind(DiagStatus), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model7C
coef_test(model7C, vcov = "CR2")
#Depression Status
model8S <- rma.mv(g ~ cbind(DepStatus), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model8S
coef_test(model8S, vcov = "CR2")
model8C <- rma.mv(g ~ cbind(DepStatus), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model8C
coef_test(model8C, vcov = "CR2")
#Female vs. Male
model9S <- rma.mv(g ~ cbind(sex), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model9S
coef_test(model9S, vcov = "CR2")
model9C <- rma.mv(g ~ cbind(sex), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model9C
coef_test(model9C, vcov = "CR2")
#Depressed group education
model10S <- rma.mv(g ~ cbind(edu), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model10S
coef_test(model10S, vcov = "CR2")
model10C <- rma.mv(g ~ cbind(edu), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model10C
coef_test(model10C, vcov = "CR2")
#Groups matched for age vs. not
model11S <- rma.mv(g ~ cbind(matchAge), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model11S
coef_test(model11S, vcov = "CR2")
model11C <- rma.mv(g ~ cbind(matchAge), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model11C
coef_test(model11C, vcov = "CR2")
#Groups matched for education vs. not
model12S <- rma.mv(g ~ cbind(matchEdu), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model12S
coef_test(model12S, vcov = "CR2")
model12C <- rma.mv(g ~ cbind(matchEdu), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model12C
coef_test(model12C, vcov = "CR2")
#Depressed group IQ
model13S <- rma.mv(g ~ cbind(IQDep), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model13S
coef_test(model13S, vcov = "CR2")
model13C <- rma.mv(g ~ cbind(IQDep), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model13C
coef_test(model13C, vcov = "CR2")
#Recurrent vs. First Episode
model14S <- rma.mv(g ~ cbind(episode), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model14S
coef_test(model14S, vcov = "CR2")
#Onset Age
model15S <- rma.mv(g ~ cbind(onsetAge), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model15S
coef_test(model15S, vcov = "CR2")
#Onset Age Calc
model16S <- rma.mv(g ~ cbind(onsetAgeCalc), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model16S
coef_test(model16S, vcov = "CR2")
#Time since diagnosis
model17S <- rma.mv(g ~ cbind(duration), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model17S
coef_test(model17S, vcov = "CR2")
#Time since diagnosis calc
model18S <- rma.mv(g ~ cbind(durationCalc), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model18S
coef_test(model18S, vcov = "CR2")
#Antidepressant use
model19S <- rma.mv(g ~ cbind(med), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model19S
coef_test(model19S, vcov = "CR2")
model19C <- rma.mv(g ~ cbind(med), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model19C
coef_test(model19C, vcov = "CR2")
#Clinical vs. community sample
model20S <- rma.mv(g ~ cbind(Recruitment), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model20S
coef_test(model20S, vcov = "CR2")
model20C <- rma.mv(g ~ cbind(Recruitment), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model20C
coef_test(model20C, vcov = "CR2")
#MADRS Score
model21S <- rma.mv(g ~ cbind(MADRS), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model21S
coef_test(model21S, vcov = "CR2")
model21C <- rma.mv(g ~ cbind(MADRS), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model21C
coef_test(model21C, vcov = "CR2")
#HDRS Score
model22S <- rma.mv(g ~ cbind(HDRS), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model22S
coef_test(model22S, vcov = "CR2")
model22C <- rma.mv(g ~ cbind(HDRS), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model22C
coef_test(model22C, vcov = "CR2")
#BDI Score
model23S <- rma.mv(g ~ cbind(BDI), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model23S
coef_test(model23S, vcov = "CR2")
model23C <- rma.mv(g ~ cbind(BDI), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model23C
coef_test(model23C, vcov = "CR2")
#HADS Score
model24S <- rma.mv(g ~ cbind(HADS), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model24S
coef_test(model24S, vcov = "CR2")
model24C <- rma.mv(g ~ cbind(HADS), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model24C
coef_test(model24C, vcov = "CR2")
#CESD Score
model25S <- rma.mv(g ~ cbind(CESD), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model25S
coef_test(model25S, vcov = "CR2")
model25C <- rma.mv(g ~ cbind(CESD), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model25C
coef_test(model25C, vcov = "CR2")
#BDI Calc
model26S <- rma.mv(g ~ cbind(BDICalc), varg, random =~1|ID/Meas, data = dataS, method = "ML")
model26S
coef_test(model26S, vcov = "CR2")
model26C <- rma.mv(g ~ cbind(BDICalc), varg, random =~1|ID/Meas, data = dataC, method = "ML")
model26C
coef_test(model26C, vcov = "CR2")
#AMT vs. not
model27S <- rma.mv(g ~ cbind(AMT), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model27S
coef_test(model27S, vcov = "CR2")
model27C <- rma.mv(g ~ cbind(AMT), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model27C
coef_test(model27C, vcov = "CR2")
#Positive & Negative vs. Neutral
model28S <- rma.mv(g ~ cbind(Positive, Negative), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model28S
coef_test(model28S, vcov = "CR2")
model28C <- rma.mv(g ~ cbind(Positive, Negative), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model28C
coef_test(model28C, vcov = "CR2")
#Neutral & Positive vs. Negative
model29S <- rma.mv(g ~ cbind(Neutral, Positive), varg, random =~ 1|ID/Meas, data = dataS, method = "ML")
model29S
coef_test(model29S, vcov = "CR2")
model29C <- rma.mv(g ~ cbind(Neutral, Positive), varg, random =~ 1|ID/Meas, data = dataC, method = "ML")
model29C
coef_test(model29C, vcov = "CR2")

#*****Publication Bias Analyses*****
dataAS <- read.csv("Agg_dataS.csv", as.is=TRUE)
dataAC <- read.csv("Agg_dataC.csv", as.is=TRUE)

res1 <- rma(g,vi, data=dataS, measure = "SMD", method = "ML") 
regtest(res1, predictor = "vi") 
trimfill(res1, estimator="R0") 
trimfill(res1, estimator="L0") 

res2 <- rma(g,vi, data=dataC, measure = "SMD", method = "ML") 
regtest(res2, predictor = "vi") 
trimfill(res2, estimator="R0") 
trimfill(res2, estimator="L0") 

res3 <- rma(g,vi, data=dataAS, measure = "SMD", method = "ML") 
regtest(res3, predictor = "vi") 
trimfill(res3, estimator="R0") 
trimfill(res3, estimator="L0") 

res4 <- rma(g,vi, data=dataAC, measure = "SMD", method = "ML") 
regtest(res4, predictor = "vi") 
trimfill(res4, estimator="R0") 
trimfill(res4, estimator="L0") 

#*****Forest Plots*****
forest(Model4S, slab = dataS$Title, order = "obs", cex = 0.8, efac = 0.75,
                      pch = 19, steps = 5)

text(-13.4, 142.3, "Study name", pos=4, cex = 1.0)
text(11.2, 142.3, "Effect size  and 95% CI", pos=2, cex = 1.0)

forest(Model4C, slab = dataC$Title, order = "obs", cex = 1.1, efac = 0.75,
       pch = 19, steps = 5)

text(-11.6, 42.5, "Study name", pos=4, cex = 1.1)
text(13.6, 42.5, "Effect size  and 95% CI", pos=2, cex = 1.1)

