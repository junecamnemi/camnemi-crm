# ad-hoc legacy scripts (archived 2026-09-29)

380 one-off scripts that **nothing references** (no import, no subprocess, no cron job,
no skill doc) were moved out of `backend/` so the guide pipeline has ONE management point:

- collector `backend/guide_page_collect.py` · census `backend/guide_census.py` ·
  entry point `backend/run_guide_kb_pipeline.py` · data home `backend/_pipeline_data/`

Scripts still referenced by cron/code/docs stay in `backend/` (81 of them) and are listed
in `adhoc_legacy_MANIFEST.json` → `kept_in_place`.

## Restore everything

```bash
cd /c/Users/wisew/camnemi-crm/backend/_pipeline_data/archive
python -c "import json,shutil;m=json.load(open('adhoc_legacy_MANIFEST.json'));[shutil.move(f['to'],f['from']) for f in m['files']]"
```

## Sibling folder

`_pipeline_data/archive/adhoc_2026-09-29/` (subdir `scripts/`, data in `data/`) holds the 19
guide-collection one-offs that the single collector/census modules replaced:
`_collect_junior_lang.py`, `_collect_junior_lang_strong.py`, `_collect_junior_lang_final.py`,
`_collect_junior_lang_last3.py`, `_collect_htmlonly.py`, `_retry_htmlonly.py`,
`_discover_junior_lang.py`, `_probe_junior_lang_links.py`, `_probe_last3.py`, `_probe_chsu*.py`,
`_build_htmlonly_targets.py`, `_census_final.py`, `_qa_lang_files.py`, `_fake_pdf_audit.py`,
`_htmlonly_audit.py`, `_junior_lang_audit.py`, `_restore_hanyang.py`, `_fix_kwu*.py`, `_note_recollect.py`.

## What is here (grouped by script prefix)

### `_add_*` (15)
- `_add_8lang_cdb.py` — !/usr/bin/env python3
- `_add_8lang_kb.py` — !/usr/bin/env python3
- `_add_inha.py` — 인하대 직접 확보
- `_add_jei_lang.py` — !/usr/bin/env python3
- `_add_junior_lang_urls.py` — !/usr/bin/env python3
- `_add_junior_lang_urls2.py` — !/usr/bin/env python3
- `_add_junior_langnote.py` — !/usr/bin/env python3
- `_add_kyungwoon_ma.py` — -*- coding: utf-8 -*-
- `_add_lang.py`
- `_add_ma.py` — 직접 브라우저로 확보한 ma/lang URL
- `_add_ma_new.py` — -*- coding: utf-8 -*-
- `_add_ma_to_kb.py` — !/usr/bin/env python3
- `_add_selftest_kb.py` — !/usr/bin/env python3
- `_add_sogang_ma.py` — !/usr/bin/env python3
- `_add_student_count.py` — !/usr/bin/env python3

### `_analyze_*` (2)
- `_analyze_manual_astra.py` — !/usr/bin/env python3
- `_analyze_review_batch.py` — !/usr/bin/env python3

### `_apply_*` (11)
- `_apply_applysystems.py` — !/usr/bin/env python3
- `_apply_exclusions.py` — !/usr/bin/env python3
- `_apply_ipsi_probe.py` — 후보에서 외국인 학부 입학 URL 선별
- `_apply_jr_lang.py` — 어학원 URL 선별
- `_apply_jr_lang2.py` — 어학원 URL 선별
- `_apply_jr_picks.py` — 부적합 URL 제외 (카카오 등)
- `_apply_jr_results.py` — 배치 결과에서 ba_foreign_url 반영
- `_apply_lang_preserve.py` — !/usr/bin/env python3
- `_apply_primary.py` — !/usr/bin/env python3
- `_apply_system_scan.py` — !/usr/bin/env python3
- `_apply_ws2.py` — 최종 커버리지

### `_astra_*` (2)
- `_astra_pdf.py` — !/usr/bin/env python3
- `_astra_sections.py` — !/usr/bin/env python3

