Lia.setDebugMode(true);

var DepartmentIdx = {
    HOME: 1,
    ADMISSION: 11, // 대학입학
    GRAENT: 12, // 대학원 입학
    CSTSENT: 13, // 신학대학원 입학
    CSFUND: 14, // 발전기금
    SANHAK: 15, // 산학협력단
    CSTS : 16, // 신학대학원
    
    // 대학교 학과
    THEOL: 17, // 신학과
    MUSIC: 18, // 교회음악과
    CSEDUCATION: 19, // 기독교교육과
    ENGLISH: 20, // 영어교육과
    HISTORY: 21, // 역사교육과
    CSUCHILD: 22, // 유아교육과
    TEACHER: 23, // 교직과
    CSADONG: 24, // 아동학과
    SOCIALWORK: 25, // 사회복지학과
    REHAB: 26, // 중독상담학과
    KOREAN: 27, // 다문화한국어학과
    HOKMA: 28, // 호크마교양교육
    INDUSTRY: 49, // 산업교육학부

    // 대학원 학과
    GRADUATE : 30, //일반대학원
    EDUCATION : 31, //교육대학원
    MISSION : 32, //선교대학원
    PASTOR : 33, //목회신학전문대학원
    SOCIAL : 34, //사회복지대학원
    COUNSELING : 35, //상담대학원
    CHMUSIC : 36, //교회음악대학원
    PEACE : 38, // 평화통일대학원

    // 부설
    CHAPEL : 39, // 교목실
    CSS: 40, // 부설평생교육원 (양지)

    RTRC: 42, // 개혁신학연구센터
    DORMITORY: 43, // 경건훈련처
    DORMITORY_Y: 44, // 양지생활관
    BIBLICA: 45, // 성지언어연구소
    ASSOCIATION: 47, // 사당생활관
    RESERVE: 48, // 사당생활관
    CSTEACHER: 51, // 교원양성지원센터
};


var MenuId = {
    HOME: {
        NOTICE: 1089,
        NEWS: 1090, // 총신광장 > 총신소식 > 총신소식
        SCHEDULE: 1017,
        MOVEMENT: 878, // 대학소개 > 총장소개 > 총장동정
        PRESS: 1091, // 총신광장 > 총신소식 > 언론속의총신
        PROMOTION: 1093, // 총신광장 > 총신소식 > 홍보영상
        MILITARY: [1426, 1431, 1434], // 예비군, 병무, 민방위
        MINISTRY: 1110, // 사역게시판
        HAKSA_FAQ: 1898
    },
    ADMISSION: {
        NOTICE: 552,
        FAQ: 641,
        QNA: 553
    },
    GRAENT: {
        NOTICE: 638,
        QNA: 639,
        DOC: 576, // 입시소정양식
        QB: 2385,//기출문제
    },
    CSTSENT: {
        NOTICE: 1179,
        QNA: 1180
    },
    CSFUND: {
        INTRO: 846, // 기금소개
        TAX: 870, // 세제혜택
        STORY: 855, // 후원소식 > 후원스토리
        PRESS: 856, // 후원소식 > 보도자료
        // STATUS1: 629, // 후원소식 > 후원현황 > 1004모금
        // STATUS2: 630, // 후원소식 > 후원현황 > 총신100만
        STATUS: 857, // 후원현황 부모메뉴
        STATUS1: 861, // 후원소식 > 후원현황 > 교회 및 단체 후원현황
        STATUS2: 862, // 후원소식 > 후원현황 > 개인후원약정현황
        STATUS3: 863, // 후원소식 > 후원현황 > 100만기도후원회-월별후원금현황
        HONOR1: 867, // 기부자 예우 > 명예의전당 > 5천만 이상
        HONOR2: 868, // 기부자 예우 > 명예의전당 > 5천만 이상
        HONOR3: 869, // 기부자 예우 > 명예의전당 > 1억원 이상
    },
    SANHAK: {
        NOTICE: 681, // 공지사항
        ASSIGNMENT: 683, // 과제공고
        NEWS: 678, // 연구소식
    },
    CSTS: {
        NOTICE: 1202,
        RULE: 1187, // 규정집
        RULE_LIST: { // 하위 규정집
            ITEM1: 1188, // 학칙
            ITEM2: 1189, // 학사내규
            ITEM3: 1190, // 장학금 운영규정
            ITEM4: 1191, // 부정행위자 징계규정
            ITEM5: 1192, // 학생생활에 관한 규정
            ITEM6: 1193, // 주차관리 규정
            ITEM7: 1194 // 성희롱·성폭력예방과 처리에 관한 규정
        },
        TIMETABLE: 1200, // 강의시간표
        NEWS: 1206 // 총신뉴스
    },
    BOOK1: 3041,
    BOOK2: 3053,
    BOOK3: 3054
};

