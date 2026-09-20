# Data catalog

Counts describe records, not necessarily distinct seats. Contract checks do not certify source accuracy.

| Table | Rows | Years | Grain | Validation |
| --- | ---: | --- | --- | --- |
| [gp/gp_head_candidates_2021](gp/gp_head_candidates_2021.parquet) | 373,096 | 2021 | one candidate | contract_checked |
| [gp/gp_head_election_records](gp/gp_head_election_records.parquet) | 212,525 | 2005, 2010, 2015, 2021 | one winner-list or winner-marked record | contract_checked |
| [gp/gp_head_winner_records_2005](gp/gp_head_winner_records_2005.parquet) | 51,872 | 2005 | one winner-list source record | contract_checked |
| [gp/gp_head_winner_records_2010](gp/gp_head_winner_records_2010.parquet) | 51,861 | 2010 | one winner-list source record | contract_checked |
| [gp/gp_head_winner_records_2015](gp/gp_head_winner_records_2015.parquet) | 59,019 | 2015 | one winner-list source record | contract_checked |
| [offices/up_gram_panchayat_head_declared_winner](offices/up_gram_panchayat_head_declared_winner.parquet) | 212,525 | 2005, 2010, 2015, 2021 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_gram_panchayat_head_seat_reservation](offices/up_gram_panchayat_head_seat_reservation.parquet) | 59,426 | 2015, 2021 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_gram_panchayat_member_seat_reservation](offices/up_gram_panchayat_member_seat_reservation.parquet) | 743,685 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_mayor_candidate_record](offices/up_municipal_corporation_mayor_candidate_record.parquet) | 145 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_mayor_declared_winner](offices/up_municipal_corporation_mayor_declared_winner.parquet) | 28 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_mayor_seat_reservation](offices/up_municipal_corporation_mayor_seat_reservation.parquet) | 30 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_ward_member_candidate_record](offices/up_municipal_corporation_ward_member_candidate_record.parquet) | 8,010 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_ward_member_declared_winner](offices/up_municipal_corporation_ward_member_declared_winner.parquet) | 2,280 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_corporation_ward_member_seat_reservation](offices/up_municipal_corporation_ward_member_seat_reservation.parquet) | 2,460 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_chair_candidate_record](offices/up_municipal_council_chair_candidate_record.parquet) | 1,619 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_chair_declared_winner](offices/up_municipal_council_chair_declared_winner.parquet) | 392 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_chair_seat_reservation](offices/up_municipal_council_chair_seat_reservation.parquet) | 394 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_ward_member_candidate_record](offices/up_municipal_council_ward_member_candidate_record.parquet) | 22,952 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_ward_member_declared_winner](offices/up_municipal_council_ward_member_declared_winner.parquet) | 10,358 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_municipal_council_ward_member_seat_reservation](offices/up_municipal_council_ward_member_seat_reservation.parquet) | 10,131 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_chair_candidate_record](offices/up_nagar_panchayat_chair_candidate_record.parquet) | 3,099 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_chair_declared_winner](offices/up_nagar_panchayat_chair_declared_winner.parquet) | 861 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_chair_seat_reservation](offices/up_nagar_panchayat_chair_seat_reservation.parquet) | 967 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_ward_member_candidate_record](offices/up_nagar_panchayat_ward_member_candidate_record.parquet) | 17,714 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_ward_member_declared_winner](offices/up_nagar_panchayat_ward_member_declared_winner.parquet) | 10,592 | 2012, 2017 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_nagar_panchayat_ward_member_seat_reservation](offices/up_nagar_panchayat_ward_member_seat_reservation.parquet) | 12,135 | 2012, 2023 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_head_declared_winner](offices/up_panchayat_samiti_head_declared_winner.parquet) | 816 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_head_elected_official](offices/up_panchayat_samiti_head_elected_official.parquet) | 820 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_head_reported_official](offices/up_panchayat_samiti_head_reported_official.parquet) | 821 | 2010 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_head_seat_reservation](offices/up_panchayat_samiti_head_seat_reservation.parquet) | 933 | 1995, 2000, 2005, 2010, 2015, 2021 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_junior_deputy_elected_official](offices/up_panchayat_samiti_junior_deputy_elected_official.parquet) | 819 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_member_declared_winner](offices/up_panchayat_samiti_member_declared_winner.parquet) | 77,743 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_member_reported_official](offices/up_panchayat_samiti_member_reported_official.parquet) | 127,598 | 2005, 2010 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_member_seat_reservation](offices/up_panchayat_samiti_member_seat_reservation.parquet) | 80,993 | 2015, 2021 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_member_source_status_notice](offices/up_panchayat_samiti_member_source_status_notice.parquet) | 12 | 2010 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_panchayat_samiti_senior_deputy_elected_official](offices/up_panchayat_samiti_senior_deputy_elected_official.parquet) | 820 | 2006 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_head_declared_winner](offices/up_zilla_parishad_head_declared_winner.parquet) | 74 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_head_elected_official](offices/up_zilla_parishad_head_elected_official.parquet) | 70 | 2005 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_head_reported_official](offices/up_zilla_parishad_head_reported_official.parquet) | 72 | 2010 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_head_seat_reservation](offices/up_zilla_parishad_head_seat_reservation.parquet) | 75 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_member_declared_winner](offices/up_zilla_parishad_member_declared_winner.parquet) | 3,121 | 2015 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_member_elected_official](offices/up_zilla_parishad_member_elected_official.parquet) | 2,561 | 2005 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_member_reported_official](offices/up_zilla_parishad_member_reported_official.parquet) | 2,624 | 2010 | one source observation; sources may overlap | provisional_source_observations |
| [offices/up_zilla_parishad_member_seat_reservation](offices/up_zilla_parishad_member_seat_reservation.parquet) | 3,503 | 1995, 2000, 2005, 2010, 2015, 2021 | one source observation; sources may overlap | provisional_source_observations |
| [panels/gp_adjacent_links](panels/gp_adjacent_links.parquet) | 128,687 | see source documentation | one accepted adjacent-wave link | geographic_linkage |
| [panels/gp_four_election_links](panels/gp_four_election_links.parquet) | 29,734 | see source documentation | one linked four-election history | geographic_linkage |
| [panels/gp_lgd_bridge](panels/gp_lgd_bridge.parquet) | 157,186 | see source documentation | one historical panel row projected to the LGD vintage | geographic_linkage |
| [panels/gp_link_candidates](panels/gp_link_candidates.parquet) | 129,752 | see source documentation | one assessed adjacent-wave linkage candidate | geographic_linkage |
| [panels/gp_panel_2005_2010](panels/gp_panel_2005_2010.parquet) | 42,622 | see source documentation | one linked source-record pair or four-election history | geographic_linkage |
| [panels/gp_panel_2005_2010_2015_2021](panels/gp_panel_2005_2010_2015_2021.parquet) | 29,734 | see source documentation | one linked source-record pair or four-election history | geographic_linkage |
| [panels/gp_panel_2010_2015](panels/gp_panel_2010_2015.parquet) | 39,551 | see source documentation | one linked source-record pair or four-election history | geographic_linkage |
| [panels/gp_panel_2015_2021](panels/gp_panel_2015_2021.parquet) | 46,514 | see source documentation | one linked source-record pair or four-election history | geographic_linkage |
| [weaver/weaver_20250302_wide](weaver/weaver_20250302_wide.parquet) | 105,527 | see source documentation | one source GP identifier, wide across waves | external_source_preparation |
| [weaver/weaver_20250317_wide](weaver/weaver_20250317_wide.parquet) | 61,338 | see source documentation | one source GP identifier, wide across waves | external_source_preparation |