### `_audit_*` (19)
- `_audit_10.py`
- `_audit_11.py` — LANG gap recount with norm match
- `_audit_12.py`
- `_audit_2.py` — field frequency
- `_audit_3.py` — missing lists (top few)
- `_audit_3layer.py` — -*- coding: utf-8 -*-
- `_audit_3tier.py`
- `_audit_4.py`
- `_audit_5.py` — sample program
- `_audit_6.py` — KB vs CDB per-field diff for BA scholarship & MA tuition & ielts
- `_audit_7.py` — bracket match
- `_audit_8.py` — how many data.js entries carry any lang data field
- `_audit_9.py` — duplicate-ish keys in MA
- `_audit_final_cov.py` — 전문대 PDF
- `_audit_guide_final.py` — per-school level->set(urls)
- `_audit_guide_links.py` — 요구 레벨
- `_audit_guides.py` — 1) unvcd_index (등록유지 228) 로드
- `_audit_homepage_links.py` — 1) scrape_map (학교 자체) 레벨별 URL — 등록유지
- `_audit_pdffolders.py` — 샘플 파일명

### `_backfill_*` (3)
- `_backfill_ba_url.py` — -*- coding: utf-8 -*-
- `_backfill_dept_tuition.py` — -*- coding: utf-8 -*-
- `_backfill_kb_fields.py` — -*- coding: utf-8 -*-

### `_build_*` (5)
- `_build_discover_targets.py` — !/usr/bin/env python3
- `_build_kb.py` — !/usr/bin/env python3
- `_build_konyang_d4_pdf.py` — -*- coding: utf-8 -*-
- `_build_lang_kb.py` — -*- coding: utf-8 -*-
- `_build_visa_kb.py` — !/usr/bin/env python3

### `_categorize_*` (1)
- `_categorize_scholarships.py` — !/usr/bin/env python3

### `_che_*` (1)
- `_che_all_pro.py` — !/usr/bin/env python3

### `_check_*` (2)
- `_check_adiga_junior.py` — !/usr/bin/env python3
- `_check_bangmun.py`

### `_chk_*` (2)
- `_chk_foreign.py` — 1) 전문대 폴더 - 외국인 여부 (파일명/내용으로 확인)
- `_chk_manifest.py`

### `_classify_*` (1)
- `_classify_foreign.py` — -*- coding: utf-8 -*-

### `_clean_*` (3)
- `_clean_junior_deg.py` — -*- coding: utf-8 -*-
- `_clean_rediscover.py` — !/usr/bin/env python3
- `_clean_wave2.py` — -*- coding: utf-8 -*-

### `_cmp_*` (1)
- `_cmp_ma.py`

### `_coll_*` (2)
- `_coll_ajax_probe.py` — !/usr/bin/env python3
- `_coll_list_probe.py` — !/usr/bin/env python3

### `_combined_*` (1)
- `_combined_pro.py` — !/usr/bin/env python3

### `_compare_*` (1)
- `_compare_scholarship.py` — -*- coding: utf-8 -*-

### `_curation_*` (1)
- `_curation_ma_extract.py`

### `_dbg_*` (8)
- `_dbg_acad.py` — 테이블 목록
- `_dbg_acad2.py` — !/usr/bin/env python3
- `_dbg_datagokr.py` — 찾기: academyinfo-mcp 설치 여부 / data.go.kr 키 / 기존 스냅샷
- `_dbg_filter.py` — 제외 목록 상세
- `_dbg_gachon.py`
- `_dbg_ipsi.py` — capture full quoted arg
- `_dbg_match.py` — adiga 기본 URL과 매칭
- `_dbg_stats.py` — univDetail 전체에서 통계 관련 라벨/탭 스캔

### `_debug_*` (1)
- `_debug_call.py` — !/usr/bin/env python3

### `_dedup_*` (1)
- `_dedup_consulting.py` — -*- coding: utf-8 -*-

### `_dedupe_*` (1)
- `_dedupe_inha.py` — !/usr/bin/env python3

### `_deep_*` (3)
- `_deep_extract_all.py` — -*- coding: utf-8 -*-
- `_deep_verify.py` — !/usr/bin/env python3
- `_deep_verify2.py` — !/usr/bin/env python3

### `_detail_*` (1)
- `_detail_analysis.py` — !/usr/bin/env python3

### `_deu_*` (1)
- `_deu_guide.py` — !/usr/bin/env python3

### `_diag_*` (2)
- `_diag_search.py` — !/usr/bin/env python3
- `_diag_search2.py` — !/usr/bin/env python3