// 학과별 MenuId
MenuId[DepartmentIdx.THEOL] = MenuId['THEOL'] = {
    NOTICE: 1222,
    GALLERY: 1218,
    SCHEDULE: 1215
};
MenuId[DepartmentIdx.MUSIC] = MenuId['MUSIC'] = {
    NOTICE: 1240,
    GALLERY: 1236,
    SCHEDULE: 1233
};
MenuId[DepartmentIdx.CSEDUCATION] = MenuId['CSEDUCATION'] = {
    NOTICE: 1258,
    GALLERY: 1254,
    SCHEDULE: 1251
};
MenuId[DepartmentIdx.ENGLISH] = MenuId['ENGLISH'] = {
    NOTICE: 1276,
    GALLERY: 1272,
    SCHEDULE: 1269
};
MenuId[DepartmentIdx.HISTORY] = MenuId['HISTORY'] = {
    NOTICE: 294,
    GALLERY: 1290,
    SCHEDULE: 1287
};
MenuId[DepartmentIdx.CSUCHILD] = MenuId['CSUCHILD'] = {
    NOTICE: 1312,
    GALLERY: 1308,
    SCHEDULE: 1305
};
MenuId[DepartmentIdx.TEACHER] = MenuId['TEACHER'] = {
    NOTICE: 1330,
    GALLERY: 1326,
    SCHEDULE: 1323
};
MenuId[DepartmentIdx.CSADONG] = MenuId['CSADONG'] = {
    NOTICE: 1348,
    GALLERY: 1344,
    SCHEDULE: 1341
};
MenuId[DepartmentIdx.SOCIALWORK] = MenuId['SOCIALWORK'] = {
    NOTICE: 2526,
    GALLERY: 1362,
    SCHEDULE: 1359
};
MenuId[DepartmentIdx.REHAB] = MenuId['REHAB'] = {
    NOTICE: 1384,
    GALLERY: 1380,
    SCHEDULE: 1377
};
MenuId[DepartmentIdx.KOREAN] = MenuId['KOREAN'] = {
    NOTICE: 1402,
    GALLERY: 1398,
    SCHEDULE: 1395
};
MenuId[DepartmentIdx.HOKMA] = MenuId['HOKMA'] = {
    NOTICE: 1420,
    GALLERY: 1416,
    SCHEDULE: 1413
};
MenuId[DepartmentIdx.INDUSTRY] = MenuId['INDUSTRY'] = {
    NOTICE: 2660,
    GALLERY: 2642,
    SCHEDULE: 2661
};

