#install.packages(c('tidyverse', 'caret', 'neuralnet'))

library(tidyverse)
library(caret)
library(neuralnet)

datos = iris

muestra = createDataPartition(datos$Species, p=0.8, list = F)
train = datos[muestra,]
test = datos[-muestra,]

head(train, 5)
tail(train, 5)
train[17:25,]

sepal_length = train$Sepal.Length
hist(sepal_length)
hist(train$Petal.Length)

red.neuronal = neuralnet(Species ~ Sepal.Length + Sepal.Width + Petal.Length + Petal.Width, data = train, hidden = c(2,3))
red.neuronal$act.fct

plot(red.neuronal)

# -------------------------------------------------------------------------

prediccion = predict(red.neuronal, test, type='class')

# Decodificar maximo = Especie
specie.decod = apply(prediccion, 1, which.max)

specie.pred = data_frame(specie.decod)
specie.pred = mutate(specie.pred, especie = recode(specie.pred$specie.decod, "1" = "Setosa", "2"="Versicolor", "3"="Virginica"))

test$Species.pred = specie.pred$especie

