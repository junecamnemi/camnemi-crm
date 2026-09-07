var PageUrl = {
    HOME : '/',
    CMS: '/page/cms',
    USER_INFO: '/page/cms/userInfo'
    //CERTIFICATE: '/page/lms/certificate',
};

var PlayerUrl = {
    VIDEO : '/player/vplayer',
    AUDIO : '/player/aplayer',
    VIMEO : '/player/vimeo',
    YOUTUBE : '/player/youtube'
};

var PopupTitleHelper = {

    getDeletePopupTitle: function (itemCategoryTitle, itemTitle) {

        var title = '선택하신 ' + itemCategoryTitle + '을(를) 정말 삭제하시겠습니까?</br></br>[항목: ' + itemTitle + ']';

        return title;
    },
    getAddPopupTitle: function () {

        var title = '이대로 등록하시겠습니까?';

        return title;
    },
    getEditPopupTitle: function () {

        var title = '이대로 변경하시겠습니까?';

        return title;
    },
    getNullOrEmptyValueTitle: function (itemName) {

        var title = '을(를) 입력해주세요.';

        return title;
    }
};


var PopupUrl = {

    PROGRESS: 'cms/popup/progress',
    REGISTER_RESULT_POPUP: 'cms/popup/register_result_popup',

    REGISTER_FILE_USER : 'cms/popup/register_file_user',
    SEARCH_USER : 'cms/popup/search_user',
    EXCEL_DOWNLOAD : 'cms/popup/excel_download',
    EXPORT_DOWNLOAD : 'cms/popup/export_download',
    EXPORT_DOWNLOAD_PROGRESS : 'cms/popup/export_download_progress',

    COMBO_BOX : 'cms/popup/combo_box',
    RADIO_SELECT : 'cms/popup/radio_select',
    REGISTER_EXCEL : 'cms/popup/register_excel',
    REGISTER_GALLERY : 'cms/popup/register_gallery',
    CHECK_BOX : 'cms/popup/check_box',
    CHECK_BOX_LIST : 'cms/popup/check_box_list',

    IMAGE : 'cms/popup/image',
    VIDEO : 'cms/popup/video',

    OPTION_LIST_BUTTON_SELECT : 'cms/popup/option_list_button_select',

    GALLERY_IMAGE_POPUP: 'cms/popup/gallery_image_popup',

    MENU_MANAGER: 'cms/popup/menu_manager',
    MENU_USER: 'cms/popup/menu_user',
    MENU_MANAGER_REGISTER: 'cms/popup/menu_manager_register',
    ASSIGN_MANGER : 'cms/popup/assign_manager',

    EDIT_SCHEDULE : 'cms/popup/edit_schedule',
    INFO_CALENDAR : 'cms/popup/info_calendar',
    REGISTER_CALENDAR : 'cms/popup/register_calendar',

    REGISTER_FOOD_CALENDAR : 'cms/popup/register_food_calendar',

    SURVEY_POPUP: 'cms/popup/survey_popup',
    IMPORT_SURVEY: 'cms/popup/import_survey',
    DATETIME_SELECT: 'cms/popup/datetime_select',
    SURVEY_PARTICIPANT_LIST: 'cms/popup/survey_participant_list',
    SURVEY_EXCEL_DOWNLOAD: 'cms/popup/survey_excel_download',
    OTHER_ANSWER_LIST: 'cms/popup/other_answer_list'
};

var ServicePopupUrl = {

    ALERT_POPUP : 'service/popup/alert_popup'
};


var ResponseNode = {
    BODY: 'body',
    CODE: 'code'
};

var ScheduleOrderBy = {
    START_DATE_DESC: 1,
    START_DATE_ASC: 2
};

var ScheduleStatus = {
    NEW: 1000,
    APPROVED: 2000,
    REJECTED: 3000,

    codeMap: {
        1000: '신규',
        2000: '승인',
        3000: '거절'
    },

    colorMap: {
        1000: { backgroundColor : '#e99200', color : '#ffffff' },
        2000: { backgroundColor : '#5086f7', color : '#ffffff' },
        3000: { backgroundColor : '#cccccc', color : '#333333' },
    },

    setColorMap : function( map ) {
        ScheduleStatus.colorMap = map;
    },

    getColorMap: function () {
        return ScheduleStatus.colorMap;
    },

    setCodeMap : function( map ) {
        ScheduleStatus.codeMap = map;
    },

    getCodeMap: function () {
        return ScheduleStatus.codeMap;
    },

    getColor: function (code) {

        code = parseInt(code);
        var color = ScheduleStatus.colorMap[code];
        if (color == undefined)
            color = {};

        return color;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = ScheduleStatus.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },

    createOptionList : function( all ) {

        var list = [];

        if ( all == true ) {

            list.push({
                value : '',
                name : '전체'
            });
        }

        for ( var key in ScheduleStatus.codeMap ) {

            list.push({
                value : key,
                name : ScheduleStatus.codeMap[key]
            });
        }

        return list;
    }
};

