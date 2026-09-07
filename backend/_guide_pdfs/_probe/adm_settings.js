
ProjectStrings.TITLE = "총신대학교";
ProjectStrings.COPYRIGHT = "Copyright © 2017 CSU. ALL RIGHTS RESERVED.";
ProjectSettings.USE_MULTI_LANGUAGE = false;
ProjectSettings.USE_MENU_BOARD_WRITEABLE_WITHOUT_LOGGED_IN = true;

ProjectSettings.UserInfo = {};
ProjectSettings.UserInfo.onAppendToButtonSectionInHome = function ( buttonSection, user ) {};
ProjectSettings.UserInfo.onIndexLoaded = function () {};

var checkValidDepartmentIdx = function( idx ) {
    return !Lia.contains(idx, 2, 3, 4, 5, 6, 7, 8, 9, 10, 29, 37);
}


ProjectSettings.CustomMenuBoard.onDepartmentFilter = function( list ) {

    var newList = [];
    for ( var i = 0, l = list.length; i < l; i++ ) {

        var item = list[i];
        var idx = Lia.p(item,'idx');
        if ( checkValidDepartmentIdx (idx) ) {
            newList.push(item);
        }
    }

    return newList;
};

LanguageType.setCodeMap({
    'ko' : '한국어'
    // 'en' : '영어',
    // 'zh' : '중국어',
    // 'vi' : '베트남어'
});




BoardType.setCodeMap({
    1: '공지사항',
    2: '자료실',
    3: '질의응답',
    4: '자주묻는질문',
    
    // 문서 관련
    5: '문서 PDF 뷰',
    // 51: '문서 리스트',

    // 갤러리 관련
    6: '갤러리',
    // 61: '액자형 갤러리',

    // 그 외의 양식
    9: '일반 게시판',
    // 91: '교수 리스트'
});

ContentType.setCodeMap({
    1: 'HTML',
    2: 'JSON',
    3: 'XML',
    4: 'LINK',
    5: 'HTML+SCRIPT',
    6: 'BOARD',
    7: 'CALENDAR',
    8: 'MENU LINK'
});

// 커스텀용
BoardType['DOCUMENT_LIST'] = 51;
BoardType['GALLERY_FRAME'] = 61;
BoardType['FACULTY_LIST'] = 91;

var BaseMenuList = {};
BaseMenuList[UserRole.ADMIN] = [

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico9.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico9_pressed.png',

        'text': '사용자',
        'menu': ['user'],
        'subMenuList' : [
            {'text': '계정관리', 'menu': ['user/account']},
            {'text': '학과 관리자 배정', 'menu': ['user/department_admin_manage']}
        ]
    },

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10_pressed.png',

        'text': '홈페이지',
        'menu': ['menu']
    },
    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6_pressed.png',

        'text': '학사일정',
        'menu': ['schedule']
    },
    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1_pressed.png',

        'text': '배너',
        'menu': ['main/banner'],
        'markPrefixList': ['main/banner', 'main/banner_write', 'main/banner_detail']
    },
    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1_pressed.png',

        'text': '발전기금',
        'menu': ['fund'],
        'subMenuList': [
            {
                'text': '온라인신청',
                'menu': ['fund/application'],
                'subMenuList': [
                    {'text': '온라인신청 양식 관리',
                        'menu': ['fund/application/application_form'],
                        'markPrefixList' : ['fund/application/application_form_register']
                    },
                    {'text': '온라인신청 관리',
                        'menu': ['fund/application/application'],
                        'markPrefixList' : [
                            'fund/application/application_detail',
                            'fund/application/user_application_detail',
                            'fund/application/application_register']
                    }
                ]
            },
            // {
            //     'text': '후원현황 관리',
            //     'menu': ['fund/status/fund_status']
            // }
        ]
    },
    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15_pressed.png',

        'menu': ['logout'],
        'text': '로그아웃'
    }

];



BaseMenuList[UserRole.OPERATION_ADMIN] = [

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10_pressed.png',

        'text': '홈페이지',
        'menu': ['menu']
    },

    Array.isNotEmpty(Server.departmentScheduleAdministratorSummaryList)?{
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6_pressed.png',

        'text': '학사일정',
        'menu': ['schedule']
    }:undefined,

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15_pressed.png',

        'menu': ['logout'],
        'text': '로그아웃'
    }

];

BaseMenuList[UserRole.DEPARTMENT_ADMIN] = [

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico10_pressed.png',

        'text': '홈페이지',
        'menu': ['menu']
    },

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico6_pressed.png',

        'text': '학사일정',
        'menu': ['schedule']
    },

    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1_pressed.png',

        'text': '배너',
        'menu': ['main/banner'],
        'markPrefixList': ['main/banner', 'main/banner_write', 'main/banner_detail']
    },
    // {
    //     'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1.png',
    //     'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico1_pressed.png',
    //
    //     'text': '발전기금',
    //     'menu': ['application'],
    //     'subMenuList': [
    //         {'text': '온라인신청 양식 관리',
    //             'menu': ['application/application_form'],
    //             'markPrefixList' : ['application/application_form_register']
    //         },
    //         {'text': '온라인신청 관리',
    //             'menu': ['application/application'],
    //             'markPrefixList' : [
    //                 'application/application_detail',
    //                 'application/user_application_detail',
    //                 'application/application_register']
    //         }
    //     ]
    // },
    {
        'iconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15.png',
        'pressedIconImageUrl': '/res/lia/triton/img/menu_sidedropdown/ico15_pressed.png',

        'menu': ['logout'],
        'text': '로그아웃'
    }

];


