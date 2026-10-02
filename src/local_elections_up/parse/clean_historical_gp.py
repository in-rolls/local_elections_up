"""Reproduce the recorded 2005/2010 cleaning rules.

The original notebooks survive in commit 42fb6190469688fd558596460aef44282e37f6d2.
Frequency-selected reservation labels and field precedence reproduce those
preparations; changing them requires a separately reviewed data correction.
"""

import re

import numpy as np

GP_RES_STATUS = [
    "अनारक्षित",
    "महिला",
    "अनुसूचित जाति - महिला",
    "पिछड़ी जाति - महिला",
    "पिछड़ी जाति",
    "अनुसूचित जाति",
    "पिछड़ी जाति महिला -",
    "अनुसूचित जाति महिला -महिलाअनुसूचित जाति महिला -",
    "पिछड़ी जाति महिला",
    "अनुसूचित जाति महिला",
    "पिछड़ी जाति महिला -अनुसूचित जाति महिला -",
    "पिछड़ी जाति महिला --",
    "अनुसूचित जाति महिला - ",
]


def process_info(info):
    if not isinstance(info, str):
        return ("", "", None)
    gender = ""
    age = None
    keywords = {"महिला": "woman", "पुरुष": "man"}
    age_pattern = re.compile("\\b\\d+\\b")
    found_age = age_pattern.findall(info)
    if found_age:
        age = int(found_age[0])
        info = age_pattern.sub("", info).strip()
    for keyword, _eng_gender in keywords.items():
        if keyword in info:
            gender = keyword
            info = info.replace(keyword, "").strip()
    return (info, gender, age)


def clean_2005(data):
    data = data.copy()
    data["gp_name"] = (
        data["gp_name"]
        .str.strip()
        .str.replace("^(\\s?-\\s?|\\s?--\\s?)|(\\s-|\\s--|\\s---)$", "", regex=True)
        .str.replace("\\s{2,}", " ", regex=True)
        .str.strip()
        .str.strip()
        .str.replace("[0-9\\[\\]]", "", regex=True)
    )
    gp_res_status = GP_RES_STATUS
    data["gp_res_status_temp"] = np.where(
        data["gp_name"].str.strip().isin(gp_res_status), data["gp_name"], ""
    )
    pattern = "|".join(map(re.escape, gp_res_status))
    data["gp_name_fin"] = (
        data["gp_name"].str.replace(pattern, "", regex=True).str.strip()
    )
    data["gp_res_status_fin"] = data.apply(
        lambda x: (
            x["gp_res_status_temp"]
            if x["gp_res_status_temp"] != ""
            else x["gp_reservation_status"]
        ),
        axis=1,
    )
    data["gp_res_status_fin"] = (
        data["gp_res_status_fin"]
        .str.strip()
        .str.replace("^(\\s?-\\s?|\\s?--\\s?)|(\\s-|\\s--|\\s---)$", "", regex=True)
        .str.strip()
        .str.replace("\\s{2,}", " ", regex=True)
        .str.strip()
    )
    valid_categories = data["gp_res_status_fin"].value_counts()[:12].index.to_list()
    valid_categories.extend(
        ["अनुसूचित जन जाति", "अनुसूचित जन जाति महिल", "अनुसूचित जनजाति महिल", "पिछड़ी जाति"]
    )
    data["gp_res_status_fin"] = np.where(
        data["gp_res_status_fin"].isin(valid_categories), data["gp_res_status_fin"], ""
    )
    translit_dict = {
        "अनारक्षित": "Unreserved",
        "पिछड़ी जाति": "Other Backward Class",
        "महिला": "Female",
        "अनुसूचित जाति": "Scheduled Caste",
        "पिछड़ी जाति - महिला": "Other Backward Class - Female",
        "पिछड़ी जाति महिला": "Other Backward Class - Female",
        "अनुसूचित जाति - महिला": "Scheduled Caste - Female",
        "अनुसूचित जाति महिला": "Scheduled Caste - Female",
        "पिछडी जाति": "Other Backward Class",
        "पिछडी जाति - महिला": "Other Backward Class - Female",
        "पिछड़ी जाति महिला": "Other Backward Class - Female",
        "": "Unknown",
        "अनुसूचित जन जाति": "Scheduled Tribe",
        "अनुसूचित जनजाति महिल": "Scheduled Tribe - Female",
        "अनुसूचित जन जाति - महिला": "Scheduled Tribe - Female",
        "पिछड़ी जाति - महिला": "Other Backward Class - Female",
        "पिछडी जाति महिला": "Other Backward Class - Female",
        "अनुसूचित जन जाति महिल": "Scheduled Tribe - Female",
    }
    data["gp_res_status_fin_eng"] = data["gp_res_status_fin"].map(translit_dict)
    data["candidate_res_status_fin"], data["cand_sex_t"], data["age_t"] = zip(
        *data["candidate_res_status"].apply(process_info), strict=True
    )
    data["educ_t2"], data["cand_sex_t2"], data["age_t2"] = zip(
        *data["sex"].apply(process_info), strict=True
    )
    data["cand_sex_fin"] = data.apply(
        lambda x: x["cand_sex_t"] if x["cand_sex_t2"] == "" else x["cand_sex_t2"],
        axis=1,
    )
    data.drop(
        columns=["gp_res_status_temp", "cand_sex_t", "age_t", "educ_t2", "cand_sex_t2"],
        inplace=True,
    )
    return data