### `_dl_*` (3)
- `_dl_kyungwoon.py` — !/usr/bin/env python3
- `_dl_manuals.py` — !/usr/bin/env python3
- `_dl_manuals2.py` — !/usr/bin/env python3

### `_dongcui_*` (1)
- `_dongcui_lang.py` — !/usr/bin/env python3

### `_duksung_*` (1)
- `_duksung_lang.py` — !/usr/bin/env python3

### `_dump_*` (2)
- `_dump_ic_bc.py` — !/usr/bin/env python3
- `_dump_notes.py` — !/usr/bin/env python3

### `_eng_*` (5)
- `_eng_all.py` — !/usr/bin/env python3
- `_eng_majors_dump.py` — !/usr/bin/env python3
- `_eng_more.py` — !/usr/bin/env python3
- `_eng_track_precise.py` — !/usr/bin/env python3
- `_eng_track_scan.py` — !/usr/bin/env python3

### `_enum_*` (1)
- `_enum_junior_adiga.py` — !/usr/bin/env python3

### `_extract_*` (5)
- `_extract_8lang.py` — !/usr/bin/env python3
- `_extract_batch3.py` — -*- coding: utf-8 -*-
- `_extract_bypass.py` — -*- coding: utf-8 -*-
- `_extract_bypass_missing.py` — -*- coding: utf-8 -*-
- `_extract_junior_list.py` — !/usr/bin/env python3

### `_faq_*` (1)
- `_faq_verify_pro.py` — !/usr/bin/env python3

### `_fetch_*` (1)
- `_fetch_opus_sample.py` — !/usr/bin/env python3

### `_fill_*` (1)
- `_fill_lang_urls_confident.py` — -*- coding: utf-8 -*-

### `_final_*` (4)
- `_final_jr.py` — 여주대·송곡대 - 입시홈페이지 메인으로 기록 (외국인 전형은 adiga PDF로 커버)
- `_final_koreatech.py` — unvcd_index에 반영
- `_final_one_per_school.py` — -*- coding: utf-8 -*-
- `_final_verified.py` — !/usr/bin/env python3

### `_finalize_*` (1)
- `_finalize_univ4.py` — 1) 학부 외국인 URL

### `_find_*` (8)
- `_find_foreign_redo.py` — -*- coding: utf-8 -*-
- `_find_guide_gaps.py` — -*- coding: utf-8 -*-
- `_find_imgonly.py` — !/usr/bin/env python3
- `_find_junior_codes.py` — !/usr/bin/env python3
- `_find_lang_urls.py` — -*- coding: utf-8 -*-
- `_find_manuals.py` — !/usr/bin/env python3
- `_find_paging.py` — !/usr/bin/env python3
- `_find_paging2.py` — !/usr/bin/env python3

### `_fix_*` (7)
- `_fix_en_names.py` — !/usr/bin/env python3
- `_fix_kw_grad_scholar.py` — !/usr/bin/env python3
- `_fix_kw_scholar.py` — !/usr/bin/env python3
- `_fix_kwu2.py`
- `_fix_ma_lang.py` — !/usr/bin/env python3
- `_fix_scholarships.py` — !/usr/bin/env python3
- `_fix_seoul_univs.py` — !/usr/bin/env python3

### `_foreign_*` (1)
- `_foreign_pages.py` — -*- coding: utf-8 -*-

### `_full_*` (1)
- `_full_search.py` — !/usr/bin/env python3

### `_gap_*` (1)
- `_gap_all_levels.py` — -*- coding: utf-8 -*-

### `_gen_*` (2)
- `_gen_batches.py` — !/usr/bin/env python3
- `_gen_kw_fee_pdf.py` — !/usr/bin/env python3

### `_gksu_*` (1)
- `_gksu_scan_all.py` — -*- coding: utf-8 -*-

### `_guide_*` (1)
- `_guide_gap_by_level.py` — -*- coding: utf-8 -*-

### `_hikorea_*` (1)
- `_hikorea_links.py` — !/usr/bin/env python3