// 교수진소개 커스텀 입력란
var FaciltyData = {
    PROFNAME: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '성명'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'title');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "성명"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'title' },
                    theme : Triton.TextInput.Theme.Full,
                    value: Lia.p(boardContent, 'title')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "성명"});
            detailTable.appendValueColumn({content: Lia.pd('-', boardContent, 'title')});
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
        }
    },
    MAJOR: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '100px' },
                content: '전공'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'major');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {

            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "전공"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'major' },
                    theme : Triton.TextInput.Theme.Full,
                    value : Lia.p(boardContent,'properties', 'major')
                })
            });
        },

        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "전공"});
            detailTable.appendValueColumn({
                content: Lia.pd('-', boardContent, 'properties', 'major')
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['major'] = parameterMap['major'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    EMAIL: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '이메일'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'email');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "이메일"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'email' },
                    theme : Triton.TextInput.Theme.Full,
                    value : Lia.p(boardContent,'properties', 'email')
                })
            });
        },

        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "이메일"});
            detailTable.appendValueColumn({
                content: Lia.pd('-', boardContent, 'properties', 'email')
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['email'] = parameterMap['email'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATA1: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '학력사항'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'data1');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "학력사항"});
            detailTable.appendValueColumn({
                content: new Triton.TextArea({
                    form : { name : 'data1' },
                    value : Lia.p(boardContent,'properties', 'data1')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "학력사항"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'data1');
            data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['data1'] = parameterMap['data1'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATA2: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: {width: '240px'},
                content: '경력사항'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'data1');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "경력사항"});
            detailTable.appendValueColumn({
                content: new Triton.TextArea({
                    form: {name: 'data2'},
                    value : Lia.p(boardContent,'properties', 'data2')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "경력사항"});
            var data2 = Lia.pd('-', boardContent, 'properties', 'data2');
            data2 = Lia.nl2br(data2)
            detailTable.appendValueColumn({
                content: data2
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['data2'] = parameterMap['data2'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATA3: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: {width: '240px'},
                content: '학술활동'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'data3');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "학술활동"});
            detailTable.appendValueColumn({
                content: new Triton.TextArea({
                    form: {name: 'data3'},
                    value : Lia.p(boardContent,'properties', 'data3')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "학술활동"});
            var data3 = Lia.pd('-', boardContent, 'properties', 'data3');
            data3 = Lia.nl2br(data3)
            detailTable.appendValueColumn({
                content: Lia.pd('-', boardContent, 'properties', 'data3')
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['data3'] = parameterMap['data3'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATA4: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: {width: '240px'},
                content: '연구업적 링크'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'data4');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연구업적 링크"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form: {name: 'data4'},
                    theme: Triton.TextInput.Theme.Full,
                    value : Lia.p(boardContent,'properties', 'data4')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연구업적 링크"});
            var data3 = Lia.pd('-', boardContent, 'properties', 'data4');
            data3 = Lia.nl2br(data3)
            detailTable.appendValueColumn({
                content: Lia.pd('-', boardContent, 'properties', 'data4')
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['data4'] = parameterMap['data4'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATA5: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: {width: '240px'},
                content: '연락처'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'data4');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연락처"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form: {name: 'data5'},
                    theme: Triton.TextInput.Theme.Full,
                    value : Lia.p(boardContent,'properties', 'data5')
                })
            });
        },

        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연락처"});
            var data3 = Lia.pd('-', boardContent, 'properties', 'data5');
            data3 = Lia.nl2br(data3)
            detailTable.appendValueColumn({
                content: Lia.pd('-', boardContent, 'properties', 'data5')
            });
        },

        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['data5'] = parameterMap['data5'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    }
}

// 발전기금 명예의전당 입력란
var HonorData = {
    NAME: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '기부자명'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'title');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부자명"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'title' },
                    value: Lia.p(boardContent, 'title')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부자명"});
            detailTable.appendValueColumn({content: Lia.pd('-', boardContent, 'title')});
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
        }
    },
    AMOUNT: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '기부금액'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'amount');
            listTable.appendColumn({ content: '금 ' + Lia.numberToHangul(content) + ' 원' });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부금액"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'amount' },
                    attr: { type: 'number' },
                    value : Lia.p(boardContent,'properties', 'amount'),
                    onKeyUp: function(e) {
                        $('.text_amount').text(Lia.numberToHangul($(this).val()));
                    }
                })
            });

            detailTable.appendItem(new Triton.Span({
                content: '금',
                css: { 'margin-left': '15px', 'margin-right': '3px' }
            }));

            detailTable.appendItem(new Triton.Span({
                attr: { 'class': 'text_amount'},
                content: '-',
                css: { 'display': 'inline-block', 'margin-left': '5px', 'max-width': '300px', 'color': 'blue' }
            }));

            detailTable.appendItem(new Triton.Span({
                content: '원 정',
                css: { 'margin-left': '5px' }
            }));
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부금액"});
            var amount = Lia.pd('-', boardContent, 'properties', 'amount');
            amount = Lia.nl2br(amount)
            detailTable.appendValueColumn({
                content: amount + '원 (금 ' + Lia.numberToHangul(amount) + '원 정)'
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['amount'] = parameterMap['amount'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    DATE: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '기부일자'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'date');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부일자"});
            detailTable.appendValueColumn({
                content: new Triton.DatetimePicker({
                    type: Triton.DatetimePicker.TYPE_DATE,
                    form: {name: 'date'},
                    value: Lia.p(boardContent,'properties', 'date')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "기부일자"});
            var date = Lia.pd('-', boardContent, 'properties', 'date');
            date = Lia.nl2br(date)
            detailTable.appendValueColumn({
                content: date
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['date'] = parameterMap['date'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    }
}

// 발전기금 후원현황 : 교회 및 단체 후원현황
var FUNDSTATUS1 = {
    BASEYM: { // 기준연월
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '년/월'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var year = Lia.pd('-', contentSummary, 'properties', 'year');
            var month = Lia.pd('-', contentSummary, 'properties', 'month');
            listTable.appendColumn({ content: year + '/' + month });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});
            detailTable.appendValueColumn({
                content: ''
            });

            var date = new Date();
            var year = Lia.p(boardContent, 'year');
            var month = Lia.p(boardContent, 'month');

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'year' },
                attr: { 'type' : 'number', 'min' : '1900', 'max' : '2999' },
                css: { 'width': '80px' },
                value: (year == undefined) ? date.getFullYear() : year
            }));

            detailTable.appendItem(new Triton.Span({
                content: ' / ',
                css: { 'display': 'inline-block', 'margin': '0px 10px' }
            }));

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'month' },
                attr: { 'type' : 'number', 'min' : '1', 'max' : '12' },
                css: { 'width': '80px' },
                value: (month == undefined) ? date.getMonth() + 1 : month
            }));

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});

            var year = Lia.pd('-', boardContent, 'properties', 'year');
            var month = Lia.pd('-', boardContent, 'properties', 'month');

            detailTable.appendValueColumn({
                content: year + ' / ' + month
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['year'] = parameterMap['year'];
            properties['month'] = parameterMap['month'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    FUNDLIST: {
        attachHeaderToBoardList: function (listTable, boardList) {
            return undefined;
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            return undefined;
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "후원자목록", attr: { 'rowspan': 2 }});
            detailTable.appendValueColumn({
                content: '입력창에 후원자 교회/기관명을 입력하고, <b>엔터키(Enter)로 줄바꿈하면</b> ' +
                    '자동으로 목록에 추가됩니다.<br/>' +
                    '엑셀 복사/붙여넣기 (Ctrl + C / V) 시에도 자동으로 목록이 입력됩니다.'
            });
            detailTable.appendRow({});
            detailTable.appendValueColumn({
                content: '',
                attr: { 'colspan': '2' }
            });

            var splitedArr = undefined;

            var listTextArea = new Triton.TextArea({
                form : { name : 'body' },
                css: { 'width': '49%', 'min-height': '700px', 'display': 'inline-block', 'vertical-align': 'top' },
                value: Lia.pd('', boardContent, 'body'),
                onKeyUp: function(e) {

                    listRenderTable.empty();
                    listRenderTable.appendHeaderRow({});
                    listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
                    listRenderTable.appendHeaderColumn({ content: '교회/기관명' });

                    var jThis = $(this);
                    var text = jThis.val();

                    if(text != '') {
                        splitedArr = text.trim().split(/\n+/);
                    }

                    for(var idx in splitedArr) {
                        var name = splitedArr[idx];
                        listRenderTable.appendRow({});
                        listRenderTable.appendColumn({ content: Number(idx) + 1 });
                        listRenderTable.appendColumn({ content: name });
                    }
                }
            });

            var listRenderArea = new Triton.Panel({ css: { 'width': '49%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '2%' } });
            var listRenderTable = new Triton.ListTable({
                appendTo: listRenderArea
            });

            listRenderTable.appendHeaderRow({});
            listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
            listRenderTable.appendHeaderColumn({ content: '교회/기관명' });

            listRenderTable.appendRow({});
            listRenderTable.appendColumn({ content: '입력된 데이터가 없습니다.', css: { 'line-height': '100px' }, attr: { 'colspan': 2 } });

            var body = Lia.p(boardContent, 'body');
            if(body != undefined) {
                splitedArr = body.trim().split(/\n+/);
                listRenderTable.empty();
                listRenderTable.appendHeaderRow({});
                listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
                listRenderTable.appendHeaderColumn({ content: '교회/기관명' });
            }

            for(var idx in splitedArr) {

                var name = splitedArr[idx];
                listRenderTable.appendRow({});
                listRenderTable.appendColumn({ content: Number(idx) + 1 });
                listRenderTable.appendColumn({ content: name });
            }


            detailTable.appendItem(listTextArea);
            detailTable.appendItem(listRenderArea);

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "후원자목록"});

            var splitedArr = undefined;
            var body = Lia.p(boardContent, 'body');

            if(body != undefined && body != '') {
                splitedArr = body.trim().split(/\n+/);

            }


            detailTable.appendValueColumn({content: ''});

            var fundListArea = new Triton.Panel({});
            var listRenderTable = new Triton.ListTable({appendTo: fundListArea});

            listRenderTable.appendHeaderRow({});
            listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
            listRenderTable.appendHeaderColumn({ content: '교회/기관명' });

            for(var idx in splitedArr) {
                var name = splitedArr[idx];
                listRenderTable.appendRow({});
                listRenderTable.appendColumn({ content: Number(idx) + 1 });
                listRenderTable.appendColumn({ content: name });
            }

            detailTable.appendItem(fundListArea);


        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
        }
    }
}

// 발전기금 후원현황 : 개인후원약정현황
var FUNDSTATUS2 = {
    BASEYM: { // 기준연월
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '년/월'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var year = Lia.pd('-', contentSummary, 'properties', 'year');
            var month = Lia.pd('-', contentSummary, 'properties', 'month');
            listTable.appendColumn({ content: year + '/' + month });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});
            detailTable.appendValueColumn({
                content: ''
            });

            var date = new Date();
            var year = Lia.p(boardContent, 'year');
            var month = Lia.p(boardContent, 'month');

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'year' },
                attr: { 'type' : 'number', 'min' : '1900', 'max' : '2999' },
                css: { 'width': '80px' },
                value: (year == undefined) ? date.getFullYear() : year
            }));

            detailTable.appendItem(new Triton.Span({
                content: ' / ',
                css: { 'display': 'inline-block', 'margin': '0px 10px' }
            }));

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'month' },
                attr: { 'type' : 'number', 'min' : '1', 'max' : '12' },
                css: { 'width': '80px' },
                value: (month == undefined) ? date.getMonth() + 1 : month
            }));

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});

            var year = Lia.pd('-', boardContent, 'properties', 'year');
            var month = Lia.pd('-', boardContent, 'properties', 'month');

            detailTable.appendValueColumn({
                content: year + ' / ' + month
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['year'] = parameterMap['year'];
            properties['month'] = parameterMap['month'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    FUNDLIST: {
        attachHeaderToBoardList: function (listTable, boardList) {
            return undefined;
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            return undefined;
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "후원자목록", attr: { 'rowspan': 2 }});
            detailTable.appendValueColumn({
                content: '입력창에 후원자명을 입력하고, <b>엔터키(Enter)로 줄바꿈하면</b> ' +
                    '자동으로 목록에 추가됩니다.<br/>' +
                    '엑셀 복사/붙여넣기 (Ctrl + C / V) 시에도 자동으로 목록이 입력됩니다.'
            });
            detailTable.appendRow({});
            detailTable.appendValueColumn({
                content: '',
                attr: { 'colspan': '2' }
            });

            var splitedArr = undefined;

            var listTextArea = new Triton.TextArea({
                form : { name : 'body' },
                css: { 'width': '49%', 'min-height': '700px', 'display': 'inline-block', 'vertical-align': 'top' },
                value: Lia.pd('', boardContent, 'body'),
                onKeyUp: function(e) {

                    listRenderTable.empty();
                    listRenderTable.appendHeaderRow({});
                    listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
                    listRenderTable.appendHeaderColumn({ content: '후원자명' });

                    var jThis = $(this);
                    var text = jThis.val();

                    if(text != '') {
                        splitedArr = text.trim().split(/\n+/);
                    }

                    for(var idx in splitedArr) {
                        var name = splitedArr[idx];
                        listRenderTable.appendRow({});
                        listRenderTable.appendColumn({ content: Number(idx) + 1 });
                        listRenderTable.appendColumn({ content: name });
                    }
                }
            });

            var listRenderArea = new Triton.Panel({ css: { 'width': '49%', 'display': 'inline-block', 'vertical-align': 'top', 'margin-left': '2%' } });
            var listRenderTable = new Triton.ListTable({
                appendTo: listRenderArea
            });

            listRenderTable.appendHeaderRow({});
            listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
            listRenderTable.appendHeaderColumn({ content: '후원자명' });

            listRenderTable.appendRow({});
            listRenderTable.appendColumn({ content: '입력된 데이터가 없습니다.', css: { 'line-height': '100px' }, attr: { 'colspan': 2 } });

            var body = Lia.p(boardContent, 'body');
            if(body != undefined) {
                splitedArr = body.trim().split(/\n+/);
                listRenderTable.empty();
                listRenderTable.appendHeaderRow({});
                listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
                listRenderTable.appendHeaderColumn({ content: '후원자명' });
            }

            for(var idx in splitedArr) {

                var name = splitedArr[idx];
                listRenderTable.appendRow({});
                listRenderTable.appendColumn({ content: Number(idx) + 1 });
                listRenderTable.appendColumn({ content: name });
            }


            detailTable.appendItem(listTextArea);
            detailTable.appendItem(listRenderArea);

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "후원자명"});

            var splitedArr = undefined;
            var body = Lia.p(boardContent, 'body');

            if(body != undefined && body != '') {
                splitedArr = body.trim().split(/\n+/);

            }


            detailTable.appendValueColumn({content: ''});

            var fundListArea = new Triton.Panel({});
            var listRenderTable = new Triton.ListTable({appendTo: fundListArea});

            listRenderTable.appendHeaderRow({});
            listRenderTable.appendHeaderColumn({ content: '번호', css: { 'width': '80px' } });
            listRenderTable.appendHeaderColumn({ content: '후원자명' });

            for(var idx in splitedArr) {
                var name = splitedArr[idx];
                listRenderTable.appendRow({});
                listRenderTable.appendColumn({ content: Number(idx) + 1 });
                listRenderTable.appendColumn({ content: name });
            }

            detailTable.appendItem(fundListArea);


        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
        }
    }
}