def clean_2010(data):
    data = data.copy()
    data["gp_name_temp"] = (
        data["sr_gp_combo"]
        .str.strip()
        .str.replace("[0-9\\[\\]]", "", regex=True)
        .str.strip()
    )
    data["gp_name"] = (
        data["gp_name"]
        .str.strip()
        .str.replace("^(\\s?-\\s?|\\s?--\\s?)|(\\s-|\\s--|\\s---)$", "", regex=True)
        .str.replace("\\s{2,}", " ", regex=True)
        .str.strip()
        .str.replace("[0-9\\[\\]]", "", regex=True)
    )
    gp_res_status = GP_RES_STATUS
    data["gp_res_status_temp"] = np.where(
        data["gp_name"].str.strip().isin(gp_res_status), data["gp_name"], ""
    )
    pattern = "|".join(map(re.escape, gp_res_status))
    data["gp_name_fin"] = (
        data["gp_name"].str.replace(pattern, "", regex=True).str.strip()
    )
    data["gp_name_fin"] = data.apply(
        lambda x: x["gp_name_temp"] if x["gp_name_temp"] != "" else x["gp_name_fin"],
        axis=1,
    )
    data["gp_res_status_fin"] = data.apply(
        lambda x: (
            x["gp_res_status_temp"]
            if x["gp_res_status_temp"] != ""
            else x["gp_reservation_status"]
        ),
        axis=1,
    )
    data["gp_res_status_fin"] = (
        data["gp_res_status_fin"]
        .str.strip()
        .str.replace("^(\\s?-\\s?|\\s?--\\s?)|(\\s-|\\s--|\\s---)$", "", regex=True)
        .str.strip()
        .str.replace("\\s{2,}", " ", regex=True)
        .str.strip()
    )
    valid_categories = data["gp_res_status_fin"].value_counts()[:15].index.to_list()
    valid_categories.extend(
        [
            "अनुसूचित जन जाति",
            "अनुसूचित जन जाति महिल",
            "पिछड़ी जाति",
            "अनुसूचित जन जाति - महिला",
        ]
    )
    data["gp_res_status_fin"] = np.where(
        data["gp_res_status_fin"].isin(valid_categories), data["gp_res_status_fin"], ""
    )
    translit_dict = {
        "अनारक्षित": "Unreserved",
        "पिछड़ी जाति": "Other Backward Class",
        "महिला": "Female",
        "अनुसूचित जाति": "Scheduled Caste",
        "पिछड़ी जाति - महिला": "Other Backward Class - Female",
        "पिछड़ी जाति महिला": "Other Backward Class - Female",
        "अनुसूचित जाति - महिला": "Scheduled Caste - Female",
        "अनुसूचित जाति महिला": "Scheduled Caste - Female",
        "पिछडी जाति": "Other Backward Class",
        "पिछडी जाति - महिला": "Other Backward Class - Female",
        "पिछड़ी जाति महिला": "Other Backward Class - Female",
        "": "Unknown",
        "अनुसूचित जन जाति": "Scheduled Tribe",
        "अनुसूचित जन जाति - महिला": "Scheduled Tribe - Female",
        "पिछड़ी जाति - महिला": "Other Backward Class - Female",
        "पिछडी जाति महिला": "Other Backward Class - Female",
    }
    data["gp_res_status_fin_eng"] = data["gp_res_status_fin"].map(translit_dict)
    data["candidate_res_status_fin"], data["cand_sex_t"], data["age_t"] = zip(
        *data["candidate_res_status"].apply(process_info), strict=True
    )
    data["educ_t2"], data["cand_sex_t2"], data["age_t2"] = zip(
        *data["sex"].apply(process_info), strict=True
    )
    data["educ_t3"], data["cand_sex_t3"], data["age_t3"] = zip(
        *data["age"].apply(process_info), strict=True
    )
    data["educ_t4"], data["cand_sex_t4"], data["age_t4"] = zip(
        *data["education"].apply(process_info), strict=True
    )
    data["cand_sex_fin"] = data.apply(
        lambda x: x["cand_sex_t2"] if x["cand_sex_t3"] == "" else x["cand_sex_t3"],
        axis=1,
    )
    data["age_fin"] = data.apply(
        lambda x: x["age_t2"] if x["age_t3"] == "" else x["age_t3"], axis=1
    )
    data["educ_fin"] = data.apply(
        lambda x: x["educ_t2"] if x["educ_t3"] == "" else x["educ_t3"], axis=1
    )
    data["educ_fin"] = data.apply(
        lambda x: x["educ_fin"] if x["educ_t4"] == "" else x["educ_t4"], axis=1
    )
    translit_dict = {
        "साक्षर": "Literate",
        "हाई स्कूल": "High School",
        "इण्टर": "Intermediate",
        "प्राईमरी": "Primary",
        "जूनियर हाई स्कूल": "Junior High School",
        "स्नातक": "Graduate",
        "निरक्षर": "Illiterate",
        "परास्नातक": "Postgraduate",
    }
    data["educ_fin_eng"] = data["educ_fin"].map(translit_dict)
    data.drop(
        columns=[
            "gp_name_temp",
            "gp_res_status_temp",
            "cand_sex_t",
            "age_t",
            "educ_t2",
            "cand_sex_t2",
            "age_t2",
            "cand_sex_t3",
            "age_t3",
            "educ_t3",
            "cand_sex_t4",
            "age_t4",
            "educ_t4",
        ],
        inplace=True,
    )
    return data