### `_hwp_*` (17)
- `_hwp_api_probe.py` — !/usr/bin/env python3
- `_hwp_com.py` — !/usr/bin/env python3
- `_hwp_com2.py` — !/usr/bin/env python3
- `_hwp_com3.py` — !/usr/bin/env python3
- `_hwp_com4.py` — !/usr/bin/env python3
- `_hwp_copy3.py` — !/usr/bin/env python3
- `_hwp_copy_running.py` — !/usr/bin/env python3
- `_hwp_extract_all.py` — !/usr/bin/env python3
- `_hwp_ocr.py` — !/usr/bin/env python3
- `_hwp_open_visible.py` — !/usr/bin/env python3
- `_hwp_print.py` — !/usr/bin/env python3
- `_hwp_print2.py` — !/usr/bin/env python3
- `_hwp_read.py` — BodyText/Section0 (often zlib raw deflate)
- `_hwp_render_probe.py` — !/usr/bin/env python3
- `_hwp_text.py` — !/usr/bin/env python3
- `_hwp_text2.py` — !/usr/bin/env python3
- `_hwp_viewtext.py` — !/usr/bin/env python3

### `_identify_*` (1)
- `_identify_exclusions.py` — !/usr/bin/env python3

### `_ielts_*` (1)
- `_ielts_verify.py` — !/usr/bin/env python3

### `_ielts50_*` (2)
- `_ielts50_scan.py` — !/usr/bin/env python3
- `_ielts50_scan2.py` — !/usr/bin/env python3

### `_incheon_*` (1)
- `_incheon_bucheon.py` — !/usr/bin/env python3

### `_index_*` (1)
- `_index_foreign_guides.py` — 파일명에서 unvCd_학교명[캠퍼스]_연도_타입 추출

### `_inspect_*` (4)
- `_inspect_hikorea.py`
- `_inspect_hk_detail.py`
- `_inspect_job.py`
- `_inspect_my_fetches.py` — -*- coding: utf-8 -*-

### `_jbnu_*` (1)
- `_jbnu_check.py` — !/usr/bin/env python3

### `_job_*` (2)
- `_job_manual_pro.py` — !/usr/bin/env python3
- `_job_merge.py` — !/usr/bin/env python3

### `_junior_*` (9)
- `_junior_deepscan.py` — -*- coding: utf-8 -*-
- `_junior_direct_dl.py` — -*- coding: utf-8 -*-
- `_junior_direct_scan.py` — -*- coding: utf-8 -*-
- `_junior_filedown_dl.py` — -*- coding: utf-8 -*-
- `_junior_foreign_status.py` — -*- coding: utf-8 -*-
- `_junior_gap_report.py` — !/usr/bin/env python3
- `_junior_lang_audit.py` — -*- coding: utf-8 -*-
- `_junior_render.py` — -*- coding: utf-8 -*-
- `_junior_render_par.py` — -*- coding: utf-8 -*-

### `_kb_*` (2)
- `_kb_gap_analysis.py` — -*- coding: utf-8 -*-
- `_kb_guide_pathcheck.py` — -*- coding: utf-8 -*-

### `_kbeauty_*` (1)
- `_kbeauty_report.py` — -*- coding: utf-8 -*-

### `_kw_*` (13)
- `_kw_2hakgi.py`
- `_kw_2hakgi_ocr.py`
- `_kw_analysis.py` — !/usr/bin/env python3
- `_kw_ba_extract.py` — 전형안내: PDF p13~p19 (0-index 12..18)
- `_kw_ba_pdf.py` — page text + which pages mention 외국인/등록금/장학/전형
- `_kw_both_guide.py`
- `_kw_foreign_pdf.py` — find pages mentioning 외국인/이중언어/영어Track/정원외
- `_kw_guide.py`
- `_kw_guide2.py`
- `_kw_ocr_pages.py`
- `_kw_pages.py`
- `_kw_scholar_src.py`
- `_kw_scholar_src2.py` — 1) 대학원 요강에 장학 티어가 있나?

### `_lang_*` (2)
- `_lang_bypass_kyungwoon.py` — -*- coding: utf-8 -*-
- `_lang_verify.py` — !/usr/bin/env python3

### `_library_*` (2)
- `_library_dedupe.py` — -*- coding: utf-8 -*-
- `_library_level_audit.py` — -*- coding: utf-8 -*-

### `_low_*` (1)
- `_low_req_check.py` — !/usr/bin/env python3

