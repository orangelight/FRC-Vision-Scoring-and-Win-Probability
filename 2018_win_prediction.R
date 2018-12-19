con = dbConnect(RSQLite::SQLite(), "C:\\Users\\darkd\\Documents\\ScoreProject\\timeseriesdb.db")

modelList <- list()
for(i in 1:150){
  train_data = merge(x = timedata[timedata$time==i,c(2,5,6,7,8,9)], y = outcomes, by = "match_key", all.x = TRUE)
  train_data$difference <- train_data$red_score -  train_data$blue_score
  glm.fit=glm(outcome~difference+scale_control+red_switch_control+blue_switch_control, data=train_data, family = binomial, na.action = na.omit)
  modelList <- c(modelList, list(glm.fit))
}

pdf("plotstest.pdf", width = 50, height = 50)
par(mfrow=c(13,13))
for(i in 150:1) {
  train_data = merge(x = timedata[timedata$time==i,c(2,5,6)], y = outcomes, by = "match_key", all.x = TRUE)
  train_data$difference <- train_data$red_score -  train_data$blue_score
  plot(train_data$difference, train_data$outcome)
  curve(predict(modelList[[i]], newdata=data.frame(difference=x), type = "response")+1,add=TRUE)
  abline(h=1.5)
}
dev.off()

match42 = timedata[timedata$match_key=='2018mimil_qf1m1',c(2,4,5,6,7,8,9)]
match42$difference <- match42$red_score-match42$blue_score
predData <- vector()
for(i in 150:1) {
  #plot(train_data$difference, train_data$outcome)
  #curve(predict(modelList[[i]], newdata=data.frame(difference=x), type = "response")+1,add=TRUE)
  #abline(h=1.5)
  predData<- c(predData, predict(modelList[[i]], newdata=match42[match42$time==i, c(8,5,6,7)], type = "response"))
}
plot(-1,-1, xlim=c(1,150), ylim=c(0,1), title(main='2018micen_qf4m2'), xlab="Time(s)", ylab="Probability red wins")
lines(predData)