// 대학원 학과별 MenuId
MenuId[DepartmentIdx.GRADUATE] = MenuId['GRADUATE'] = {
    //SCHEDULE : TB_MENU 에 deptNo. 일정
    NOTICE : 1694,
    SCHEDULE : 1521,
    QUICK1 : 1524, //전체강의시간표
    QUICK2 : 1519, //교육과정
    QUICK3 : 1936, //각종서식
    QUICK4 : 2315 //대학원 가이드북
};
MenuId[DepartmentIdx.EDUCATION] = MenuId['EDUCATION'] = {
    NOTICE : 1696,
    SCHEDULE : 1547,
    QUICK1 : 1550, //전체강의시간표
    QUICK2 : 1735, //교육과정(기독교)
    QUICK3 : 1937, //각종서식
    QUICK4 : 2316 //대학원 가이드북
};
MenuId[DepartmentIdx.MISSION] = MenuId['MISSION'] = {
    NOTICE : 1698,
    SCHEDULE : 1573,
    QUICK1 : 1576, //전체강의시간표
    QUICK2 : 1571, //교육과정
    QUICK3 : 1938, //각종서식
    QUICK4 : 2317 //대학원 가이드북
};
MenuId[DepartmentIdx.PASTOR] = MenuId['PASTOR'] = {
    NOTICE : 1700,
    SCHEDULE : 1599,
    QUICK1 : 1602, //전체강의시간표
    QUICK2 : 1597, //교육과정
    QUICK3 : 1939, //각종서식
    QUICK4 : 2318 //대학원 가이드북
};
MenuId[DepartmentIdx.SOCIAL] = MenuId['SOCIAL'] = {
    NOTICE : 1702,
    SCHEDULE : 1625,
    QUICK1 : 1628, //전체강의시간표
    QUICK2 : 1623, //교육과정
    QUICK3 : 1940, //각종서식
    QUICK4 : 2319 //대학원 가이드북
};
MenuId[DepartmentIdx.COUNSELING] = MenuId['COUNSELING'] = {
    NOTICE : 1704,
    SCHEDULE : 1651,
    QUICK1 : 1654, //전체강의시간표
    QUICK2 : 1649, //교육과정
    QUICK3 : 1941, //각종서식
    QUICK4 : 2322 //대학원 가이드북
};
MenuId[DepartmentIdx.CHMUSIC] = MenuId['CHMUSIC'] = {
    NOTICE : 1692,
    SCHEDULE : 1677,
    QUICK1 : 1680, //전체강의시간표
    QUICK2 : 1675, //교육과정
    QUICK3 : 1942, //각종서식
    QUICK4 : 2323 //대학원 가이드북
};

MenuId[DepartmentIdx.PEACE] = MenuId['PEACE'] = {
    NOTICE : 2015,
    SCHEDULE : 1995,
    QUICK1 : 1998, //전체강의시간표
    // QUICK2 : 1675, //교육과정, 추가바람
    QUICK3 : 1999, //각종서식
    QUICK4 : 2324 //대학원 가이드북
};


// 부설기관
MenuId[DepartmentIdx.CHAPEL] = MenuId['CHAPEL'] = {
    NOTICE : 2060, // 공지사항
    SCHEDULE: '',
};
MenuId[DepartmentIdx.CSS] = MenuId['CSS'] = {
    NOTICE : 2088, // 공지사항
    STUDENT: 2089, // 학생게시판
    SCHEDULE: 2093,
    QUICK1 : 2084,
    QUICK2 : 2091
};



MenuId[DepartmentIdx.RTRC] = MenuId['RTRC'] = {
    NOTICE : '2186', // 공지사항
    STUDENT: '2184', // 학생게시판
    SCHEDULE: '2182',
    QUICK1 : '',
    QUICK2 : ''
};