### `_ma_*` (12)
- `_ma_cells.py` — -*- coding: utf-8 -*-
- `_ma_cells2.py` — -*- coding: utf-8 -*-
- `_ma_extract.py` — !/usr/bin/env python3
- `_ma_extract_b1.py` — -*- coding: utf-8 -*-
- `_ma_final_analysis.py` — !/usr/bin/env python3
- `_ma_multi_analysis.py` — !/usr/bin/env python3
- `_ma_render.py` — -*- coding: utf-8 -*-
- `_ma_rich_extract.py` — !/usr/bin/env python3
- `_ma_selftest.py` — 1) top-level selftest section
- `_ma_selftest2.py`
- `_ma_selftest3.py` — locate the sentence
- `_ma_tuition_analysis.py` — !/usr/bin/env python3

### `_make_*` (3)
- `_make_pdf.py` — !/usr/bin/env python3
- `_make_pdf_full.py` — !/usr/bin/env python3
- `_make_pdf_sch.py` — !/usr/bin/env python3

### `_manual_*` (20)
- `_manual_jr.py` — 입시홈페이지에서 외국인 링크 발견했지만 선별 못한 5교 수동 보완
- `_manual_jr2.py` — 웹 검색으로 확보한 전문대 외국인 학부 URL
- `_manual_jr_lang.py` — 전주비전대 + 어학원 PDF 있는 학교 수동 보완
- `_manual_jr_lang10.py` — 최종
- `_manual_jr_lang11.py` — 최종
- `_manual_jr_lang12.py` — 최종
- `_manual_jr_lang13.py` — 최종
- `_manual_jr_lang14.py` — 최종
- `_manual_jr_lang15.py` — 최종
- `_manual_jr_lang16.py` — 최종
- `_manual_jr_lang17.py` — 최종
- `_manual_jr_lang2.py`
- `_manual_jr_lang3.py` — 최종
- `_manual_jr_lang4.py`
- `_manual_jr_lang5.py`
- `_manual_jr_lang6.py`
- `_manual_jr_lang7.py`
- `_manual_jr_lang8.py`
- `_manual_jr_lang9.py`
- `_manual_pro.py` — !/usr/bin/env python3

### `_merge_*` (13)
- `_merge_b1.py` — 배치1 결과 20교
- `_merge_b2.py` — 배치2_rest 결과 17교
- `_merge_ba_scholarship.py` — -*- coding: utf-8 -*-
- `_merge_ba_tuition_results.py` — -*- coding: utf-8 -*-
- `_merge_ba_urls.py` — 1) 크롤 결과 21교
- `_merge_bypass_kb.py` — -*- coding: utf-8 -*-
- `_merge_foreign_index.py` — unvCd -> 이름급 매칭용
- `_merge_junior_foreign_kb.py` — -*- coding: utf-8 -*-
- `_merge_lang_tuition.py` — -*- coding: utf-8 -*-
- `_merge_ma_normalized.py` — -*- coding: utf-8 -*-
- `_merge_ma_scholarship.py` — -*- coding: utf-8 -*-
- `_merge_ma_tuition_batches.py` — -*- coding: utf-8 -*-
- `_merge_w2.py` — -*- coding: utf-8 -*-

### `_misc_*` (9)
- `_classify.py` — !/usr/bin/env python3
- `_inventory.py` — 인벤토리: 폴더별 외국인 요강 전수
- `_kcard.py` — !/usr/bin/env python3
- `_kiwu.py` — !/usr/bin/env python3
- `_refscan.py`
- `_refscan2.py`
- `_seojeong.py` — !/usr/bin/env python3
- `_ultimate.py` — !/usr/bin/env python3
- `_xml2md.py` — !/usr/bin/env python3

### `_monitor_*` (1)
- `_monitor_counts.py`

### `_near_*` (3)
- `_near_detail.py` — !/usr/bin/env python3
- `_near_fees.py` — !/usr/bin/env python3
- `_near_namyangju_scan.py` — !/usr/bin/env python3

### `_normalize_*` (3)
- `_normalize_json_format.py`
- `_normalize_langtui.py` — -*- coding: utf-8 -*-
- `_normalize_ma_tuition.py` — -*- coding: utf-8 -*-

### `_ocr_*` (3)
- `_ocr_8lang.py` — !/usr/bin/env python3
- `_ocr_missing.py` — !/usr/bin/env python3
- `_ocr_untrusted.py` — !/usr/bin/env python3

### `_opus_*` (1)
- `_opus_analyze.py` — !/usr/bin/env python3