// 발전기금 후원현황 : 월별후원금현황
var FUNDSTATUS3 = {
    BASEYM: { // 기준연월
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '년/월'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var year = Lia.pd('-', contentSummary, 'properties', 'year');
            var month = Lia.pd('-', contentSummary, 'properties', 'month');
            listTable.appendColumn({ content: year + '/' + month });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});
            detailTable.appendValueColumn({
                content: ''
            });

            var date = new Date();
            var year = Lia.p(boardContent, 'year');
            var month = Lia.p(boardContent, 'month');

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'year' },
                attr: { 'type' : 'number', 'min' : '1900', 'max' : '2999' },
                css: { 'width': '80px' },
                value: (year == undefined) ? date.getFullYear() : year
            }));

            detailTable.appendItem(new Triton.Span({
                content: ' / ',
                css: { 'display': 'inline-block', 'margin': '0px 10px' }
            }));

            detailTable.appendItem(new Triton.TextInput({
                form : { name : 'month' },
                attr: { 'type' : 'number', 'min' : '1', 'max' : '12' },
                css: { 'width': '80px' },
                value: (month == undefined) ? date.getMonth() + 1 : month
            }));

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "년/월"});

            var year = Lia.pd('-', boardContent, 'properties', 'year');
            var month = Lia.pd('-', boardContent, 'properties', 'month');

            detailTable.appendValueColumn({
                content: year + ' / ' + month
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['year'] = parameterMap['year'];
            properties['month'] = parameterMap['month'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    AMOUNT: { // 금액
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({content: '금액'});
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'title');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {

            Requester.awb(ApiUrl.Board.GET_BOARD_CONTENT_SUMMARY_LIST, {
                boardIdList : BoardId.CSFUND.STATUS3,
                isDeleted : 0,
                isAvailable : 1,
                parentBoardContentId : -1,
                page: 1,
                count: 1,
                includeBody : 1
            }, function(status, data){
                // var latestAccumulation = Lia.pd(0, data, 'body', 'list', 0, 'body');
                // latestAccumulation = Number(latestAccumulation);
                $('.value_title').on('change', function(e){
                    var jThis = $(this);
                    $('.amount_helper').text(Lia.numberToHangul(jThis.val()) + ' 원');
                });
            })

            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "금액"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'title' },
                    attr: { type: 'number', 'class': 'value_title' },
                    theme : Triton.TextInput.Theme.Full,
                    value: Lia.p(boardContent, 'title')
                })
            });

            detailTable.appendItem(new Triton.Span({
                attr: { 'class': 'triton_span triton_content amount_helper' },
                css: { 'display': 'block', 'margin-top': '5px' },
                content: ''
            }));
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "금액"});
            detailTable.appendValueColumn({content: Lia.pd('-', boardContent, 'title')});
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            parameterMap['title'] = $('.value_title').val();
        }
    },
    CUMULATED: { // 누계금액
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                content: '누계금액'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'body');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "누계금액"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'body' },
                    attr: { 'class': 'accum_amount' },
                    theme : Triton.TextInput.Theme.Full
                })
            });

            // detailTable.appendItem(new Triton.Span({
            //     attr: { 'class': 'triton_span triton_content accum_helper' },
            //     css: { 'display': 'block', 'margin-top': '5px' },
            //     content: '금액을 입력하고 Enter를 누르면 자동으로 계산됩니다.'
            // }));

        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "누계금액"});
            var cumulated = Lia.pd('-', boardContent, 'body');
            detailTable.appendValueColumn({content: cumulated});
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            parameterMap['body'] = $('.accum_amount').val();
        }
    }
}