var MessageType = {
    EMAIL: 1,
    TEXT: 2,
    PUSH: 3,
    INERTNAL: 9,

    codeMap: {
        1: '이메일',
        2: 'SMS',
        3: 'PUSH',
        9: '자동문자'
    },

    getCodeMap: function () {
        return MessageType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = MessageType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var MessageReceiverResult = {

    // 발송 전
    NULL_OR_EMPTY_ADDRESS: 10,
    INVALID_ADDRESS: 11,

    // 발송 중
    WAITING: 20,
    SENDING: 21,

    // 결과
    SUCCESS: 30,
    FAILURE: 31,


    codeMap: {
        10: '존재하지 않은 주소',
        11: '올바르지 않은 주소',
        20: '발송 준비 중',
        21: '발송 중',
        30: '성공',
        31: '실패'
    },

    getCodeMap: function () {
        return MessageReceiverResult.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = MessageReceiverResult.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }

};

var TermsOfServiceType = {
    SIGN_UP: 1,

    codeMap: {
        1: '사용자 가입'
    },

    getCodeMap: function () {
        return TermsOfServiceType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = TermsOfServiceType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var PaymentMethod = {

    INICIS: 1,
    PAYPAL: 2,
    KAKAO_PAY: 3,
    NAVER_PAY: 4,

    codeMap: {
        1: 'INICIS',
        2: 'PAYPAL',
        3: 'KAKAO PAY',
        4: 'NAVER PAY'
    },

    nameMap : undefined,

    getCodeMap: function () {
        return PaymentMethod.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = PaymentMethod.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },
    createOptionList : function( all, allText, allValue ) {

        var list = [];

        if ( all == true ) {

            list.push({
                value : Lia.pcd('', allValue),
                name : Lia.pcd('전체', allText)
            });
        }

        for ( var code in PaymentMethod.codeMap ) {

            list.push({
                value : code,
                name : PaymentMethod.getName(code)
            });
        }

        return list;
    }
};


var PaymentStatus = {

    ORDERED: 100,
    WAITING_FOR_APPROVAL: 200,
    APPROVED: 201,

    CANCELLED: 300,

    REFUND_REQUESTED: 400,
    REFUND_REJECTED: 401,
    REFUNDED: 402,

    PARTIAL_REFUND_REQUESTED: 410,
    PARTIAL_REFUND_REJECTED: 411,
    PARTIAL_REFUNDED: 412,

    SHIPPING : 500,
    SHIPPING_COMPLETED : 501,

    TRANSACTION_FAILURE: 900,
    TRANSACTION_FAILURE_DUE_TO_INSUFFICIENT_ACCOUNT_BALANCE: 901,

    codeMap: {
        100: "결제 요청",

        200: "승인 대기",
        201: "결제 승인",

        300: "결제 취소",

        400: "환불 요청",
        401: "환불 거절",
        402: "환불 완료",

        410: "부분 환불 요청",
        411: "부분 환불 거절",
        412: "부분 환불 완료",

        500: "배송 중",
        501: "배송 완료",

        900: "결제 실패",
        901: "결제 실패"
    },

    colorMap : {

        100:'#084897',
        200:'#084897',
        201:'#084897',

        300:'#F33A3A',
        400:'#F33A3A',
        401:'#F33A3A',
        402:'#F33A3A',
        410:'#F33A3A',
        411:'#F33A3A',
        412:'#F33A3A',

        500:'#084897',
        501:'#084897',

        900:'#5d5d5d',
        901:'#5d5d5d'
    },

    getCodeMap: function () {
        return PaymentStatus.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = PaymentStatus.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },

    getColor : function( code, defaultValue ) {
        var value = PaymentStatus.colorMap[code];
        if ( value ==undefined){
            return defaultValue;
        }
        return value;
    },

    createOptionList : function( all, allText, allValue ) {

        var list = [];

        if ( all == true ) {

            var allList = [];

            for ( var code in PaymentStatus.codeMap ) {

                if ( code == PaymentStatus.ORDERED ) {
                    continue;
                }

                allList.push(code);
            }


            list.push({
                value : Lia.pcd(allList.join(','), allValue),
                name : Lia.pcd('전체', allText)
            });
        }

        for ( var code in PaymentStatus.codeMap ) {

            if ( code == PaymentStatus.ORDERED ) {
                continue;
            }

            list.push({
                value : code,
                name : PaymentStatus.getName(code)
            });
        }

        return list;
    }
};

var PriceUnit = {

    KRW : 'KRW',
    USD : 'USD',

    codeMap : {
        'KRW' : '원',
        'USD' : '$'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in PriceUnit.codeMap) {
            optionList.push({value: key, name: PriceUnit.codeMap[key]});
        }

        return optionList;
    },

    getName: function (code, defaultText) {

        var name = PriceUnit.codeMap[code];
        if (name == undefined)
            name = defaultText;

        return name;
    },

    getPriceString: function (amount, code) {

        var text = '';

        if(amount == '-') {
            return '-'
        }

        var parsingAmount = PriceUnit.toNumberFormat(amount);
        if(code == PriceUnit.KRW) {
            text = parsingAmount + ' ' + PriceUnit.getName(code);
        } else if(code == PriceUnit.USD) {
            text =  PriceUnit.getName(code) + parsingAmount + ' ' + code;
        }

        return text;
    },


    toNumberFormat : function (str) {
        str = String(str);
        return str.replace(/(\d)(?=(?:\d{3})+(?!\d))/g, '$1,');
    }

};


var Code = {

    SUCCESS: 10000,

    INVALID_SESSION: 22000,

    TEMPORARY_USER: 22005,

    UNAUTHORIZED_USER: 23000,

    ALREADY_REGISTERED_USER_ID: 30022,

    ALREADY_SUBMITTED_STUDENT_WORK: 57001,
    ALREADY_TAKEN_AND_COMPLETED_COURSE: 55014,

    STUDENT_ATTENDANCE_REQUIREMENT_NOT_MET: 56008,
    UNABLE_TO_LEARN_MULTIPLE_CONTENT_AT_ONCE: 59000,
    TOO_LATE_TO_CANCEL_SURVEY_REQUEST : 61203,

    NO_SUCH_USER_TERMS_OF_SERVICE: 84100,
    NEED_TO_AGREE_TERMS_OF_SERVICE: 84102,

    // HTTP
    TIMEOUT: jQuery.Requester.HttpStatus.TIMEOUT,
    NOT_FOUND: jQuery.Requester.HttpStatus.NOT_FOUND,
    INTERNAL_SERVER_ERROR: jQuery.Requester.HttpStatus.INTERNAL_SERVER_ERROR,
    BAD_GATEWAY: jQuery.Requester.HttpStatus.BAD_GATEWAY,
    BAD_REQUEST: jQuery.Requester.HttpStatus.BAD_REQUEST,

    MessageMap: {},

    init: function () {

        Code.MessageMap[Code.SUCCESS] = {title: '성공', message: '요청이 성공적으로 완료되었습니다.'};

        // HTTP
        Code.MessageMap[Code.NOT_FOUND] = {title: '안내', message: '페이지를 찾을 수 없습니다.'};
        Code.MessageMap[Code.INTERNAL_SERVER_ERROR] = {title: '안내', message: '오류가 발생하였습니다.'};
        Code.MessageMap[Code.BAD_GATEWAY] = {title: '안내', message: '서버와 연결상태가 좋지 않습니다.'};
        Code.MessageMap[Code.TIMEOUT] = {title: '안내', message: '시간초과가 발생하였습니다.'};
        Code.MessageMap[Code.BAD_REQUEST] = {title: '안내', message: '잘못된 요청입니다.'};
    },

    getMessage: function (value, defaultValues) {

        if (defaultValues == undefined) {
            defaultValues = '에러가 발생하였습니다.' + '(' + value + ')';
        }

        return Lia.pd(defaultValues, Code.MessageMap, value, 'message');
    },
    getMessageByResponse: function (data, defaultValues) {

        var code = Lia.p(data, 'code');
        if (code == undefined)
            code = data;

        var s = Lia.p(Code.MessageMap, code);
        if (s != undefined) {
            return Lia.p(s, 'message');
        }

        var message = Lia.p(data, 'message');
        if (String.isNotBlank(message)) {
            return message;
        }

        return Code.getMessage(code, defaultValues);
    },
    getTitle: function (value, defaultValues) {

        if (defaultValues == undefined) {
            defaultValues = '안내';
        }

        return Lia.pd(defaultValues, Code.MessageMap, value, 'title');
    },
    getTitleByResponse: function (data, defaultValues) {

        var code = Lia.p(data, 'code');
        if (code == undefined)
            code = data;

        return Code.getTitle(code, defaultValues);
    }
};
Code.init();


var BannerType = {
    TOP: 1,

    MIDDLE: 2,
    MOBILE_MIDDLE: 9,

    BOTTOM: 3,
    LEFT: 4,
    RIGHT: 5,
    POPUP: 6,

    NEW_TAB: 7,
    NEW_WINDOW: 8,

    HEADER: 10,
    FOOTER: 11,
    HEADLINE: 12,
    TICKER: 13,
    SLIDE: 14,

    TOP_LEFT: 15,
    TOP_RIGHT: 16,
    MIDDLE_LEFT: 17,
    MIDDLE_RIGHT: 18,
    BOTTOM_LEFT: 19,
    BOTTOM_RIGHT: 20,

    TABLET_MIDDLE: 21,
    //MOBILE_MIDDLE: 22,

    FACEBOOK: 23,
    TWITTER : 24,
    INSTAGRAM : 25,
    YOUTUBE : 26,

    map: {
        1 : '상단',
        2 : '중간',
        9 : '모바일 중간',
        3 : '하단',
        6 : '팝업',

        10: '해더',
        11: '푸터',
        12: '해드라인',
        13: '티커',
        14: '슬라이드',

        15: '상단 좌측',
        16: '상단 우측',
        17: '중단 좌측',
        18: '중단 우측',
        19: '하단 좌측',
        20: '하단 우측',

        21: '중단(타블렛)',
        //22: '중간(모바일)',

        23: 'Facebook',
        24: 'Twitter',
        25: 'Instagram',
        26: 'YouTube'
    },

    setMap : function( map ) {
        BannerType.map = map;
    },

    init: function () {
        //BannerType.map[BannerType.TOP] = '상단';
        //BannerType.map[BannerType.MIDDLE] = '중간';
        //BannerType.map[BannerType.MOBILE_MIDDLE] = '모바일 중간';
        //BannerType.map[BannerType.BOTTOM] = '하단';
        //BannerType.map[BannerType.LEFT]='왼쪽';
        //BannerType.map[BannerType.RIGHT]='오른쪽';
        //BannerType.map[BannerType.POPUP] = '팝업';
        //BannerType.map[BannerType.NEW_TAB]='새탭';
        //BannerType.map[BannerType.NEW_WINDOW]='새창';
    },

    createOptionList : function( all, allText ) {

        var optionList = [];

        if ( all == true ) {
            optionList.push({
                value : '',
                name : Lia.pd('타입 전체', allText)
            });
        }

        for ( var key in BannerType.map ) {

            var option = {
                name : BannerType.getName(key),
                value : key
            };

            optionList.push(option);
        }

        return optionList;
    },

    getNameMap: function () {
        return BannerType.map;
    },

    getName: function (type) {
        return BannerType.map[type];
    }
};

var BoardType = {
    MAIN: 0,
    ANNOUNCEMENT: 1,
    DOWNLOAD: 2,
    QUESTION_AND_ANSWER: 3,
    FAQ: 4,
    DOCUMENT: 5,
    GALLERY: 6,
    FLOATING_TEXT: 7,
    POSTER: 8,
    GENERAL: 9,

    codeMap: {
        0: '메인',
        1: '공지사항',
        2: '자료실',
        3: '질의응답',
        4: '자주묻는질문',
        5: '문서',
        6: '갤러리',
        7: '흐르는 TEXT',
        8: '포스터',
        9: '일반'
    },

    setCodeMap : function(map) {
        BoardType.codeMap = map;
    },

    createOptionList: function () {

        var optionList = [];

        optionList.push({value: '', name: '선택'});

        for (var key in BoardType.codeMap) {
            optionList.push({value: key, name: BoardType.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return BoardType.codeMap;
    },

    getName: function (val) {

        return BoardType.codeMap[val];
    }
};

var BoardContentOrderBy = {
    TITLE_ASC: 1,
    TITLE_DESC: 2,
    REGISTERED_DATE_ASC: 3,
    REGISTERED_DATE_DESC: 4,
    LAST_MODIFIED_DATE_ASC: 5,
    LAST_MODIFIED_DATE_DESC: 6,
    DELETED_DATE_ASC: 7,
    DELETED_DATE_DESC: 8,
    EFFECTIVE_START_DATE_ASC: 9,
    EFFECTIVE_START_DATE_DESC: 10,
    EFFECTIVE_END_DATE_ASC: 11,
    EFFECTIVE_END_DATE_DESC: 12,
    VIEW_COUNT_ASC: 13,
    VIEW_COUNT_DESC: 14,
    DISPLAY_ORDER_ASC: 15,
    DISPLAY_ORDER_DESC: 16,

    RANDOM: 90
};

var SearchOption;
var SearchOptionList = SearchOption =  function () {
    this.list = [];
};
SearchOptionList.prototype.add = function (code, keyword, property) {

    var option = {
        code: code,
        keyword: keyword
    };

    if ( String.isNotBlank(property) ) {
        option['property'] = property;
    }

    this.list.push(option);
};

SearchOptionList.prototype.size = function () {
    return this.list.length;
};
SearchOptionList.prototype.get = function () {
    return JSON.stringify(this.list);
};

SearchOptionList.createOption = SearchOption.createOption  = function (code, keyword) {
    var searchOption = new SearchOption();
    searchOption.add(code, keyword);
    return searchOption.get();
};

SearchOption.MessageSummary = SearchOptionList.MessageSummary = {
    TITLE: 1,
    BODY: 2,
    SENT_DATE_FROM_DATE: 3,
    SENT_DATE_TO_DATE: 4
};

SearchOption.BoardContent = SearchOptionList.BoardContent = {

    TITLE: 1,
    BODY: 2,
    TITLE_OR_BODY: 3,
    REGISTERED_BY_USER_NAME: 4,
    LAST_MODIFIED_BY_USER_NAME: 5,
    DELETED_BY_USER_NAME: 6,
    REGISTERED_BY_USER_ID: 7,
    LAST_MODIFIED_BY_USER_ID: 8,
    DELETED_BY_USER_ID: 9,
    REGISTERED_DATE_FROM_DATE: 10,
    REGISTERED_DATE_TO_DATE: 11,
    TO_TITLE: 12,
    FROM_TITLE: 13,
    OWNER_NAME: 14,
    IS_PRIVATE: 15,
    PROPERTIES: 16,

    createOptionList: function () {

        var optionList = [];
        optionList.push({name: '제목+내용', value: SearchOption.BoardContent.TITLE_OR_BODY});
        optionList.push({name: '제목', value: SearchOption.BoardContent.TITLE});
        optionList.push({name: '내용', value: SearchOption.BoardContent.BODY});
        optionList.push({name: '이름', value: SearchOption.BoardContent.REGISTERED_BY_USER_NAME});
        optionList.push({name: '아이디', value: SearchOption.BoardContent.REGISTERED_BY_USER_ID});
        return optionList;
    }

};

SearchOption.StudentReportSummary = SearchOptionList.StudentReportSummary = {

    STUDENT_USER_ID: 1,
    STUDENT_USER_NAME: 2,

    COURSE_TITLE: 3,

    TOTAL_MARK_FROM: 4,
    TOTAL_MARK_TO: 5,
    EXAM_TOTAL_MARK_FROM: 6,
    EXAM_TOTAL_MARK_TO: 7,
    QUIZ_TOTAL_MARK_FROM: 8,
    QUIZ_TOTAL_MARK_TO: 9,
    ASSIGNMENT_TOTAL_MARK_FROM: 10,
    ASSIGNMENT_TOTAL_MARK_TO: 11,
    FORUM_TOTAL_MARK_FROM: 12,
    FORUM_TOTAL_MARK_TO: 13,
    LIVE_SEMINAR_TOTAL_MARK_FROM: 14,
    LIVE_SEMINAR_TOTAL_MARK_TO: 15,
    ETC_TOTAL_MARK_FROM: 16,
    ETC_TOTAL_MARK_TO: 17,
    ATTENDANCE_TOTAL_MARK_FROM: 18,
    ATTENDANCE_TOTAL_MARK_TO: 19,

    EXAM_PARTICIPATION: 20,
    QUIZ_PARTICIPATION: 21,
    ASSIGNMENT_PARTICIPATION: 22,
    FORUM_PARTICIPATION: 23,
    LIVE_SEMINAR_PARTICIPATION: 24,

    STUDY_START_DATE: 25,
    STUDY_END_DATE: 26,

    STUDENT_COMPANY_NAME: 27
};


SearchOption.SurveyRequestSummary = SearchOptionList.SurveyRequestSummary = {
    TITLE: 1,
    COURSE_TITLE: 2
};

SearchOption.SurveySearchBy = SearchOptionList.SurveySearchBy = {
    TITLE: 1,
    AUTHOR_ID: 2,
    AUTHOR_NAME: 3,
    REGISTERED_DATE_FROM_DATE: 4,
    REGISTERED_DATE_TO_DATE: 5
};

SearchOption.Payment = SearchOptionList.Payment = {
    PRODUCT_TITLE: 1,
    USER_ID : 2,
    USER_NAME : 3,

    nameMap : {3 : '이름',
        2 : '아이디',
        1 : '상품명'},
    optionList : [
        {name : '상품명' , value : 1},{name : '아이디' , value : 2},{name : '이름' , value : 3}
    ],

    getNameMap : function() {
        return this.nameMap;
    },

    getOptionList : function() {
        return this.optionList;
    }
};

SearchOption.createOption = SearchOptionList.createOption = function (code, keyword) {
    var searchOptionList = new SearchOptionList();
    searchOptionList.add(code, keyword);
    return searchOptionList.get();
};

SearchOption.Coupon = SearchOptionList.Coupon = {
    TITLE : 1,
    START_DATE : 2,
    END_DATE : 3
};

SearchOption.Product = SearchOptionList.Product = {
    TITLE : 1,
    START_DATE : 2,
    END_DATE : 3
};




var SearchByDefault = {
    USER_ID: 1,
    USER_NAME: 2
};

var BoardContentStatus = {

    // 신규 접수
    NEW: 1000,

    // 구분
    ISSUE: 1001,
    CONTENT_TEAM_ISSUE: 1002,
    CONTENT_PROVIDER_ISSUE: 1003,
    TEACHER_ISSUE: 1004,

    PROCESSING: 2000,
    CONTENT_TEAM_PROCESSING: 2001,
    CONTENT_PROVIDER_PROCESSING: 2002,
    TEACHER_PROCESSING: 2003,

    WORKING : 2500,
    CONTENT_TEAM_WORKING : 2501,
    CONTENT_PROVIDER_WORKING: 2502,
    TEACHER_WORKING :2503,

    UNABLE_TO_PROCESS: 3000,
    CONTENT_TEAM_UNABLE_TO_PROCESS: 3001,
    CONTENT_PROVIDER_UNABLE_TO_PROCESS: 3002,
    TEACHER_UNABLE_TO_PROCESS: 3003,

    DONE: 4000,
    CONTENT_TEAM_DONE: 4001,
    CONTENT_PROVIDER_DONE: 4002,
    TEACHER_DONE: 4003,

    // 처리 완료
    CONFIRMED: 9000,

    codeMap: {

        1000: '신규 등록',

        1001: '이슈',
        1002: '콘텐츠 개발 팀 이슈',
        1003: 'CP 사 이슈',
        1004: '교강사 이슈',

        2000: '진행중',
        2001: '콘텐츠 개발 팀 진행중',
        2002: 'CP 사 진행중',
        2003: '교강사 진행중',

        2500: '처리중',
        2501: '콘텐츠 개발 팀 처리중',
        2502: 'CP 사 처리중',
        2503: '교강사 처리중',

        3000: '처리 불가',
        3001: '콘텐츠 개발 팀 처리 불가',
        3002: 'CP 사 처리 불가',
        3003: '교강사 처리 불가',

        4000: '처리 완료',
        4001: '콘텐츠 개발 팀 처리 완료',
        4002: 'CP 사 처리 완료',
        4003: '교강사 처리 완료',

        9000: '완료'
    },

    getName: function (code, defaultValue) {

        if (defaultValue == undefined)
            defaultValue = '-';

        return Lia.pd(defaultValue, BoardContentStatus.codeMap, code);
    },

    getNameSimply: function (code) {

        if (code <= 1000) {
            return '신규등록';
        } else if (code == 4000) {
            return '처리 완료';
        } else if (code < 9000) {
            return '처리 중';
        } else {
            return '답변완료';
        }
    },

    createOptionList: function (typeList, all, allText, allValue) {

        var optionList = [];

        if (all) {

            if (String.isBlank(allValue)) {

                allValue = '';
                for (var key in typeList) {

                    var type = typeList[key];
                    if (String.isNotBlank(allValue)) {
                        allValue += ',';

                    }

                    allValue += type;
                }
            }

            optionList.push({name: allText, value: allValue});
        }


        for (var key in typeList) {

            var arrayKey = typeList[key];
            var value = BoardContentStatus.codeMap[arrayKey];
            optionList.push({value: arrayKey, name: value});
        }

        return optionList;
    }
};


BoardContentStatus.qna = [
    BoardContentStatus.NEW,
    BoardContentStatus.PROCESSING,
    BoardContentStatus.CONFIRMED
];

BoardContentStatus.suggest = [
    BoardContentStatus.NEW,
    BoardContentStatus.ISSUE,
    BoardContentStatus.PROCESSING,
    BoardContentStatus.WORKING,
    BoardContentStatus.CONFIRMED
];

// TODO deprecated
var BoardContentSearchBy = {
    TITLE: 1,
    BODY: 2,
    TITLE_OR_BODY: 3,
    REGISTERED_BY_USER_NAME: 4,
    LAST_MODIFIED_BY_USER_NAME: 5,
    DELETED_BY_USER_NAME: 6,
    REGISTERED_BY_USER_ID: 7,
    LAST_MODIFIED_BY_USER_ID: 8,
    DELETED_BY_USER_ID: 9,
    REGISTERED_DATE_FROM_DATE: 10,
    REGISTERED_DATE_TO_DATE: 11,
    TITLE_FROM_CHARACTER: 12,
    TITLE_TO_CHARACTER: 13
};

var SystemEventLevel = {
    INFO: 1,
    WARNING: 2,
    ERROR: 3,

    codeMap: {
        1: '정보',
        2: '경고',
        3: '오류'
    },

    getCodeMap: function () {
        return SystemEventLevel.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = SystemEventLevel.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var UserReferrerType = {
    SEARCH_ENGINE: 1,
    PRESS: 2,
    SNS: 3,
    EMAIL: 4,
    ADMIN: 8,
    OTHER: 9,

    codeMap: {
        1: '포털검색',
        2: '언론매체',
        3: 'SNS',
        4: '홍보메일',
        8: '관리자',
        9: '기타'
    },

    getCodeMap: function () {
        return UserReferrerType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = UserReferrerType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var ThirdPartyUserAccountType = {
    SSN_AUTHENTICATION: 1,
    FACEBOOK: 2,
    TWITTER: 3,
    NAVER: 4,
    KAKAO: 5
};

var UserDeviceType = {
    UNKNOWN: 1,
    PC: 2,
    TABLET: 3,
    MOBILE: 4,

    codeMap: {
        1: '알수없음',
        2: 'PC',
        3: 'TABLET',
        4: 'MOBILE'
    },

    getName: function (code, defaultValue) {

        if (defaultValue == undefined)
            defaultValue = '';

        return Lia.pd(defaultValue, UserDeviceType.codeMap, code);

    }
};

var BoardOrderBy = {
    TITLE_ASC: 1,
    TITLE_DESC: 2,
    REGISTERED_DATE_ASC: 3,
    REGISTERED_DATE_DESC: 4,
    LAST_MODIFIED_DATE_ASC: 5,
    LAST_MODIFIED_DATE_DESC: 6,
    DELETED_DATE_ASC: 7,
    DELETED_DATE_DESC: 8,
    EFFECTIVE_START_DATE_ASC: 9,
    EFFECTIVE_START_DATE_DESC: 10,
    EFFECTIVE_END_DATE_ASC: 11,
    EFFECTIVE_END_DATE_DESC: 12,
    VIEW_COUNT_ASC: 13,
    VIEW_COUNT_DESC: 14
};


var UserEducationLevel = {
    DOCTORATE: 1,
    MASTER: 2,
    BACHELOR: 3,
    ASSOCIATE: 4,
    SECONDARY_SCHOOL: 5,
    //JUNIOR_SECONDARY_SCHOOL: 6,
    //ELEMENTARY_SCHOOL: 7,
    //NONE: 8,
    //OTHER: 9,

    codeMap: {
        1: '박사',
        2: '석사',
        3: '학사',
        4: '전문학사',
        5: '고졸'
        //6: '중졸',
        //7: '초졸',
        //8: '없음'
        //9: '기타'
    },

    createOptionList: function (addDefault, addDefaultName, addDefaultValue) {

        var optionList = [];

        if (addDefault) {

            if (addDefaultName == undefined) {
                addDefaultName = '선택';
            }

            if (addDefaultValue == undefined) {
                addDefaultValue = '';
            }


            optionList.push({name: addDefaultName, value: addDefaultValue});
        }

        for (var code in  UserEducationLevel.codeMap) {

            optionList.push({name: Lia.p(UserEducationLevel.codeMap, code), value: code});
        }


        return optionList;
    },

    getCodeMap: function () {
        return UserEducationLevel.codeMap;
    },

    getName: function (code, defaultText) {

        code = parseInt(code);
        var name = UserEducationLevel.codeMap[code];
        if (name == undefined)
            name = defaultText;

        return name;
    }
};

var UserEmploymentStatus = {

    // 무직
    UNEMPLOYED: 10,

    // 구인중
    JOB_SEARCHING: 11,

    // 재직중
    EMPLOYED_SMALL_COMPANY: 20,
    EMPLOYED_MEDIUM_COMPANY: 21,
    EMPLOYED_LARGE_COMPANY: 22,
    EMPLOYED_VERY_LARGE_COMPANY: 23,

    // e-koreatech에서는 사용x
    RETIRED: 30,

    codeMap: {
        10: '무직(구직 계획 없음)',
        11: '구직 중',
        20: '재직중 (소기업 - 50인 미만)',
        21: '재직중 (중기업 - 300인 미만)',
        22: '재직중 (중견기업 - 300인 이상)',
        23: '재직중 (대기업 - 1000인 이상)',
        30: '은퇴'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in UserEmploymentStatus.codeMap) {
            optionList.push({value: key, name: UserEmploymentStatus.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return UserEmploymentStatus.codeMap;
    },

    getName: function (code, defaultText) {

        code = parseInt(code);
        var name = UserEmploymentStatus.codeMap[code];
        if (name == undefined)
            name = defaultText;

        return name;
    }
};

//var SystemVariableName = {
//    'USER_ID_PATTERN' : 'USER_ID_PATTERN',
//    'MULTI_LOGIN_LEVEL' : 'MULTI_LOGIN_LEVEL',
//    'FILE_UPLOAD_PATH_TO_CDN' : 'FILE_UPLOAD_PATH_TO_CDN',
//    'FILE_UPLOAD_DIR_PATH' : 'FILE_UPLOAD_DIR_PATH',
//    'FILE_UPLOAD_DIR_NAME' : 'FILE_UPLOAD_DIR_NAME',
//    'ID_CERT_PATH' : 'ID_CERT_PATH',
//    'ID_CERT_CP_CODE' : 'ID_CERT_CP_CODE',
//    'ID_CERT_IDP_URL' : 'ID_CERT_IDP_URL',
//    'ID_CERT_RETURN_DOMAIN' : 'ID_CERT_RETURN_DOMAIN',
//    'ID_CERT_HS_ACTION_URL' : 'ID_CERT_HS_ACTION_URL',
//    'ID_CERT_IPIN_ACTION_URL' : 'ID_CERT_IPIN_ACTION_URL',
//    'ID_CERT_HS_END_POINT_URL' : 'ID_CERT_HS_END_POINT_URL',
//    'ID_CERT_IPIN_END_POINT_URL' : 'ID_CERT_IPIN_END_POINT_URL',
//    'FILE_UPLOAD_FTP_IP' : 'FILE_UPLOAD_FTP_IP',
//    'FILE_UPLOAD_FTP_PORT' : 'FILE_UPLOAD_FTP_PORT',
//    'FILE_UPLOAD_FTP_ID' : 'FILE_UPLOAD_FTP_ID',
//    'FILE_UPLOAD_FTP_PW' : 'FILE_UPLOAD_FTP_PW',
//    'FILE_UPLOAD_FTP_PATH' : 'FILE_UPLOAD_FTP_PATH',
//    'FILE_DOWNLOAD_URL_PREFIX' : 'FILE_DOWNLOAD_URL_PREFIX',
//    'COURSE_VOD_RTMP_URL_FORMAT' : 'COURSE_VOD_RTMP_URL_FORMAT',
//    'COURSE_VOD_HLS_URL_FORMAT' : 'COURSE_VOD_HLS_URL_FORMAT',
//    'COURSE_VOD_RTSP_URL_FORMAT' : 'COURSE_VOD_RTSP_URL_FORMAT',
//    'DEFAULT_EMAIL_ADDRESS' : 'DEFAULT_EMAIL_ADDRESS',
//    'DEFAULT_PHONE_NUMBER' : 'DEFAULT_PHONE_NUMBER',
//
//    codeMap : {
//        'USER_ID_PATTERN' : '아이디 형식',
//        'MULTI_LOGIN_LEVEL' : '중복 로그인 권한',
//        'FILE_UPLOAD_PATH_TO_CDN' : '',
//        'FILE_UPLOAD_DIR_PATH' : '파일 업로드 경로',
//        'FILE_UPLOAD_DIR_NAME' : '',
//        'ID_CERT_PATH' : '',
//        'ID_CERT_CP_CODE' : '',
//        'ID_CERT_IDP_URL' : '',
//        'ID_CERT_RETURN_DOMAIN' : '',
//        'ID_CERT_HS_ACTION_URL' : '',
//        'ID_CERT_IPIN_ACTION_URL' : '',
//        'ID_CERT_HS_END_POINT_URL' : '',
//        'ID_CERT_IPIN_END_POINT_URL' : '',
//        'FILE_UPLOAD_FTP_IP' : '콘텐츠 FTP IP',
//        'FILE_UPLOAD_FTP_PORT' : '콘텐츠 FTP PORT',
//        'FILE_UPLOAD_FTP_ID' : '콘텐츠 FTP ID',
//        'FILE_UPLOAD_FTP_PW' : '콘텐츠 FTP PW',
//        'FILE_UPLOAD_FTP_PATH' : '콘텐츠 업로드 경로',
//        'FILE_DOWNLOAD_URL_PREFIX' : '첨부파일 다운로드 URL',
//        'COURSE_VOD_RTMP_URL_FORMAT' : '',
//        'COURSE_VOD_HLS_URL_FORMAT' : '',
//        'COURSE_VOD_RTSP_URL_FORMAT' : '',
//        'DEFAULT_EMAIL_ADDRESS' : '시스템 이메일',
//        'DEFAULT_PHONE_NUMBER' : '시스템 전화번호'
//    },
//
//    getCodeMap : function () {
//        return SystemVariableName.codeMap;
//    },
//
//    getName : function (code) {
//
//        //code = parse(code);
//        var name = SystemVariableName.codeMap[code];
//        if ( name == undefined )
//            name = '';
//
//        return name;
//    }
//};

var Institution = {
    FORMAL: 'FORMAL',
    INFORMAL: 'INFORMAL',
    LAB: 'LAB',
    MARKET: 'MARKET',

    codeMap: {
        'FORMAL': '평생능력개발',
        'INFORMAL': '비형식',
        'LAB': '온라인실습실',
        'MARKET': 'e-koreatech마켓'
    },

    getCodeMap: function () {
        return Institution.codeMap;
    },

    getName: function (code, defaultText) {

        if (code == 'FORMAL')
            return '평생능력개발';
        else if (code == 'INFORMAL')
            return '비형식';
        else if (code == 'LAB')
            return '온라인실습실';
        else if (code == 'MARKET')
            return 'e-koreatech마켓';
    }
};

var UserGender = {
    MALE: 1,
    FEMALE: 2,
    OTHER: 3,
    UNKNOWN: 4,

    codeMap: {
        1: '남자',
        2: '여자',
        3: '기타',
        4: '알수없음'
    },

    getCodeMap: function () {
        return UserGender.codeMap;
    },

    getName: function (code, defaultText) {

        code = parseInt(code);
        var name = UserGender.codeMap[code];
        if (name == undefined)
            name = defaultText;

        return name;
    }

};

var CourseContentItemType = {
    UNIT: 1,
    LESSON: 2,
    LINK: 3
};

var UserOrderBy = {

    ID_ASC: 1,
    ID_DESC: 2,
    NAME_ASC: 3,
    NAME_DESC: 4,
    EMAIL_ASC: 5,
    EMAIL_DESC: 6,
    ADDRESS_ASC: 7,
    ADDRESS_DESC: 8,
    REGISTERED_DATE_ASC: 9,
    REGISTERED_DATE_DESC: 10
};

var UserRole = {
    ADMIN: 10,
    OPERATION_ADMIN: 11,
    DEPARTMENT_ADMIN: 12,
    BOARD_MEMBER: 19,
    MEMBER: 20,
    NOT_LOGGED_IN: 50,

    codeMap: {
        10: '관리자',
        11: '운영 관리자',
        12: '학과 관리자',
        19: '게시판 사용자',
        20: '일반 사용자'
    },

    getCodeMap: function () {
        return UserRole.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = UserRole.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },

    createOptionList: function (all, allName, nameSuffix) {

        var optionList = [];

        if (all) {

            if (String.isBlank(allName))
                allName = '전체';

            optionList.push({
                name: allName,
                value: ''
            });
        }

        for (var key in UserRole.codeMap) {

            var name = UserRole.codeMap[key];

            if (String.isNotBlank(nameSuffix))
                name = name + nameSuffix

            optionList.push({value: key, name: name});
        }

        return optionList;
    }
};


SearchOption.SurveyParticipant = SearchOptionList.SurveyParticipant = {
    USER_ID :  1,
    USER_NAME : 2
};

var SurveyRequestType = {

    GENERAL: 1,

    codeMap: {
        1: '일반'
    },

    getCodeMap: function () {
        return SurveyRequestType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = SurveyRequestType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in SurveyRequestType.codeMap) {
            optionList.push({value: key, name: SurveyRequestType.codeMap[key]});
        }

        return optionList;
    }

};


var UserSearchBy = {
    ID: 1,
    NAME: 2,
    JOB: 3,
    COMPANY_NAME: 4,
    EMAIL: 5,
    ADDRESS: 6,
    PHONE_NUMBER: 7,
    REGISTERED_DATE_FROM_DATE: 8,
    REGISTERED_DATE_TO_DATE: 9
};

var UserStatus = {
    ACTIVE: 1,
    INACTIVE: 2,
    DORMANT: 3,
    WITHDRAW: 4,
    TEMPORARY: 5,

    codeMap: {
        1: '활성',
        2: '비활성',
        3: '휴면',
        4: '탈퇴',
        5: '임시'
    },

    createOptionList: function (addDefault, addDefaultName, addDefaultValue) {

        var optionList = [];

        if (addDefault) {

            if (addDefaultName == undefined) {
                addDefaultName = '전체';
            }

            if (addDefaultValue == undefined) {
                addDefaultValue = '';
            }


            optionList.push({name: addDefaultName, value: addDefaultValue});
        }

        for (var key in UserStatus.codeMap) {
            optionList.push({value: key, name: UserStatus.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return UserStatus.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = UserStatus.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var StatisticsType = {

    YEARLY: 20,
    MONTHLY: 21,
    DAILY: 22,
    HOURLY: 23,

    codeMap: {
        20: '연별',
        21: '월별',
        22: '일별',
        23: '시간별'
    },

    getName: function (code) {

        code = parseInt(code);
        var name = StatisticsType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var CourseEnrollmentStatus = {

    ENROLLMENT_REQUESTED: 10,
    AUDITING_REQUESTED: 11,
    ENROLLED: 20,
    AUDITING: 21,
    UNENROLLED: 30,
    AUDITING_CANCELLED: 31,

    codeMap: {
        10: '수강 대기',
        11: '청강 대기',
        20: '수강 중',
        21: '청강 중',
        30: '수강 취소',
        31: '청강 취소'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in CourseEnrollmentStatus.codeMap) {
            optionList.push({value: key, name: CourseEnrollmentStatus.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return CourseEnrollmentStatus.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = CourseEnrollmentStatus.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var CourseCodeYear = {

    2003: 2003,
    2004: 2004,
    2005: 2005,
    2006: 2006,
    2007: 2007,
    2008: 2008,
    2009: 2009,
    2010: 2010,
    2011: 2011,
    2012: 2012,
    2013: 2013,
    2014: 2014,
    2015: 2015,
    2016: 2016,
    2017: 2017,
    2018: 2018,
    2019: 2019,
    2020: 2020,
    2021: 2021,
    2022: 2022,
    2023: 2023,
    2024: 2024,
    2025: 2025,
    2026: 2026,

    codeMap: {
        2003: '2003',
        2004: '2004',
        2005: '2005',
        2006: '2006',
        2007: '2007',
        2008: '2008',
        2009: '2009',
        2010: '2010',
        2011: '2011',
        2012: '2012',
        2013: '2013',
        2014: '2014',
        2015: '2015',
        2016: '2016',
        2017: '2017',
        2018: '2018',
        2019: '2019',
        2020: '2020',
        2021: '2021',
        2022: '2022',
        2023: '2023',
        2024: '2024',
        2025: '2025',
        2026: '2026'
    },

    createOptionList: function () {

        var optionList = [];

        optionList.push({value: '', name: '선택'});

        for (var key in CourseCodeYear.codeMap) {
            optionList.push({value: key, name: CourseCodeYear.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return CourseCodeYear.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = CourseCodeYear.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var ContentType = {

    HTML: 1,
    JSON: 2,
    XML: 3,
    LINK: 4,
    HTML_SCRIPT: 5,
    BOARD: 6,
    CALENDAR: 7,
    MENU_LINK: 8,

    codeMap: {
        1: 'HTML',
        2: 'JSON',
        3: 'XML',
        4: 'LINK',
        5: 'HTML+SCRIPT',
        6: 'BOARD',
        7: 'CALENDAR',
        8: 'MENU LINK'
    },

    createOptionList: function () {

        var optionList = [];

        optionList.push({value: '', name: '선택'});

        for (var key in ContentType.codeMap) {
            optionList.push({value: key, name: ContentType.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return ContentType.codeMap;
    },

    setCodeMap : function( map ) {
        ContentType.codeMap = map;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = ContentType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var PackageContentPackageType = {

    IFRAME: 1,
    SCORM: 2,
    ETC: 9,

    codeMap: {
        1: 'IFRAME',
        2: 'FLASH',
        9: 'ETC'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in PackageContentPackageType.codeMap) {
            optionList.push({value: key, name: PackageContentPackageType.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return PackageContentPackageType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = PackageContentPackageType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var VideoType = {
    VIMEO: 1,
    YOUTUBE: 2,

    codeMap: {
        1: 'VIMEO',
        2: 'YOUTUBE'
    },

    getName: function (code) {

        code = parseInt(code);
        var name = VideoType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var VideoContentVideoType = {
    FILE: 1,
    YOU_TUBE: 2,
    VIMEO: 3,

    codeMap: {
        1: 'FILE',
        2: 'YOUTUBE',
        3: 'VIMEO'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in VideoContentVideoType.codeMap) {
            optionList.push({value: key, name: VideoContentVideoType.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return VideoContentVideoType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = VideoContentVideoType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var QuestionDifficulty = {

    EASIEST: 1,
    EASY: 2,
    MEDIUM: 3,
    HARD: 4,
    HARDEST: 5,

    codeMap: {
        1: '최하',
        2: '하',
        3: '중',
        4: '상',
        5: '최상'
    },

    createOptionList: function (contansRandomSelect) {

        var optionList = [];

        if (contansRandomSelect) {
            optionList.push({value: '', name: '임의 선택'})
        }

        for (var key in QuestionDifficulty.codeMap) {
            optionList.push({value: key, name: QuestionDifficulty.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return QuestionDifficulty.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = QuestionDifficulty.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var QuestionType = {

    MULTIPLE_CHOICE: 1,
    TRUE_FALSE: 2,
    SHORT_ANSWER: 3,
    ESSAYS: 4,
    MULTIPLE_CHOICE_WITH_OTHER_OPTION: 5,

    codeMap: {
        1: '객관식',
        5: '객관식+기타입력',
        2: 'O,X',
        3: '단답형',
        4: '서술형'
    },

    createOptionList: function (containsRandomSelect, surveyMode) {

        var optionList = [];

        if (containsRandomSelect) {
            optionList.push({value: '', name: '임의 선택'});
        }


        optionList.push({
            value: QuestionType.MULTIPLE_CHOICE,
            name: QuestionType.codeMap[QuestionType.MULTIPLE_CHOICE]
        });

        if (surveyMode)
            optionList.push({
                value: QuestionType.MULTIPLE_CHOICE_WITH_OTHER_OPTION,
                name: QuestionType.codeMap[QuestionType.MULTIPLE_CHOICE_WITH_OTHER_OPTION]
            });

        optionList.push({value: QuestionType.TRUE_FALSE, name: QuestionType.codeMap[QuestionType.TRUE_FALSE]});
        optionList.push({value: QuestionType.SHORT_ANSWER, name: QuestionType.codeMap[QuestionType.SHORT_ANSWER]});
        optionList.push({value: QuestionType.ESSAYS, name: QuestionType.codeMap[QuestionType.ESSAYS]});

        return optionList;
    },

    getCodeMap: function () {
        return QuestionType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = QuestionType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var ApplicationFormItemQuestionType = {

    MULTIPLE_CHOICE: 1,
    TRUE_FALSE: 2,
    SHORT_ANSWER: 3,
    ESSAYS: 4,
    MULTIPLE_CHOICE_WITH_OTHER_OPTION: 5,
    DATETIME: 6,
    FILE_UPLOAD: 7,

    codeMap: {
        1: '객관식',
        5: '객관식+기타입력',
        2: 'O,X',
        3: '단답형',
        6: '날짜',
        4: '서술형',
        7: '파일'
    },

    createOptionList: function (type) {

        var optionList = [];

        if (type == 'drone') {

            optionList.push({
                value: ApplicationFormItemQuestionType.MULTIPLE_CHOICE,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.MULTIPLE_CHOICE]
            });

            optionList.push({
                value: ApplicationFormItemQuestionType.SHORT_ANSWER,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.SHORT_ANSWER]
            });

            optionList.push({
                value: ApplicationFormItemQuestionType.ESSAYS,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.ESSAYS]
            });

            optionList.push({
                value: ApplicationFormItemQuestionType.FILE_UPLOAD,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.FILE_UPLOAD]
            });


        } else if(type == undefined){

            optionList.push({
                value: ApplicationFormItemQuestionType.MULTIPLE_CHOICE,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.MULTIPLE_CHOICE]
            });

            optionList.push({
                value: ApplicationFormItemQuestionType.MULTIPLE_CHOICE_WITH_OTHER_OPTION,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.MULTIPLE_CHOICE_WITH_OTHER_OPTION]
            });

            optionList.push({
                value: ApplicationFormItemQuestionType.TRUE_FALSE,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.TRUE_FALSE]
            });
            optionList.push({
                value: ApplicationFormItemQuestionType.SHORT_ANSWER,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.SHORT_ANSWER]
            });
            optionList.push({
                value: ApplicationFormItemQuestionType.DATETIME,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.DATETIME]
            });
            optionList.push({
                value: ApplicationFormItemQuestionType.ESSAYS,
                name: ApplicationFormItemQuestionType.codeMap[ApplicationFormItemQuestionType.ESSAYS]
            });
        }

        return optionList;
    },

    getCodeMap: function () {
        return ApplicationFormItemQuestionType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = ApplicationFormItemQuestionType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var ApplicationFormItemCheckType = {

    NONE: 0,
    ID: 1,
    NAME: 2,
    EMAIL: 3,
    NUMERIC: 4,

    codeMap: {
        1: '없음',
        2: '아이디',
        3: '이름',
        4: '이메일',
        5: '숫자'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in ApplicationFormItemCheckType.codeMap) {

            optionList.push({
                value: key,
                name: ApplicationFormItemCheckType.codeMap[key]
            });

        }

        return optionList;
    },

    getCodeMap: function () {
        return ApplicationFormItemCheckType.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = ApplicationFormItemCheckType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    },

    check: function (code, value) {

        if (code == ApplicationFormItemCheckType.NONE) {
            return true;
        } else if (code == ApplicationFormItemCheckType.ID) {
            return Lia.checkValidId(value);
        } else if (code == ApplicationFormItemCheckType.NAME) {
            return Lia.checkValidName(value);
        } else if (code == ApplicationFormItemCheckType.EMAIL) {
            return Lia.checkValidName(value);
        } else if (code == ApplicationFormItemCheckType.NUMERIC) {
            return Lia.checkValidNumeric(value);
        }

        return true;
    }
};


var ApplicationFormItemListType = {

    NONE: 1,
    COMBO_BOX: 2,
    LIST: 3,

    codeMap: {
        1: '선택',
        2: '콤보박스',
        3: '나열'
    },

    createOptionList: function () {

        var optionList = [];

        optionList.push({
            value: ApplicationFormItemListType.NONE,
            name: ApplicationFormItemListType.codeMap[ApplicationFormItemListType.NONE]
        });

        optionList.push({
            value: ApplicationFormItemListType.COMBO_BOX,
            name: ApplicationFormItemListType.codeMap[ApplicationFormItemListType.COMBO_BOX]
        });

        optionList.push({
            value: ApplicationFormItemListType.LIST,
            name: ApplicationFormItemListType.codeMap[ApplicationFormItemListType.LIST]
        });

        return optionList;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = ApplicationFormItemListType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};


var UploadedFileCategory = {

    USER_RESOURCE_PUBLIC: 1000,
    BOARD_ATTACHMENT_PUBLIC: 1001,
    HTML_EDITOR_PUBLIC: 1004,
    TEMPORARY_PUBLIC: 1005,

    // Private
    USER_RESOURCE_PRIVATE: 2000,
    BOARD_ATTACHMENT_PRIVATE: 2001,
    HTML_EDITOR_PRIVATE: 2004,
    TEMPORARY_PRIVATE: 2005,

    // FTP
    CONTENT_FTP: 3000
};

var LanguageType = {

    KO: 'ko',
    EN: 'en',
    ZH: 'zh',
    VI: 'vi',

    codeMap: {
        'ko' : '한국어'
        // 'en' : '영어',
        // 'zh' : '중국어',
        // 'vi' : '베트남어'
    },

    setCodeMap : function( map ) {
        LanguageType.codeMap = map;
    },

    getCodeMap: function () {
        return LanguageType.codeMap;
    },

    createOptionList: function (addDefault, addDefaultName, addDefaultValue) {

        var optionList = [];

        if (addDefault) {

            if (addDefaultName == undefined) {
                addDefaultName = '선택';
            }

            if (addDefaultValue == undefined) {
                addDefaultValue = '';
            }


            optionList.push({name: addDefaultName, value: addDefaultValue});
        }

        for (var code in LanguageType.codeMap) {

            optionList.push({name: Lia.p(LanguageType.codeMap, code), value: code});
        }


        return optionList;
    },

    getName: function (code) {

        var name = LanguageType.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var LessonItemMobileCompatibility = {

    FULLY_SUPPORTED: 1,
    FULLY_SUPPORTED_BUT_MOBILE_APP_REQUIRED: 2,
    FULLY_SUPPORTED_BUT_MOBILE_APP_RECOMMENDED: 3,
    PC_ONLY: 4,
    MOBILE_ONLY: 5,


    codeMap: {
        1: 'PC + 모바일',
        2: 'PC + 모바일 (앱 설치 필요)',
        3: 'PC + 모바일 (앱 설치 권장)',
        4: 'PC',
        5: '모바일'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in LessonItemMobileCompatibility.codeMap) {
            optionList.push({value: key, name: LessonItemMobileCompatibility.codeMap[key]});
        }

        return optionList;
    },

    getCodeMap: function () {
        return LessonItemMobileCompatibility.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = LessonItemMobileCompatibility.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var MarkingSchemeCategory = {

    EXAM: 1,
    QUIZ: 2,
    ASSIGNMENT: 3,
    FORUM: 4,
    LIVE_SEMINAR: 5,
    ATTENDANCE: 9
};


var StudentAttendanceStatus = {
    PRESENT: 1,
    LATE: 2,
    NOT_ENOUGH_LEARNING_TIME: 3,
    ATTENDANCE_POPUP_TIMEOUT: 4,
    ABSENT: 5,

    codeMap: {
        1: '출석',
        2: '지각',
        3: '시간 미달',
        4: '팝업 미체크',
        5: '결석'
    },

    getCodeMap: function () {
        return StudentAttendanceStatus.codeMap;
    },

    getName: function (code) {

        code = parseInt(code);
        var name = StudentAttendanceStatus.codeMap[code];
        if (name == undefined)
            name = '';

        return name;
    }
};

var ApplicationFormItemType = {

    REQUIRED: 1,
    OPTIONAL: 2,
    UNNECESSARY: 3,

    codeMap: {
        1: '필수',
        2: '옵션',
        3: '사용하지않음'
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in ApplicationFormItemType.codeMap) {
            optionList.push({value: key, name: ApplicationFormItemType.codeMap[key]});
        }

        return optionList;
    }
};

var ApplicationFormItemValue = {

    INTEGER: 1,
    DECIMAL: 2,
    STRING: 3,
    TEXT: 4,
    BOOLEAN: 5,
    DATETIME: 6,

    codeMap: {
        1: 'INTEGER',
        2: 'DECIMAL',
        3: 'STRING',
        4: 'TEXT',
        5: 'BOOLEAN',
        6: 'DATETIME'
    },

    getCodeMap: function () {
        return ApplicationFormItemValue.codeMap;
    },

    createOptionList: function () {

        var optionList = [];

        for (var key in ApplicationFormItemValue.codeMap) {
            optionList.push({value: key, name: ApplicationFormItemValue.codeMap[key]});
        }

        return optionList;
    },

    getFieldName: function (code) {

        var name = ApplicationFormItemValue.codeMap[code];
        return name.toLowerCase() + "_value";
    }
};



var AsyncTaskStatus = {
    NEW: 1,
    PROCESSING: 2,
    CANCELLED: 3,
    FAILED: 4,
    COMPLETED: 5,

    codeMap: {
        1: '생성',
        2: '처리 중',
        3: '취소',
        4: '실패',
        5: '완료'
    },

    getName: function (code) {
        return Lia.pd('', AsyncTaskStatus.codeMap, code);
    }
};


// ALL_SUCCESS(1),
//     PARTIAL_SUCCESS(2),
//     ALL_FAIL(3);

var AsyncTaskResultStatus = {
    ALL_SUCCESS: 1,
    PARTIAL_SUCCESS: 2,
    ALL_FAIL: 3,

    codeMap: {
        1: '전체 성공',
        2: '부분 성공',
        3: '전체 실패'
    },

    getName: function (code) {
        return Lia.pd('', AsyncTaskResultStatus.codeMap, code);
    }
};



var ChartConstants = {

    Color: {

        YELLOW: 'rgba(255,255,128,1)',
        GREEN: 'rgba(128,255,128,1)',
        RED: 'rgba(255,128,128,1)',
        ORGANGE: 'rgba(255,160,128,1)',
        BLUE: 'rgba(64,128,255,1)',
        TURQUOISE: 'rgba(128,255,255,1)',
        PURPLE: 'rgba(192,128,255,1)',
        PINK: 'rgba(255,128,255,1)',
        GREY: 'rgba(172,172,172,1)'
    }
};

var UserEventType = {
    LOGIN :10000,
    LOGIN_WITH_THIRD_PARTY_ACCOUNT :10001,
    LOGOUT :10002,
    CMS_PAGE:10003,
    MENU:10004,
    SERVICE_PAGE:10005
};




var PolarisStrings = undefined;
var PlutoStrings = undefined;
var ProjectStrings = PolarisStrings = PlutoStrings = {};
ProjectStrings.TITLE = "VSQUARE";
ProjectStrings.COPYRIGHT = "Copyright © VSQUARE Inc. ALL RIGHTS RESERVED.";


var PolarisSettings = undefined;
var PlutoSettings = undefined;
var ProjectSettings = PolarisSettings = PlutoSettings = {};

ProjectSettings.USE_MULTI_LANGUAGE = false;
ProjectSettings.USE_USER_RECEIVE_EMAIL = false;
ProjectSettings.USE_USER_REGISTERED_DATE = false;
ProjectSettings.USE_MENU_BOARD_ALLOW_VOTE = false;
ProjectSettings.USE_MENU_BOARD_ALLOW_ANONYMOUS = false;
ProjectSettings.USE_MENU_BOARD_IS_RESTRICTABLE = false;
ProjectSettings.USE_REF_PAGE_URL = true;
ProjectSettings.USE_MENU_BOARD_WRITEABLE_WITHOUT_LOGGED_IN = false;
ProjectSettings.MENU_EDIT_ONLY = false;
ProjectSettings.MULTIPLE_CHOICE_DI_IDX = 999;
ProjectSettings.MULTIPLE_CHOICE_DI_PREFIX = '#_';
ProjectSettings.DEFAULT_MENU_NAME = 'menu';

ProjectSettings.TabStorageKey = undefined;
ProjectSettings.PageConstructorType = undefined;
ProjectSettings.PageConstructorMenuPanelWidth = undefined;
ProjectSettings.Logo = {
    logoImageUrl: '/res/cms/img/index/img_header_logo.png',
    logoImageHeight: '35px',
    mobileLogoImageHeight: '25px'
};

ProjectSettings.BlueCMSLoginButton = {
    loginLogoContainerUrl : '/res/cms/img/login/img_login_logo_b.png',
    backgroundColor : '#123C6F',
    jutPressedBackgroundColor : '#104B94',
    jutBackgroundColor : '#17539D',
    textColor : '#FFFFFF'
};

ProjectSettings.RedCMSLoginButton = {
    loginLogoContainerUrl : '/res/cms/img/login/img_login_logo_r.png',
    backgroundColor : '#940000',
    jutPressedBackgroundColor : '#bc0000',
    jutBackgroundColor : '#bc0000',
    textColor : '#FFFFFF'
};

ProjectSettings.DEFAULT_EXCEL_DOWNLOAD_COUNT = 5000;
ProjectSettings.CMSLoginButton = ProjectSettings.BlueCMSLoginButton;
ProjectSettings.ListTableWith = {
    ROW_NUMBER : '80px',
    USER_NAME : '150px',
    CHECK_BOX : '50px',
    USER_ID : '150px',
    DATE : '80px',
    DATETIME : '90px',
    START_DATE_AND_END_DATE: '85px',
    START_DATETIME_AND_END_DATETIME: '170px'
};

ProjectSettings.DetailTableWidth = {
    SMALL : '100px',
    DEFAULT  : '150px',
    LEV_2 : '190px',
    EVALUATION : '265px',
    SEARCH  : '150px'
};

ProjectSettings.CountOptionList = [
    { name : '10개씩 보기', value : 10 },
    { name : '20개씩 보기', value : 20, selected : true },
    { name : '30개씩 보기', value : 30 },
    { name : '40개씩 보기', value : 40 },
    { name : '50개씩 보기', value : 50 },
    { name : '60개씩 보기', value : 60 },
    { name : '70개씩 보기', value : 70 },
    { name : '80개씩 보기', value : 80 },
    { name : '90개씩 보기', value : 90 },
    { name : '100개씩 보기', value : 100 }
];


ProjectSettings.Menu = {};

ProjectSettings.Menu.rootDepartmentIdx = 1;

ProjectSettings.Menu.onPageUrl = function( menu ) {

    var pageUrl = '/';

    var departmentIdx = Lia.p(menu, 'department_idx');
    if ( ProjectSettings.Menu.rootDepartmentIdx == departmentIdx ) {
        return pageUrl;
    }

    var departmentId = Lia.p(menu, 'department_id');
    if ( String.isNotBlank(departmentId) ) {
        pageUrl = '/department/' + departmentId;
    }

    return pageUrl;
};

ProjectSettings.Menu.onPageBoardParameterMap = function( menuId, parentMenuId ) {
    return {
        'm1' : 'normal/board'
    };
};




ProjectSettings.CustomMenuBoard = {};

ProjectSettings.CustomMenuBoard.onBoardListBaseRequestParameterMap = function( map, menu ) {
    return map;
};

ProjectSettings.CustomMenuBoard.setBoardOption = function (menu, boardOption) {
    return boardOption;
};

ProjectSettings.CustomMenuBoard.onBoardList = function( menu, boardList ) {
};
ProjectSettings.CustomMenuBoard.onBoardListFieldList = function( menu ) {
    return undefined;
};
ProjectSettings.CustomMenuBoard.onBoardListMode = function( menu ) {
    return Triton.BoardList.Mode.GENERAL;
};

ProjectSettings.CustomMenuBoard.onBoardDetail = function( menu, boardContent, boardDetail ) {
    return undefined;
};
ProjectSettings.CustomMenuBoard.onBoardDetailFieldList = function( menu, boardContent ) {
    return undefined;
};

ProjectSettings.CustomMenuBoard.onBoardDetailEditable = function( menu, boardContent ) {
    return true;
};

ProjectSettings.CustomMenuBoard.onBoardWrite = function( menu, boardContent, boardWrite ) {
};

ProjectSettings.CustomMenuBoard.onBoardWriteFieldList = function( menu, boardContent ) {
    return undefined;
};
ProjectSettings.CustomMenuBoard.onBoardWriteSaved = function( menu, boardWrite, parameterMap, data ) {
    return true;
};

ProjectSettings.CustomMenuBoard.onDepartmentFilter = function( list ) {
    return list;
};


ProjectSettings.CustomMenuWriteFieldList = {
    list : [],
    add : function( item ) {
        ProjectSettings.CustomMenuWriteFieldList.list.push(item);
    },
    getList : function() {
        return ProjectSettings.CustomMenuWriteFieldList.list;
    }
};