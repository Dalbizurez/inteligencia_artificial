#install.packages(c('tidyverse', 'caret', 'neuralnet'))

library(tidyverse)
library(caret)
library(neuralnet)
library(palmerpenguins)

datos = penguins %>% 
  drop_na(species, bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g)

datos = datos %>%
  mutate(
    Adelie    = ifelse(species == "Adelie", 1, 0),
    Gentoo    = ifelse(species == "Gentoo", 1, 0),
    Chinstrap = ifelse(species == "Chinstrap", 1, 0)
  )

datos = datos %>%
  mutate(across(c(bill_length_mm, bill_depth_mm, flipper_length_mm, body_mass_g), scale))

muestra = createDataPartition(datos$species, p=0.8, list = FALSE)
train = datos[muestra,]
test = datos[-muestra,]

head(train, 5)
tail(train, 5)
train[17:25,]

red.neuronal = neuralnet(species ~ bill_length_mm + bill_depth_mm + flipper_length_mm + body_mass_g, data = train, hidden = c(2,3))
red.neuronal$act.fct

plot(red.neuronal)

# -------------------------------------------------------------------------

prediccion = predict(red.neuronal, test, type='class')

# Decodificar maximo = Especie
specie.decod = apply(prediccion, 1, which.max)

specie.pred = data_frame(specie.decod)
specie.pred = mutate(specie.pred, especie = recode(specie.pred$specie.decod, "1" = "Adelie", "2"="Gentoo", "3"="Chinstrap"))

test$Species.pred = specie.pred$especie