MenuId[DepartmentIdx.DORMITORY] = MenuId['DORMITORY'] = {
    NOTICE : '2203', // 공지사항
    STUDENT: '', // 학생게시판
    SCHEDULE: '2204',
    QUICK1 : '',
    QUICK2 : ''
};
MenuId[DepartmentIdx.DORMITORY_Y] = MenuId['DORMITORY_Y'] = {
    NOTICE : '2190', // 공지사항
    STUDENT: '2192', // 학생게시판
    SCHEDULE: '',
    QUICK1 : '',
    QUICK2 : ''
};
MenuId[DepartmentIdx.BIBLICA] = MenuId['BIBLICA'] = {
    NOTICE : '2281', // 공지사항
    STUDENT: '', // 학생게시판
    SCHEDULE: '',
    QUICK1 : '',
    QUICK2 : ''
};
MenuId[DepartmentIdx.ASSOCIATION] = MenuId['ASSOCIATION'] = {
    NOTICE : '2540', // 공지사항
    STUDENT: '', // 학생게시판
    SCHEDULE: '',
    QUICK1 : '',
    QUICK2 : ''
};
MenuId[DepartmentIdx.RESERVE] = MenuId['RESERVE'] = {
    NOTICE : '2594', // 공지사항
    STUDENT: '', // 학생게시판
    SCHEDULE: '',
    QUICK1 : '',
    QUICK2 : ''
};
MenuId[DepartmentIdx.CSTEACHER] = MenuId['CSTEACHER'] = {
    NOTICE : '2909', // 공지사항
    STUDENT: '', // 학생게시판
    SCHEDULE: '3004',
    QUICK1 : '',
    QUICK2 : ''
};



