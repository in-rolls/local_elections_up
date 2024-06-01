# Load libs.
library(readr)
library(arrow)
library(tidyverse)
library(stringi)

# Load dat
up_2005 <- read_parquet("data/fin/up_gp_sarpanch_2005_fixed_with_transliteration.parquet")
up_2010 <- read_parquet("data/fin/up_gp_sarpanch_2010_fixed_with_transliteration.parquet")
up_2015 <- read_parquet("data/fin/up_gp_sarpanch_2015_fixed_with_transliteration.parquet")
up_2021 <- read_parquet("data/fin/up_gp_sarpanch_2021_fixed_with_transliteration.parquet")

# Let's filter to winners for 2021
up_2021 <- up_2021 %>% filter(result == 'विजेता')

# See https://en.wikipedia.org/wiki/Kanpur_Dehat_district
up_2010$district_name     <- ifelse(up_2010$district_name == "रमाबाई नगर", "कानपुर देहात", up_2010$district_name)
up_2010$district_name_eng <- ifelse(up_2010$district_name_eng == "Ramabai Nagar", "Kanpur Dehat", up_2010$district_name_eng)

# Transform
up_2005_dedupe <- up_2005 %>%
     mutate(female_res = grepl("Female", gp_res_status_fin_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name_fin)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))
up_2010_dedupe <- up_2010 %>%
     mutate(female_res = grepl("Female", gp_res_status_fin_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name_fin)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))
up_2015_dedupe <- up_2015 %>%
     mutate(female_res = grepl("Female", gp_reservation_status_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))
up_2021_dedupe <- up_2021 %>%
     mutate(female_res = grepl("Female", gp_reservation_status_eng, ignore.case = TRUE),
            key = normalize_string(paste(district_name, block_name, gp_name)),
            eng_key = normalize_string(paste(district_name_eng, block_name_eng, gp_name_eng))) %>%
     filter (!duplicated(key))

# Join
up_05_10 <- inner_join(up_2005_dedupe, up_2010_dedupe, by = "key", suffix = c("_2005", "_2010"))
up_10_15 <- inner_join(up_2010_dedupe, up_2015_dedupe, by = "key", suffix = c("_2010", "_2015"))
up_15_21 <- inner_join(up_2015_dedupe, up_2021_dedupe, by = "key", suffix = c("_2015", "_2021"))
up_all   <- inner_join(up_05_10, up_15_21, by = "key")