var BOOK = {
    WRITER: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '글'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'writer');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "글"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'writer' },
                    value : Lia.p(boardContent,'properties', 'writer')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "글"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'writer');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['writer'] = parameterMap['writer'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    PUBLICATION_DATE: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '출간일'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'publication_date');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "출간일"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'publication_date' },
                    value : Lia.p(boardContent,'properties', 'publication_date')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "출간일"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'publication_date');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['publication_date'] = parameterMap['publication_date'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    PUBLICATION_COMPANY: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '출판사'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'publication_company');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "출판사"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'publication_company' },
                    value : Lia.p(boardContent,'properties', 'publication_company')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "출판사"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'publication_company');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['publication_company'] = parameterMap['publication_company'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    PACKAGE: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '판형'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'package');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "판형"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'package' },
                    value : Lia.p(boardContent,'properties', 'package')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "판형"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'package');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['package'] = parameterMap['package'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    FIELD: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '페이지'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'field');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "페이지"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'field' },
                    value : Lia.p(boardContent,'properties', 'field')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "페이지"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'field');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['field'] = parameterMap['field'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    PRICE: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '정가'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'price');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "정가"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'price' },
                    value : Lia.p(boardContent,'properties', 'price')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "정가"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'price');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['price'] = parameterMap['price'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    SUBSCRIPTION: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '연구독'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'subscription');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연구독"});
            detailTable.appendValueColumn({
                content: new Triton.TextInput({
                    form : { name : 'subscription' },
                    value : Lia.p(boardContent,'properties', 'subscription')
                })
            });
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "연구독"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'subscription');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['subscription'] = parameterMap['subscription'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    INTRODUCE: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '책소개'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'introduce');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            var textEditor;
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "책소개"});
            detailTable.appendValueColumn({
                content: textEditor = new Triton.TextEditor({
                    form : { name : 'introduce' },
                    value : Lia.p(boardContent,'properties', 'introduce')
                })
            });
            textEditor.initTextEditor();
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "책소개"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'introduce');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['introduce'] = parameterMap['introduce'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    REVIEW: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '목차'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'review');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            var textEditor;
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "목차"});
            detailTable.appendValueColumn({
                content: textEditor = new Triton.TextEditor({
                    form : { name : 'review' },
                    value : Lia.p(boardContent,'properties', 'review')
                })
            });
            textEditor.initTextEditor();
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "목차"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'review');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['review'] = parameterMap['review'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    LIST: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '저자소개'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'list');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            var textEditor;
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "저자소개"});
            detailTable.appendValueColumn({
                content: textEditor = new Triton.TextEditor({
                    form : { name : 'list' },
                    value : Lia.p(boardContent,'properties', 'list')
                })
            });
            textEditor.initTextEditor();
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "저자소개"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'list');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['list'] = parameterMap['list'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
    INTRODUCE_WRITER: {
        attachHeaderToBoardList: function (listTable, boardList) {
            listTable.appendHeaderColumn({
                css: { width: '240px' },
                content: '본문 중에서'
            });
        },
        attachToBoardList: function (listTable, contentSummary, data, boardList) {
            var content = Lia.pd('-', contentSummary, 'properties', 'introduce_writer');
            listTable.appendColumn({ content: content });
        },
        attachToBoardWrite: function (detailTable, boardContent, boardWrite) {
            var textEditor;
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "본문 중에서"});
            detailTable.appendValueColumn({
                content: textEditor = new Triton.TextEditor({
                    form : { name : 'introduce_writer' },
                    value : Lia.p(boardContent,'properties', 'introduce_writer')
                })
            });
            textEditor.initTextEditor();
        },
        attachToBoardDetail: function (detailTable, boardContent, boardDetail) {
            detailTable.appendRow({});
            detailTable.appendKeyColumn({content: "본문 중에서"});
            var data1 = Lia.pd('-', boardContent, 'properties', 'introduce_writer');
            // data1 = Lia.nl2br(data1)
            detailTable.appendValueColumn({
                content: data1
            });
        },
        attachToParameterMap: function (parameterMap, fieldObject, boardWrite) {
            var properties = {};

            if(parameterMap['properties'] != undefined) {
                properties = JSON.parse(parameterMap['properties']);
            }

            properties['introduce_writer'] = parameterMap['introduce_writer'];
            parameterMap['properties'] = JSON.stringify(properties);
        }
    },
}