var BoardId = {
    HOME: {
        NOTICE : {
            ROOT: 161, // 부모 게시판
            LIST: [
                432, // 일반
                433, // 대학장학
                434, // 대학
                435, // 신대원
                436, // 대학원
                437, // 비교과
                438, // 채용
                439, // 입찰
                323, // * 예비군 > 예비군
                324, // * 예비군 > 병무
                325, // * 예비군 > 민방위
            ]
        },
        NEWS: 162, // 총신광장 > 총신소식 > 총신소식
        MOVEMENT: 141, // 대학소개 > 총장소개 > 총장동정
        HISTORY_GALLERY: 142, // 대학소개 > 역사와비전 ? 역사갤러리
        PRESS: 163, // 총신광장 > 총신소식 > 언론속의총신
        PROMOTION: 165, // 총신광장 > 총신소식 > 홍보영상
        MILITARY: [323, 324, 325], // 예비군, 병무, 민방위
        DOCUMENT_LIST : [427,428], //학사안내 > 졸업 > 성경고사기출문제
        MINISTRY: 178, // 사역게시판
        HAKSA_FAQ : 431,
        FACULTY :{
            PSEDU_ADONG : 620,               // 대학 > 산업교육학부 > 아동학과(대학) 교수소개
            PSEDU_COUNSELING : 621,          // 대학 > 산업교육학부 > 아동상담심리학과(대학) 교수소개
            PSEDU2_EDUCATION : 622,     // 대학원 > 산업교육학부 대학원 > 교육대학원(유아교육학과) 교수소개
            PSEDU2_COUNSELING : 623, // 대학원 > 산업교육학부 대학원 > 상담대학원(아동상담심리학과) 교수소개
            PSEDU2_GRADUATE_CHILD : 624, // 대학원 > 산업교육학부 대학원 > 일반대학원(유아교육학과) 교수소개
            PSEDU2_GRADUATE_COUNSELING : 625, // 대학원 > 산업교육학부 대학원 > 일반대학원(유아상담심리학과) 교수소개

            PSEDU2_ALL : 645, // 대학원 > 산업교육학부 대학원 > 일반대학원(유아상담심리학과) 교수소개
        }
    },
    ADMISSION: {
        NOTICE: 6,
        QNA: 7,
        FAQ: 63,
        PROMOTION_GALLERY: 8,
        APPLY_GUIDE1: 19, // 모집요강 - 수시
        APPLY_GUIDE2: 9, // 모집요강 - 정시
        APPLY_GUIDE3: 13, // 모집요강 - 정시
        APPLY_GUIDE4: 16, // 모집요강 - 정시
        DOC1: 21, // 제출서류양식 - 수시
        DOC2: 11, // 제출서류양식 - 정시
        DOC3: 14, // 제출서류양식 - 편입
        DOC4: 17, // 제출서류양식 - 재외국민/외국인
    },
    GRAENT: {
        APPLY_GUIDE1: 76, // 일반대학원 - 석사
        APPLY_GUIDE2: 77, // 일반대학원 - 박사
        APPLY_GUIDE3: 78, // 목회신학전문대학원 - 석사
        APPLY_GUIDE4: 79, // 목회신학전문대학원 - 박사
        APPLY_GUIDE5: 66, // 선교대학원
        APPLY_GUIDE6: 67, // 교육대학원
        APPLY_GUIDE7: 68, // 사회복지대학원
        APPLY_GUIDE8: 69, // 상담대학원
        APPLY_GUIDE9: 70, // 교회음악대학원
        // APPLY_GUIDE10: 82, // 외국인전형 (한글) : TODO : 임시적으로 PDF뷰 가림
        // APPLY_GUIDE11: 83, // 외국인전형 (영문)
        APPLY_GUIDE12: 91, // 평화통일대학원
        APPLY_GUIDELINE: 643, // English Th.M Program
        DOC: 102, // 입시소정양식
        NOTICE: 60,
        QNA: 61,
    },
    CSTSENT: {
        NOTICE: 212,
        QNA: 213,
        APPLY_GUIDE1: 202, // 모집요강 : 일반전형
        APPLY_GUIDE2: 204, // 모집요강 : 수시전형
        APPLY_GUIDE3: 206, // 모집요강 : 특별전형
        APPLY_GUIDE4: 208, // 모집요강 : 편입전형
        APPLY_GUIDE5: 210, // 모집요강 : 외국인전형
        DOC1: 203, // 제출서류양식 : 일반전형
        DOC2: 205, // 제출서류양식 : 수시전형
        DOC3: 207, // 제출서류양식 : 특별전형
        DOC4: 209, // 제출서류양식 : 편입
        DOC5: 211 // 제출서류양식 : 외국인
    },
    CSFUND: {
        STORY: 130, // 후원소식 > 후원스토리
        PRESS: 131, // 후원소식 > 보도자료
        // STATUS1: 38, // 후원소식 > 후원현황 > 1004모금
        // STATUS2: 39, // 후원소식 > 후원현황 > 총신100만
        STATUS1: 134, // 후원소식 > 후원현황 > 교회 및 단체 후원현황
        STATUS2: 135, // 후원소식 > 후원현황 > 개인후원약정현황
        STATUS3: 136, // 후원소식 > 후원현황 > 100만기도후원회-월별후원금현황
        HONOR1: 137, // 기부자 예우 > 명예의전당 > 5천만 이상
        HONOR2: 138, // 기부자 예우 > 명예의전당 > 1천만 이상
        HONOR3: 139, // 기부자 예우 > 명예의전당 > 1억원 이상
        FILE: 140 // 페이지에 쓸 양식들
    },
    SANHAK: {
        NOTICE: 85, // 공지사항
        ASSIGNMENT: 87, // 과제공고
        NEWS: 84 // 연구소식
    },
    CSTS: {
        NOTICE: 216,
        FACULTY: 335,
        TIMETABLE: 215, // 강의시간표
        NEWS: 220 // 신대원 뉴스
    }
};

FileContentId = {
    CSFUND: {
        AGREEMENT: 684 // 1004(천사) 모금운동 후원약정서
    }
};

