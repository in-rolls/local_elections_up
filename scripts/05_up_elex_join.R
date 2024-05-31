# Load libs.
library(readr)
library(tidyverse)
library(stringi)

# Load dat
up_2005 <- read_csv("local_elections_up/up_gp_sarpanch_2005_fixed_with_transliteration.csv")
up_2010 <- read_csv("local_elections_up/up_gp_sarpanch_2010_fixed_with_transliteration.csv")

# See https://en.wikipedia.org/wiki/Kanpur_Dehat_district
up_2010$district_name     <- ifelse(up_2010$district_name == "रमाबाई नगर", "कानपुर देहात", up_2010$district_name)
up_2010$district_name_eng <- ifelse(up_2010$district_name_eng == "Ramabai Nagar", "Kanpur Dehat", up_2010$district_name_eng)

# Reservation
up_2005 <- up_2005 %>%
     mutate(female_res = grepl("Female", gp_res_status_fin_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name_fin)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))
up_2010 <- up_2010 %>%
     mutate(female_res = grepl("Female", gp_res_status_fin_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name_fin)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))

# Join
up_all <- inner_join(up_2005_dedupe, up_2010_dedupe, by = "key", suffix = c("_2005", "_2010"))