### `_parse_*` (5)
- `_parse_bypass.py` — -*- coding: utf-8 -*-
- `_parse_bypass_lib.py` — -*- coding: utf-8 -*-
- `_parse_hikorea_astra.py` — !/usr/bin/env python3
- `_parse_mis.py` — -*- coding: utf-8 -*-
- `_parse_scholarship.py` — !/usr/bin/env python3

### `_patch_*` (2)
- `_patch_consulting_fillonly.py` — -*- coding: utf-8 -*-
- `_patch_jobpdf.py`

### `_pick_*` (1)
- `_pick_jr_urls.py` — 후보 중 외국인/국제/입학 관련 URL 선별

### `_prep_*` (28)
- `_prep_all_gap_batches.py` — -*- coding: utf-8 -*-
- `_prep_ba_gap_batches.py` — -*- coding: utf-8 -*-
- `_prep_bypass_batches.py` — -*- coding: utf-8 -*-
- `_prep_collect_batches.py` — -*- coding: utf-8 -*-
- `_prep_curation_batches.py` — -*- coding: utf-8 -*-
- `_prep_curation_v2.py` — -*- coding: utf-8 -*-
- `_prep_foreign_redo.py` — -*- coding: utf-8 -*-
- `_prep_gap_batches.py` — -*- coding: utf-8 -*-
- `_prep_jdeg_batches.py` — -*- coding: utf-8 -*-
- `_prep_jr_browser.py` — 홈페이지 도메인에서 ipsi/iphak 경로 후보 생성
- `_prep_jr_lang2_ws.py`
- `_prep_jr_lang_ws.py`
- `_prep_jr_ws.py` — 3개 배치
- `_prep_jr_ws2.py` — 3개 배치
- `_prep_junior.py`
- `_prep_junior_deg.py` — -*- coding: utf-8 -*-
- `_prep_lang_batches.py` — -*- coding: utf-8 -*-
- `_prep_ma2.py` — -*- coding: utf-8 -*-
- `_prep_ma_batches.py` — -*- coding: utf-8 -*-
- `_prep_ma_lang.py`
- `_prep_ma_lang2.py`
- `_prep_ma_retry.py` — -*- coding: utf-8 -*-
- `_prep_mis_batches.py` — -*- coding: utf-8 -*-
- `_prep_pdf_collection.py` — -*- coding: utf-8 -*-
- `_prep_pharm_check.py` — -*- coding: utf-8 -*-
- `_prep_retry_small.py` — -*- coding: utf-8 -*-
- `_prep_targets2.py` — 미보유 39교의 출발 URL
- `_prep_wave2.py` — -*- coding: utf-8 -*-

### `_print_*` (4)
- `_print_uic.py` — -*- coding: utf-8 -*-
- `_print_uic2.py` — -*- coding: utf-8 -*-
- `_print_uic3.py` — -*- coding: utf-8 -*-
- `_print_uic4.py` — -*- coding: utf-8 -*-

### `_probe_*` (1)
- `_probe_prices.py` — !/usr/bin/env python3

### `_promote_*` (2)
- `_promote_all.py` — !/usr/bin/env python3
- `_promote_scrape.py` — !/usr/bin/env python3

### `_qual_*` (1)
- `_qual_check.py` — !/usr/bin/env python3

### `_read_*` (1)
- `_read_voice.py`

### `_rebuild_*` (2)
- `_rebuild_ba_results.py` — -*- coding: utf-8 -*-
- `_rebuild_ba_results2.py` — -*- coding: utf-8 -*-

### `_reconcile_*` (1)
- `_reconcile_gap.py` — -*- coding: utf-8 -*-

### `_redl_*` (3)
- `_redl_batch.py` — -*- coding: utf-8 -*-
- `_redl_make_targets.py` — -*- coding: utf-8 -*-
- `_redl_worklist.py` — -*- coding: utf-8 -*-

### `_reflag_*` (1)
- `_reflag_visa.py` — -*- coding: utf-8 -*-

### `_render_*` (1)
- `_render_8lang.py` — !/usr/bin/env python3

### `_restore_*` (1)
- `_restore_enrichment_monitor.py` — Re-attach enrichment fields dropped by the consulting DB rebuild.

### `_retry_*` (2)
- `_retry_browser.py` — !/usr/bin/env python3
- `_retry_guides.py` — !/usr/bin/env python3

### `_sajeung_*` (1)
- `_sajeung_pro.py` — !/usr/bin/env python3