ProjectSettings.Menu.onPageUrl = function( menu ) {

    var pageUrl = '/';

    var departmentIdx = Lia.p(menu, 'department_idx');
    if ( departmentIdx == 1 ) {
        return pageUrl;
    }

    var departmentId = Lia.p(menu, 'department_id');
    if ( String.isNotBlank(departmentId) ) {
        pageUrl = '/department/' + departmentId;
    }

    return pageUrl;
};



ProjectSettings.CustomMenuBoard.onBoardListBaseRequestParameterMap = function( map, menu ) {
    var menuId = Lia.p(menu, 'id');

    var isStatus3 = Lia.contains(menuId, MenuId.CSFUND.STATUS3);

    if(isStatus3) {
        map['includeBody'] = 1;
    }

    return map;
};

ProjectSettings.CustomMenuBoard.onBoardList = function( menu, boardList ) {

};

ProjectSettings.CustomMenuBoard.onBoardListFieldList = function( menu ) {

    var title = Lia.p(menu, 'title');
    var menuId = Lia.p(menu, 'id');
    var boardId = Lia.p(menu, 'content', 'data', 'id');

    // 학과 > 교수진 소개
    var isFaculty = title == "교수진소개" || title == "교수소개"
        || boardId == BoardId.HOME.FACULTY.PSEDU_ADONG
        || boardId == BoardId.HOME.FACULTY.PSEDU_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_EDUCATION
        || boardId == BoardId.HOME.FACULTY.PSEDU2_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_CHILD
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_COUNSELING;

    if(isFaculty) {
        return [
            Triton.Board.ValueType.ROW_NUMBER,
            FaciltyData.PROFNAME,
            FaciltyData.MAJOR,
            FaciltyData.EMAIL,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }


    // 발전기금 > 명예의전당
    var isHonor = Lia.contains(menuId, MenuId.CSFUND.HONOR1, MenuId.CSFUND.HONOR2, MenuId.CSFUND.HONOR3);

    if( isHonor ) {
        return [
            Triton.Board.ValueType.ROW_NUMBER,
            HonorData.NAME,
            HonorData.AMOUNT,
            HonorData.DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }


    // 발전기금 > 후원현황황 > 교회 및 단체 후원현황
    var isStatus1 = Lia.contains(menuId, MenuId.CSFUND.STATUS1);

    if( isStatus1 ) {

        return [
            Triton.Board.ValueType.ROW_NUMBER,
            // FUNDSTATUS1.BASEYM,
            Triton.Board.ValueType.TITLE,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황황 > 개인후원약정현황
    var isStatus2 = Lia.contains(menuId, MenuId.CSFUND.STATUS2);

    if( isStatus2 ) {

        return [
            Triton.Board.ValueType.ROW_NUMBER,
            FUNDSTATUS2.BASEYM,
            Triton.Board.ValueType.TITLE,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황황 > 월별후원금현황
    var isStatus3 = Lia.contains(menuId, MenuId.CSFUND.STATUS3);

    if( isStatus3 ) {

        return [
            Triton.Board.ValueType.ROW_NUMBER,
            FUNDSTATUS3.BASEYM,
            FUNDSTATUS3.AMOUNT,
            FUNDSTATUS3.CUMULATED,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    var isBook = Lia.contains(menuId, MenuId.BOOK1, MenuId.BOOK2, MenuId.BOOK3);

    if ( isBook ) {
        return [
            Triton.Board.ValueType.ROW_NUMBER,
            Triton.Board.ValueType.TITLE,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    return undefined;
};

ProjectSettings.CustomMenuBoard.onBoardListMode = function( menu ) {
    var title = Lia.p(menu, 'title');
    var menuId = Lia.p(menu, 'id');
    var boardId = Lia.p(menu, 'content', 'data', 'id');

    // 학과 > 교수진 소개
    var isFaculty = title == "교수진소개" || title == "교수소개"
        || boardId == BoardId.HOME.FACULTY.PSEDU_ADONG
        || boardId == BoardId.HOME.FACULTY.PSEDU_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_EDUCATION
        || boardId == BoardId.HOME.FACULTY.PSEDU2_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_CHILD
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_COUNSELING;
    if (isFaculty) {
        return Triton.BoardList.Mode.DISPLAY_ORDER;
    }
    // var isBook = Lia.contains(menuId, MenuId.BOOK1, MenuId.BOOK2, MenuId.BOOK3);
    //
    // if ( isBook ) {
    //     return Triton.BoardList.Mode.DISPLAY_ORDER;
    // }
};

ProjectSettings.CustomMenuBoard.onBoardDetail = function( menu, boardContent, boardDetail ) {
    return undefined;
};


ProjectSettings.CustomMenuBoard.onBoardDetailFieldList = function( menu, boardContent ) {
    var title = Lia.p(menu, 'title');
    var menuId = Lia.p(menu, 'id');
    var boardId = Lia.p(menu, 'content', 'data', 'id');

    var isFaculty = title == "교수진소개" || title == "교수소개"
        || boardId == BoardId.HOME.FACULTY.PSEDU_ADONG
        || boardId == BoardId.HOME.FACULTY.PSEDU_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_EDUCATION
        || boardId == BoardId.HOME.FACULTY.PSEDU2_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_CHILD
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_COUNSELING;

    if(isFaculty) {
        return [
            FaciltyData.PROFNAME,
            FaciltyData.MAJOR,
            FaciltyData.EMAIL,
            Triton.Board.ValueType.ATTACHMENT,
            FaciltyData.DATA1,
            FaciltyData.DATA2,
            FaciltyData.DATA3,
            FaciltyData.DATA4,
            FaciltyData.DATA5,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 명예의전당
    var isHonor = Lia.contains(menuId, MenuId.CSFUND.HONOR1, MenuId.CSFUND.HONOR2, MenuId.CSFUND.HONOR3);

    if( isHonor ) {
        return [
            HonorData.NAME,
            HonorData.AMOUNT,
            HonorData.DATE,
            Triton.Board.ValueType.ATTACHMENT,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황 > 교회 및 단체 후원현황
    var isStatus1 = Lia.contains(menuId, MenuId.CSFUND.STATUS1);

    if( isStatus1 ) {
        return [
            // FUNDSTATUS1.BASEYM,
            Triton.Board.ValueType.TITLE,
            FUNDSTATUS1.FUNDLIST,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황 > 개인후원약정현황
    var isStatus2 = Lia.contains(menuId, MenuId.CSFUND.STATUS2);

    if( isStatus2 ) {
        return [
            FUNDSTATUS2.BASEYM,
            Triton.Board.ValueType.TITLE,
            FUNDSTATUS2.FUNDLIST,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황황 > 월별후원금현황
    var isStatus3 = Lia.contains(menuId, MenuId.CSFUND.STATUS3);

    if( isStatus3 ) {

        return [
            FUNDSTATUS3.BASEYM,
            FUNDSTATUS3.AMOUNT,
            FUNDSTATUS3.CUMULATED,
            Triton.Board.ValueType.WRITER,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    var isBook = Lia.contains(menuId, MenuId.BOOK1, MenuId.BOOK2, MenuId.BOOK3);

    if ( isBook ) {
        return [
            Triton.Board.ValueType.TITLE,
            Triton.Board.ValueType.IMAGE_URL,
            BOOK.WRITER,
            BOOK.PUBLICATION_DATE,
            BOOK.PUBLICATION_COMPANY,
            BOOK.PACKAGE,
            BOOK.FIELD,
            BOOK.PRICE,
            BOOK.SUBSCRIPTION,
            BOOK.INTRODUCE,
            BOOK.REVIEW,
            BOOK.LIST,
            BOOK.INTRODUCE_WRITER,
            Triton.Board.ValueType.LINK,
            Triton.Board.ValueType.REGISTERED_DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    return undefined;
};

ProjectSettings.CustomMenuBoard.onBoardWrite = function( menu, boardContent, boardWrite ) {

};


ProjectSettings.CustomMenuBoard.onBoardWriteFieldList = function( menu, boardContent ) {
    var title = Lia.p(menu, 'title');
    var menuId = Lia.p(menu, 'id');
    var boardId = Lia.p(menu, 'content', 'data', 'id');

    var isFaculty = title == "교수진소개" || title == "교수소개"
        || boardId == BoardId.HOME.FACULTY.PSEDU_ADONG
        || boardId == BoardId.HOME.FACULTY.PSEDU_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_EDUCATION
        || boardId == BoardId.HOME.FACULTY.PSEDU2_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_CHILD
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_COUNSELING;

    if(isFaculty) {
        return [
            FaciltyData.PROFNAME,
            FaciltyData.MAJOR,
            FaciltyData.EMAIL,
            Triton.Board.ValueType.ATTACHMENT,
            FaciltyData.DATA1,
            FaciltyData.DATA2,
            FaciltyData.DATA3,
            FaciltyData.DATA4,
            FaciltyData.DATA5,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 명예의전당
    var isHonor = Lia.contains(menuId, MenuId.CSFUND.HONOR1, MenuId.CSFUND.HONOR2, MenuId.CSFUND.HONOR3);

    if( isHonor ) {
        return [
            HonorData.NAME,
            Triton.Board.ValueType.ATTACHMENT,
            HonorData.AMOUNT,
            HonorData.DATE,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황 > 교회 및 단체 후원현황
    var isStatus1 = Lia.contains(menuId, MenuId.CSFUND.STATUS1);

    if( isStatus1 ) {

        return [
            Triton.Board.ValueType.TITLE,
            // FUNDSTATUS1.BASEYM,
            FUNDSTATUS1.FUNDLIST,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황 > 개인후원약정현황
    var isStatus2 = Lia.contains(menuId, MenuId.CSFUND.STATUS2);

    if( isStatus2 ) {
        return [
            Triton.Board.ValueType.TITLE,
            FUNDSTATUS2.BASEYM,
            FUNDSTATUS2.FUNDLIST,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    // 발전기금 > 후원현황황 > 월별후원금현황
    var isStatus3 = Lia.contains(menuId, MenuId.CSFUND.STATUS3);

    if( isStatus3 ) {

        return [
            FUNDSTATUS3.BASEYM,
            FUNDSTATUS3.AMOUNT,
            FUNDSTATUS3.CUMULATED,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    var isBook = Lia.contains(menuId, MenuId.BOOK1, MenuId.BOOK2, MenuId.BOOK3);

    if ( isBook ) {
        return [
            Triton.Board.ValueType.TITLE,
            Triton.Board.ValueType.IMAGE_URL,
            BOOK.WRITER,
            BOOK.PUBLICATION_DATE,
            BOOK.PUBLICATION_COMPANY,
            BOOK.PACKAGE,
            BOOK.FIELD,
            BOOK.PRICE,
            BOOK.SUBSCRIPTION,
            BOOK.INTRODUCE,
            BOOK.REVIEW,
            BOOK.LIST,
            BOOK.INTRODUCE_WRITER,
            Triton.Board.ValueType.LINK,
            Triton.Board.ValueType.IS_AVAILABLE
        ]
    }

    return undefined;

};


ProjectSettings.CustomMenuBoard.onBoardWriteSaved = function( menu, boardWrite, parameterMap, data ) {
    var title = Lia.p(menu, 'title');
    var menuId = Lia.p(menu, 'id');
    var boardId = Lia.p(menu, 'content', 'data', 'id');

    var isFaculty = title == "교수진소개" || title == "교수소개"
        || boardId == BoardId.HOME.FACULTY.PSEDU_ADONG
        || boardId == BoardId.HOME.FACULTY.PSEDU_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_EDUCATION
        || boardId == BoardId.HOME.FACULTY.PSEDU2_COUNSELING
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_CHILD
        || boardId == BoardId.HOME.FACULTY.PSEDU2_GRADUATE_COUNSELING;

    if(isFaculty) {

        parameterMap['properties'] = JSON.stringify({
            major: parameterMap['major'],
            email: parameterMap['email'],
            profile_img: parameterMap['attachmentList'],
            data1: parameterMap['data1'],
            data2: parameterMap['data2'],
            data3: parameterMap['data3'],
            data4: parameterMap['data4'],
            data5: parameterMap['data5']
        });

    }

    return true;
};

ProjectSettings.CustomMenuBoard.onMenuBoardParameterMap = function( menuId, parentMenuId ) {
    return {
        'm1' : 'normal/board'
    };
};

ProjectSettings.CustomMenuBoard.onMenuUrl = function( menu) {
    return '/';
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