//학과별 boardId
BoardId[DepartmentIdx.THEOL] = BoardId['THEOL'] = {
    NOTICE: 227,
    GALLERY: 225,
    FACULTY: 221,
    PDF : [ 222, 223, 224 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.MUSIC] = BoardId['MUSIC'] = {
    NOTICE: 235,
    GALLERY: 234,
    FACULTY: 230,
    PDF : [ 231, 232, 233 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.CSEDUCATION] = BoardId['CSEDUCATION'] = {
    NOTICE: 243,
    GALLERY: 242,
    FACULTY: 238,
    PDF : [ 239, 240, 241 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.ENGLISH] = BoardId['ENGLISH'] = {
    NOTICE: 251,
    GALLERY: 250,
    FACULTY: 246,
    PDF : [ 247, 248, 249 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.HISTORY] = BoardId['HISTORY'] = {
    NOTICE: 259,
    GALLERY: 258,
    FACULTY: 254,
    PDF : [ 255, 256, 257 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.CSUCHILD] = BoardId['CSUCHILD'] = {
    NOTICE: 267,
    GALLERY: 266,
    FACULTY: 262,
    PDF : [ 263, 264, 265 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.TEACHER] = BoardId['TEACHER'] = {
    NOTICE: 276,
    GALLERY: 274,
    FACULTY: 270,
    PDF : [ 271, 272, 273 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.CSADONG] = BoardId['CSADONG'] = {
    NOTICE: 285,
    GALLERY: 283,
    FACULTY: 279,
    PDF : [ 280, 281, 282 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.SOCIALWORK] = BoardId['SOCIALWORK'] = {
    NOTICE: 630,
    GALLERY: 292,
    FACULTY: 288,
    PDF : [ 289, 290, 291 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.REHAB] = BoardId['REHAB'] = {
    NOTICE: 303,
    GALLERY: 301,
    FACULTY: 297,
    PDF : [ 298, 299, 300 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.KOREAN] = BoardId['KOREAN'] = {
    NOTICE: 312,
    GALLERY: 310,
    FACULTY: 306,
    PDF : [ 307, 308, 309 ] // 메인 연동용 [교육과정, 학점이수기준표, 졸업사정기준]
}
BoardId[DepartmentIdx.HOKMA] = BoardId['HOKMA'] = {
    NOTICE: 320,
    GALLERY: 318,
    FACULTY: 315,
    PDF : [ 316, 317 ] // 교육과정, 학점이수 기준표
}
BoardId[DepartmentIdx.INDUSTRY] = BoardId['INDUSTRY'] = {
    NOTICE: 651,
    GALLERY: 647,
    FACULTY: 645
    // PDF : [ 316, 317 ] // 교육과정, 학점이수 기준표
}

// 대학원 학과별 boardId
BoardId[DepartmentIdx.GRADUATE] = BoardId['GRADUATE'] = {
    FACULTY : 344,
    DOC : [346,349],
    NOTICE: 388,
    PDF : 396,
    DOCUMENT_LIST : [347,348],//학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.EDUCATION] = BoardId['EDUCATION'] = {
    FACULTY : [412,416,417,489],
    DOC : [351,354],
    NOTICE: 389,
    PDF : 403,
    DOCUMENT_LIST : [352,353] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.MISSION] = BoardId['MISSION'] = {
    FACULTY : 356,
    DOC : [359,362],
    NOTICE: 390,
    PDF : 402,
    DOCUMENT_LIST : [360,361] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.PASTOR] = BoardId['PASTOR'] = {
    FACULTY : 363,
    DOC : [365,368],
    NOTICE: 391,
    PDF : 401,
    DOCUMENT_LIST : [366,367] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.SOCIAL] = BoardId['SOCIAL'] = {
    FACULTY : 369,
    DOC : [371,374],
    NOTICE: 392,
    PDF : 400,
    DOCUMENT_LIST : [372,373] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.COUNSELING] = BoardId['COUNSELING'] = {
    FACULTY : 375,
    DOC : [377,380],
    NOTICE: 393,
    PDF : 399,
    DOCUMENT_LIST : [378,379] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.CHMUSIC] = BoardId['CHMUSIC'] = {
    FACULTY : 381,
    DOC : [383,386],
    NOTICE: 387,
    PDF : 398,
    DOCUMENT_LIST : [384,385] //학위논문 > [논문관련양식, 논문예시파일]
}
BoardId[DepartmentIdx.PEACE] = BoardId['PEACE'] = {
    FACULTY : 613,
    DOC : [460,467],
    NOTICE: 'null',
    PDF : 468,
    DOCUMENT_LIST : [465,466] //학위논문 > [논문관련양식, 논문예시파일]
}


var ProjectConstants = {
};

var ProjectApiUrl = {
};

var ProjectPageUrl = {
    DEPARTMENT: '/department',
    CMS: '/cms',
    ERROR_500: 'error500',
    ERROR_404: 'error404'
};


// TOP: 1,
//
//     MIDDLE: 2,
//     MOBILE_MIDDLE: 9,
//
//     BOTTOM: 3,
//     LEFT: 4,
//     RIGHT: 5,
//     POPUP: 6,
//
//     NEW_TAB: 7,
//     NEW_WINDOW: 8,

BannerType.setMap({
    1 : '상단',
    2 : '중간',
    3 : '퀵메뉴',
    6 : '팝업',
    10 : '대학 입시 홈페이지',
    11 : '신대원 입시 홈페이지',
    12 : '대학원 입시 홈페이지',
    13 : '계약학과 입시 홈페이지'
});

var ProjectUrlHelper = {

    openCms: function () {
        Requester.open('/page/cms');
    },

    needLogin : function( cancelable ) {

        if ( cancelable == false ) {
            cancelable = function() {
                Lia.redirect('/');
            };
        }

        PopupManager.alert('확인', '로그인이 필요한 서비스입니다.<br/>지금 로그인 하시겠습니까?', function(){
            Lia.redirect(Server.ssoServerUrl + '/?redirect_url=' + encodeURIComponent(document.location.href));
        }, cancelable);
    },

    openCmsLogin: function () {

        var jLocation = $(location);
        var baseUrl = jLocation.attr('protocol') + '//' + jLocation.attr('host');

        var url = baseUrl + '/page/cms';
        Lia.redirectGet(Server.ssoServerUrl + '', {
            'redirect_url': url
        });
    }
};


PathHelper.getFileUrl =  function (url, destFilename, ignoreDestFilename) {

    if (String.isBlank(url)) {
        return undefined;
    }

    if (ignoreDestFilename == undefined)
        ignoreDestFilename = 0;

    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }

    if (url.indexOf(ApiUrl.File.GET) == 0) {
        return url;
    }

    if (url.startsWith('/res/')) {
        return url;
    }

    var jLocation = $(location);
    // var baseUrl = jLocation.attr('protocol') + '//nsu.ac.kr';
    var baseUrl = jLocation.attr('protocol') + '//' + jLocation.attr('host');
    if ( Lia.isDebugMode() ) {
        baseUrl = 'https://www.csu.ac.kr/'
    }

    var fileParameterMap = {
        path: url
    };

    if (String.isNotBlank(destFilename)) {
        fileParameterMap['destFilename'] = destFilename;
    }

    fileParameterMap['ignoreDestFilename'] = ignoreDestFilename;

    return baseUrl + ApiUrl.File.GET + Lia.convertArrayToQueryString(fileParameterMap);
};

PathHelper.getPdfUrl = function (url, destFilename, ignoreDestFilename) {

    if (String.isBlank(url)) {
        return undefined;
    }

    if (ignoreDestFilename == undefined)
        ignoreDestFilename = 0;

    if (url.startsWith('http://') || url.startsWith('https://')) {
        return url;
    }

    if (url.indexOf(ApiUrl.File.GET) == 0) {
        return url;
    }

    if (url.startsWith('/res/')) {
        return url;
    }

    var jLocation = $(location);


    var baseUrl = jLocation.attr('protocol') + '//' + jLocation.attr('host');

    if ( Lia.isDebugMode() ) {
        baseUrl = 'https://www.csu.ac.kr/'
    }

    var fileParameterMap = {
        path: url
    };

    if (String.isNotBlank(destFilename)) {
        fileParameterMap['destFilename'] = destFilename;
    }

    fileParameterMap['ignoreDestFilename'] = ignoreDestFilename;

    return baseUrl + '/api/file/getPdf' + Lia.convertArrayToQueryString(fileParameterMap);
};

var PDFHelper = {

    objFlag: true,
    gviewFlag: false,

    show: function (attachedPdf, fileName, customClass) {
        var jPdf = $('.apply_pdf');

        var fileName = Lia.pd('파일', fileName);

        if(customClass != undefined) {
            jPdf = $(customClass);
        }

        if(Lia.checkFirefox()) {
            // 파이어 폭스의 경우에는 인라인 PDF 지원 안함
            PDFHelper.renderGview(jPdf, attachedPdf);
        } else {
            var width = $(window).width();
            if(width > 1240) {
                PDFHelper.renderPdfObject(jPdf, attachedPdf, fileName, customClass);
            } else {
                PDFHelper.renderGview(jPdf, attachedPdf, customClass);
            }

        }

    },

    renderPdfObject: function (jPdf, attachedPdf, fileName, customClass) {
        jPdf.empty();
        jPdf.removeClass('pdfobject-container');

        var jLocation = $(location);
        var baseUrl = jLocation.attr('protocol') + '//' + jLocation.attr('host');
        if ( Lia.isDebugMode() ) {
            baseUrl = 'https://www.csu.ac.kr/'
        }

        var fileParameterMap = {
            path: attachedPdf
        };

        if ( String.isNotBlank(fileName) ) {
            fileParameterMap['destFilename'] = fileName;
        }

        var viewpath = baseUrl + '/api/file/getPdf' + Lia.convertArrayToQueryString(fileParameterMap);

        if(customClass != undefined) {
            PDFObject.embed(viewpath, customClass);
        } else {
            PDFObject.embed(viewpath, ".apply_pdf");
        }


    },

    renderGview: function (jPdf, attachedPdf, fileName, customClass) {

        if(customClass != undefined || String.isNotBlank(customClass)) {
            var jPdf = $(customClass);
        }

        jPdf.empty();
        jPdf.removeClass('pdfobject-container');

        var jLocation = $(location);
        var baseUrl = jLocation.attr('protocol') + '//' + jLocation.attr('host');

        if ( Lia.isDebugMode() ) {
            baseUrl = 'https://www.csu.ac.kr'
        }

        var fileParameterMap = {
            path: attachedPdf
        };

        if ( String.isNotBlank(fileName) ) {
            fileParameterMap['destFilename'] = fileName;
        }

        var viewpath = baseUrl + '/api/file/get' + Lia.convertArrayToQueryString(fileParameterMap);

        var jGview = $('<iframe src="https://docs.google.com/gview?url='+ viewpath +'&embedded=true" frameborder="0"></iframe>');
        jPdf.append(jGview);
    }
}



$('.page_btn').on('click', function (e){

    var jThis = $(this);

    var m1 = jThis.attr('m1');
    var menuId = jThis.attr('menu-id');

    if(m1 == 'page' && String.isNotBlank(menuId)) {
        PageManager.go([m1], { 'menu_id': menuId });
    } else {
        PageManager.go([m1]);
    }
});



var ONLY_CONTENTS = {
    init: function () {
        var isRemoveFrame = PageManager.pc('removeFrame');
        if(isRemoveFrame == '1') {
            console.info('콘텐츠 보기 전용 페이지에 진입하셨습니다.');

            // 헤더탑 숨기기
            $('#header_top').hide();
            $('#header').hide();
            $('.page_content_header').hide();
            $('.page_content_menu').hide();
            $('.page_content_sub_menu').hide();
            $('.page_content_menu_mobile').hide();
            $('.page_content_menu_panel').hide();
            $('#footer').hide();
        }
    }
}