### `_scan_*` (11)
- `_scan_apply_pdfs.py` — !/usr/bin/env python3
- `_scan_fees.py` — !/usr/bin/env python3
- `_scan_foreign.py` — 외국인/ 하위폴더와 상위 폴더 모두 포함 전수 스캔
- `_scan_junior_foreign.py` — -*- coding: utf-8 -*-
- `_scan_junior_period.py` — -*- coding: utf-8 -*-
- `_scan_lang_pdfs.py` — -*- coding: utf-8 -*-
- `_scan_lang_tuition_gap.py` — -*- coding: utf-8 -*-
- `_scan_ma_gaps.py` — -*- coding: utf-8 -*-
- `_scan_ma_new.py` — -*- coding: utf-8 -*-
- `_scan_ma_scholarship.py` — -*- coding: utf-8 -*-
- `_scan_pharmacy.py` — -*- coding: utf-8 -*-

### `_sch_*` (1)
- `_sch_verify.py` — !/usr/bin/env python3

### `_sejong_*` (1)
- `_sejong_check.py` — !/usr/bin/env python3

### `_selftest_*` (2)
- `_selftest_scan.py` — !/usr/bin/env python3
- `_selftest_scan2.py` — !/usr/bin/env python3

### `_session_*` (1)
- `_session_paging.py` — !/usr/bin/env python3

### `_swu_*` (2)
- `_swu_lang_check.py` — !/usr/bin/env python3
- `_swu_lang_page.py` — !/usr/bin/env python3

### `_sync_*` (4)
- `_sync_datajs_bypass.py` — -*- coding: utf-8 -*-
- `_sync_datajs_desc.py` — -*- coding: utf-8 -*-
- `_sync_datajs_v2.py` — -*- coding: utf-8 -*-
- `_sync_period_kb.py` — -*- coding: utf-8 -*-

### `_test_*` (1)
- `_test_paging.py` — !/usr/bin/env python3

### `_topik2_*` (2)
- `_topik2_list.py` — -*- coding: utf-8 -*-
- `_topik2_majors.py` — -*- coding: utf-8 -*-

### `_track_*` (1)
- `_track_summary.py` — !/usr/bin/env python3

### `_tuition_*` (4)
- `_tuition_amounts.py` — !/usr/bin/env python3
- `_tuition_compile.py` — !/usr/bin/env python3
- `_tuition_dump.py` — !/usr/bin/env python3
- `_tuition_more.py` — !/usr/bin/env python3

### `_ultra_*` (1)
- `_ultra_final.py` — !/usr/bin/env python3

### `_update_*` (8)
- `_update_4yr_lang_urls.py` — !/usr/bin/env python3
- `_update_crm_lang.py` — !/usr/bin/env python3
- `_update_crm_lang2.py` — !/usr/bin/env python3
- `_update_kb_lang.py` — !/usr/bin/env python3
- `_update_kb_topik6.py` — -*- coding: utf-8 -*-
- `_update_konyang_kb.py` — -*- coding: utf-8 -*-
- `_update_lang2027.py` — !/usr/bin/env python3
- `_update_seoul_winter.py` — -*- coding: utf-8 -*-

### `_verify_*` (6)
- `_verify_collected_2027.py` — !/usr/bin/env python3
- `_verify_datajs.py`
- `_verify_keeper_set.py` — -*- coding: utf-8 -*-
- `_verify_langpdf.py`
- `_verify_restore.py` — -*- coding: utf-8 -*-
- `_verify_scrape.py` — !/usr/bin/env python3

### `_w2_*` (9)
- `_w2_batch1_extract.py` — -*- coding: utf-8 -*-
- `_w2_batch1_render.py` — -*- coding: utf-8 -*-
- `_w2_batch2_extract.py` — -*- coding: utf-8 -*-
- `_w2_batch6_extract.py` — -*- coding: utf-8 -*-
- `_w2_batch6_render_cha.py` — -*- coding: utf-8 -*-
- `_w2_batch8_extract.py` — !/usr/bin/env python3
- `_w2_extract8.py`
- `_w2_render8.py` — render every page at 150 dpi for vision fallback
- `_w2_verify_batch2.py` — -*- coding: utf-8 -*-

### `_watermark_*` (1)
- `_watermark_manuals.py` — -*- coding: utf-8 -*-
