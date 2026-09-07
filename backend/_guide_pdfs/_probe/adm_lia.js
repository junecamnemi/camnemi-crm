/*
    version '1.9.56.RELEASE'

    z-index 관련 설정
        popup : 10000 부터 시작
        컴포넌트 내 popup : 100 부터 시작
 */

var Lia = {

    KeyCode: {

        ENTER: 13,
        ESCAPE: 27,
        DEL: 46,

        LEFT: 37,
        TOP: 38,
        RIGHT: 39,
        BOTTOM: 40
    },

    MouseCode: {

        LEFT: 1,
        MIDDLE: 2,
        RIGHT: 3

    },

    UriConversionType: {

        ENCODE_DECODE_URI_COMPONENT: 0,
        ENCODE_DECODE_URI: 1,
        ESCAPE_UNESCAPE: 2,

        DEFAULT: 0
    },

    Component: {

        Name: {

            BUTTON: 'button',
            FORM_ELEMENT: 'form_element',
            PIE: 'pie',
            IMAGE_BUTTON: 'image_button',
            IMAGE_BUTTON_CONTAINER: 'image_button_container',
            IMAGE_BOX: 'image_box',
            FLAT_BUTTON: 'flat_button',
            IMAGE_SELECT: 'image_select',
            IMAGE_SELECT_LIST: 'image_select_list',
            RESIZE: 'resize',
            DIM: 'dim',
            POPUP: 'popup',
            DIV_PLACEHOLDER_INPUT: 'div_placeholder_input',
            TEXT_PLACEHOLDER_INPUT: 'text_placeholder_input',
            IMAGE_INPUT: 'image_input',
            LOADING_INDICATOR: 'loading_indicator',
            LANG: 'lang',
            TEXT_EDITOR: 'text_editor',
            PDF_VIEWER: 'pdf_viewer',
            OFFICE_VIEWER: 'office_viewer',
            CODE_EDITOR: 'code_editor',
            PAGER: 'pager',
            COMBO_BOX: 'combo_box',

            SORTABLE: 'sortable',
            SORTABLE_ITEM: 'sortable_item',
            SORTABLE_MOVER: 'sortable_mover',

            FILE_UPLOADER: 'file_uploader',
            FILE_UPLOADER_LIST: 'file_uploader_list',
            IMAGE_COVER: 'image_cover'
        },

        Flag: {

            HOVER: 'hover',
            PRESS: 'press',
            NO_CHANGE: 'no_change',
            NO_BIND: 'no_bind',
            NO_DIM: 'no_dim',
            PRESSED: 'pressed',
            PRESSING: 'pressing',
            HOVERING: 'hovering',

            NO_CONTAIN: 'no_contain',
            NO_RESIZE: 'no_resize',
            NO_ADJUST: 'no_adjust',
            HIDDEN_OVERFLOW: 'hidden_overflow',
            ALIGN_LEFT: 'align_left',
            ALIGN_RIGHT: 'align_right',
            ALIGN_CENTER: 'align_center',
            SHOWING: 'showing',
            PASSWORD: 'password',
            TEXTAREA: 'textarea',
            PLACEHOLDER: 'placeholder',
            WITHOUT_ANIMATING: 'without_animating',
            JUT: 'jut',
            RADIO: 'radio',
            CHECK: 'check',
            DISABLED: 'disabled',
            CANCELABLE: 'cancelable',
            PLAYING: 'playing',
            LOADING: 'loading',
            MOVABLE: 'movable',
            MOVING: 'moving',

            INITED: 'inited',

            IMAGE_ERROR: 'image_error',

            IMAGE_BUTTON_INITED: 'image_button_inited',
            IMAGE_BUTTON_CONTAINER_INITED: 'image_button_container_inited',

            IMAGE_BOX_INITED: 'image_box_inited',
            FLAT_BUTTON_INITED: 'flat_button_inited',

            LOADING_INITED: 'loading_inited',
            JUT_INITED: 'jut_inited',
            CHECK_INITED: 'check_inited',
            RADIO_INITED: 'radio_inited'
        },

        AttrName: {

            SRC: 'lia-src',
            ERROR_SRC: 'lia-error-src',

            SELECTOR: 'lia-selector',
            DEFAULT_BACKGROUND_COLOR: 'lia-background-color',
            HOVERING_BACKGROUND_COLOR: 'lia-hovering-background-color',
            PRESSED_BACKGROUND_COLOR: 'lia-pressed-background-color',
            DEFAULT_TEXT_COLOR: 'lia-text-color',
            HOVERING_TEXT_COLOR: 'lia-hovering-text-color',
            PRESSED_TEXT_COLOR: 'lia-pressed-text-color',
            ROUND_WIDTH: 'lia-round-width',
            DIRECTION: 'lia-direction',
            SHADOW_WIDTH: 'lia-shadow-width',
            POSTFIX: 'lia-postfix',

            PADDING: 'lia-padding',
            PADDING_LEFT: 'lia-padding-left',
            PADDING_RIGHT: 'lia-padding-right',
            PADDING_TOP: 'lia-padding-top',
            PADDING_BOTTOM: 'lia-padding-bottom',
            PADDING_VERTICAL: 'lia-padding-vertical',
            PADDING_HORIZONTAL: 'lia-padding-horizontal',

            MARGIN: 'lia-margin',
            MARGIN_LEFT: 'lia-margin-left',
            MARGIN_RIGHT: 'lia-margin-right',
            MARGIN_TOP: 'lia-margin-top',
            MARGIN_BOTTOM: 'lia-margin-bottom',
            MARGIN_VERTICAL: 'lia-margin-vertical',
            MARGIN_HORIZONTAL: 'lia-margin-horizontal',

            TEXT_COLOR: 'lia-text-color',

            WIDTH: 'lia-width',
            HEIGHT: 'lia-height',
            TOP: 'lia-top',
            LEFT: 'lia-left',
            RIGHT: 'lia-right',
            BOTTOM: 'lia-bottom',

            FONT_SIZE: 'lia-font-size',
            LINE_HEIGHT: 'lia-line-height',

            BORDER_WIDTH: 'lia-border-width',
            BORDER_TOP_WIDTH: 'lia-border-top-width',
            BORDER_BOTTOM_WIDTH: 'lia-border-bottom-width',
            BORDER_LEFT_WIDTH: 'lia-border-left-width',
            BORDER_RIGHT_WIDTH: 'lia-border-right-width',

            BORDER_RADIUS: 'lia-border-radius',
            BACKGROUND_SIZE: 'lia-background-size',
            MIN_HEIGHT: 'lia-min-height',

            JUT_DEFAULT_BACKGROUND_COLOR: 'lia-jut-background-color',
            JUT_HOVERING_BACKGROUND_COLOR: 'lia-jut-hovering-background-color',
            JUT_PRESSED_BACKGROUND_COLOR: 'lia-jut-pressed-background-color',

            HOVER_COLOR: 'lia-hover-color',
            ROW_HEIGHT: 'lia-row-height',

            FONT_FAMILY: 'lia-font-family',
            FONT_WEIGHT: 'lia-font-weight',

            PLACEHOLDER: 'lia-placeholder',
            PLACEHOLDER_TEXT_COLOR: 'lia-placeholder-text-color',
            PLACEHOLDER_FONT_WEIGHT: 'lia-placeholder-font-weight',
            PLACEHOLDER_FONT_FAMILY: 'lia-placeholder-font-family',
            PLACEHOLDER_FONT_SIZE: 'lia-placeholder-font-size',

            Z_INDEX: 'lia-z-index',

            NAME: 'lia-name',
            VALUE: 'lia-value',
            CHECK: 'lia-check',
            TYPE: 'lia-type',

            GROUP: 'lia-group',
            OPACITY: 'lia-opacity',

            BACKGROUND_IMAGE: 'lia-background-image',
            BACKGROUND_COLOR: 'lia-background-color',

            DIM_BACKGROUND_COLOR: 'lia-dim-background-color',

            DIM: 'lia-dim',
            POPUP: 'lia-popup',

            INDEX: 'lia-index',
            START_INDEX: 'lia-start-index',
            END_INDEX: 'lia-end-index',

            INDEX_FORMAT: 'lia-index-format',
            POSITION_TOP: 'lia-position-top',
            POSITION_LEFT: 'lia-position-left',

            REFER_COUNT: 'lia-refer-count',

            KEY: 'lia-key',
            ATTR: 'lia-attr',
            CSS: 'lia-css',

            POSITION: 'lia-position'
        },

        Event: {

            SELECTED: 'lia:selected',
            STATUS_CHANGED: 'lia:statuschanged',
            SHOW: 'lia:show',
            HIDE: 'lia:hide'
        },

        Value: {

            Button: {

                SRC_DEFAULT_POSTFIX: '.png',
                SRC_PRESSED_POSTFIX: '_pressed.png',
                SRC_HOVERING_POSTFIX: '_hovering.png',

                Status: {

                    DEFAULT: 'default',
                    HOVERING: 'hovering',
                    PRESSING: 'pressing',
                    PRESSED: 'pressed'
                },

                ImageBox: {

                    DEFAULT_INDEX: 0,
                    PRESSED_INDEX: 1,
                    HOVERING_INDEX: 2,

                    IMAGE_BOX_INDEX: 'image-box-index'
                },

                FlatButton: {

                    DEFAULT_SHADOW_WIDTH: '7px',
                    DEFAULT_ROUND_WIDTH: '10px'

                }

            },

            LoadingIndicator: {

                TIMER_DURATION: 100,
                DEFAULT_START_INDEX: 1,
                REPLACE_INDEX_WORD: '{index}'
            },

            FormSerializer: {

                Boolean: {

                    TRUE: 1,
                    FALSE: 0
                }
            },

            ImagePlaceholderInput: {

                REPLACEMENT_POSTFIX: '.png',

                DEFAULT_POSTFIX: 'placeholder',
                DEFAULT_HORIZONTAL_PADDING: '10px',
                DEFAULT_VERTICAL_PADDING: '0px',
                DEFAULT_TEXT_COLOR: '#000000'
            },

            ImageSelect: {

                NAME: 'name',
                VALUE: 'value',
                INDEX: 'index',

                SELECT: 'image_select',
                LIST: 'list',
                LIST_ARRAY: 'image-select-list-array',
                DEFAULT_LIST_ROW_HEIGHT: '20px',
                LIST_FADE_DURATION: 300
            },

            Popup: {

                DEFAULT_Z_INDEX: 10000,
                DEFAULT_DIM_BACKGROUND_COLOR: '#000000',
                DEFAULT_DIM_OPACITY: 0.7,
                FADE_DURATION: 300,

                Position: {

                    FIXED: 'fixed',
                    ABSOLUTE: 'absolute'
                },
                DEFAULT_POSITION: 'fixed',

                NEXT_POPUP: '{next-popup}',
                PREV_DIM: '{prev-dim}'

            },

            FormUpload: {

                NAME: 'name',
                PATH: 'path',
                FORM: 'form',
                TAG: 'tag',
                RESPONSE: 'response',

                DEFAULT_PATH_NODE_NAME: 'path'
            },

            TextPlaceholderInput: {

                DEFAULT_PADDING: '0px',
                APPEND_TEXT: '   '
            },

            Resize: {

                DEFAULT_BASE_WIDTH: 640,
                DEFAULT_BASE_HEIGHT: 960
            },

            FileUploader: {

                ATTACHMENT : 'file-uploader-attachment',

                VIEWS_FILE_CONTENT : 'file-uploader-views-file-content',

                OPENS_WITHOUT_VIEWER : 'file-uploader-opens-without-viewer',

                ATTACHMENT_HTML : 'file-uploader-attachment-html',

                ATTACHMENT_DELETE_BUTTON_HTML : 'file-uploader-attachment-delete-button-html',

                DEFAULT_OPENS_WITHOUT_VIEWER: false,

                DEFAULT_HTML: '<div style="overflow:hidden;position:relative;background-color:#003e74;color:#ffffff;width:110px;height:40px;line-height:40px;font-size:14px;">' +
                    '<div style="height:40px;line-height:40px;text-align: center;">파일 추가</div>' +
                    '<div style="position:absolute;left:0;top:0;"><form method="post" enctype="multipart/form-data"><input type="file" name="file" style="font-size:999px;opacity:0;filter: alpha(opacity=0);" /></form></div>' +
                    '</div>' +
                    '<div class="file_uploader_list">' +
                    '</div>',
                DEFAULT_ATTACHMENT_HTML: '<div class="file_uploader_item" style="list-style: none;margin-top:10px;clear:both;cursor:pointer;"><img src="/res/service/img/common/img_file.png" >' +
                    '<span class="file_uploader_item_name" style="margin-left:10px;margin-right:10px;"></span></div>',

                DEFAULT_ATTACHMENT_FILE_VIEW_HTML: '<div class="file_uploader_item_file_view"></div>',

                DEFAULT_ATTACHMENT_DELETE_BUTTON_HTML: '<img class="file_uploader_item_delete_button" src="/res/service/img/common/img_filedelete.png" />',
                DEFAULT_ATTACHMENT_HANDLER: function (attachment, options) {

                    var unuseDeleteButton = Lia.p(options,'unuseDeleteButton');
                    var viewsFileContent = Lia.p(options,'viewsFileContent');
                    var opensWithoutViewer = Lia.p(options,'opensWithoutViewer');

                    var jAttachment = $(Lia.pd(jQuery.liaFileUploaderAttachmentHtml, options, 'attachmentHtml'));
                    if (!unuseDeleteButton) {
                        var attachmentDeleteButtonHtml = Lia.pd(jQuery.liaFileUploaderAttachmentDeleteButtonHtml, options, 'attachmentDeleteButtonHtml');
                        jAttachment.append(attachmentDeleteButtonHtml);
                    }

                    jAttachment.find('.file_uploader_item_name').text(Lia.p(attachment, 'original_filename'));

                    jAttachment.on('click', {
                        opensWithoutViewer : opensWithoutViewer
                    }, function (e) {

                        var opensWithoutViewer = e.data.opensWithoutViewer;

                        var attachment = $(this).data(Lia.Component.Value.FileUploader.ATTACHMENT);
                        var url = attachment['url'];
                        var originalFileName = attachment['original_filename'];


                        if ( opensWithoutViewer == true  ) {

                            var openUrl = PathHelper.getFileUrl(url, originalFileName);
                            Lia.open(openUrl);

                        } else {
                            PathHelper.open(url, originalFileName);
                        }


                    });

                    if( viewsFileContent ) {

                        // 특정 확장자만 파일 viewing 하도록 설정된다.
                        var url = attachment['url'];
                        var size = attachment['size'];
                        var extension = FileHelper.extractFileExtOnly(url);
                        if ( String.isNotBlank(extension) ) {

                            if ( FileHelper.isImageFile(url)) {

                                // 이미지 파일일 경우 이미지로 보여줌
                                var jAttachmentFileView = $(jQuery.liaFileUploaderAttachmentFileViewHtml);
                                jAttachment.append(jAttachmentFileView);

                                var jImage = jQuery('<img />');
                                jAttachmentFileView.append(jImage);

                                jImage.attr({
                                    src: PathHelper.getFileUrl(url)
                                });
                                jImage.css({
                                    'margin-top' :'5px',
                                    'display': ' block',
                                    'cursor': 'pointer',
                                    'max-width': '100%'
                                });
                                jImage.on('click', function() {
                                    AjaxPopupHelper.image($(this).attr('src'));
                                });

                            } else if ( FileHelper.isPdfFile(url) ) {

                                var jAttachmentFileView = $(jQuery.liaFileUploaderAttachmentFileViewHtml);
                                jAttachment.append(jAttachmentFileView);

                                var jViewer = $('<div class="pdf_viewer" style="width:100%;height:600px;margin-top:5px;"></div>');
                                jAttachmentFileView.append(jViewer);

                                jViewer.css({'margin': '0 auto'});
                                jViewer.initPdfViewer({
                                    src: PathHelper.getFileUrl(url)
                                });


                            } else if ( FileHelper.isOfficeFile(url) ) {

                                var sizeInMB = (size / 1024) / 1024;
                                if ( sizeInMB <= 25 ) {

                                    var jAttachmentFileView = $(jQuery.liaFileUploaderAttachmentFileViewHtml);
                                    jAttachment.append(jAttachmentFileView);

                                    var jViewer = $('<div class="office_viewer" style="width:100%;height:600px;margin-top:5px;"></div>');
                                    jViewer.css({'margin': '0 auto'});
                                    jViewer.initOfficeViewer({
                                        src: PathHelper.getFileUrl(url)
                                    });
                                    jAttachmentFileView.append(jViewer);
                                }
                            }
                        }
                    }

                    return jAttachment;
                },

            },

            Requester: {

                DefaultRequestValue: {

                    DEFAULT_TIMEOUT: undefined,
                    DEFAULT_TIMEOUT_WITH_SUBMIT: undefined,
                    DEFAULT_SYNC: false,
                    DEFAULT_DATA_TYPE: 'json',
                    DEFAULT_Q: true,
                    DEFAULT_CACHE: false,
                    DEFAULT_METHOD: 'post',
                    DEFAULT_NO_EXECUTE_ON_RESPONSE_WHEN_ERROR: false,
                    DEFAULT_XHR_FIELDS: {}
                },

                Status: {

                    SUCCESS: true,
                    ERROR: false
                },

                XhrStatus: {

                    ABORT: 'abort',
                    TIMEOUT: 'timeout'
                },

                HttpStatus: {

                    ERROR: 0,
                    ABORT: -1,
                    TIMEOUT: -2,
                    BAD_REQUEST: 400,
                    NOT_FOUND: 404,
                    INTERNAL_SERVER_ERROR: 500,
                    NOT_IMPLEMENTED: 501,
                    BAD_GATEWAY: 502,
                    SERVICE_UNAVAILABLE: 503,
                    GATEWAY_TIMEOUT: 504
                },


                Type: {

                    REQUEST: 1,
                    EXECUTE: 2
                }
            },


            CodeEditor: {

                Url: {

                    MONACO_EDITOR: '/res/lia/embed/monacoeditor.html',
                    ACE_EDITOR: '/res/lia/embed/aceeditor.html'
                },

                Type: {

                    ACE_EDITOR: 1,
                    MONACO_EDITOR: 2,

                    RECOMMEND: 0
                }

            }
        }
    },


    isMobile: undefined,
    ieVersion: undefined,

    debugMode: false,
    isDebugMode: function () {
        return Lia.debugMode;
    },

    setDebugMode: function (mode) {
        Lia.debugMode = mode;
    },

    logMode: false,
    isLogMode: function () {
        return Lia.logMode;
    },

    setLogMode: function (mode) {
        Lia.logMode = mode;
    },

    // 로그 함수
    log : function() {

        if ( Lia.logMode != true ) {
            return;
        }

        console.log.apply(this, arguments);
    },

    /**
     * 초기화
     */
    init: function () {
    },

    /**
     * 모바일 환경인지 체크
     *
     * @returns {boolean}
     */
    checkMobile: function () {

        var ua = navigator.userAgent;
        var mobileKeyWords = ['iPhone', 'iPod', 'iPad', 'BlackBerry', 'Android', 'Windows CE'];
        for (var i = 0, l = mobileKeyWords.length; i < l; i++) {
            if (ua.match(mobileKeyWords[i]) != null)
                return true;
        }

        return false;
    },

    /**
     * 리스트 키를 맵 형태로 만듬
     *
     * @returns {boolean}
     */
    convertListToMap: function (list, key) {

        var map = {};
        if (list != undefined) {

            for (var listKey in list) {
                var item = list[listKey];
                map[item[key]] = item;
            }
        }

        return map;
    },

    /**
     * 맵을 리스트 맵 리스트 안으로 만듬
     *
     * @returns {boolean}
     */
    convertListToListMap: function (list, key) {

        var map = {};

        if (list != undefined) {

            for (var listKey in list) {

                var item = list[listKey];

                var itemKey = item[key];
                if (map[itemKey] == undefined)
                    map[itemKey] = [];

                map[itemKey].push(item);
            }
        }

        return map;
    },

    /**
     * 일렬의 리스트를 구조화된 리스트로 만들어주기 ( parent_id 보고 child_list 생성 )
     *
     * @returns []
     */
    convertListForChildList: function (list, key, parentKey, childListKey) {

        key = Lia.pcd('id', key);
        parentKey = Lia.pcd('parent_id', parentKey);
        childListKey = Lia.pcd('child_list', childListKey);

        var newList = [];

        if (Array.isNotEmpty(list)) {

            var map = Lia.convertListToMap(list, key);

            for (var i = 0, l = list.length; i < l; i++) {

                var item = list[i];

                var parentId = Lia.p(item, parentKey);

                if (parentId == undefined) {
                    newList.push(item);
                } else {

                    var mapItem = map[parentId];
                    if (mapItem != undefined) {

                        var childList = mapItem[childListKey];
                        if (childList == undefined) {
                            mapItem[childListKey] = childList = [];
                        }

                        childList.push(item);
                    }
                }
            }
        }

        return newList;
    },


    /**
     * 아이폰, 아이패드, 아이팟인지 체크
     *
     * @returns {boolean}
     */
    checkiPhoneSeries: function () {

        var ua = navigator.userAgent;
        var iphoneKeyWords = ['iPhone', 'iPod', 'iPad'];
        for (var i = 0, l = iphoneKeyWords.length; i < l; i++) {
            if (ua.match(iphoneKeyWords[i]) != null)
                return true;
        }

        return false;
    },

    /**
     * 안드로이드 인지 체크
     *
     * @returns {boolean}
     */
    checkAndroid: function () {

        return navigator.userAgent.indexOf('Android') > -1;
    },

    /**
     * 인터넷 익스플로러 버전 체크
     * 익스가 아니라면 -1 리턴
     *
     * @returns {number}
     */
    checkInternetExplorerVersion: function () {

        var version = -1;
        var ua = navigator.userAgent;
        if (ua.indexOf('MSIE') != -1) {
            var regexp = new RegExp('MSIE ([0-9]{1,}[\.0-9]{0,})');
            if (regexp.exec(ua) != null)
                version = parseFloat(RegExp.$1);
        } else if (ua.indexOf('Trident') != -1) {
            version = 11;
        }

        return version;
    },

    /**
     * 크롬인지 체크
     *
     * @returns {boolean}
     */
    checkChrome: function () {

        return navigator.userAgent.indexOf('Chrome') > -1;
    },

    /**
     * 사파리인지 체크
     *
     * @returns {boolean}
     */
    checkSafari: function () {

        var ua = navigator.userAgent;
        return (ua.indexOf('Safari') != -1 && navigator.userAgent.indexOf('Chrome') == -1);
    },

    /**
     * 파이어폭스인지 체크
     *
     * @returns {boolean}
     */
    checkFirefox: function () {

        return navigator.userAgent.indexOf('Firefox') > -1;
    },

    /**
     * 오페라인지 체크
     * @returns {boolean}
     */
    checkOpera: function () {

        return navigator.userAgent.indexOf('Presto') > -1;
    },

    /**
     * 타임스켐프 얻음
     */
    getTimestamp: function () {

        return new Date().getTime();
    },

    /**
     * 폼을 생성하여 페이지 이동
     *
     * @param method
     * @param url
     * @param parameterMap
     */
    redirectForm: function (method, url, parameterMap) {

        var jForm = $('<form method="' + method + '" action="' + url + '" style="width:0px;height:0px;"></form>');
        jQuery('body').append(jForm);

        if (parameterMap != undefined) {
            for (var key in parameterMap) {

                var jInput = jQuery('<input type="hidden" />');
                jInput.attr({'name': key, 'value': parameterMap[key]});
                jForm.append(jInput);
            }
        }

        jForm.submit();
    },

    /**
     * POST로 페이지 이동
     *
     * @param url
     * @param parameter
     */
    redirectPost: function (url, parameter) {

        Lia.redirectForm('post', url, parameter);
    },

    /**
     * GET으로 페이지 이동
     *
     * @param url
     * @param parameter
     */
    redirectGet: function (url, parameter) {

        Lia.redirectForm('get', url, parameter);
    },

    /**
     * URL방식으로 페이지 이동
     *
     * @param url
     * @param parameter
     */
    redirect: function (url, parameterMap, uriConversionType) {

        var addingMark = (url.indexOf('?') >= 0) ? '&' : '?';
        window.location.href = url + Lia.convertArrayToQueryString(parameterMap, uriConversionType, addingMark);
    },

    open: function (url, parameterMap, options, uriConversionType) {

        var addingMark = (url.indexOf('?') >= 0) ? '&' : '?';

        var optionString = '';

        if (options != undefined) {

            for (var key in options) {

                var value = options[key];

                if (String.isNotBlank(optionString)) {
                    optionString += ',';
                }

                optionString += key + '=' + value;
            }
        }


        window.open(url + Lia.convertArrayToQueryString(parameterMap, uriConversionType, addingMark), '', optionString);
    },


    postWindowIdx : 0,

    openPost : function (url, parameterMap, options) {

        var optionString = '';

        if (options != undefined) {

            for (var key in options) {

                var value = options[key];

                if (String.isNotBlank(optionString)) {
                    optionString += ',';
                }

                optionString += key + '=' + value;
            }
        }

        var name = "post_window_id_" + Lia.getTimestamp() + Lia.postWindowIdx++;

        var jForm = $('<form target="'+name+'" name="'+name+'" method="' + 'POST' + '" action="' + url + '" style="width:0px;height:0px;"></form>');

        if (parameterMap != undefined) {
            for (var key in parameterMap) {

                var jInput = jQuery('<input type="hidden" />');
                jInput.attr({'name': key, 'value': parameterMap[key]});
                jForm.append(jInput);
            }
        }

        jQuery('body').append(jForm);

        window.open('', name, optionString);

        jForm.submit();
    },


    /**
     * 페이지 새로고침
     */
    refresh: function (forceget) {

        if (forceget == undefined)
            forceget = true;

        window.location.reload(forceget);
    },

    /**
     * 배열을 쿼리 스트링으로 변환
     *
     * @param array
     * @returns {string}
     */
    convertArrayToQueryString: function (array, uriConversionType, addingMark) {

        if (addingMark == undefined)
            addingMark = '?';

        var queryString = '';
        if (array != undefined) {
            for (var key in array) {
                if (queryString != '')
                    queryString += '&';

                queryString += key + '=' + Lia.encodeUri(array[key], uriConversionType);
            }

            if (addingMark != '' && queryString != '')
                queryString = addingMark + queryString;
        }
        return queryString;
    },

    /**
     * 객체 deep copy
     *
     * @param object
     * @returns {*}
     */
    deepCopy: function (object) {

        if (typeof object == "object") {

            var map = {};
            for (var key in object) {
                map[key] = object[key];
            }

            object = map;
        }

        return object;
    },

    /**
     * 객체의 내용 복사
     *
     * @param toObject
     * @param fromObject
     * @returns {*}
     */
    combine: function (toObject, fromObject) {

        for (var key in fromObject) {

            toObject[key] = fromObject[key];
        }

        return toObject;

    },

    /**
     * uri 인코딩
     * @param text
     * @param type
     * @returns {*}
     */
    encodeUri: function (text, type) {

        if (type == undefined)
            type = Lia.UriConversionType.DEFAULT;

        if (type == Lia.UriConversionType.ENCODE_DECODE_URI)
            return encodeURI(text);
        else if (type == Lia.UriConversionType.ESCAPE_UNESCAPE)
            return escape(text);

        return encodeURIComponent(text);
    },

    /**
     * uri 디코딩
     * @param text
     * @param type
     * @returns {*}
     */
    decodeUri: function (text, type) {

        if (type == undefined)
            type = Lia.UriConversionType.DEFAULT;

        if (type == Lia.UriConversionType.ENCODE_DECODE_URI)
            return decodeURI(text);
        else if (type == Lia.UriConversionType.ESCAPE_UNESCAPE)
            return unescape(text);

        return decodeURIComponent(text);
    },

    /**
     * uri 디코딩 ( try - catch )
     *
     * @param text
     * @param type
     * @returns {*}
     */
    decodeUriSafety: function (text, type) {

        try {
            return Lia.decodeUri(text, type);
        } catch (e) {
            return text;
        }
    },

    /**
     * 주소창에 있는 Get을 통하여 들오언 파라미터 추출
     *
     * @returns {{}}
     */
    extractGetParameterMap: function (uriConversionType) {

        return Lia.convertQueryStringToArray(window.location.search.substring(1), uriConversionType);
    },


    /**
     * URL을 기준으로 들어온 파라미터 추출
     *
     * @returns {{}}
     */
    extractGetParameterMapFromUrl: function (url, uriConversionType) {

        var idx = url.lastIndexOf('?');
        return Lia.convertQueryStringToArray(idx == -1 ? undefined : url.substring(idx + 1), uriConversionType);
    },


    /**
     * 기본 URL 추출
     *  https://abcde.com:12345/page/lms -> https://abcde.com:12345/
     */
    extractBaseUrl: function () {

        var jLocation = jQuery(location);
        return jLocation.attr('protocol') + '//' + jLocation.attr('host');
    },


    /**
     *  QueryString Javasscript 객체로 변환
     *
     * @returns {{}}
     */
    convertQueryStringToArray: function (queryString, uriConversionType) {

        var queryParameter = {};
        if (String.isNullOrWhitespace(queryString))
            return queryParameter;

        var items = queryString.split('&');

        for (var i = 0, l = items.length; i < l; i++) {
            var pair = items[i].split('=');
            queryParameter[pair[0]] = Lia.decodeUri(pair[1], uriConversionType);
        }

        return queryParameter
    },

    /**
     * 해당 위치까지 스크롤
     *
     * @param y
     * @param duration
     */
    scrollTo: function (y, duration, complete, easing) {

        if (duration == undefined) {
            duration = 400;
        }

        if (easing == undefined) {
            easing = 'swing';
        }

        jQuery('html, body').animate({scrollTop: y}, duration, easing, complete);
    },

    /**
     * y축 스크롤 위치 반환
     *
     * @returns top
     */
    getScrollTop: function () {

        var scrollTop = $('body').scrollTop();
        if (scrollTop == 0)
            scrollTop = $('html').scrollTop();

        return scrollTop;

    },

    openFullScreenMode: function () {

        try {
            var docV = document.documentElement;

            if (docV.requestFullscreen)
                docV.requestFullscreen();
            else if (docV.webkitRequestFullscreen) // Chrome, Safari (webkit)
                docV.webkitRequestFullscreen();
            else if (docV.mozRequestFullScreen) // Firefox
                docV.mozRequestFullScreen();
            else if (docV.msRequestFullscreen) // IE or Edge
                docV.msRequestFullscreen();
        } catch (e) {
        }

    },

    closeFullScreenMode: function () {

        try {
            if (document.exitFullscreen)
                document.exitFullscreen();
            else if (document.webkitExitFullscreen) // Chrome, Safari (webkit)
                document.webkitExitFullscreen();
            else if (document.mozCancelFullScreen) // Firefox
                document.mozCancelFullScreen();
            else if (document.msExitFullscreen) // IE or Edge
                document.msExitFullscreen();
        } catch (e) {
        }
    },

    /**
     * x축 스크롤 위치 반환
     *
     * @returns left
     */
    getScrollLeft: function () {

        var scrollTop = $('body').scrollLeft();
        if (scrollTop == 0)
            scrollTop = $('html').scrollLeft();

        return scrollTop;

    },

    /**
     * deprecated
     * go FileHelper
     *
     * 파일 확장자 추출
     * 추출할 수 없으면 null
     *
     * @param file
     * @returns {*}
     */
    extractFileExt: function (file) {

        if (String.isNullOrWhitespace(file))
            return null;

        var len = file.length;
        var last = file.lastIndexOf('.');
        if (last == -1)
            return null;

        var ext = file.substring(last, len);
        ext = ext.toLowerCase();

        return ext;
    },

    /**
     * deprecated
     * go FileHelper
     *
     * 파일 이름 추출
     * 추출할 수 없으면 null
     *
     * @param file
     * @returns {*}
     */
    extractFilename: function (file) {

        if (String.isNullOrWhitespace(file))
            return null;

        var len = file.length;
        var last = file.lastIndexOf('/');
        if (last == -1) {
            last = file.lastIndexOf("\\");
            if (last == -1)
                return null;
        }

        var filename = file.substring(last + 1, len);
        return filename;
    },

    /**
     * Whitespace를 &nbsp 태그로 변환
     *
     * @returns {string}
     */
    ws2tag: function (text) {

        if (text == undefined) {
            return text;
        }

        return text.replace(/ /g, '&nbsp;');
    },

    /**
     * xss 공격에 대한 대비
     *
     * @returns {string}
     */
    preventScript: function (text) {

        if (text == undefined) {
            return text;
        }

        text = text.replace(/<script/gi, '&lt;script');
        text = text.replace(/<\/script/gi, '&lt;/script');

        text = text.replace(/<iframe/gi, '&lt;iframe');
        text = text.replace(/<\/iframe>/gi, '&lt;/iframe');

        text = text.replace(/<form/gi, '&lt;form');
        text = text.replace(/<\/form/gi, '&lt;/form');

        text = text.replace(/<embed/gi, '&lt;embed');
        text = text.replace(/<\/embed/gi, '&lt;/embed');

        text = text.replace(/[\<](.*)(on([a-zA-Z]+)=(["']*)|formaction=(["']*)|action=(["']*))/gi, '<$1\/*');

        return text
    },

    /**
     * html -> jQuery 객체로 변환
     * 이미지 및 테이블 태그 정리
     *
     * @returns {string}
     */
    convertHtml : function( html ) {

        var jHtml = jQuery('<div>' + html + '</div>');
        jHtml.find('img').css({'max-width' : '100%'});
        jHtml.find('table').css({'width' : '100%'}).wrap('<div style="width:100%;overflow-x:auto;"></div>');
        return jHtml;
    },

    /**
     * Whitespace를 &nbsp 태그로 변환
     * 2칸 기준으로
     *
     * @returns {string}
     */
    ws2tagInHtml: function (text) {

        if (text == undefined) {
            return text;
        }

        return text.replace(/  /g, '&nbsp; ');
    },

    /**
     * 꺽쇠 변환
     *
     * @returns {string}
     */
    inequalitySign2tag: function (text) {

        if (text == undefined)
            return text;

        return text.replace(/\</g, '&lt;').replace(/\>/g, '&gt;');
    },

    /**
     * 개행 문자를 BR 태그로 변환
     *
     * @returns {string}
     */
    nl2br: function (text) {

        if (text == undefined) {
            return text;
        }

        return text.replace(/\n/g, '<br />');
    },

    /**
     * BR태그를 개행문자로 변환
     *
     * @returns {string}
     */
    br2nl: function (text) {

        if (text == undefined) {
            return text;
        }

        return text.replace(/\<br[ ]*\/?\>/g, '\n');
    },

    /**
     * 올바른 아이디인지 체크
     * 숫자와 영문자 - _ 만으로 구성되어야 함
     *
     * @param text
     * @returns {boolean}
     */
    checkValidId: function (text) {

        return !(/[^0-9a-zA-Z_\-]/.test(text));
    },

    /**
     * 올바른 이름인지 체크
     *
     * @param text
     * @returns {boolean}
     */
    checkValidName: function (text) {

        return !(/[^0-9a-zA-Z()\[\]\-_ 가-힣]/.test(text));
    },


    /**
     * 올바른 이메일 형식인지 체크
     *
     * @param text
     * @returns {boolean}
     */
    checkValidEmail: function (text) {

        return (/^[_\.0-9a-zA-Z-]+@([0-9a-zA-Z][0-9a-zA-Z-]+\.)+[a-zA-Z]{2,6}$/.test(text));
    },

    /**
     * 숫자를 한글로 변환
     *
     * @param text
     * @returns {string}
     */

    numberToHangul: function (strNumber) {
        strNumber = strNumber.replace(new RegExp(",", "g"), "");
        var arrayAmt = ["일", "이", "삼", "사", "오", "육", "칠", "팔", "구", "십"];
        var arraypos = ["", "십", "백", "천"];
        var arrayUnit = ["", "만", "억", "조", "경", "해", "자", "양", "구", "간", "정", "재", "극", "항하사", "아승기", "나유타", "불가사의", "무량대수"];
        var pos = strNumber.length % 4;
        var len = (strNumber.length / 4).toString();
        if (len.indexOf(".") > 0)
            var unit = len.substring(0, len.indexOf("."));
        else
            var unit = strNumber.length / 4 - 1;
        var korNumber = "";
        var op = 0;
        for (i = 0; i < strNumber.length; i++) {
            if (pos == 0) pos = 4;
            var num = parseInt(strNumber.substring(i, i + 1));
            if (num != 0) {
                korNumber += arrayAmt[num - 1];
                korNumber += arraypos[pos - 1];
                op = 1;
            }
            if (pos == 1) {
                if (op == 1) korNumber += arrayUnit[unit];
                unit--;
                op = 0;
            }
            pos--;
        }

        if (korNumber.length == 0 || korNumber.length == null)
            return "";
        else
            return korNumber;
    },

    /**
     * 숫자로만 이루어져 있는지 체크
     *
     * @param text
     * @returns {boolean}
     */
    checkValidDigit: function (text) {

        return !(/[^0-9]/.test(text));
    },


    /**
     * 숫자 혹은 문자만으로 구성인지 체크
     *
     * @param text
     * @returns {boolean}
     */
    checkValidAlphabetAndDigit: function (text) {

        return !(/[^0-9a-zA-Z]/.test(text));
    },


    /**
     * 숫자인지 체크
     *
     * @param text
     * @returns {boolean}
     */
    checkValidNumeric: function (text) {

        return jQuery.isNumeric(text);
    },

    /**
     * 배열 사이즈 구함
     *
     * @param array
     * @returns {Number}
     */
    assocArraySize: function (array) {

        var size = 0, key;
        for (key in array)
            ++size;

        return size;
    },

    /**
     * 속성 추출, 없으면 기본값 리턴
     *
     * @returns {*}
     */
    extractPropertyWithDefault: function () {

        var length = arguments.length;
        if (length < 1)
            return undefined;

        var defaultValue = arguments[0];
        if (length < 2)
            return defaultValue;

        var object = arguments[1];
        if (object == undefined)
            return defaultValue;

        for (var i = 2; i < length; i++) {

            var key = arguments[i];
            object = object[key];
            if (object == undefined)
                return defaultValue;
        }

        return object;
    },

    /**
     * 속성 추출, 없으면 기본값 리턴
     *
     * @returns {*}
     */
    extractPropertyWithCheckingAndDefault: function () {

        var length = arguments.length;
        if (length < 1)
            return undefined;

        var defaultValue = arguments[0];
        if (length < 2)
            return defaultValue;

        var object = arguments[1];
        if (object == undefined)
            return defaultValue;

        for (var i = 2; i < length; i++) {

            var key = arguments[i];
            object = object[key];
            if (object == undefined)
                return defaultValue;
        }

        if (String.isBlank(object)) {
            return defaultValue;
        }

        return object;
    },

    /**
     * 속성 추출
     *
     * @returns {*}
     */
    extractProperty: function () {

        var length = arguments.length;
        if (length <= 1)
            return undefined;

        var object = arguments[0];
        if (object == undefined)
            return undefined;

        for (var i = 1; i < length; i++) {

            var key = arguments[i];
            object = object[key];
            if (object == undefined)
                return undefined;
        }

        return object;
    },

    /**
     * 2개 객체에서 기본 값 추출
     * (1번 객체, 2번 객체, 파라미터 ... )
     * 1번 검색 - 없으면 2번 검색
     *
     * @returns {*}
     */
    extractPropertyFromTwoMap: function () {

        if (arguments.length < 2) {
            return undefined;
        }

        var map1 = Lia.extractProperty(arguments, 0);
        var map2 = Lia.extractProperty(arguments, 1);

        var map1ParameterList = [];
        map1ParameterList.push(map1);

        var map2ParameterList = [];
        map2ParameterList.push(map2);

        for (var i = 2, l = arguments.length; i < l; i++) {

            map1ParameterList.push(arguments[i]);
            map2ParameterList.push(arguments[i]);
        }

        var object = Lia.extractProperty.apply(this, map1ParameterList);
        if (object == undefined)
            object = Lia.extractProperty.apply(this, map2ParameterList);

        return object;
    },

    /**
     * 2개 객체에서 기본 값 추출 with 기본값
     * (기본값, 1번 객체, 2번 객체, 파라미터 ... )
     * 2번 검색 - 없으면 1번 검색 - 없으면 기본 값 반환
     *
     * @returns {*}
     */
    extractPropertyFromTwoMapWithDefault: function () {

        var defaultValues = arguments[0];
        if (arguments.length < 3) {
            return defaultValues;
        }

        var map1 = Lia.extractProperty(arguments, 1);
        var map2 = Lia.extractProperty(arguments, 2);

        var map1ParameterList = [];
        map1ParameterList.push(map1);

        var map2ParameterList = [];
        map2ParameterList.push(map2);

        for (var i = 3, l = arguments.length; i < l; i++) {

            map1ParameterList.push(arguments[i]);
            map2ParameterList.push(arguments[i]);
        }

        var object = Lia.extractProperty.apply(this, map2ParameterList);
        if (object == undefined)
            object = Lia.extractProperty.apply(this, map1ParameterList);
        if (object == undefined)
            object = defaultValues;

        return object;
    },

    /**
     * 현재 시간이 해당 시간 내에 있는지 체크
     *
     * @param startHour
     * @param endHour
     * @returns {boolean}
     */
    checkHourIn: function (startHour, endHour) {

        var hour = new Date().getHours();

        if (startHour == endHour) {
            return (hour == startHour);
        } else if (startHour < endHour) {
            return (hour >= startHour && hour <= endHour);
        } else if (startHour > endHour) {
            return (hour >= startHour || hour <= endHour);
        }

        return false;
    },

    /**
     * 날짜 YYYY-MM-DD HH:MM:SS 를 날짜만 추출하여 포매팅
     *
     * @param date YYYY-MM-DD HH:MM:SS
     * @param between 구분자
     * @returns {string}
     */

    formatDateWithSeparator: function (date, between) {

        if(String.isBlank(date)) {
            return '-';
        } else {
            var regex = /(\d{4})-(\d{2})-(\d{2}) \d{2}:\d{2}:\d{2}/;
            var formatting = '$1' + between + '$2' + between + '$3';

            return date.replace(regex, formatting);
        }
    },
    /**
     * 날짜 YYYY-MM-DD HH:MM:SS 를 영어식 날짜 표기법으로 변경
     * Ex ) 2020-12-06 02:42:24  ==>  Feb 27, 2020
     * @param date string YYYY-MM-DD HH:MM:SS
     * @returns english format
     */

    dateStringToEngFormat: function (dateString) {
        var month = ['Jan', 'Feb', 'Mar', "Apr", "May", 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        var date = dateString;

        var substr = date.split('-');
        var substr2 = substr[2].split(' ');

        var monthIdx = Number(substr[1]);
        var day = substr2[0];

        var result = month[monthIdx - 1] + " " + day + ", " + substr[0];

        return result;
    },


    /**
     * 현재 시간이 해당 요일 안에 있는지 체크
     *
     * @param startHour
     * @param endHour
     * @returns {boolean}
     */
    checkDayOfWeekIn: function (startDay, endDay) {

        var day = new Date().getDay();

        if (startDay == endDay) {
            return (day == startDay);
        } else if (startDay < endDay) {
            return (day >= startDay && day <= endDay);
        } else if (startDay > endDay) {
            return (day >= startDay || day <= endDay);
        }

        return false;
    },

    convertSecToTime: function (sec) {

        if (sec == undefined)
            return false;

        var hours = Math.floor(sec / 3600) < 10 ? ("00" + Math.floor(sec / 3600)).slice(-2) : Math.floor(sec / 3600);
        var minutes = ("00" + Math.floor((sec % 3600) / 60)).slice(-2);
        var seconds = ("00" + (sec % 3600) % 60).slice(-2);

        return hours + ":" + minutes + ":" + seconds;

    },

    /**
     * 두 날짜 간 일수 계산 (당일은 1일로 계산, 날짜형식이 아닌 경우 null 반환)
     *
     * @param startDay YYYY-MM-DD
     * @param endDay YYYY-MM-DD
     * @returns {(number|null)}
     */

    getDayDiff: function (startDay, endDay) {
        var regEx = /\d{4}-\d{2}-\d{2}/;
        if (regEx.test(startDay) && regEx.test(endDay)) {
            var _startDay = new Date(startDay);
            var _endDay = new Date(endDay);
            var msDiff = Date.parse(_endDay) - Date.parse(_startDay);
            return msDiff / 86400000 + 1;
        } else return null;
    },


    /**
     * 같은 key - value 가지고 있는지
     *
     * @returns {boolean}
     */
    isSameMap: function (map1, map2) {

        if (map1 == map2) {
            return true;
        }

        if (map1 == undefined || map2 == undefined) {
            return false;
        }

        if (Lia.assocArraySize(map1) != Lia.assocArraySize(map2)) {
            return false;
        }

        for (var key in map1) {

            if (map1[key] != map2[key]) {
                return false;
            }

        }

        return true;
    },


    /**
     * 같은 key - value 가지고 있는지
     * blank는 동일하게 인지한다.
     *
     * @returns {boolean}
     */
    isSameMapWithoutBlank: function (map1, map2) {

        if (map1 == map2) {
            return true;
        }

        if (map1 == undefined || map2 == undefined) {
            return false;
        }

        var new1Map = {};
        for (var key in map1) {

            var item = map1[key];
            if ( String.isNotBlank(item) ) {
                new1Map[key] = item;
            }
        }

        var new2Map = {};
        for (var key in map2) {

            var item = map2[key];
            if ( String.isNotBlank(item) ) {
                new2Map[key] = item;
            }
        }

        return Lia.isSameMap(new1Map, new2Map);
    },

    convertBytesToSize: function (bytes, decimals) {
        if (bytes == 0) return '0 Byte';
        var k = 1000; // or 1024 for binary
        var dm = decimals + 1 || 3;
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    convertBytesToSizeInBinary: function (bytes, decimals) {
        if (bytes == 0) return '0 Byte';
        var k = 1024; // or 1024 for binary
        var dm = decimals + 1 || 3;
        var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    convertBps: function (bps, decimals) {
        if (bps == 0) return '0 bps';
        var k = 1000; // or 1024 for binary
        var dm = decimals + 1 || 3;
        var sizes = ['bps', 'Kbps', 'Mbps', 'Gbps', 'Tbps', 'Pbps', 'Ebps', 'Zbps', 'Ybps'];
        var i = Math.floor(Math.log(bps) / Math.log(k));
        return parseFloat((bps / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    },

    contains: function () {

        var argumentLength = arguments.length;
        if (argumentLength <= 2) {
            return (arguments[0] == arguments[1]);
        }

        var base = arguments[0];
        for (var i = 1; i < argumentLength; i++) {

            if (base == arguments[i])
                return true;
        }

        return false;
    },

    convertStrToObj: function (s) {

        if (typeof s == 'string') {
            return JSON.parse(s);
        }

        return s;
    },

    convertJSONStringIfNotEmpty: function ( o ) {

        if ( Lia.assocArraySize(o) > 0 ) {
            return JSON.stringify(o);
        }

        return undefined;
    },

    /**
     * 객체 each 함수
     * 
     * @param object 대상 object
     * @param func 실행 함수
     * @param passObject 전달 객체
     * @returns {boolean} 실행했는지의 여부
     */
    each : function (object, func, passObject) {

        if ( object == undefined ) {
            return false;
        }

        var executed = false;

        for ( var key in object ) {

            if ( !object.hasOwnProperty(key) ) {
                continue;
            }

            var item = object[key];
            var exit = func(item, key, object, passObject);
            if ( exit == true ) {
                return true;
            }

            executed = true;
        }

        return executed;
    }
};

if (typeof String.isNullOrWhitespace !== 'function') {
    /**
     * Whitespace 거나 NULL 이면 true 반환
     *
     * @param text
     * @returns {boolean}
     */
    String.isNullOrWhitespace = function (text) {

        if (text == null)
            return true;

        if (typeof text == 'string' && text.trim().length == 0)
            return true;

        return false;
    }
}

if (typeof String.isNotNullOrWhitespace !== 'function') {
    /**
     * Whitespace 거나 NULL 이면 true 반환
     *
     * @param text
     * @returns {boolean}
     */
    String.isNotNullOrWhitespace = function (text) {

        return !String.isNullOrWhitespace(text);
    }
}


if (typeof String.isBlank !== 'function') {
    /**
     * Whitespace 거나 NULL 이면 true 반환
     *
     * @param text
     * @returns {boolean}
     */
    String.isBlank = String.isNullOrWhitespace;
}

if (typeof String.isNotBlank !== 'function') {
    /**
     * Whitespace 거나 NULL 이면 true 반환
     *
     * @param text
     * @returns {boolean}
     */
    String.isNotBlank = String.isNotNullOrWhitespace;
}


if (typeof Array.isBlank !== 'function') {
    /**
     * undefined거나 list 개수가 0이면 true 리턴
     *
     * @param array
     * @returns {boolean}
     */
    Array.isBlank = function (array) {

        return (array == undefined || array.length == 0);
    }
}

if (typeof Array.isNotBlank !== 'function') {
    /**
     * undefined거나 list 개수가 0이면 true 리턴 반대
     *
     * @param array
     * @returns {boolean}
     */
    Array.isNotBlank = function (array) {

        return !(Array.isBlank(array));
    }
}


if (typeof Array.isEmpty !== 'function') {

    /**
     * undefined거나 list 개수가 0이면 true 리턴
     *
     * @param array
     * @returns {boolean}
     */
    Array.isEmpty = function (array) {

        if (array == undefined || array.length == 0) {
            return true;
        }

        return false;
    };
}


if (typeof Array.isNotEmpty !== 'function') {

    /**
     * undefined거나 list 개수가 0이면 true 리턴 반대
     *
     * @param array
     * @returns {boolean}
     */
    Array.isNotEmpty = function (array) {

        return !(Array.isEmpty(array));
    };
}

if (typeof Array.forEach !== 'function') {


    /**
     *
     * @param list 배열
     * @param func func( item, index, array, object )
     * @param object 전달 object
     * @returns {boolean} 0 이상인 경우
     */
    Array.forEach = function (list, func, object) {

        if ( list == undefined ) {
            return false;
        }

        var size = list.length;
        if ( size <= 0 ) {
            return false;
        }


        for ( var i = 0, l = size; i < l; i++ ) {

            var item = list[i];
            var exit = func(item, i, list, object);
            if ( exit == true ) {
                return true;
            }
        }

        return true;
    };
}



if (typeof String.prototype.endsWith !== 'function') {
    /**
     * 문자열이 해당 suffix 로 끝나는지 체크
     *
     * @param suffix
     * @returns {boolean}
     */
    String.prototype.endsWith = function (suffix) {

        return this.indexOf(
            suffix,
            this.length - suffix.length) != -1;
    };
}


if (typeof String.prototype.startsWith !== 'function') {
    /**
     * 문자열이 해당 suffix 로 시작하는지 체크
     *
     * @param suffix
     * @returns {boolean}
     */
    String.prototype.startsWith = function (suffix) {

        return this.indexOf(suffix) == 0;
    };
}


if (typeof String.prototype.trim !== 'function') {
    /**
     * 문자열 끝의 공백 없앰
     *
     * @returns {string}
     */
    String.prototype.trim = function () {

        return this.replace(/^\s+|\s+$/g, '');
    }
}


if (typeof String.prototype.removeWhitespace !== 'function') {
    /**
     * 문자열 안 공백 삭제
     *
     * @returns {string}
     */
    String.prototype.removeWhitespace = function () {

        return this.replace(/ /g, '');
    }
}


if (typeof String.prototype.removeBlank !== 'function') {
    /**
     * 문자열 안 공백 삭제
     *
     * @returns {string}
     */
    String.prototype.removeBlank = String.prototype.removeWhitespace;
}


if (typeof String.prototype.contains !== 'function') {
    String.prototype.contains = function (suffix) {

        return this.indexOf(suffix) >= 0;
    };
}

if (typeof Array.includes !== 'function') {
    Array.includes = function (sourceElements, searchElement /*, fromIndex*/) {

        var O = Object(sourceElements);
        var len = parseInt(O.length, 10) || 0;
        if (len === 0) {
            return false;
        }

        var n = parseInt(arguments[2], 10) || 0;
        var k;
        if (n >= 0) {
            k = n;
        } else {
            k = len + n;
            if (k < 0) {
                k = 0;
            }
        }

        var currentElement;
        while (k < len) {
            currentElement = O[k];
            if (searchElement === currentElement ||
                (searchElement !== searchElement && currentElement !== currentElement)) { // NaN !== NaN
                return true;
            }
            k++;
        }
        return false;
    };
}


Lia.extractGetParameter = Lia.extractGetParameterMap;
Lia.extractGetParameterFromUrl = Lia.extractGetParameterMapFromUrl;
Lia.isMobile = Lia.checkMobile();
Lia.ieVersion = Lia.checkInternetExplorerVersion();
Lia.p = Lia.extractProperty;
Lia.pd = Lia.extractPropertyWithDefault;
Lia.pcd = Lia.extractPropertyWithCheckingAndDefault;
Lia.pt = Lia.extractPropertyFromTwoMap;
Lia.ptd = Lia.extractPropertyFromTwoMapWithDefault;


// 지원하는 브라우져 체크
// ie 11 이하 브라우져는 지원하지 않음.
if ( Lia.ieVersion > 0 && Lia.ieVersion < 11 ) {
    alert('지금 접속하신 브라우저는 더 이상 지원하지 않습니다.\n' +
        '(This browser is no longer supported.)');
}


var console = window.console || {
    log: function () {
    }
};

// window.setTimeout 으로 호출해야 함
//if ( Lia.ieVersion != -1 && Lia.ieVersion <= 9 ) {

var __nativeST__ = window.setTimeout, __nativeSI__ = window.setInterval;

window.setTimeout = function (vCallback, nDelay /*, argumentToPass1, argumentToPass2, etc. */) {
    var oThis = this, aArgs = Array.prototype.slice.call(arguments, 2);
    return __nativeST__(vCallback instanceof Function ? function () {
        vCallback.apply(oThis, aArgs);
    } : vCallback, nDelay);
};

window.setInterval = function (vCallback, nDelay /*, argumentToPass1, argumentToPass2, etc. */) {
    var oThis = this, aArgs = Array.prototype.slice.call(arguments, 2);
    return __nativeSI__(vCallback instanceof Function ? function () {
        vCallback.apply(oThis, aArgs);
    } : vCallback, nDelay);
};
//}


/* Lia.Strings 구현 */
Lia.Strings = {


    MESSAGE: {

        CONFIRM_DELETE: {
            ko: '정말 삭제하시겠습니까?',
            en: 'Are you sure you want to delete this?',
        },
        CONFIRM_EDIT: {
            'ko': '이대로 저장하시겠습니까?',
            'en': 'Do you want to save changes?'
        },

        NOT_ALLOWED_TO_READ: {
            ko: '읽을 수 있는 권한이 없습니다.',
            en: 'Not allowed to read.',
        },

        PDF_VIEWER_SUPPORT_WARNING: {

            'ko': '이 브라우저는 PDF 미리보기를 지원하지 않습니다.<BR/>' +
                'PDF 뷰어 프로그램을 설치해주시기 바랍니다.',
            'en': 'This browser does not support inline PDFs.<BR/>' +
                'Please install PDF viewer program.'
        },

        IFRAME_SUPPORT_WARNING: {

            'ko': '이 브라우저는 iframe을 지원하지 않습니다.',
            'en': 'This browser does not support iframe.'
        }
    },

    POPUP: {

        TITLE: {

            INFO: {
                ko: '안내',
                en: 'Info',
            },

            CAUTION: {
                ko: '주의',
                en: 'Caution',
            }

        },
    },

    BUTTON: {

        OK: {
            ko: '확인',
            en: 'OK',
        },

        CONFIRM: {
            ko: '확인',
            en: 'Confirm',
        },

        CANCEL: {
            ko: '취소',
            en: 'Cancel',
        },

        SET_AVAILABILITY: {
            ko: '게시 설정',
            en: 'Set Availability',
        },

        EDIT_CATEGORY: {
            ko: '카테고리 편집',
            en: 'Edit Category',
        },


        ADD: {

            'ko': '+ 추가',
            'en': '+ Add'
        },

        EDIT: {

            'ko': '편집',
            'en': 'Edit'
        },


        DELETE_MENU: {

            'ko': '메뉴 삭제',
            'en': 'Delete Menu'
        },

        DELETE: {

            'ko': '삭제',
            'en': 'Delete'
        },
    },

    OPTION_LIST: {

        ALL: {

            'ko': '전체',
            'en': 'Select All'
        },

        SELECT: {

            'ko': '선택',
            'en': 'Select'
        },

        NONE: {

            'ko': '없음',
            'en':  'None'
        },

        AVAILABLE: {

            'ko':  '게시',
            'en':  'Available'
        },

        NOT_AVAILABLE: {

            'ko':  '비게시',
            'en':  'Not Available'
        },
    },

    TRITON: {

        EMAIL_INPUT: {

            DIRECT_INPUT: {
                ko: '직접입력',
                en: 'Direct Input'
            }
        },


        ADDRESS_INPUT: {

            SEARCH: {
                ko: '검색',
                en: 'Search'
            }
        },

        TAB: {

            CLOSE: {
                ko: '탭 닫기',
                en: 'Close',
            },

            CLOSE_OTHERS: {
                ko: '다른 탭 모두 닫기',
                en: 'Close Others',
            }

        },

        HEADER: {

            HELLO: {
                ko: '님 환영합니다.',
                en: ', Hello!',
            },

            LAST_LOGGED_IN: {
                ko: '최종 로그인',
                en: 'Last logged in',
            },

            EXTEND_TIMEOUT : {
                ko: '연장',
                en: 'Extend',
            }
        },


        UPLOADER: {

            ATTACHMENT: {
                ko: '첨부파일',
                en: 'Attachment',
            }

        }
    },

    CALENDAR: {

        CALENDAR_SUNDAY: {
            "ko": "일",
            "en": "Sun",
            "zh": "星期日"
        },
        CALENDAR_MONDAY: {

            "ko": "월",
            "en": "Mon",
            "zh": "星期一"
        },
        CALENDAR_TUESDAY: {

            "ko": "화",
            "en": "Tue",
            "zh": "星期二"
        },
        CALENDAR_WEDNESDAY: {

            "ko": "수",
            "en": "Wed",
            "zh": "星期三"
        },
        CALENDAR_THURSDAY: {

            "ko": "목",
            "en": "Thu",
            "zh": "星期四"
        },
        CALENDAR_FRIDAY: {

            "ko": "금",
            "en": "Fri",
            "zh": "星期五"
        },
        CALENDAR_SATURDAY: {

            "ko": "토",
            "en": "Sat",
            "zh": "星期六"
        },

    },

    BOARD: {

        REGISTERED: {
            'ko': '등록 된 글',
            'en': 'Registered'
        },
        DELETED: {
            'ko': '삭제 된 글',
            'en': 'Deleted'
        },

        STATUS: {
            ko: '상태',
            en: 'Status'
        },

        IS_AVAILABLE_DATE: {
            ko: '게시일',
            en: 'Available Date'
        },

        IS_AVAILABLE: {
            ko: '게시',
            en: 'Available'
        },

        NO: {
            ko: '번호',
            en: '#'
        },

        TITLE: {
            ko: '제목',
            en: 'Title'
        },

        ATTACHMENT: {
            ko: '첨부파일',
            en: 'Browse'
        },

        REGISTERED_DATE: {
            ko: '작성일',
            en: 'Registered Date'
        },

        LAST_MODIFIED_DATE: {
            ko: '최근 수정일',
            en: 'Last Modified Date'
        },

        CATEGORY: {
            ko: '카테고리',
            en: 'Category'
        },

        ALL: {
            ko: '전체',
            en: 'All'
        },

        VIEWS: {
            ko: '조회 수',
            en: 'Views'
        },

        ITEMS_PER_PAGES: {
            ko: '개씩 보기',
            en: 'Items per Page'
        },

        ADD: {
            ko: '글쓰기',
            en: 'New'
        },

        AUTHOR: {
            ko: '작성자',
            en: 'Author'
        },

        AUTHOR_USERNAME: {
            ko: '작성자 아이디',
            en: 'Author Username'
        },

        AUTHOR_NAME: {
            ko: '작성자 이름',
            en: 'Author Name'
        },

        SEARCH: {
            ko: '검색',
            en: 'Search'
        },

        SEARCH_RESULT: {
            ko: '검색 결과',
            en: 'Search Result'
        },

        BODY: {
            ko: '내용',
            en: 'Body'
        },

        PRIVATE_CONTENT: {
            ko: '비밀글',
            en: 'Private'
        },

        LIST: {
            ko: '목록',
            en: 'List'
        },

        SAVE: {
            ko: '저장',
            en: 'Save'
        },

        CANCEL: {
            ko: '취소',
            en: 'Cancel'
        },

        ID: {
            ko: '아이디',
            en: 'ID'
        },

        NAME: {
            ko: '이름',
            en: 'Name'
        },

        NO_CATEGORY: {
            ko: '카테고리 없음',
            en: 'No Category'
        },

        COMMENT: {
            ko: '답변',
            en: 'Comment'
        },

        NO_CONTENT: {
            ko: '표시할 항목이 없습니다.',
            en: 'No content.'
        },

        WAITING: {
            ko: '대기',
            en: 'Waiting'
        },
        COMPLETED: {
            ko: '완료',
            en: 'Completed'
        },

        SEARCH_PLACEHOLDER: {
            ko: '검색',
            en: 'Search'
        },

        EDIT_OR_DELETE: {
            ko: '수정 및 삭제',
            en: 'Edit or Delete'
        }

    },


    Locale: {
        KO: 'ko',
        EN: 'en',
        ZH: 'zh'
    },

    locale: 'ko',

    applyStrings: function (j) {

        var jStrings = undefined;
        if (j != undefined) {
            jStrings = j.find('.strings');
        } else {
            jStrings = $('.strings');
        }

        jStrings.each(function () {

            var jThis = $(this);
            var name = jThis.dataAttr('lia-string-key');
            if (String.isNotBlank(name)) {

                var text = Lia.Strings.getString(name);
                jThis.html(text);
            }
        });
    },

    setLocale: function (locale) {
        Lia.Strings.locale = locale;
    },

    getLocale: function () {
        return Lia.Strings.locale;
    },

    isLocaleKo: function () {
        return Lia.Strings.locale == Lia.Strings.Locale.KO;
    },

    getString: function (name, locale) {

        if (locale == undefined) {
            locale = Lia.Strings.locale;
        }

        if (typeof name == 'string') {

            var nameSplit = name.split('.');
            var object = Lia.Strings;
            for (var i = 0, l = nameSplit.length; i < l; i++) {

                var key = nameSplit[i];
                object = object[key];
                if (object == undefined) {
                    return undefined;
                }
            }

            name = object;
        }

        return Lia.p(name, locale);
    },

    setString: function (text, name, locale) {

        if (locale == undefined) {
            locale = Lia.Strings.locale;
        }

        if (typeof name == 'string') {

            var nameSplit = name.split('.');
            var object = Lia.Strings;
            for (var i = 0, l = nameSplit.length; i < l; i++) {

                var key = nameSplit[i];
                object = object[key];
                if (object == undefined) {
                    object[key] = {};
                }
            }

            name = object;
        }

        if (name[locale] == undefined) {
            name[locale] = {};
        }

        name[locale] = text;
    }
};


/**
 * 공용 확장 함수
 */

(function ($) {
    

    $.fn.extend({

        dataAttr : function (key, value) {

            if ( value == undefined ) {

                var jEq= this.eq(0);

                value = jEq.attr('data-' + key);
                if ( value == undefined ) {
                    value = jEq.attr(key);
                }

                return value;
            }


            for (var i = 0, l = this.length; i < l; i++) {

                var jEq  = this.eq(i);
                jEq.attr('data-'+key, value);
            }

            return this;

        }
    });
})(jQuery);
/*

 lia.lang.js
 여러가지 언어 사용할 수 있도록 지원

 <span class="lang" data-lia-name="{항목 이름}" data-lia-attr="{적용할 attr}"></span>
 data-lia-attr 이 없으면 text 함수 사용

 맵은 이런식으로

 var LANG_MAP = {

 'name' : {
 'us' : 'test',
 'ko' : '테스트'
 }
 };

 $.initLang(LANG_MAP, 'us');         // 초기화
 $.applyLang( selector );            // 적용
 $.getLangValue( name, 'us');        // 값 반환
 $.getLangValue( name );             // 값 반환 ( 기본 키로 )

 */

jQuery.extend({

    liaLangMap: undefined,
    liaLangKey: undefined,
    initLang: function (langMap, langKey) {

        jQuery.liaLangMap = langMap;
        jQuery.liaLangKey = langKey;
    },

    applyLang: function (j) {

        var selector = '.' + Lia.Component.Name.LANG;

        if (j == undefined)
            j = $(selector);
        else
            j = j.find(selector);

        return j.applyLang();
    },

    getLangValue: function (name, key) {

        var langMap = jQuery.liaLangMap;
        if (langMap == undefined)
            return '';

        if (key == undefined)
            key = jQuery.liaLangKey;
        if (key == undefined)
            return '';

        var value = undefined;
        var map = langMap[name];
        if (map != undefined)
            value = map[key];

        if (String.isNullOrWhitespace(value))
            value = '';

        return value;

    }

});

jQuery.fn.extend({

    applyLang: function () {

        return this.each(function () {

            var j = jQuery(this);
            if (!j.hasClass(Lia.Component.Name.LANG))
                return;

            var name = j.dataAttr(Lia.Component.AttrName.NAME);
            if (String.isNullOrWhitespace(name))
                return;

            var value = jQuery.getLangValue(name);

            var attr = j.dataAttr(Lia.Component.AttrName.ATTR);
            if (attr != undefined) {
                j.attr(attr, value);
                return;
            }

            var css = j.dataAttr(Lia.Component.AttrName.CSS);
            if (css != undefined) {
                j.css(css, value);
                return;
            }

            j.html(value);
        });

    }

});


/**
 * popup
 *
 * 구현 가이드
 *      사이트 콘텐츠 부분을 wrapping하는 div의 position을 absolute로
 *      제일 하단에 dim 객체와 popup 객체를 위치
 *
 *      <body>
 *          <div id="wrapper" style="position:absolute;>
 *              ...
 *          </div>
 *
 *          <div class="dim [cancelable]" data-lia-z-index="{z-index 값}" data-lia-popup="{연결된 Popup Selector}" data-lia-opacity data-lia-dim-background-color data-lia-opacity></div>
 *          <div id="info_popup" class="popup" style="width:{popup width};height:{popup height}" data-lia-z-index="{z-index 값}"
 *          data-lia-position-top="{위치 값 고정 시}"
 *          data-lia-position-left="{위치 값 고정 시}"
 *          data-lia-position="{위치 : fiexed, absolute}"
 *          data-lia-dim="{사용할 Dim Selector}"></div>
 *      </body>
 *
 * popup
 *      .popupShow
 *          팝업 보여짐
 *      .popupHide
 *          팝업 사라짐
 *
 * $.showPopup()
 *      있는팝업 모두 다 보여짐
 * $.showPopup(selector)
 *      해당 selector 팝업 show
 * $.hidePopup()
 *      있는팝업 모두 다 사라짐
 * $.hidePopup(selector)
 *      해당 selector 팝업 hide
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initDim();
 $.initPopup();

 $(window).resize(function(){

 $.adjustPopup();
 });
 });

 */

jQuery.extend({

    liaPopupZIndex: Lia.Component.Value.Popup.DEFAULT_Z_INDEX,

    /**
     * 팝업 순서 지정해줄 함수
     *
     * @param index
     */
    initPopupZIndex: function (index) {

        jQuery.liaPopupZIndex = index;
    },

    /**
     * 초기화
     */
    initPopup: function (j, options) {

        var selector = '.' + Lia.Component.Name.POPUP;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.initPopup(options);
    },


    /**
     * 초기화
     */
    initDim: function (j) {

        var selector = '.' + Lia.Component.Name.DIM;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.initDim();
    },

    /**
     * 조정
     */
    adjustPopup: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.adjustPopup();
    },

    /**
     * 팝업 표시
     *   해당 selector
     *   모든 팝업 : 인자 없을 때
     *
     * @param selector
     */
    showPopup: function (selector, options) {

        if (selector == undefined)
            return jQuery('.' + Lia.Component.Name.POPUP).showPopup(options);
        else
            return jQuery(selector).showPopup(options);

    },

    /**
     * 팝업 내려기
     *   해당 selector
     *   모든 팝업 : 인자 없을 때
     *
     * @param selector
     */
    hidePopup: function (selector, options) {

        if (selector == undefined)
            return jQuery('.' + Lia.Component.Name.POPUP).hidePopup(options);
        else
            return jQuery(selector).hidePopup(options);
    },

    /**
     * 팝업이 표시되고 있는지 여부
     *   해당 selector
     *   모든 팝업 : 인자 없을 때
     *
     * @param selector
     * @returns {*}
     */
    isShowingPopup: function (selector) {

        if (selector == undefined)
            return jQuery('.' + Lia.Component.Name.POPUP).isShowingPopup();
        else
            return jQuery(selector).isShowingPopup();
    }
});

jQuery.fn.extend({

    /**
     * dim 초기화
     *
     * @returns {*}
     */
    initDim: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            if (jThis.hasClass(Lia.Component.Flag.INITED))
                return;

            var position = jThis.dataAttr(Lia.Component.AttrName.POSITION);
            if (position == undefined)
                position = Lia.Component.Value.Popup.DEFAULT_POSITION;

            var opacity = jThis.dataAttr(Lia.Component.AttrName.OPACITY);
            if (opacity == undefined)
                opacity = Lia.Component.Value.Popup.DEFAULT_DIM_OPACITY;

            var dimBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.DIM_BACKGROUND_COLOR);
            if (dimBackgroundColor == undefined)
                dimBackgroundColor = Lia.Component.Value.Popup.DEFAULT_DIM_BACKGROUND_COLOR;

            jThis.css({
                'background-color': dimBackgroundColor,
                'opacity': opacity,
                'position': position,

                'left': '0px',
                'top': '0px',
                'width': '100%',
                'height': '100%'

            }).click(function (e) {

                e.preventDefault();

                var jThis = jQuery(this);
                var cancelable = jThis.hasClass(Lia.Component.Flag.CANCELABLE);
                if (cancelable) {

                    var jPopup = undefined;

                    var popup = jThis.dataAttr(Lia.Component.AttrName.POPUP);
                    if (popup == Lia.Component.Value.Popup.NEXT_POPUP) {

                        jPopup = jThis.next('.' + Lia.Component.Name.POPUP);

                    } else if (popup != undefined) {

                        jPopup = jQuery('.' + Lia.Component.Name.POPUP).filter(popup);
                    }

                    if (jPopup != undefined) {
                        jPopup.hidePopup();
                    }
                }

            }).hide();

            jThis.addClass(Lia.Component.Flag.INITED);
        });
    },

    /**
     * popup 초기화
     *
     * @returns {*}
     */
    initPopup: function (options) {

        return this.each(function () {

            var jThis = jQuery(this);
            if (jThis.hasClass(Lia.Component.Flag.INITED))
                return;

            var position = jThis.dataAttr(Lia.Component.AttrName.POSITION);
            if (position == undefined)
                position = Lia.Component.Value.Popup.DEFAULT_POSITION;

            jThis.css({
                'position': position,
                'left': '0px',
                'top': '0px'
            }).adjustPopup().hide();

            jThis.addClass(Lia.Component.Flag.INITED);
        });
    },

    /**
     * 팝업 위치 조정
     *
     * @returns {*}
     */
    adjustPopup: function () {

        return this.each(function () {

            var jWindow = jQuery(window);
            var windowWidth = parseFloat(jWindow.width());
            var windowHeight = parseFloat(jWindow.height());

            var jThis = jQuery(this);
            var width = parseFloat(jThis.outerWidth(true));
            var height = parseFloat(jThis.outerHeight(true));

            var position = jThis.dataAttr(Lia.Component.AttrName.POSITION);
            if (position == undefined)
                position = Lia.Component.Value.Popup.DEFAULT_POSITION;

            var positionTop = jThis.dataAttr(Lia.Component.AttrName.POSITION_TOP);
            if (positionTop != undefined) {

                jThis.css({
                    'top': positionTop
                });

            } else {

                if (!jThis.hasClass(Lia.Component.Flag.NO_ADJUST)) {

                    if (position == Lia.Component.Value.Popup.Position.FIXED) {
                        jThis.css({
                            'top': ((windowHeight - height) / 2) + 'px'
                        });
                    } else if (position == Lia.Component.Value.Popup.Position.ABSOLUTE) {
                        var scrollTop = Lia.getScrollTop();
                        var top = (scrollTop + ((windowHeight - height) / 2));
                        if (top < 0) {
                            top = 0;
                        }

                        jThis.css({
                            'top': top + 'px'
                        });

                    }
                }
            }

            var positionLeft = jThis.dataAttr(Lia.Component.AttrName.POSITION_LEFT);
            if (positionLeft != undefined) {

                jThis.css({
                    'left': positionLeft
                });

            } else {

                jThis.css({
                    'left': ((windowWidth - width) / 2) + 'px'
                });
            }


        });
    },

    /**
     * 팝업 표시 여부
     *
     * @returns {*}
     */
    isShowingPopup: function () {

        return this.hasClass(Lia.Component.Flag.SHOWING);
    },

    /**
     * 팝업 표시
     *
     * @returns {*}
     */
    showPopup: function (options) {

        for (var i = 0, l = this.length; i < l; i++) {

            var jThis = this.eq(i);
            if (!jThis.hasClass(Lia.Component.Flag.NO_DIM)) {

                var jDim = undefined;
                var dim = jThis.dataAttr(Lia.Component.AttrName.DIM);
                if (dim == Lia.Component.Value.Popup.PREV_DIM) {

                    jDim = jThis.prev('.' + Lia.Component.Name.DIM);

                } else if (dim != undefined) {

                    jDim = jQuery('.' + Lia.Component.Name.DIM).filter(dim);
                }

                if (jDim != undefined)
                    jDim.each(liaShowPopup);
            }

            var dom = jThis.get(0);
            liaShowPopup.call(dom);
            jThis.adjustPopup();

            jThis.attr('tabindex', 0);
            jThis.focus();
            jThis.blur();
            jThis.removeAttr('tabindex');
        }

        return this;
    },

    /**
     * 팝업 내리기
     *
     * @returns {*}
     */
    hidePopup: function (options) {

        for (var i = 0, l = this.length; i < l; i++) {

            var jThis = this.eq(i);
            if (!jThis.hasClass(Lia.Component.Flag.NO_DIM)) {
                var jDim = undefined;

                var dim = jThis.dataAttr(Lia.Component.AttrName.DIM);
                if (dim == Lia.Component.Value.Popup.PREV_DIM) {

                    jDim = jThis.prev('.' + Lia.Component.Name.DIM);

                } else if (dim != undefined) {

                    jDim = jQuery('.' + Lia.Component.Name.DIM).filter(dim);
                }

                if (jDim != undefined)
                    jDim.each(liaHidePopup);
            }

            liaHidePopup.call(jThis.get(0), options);
        }

        return this;
    }
});

function liaShowPopup(options) {
    var jThis = jQuery(this);
    if (!jThis.hasClass(Lia.Component.Flag.SHOWING)) {
        var zIndex = jThis.dataAttr(Lia.Component.AttrName.Z_INDEX);
        if (String.isBlank(zIndex)) {

            zIndex = jQuery.liaPopupZIndex;
            var jList = jQuery('.' + Lia.Component.Name.DIM + ',.' + Lia.Component.Name.POPUP);
            for (var i = 0, l = jList.length; i < l; i++) {
                var baseZIndex = jList.eq(i).css('z-index');
                if (String.isNotBlank(baseZIndex)) {
                    baseZIndex = parseInt(baseZIndex);
                    if (baseZIndex > zIndex) {
                        zIndex = baseZIndex;
                    }
                }
            }

            ++zIndex;
        }


        jThis.css('z-index', zIndex).addClass(Lia.Component.Flag.SHOWING);
        if (jThis.hasClass(Lia.Component.Flag.WITHOUT_ANIMATING)) {

            jThis.show();
            var showEvent = new jQuery.Event(Lia.Component.Event.SHOW);
            jThis.trigger(showEvent);

        } else {
            jThis.fadeIn(Lia.Component.Value.Popup.FADE_DURATION);
            window.setTimeout.call(this, function (data) {

                var jThis = jQuery(this);
                var showEvent = new jQuery.Event(Lia.Component.Event.SHOW);
                jThis.trigger(showEvent);

            }, Lia.Component.Value.Popup.FADE_DURATION);
        }
    }
}


function liaHidePopup(options) {
    var jThis = jQuery(this);

    if (jThis.hasClass(Lia.Component.Flag.SHOWING)) {
        jThis.removeClass(Lia.Component.Flag.SHOWING);
        if (jThis.hasClass(Lia.Component.Flag.WITHOUT_ANIMATING)) {
            jThis.hide();
            var hideEvent = new jQuery.Event(Lia.Component.Event.HIDE);
            jThis.trigger(hideEvent);
        } else {
            jThis.fadeOut(Lia.Component.Value.Popup.FADE_DURATION);
            window.setTimeout.call(this, function (data) {

                var jThis = jQuery(this);
                var hideEvent = new jQuery.Event(Lia.Component.Event.HIDE);
                jThis.trigger(hideEvent);

            }, Lia.Component.Value.Popup.FADE_DURATION);
        }
    }
}


/**
 * lia.queue.js
 *
 * queue class
 *
 **/
/*
 */

Lia.Queue = function () {

    this.init();
};

Lia.Queue.prototype.init = function () {
    this.list = [];
};

Lia.Queue.prototype.enqueue = function (element) {
    this.list.push(element);
};

Lia.Queue.prototype.peek = function () {
    if (this.empty())
        return null;
    return this.list[0];
};

Lia.Queue.prototype.dequeue = function () {

    if (this.empty()) {
        return null;
    } else {
        return this.list.shift();
    }
};

Lia.Queue.prototype.empty = function () {
    return (this.list.length == 0);
};

Lia.Queue.prototype.size = function () {
    return this.list.length;
};

Lia.Queue.prototype.clear = function () {
    while (this.list.length > 0) {
        this.list.pop();
    }
};
/**
 * pager
 *
 * 페이지 순서대로 크고 끼고 할 수 있도록
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initImageSelect();
 $.initImageSelectList();
 });
 */

(function ($) {

    $.fn.extend({

        pagerIndex: function (index) {

            if (index == undefined) {

                return this.eq(0).children('.' + Lia.Component.Flag.SHOWING).index();
            }

            for (var i = 0, l = this.length; i < l; i++) {

                var jEq = this.eq(i);
                var jChildren = jEq.children();

                jChildren.hide().filter(Lia.Component.Flag.SHOWING).removeClass(Lia.Component.Flag.SHOWING);
                jChildren.eq(index).addClass(Lia.Component.Flag.SHOWING).show();
            }

            return this;
        }
    });
})(jQuery);
/**
 * resize
 *
 * 화면 사이즈에 맞도록 크기 변경
 *
 * <tag class="resize"
 data-lia-padding-left="{padding-left}"
 data-lia-padding-right="{padding-right}"
 data-lia-padding-top="{padding-top}"
 data-lia-padding-bottom="{padding-bottom}"
 data-lia-margin-left="{margin-left}"
 data-lia-margin-right="{margin-right}"
 data-lia-margin-top="{margin-top}"
 data-lia-margin-bottom="{margin-bottom}"
 data-lia-width="{width}"
 data-lia-height="{height}"
 data-lia-font-size="{font-size}"
 data-lia-top="{top}"
 data-lia-left="{left}"
 data-lia-line-height="{line-height}"
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.adjustResize();
 $(window).resize(function() {
 $.adjustResize();
 });
 });
 */

(function ($) {


    $.extend({

        liaIsResizeBaseOnOnlyWidth: true,
        setResizeBaseOnOnlyWidth: function (isResizeBaseOnOnlyWidth) {
            jQuery.liaIsResizeBaseOnOnlyWidth = isResizeBaseOnOnlyWidth;
        },

        liaResizeBaseWidth: Lia.Component.Value.Resize.DEFAULT_BASE_WIDTH,
        setResizeBaseWidth: function (width) {
            jQuery.liaResizeBaseWidth = width;
        },

        liaResizeBaseHeight: Lia.Component.Value.Resize.DEFAULT_BASE_HEIGHT,
        setResizeBaseHeight: function (height) {
            jQuery.liaResizeBaseHeight = height;
        },

        liaResizeSelector: undefined,
        setResizeSelector: function (selector) {
            jQuery.liaResizeSelector = selector;
        },

        /**
         * 조정
         */
        adjustResize: function (j, jWindow) {

            var selector = '.' + Lia.Component.Name.RESIZE;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            if (jWindow == undefined) {
                j.adjustResize();
            } else {
                j.adjustResize(jWindow);
            }
        }
    });

    $.fn.extend({

        adjustResize: function (jWindow) {

            var jWindow = jWindow == undefined ? (jQuery(jQuery.liaResizeSelector == undefined ? window : jQuery.liaResizeSelector)) : jWindow;
            return this.each(function () {
                var jThis = $(this);
                var deviceWidth = parseFloat(jWindow.width());
                var deviceHeight = parseFloat(jWindow.height());

                var css = {};

                var w = $.liaIsResizeBaseOnOnlyWidth;

                liaSet(jThis, Lia.Component.AttrName.PADDING_LEFT, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.PADDING_RIGHT, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.PADDING_TOP, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.PADDING_BOTTOM, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.MARGIN_LEFT, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.MARGIN_RIGHT, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.MARGIN_TOP, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.MARGIN_BOTTOM, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.WIDTH, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.HEIGHT, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.FONT_SIZE, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.TOP, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.LEFT, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.RIGHT, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BOTTOM, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.LINE_HEIGHT, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_WIDTH, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_TOP_WIDTH, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_BOTTOM_WIDTH, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_LEFT_WIDTH, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_RIGHT_WIDTH, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BORDER_RADIUS, css, deviceWidth, deviceHeight, w);
                liaSet(jThis, Lia.Component.AttrName.BACKGROUND_SIZE, css, deviceWidth, deviceHeight, true);
                liaSet(jThis, Lia.Component.AttrName.MIN_HEIGHT, css, deviceWidth, deviceHeight, w);

                jThis.css(css);
            });
        }

    });


})(jQuery);

function liaSet(j, baseAttrName, css, deviceWidth, deviceHeight, w) {
    var px = j.attr(baseAttrName);
    if (px != undefined)
        css[baseAttrName.replace('lia-', '')] = (parseFloat(px) * (w ? deviceWidth : deviceHeight) / (w ? $.liaResizeBaseWidth : $.liaResizeBaseHeight)) + 'px';
}

/**
 * button
 *
 * 버튼 컴포넌트 공용 모듈
 * ( image_button, image_box, flat_button, flat_button jut )
 */
/*
 $(document).ready(function() {
 $.initButton();
 });
 */

(function ($) {


    $.extend({

        /**
         * 초기화
         */
        initButton: function (j, options) {

            var selector = '.' + Lia.Component.Name.BUTTON;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initButton(options);
        }
    });

    $.fn.extend({

        /**
         * 각 해당 컴포넌트에 맞도록 버튼 상태 세팅 혹은 리턴
         *
         * @param pressed
         * @param isInternalCall
         * @returns {*}
         */
        buttonPressed: function (pressed) {

            if (pressed == undefined)
                return this.hasClass(Lia.Component.Flag.PRESSED);
            else if (pressed)
                this.addClass(Lia.Component.Flag.PRESSED);
            else
                this.removeClass(Lia.Component.Flag.PRESSED);

            return this.checkButtonStatus();
        },

        /**
         * 초기화
         */
        initButton: function () {

            for (var i = 0, l = this.length; i < l; i++) {

                var jEq = this.eq(i);
                if (jEq.hasClass(Lia.Component.Flag.INITED))
                    continue;

                var noBind = jEq.hasClass(Lia.Component.Flag.NO_BIND);
                if (!noBind) {

                    if (Lia.isMobile) {
                        jEq.on('touchstart', liaButtonDown).on('touchend', liaButtonLeave);
                    } else {
                        jEq.on('mousedown', liaButtonDown)
                            .on('mouseup', liaButtonUp)
                            .on('mouseenter', liaButtonEnter)
                            .on('mouseleave', liaButtonLeave);
                    }
                }

                jEq.checkButtonStatus();
                jEq.addClass(Lia.Component.Flag.INITED);
            }

            return this;
        },

        getButtonStatus: function () {

            var status = Lia.Component.Value.Button.Status.DEFAULT;

            var pressing = this.hasClass(Lia.Component.Flag.PRESSING);
            var hovering = this.hasClass(Lia.Component.Flag.HOVERING);
            var pressed = this.hasClass(Lia.Component.Flag.PRESSED);

            if (pressed) {
                status = Lia.Component.Value.Button.Status.PRESSED;
            } else if (pressing) {
                status = Lia.Component.Value.Button.Status.PRESSING;
            } else if (hovering) {
                status = Lia.Component.Value.Button.Status.HOVERING;
            }

            return status;
        },

        checkButtonStatus: function () {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var status = jThis.getButtonStatus();

                var statusChangedEvent = new jQuery.Event(Lia.Component.Event.STATUS_CHANGED);
                statusChangedEvent.status = status;
                jThis.trigger(statusChangedEvent);
            }

            return this;
        }
    });
})(jQuery);


function liaButtonEnter(e) {

    var jThis = $(this);

    var isNoChange = jThis.hasClass(Lia.Component.Flag.NO_CHANGE);
    if (isNoChange)
        return;

    var status = jThis.getButtonStatus();

    jThis.addClass(Lia.Component.Flag.HOVERING);

    if (status == jThis.getButtonStatus())
        return;

    jThis.checkButtonStatus();
}

function liaButtonLeave(e) {

    var jThis = $(this);

    var isNoChange = jThis.hasClass(Lia.Component.Flag.NO_CHANGE);
    if (isNoChange)
        return;

    var status = jThis.getButtonStatus();

    jThis.removeClass(Lia.Component.Flag.PRESSING).removeClass(Lia.Component.Flag.HOVERING);

    if (status == jThis.getButtonStatus())
        return;

    jThis.checkButtonStatus();
}

function liaButtonDown(e) {

    var jThis = $(this);

    var isNoChange = jThis.hasClass(Lia.Component.Flag.NO_CHANGE);
    if (isNoChange)
        return;

    var status = jThis.getButtonStatus();

    jThis.addClass(Lia.Component.Flag.PRESSING);

    if (status == jThis.getButtonStatus())
        return;

    jThis.checkButtonStatus();
}

function liaButtonUp(e) {

    var jThis = $(this);

    var isNoChange = jThis.hasClass(Lia.Component.Flag.NO_CHANGE);
    if (isNoChange)
        return;

    var status = jThis.getButtonStatus();

    jThis.removeClass(Lia.Component.Flag.PRESSING);

    if (status == jThis.getButtonStatus())
        return;

    jThis.checkButtonStatus();
}


var DateHelper = jQuery.DateHelper = Lia.DateHelper = {

    FORMAT_YY_MM_DD_HH_mm_ss: 'yyyy-MM-dd HH:mm:ss',
    FORMAT_YY_MM_DD: 'yyyy-MM-dd',

    getDateObject: function (text) {

        if (typeof text == 'string') {
            return Date.parse(text);
        } else {
            return text;
        }
    },

    dateStringToYY_MM_DD: function (text, defaultString) {

        if (String.isBlank(text))
            return defaultString;


        if (text.length < 10) {
            return defaultString;
        }


        return text.substr(0, 10);
    },

    secToHH_MM_SS: function (sec) {

        if (String.isBlank(sec)) {
            return '00:00:00';
        }

        var h = Math.floor(sec / 3600);
        sec = sec % 3600;
        var m = Math.floor(sec / 60);
        sec = sec % 60;

        if (h <= 9)
            h = '0' + h;

        if (m <= 9)
            m = '0' + m;

        if (sec <= 9)
            sec = '0' + sec;

        return h + ':' + m + ":" + sec;
    },

    secToMM_SS: function (sec) {

        if (String.isBlank(sec)) {
            return '00:00';
        }

        var h = Math.floor(sec / 3600);
        sec = sec % 3600;
        var m = Math.floor(sec / 60);
        sec = sec % 60;

        if (m <= 9) {
            m = '0' + m;
        }

        if (sec <= 9) {
            sec = '0' + sec;
        }

        var timeString = '';
        if (h > 0) {
            timeString += h;
        }

        if (String.isNotBlank(timeString)) {
            timeString += ':';
        }

        timeString += m + ':' + sec;
        return timeString;
    },

    hourToMills : function( hour ) {

        return hour * 60 * 60 * 1000;
    },

    getDayString : function( day, locale ) {

        var dayStringList = [
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_SUNDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_MONDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_TUESDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_WEDNESDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_THURSDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_FRIDAY, locale),
            Lia.Strings.getString(Lia.Strings.CALENDAR.CALENDAR_SATURDAY, locale)
        ];

        return dayStringList[day];
    }

};

var FormatHelper = jQuery.FormatHelper = Lia.FormatHelper = {

    phoneNumber: function (num) {

        if (String.isBlank(num)) {
            return undefined;
        }

        var formatNum = undefined;

        num = num.replace(/-/g, '');
        if (num.length == 11) {
            formatNum = num.replace(/([0-9*]{3})([0-9*]{4})([0-9*]{4})/, '$1-$2-$3');
        } else if (num.length == 8) {
            formatNum = num.replace(/([0-9*]{4})([0-9*]{4})/, '$1-$2');
        } else {
            if (num.indexOf('02') == 0) {

                if (num.length == 9) {
                    formatNum = num.replace(/([0-9*]{2})([0-9*]{3})([0-9*]{4})/, '$1-$2-$3');
                } else if (num.length == 10) {
                    formatNum = num.replace(/([0-9*]{2})([0-9*]{4})([0-9*]{4})/, '$1-$2-$3');
                }

            } else {

                if (num.length == 10) {
                    formatNum = num.replace(/([0-9*]{3})([0-9*]{3})([0-9*]{4})/, '$1-$2-$3');
                }
            }
        }

        return formatNum;
    },

    toPrice: function (number) {

        if (number == undefined || isNaN(number))
            return;

        var num = parseInt(number);
        var len, point, str;

        num = num + "";
        point = num.length % 3;
        len = num.length;

        str = num.substring(0, point);
        while (point < len) {
            if (str != "") str += ",";
            str += num.substring(point, point + 3);
            point += 3;
        }

        return str;
    },


    toCamel: function (item) {
        return item.replace(/[-_]([a-z])/g, function (a) {
            return a[1].toUpperCase();
        })
    },

    toUnderscore: function (item) {
        return item.replace(/([A-Z])/g, function (a) {
            return '_' + a[0].toLowerCase();
        })
    },

    arrayKeyToUnderscore: function (item) {

        var r = {};
        for (var key in item) {
            r[Lia.FormatHelper.toUnderscore(key)] = item[key];
        }

        return r;
    },

    arrayKeyToCamel: function (item) {

        var r = {};
        for (var key in item) {
            r[Lia.FormatHelper.toCamel(key)] = item[key];
        }

        return r;
    },

    numberWithCommas: function (x) {

        if (x == undefined || isNaN(x)) {
            return;
        }

        return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }
};


var SubtitleHelper = jQuery.SubtitleHelper = Lia.SubtitleHelper = {


    extractText: function (list, sec) {

        var text = "";

        if (Array.isEmpty(list)) {
            return text;
        }

        for (var i = 0, l = list.length; i < l; i++) {
            var item = list[i];

            var currentStartTime = item.startTime;
            var currentEndTime = Lia.pd(Lia.p(list, i + 1, 'startTime'), item.endTime);
            var currentLine = item.text;

            if (currentStartTime <= sec && ((currentEndTime != undefined && sec < currentEndTime) || currentEndTime == undefined)) {
                text = currentLine;
                break;
            }
        }

        return text;
    },

    parseSmi: function (data) {

        var list = [];

        if (String.isBlank(data)) {
            return list;
        }

        var lines = data.split('\n');

        var bodyStart = false;

        for (var i = 0, l = lines.length; i < l; i++) {

            var line = lines[i];
            var upperCaseLine = line.trim().toUpperCase();

            if (bodyStart == false) {

                if (upperCaseLine == '<BODY>') {
                    bodyStart = true;
                }
                continue;
            }

            if (upperCaseLine == "</BODY>") {
                break;
            }

            if (upperCaseLine.startsWith('<SYNC')) {

                var syncTag = upperCaseLine.substr(0, upperCaseLine.indexOf('>'));
                var startTime = syncTag.substr(syncTag.indexOf('=') + 1);

                var text = '';
                var i2 = 1;

                while (true) {

                    var orignalLine = lines[i + i2].trim();
                    var upperCaseNextLine = lines[i + i2].trim().toUpperCase();
                    if (upperCaseNextLine.startsWith('<SYNC') || String.isBlank(upperCaseNextLine) || upperCaseNextLine == '</BODY>') {
                        break;
                    }

                    orignalLine = orignalLine.replace(/\s*(<br ?\/>\s*)+/g, "<br />").replace(/^<br>|<br \/>|<br \/>$/gi, "");

                    if (String.isNotBlank(text))
                        text += '<BR/>';

                    text += orignalLine;
                    i2++;
                }

                i += i2;

                list.push({startTime: startTime, endTime: undefined, text: text});
            }
        }

        // 정렬
        for (var i = 0, l = list.length; i < l; i++) {
            for (var j = i + 1; j < l; j++) {

                var item1 = list[i];
                var item2 = list[j];

                if (i > j) {
                    list[j] = item1;
                    list[i] = item2;
                }
            }
        }

        return list;
    },

    SRT_NUMBER_INDEX: 0,
    SRT_TIME_INDEX: 1,
    SRT_TEXT_INDEX: 2,

    parseSrt: function (data) {

        var list = [];
        if (String.isBlank(data)) {
            return list;
        }

        var lines = data.split('\n');

        var startTime = null;
        var endTime = null;
        var text = null;
        var index = Lia.SubtitleHelper.SRT_NUMBER_INDEX;

        for (var key in lines) {

            var line = lines[key];

            if (index == Lia.SubtitleHelper.SRT_NUMBER_INDEX) {

                // 공백이면 스킵
                if (!String.isNullOrWhitespace(line)) {
                    index = Lia.SubtitleHelper.SRT_TIME_INDEX;
                }


            } else if (index == Lia.SubtitleHelper.SRT_TIME_INDEX) {

                var items = line.split('-->');

                var startTimeString = items[0].trim();
                var startHour = parseInt(startTimeString.substr(0, 2));
                var startMin = parseInt(startTimeString.substr(3, 2));
                var startSec = parseInt(startTimeString.substr(6, 2));
                var startMs = parseInt(startTimeString.substr(9, 3));
                startTime = startHour * 60 * 60 * 1000 + startMin * 60 * 1000 + startSec * 1000 + startMs;

                var endTimeString = items[1].trim();
                var endHour = parseInt(endTimeString.substr(0, 2));
                var endMin = parseInt(endTimeString.substr(3, 2));
                var endSec = parseInt(endTimeString.substr(6, 2));
                var endMs = parseInt(endTimeString.substr(9, 3));
                endTime = endHour * 60 * 60 * 1000 + endMin * 60 * 1000 + endSec * 1000 + endMs;

                index = Lia.SubtitleHelper.SRT_TEXT_INDEX;


            } else if (index == Lia.SubtitleHelper.SRT_TEXT_INDEX) {

                if (String.isNullOrWhitespace(line)) {

                    if (startTime != null && endTime != null && text != null) {
                        list.push({startTime: startTime, endTime: endTime, text: text});
                    }

                    index = Lia.SubtitleHelper.SRT_NUMBER_INDEX;
                    startTime = null;
                    endTime = null;
                    text = null;

                } else {

                    if (text == null)
                        text = line.trim();
                    else {
                        text += "<br/>";
                        text += line.trim();
                    }

                }
            }
        }

        if (startTime != null && endTime != null && text != null) {
            list.push({startTime: startTime, endTime: endTime, text: text});
        }

        for (var i = 0, l = list.length; i < l; i++) {
            for (var j = i + 1; j < l; j++) {

                var item1 = list[i];
                var item2 = list[j];

                if (i > j) {
                    list[j] = item1;
                    list[i] = item2;
                }
            }
        }

        return list;
    }
};


var CookieHelper = jQuery.CookieHelper = Lia.CookieHelper = {

    set: function (key, value, days) {

        if (days == undefined) {
            days = 365 * 3;
        }

        $.cookie(key, value, {expires: days, path: '/'});
    },

    get: function (key) {
        return jQuery.cookie(key);
    },

    remove: function (key) {
        jQuery.removeCookie(key, {path: '/'});
    }
};


var IFrameManager = jQuery.IFrameManager = Lia.IFrameManager = {

    listenerList: [],
    addListener: function (func, object) {
        Lia.IFrameManager.listenerList.push({
            func: func,
            object: object
        });
    },
    removeListener: function (func) {

        for (var i = Lia.IFrameManager.listenerList.length; i--;) {
            if (Lia.IFrameManager.listenerList[i]['func'] === func) {
                Lia.IFrameManager.listenerList.splice(i, 1);
            }
        }
    },
    message: function (key, type, object) {

        for (var i = 0, l = Lia.IFrameManager.listenerList.length; i < l; i++) {

            var func = Lia.p(Lia.IFrameManager.listenerList[i], 'func');
            var passedObject = Lia.p(Lia.IFrameManager.listenerList[i], 'object');
            func(key, type, object, passedObject);
        }
    },
    parentMessage: function (key, type, object) {

        parent.Lia.IFrameManager.message(key, type, object);
    },

    execute: function (name, funcName, object) {

        try {

            var frame = frames[name];
            var func = frame[funcName];
            func(object);

        } catch (e) {
        }
    }
};


var YouTubeHelper = jQuery.YouTubeHelper = Lia.YouTubeHelper = {


    getEmbedUrl: function (url) {

        var id = Lia.YouTubeHelper.extractId(url);
        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://www.youtube.com/embed/' + id;
    },

    getThumbnailUrl: function (url, quality) {

        // 유튜브에서 제공하는 해상도 옵션
        // (320x180) mqdefault
        // (480x360) hqdefault (기본값)
        // (640x480) sddefault
        // (120x90) default
        // (1280x720 또는 1920x1080) maxresdefault

        var id = Lia.YouTubeHelper.extractId(url);
        var thumbQuality = Lia.pcd('hqdefault', quality);

        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://img.youtube.com/vi/' + id + '/' + thumbQuality + '.jpg';
    },

    extractId: function (url) {

        // https://youtu.be/vgwq5cckZaI
        // https://www.youtube.com/embed/vgwq5cckZaI
        // https://www.youtube.com/watch?v=vgwq5cckZaI&feature=youtu.be

        var regExp = /http(s)?:\/\/(www\.)?(youtu\.be|youtube\.com|)\//;
        var match = url.match(regExp);
        if (Array.isEmpty(match)) {
            return undefined;
        }

        var pm = Lia.extractGetParameterMapFromUrl(url);

        var id = Lia.p(pm, 'v');
        if (String.isNotBlank(id)) {
            return id;
        }

        var baseUrl = url;
        var parameterIdx = url.lastIndexOf('?');
        if (parameterIdx >= 0) {
            baseUrl = url.substr(0, parameterIdx);
        }

        var idx = baseUrl.lastIndexOf('/');
        return baseUrl.substr(idx + 1);
    }
};

var TedHelper = jQuery.TedHelper = Lia.TedHelper = {

    getEmbedUrl: function (url) {

        var id = Lia.TedHelper.extractId(url);
        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://embed.ted.com/talks/' + id;
    },

    getThumbnailUrl: function (url, quality) {

        var id = Lia.TedHelper.extractId(url);
        var thumbQuality = Lia.pcd('hqdefault', quality);

        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://img.youtube.com/vi/' + id + '/' + thumbQuality + '.jpg';
    },

    extractId: function (url) {

        // https://www.ted.com/talks/simon_sinek_how_to_discover_your_why_in_difficult_times?utm_campaign=tedspread&utm_medium=referral&utm_source=tedcomshare

        var regExp = /http(s)?:\/\/(www\.)?(ted\.com|)\//;
        var match = url.match(regExp);
        if (Array.isEmpty(match)) {
            return undefined;
        }

        var baseUrl = url;
        var parameterIdx = url.lastIndexOf('?');
        if (parameterIdx >= 0) {
            baseUrl = url.substr(0, parameterIdx);
        }

        var idx = baseUrl.lastIndexOf('/');
        return baseUrl.substr(idx + 1);
    }
};

var PreziHelper = jQuery.PreziHelper = Lia.PreziHelper = {

    getEmbedUrl: function (url) {

        // https://prezi.com/v/embed/v3u8z2zjaysw/

        var id = Lia.PreziHelper.extractId(url);
        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://prezi.com/v/embed/v3u8z2zjaysw/' + id + '/';
    },

    getThumbnailUrl: function (url, quality) {

        var id = Lia.PreziHelper.extractId(url);
        var thumbQuality = Lia.pcd('hqdefault', quality);

        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://img.youtube.com/vi/' + id + '/' + thumbQuality + '.jpg';
    },

    extractId: function (url) {

        // https://prezi.com/v/v3u8z2zjaysw/eid-learning-plans/

        var regExp = /http(s)?:\/\/(www\.)?(prezi\.com|)\//;
        var match = url.match(regExp);
        if (Array.isEmpty(match)) {
            return undefined;
        }

        var path = url.substring(20);
        var id = path.split('/')[0];

        return id;
    }
};

var VimeoHelper = jQuery.VimeoHelper = Lia.VimeoHelper = {

    getEmbedUrl: function (url) {

        var id = Lia.VimeoHelper.extractId(url);
        if (String.isBlank(id)) {
            id = url;
        }

        return 'https://player.vimeo.com/video/' + id;
    },

    extractId: function (url) {

        var regExp = /(vimeo(pro)?\.com)\/(?:[^\d]+)?(\d+)\??(.*)?$/;
        var match = url.match(regExp);
        return Lia.p(match, 3);
    }
};


var GoogleChartHelper = jQuery.GoogleChartHelper = Lia.GoogleChartHelper = {

    loaded: false,
    func: undefined,
    object: undefined,

    init: function (options) {

        var packages = Lia.pd(['bar'], options, 'packages');
        google.load('visualization', '1.1', {'packages': packages});

        google.setOnLoadCallback(function () {
            Lia.GoogleChartHelper.loaded = true;
        });
    },

    draw: function (func, object) {

        Lia.GoogleChartHelper.func = func;
        Lia.GoogleChartHelper.object = object;
        Lia.GoogleChartHelper.loop();

    },

    loop: function () {

        if (Lia.GoogleChartHelper.loaded) {
            Lia.GoogleChartHelper.func(Lia.GoogleChartHelper.object);
        } else {
            setTimeout(function () {
                Lia.GoogleChartHelper.loop();
            }, 10);
        }
    }
};


var LoadingPopupManager = jQuery.LoadingPopupManager = Lia.LoadingPopupManager = {
    init: function (j) {
        jQuery.initDim(j);
        jQuery.initPopup(j);
        jQuery.initPopupLoading(j);
    },

    show: function (j) {
        jQuery.showPopupLoading(j);
    },

    hide: function (j) {
        jQuery.hidePopupLoading(j);
    },

    clear: function (j) {
        jQuery.clearAndHidePopupLoading(j);
    }
};


var FileHelper = jQuery.FileHelper = Lia.FileHelper = {


    /**
     * 파일 확장자 추출
     * 추출할 수 없으면 null
     *
     * @param file
     * @returns {*}
     */
    extractFileExt: function (file) {

        if (String.isNullOrWhitespace(file))
            return null;

        var len = file.length;
        var last = file.lastIndexOf('.');
        if (last == -1)
            return null;

        var ext = file.substring(last, len);
        ext = ext.toLowerCase();

        return ext;
    },

    /**
     * 파일 확장자 추출 ( .빼고 )
     * 추출할 수 없으면 null
     *
     * @param file
     * @returns {*}
     */
    extractFileExtOnly: function (file) {

        if (String.isNullOrWhitespace(file))
            return null;

        var len = file.length;
        var last = file.lastIndexOf('.');
        if (last == -1)
            return null;

        var ext = file.substring(last + 1);
        ext = ext.toLowerCase();

        return ext;
    },


    /**
     * 파일 이름 추출
     * 추출할 수 없으면 null
     *
     * @param file
     * @returns {*}
     */
    extractFilename: function (file) {

        if (String.isNullOrWhitespace(file))
            return null;

        var len = file.length;
        var last = file.lastIndexOf('/');
        if (last == -1) {
            last = file.lastIndexOf("\\");
            if (last == -1)
                return null;
        }

        var filename = file.substring(last + 1, len);
        return filename;
    },

    isFile: function (url, extList) {

        var ext = FileHelper.extractFileExtOnly(url);
        if (String.isBlank(ext)) {
            return false;
        }

        ext = ext.toLowerCase();

        var isFile = false;
        for (var i = 0, l = extList.length; i < l; i++) {
            var extItem = extList[i];
            if (extItem == ext) {
                isFile = true;
                break;
            }
        }

        return isFile;
    },


    isImageFile: function (url) {
        return FileHelper.isFile(url, ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'svg']);
    },

    isPdfFile: function (url) {
        return FileHelper.isFile(url, ['pdf']);
    },

    isOfficeFile: function (url) {
        return FileHelper.isFile(url, ['doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx' ]);
    },

    isAudioFile: function (url) {
        return FileHelper.isFile(url, ['mp3', 'wav', 'ogg']);
    },

    isVideoFile: function (url) {
        return FileHelper.isFile(url, ['mp4', 'avi', 'mov', 'mkv', 'wmv']);
    }

};


// content_slider_item_container :  실제 이동 부 틀
// content_slider_item : 실제 이동 부
// content_slider_left_button :  왼쪽으로
// content_slider_right_button 오른쪽으로
// page.onChange

// <div class="content_slider" style="display:none;">
//
//     <div class="content_slider_left_button">
//         <img src="/res/lms/img/study/main/arr_bookmark_prev.png" />
//     </div>
//
//     <div class="memo_section_list_contents content_slider_item_container" style="height:80px;">
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//          <div class="content_slider_item"></div>
//     </div>
//
//     <div class="content_slider_right_button">
//         <img src="/res/lms/img/study/main/arr_bookmark_next.png" />
//     </div>
//
// </div>

// page.contentSlider = new jQuery.ContentSlider({
//     j: page.find('.page_home_banner'),
//     loopTime: 5000,
//     count: function (width) {
//         return 1;
//     },
//     onChange : function( currentIndex ) {}
// });
//
// page.contentSlider.startLoop();


var ContentSlider = jQuery.ContentSlider = Lia.ContentSlider = function (options) {
    this.init(options);
};

Lia.ContentSlider.prototype.init = function (options) {

    var page = this;

    page.options = options;
    page.jContentSlider = Lia.p(options, 'j');

    page.easing = Lia.pd('easeInOutExpo', options, 'easing');
    page.count = Lia.pd(1, options, 'count');
    page.onChange = Lia.p(options, 'onChange');

    page.loopTime = Lia.pd(10000, options, 'loopTime');
    page.currentIndex = -1;
    page.timer = undefined;

    page.jContainer = page.jContentSlider.find('.content_slider_item_container').css({
        'position': 'relative',
        'top': '0',
        'left': '0',
        'overflow': 'hidden'
    });

    page.jContentSliderItemList = page.jContentSlider.find('.content_slider_item');
    page.jContentSliderItemList.css({
        'position': 'absolute',
        'top': '0'
    });

    page.jLeftButton = page.jContentSlider.find('.content_slider_left_button').off('click.content_slider').on('click.content_slider', function () {
        page.prev();
    }).hide();

    page.jRightButton = page.jContentSlider.find('.content_slider_right_button').off('click.content_slider').on('click.content_slider', function () {
        page.next();
    }).hide();


    page.onResize();
};

Lia.ContentSlider.prototype.onResize = function () {

    var page = this;

    var currentIndex = page.currentIndex;
    page.currentIndex = -1;

    if (currentIndex == -1) {
        currentIndex = 0;
    }

    page.index(currentIndex);
};

Lia.ContentSlider.prototype.index = function (index, backward) {

    var page = this;
    if (index == undefined) {
        return page.currentIndex;
    }

    var sliderWidth = page.jContainer.width();
    var sliderHeight = page.jContainer.height();

    page.jContentSliderItemList.stop();

    var itemCount = 1;
    if (typeof page.count == 'function') {
        itemCount = page.count(sliderWidth, sliderHeight, page);
    } else {
        itemCount = page.count;
    }

    var contentCount = page.jContentSliderItemList.length;

    var full = (contentCount <= itemCount);
    if (full) {
        page.jLeftButton.hide();
        page.jRightButton.hide();

        if (page.currentIndex != -1) {
            index = page.currentIndex;
        }

    } else {
        page.jLeftButton.show();
        page.jRightButton.show();
    }

    var delta = index;
    if (page.currentIndex != -1 && !full) {

        if (backward) {
            delta = index + 1;
        } else {
            delta = index - 1;
        }
    }

    var itemSliderWidth = sliderWidth / itemCount;

    var left = 0;
    for (var i = 0, l = contentCount; i < l; i++) {

        var jjBannerSliderItem = page.jContentSliderItemList.eq((i + delta + l) % l);

        if (backward && i == l - 1) {

            jjBannerSliderItem.css({
                width: itemSliderWidth + 'px',
                left: (-1 * itemSliderWidth) + 'px'
            });

        } else {

            jjBannerSliderItem.css({
                width: itemSliderWidth + 'px',
                left: left + 'px'
            });

            left += itemSliderWidth;
        }
    }

    if (!full) {

        if (page.currentIndex != -1 && backward) {

            page.jContentSliderItemList.animate({
                left: '+=' + itemSliderWidth + 'px'
            }, {
                easing: page.easing,
                duration: 500
            });

        } else if (page.currentIndex != -1) {

            page.jContentSliderItemList.animate({
                left: '-=' + itemSliderWidth + 'px'
            }, {
                easing: page.easing,
                duration: 500
            });
        }
    }

    var beforeIndex = page.currentIndex;
    page.currentIndex = index;

    if (page.onChange != undefined) {
        page.onChange(index, beforeIndex);
    }
};


Lia.ContentSlider.prototype.getContainerWidth = function () {

    var page = this;
    if (page.jContainer == undefined) {
        return undefined;
    }

    return page.jContainer.width();
};


Lia.ContentSlider.prototype.getContainerHeight = function () {

    var page = this;
    if (page.jContainer == undefined) {
        return undefined;
    }

    return page.jContainer.height();
};


Lia.ContentSlider.prototype.next = function () {

    var page = this;

    var index = page.currentIndex;
    if (index == -1) {
        index = 0;
    } else {
        ++index;
    }

    var count = page.jContentSliderItemList.length;
    index = (index + count) % count;

    if (page.isLooping()) {
        page.stopTimer();
        page.index(index);
        page.startTimer();
    } else {
        page.index(index);
    }
};

Lia.ContentSlider.prototype.prev = function () {

    var page = this;

    var index = page.currentIndex;
    if (index == -1) {
        index = 0;
    } else {
        --index;
    }

    var count = page.jContentSliderItemList.length;
    index = (index + count) % count;


    if (page.isLooping()) {
        page.stopTimer();
        page.index(index, true);
        page.startTimer();
    } else {
        page.index(index, true);
    }
};


Lia.ContentSlider.prototype.isLooping = function () {

    var page = this;
    return (page.timer != undefined);
};

Lia.ContentSlider.prototype.startLoop = function () {

    var page = this;
    page.startTimer();

    if (page.currentIndex == -1)
        page.index(0);
};

Lia.ContentSlider.prototype.stopLoop = function () {

    var page = this;
    page.stopTimer();
};

Lia.ContentSlider.prototype.startTimer = function () {

    var page = this;
    page.stopTimer();

    page.timer = window.setInterval(function () {
        page.next();
    }, page.loopTime);
};

Lia.ContentSlider.prototype.stopTimer = function () {

    var page = this;
    if (page.timer != undefined) {
        window.clearInterval(page.timer);
        page.timer = undefined;
    }
};

Lia.ContentSlider.prototype.release = function () {

    var page = this;
    page.stopTimer();
};


var ContentSwitcher = jQuery.ContentSwitcher = Lia.ContentSwitcher = function (options) {
    this.init(options);
};

Lia.ContentSwitcher.TYPE_FADE = 1;
Lia.ContentSwitcher.TYPE_SCALE_FADE = 2;

Lia.ContentSwitcher.prototype.init = function (options) {

    var page = this;

    page.options = options;
    page.jContentSwitcher = Lia.p(options, 'j');

    page.type = Lia.pcd(Lia.ContentSwitcher.TYPE_FADE, options, 'type');
    page.duration = Lia.pd(500, options, 'duration');
    page.easing = Lia.pd('swing', options, 'easing');
    page.onChange = Lia.p(options, 'onChange');

    page.loopTime = Lia.pd(10000, options, 'loopTime');
    page.currentIndex = -1;
    page.timer = undefined;

    page.jContainer = page.jContentSwitcher.find('.content_switcher_item_container').css({});

    page.jContentSwitcherItemList = page.jContentSwitcher.find('.content_switcher_item');
    page.jContentSwitcherItemList.hide();

    page.jLeftButton = page.jContentSwitcher.find('.content_switcher_left_button').off('click.content_switcher').on('click.content_switcher', function () {
        page.prev();
    }).hide();

    page.jRightButton = page.jContentSwitcher.find('.content_switcher_right_button').off('click.content_switcher').on('click.content_switcher', function () {
        page.next();
    }).hide();
};


Lia.ContentSwitcher.prototype.index = function (index) {

    var page = this;
    if (index == undefined) {
        return page.currentIndex;
    }

    page.jContentSwitcherItemList.stop();

    var contentCount = page.jContentSwitcherItemList.length;
    if (contentCount == 0) {
        page.jLeftButton.hide();
        page.jRightButton.hide();
    } else {
        page.jLeftButton.show();
        page.jRightButton.show();
    }

    var beforeIndex = page.currentIndex;
    if ( page.type == Lia.ContentSwitcher.TYPE_FADE ) {

        if (beforeIndex == -1) {

            page.jContentSwitcherItemList.eq(index).css({
                'opacity': 1
            }).show();

        } else {

            page.jContentSwitcherItemList.eq(beforeIndex).animate({
                'opacity': 0
            }, {
                easing: page.easing,
                duration: page.duration,
                complete: function () {
                    $(this).hide();
                }
            }).show();

            page.jContentSwitcherItemList.eq(index).css({
                opacity: 0
            }).animate({
                'opacity': 1
            }, {
                easing: page.easing,
                duration: page.duration,
                complete: function () {
                }
            }).show();
        }

    } else if ( page.type == Lia.ContentSwitcher.TYPE_SCALE_FADE ) {

        if (beforeIndex == -1) {

            page.jContentSwitcherItemList.eq(index).css({
                'opacity': 1,
                'transform' : 'scale(1)'
            }).show();

        } else {

            page.jContentSwitcherItemList.eq(beforeIndex).css({
                'transform' : 'scale(1.5)',
                'transition' : 'transform '+page.duration+'ms'
            });

            page.jContentSwitcherItemList.eq(beforeIndex).animate({
                'opacity': 0
            }, {
                easing: page.easing,
                duration: page.duration,
                complete: function () {

                    var jThis = $(this);
                    jThis.hide();

                }
            }).show();

            page.jContentSwitcherItemList.eq(index).css({
                'transform' : 'scale(1)',
                'transition' : ''
            });

            page.jContentSwitcherItemList.eq(index).css({
                opacity: 0
            }).animate({
                'opacity': 1
            }, {
                easing: page.easing,
                duration: page.duration,
                complete: function () {
                }
            }).show();
        }

    }



    page.currentIndex = index;

    if (page.onChange != undefined) {
        page.onChange(index, beforeIndex, contentCount);
    }
};

Lia.ContentSwitcher.prototype.next = function () {

    var page = this;

    var index = page.currentIndex;
    if (index == -1) {
        index = 0;
    } else {
        ++index;
    }

    var count = page.jContentSwitcherItemList.length;
    index = (index + count) % count;

    if (page.isLooping()) {
        page.stopTimer();
        page.index(index);
        page.startTimer();
    } else {
        page.index(index);
    }
};

Lia.ContentSwitcher.prototype.prev = function () {

    var page = this;

    var index = page.currentIndex;
    if (index == -1) {
        index = 0;
    } else {
        --index;
    }

    var count = page.jContentSwitcherItemList.length;
    index = (index + count) % count;


    if (page.isLooping()) {
        page.stopTimer();
        page.index(index, true);
        page.startTimer();
    } else {
        page.index(index, true);
    }
};


Lia.ContentSwitcher.prototype.isLooping = function () {

    var page = this;
    return (page.timer != undefined);
};

Lia.ContentSwitcher.prototype.startLoop = function () {

    var page = this;
    page.startTimer();

    if (page.currentIndex == -1)
        page.index(0);
};

Lia.ContentSwitcher.prototype.stopLoop = function () {

    var page = this;
    page.stopTimer();
};

Lia.ContentSwitcher.prototype.startTimer = function () {
    var page = this;
    page.stopTimer();

    page.timer = window.setInterval(function () {
        page.next();
    }, page.loopTime);
};

Lia.ContentSwitcher.prototype.stopTimer = function () {

    var page = this;
    if (page.timer != undefined) {
        window.clearInterval(page.timer);
        page.timer = undefined;
    }
};

Lia.ContentSwitcher.prototype.release = function () {
    var page = this;
    page.stopTimer();
};


/**
 *  ajax 호출
 **/

jQuery.Requester = Lia.Requester = function (parameter) {
    this.init(parameter);
};

Lia.Requester.DefaultRequestValue = function (parameterMap) {

    this.cache = Lia.Requester.DefaultRequestValue.cache;
    this.cacheVersion = Lia.Requester.DefaultRequestValue.cacheVersion;

    this.sync = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_SYNC;
    this.dataType = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_DATA_TYPE;
    this.method = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_METHOD;
    this.q = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_Q;
    this.noExecuteOnResponseWhenError = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_NO_EXECUTE_ON_RESPONSE_WHEN_ERROR;
    this.xhrFields = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_XHR_FIELDS;
    this.timeout = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_TIMEOUT;
    this.timeoutWithSubmit = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_TIMEOUT_WITH_SUBMIT;

    if (parameterMap != undefined) {

        var sync = parameterMap['sync'];
        if (sync != undefined) {
            this.sync = sync;
        }

        var dataType = parameterMap['dataType'];
        if (dataType != undefined) {
            this.dataType = dataType;
        }

        var xhrFields = parameterMap['xhrFields'];
        if (xhrFields != undefined) {
            this.xhrFields = xhrFields;
        }

        var method = parameterMap['method'];
        if (method != undefined) {
            this.method = method;
        }

        var q = parameterMap['q'];
        if (q != undefined) {
            this.q = q;
        }

        var cache = parameterMap['cache'];
        if (cache != undefined) {
            this.cache = cache;
        }

        var cacheVersion = parameterMap['cacheVersion'];
        if (cacheVersion != undefined) {
            this.cacheVersion = cacheVersion;
        }

        var timeout = parameterMap['timeout'];
        if (timeout != undefined) {
            this.timeout = timeout;
        }

        var timeoutWithSubmit = parameterMap['timeoutWithSubmit'];
        if (timeoutWithSubmit != undefined) {
            this.timeoutWithSubmit = timeoutWithSubmit;
        }

        var noExecuteOnResponseWhenError = parameterMap['noExecuteOnResponseWhenError'];
        if (noExecuteOnResponseWhenError != undefined) {
            this.noExecuteOnResponseWhenError = q;
        }
    }
};


Lia.Requester.DefaultRequestValue.cache = Lia.Component.Value.Requester.DefaultRequestValue.DEFAULT_CACHE;
Lia.Requester.DefaultRequestValue.setCache = function (cache) {
    Lia.Requester.DefaultRequestValue.cache = cache;
};

Lia.Requester.DefaultRequestValue.cacheVersion = undefined;
Lia.Requester.DefaultRequestValue.setCacheVersion = function (cacheVersion) {
    Lia.Requester.DefaultRequestValue.cacheVersion = cacheVersion;
};


Lia.Requester.DefaultRequestValue.prototype.setCache = function (cache) {
    this.cache = cache;
};
Lia.Requester.DefaultRequestValue.prototype.getCache = function () {
    return this.cache;
};

Lia.Requester.DefaultRequestValue.prototype.setCacheVersion = function (cacheVersion) {
    this.cacheVersion = cacheVersion;
};
Lia.Requester.DefaultRequestValue.prototype.getCacheVersion = function () {
    return this.cacheVersion;
};

Lia.Requester.DefaultRequestValue.prototype.setQ = function (q) {
    this.q = q;
};
Lia.Requester.DefaultRequestValue.prototype.getQ = function () {
    return this.q;
};

Lia.Requester.DefaultRequestValue.prototype.getXhrFields = function () {
    return this.xhrFields;
};
Lia.Requester.DefaultRequestValue.prototype.setXhrFields = function (xhrFields) {
    this.xhrFields = xhrFields;
};

Lia.Requester.DefaultRequestValue.prototype.setMethod = function (method) {
    this.method = method;
};
Lia.Requester.DefaultRequestValue.prototype.getMethod = function () {
    return this.method;
};

Lia.Requester.DefaultRequestValue.prototype.setSync = function (sync) {
    this.sync = sync;
};
Lia.Requester.DefaultRequestValue.prototype.getSync = function () {
    return this.sync;
};

Lia.Requester.DefaultRequestValue.prototype.setTimeout = function (timeout) {
    this.timeout = timeout;
};
Lia.Requester.DefaultRequestValue.prototype.getTimeout = function () {
    return this.timeout;
};

Lia.Requester.DefaultRequestValue.prototype.setTimeoutWithSubmit = function (timeout) {
    this.timeoutWithSubmit = timeout;
};
Lia.Requester.DefaultRequestValue.prototype.getTimeoutWithSubmit = function () {
    return this.timeoutWithSubmit;
};

Lia.Requester.DefaultRequestValue.prototype.setDataType = function (dataType) {
    this.dataType = dataType;
};
Lia.Requester.DefaultRequestValue.prototype.getDataType = function () {
    return this.dataType;
};
Lia.Requester.DefaultRequestValue.prototype.setNoExecuteOnResponseWhenError = function (noExecuteOnResponseWhenError) {
    this.noExecuteOnResponseWhenError = noExecuteOnResponseWhenError;
};
Lia.Requester.DefaultRequestValue.prototype.getNoExecuteOnResponseWhenError = function () {
    return this.noExecuteOnResponseWhenError;
};

Lia.Requester.Status = Lia.Component.Value.Requester.Status;
Lia.Requester.Type = Lia.Component.Value.Requester.Type;
Lia.Requester.XhrStatus = Lia.Component.Value.Requester.XhrStatus;
Lia.Requester.HttpStatus = Lia.Component.Value.Requester.HttpStatus;

Lia.Requester.prototype.init = function (parameter) {

    this.defaultRequestValue = new Lia.Requester.DefaultRequestValue(parameter);
    this.requesting = false;
    this.queue = new Lia.Queue();
    this.queueXhr = undefined;

    this.Status = Lia.Requester.Status;
    this.isProgressSupported = Lia.Requester.isProgressSupported;

    if (parameter != undefined) {

        var responseCheckHandler = parameter['responseCheckHandler'];
        if (responseCheckHandler != undefined) {
            this.responseCheckHandler = responseCheckHandler;
        }

        var responseDataHandler = parameter['responseDataHandler'];
        if (responseDataHandler != undefined) {
            this.responseDataHandler = responseDataHandler;
        }

        var onPreRequest = parameter['onPreRequest'];
        if (onPreRequest != undefined) {
            this.onPreRequest = onPreRequest;
        }

        var onRequestEnded = parameter['onRequestEnded'];
        if (onRequestEnded != undefined) {
            this.onRequestEnded = onRequestEnded;
        }

        var onRequestStart = parameter['onRequestStart'];
        if (onRequestStart != undefined) {
            this.onRequestStart = onRequestStart;
        }

        // 기본 값
        var noExecuteOnResponseWhenError = parameter['noExecuteOnResponseWhenError'];
        if (noExecuteOnResponseWhenError != undefined) {
            this.defaultRequestValue.setNoExecuteOnResponseWhenError(noExecuteOnResponseWhenError);
        }

        var sync = parameter['sync'];
        if (sync != undefined) {
            this.defaultRequestValue.setSync(sync);
        }

        var dataType = parameter['dataType'];
        if (dataType != undefined) {
            this.defaultRequestValue.setDataType(dataType);
        }

        var method = parameter['method'];
        if (method != undefined) {
            this.defaultRequestValue.setMethod(method);
        }

        var xhrFields = parameter['xhrFields'];
        if (xhrFields != undefined) {
            this.defaultRequestValue.setXhrFields(xhrFields);
        }

        var q = parameter['q'];
        if (q != undefined) {
            this.defaultRequestValue.setQ(q);
        }

        var timeout = parameter['timeout'];
        if (timeout != undefined) {
            this.defaultRequestValue.setTimeout(timeout);
        }

        var timeoutWithSubmit = parameter['timeoutWithSubmit'];
        if (timeoutWithSubmit != undefined) {
            this.defaultRequestValue.setTimeoutWithSubmit(timeoutWithSubmit);
        }

        var cache = parameter['cache'];
        if (cache != undefined) {
            this.defaultRequestValue.setCache(cache);
        }
    }
};

Lia.Requester.prototype.isRequesting = function () {
    return this.requesting;
};

Lia.Requester.prototype.setRequesting = function (requesting) {
    this.requesting = requesting;
};

Lia.Requester.prototype.onRequestStart = function (request) {
};

Lia.Requester.prototype.setOnRequestStart = function (func) {
    this.onRequestStart = func;
};

Lia.Requester.prototype.onRequestEnded = function (status, data, request) {
};
Lia.Requester.prototype.setOnRequestEnded = function (func) {
    this.onRequestEnded = func;
};

Lia.Requester.prototype.responseCheckHandler = function (status, data, request) {
    return status;
};

Lia.Requester.prototype.setResponseCheckHandler = function (func) {
    this.responseCheckHandler = func;
};

Lia.Requester.prototype.responseDataHandler = function (status, data, request) {
    return data;
};

Lia.Requester.prototype.setResponseDataHandler = function (func) {
    this.responseDataHandler = func;
};

Lia.Requester.prototype.onPreRequest = function (request) {

    var parameterMap = request['parameterMap'];
    if (parameterMap != undefined) {

        var newParameterMap = {};

        for (var key in parameterMap) {
            var value = parameterMap[key];
            if (value != undefined)
                newParameterMap[key] = value;
        }

        request['parameterMap'] = newParameterMap;
    }
};

Lia.Requester.prototype.setOnPreRequest = function (func) {
    this.onPreRequest = func;
};

Lia.Requester.prototype.next = function () {

    if (this.requesting == false) {

        var object = this.queue.dequeue();
        if (object == null)
            return;

        var type = object['type'];
        if (type == Lia.Requester.Type.EXECUTE) {

            this.requesting = true;

            var onExecute = object['onExecute'];
            if (onExecute != undefined) {

                if (Lia.debugMode) {
                    onExecute(object);
                } else {
                    try {
                        onExecute(object);
                    } catch (err) {
                    }
                }
            }

            this.requesting = false;
            this.next();

        } else { // if ( type == Lia.Requester.Type.REQUEST ) {

            object['q'] = false;
            object['nextRequest'] = true;

            this.requesting = true;
            this.request(object);
        }

    }
};

Lia.Requester.prototype.abort = function () {

    this.queue.clear();
    if (this.queueXhr != undefined) {
        this.queueXhr.abort();
        this.queueXhr = undefined;
    }

    this.requesting = false;
};

Lia.Requester.prototype.setQueueXhr = function (xhr) {
    this.queueXhr = xhr;
};

Lia.Requester.prototype.execute = function (excute) {

    //request['onExecute'];
    excute['type'] = Lia.Requester.Type.EXECUTE;

    this.queue.enqueue(excute);

    if (this.requesting == false) {
        this.next();
    }
};


Lia.Requester.prototype.request = function (request) {

    var noExecuteOnResponseWhenError = request['noExecuteOnResponseWhenError'];
    var sync = request['sync'];
    var q = request['q'];
    var dataType = request['dataType'];
    var method = request['method'];
    var nextRequest = request['nextRequest'];
    var jForm = request['jForm'];
    var xhrFields = request['xhrFields'];
    var cache = request['cache'];
    var cacheVersion = request['cacheVersion'];
    var timeout = request['timeout'];
    var timeoutWithSubmit = request['timeoutWithSubmit'];

    //var object = request['object'];
    //var onResponse = request['onResponse'];
    //var onProgress = request['onProgress'];
    //var url = request['url'];

    if (xhrFields == undefined) {
        xhrFields = this.defaultRequestValue.getXhrFields();
    }

    if (sync == undefined) {
        sync = this.defaultRequestValue.getSync();
    }

    if (dataType == undefined) {
        dataType = this.defaultRequestValue.getDataType();
    }

    if (q == undefined) {
        q = this.defaultRequestValue.getQ();
    }

    if (method == undefined) {
        method = this.defaultRequestValue.getMethod();
    }

    if (noExecuteOnResponseWhenError == undefined) {
        noExecuteOnResponseWhenError = this.defaultRequestValue.getNoExecuteOnResponseWhenError();
    }

    if (cache == undefined) {
        cache = this.defaultRequestValue.getCache();
    }

    if (cacheVersion == undefined) {
        cacheVersion = this.defaultRequestValue.getCacheVersion();
    }

    if (timeout == undefined) {
        timeout = this.defaultRequestValue.getTimeout();
    }

    if (timeoutWithSubmit == undefined) {
        timeoutWithSubmit = this.defaultRequestValue.getTimeoutWithSubmit();
    }

    if (cache == true && String.isNotBlank(cacheVersion)) {

        var parameterMap = request['parameterMap'];
        if (parameterMap == undefined) {
            request['parameterMap'] = parameterMap = {};
        }

        parameterMap['_'] = cacheVersion;
    }

    request['noExecuteOnResponseWhenError'] = noExecuteOnResponseWhenError;
    request['sync'] = sync;
    request['dataType'] = dataType;
    request['cache'] = cache;
    request['q'] = q;
    request['method'] = method;
    request['requester'] = this;
    request['xhrFields'] = xhrFields;
    request['type'] = Lia.Requester.Type.REQUEST;


    if (q) {

        this.queue.enqueue(request);

        if (this.requesting == false) {
            this.next();
        }

    } else {

        this.onPreRequest(request);

        this.onRequestStart(request);

        if (jForm != undefined) {

            request['timeout'] = timeoutWithSubmit;

            jForm.ajaxSubmit({
                cache: request['cache'],
                method: request['method'],
                context: request,
                url: request['url'],
                forceSync: request['sync'],
                dataType: request['dataType'],
                timeout: request['timeout'],
                data: request['parameterMap'],
                xhrFields: request['xhrFields'],
                uploadProgress: function (event, position, total, percentComplete) {

                    var onProgress = Lia.p(this, 'context', 'onProgress');

                    if (onProgress == undefined)
                        return;

                    var data = {
                        event: event,
                        position: position,
                        total: total,
                        percentComplete: percentComplete
                    };

                    onProgress(data, request);
                },
                error: function (jqXhr) {

                    var responseData =  this.requester.responseDataHandler(Lia.Requester.Status.ERROR, jqXhr.status, this);

                    var status = this.requester.responseCheckHandler(Lia.Requester.Status.ERROR, responseData, this);

                    if (this.onResponse != undefined) {

                        if (status != Lia.Requester.Status.ERROR || !this.noExecuteOnResponseWhenError) {

                            if (Lia.debugMode) {
                                this.onResponse(status, responseData, this);
                            } else {
                                try {
                                    this.onResponse(status, responseData, this);
                                } catch (err) {
                                }
                            }
                        }
                    }

                    this.requester.onRequestEnded(status, responseData, this);

                    if (this.nextRequest) {

                        this.requester.setRequesting(false);
                        this.requester.setQueueXhr(undefined);
                        this.requester.next();
                    }
                },
                success: function (data) {

                    var responseData =  this.requester.responseDataHandler(Lia.Requester.Status.SUCCESS, data, this);

                    var status = this.requester.responseCheckHandler(Lia.Requester.Status.SUCCESS, responseData, this);

                    if (this.onResponse != undefined) {

                        if (status != Lia.Requester.Status.ERROR || !this.noExecuteOnResponseWhenError) {

                            if (Lia.debugMode) {
                                this.onResponse(status, responseData, this);
                            } else {
                                try {
                                    this.onResponse(status, responseData, this);
                                } catch (err) {
                                }
                            }
                        }
                    }

                    this.requester.onRequestEnded(status, responseData, this);

                    if (this.nextRequest) {
                        this.requester.setRequesting(false);
                        this.requester.setQueueXhr(undefined);
                        this.requester.next();
                    }
                }
            });

            if (nextRequest) {
                this.queueXhr = jForm.data('jqxhr');
            }

        } else {

            request['timeout'] = timeout;

            var ajaxOptions = {
                cache: request['cache'],
                type: request['method'],
                method: request['method'],
                url: request['url'],
                async: !request['sync'],
                dataType: request['dataType'],
                timeout: request['timeout'],
                data: request['parameterMap'],
                xhrFields: request['xhrFields'],
                context: request,
                // Type: Function( jqXHR jqXHR, String textStatus, String errorThrown )
                error: function (jqXhr, textStatus, errorThrown) {

                    // 자체적으로 취소 한 경우 나머지는 에러
                    if (textStatus == Lia.Requester.XhrStatus.ABORT) {
                        return;
                    }

                    var httpStatusCode = jqXhr.status;

                    // timeout 일 때 커스텀
                    if (textStatus == Lia.Requester.XhrStatus.TIMEOUT) {
                        httpStatusCode = Lia.Requester.HttpStatus.TIMEOUT;
                    }

                    var responseData =  this.requester.responseDataHandler(Lia.Requester.Status.ERROR, httpStatusCode, this);

                    var status = this.requester.responseCheckHandler(Lia.Requester.Status.ERROR, responseData, this);

                    if (this.onResponse != undefined) {

                        if (status != Lia.Requester.Status.ERROR || !this.noExecuteOnResponseWhenError) {

                            if (Lia.debugMode) {
                                this.onResponse(status, responseData, this);
                            } else {
                                try {
                                    this.onResponse(status, responseData, this);
                                } catch (err) {
                                }
                            }
                        }
                    }

                    this.requester.onRequestEnded(status, responseData, this);
                },
                success: function (data) {

                    var responseData =  this.requester.responseDataHandler(Lia.Requester.Status.SUCCESS, data, this);

                    var status = this.requester.responseCheckHandler(Lia.Requester.Status.SUCCESS, responseData, this);

                    if (this.onResponse != undefined) {

                        if (status != Lia.Requester.Status.ERROR || !this.noExecuteOnResponseWhenError) {

                            if (Lia.debugMode) {
                                this.onResponse(status, responseData, this);
                            } else {
                                try {
                                    this.onResponse(status, responseData, this);
                                } catch (err) {
                                }
                            }
                        }
                    }

                    this.requester.onRequestEnded(status, responseData, this);
                },
                complete: function (jqXHR, textStatus) {

                    if (this.nextRequest) {
                        this.requester.setRequesting(false);
                        this.requester.setQueueXhr(undefined);
                        this.requester.next();
                    }
                }
            };

            var xhr = jQuery.ajax(ajaxOptions);
            if (nextRequest) {
                this.queueXhr = xhr;
            }
        }
    }

};


Lia.Requester.prototype.func = function (onExecute, object) {

    var execute = {
        onExecute: onExecute,
        object: object
    };

    this.execute(execute);
};


Lia.Requester.prototype.ajaxWithoutBlank = function (url, parameterMap, onResponse, object,
                                                     noExecuteOnResponseWhenError, q, xhrFields) {

    var newParameterMap = undefined;
    if (parameterMap != undefined) {
        newParameterMap = {};

        for (var key in parameterMap) {

            var value = parameterMap[key];

            if (!String.isNullOrWhitespace(value))
                newParameterMap[key] = value;
        }
    }

    this.ajax(url, newParameterMap, onResponse, object, noExecuteOnResponseWhenError, q, xhrFields);
};


Lia.Requester.prototype.ajaxWithoutBlankWithoutQ = function (url, parameterMap, onResponse,
                                                             object, noExecuteOnResponseWhenError, xhrFields) {

    this.ajaxWithoutBlank(url, parameterMap, onResponse, object, noExecuteOnResponseWhenError, false, xhrFields);
};

Lia.Requester.prototype.ajax = function (url, parameterMap, onResponse, object, noExecuteOnResponseWhenError, q, xhrFields) {

    var request = {
        url: url,
        noExecuteOnResponseWhenError: noExecuteOnResponseWhenError,
        parameterMap: parameterMap,
        onResponse: onResponse,
        object: object,
        sync: false,
        q: q,
        xhrFields: xhrFields
    };

    this.request(request);
};


Lia.Requester.prototype.text = function (url, parameterMap, onResponse, object, noExecuteOnResponseWhenError, q, xhrFields) {

    var request = {
        url: url,
        noExecuteOnResponseWhenError: noExecuteOnResponseWhenError,
        parameterMap: parameterMap,
        onResponse: onResponse,
        object: object,
        sync: false,
        q: q,
        xhrFields: xhrFields,
        dataType: 'text',
        method: 'get'
    };

    this.request(request);
};

Lia.Requester.prototype.textWithoutBlank = function (url, parameterMap, onResponse, object,
                                                     noExecuteOnResponseWhenError, q, xhrFields) {

    var newParameterMap = undefined;
    if (parameterMap != undefined) {
        newParameterMap = {};

        for (var key in parameterMap) {

            var value = parameterMap[key];

            if (!String.isNullOrWhitespace(value))
                newParameterMap[key] = value;
        }
    }

    this.text(url, newParameterMap, onResponse, object, noExecuteOnResponseWhenError, q, xhrFields);
};

Lia.Requester.prototype.jsonp = function (url, parameterMap, onResponse, object, noExecuteOnResponseWhenError, q) {

    var request = {
        dataType: 'jsonp',
        url: url,
        noExecuteOnResponseWhenError: noExecuteOnResponseWhenError,
        parameterMap: parameterMap,
        onResponse: onResponse,
        object: object,
        sync: false,
        q: q
    };

    this.request(request);
};

Lia.Requester.prototype.jsonpWithoutBlank = function (url, parameterMap, onResponse, object, noExecuteOnResponseWhenError, q) {

    var newParameterMap = undefined;
    if (parameterMap != undefined) {
        newParameterMap = {};

        for (var key in parameterMap) {

            var value = parameterMap[key];

            if (!String.isNullOrWhitespace(value))
                newParameterMap[key] = value;
        }
    }

    this.jsonp(url, newParameterMap, onResponse, object, noExecuteOnResponseWhenError, q);
};


//var data = {
//    event : event,
//    position : position,
//    total : total,
//    percentComplete : percentComplete
//};
Lia.Requester.prototype.formUpload = function (url, parameterMap, jForm, onResponse, onProgress,
                                               object, noExecuteOnResponseWhenError) {

    var request = {
        url: url,
        jForm: jForm,
        onProgress: onProgress,
        noExecuteOnResponseWhenError: noExecuteOnResponseWhenError,
        parameterMap: parameterMap,
        onResponse: onResponse,
        object: object,
        sync: false,
        q: true
    };

    this.request(request);
};

Lia.Requester.prototype.formUploadWithoutBlank = function (url, parameterMap, jForm, onResponse, onProgress,
                                                           object, noExecuteOnResponseWhenError) {

    var newParameterMap = undefined;
    if (parameterMap != undefined) {
        newParameterMap = {};

        for (var key in parameterMap) {

            var value = parameterMap[key];

            if (!String.isNullOrWhitespace(value))
                newParameterMap[key] = value;
        }
    }

    this.formUpload(url, newParameterMap, jForm, onResponse, onProgress,
        object, noExecuteOnResponseWhenError);
};

Lia.Requester.prototype.open = function (url, parameterMap, options) {

    var optionString = '';

    if (options != undefined) {

        for (var key in options) {

            var value = options[key];

            if (String.isNotBlank(optionString)) {
                optionString += ',';
            }

            optionString += key + '=' + value;
        }
    }


    window.open(url + Lia.convertArrayToQueryString(parameterMap), '', optionString);
};

Lia.Requester.prototype.openWithoutBlank = function (url, parameterMap, options) {

    var newParameterMap = undefined;
    if (parameterMap != undefined) {
        newParameterMap = {};

        for (var key in parameterMap) {

            var value = parameterMap[key];

            if (!String.isNullOrWhitespace(value))
                newParameterMap[key] = value;
        }
    }

    this.open(url, newParameterMap, options);
};

Lia.Requester.init = function () {
};
Lia.Requester.checkProgressSupported = function () {
    var ieVersion = Lia.checkInternetExplorerVersion();
    if (ieVersion != -1)
        return ieVersion > 9;
    else
        return Lia.checkiPhoneSeries() || Lia.checkAndroid() || Lia.checkChrome() || Lia.checkSafari() || Lia.checkOpera() || Lia.checkFirefox();
};
Lia.Requester.isProgressSupported = Lia.Requester.checkProgressSupported();

Lia.Requester.prototype.twb = Lia.Requester.prototype.textWithoutBlank;
Lia.Requester.prototype.awb = Lia.Requester.prototype.ajaxWithoutBlank;
Lia.Requester.prototype.awbwq = Lia.Requester.prototype.ajaxWithoutBlankWithoutQ;
Lia.Requester.prototype.a = Lia.Requester.prototype.ajax;
Lia.Requester.prototype.o = Lia.Requester.prototype.open;
Lia.Requester.prototype.owb = Lia.Requester.prototype.openWithoutBlank;
Lia.Requester.prototype.jp = Lia.Requester.prototype.jsonp;
Lia.Requester.prototype.jpwb = Lia.Requester.prototype.jsonpWithoutBlank;


/**
 * image_input
 *
 * <div class="image_input" data-lia-src="{배경 이미지 주소}"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding="{양 쪽 패딩 px}"></div>
 *      input type=text
 * <div class="image_input textarea" data-lia-src="{배경 이미지 주소}"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding="{양 쪽 패딩 px}"></div>
 *      textarea
 * <div class="image_input placeholder" data-lia-src="{배경 이미지 주소}"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding="{양 쪽 패딩 px}"
 data-lia-postfix="{placeholder 파일 접미사}"></div>
 *      placehoder 들어감
 *      data-lia-postfix 가 들어가 있으면 해당 파일로 _{파일 접미사}.png 가 붙음
 *      안들어가 있으면 _placeholder.png 가 붙음
 *
 * .imageInputVal
 *      입력 값 설정 및 받아오기
 * .imageInput
 *      실제 입력 DOM객체 받아오기
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.imageInput();
 });

 */
(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initImageInput: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_INPUT;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageInput();
        }
    });

    $.fn.extend({

        /**
         * 입력된 내용 세팅, 리턴
         * @param val
         * @returns {*}
         */
        imageInputVal: function (val) {

            if (val == undefined)
                return this.find(':input').val();
            else
                this.find(':input').val(val);

            return this;
        },

        /**
         * 내용에 다른 placeholder 체크
         * @returns {*}
         */
        checkImageInput: function () {

            return this.find(':input').change();

        },

        /**
         * 실제 input 태그 반환
         * @returns {*}
         */
        imageInput: function () {
            return this.find(':input');
        },

        /**
         * 초기화
         * @returns {*}
         */
        initImageInput: function () {

            return this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.INITED))
                    return;

                var height = jThis.height() + 'px';
                var width = jThis.width() + 'px';
                var path = jThis.dataAttr(Lia.Component.AttrName.SRC);

                var jPlaceholder = $('<div />');
                jPlaceholder.css({
                    'position': 'relative',
                    'width': width,
                    'height': height
                });

                jThis.append(jPlaceholder);

                var isTextarea = jThis.hasClass(Lia.Component.Flag.TEXTAREA);
                var jInput = $('<' + (isTextarea ? 'textarea' : 'input') + ' />');

                if (!isTextarea) {
                    var type = jThis.hasClass(Lia.Component.Flag.PASSWORD) ? 'password' : 'text';
                    jInput.attr('type', type);
                } else {
                    var isImageInputNoResize = jThis.hasClass(Lia.Component.Flag.NO_RESIZE);
                    if (isImageInputNoResize)
                        jInput.css('resize', 'none');

                    var isImageInputHiddenOverflow = jThis.hasClass(Lia.Component.Flag.HIDDEN_OVERFLOW);
                    var overflow = 'auto';
                    if (isImageInputHiddenOverflow)
                        overflow = 'hidden';

                    jInput.css('overflow', overflow);
                }

                var textAlign = "left";
                var isAlignCenter = jThis.hasClass(Lia.Component.Flag.ALIGN_CENTER);
                var isAlignRight = jThis.hasClass(Lia.Component.Flag.ALIGN_RIGHT);
                if (isAlignCenter)
                    textAlign = "center";
                if (isAlignRight)
                    textAlign = "right";

                var paddingLeft = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_HORIZONTAL_PADDING;
                var paddingRight = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_HORIZONTAL_PADDING;
                var paddingTop = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_VERTICAL_PADDING;
                var paddingBottom = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_VERTICAL_PADDING;
                var padding = jThis.dataAttr(Lia.Component.AttrName.PADDING);
                if (padding != undefined) {
                    paddingLeft = padding;
                    paddingRight = padding;
                    paddingTop = padding;
                    paddingBottom = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_HORIZONTAL);
                if (padding != undefined) {
                    paddingLeft = padding;
                    paddingRight = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_VERTICAL);
                if (padding != undefined) {
                    paddingTop = padding;
                    paddingBottom = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (padding != undefined)
                    paddingLeft = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_RIGHT);
                if (padding != undefined)
                    paddingRight = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_TOP);
                if (padding != undefined)
                    paddingTop = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_BOTTOM);
                if (padding != undefined)
                    paddingBottom = padding;

                var textColor = jThis.dataAttr(Lia.Component.AttrName.TEXT_COLOR);
                if (textColor == undefined)
                    textColor = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_TEXT_COLOR;


                width = (parseFloat(width) - parseFloat(paddingLeft) - parseFloat(paddingRight)) + 'px';
                height = (parseFloat(height) - parseFloat(paddingTop) - parseFloat(paddingBottom)) + 'px';

                jInput.css({
                    'color': textColor,
                    'position': 'relative',
                    'background-color': 'transparent',
                    'border-width': '0px',
                    'outline': 'none',
                    'width': width,
                    'padding-left': paddingLeft,
                    'padding-right': paddingRight,
                    'padding-top': paddingTop,
                    'padding-bottom': paddingBottom,
                    'height': height,
                    'text-align': textAlign
                });

                if (!isTextarea && Lia.ieVersion != -1)
                    jInput.css('line-height', height);

                jThis.css('background-image', "url('" + path + "')");

                jPlaceholder.append(jInput);

                jThis.filter('.' + Lia.Component.Flag.PLACEHOLDER).find(':input').change(liaCheckImageInput).focus(function () {

                    var jThis = $(this);
                    var jPlaceholder = jThis.parent();

                    jPlaceholder.css('background-image', '');

                }).focusout(liaCheckImageInput).change();

                jThis.addClass(Lia.Component.Flag.INITED);

            });
        }

    });
})(jQuery);

function liaCheckImageInput() {
    var jThis = $(this);
    var jPlaceholder = jThis.parent();
    var jParent = jPlaceholder.parent();

    var path = jParent.attr('src');
    var postfix = jParent.dataAttr(Lia.Component.AttrName.POSTFIX);
    if (postfix == undefined)
        postfix = Lia.Component.Value.ImagePlaceholderInput.DEFAULT_POSTFIX;

    var url;
    if (jThis.val() == '')
        url = "url('" + (path = path.replace(Lia.Component.Value.ImagePlaceholderInput.REPLACEMENT_POSTFIX, postfix)) + "')";
    else
        url = '';

    jPlaceholder.css('background-image', url);

}

/**
 * deprecated
 *
 *  jquery.form.js 임포트 시켜야 함
 *
 **/

/*
 사용 코드

 var formUpload = new $.FormUpload( {url} );
 formUpload.init( { url } );
 formUpload.setUrl( { url } );
 formUpload.setContext(context);
 formUpload.add('name', $(...));
 formUpload.setOnCompleted(function(uploadList){});
 formUpload.upload();

 노드 이름 변경 ( static 함수 )

 $.FormUpload.setPathNodeName( name );

 }
 */

jQuery.FormUpload = Lia.FormUpload = function (url) {

    this.init(url);
};

Lia.FormUpload.NAME = Lia.Component.Value.FormUpload.NAME;
Lia.FormUpload.FORM = Lia.Component.Value.FormUpload.FORM;
Lia.FormUpload.TAG = Lia.Component.Value.FormUpload.TAG;
Lia.FormUpload.PATH = Lia.Component.Value.FormUpload.PATH;
Lia.FormUpload.RESPONSE = Lia.Component.Value.FormUpload.RESPONSE;


/**
 * 초기화
 */
Lia.FormUpload.prototype.init = function (url) {

    this.url = url;
    this.uploadList = [];
    this.uploadedList = [];
    this.currentUploadIndex = 0;
};

Lia.FormUpload.pathNodeName = Lia.Component.Value.FormUpload.DEFAULT_PATH_NODE_NAME;
Lia.FormUpload.isSupportedProgress = undefined;
Lia.FormUpload.init = function () {

    var ieVersion = Lia.checkInternetExplorerVersion();
    if (ieVersion != -1)
        Lia.FormUpload.isSupportedProgress = ieVersion > 9;
    else
        Lia.FormUpload.isSupportedProgress = Lia.checkiPhoneSeries() || Lia.checkAndroid() || Lia.checkChrome() || Lia.checkSafari() || Lia.checkOpera() || Lia.checkFirefox();
};

/**
 * 주소 노드 이름 설정
 * @param name
 */
Lia.FormUpload.setPathNodeName = function (name) {

    Lia.FormUpload.pathNodeName = name;
};

/**
 * url 설정
 *
 *  @param url
 */
Lia.FormUpload.prototype.setUrl = function (url) {

    this.url = url;
};

/**
 * context 설정
 *
 *  @param context
 */
Lia.FormUpload.prototype.setContext = function (context) {

    this.context = context;
};

/**
 * 현재 컨텍스트 얻기
 *
 * @returns context
 */
Lia.FormUpload.prototype.getContext = function () {

    return ((this.context == undefined) ? this : this.context);
};

/**
 * 경초 찾기 함수
 *
 * @param uploadedList
 */
Lia.FormUpload.prototype.onFindPath = function (response) {

    return response[Lia.FormUpload.pathNodeName];

};

/**
 * 경로 찾기 함수 설정
 *
 * @param func
 */
Lia.FormUpload.prototype.setOnFindPath = function (func) {

    this.onFindPath = func;
};

/**
 * 업로드
 */
Lia.FormUpload.prototype.upload = function () {

    if (this.uploadedList == null) {
        this.onCompleted.call(this.getContext(), null);
        return;
    }

    if (this.currentUploadIndex == this.uploadList.length) {
        this.onCompleted.call(this.getContext(), this.uploadedList);
        return;
    }

    this.uploadList[this.currentUploadIndex][Lia.Component.Value.FormUpload.FORM].submit();

};

/**
 * 추가
 *
 * @param name
 * @param jForm
 */
Lia.FormUpload.prototype.add = function (name, jForm, tag) {

    jForm.ajaxForm({

        context: this,
        url: this.url,
        dataType: 'json',
        uploadProgress: function (event, position, total, percentComplete) {

            if (this.uploadList == undefined)
                return;

            var currentUpload = this.uploadList[this.currentUploadIndex];
            if (this.onProgress == undefined)
                return;

            this.onProgress.call(this.getContext(), currentUpload, event, position, total, percentComplete);
        },
        error: function () {
            this.onCompleted.call(this.getContext(), null);

        },
        success: function (response) {

            var path = null;
            if (response == null || String.isNullOrWhitespace(path = this.onFindPath.call(this, response))) {
                this.onCompleted.call(this.getContext(), null);
                return;
            }

            var uploaded = {};

            var currentUpload = this.uploadList[this.currentUploadIndex];
            for (var key in currentUpload)
                uploaded[key] = currentUpload[key];

            uploaded[Lia.FormUpload.PATH] = path;
            uploaded[Lia.FormUpload.RESPONSE] = response;

            this.uploadedList.push(uploaded);

            ++this.currentUploadIndex;
            this.upload();
        }
    });

    var upload = {};
    upload[Lia.FormUpload.NAME] = name;
    upload[Lia.FormUpload.FORM] = jForm;
    upload[Lia.FormUpload.TAG] = tag;
    this.uploadList.push(upload);
};

/**
 * 진행 업데이트 함수
 *
 * @param upload add 함술 입력한 객체
 * @param event 브라우져 이벤트값
 * @param position 현재
 * @param total 전체값
 * @param percentComplete 퍼센테이지값(100기준)
 */
Lia.FormUpload.prototype.onProgress = undefined;
// function( upload, event, position, total, percentComplete ) {};

/**
 * 진행 함수 설정
 *
 * @param func
 */
Lia.FormUpload.prototype.setOnProgress = function (func) {

    this.onProgress = func;
};


/**
 * 기본 진행 함수
 * @param uploadedList
 */
Lia.FormUpload.prototype.onCompleted = function (uploadedList) {

    alert('Set onCompleted Function!\r\nUploaded List :\r\n' + JSON.stringify(uploadedList));
};


/**
 * 완료함수 설정
 *
 * @param func
 */
Lia.FormUpload.prototype.setOnCompleted = function (func) {

    this.onCompleted = func;
};
/**
 * input_select
 *
 * image_select_list 의 부모 뷰에 마우스가 벗어나면 콤보박스가 사라짐
 * 아래 형식처럼 코딩
 * height 지정해주지 말고 position:relative 로
 *
 <div style="{총 크기 설정해 주어야 함}">
 <div class="image_select {텍스트 정렬 방법}"
 style="{위치 잡아주어야 함}"
 data-lia-background-image="{이미지 주소}" ></div>
 <div class="image_select_list {텍스트 청렬 방법}"
 style="{위치 잡아주어야 함}"
 data-lia-background-image="{이미지 주소}" data-lia-row-height="{한 줄당 길이}"
 data-lia-text-color="{글자 색상}" data-lia-hover-color="{마우스 오버될 때의 색상}"></div>
 </div>
 *
 * {텍스트 정렬 방법} = align_left, align_right, align_center
 *
 * image_select
 *      .imageSelectVal
 *          보여지는 텍스트 설정 및 겨져오기
 *      .imageSelectIndex
 *          보여지는 인덱스 설정 및 가져오기
 *      .imageSelectList
 *          콤보박스 객체 설정 및 가져오기 (.image_select_list, jquery 객체)
 *
 * image_select_list
 *      .imageSelectListArray
 *          리스트 설정 및 가져오기 [ { text :  'abc', value : '1' }, { text : 'def', value : '2'} ]
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initImageSelect();
 $.initImageSelectList();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initImageSelect: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_SELECT;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageSelect();
        },

        /**
         * 초기화
         */
        initImageSelectList: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_SELECT_LIST;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            j.initImageSelectList();
        }
    });

    $.fn.extend({

        /**
         * 선택된 있는 값 세팅, 리턴
         *
         * @param val
         * @returns {*}
         */
        imageSelectVal: function (val) {

            if (val == undefined) {

                var imageSelectList = this.data(Lia.Component.Value.ImageSelect.LIST);
                if (imageSelectList == undefined)
                    return undefined;

                var array = imageSelectList.data(Lia.Component.Value.ImageSelect.LIST_ARRAY);
                var index = this.imageSelectIndex();

                return Lia.p(array, index, Lia.Component.Value.ImageSelect.VALUE);
            }

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var index = undefined;

                var imageSelectList = jThis.data(Lia.Component.Value.ImageSelect.LIST);
                if (imageSelectList == undefined)
                    return;

                var array = imageSelectList.data(Lia.Component.Value.ImageSelect.LIST_ARRAY);
                if (array != undefined) {

                    for (var k = 0, kl = array.length; k < kl; k++) {

                        var item = array[k];
                        var value = item[Lia.Component.Value.ImageSelect.VALUE];
                        if (value == val) {
                            index = k;
                            break;
                        }
                    }
                }


                jThis.imageSelectIndex(index);
            }
        },

        /**
         * 선택된 인덱스 세팅, 리턴
         *
         * @param index
         * @returns {*}
         */
        imageSelectIndex: function (index) {

            if (index == undefined)
                return this.data(Lia.Component.Value.ImageSelect.INDEX);

            return this.data(Lia.Component.Value.ImageSelect.INDEX, index).each(function () {

                var jThis = $(this);

                var index = jThis.data(Lia.Component.Value.ImageSelect.INDEX);
                if (index == undefined)
                    return;

                var imageSelectList = jThis.data(Lia.Component.Value.ImageSelect.LIST);
                if (imageSelectList == undefined)
                    return;

                var array = imageSelectList.data(Lia.Component.Value.ImageSelect.LIST_ARRAY);

                var name = Lia.p(array, index, Lia.Component.Value.ImageSelect.NAME);
                jThis.empty().append(name);
            });

        },

        /**
         * image_select_list 컴포넌트 새팅, 리턴
         *
         * @param imageSelectList
         * @returns {*}
         */
        imageSelectList: function (imageSelectList) {

            if (imageSelectList == undefined) {
                if (this.length == 0)
                    return undefined;

                return this.data(Lia.Component.Value.ImageSelect.LIST);
            }

            imageSelectList.data(Lia.Component.Value.ImageSelect.SELECT, this);
            return this.data(Lia.Component.Value.ImageSelect.LIST, imageSelectList);
        },

        /**
         * image_select_list 에 들어갈 리스트 세팅, 리턴
         * @param array
         * @returns {*}
         */
        imageSelectListArray: function (array) {

            if (array == undefined) {
                if (this.length == 0)
                    return undefined;

                return this.data(Lia.Component.Value.ImageSelect.LIST_ARRAY);
            }

            for (var i = 0, l = this.length; i < l; i++) {
                var j = this.eq(i);

                var rowHeight = j.dataAttr(Lia.Component.AttrName.ROW_HEIGHT);
                if (rowHeight == undefined)
                    rowHeight = Lia.Component.Value.ImageSelect.DEFAULT_LIST_ROW_HEIGHT;

                var jUl = $('<ul></ul>');
                jUl.css({
                    'width': '100%',
                    'height': '100%',
                    'overflow-y': 'auto',
                    'overflow-x': 'hidden'
                });

                var textAlign = "left";
                var isAlignCenter = j.hasClass(Lia.Component.Flag.ALIGN_CENTER);
                var isAlignRight = j.hasClass(Lia.Component.Flag.ALIGN_RIGHT);
                if (isAlignCenter)
                    textAlign = "center";
                if (isAlignRight)
                    textAlign = "right";

                var textColor = j.dataAttr(Lia.Component.AttrName.TEXT_COLOR);
                for (var i = 0, l = array.length; i < l; i++) {

                    var item = array[i];
                    var name = item[Lia.Component.Value.ImageSelect.NAME];

                    var jLi = $('<li>' + name + '</li>');
                    jLi.css({
                        'width': '100%',
                        'line-height': rowHeight,
                        'text-align': textAlign
                    });
                    if (textColor)
                        jLi.css({'color': textColor});

                    if (Lia.isMobile)
                        jLi.bind('touchstart', liaImageSelectListEnter()).bind('touchend', liaImageSelectListLeave);
                    else
                        jLi.mouseenter(liaImageSelectListEnter).mouseleave(liaImageSelectListLeave);

                    jLi.click(function () {

                        var jThis = $(this);
                        var index = jThis.index();

                        var imageSelectList = jThis.parent().parent();
                        var array = imageSelectList.data(Lia.Component.Value.ImageSelect.LIST_ARRAY);
                        if (array == undefined)
                            return;

                        var imageSelect = imageSelectList.data(Lia.Component.Value.ImageSelect.SELECT);
                        if (imageSelect == undefined)
                            return;

                        imageSelect.imageSelectIndex(index);
                        imageSelect.removeClass(Lia.Component.Flag.SHOWING);
                        imageSelectList.fadeOut(Lia.Component.Value.ImageSelect.LIST_FADE_DURATION);
                    });

                    jUl.append(jLi);
                }

                j.remove('ul').append(jUl).data(Lia.Component.Value.ImageSelect.LIST_ARRAY, array);
            }

            return this;
        },

        /**
         * image_select 초기화
         *
         * @returns {*}
         */
        initImageSelect: function () {

            return this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.INITED))
                    return;

                jThis.click(function () {

                    var jThis = $(this);
                    var jSelectList = jThis.data(Lia.Component.Value.ImageSelect.LIST);
                    if (jSelectList == undefined)
                        return;

                    if (jThis.hasClass(Lia.Component.Flag.SHOWING)) {
                        jSelectList.fadeOut(Lia.Component.Value.ImageSelect.LIST_FADE_DURATION);
                        jThis.removeClass(Lia.Component.Flag.SHOWING);
                    } else {
                        jSelectList.fadeIn(Lia.Component.Value.ImageSelect.LIST_FADE_DURATION);
                        jSelectList.children().scrollTop(0);
                        jThis.addClass(Lia.Component.Flag.SHOWING);
                    }

                });

                var height = jThis.height() + 'px';
                var src = jThis.dataAttr(Lia.Component.AttrName.BACKGROUND_IMAGE);

                var textAlign = "left";
                var isAlignCenter = jThis.hasClass(Lia.Component.Flag.ALIGN_CENTER);
                var isAlignRight = jThis.hasClass(Lia.Component.Flag.ALIGN_RIGHT);
                if (isAlignCenter)
                    textAlign = "center";
                if (isAlignRight)
                    textAlign = "right";

                jThis.css({
                    'overflow': 'hidden',
                    'text-align': textAlign,
                    'line-height': height,
                    'background-image': "url('" + src + "')",
                    'cursor': 'pointer'
                });

                jThis.addClass(Lia.Component.Flag.INITED);


            });

        },

        /**
         * image_select_list 초기화
         *
         * @returns {*}
         */
        initImageSelectList: function () {

            this.each(function () {

                var jThis = $(this);
                var src = jThis.dataAttr(Lia.Component.AttrName.BACKGROUND_IMAGE);
                jThis.css({
                    'background-image': "url('" + src + "')"
                });

            }).hide();

            if (!Lia.isMobile) {
                // 부모 벗어나면 리스트 창 끄기
                this.parent().mouseleave(function () {

                    var jThis = $(this);
                    var jImageSelectList = jThis.children('.' + Lia.Component.Name.IMAGE_SELECT_LIST);
                    if (jImageSelectList.length == 0)
                        return;

                    var jImageSelect = jImageSelectList.data(Lia.Component.Value.ImageSelect.SELECT);
                    if (jImageSelect == undefined)
                        return;

                    if (jImageSelect.hasClass(Lia.Component.Flag.SHOWING)) {
                        jImageSelectList.fadeOut(Lia.Component.Value.ImageSelect.LIST_FADE_DURATION);
                        jImageSelect.removeClass(Lia.Component.Flag.SHOWING);
                    }
                });
            }
            return this;
        }


    });
})(jQuery);

function liaImageSelectListEnter() {
    var jThis = $(this);
    var hoverColor = jThis.parent().parent().dataAttr(Lia.Component.AttrName.HOVER_COLOR);
    if (hoverColor)
        jThis.css('background-color', hoverColor);
}

function liaImageSelectListLeave() {
    var jThis = $(this);
    jThis.css('background-color', '');
}


/**
 *  jquery.history.js 임포트 시켜서 사용
 *  lia.requester.js 임포트 시켜서 사용
 *  ajax 호출
 **/

var Page = jQuery.Page = Lia.Page = function () {
    this.jPageContainer = undefined;
    this.jPage = undefined;
    this.cssLoading = undefined;
    this.htmlLoading = undefined;
};
Lia.Page.prototype.set = function (options) {

    if (options != undefined) {

        var jPageContainer = options['jPageContainer'];
        if (jPageContainer != undefined)
            this.jPageContainer = jPageContainer;

        var jPage = options['jPage'];
        if (jPage != undefined)
            this.jPage = jPage;
    }
};
Lia.Page.prototype.checkCssLoading = function () {
    return this.cssLoading;
};
Lia.Page.prototype.checkHtmlLoading = function () {
    return this.htmlLoading;
};
Lia.Page.prototype.getJPageContainer = function () {
    return this.jPageContainer;
};
Lia.Page.prototype.getJPage = Lia.Page.prototype.get = function () {
    return this.jPage;
};
Lia.Page.prototype.find = function (selector) {
    return this.jPage.find(selector);
};
Lia.Page.prototype.extend = function (map) {
    for (var key in map) {
        this[key] = map[key];
    }
};


var PageManager = jQuery.PageManager = Lia.PageManager = {

    Constants: {
        SUID: '_suid'
    },

    ContentType: {

        CSS: 'css',
        JS: 'js',
        HTML: 'html'
    },

    Status: {

        START: 'START',
        SUCCESS: 'SUCCESS',
        ERROR: 'ERROR'
    },

    title: '',
    History: window.History,
    cssLoading: true,
    htmlLoading: true,
    jsLoading: true,

    requester: undefined,

    ajaxQSync: false,
    ajaxQCssMethod: 'get',
    ajaxQJsMethod: 'get',
    ajaxQHtmlMethod: 'get',

    preparedContentMap: {
        css: {},
        js: {},
        html: {}
    },

    setPreparedContent: function (path, contentType, content) {

        var map = Lia.PageManager.preparedContentMap[contentType];
        map[path] = content;
    },

    setCssPreparedContent: function (path, content) {

        Lia.PageManager.setPreparedContent(path, Lia.PageManager.ContentType.CSS, content);
    },

    setJsPreparedContent: function (path, content) {

        Lia.PageManager.setPreparedContent(path, Lia.PageManager.ContentType.JS, content);
    },

    setHtmlPreparedContent: function (path, content) {

        Lia.PageManager.setPreparedContent(path, Lia.PageManager.ContentType.HTML, content);
    },


    pageList: [],
    pageContentList: {
        css: [],
        js: [],
        html: []
    },
    pageParameterNameList: [],
    setPageParameterNameList: function (pageParameterNameList) {
        Lia.PageManager.pageParameterNameList = pageParameterNameList;
    },

    pageContainerSelectorList: [],
    depth: -1,
    parameterMap: undefined,
    beforeDepth: undefined,
    beforeParameterMap: undefined,

    originalParameterMap: undefined,
    beforeOriginalParameterMap: undefined,

    parameterDecoding : true,
    setParameterDecoding: function (parameterDecoding) {
        Lia.PageManager.parameterDecoding = parameterDecoding;
    },

    uriConversionType: Lia.UriConversionType.DEFAULT,
    parameterPostfixAdding: false,
    setParameterPostfixAdding: function (parameterPostfixAdding) {
        Lia.PageManager.parameterPostfixAdding = parameterPostfixAdding;
    },
    parameterPostfix: '%',
    setParameterPostfix: function (parameterPostfix) {
        Lia.PageManager.parameterPostfix = parameterPostfix;
    },

    executingChangeWhenSameParameterMap : false,

    usingParameterMapWhenRequest: false,

    getParameterMap: function () {
        return Lia.PageManager.parameterMap;
    },

    getBeforeParameterMap: function () {
        return Lia.PageManager.beforeParameterMap;
    },

    /**
     * 페이지 변경 시작 공용 함수
     */
    setonPageSwitchStart: function (func) {
        Lia.PageManager.onPageSwitchStart = func;
    },

    onPageSwitchStart: function (beforeDepth, baseDepth, depth, parameterMap, beforeParameterMap, requesting) {
    },

    /**
     * 페이지 변경 끝 공용 함수
     */
    setonPageSwitchEnd: function (func) {
        Lia.PageManager.onPageSwitchEnd = func;
    },

    onPageSwitchEnd: function (beforeDepth, baseDepth, depth, parameterMap, beforeParameterMap, requesting) {
    },

    /**
     * 페이지 초기화 공용 함수
     */
    setOnPageInit: function (func) {
        Lia.PageManager.onPageInit = func;
    },

    onPageInit: function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
    },

    /**
     * 페이지 변경 공용 함수
     */
    setOnPageChange: function (func) {
        Lia.PageManager.onPageChange = func;
    },

    onPageChange: function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
    },


    /**
     * 페이지 릴리즈 공용 함수
     */
    setOnPageRelease: function (func) {
        Lia.PageManager.onPageRelease = func;
    },

    onPageRelease: function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
    },

    /**
     * 페이지 추가 공용 함수
     */
    setOnPageAdd: function (func) {
        Lia.PageManager.onPageAdd = func;
    },

    onPageAdd: function (jPage, jPageContainer, depth) {
        jPageContainer.empty().append(jPage);
    },

    /**
     * 페이지 삭제 공용 함수
     */
    setOnPageRemove: function (func) {
        Lia.PageManager.onPageRemove = func;
    },

    onPageRemove: function (jPage, jPageContainer, depth) {
        jPageContainer.empty();
    },

    onNormalizeParameter: function (data) {
        return data;
    },
    filePathFormatHandler: function (path, parameterMap, i) {
        return path;
    },
    cssFilePathFormatHandler: function (path, parameterMap, i) {
        return '/res/css/' + path + '.css';
    },
    htmlFilePathFormatHandler: function (path, parameterMap, i) {
        return '/res/html/' + path + '.html';
    },
    jsFilePathFormatHandler: function (path, parameterMap, i) {
        return '/res/js/' + path + '.js';
    },
    onMoveCheck: function (parameterMap) {
        return true;
    },
    onPageCheck: function (parameterMap) {
        return true;
    },
    onRefreshCheck : function(parameterMap) {
        return false;
    },

    /**
     * 페이지 체크 함수 설정
     */
    setOnRefreshCheck: function (listener) {
        Lia.PageManager.onRefreshCheck = listener;
    },

    /**
     * 페이지 체크 함수 설정
     */
    setOnPageCheck: function (listener) {
        Lia.PageManager.onPageCheck = listener;
    },

    /**
     * 받을 페이지 인자값 이름 설정
     */
    setPageParameterNameList: function (pageParameterNameList) {
        Lia.PageManager.pageParameterNameList = pageParameterNameList;
    },

    /**
     * title 설정
     */
    setTitle: function (title, setting) {
        Lia.PageManager.title = title;
        if (setting == undefined || setting == true)
            window.document.title = title;
    },

    /**
     * css 로딩 여부 설정
     */
    setCssLoading: function (loading) {
        Lia.PageManager.cssLoading = loading;
    },


    /**
     * html 로딩 여부 설정
     */
    setHtmlLoading: function (loading) {
        Lia.PageManager.htmlLoading = loading;
    },


    /**
     * js 로딩 여부 설정
     */
    setJsLoading: function (loading) {
        Lia.PageManager.jsLoading = loading;
    },

    /**
     * check 함수 설정
     */
    setOnMoveCheck: function (listener) {
        Lia.PageManager.onMoveCheck = listener;
    },

    /**
     * 변경될 page selector 들 설정
     */
    setPageContainerSelectorList: function (pageContainerSelectorList) {
        Lia.PageManager.pageContainerSelectorList = pageContainerSelectorList;
    },

    /**
     * 들어온 파라키터 노말라이즈 하는 함수 세팅
     */
    setOnNormalizeParameter: function (func) {
        Lia.PageManager.onNormalizeParameter = func;
    },

    /**
     * ajax로 sync 설정
     */
    setAjaxQSync: function (sync) {
        Lia.PageManager.ajaxQSync = sync;
    },

    /**
     * ajax로 css 요청시 method 설정
     */
    setAjaxQCssMethod: function (method) {
        Lia.PageManager.ajaxQCssMethod = method;
    },
    /**
     * ajax로 js 요청시 method 설정
     */
    setAjaxQJsMethod: function (method) {
        Lia.PageManager.ajaxQJsMethod = method;
    },
    /**
     * ajax html 요청시 method 설정
     */
    setAjaxQHtmlMethod: function (method) {
        Lia.PageManager.ajaxQHtmlMethod = method;
    },
    /**
     * request할 파일 포멧 핸들러 설정
     */
    setFilePathFormatHandler: function (handler) {
        Lia.PageManager.filePathFormatHandler = handler;
    },

    /**
     * request할 css 파일 포멧 핸들러 설정
     */
    setCssFilePathFormatHandler: function (handler) {
        Lia.PageManager.cssFilePathFormatHandler = handler;
    },

    /**
     * request할 html 파일 포멧 핸들러 설정
     */
    setHtmlFilePathFormatHandler: function (handler) {
        Lia.PageManager.htmlFilePathFormatHandler = handler;
    },

    /**
     * reqeust할 js 파일 포멧 핸들러 설정
     */
    setJsFilePathFormatHandler: function (handler) {
        Lia.PageManager.jsFilePathFormatHandler = handler;
    },

    /**
     * 진행 상황 객체
     */
    onProgress: function (status, parameterMap, beforeParameterMap) {
    },

    /**
     * 진행 상황 리스터 등록
     */
    setOnProgress: function (listener) {
        Lia.PageManager.onProgress = listener;
    },


    /**
     * 파리미터 얻기
     */
    getParameter: function (key, map) {

        var parameterMap = (map == undefined) ? Lia.PageManager.parameterMap : map;
        if (parameterMap == undefined)
            return '';

        var r = parameterMap[key];
        if (r == undefined)
            return '';

        return r;
    },

    /**
     * 파리미터 얻기 : 공백 - undefined로
     */
    getParameterWithChecking: function (key, map) {

        var parameter = Lia.PageManager.getParameter(key, map);
        if (String.isNullOrWhitespace(parameter))
            return undefined;

        return parameter;
    },

    /**
     * 파리미터 얻기 : 공백 - undefined로
     */
    getParameterWithCheckingAndDefault: function (defaultValue, key, map) {

        var parameter = Lia.PageManager.getParameterWithChecking(key, map);
        if (parameter == undefined)
            return defaultValue;

        return parameter;
    },


    /**
     * 이전 파라미터 얻기
     */
    getBeforeParameter: function (key) {

        return Lia.PageManager.getParameter(key, Lia.PageManager.beforeParameterMap);
    },

    /**
     * 이전 파리미터 얻기
     */
    getBeforeParameterWithChecking: function (key) {

        var parameter = Lia.PageManager.getBeforeParameter(key);
        if (String.isNullOrWhitespace(parameter))
            return undefined;

        return parameter;
    },

    getBeforeParameterWithCheckingAndDefault: function (defaultValue, key) {

        var parameter = Lia.PageManager.getBeforeParameterWithChecking(key);
        if (parameter == undefined)
            return defaultValue;

        return parameter;
    },

    /**
     * 현재 페이지로 파라미터만 변경해서 이동
     */
    goCurrentPage: function (parameterMap) {

        Lia.PageManager.goPage(undefined, parameterMap, false);
    },

    /**
     * 현재 페이지로 현제 페이지로 이동
     */
    goCurrentPageWithCurrentParameterMap: function (parameterMap) {

        Lia.PageManager.goPage(undefined, parameterMap, true);
    },

    /**
     * 현재 페이지로 기준으로 이동
     */
    goPage: function (name, parameterMap, withCurrentParameter) {

        // 파라미터 체크
        if (name == undefined)
            name = [];
        if (typeof name == "string")
            name = [name];

        var resultParameterMap = {};

        // 그전 파라미터 넣어줌
        var beforeParameterMap = Lia.PageManager.parameterMap;
        if (withCurrentParameter && beforeParameterMap != undefined) {

            for (var key in beforeParameterMap) {

                resultParameterMap[key] = beforeParameterMap[key];
            }
        }

        // 현재 메뉴관련 파라미터 입력해줌
        if (beforeParameterMap != undefined && name != undefined) {

            var depth = Lia.PageManager.depth;
            var nameStartIndex = depth - (name.length - 1);
            for (var i = 0; i <= depth; i++) {

                var menuKey = Lia.PageManager.getMenuKey(i);
                if (i < nameStartIndex) {
                    resultParameterMap[menuKey] = beforeParameterMap[menuKey];
                } else {
                    resultParameterMap[menuKey] = name[i - nameStartIndex];
                }
            }
        }

        // 입력한 파라미터 입력
        if (parameterMap != undefined) {

            for (var key in parameterMap) {


                if (!String.isNullOrWhitespace(parameterMap[key])) {
                    resultParameterMap[key] = parameterMap[key];
                } else {
                    delete resultParameterMap[key];
                }
            }
        }

        Lia.PageManager.move(resultParameterMap);
    },

    /**
     * 현제 페이지 기준으로 기존 파라미터와 함꼐 이동
     */
    goPageWithCurrentParameterMap: function (name, parameterMap) {

        Lia.PageManager.goPage(name, parameterMap, true);
    },

    /**
     * 페이지 이동
     */
    go: function (name, parameterMap, withCurrentParameter) {

        // 파라미터 체크
        if (typeof name == "string")
            name = [name];

        var resultParameterMap = {};

        // 그전 파라미터 넣어줌
        var beforeParameterMap = Lia.PageManager.parameterMap;
        if (withCurrentParameter && beforeParameterMap != undefined) {

            for (var key in beforeParameterMap) {

                resultParameterMap[key] = beforeParameterMap[key];
            }
        }

        // 이름 입력되어 있으면 해당 내용 적용
        if (name != undefined) {

            var nameLength = name.length;

            for (var i = 0, l = Math.max(nameLength - 1, Lia.PageManager.depth); i <= l; i++) {

                var menuKey = Lia.PageManager.getMenuKey(i);

                if (i < nameLength) {

                    resultParameterMap[menuKey] = name[i];

                } else {

                    resultParameterMap[menuKey] = undefined;
                    delete resultParameterMap[menuKey];
                }
            }
        }

        // 입력한 파라미터 입력
        if (parameterMap != undefined) {

            for (var key in parameterMap) {

                if (!String.isNullOrWhitespace(parameterMap[key])) {
                    resultParameterMap[key] = parameterMap[key];
                } else {
                    delete resultParameterMap[key];
                }
            }
        }

        Lia.PageManager.move(resultParameterMap);
    },

    /**
     * 현재 페이지와 함꼐 이동
     */
    goWithCurrentParameterMap: function (name, parameterMap) {

        Lia.PageManager.go(name, parameterMap, true);

    },

    /**
     * 파라미터 대로 이동
     */
    move: function (parameterMap) {

        if (!Lia.PageManager.onMoveCheck(parameterMap))
            return;

        if ( Lia.PageManager.executingChangeWhenSameParameterMap == true ) {

            // 같으면 change 실행시키고 리턴
            if ( Lia.isSameMapWithoutBlank(Lia.PageManager.parameterMap, parameterMap) ) {

                Lia.PageManager.pageExecuteChange();
                return;
            }
        }

        if (Lia.PageManager.parameterPostfixAdding) {
            parameterMap = Lia.PageManager.encodeParameter(Lia.deepCopy(parameterMap));
        }

        Lia.PageManager.History.pushState(null, Lia.PageManager.title, Lia.convertArrayToQueryString(parameterMap, Lia.PageManager.uriConversionType));
    },

    /**
     * 페이지 파라미터 변경
     */
    replace: function (parameterMap) {

        if (!Lia.PageManager.onMoveCheck(parameterMap))
            return;

        if (Lia.PageManager.parameterPostfixAdding) {
            parameterMap = Lia.PageManager.encodeParameter(Lia.deepCopy(parameterMap));
        }

        Lia.PageManager.History.replaceState(null, Lia.PageManager.title, Lia.convertArrayToQueryString(parameterMap, Lia.PageManager.uriConversionType));
    },

    /**
     * 다른 페이지로 이동
     */
    redirect: function (url, name, parameterMap, options) {

        // 파라미터 체크
        if (name != undefined && typeof name == "string")
            name = [name];

        var resultParameterMap = {};

        // 이름 입력되어 있으면 해당 내용 적용
        if (name != undefined) {

            for (var i = 0, l = name.length; i < l; i++) {
                var menuKey = Lia.PageManager.getMenuKey(i);
                resultParameterMap[menuKey] = name[i];
            }
        }

        // 입력한 파라미터 입력
        if (parameterMap != undefined) {

            for (var key in parameterMap) {

                if (!String.isNullOrWhitespace(parameterMap[key])) {
                    resultParameterMap[key] = parameterMap[key];
                } else {
                    delete resultParameterMap[key];
                }
            }
        }

        var parameterPostfixAdding = Lia.pcd(Lia.PageManager.parameterPostfixAdding, options, 'parameterPostfixAdding');
        if (parameterPostfixAdding) {
            resultParameterMap = Lia.PageManager.encodeParameter(resultParameterMap);
        }

        Lia.redirect(url, resultParameterMap);
    },


    createRedirectUrl: function (url, name, parameterMap) {

        // 파라미터 체크
        if (name != undefined && typeof name == "string")
            name = [name];

        var resultParameterMap = {};

        // 이름 입력되어 있으면 해당 내용 적용
        if (name != undefined) {
            for (var i = 0, l = name.length; i < l; i++) {
                var menuKey = Lia.PageManager.getMenuKey(i);
                resultParameterMap[menuKey] = name[i];
            }
        }

        // 입력한 파라미터 입력
        if (parameterMap != undefined) {

            for (var key in parameterMap) {

                if (!String.isNullOrWhitespace(parameterMap[key])) {
                    resultParameterMap[key] = parameterMap[key];
                } else {
                    delete resultParameterMap[key];
                }
            }
        }

        if (Lia.PageManager.parameterPostfixAdding) {
            resultParameterMap = Lia.PageManager.encodeParameter(resultParameterMap);
        }


        return url + Lia.convertArrayToQueryString(resultParameterMap);
    },


    open: function (url, name, parameterMap, options) {

        // 파라미터 체크
        if (name != undefined && typeof name == "string")
            name = [name];

        var resultParameterMap = {};

        // 이름 입력되어 있으면 해당 내용 적용
        if (name != undefined) {
            for (var i = 0, l = name.length; i < l; i++) {
                var menuKey = Lia.PageManager.getMenuKey(i);
                resultParameterMap[menuKey] = name[i];
            }
        }

        // 입력한 파라미터 입력
        if (parameterMap != undefined) {

            for (var key in parameterMap) {

                if (!String.isNullOrWhitespace(parameterMap[key])) {
                    resultParameterMap[key] = parameterMap[key];
                } else {
                    delete resultParameterMap[key];
                }
            }
        }

        if (Lia.PageManager.parameterPostfixAdding) {
            resultParameterMap = Lia.PageManager.encodeParameter(resultParameterMap);
        }


        Lia.PageManager.requesterOpen(url, resultParameterMap, options);
    },


    /**
     * 뒤로 이동
     */
    back: function () {

        Lia.PageManager.History.back();
    },

    forward: function () {

        Lia.PageManager.History.forward();
    },

    /**
     * 함수 등록 및 초기화
     *
     * title
     * pageParameterNameList
     * cssLoading
     * htmlLoading
     * jsLoading
     * onProgress
     * onMoveCheck
     * onPageCheck
     * onPageInit
     * onPageRelease
     * onPageAdd
     * onPageRemove
     * onPageChange
     * onPageSwitchStart
     * onPageSwitchEnd
     * onNormalizeParameter
     * filePathFormatHandler
     * cssFilePathFormatHandler
     * htmlFilePathFormatHandler
     * jsFilePathFormatHandler
     * pageContainerSelectorList
     * ajaxQSync
     * ajaxQCssMethod
     * ajaxQJsMethod
     * ajaxQHtmlMethod
     * usingParameterMapWhenRequest
     * executingChangeWhenSameParameterMap
     *
     * uriConversionType
     *
     * parameterPostfixAdding
     * parameterPostfix
     *
     * requester
     *
     */
    set: function (options) {

        for (var key in options) {

            var value = options[key];
            Lia.PageManager[key] = value;
        }
    },


    init: function (options) {

        Lia.PageManager.set(options);

        if (Lia.PageManager.requester == undefined)
            Lia.PageManager.requester = new Lia.Requester();

        Lia.PageManager.bind();
    },

    /**
     * 주소 바인드
     */
    bind: function () {

        window.document.title = Lia.PageManager.title;

        // # ? 형태의 주소가 붙어잇으면 bind, statechange 함수 에서 호출되므로 호출할 필요 없음
        var doCheck = false;
        var state = Lia.PageManager.History.getState();
        var url = state.url;
        if (!String.isNullOrWhitespace(url)) {
            var sharpIndex = url.lastIndexOf('#');
            if (sharpIndex == -1 || url.indexOf('?', sharpIndex) == -1)
                doCheck = true;
        }

        Lia.PageManager.History.Adapter.bind(window, 'statechange', function () {
            Lia.PageManager.checkPage();
        });

        // 바인딩이 되고 나서 체크해주어야지 페이지 이동이 된다.
        if (doCheck)
            Lia.PageManager.checkPage();
    },

    /**
     * 인덱스에 맞는 메뉴 키 얻음
     */
    getMenuKey: function (i) {

        if (Lia.PageManager.pageParameterNameList == undefined) {
            return undefined;
        }

        return Lia.PageManager.pageParameterNameList[i];
    },

    /**
     * 인덱스에 맞는 메뉴 파라미터 얻음
     */
    getMenuParameter: function (i, map) {

        var key = Lia.PageManager.getMenuKey(i);
        if (String.isNullOrWhitespace(key)) {
            return '';
        }

        var parameterMap = (map == undefined) ? Lia.PageManager.parameterMap : map;
        return Lia.PageManager.getParameter(key, parameterMap);
    },

    /**
     * 인덱스에 맞는 메뉴 전 파라미터 얻음
     */
    getBeforeMenuParameter: function (i) {

        return Lia.PageManager.getMenuParameter(i,
            Lia.PageManager.beforeParameterMap);
    },

    /**
     * 페이지 객체 얻음
     * (인자값 없다면 제일 마지막 객체)
     */
    getPage: function (i) {

        if (Lia.PageManager.pageList == undefined) {
            return undefined;
        }

        if (i == undefined) {
            i = Lia.PageManager.depth;
        }

        return Lia.PageManager.pageList[i];
    },

    getPageList: function () {
        return Lia.PageManager.pageList;
    },

    getDepth: function () {
        return Lia.PageManager.depth;
    },

    pageExecute: function (name, object) {

        var pageList = Lia.PageManager.pageList;
        var depth = PageManager.depth;
        if (pageList != undefined && depth != undefined) {

            for (var i = 0, l = depth; i <= l; i++) {

                var page = pageList[i];
                if (page != undefined) {
                    var member = page[name];
                    if (typeof member == "function") {
                        page[name](object);
                    }
                }
            }

        }
    },

    pageExecuteChange: function () {

        var depth = Lia.PageManager.depth;
        if (depth == undefined) {
            return;
        }

        var parameterMap = Lia.PageManager.getParameterMap();
        var beforeParameterMap = Lia.PageManager.getBeforeParameterMap();

        for (var i = 0; i <= depth; i++) {

            var page = Lia.PageManager.pageList[i];
            if (page != undefined) {
                var jPage = page.getJPage();
                var jPageContainer = page.getJPageContainer();

                Lia.PageManager.onPageChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);

                if (page.onChange != undefined) {

                    if (Lia.debugMode) {
                        page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                    } else {
                        try {
                            page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                        } catch (err) {
                        }
                    }
                }
            }
        }
    },

    pageExecuteChangeAt: function (depth) {

        var page = Lia.PageManager.pageList[depth];

        var parameterMap = Lia.PageManager.getParameterMap();
        var beforeParameterMap = Lia.PageManager.getBeforeParameterMap();

        if (page != undefined) {
            var jPage = page.getJPage();
            var jPageContainer = page.getJPageContainer();

            Lia.PageManager.onPageChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);


            if (page.onChange != undefined) {

                if (Lia.debugMode) {
                    page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                } else {
                    try {
                        page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                    } catch (err) {
                    }
                }
            }
        }
    },

    pageExecuteChangeLast: function () {

        var depth = Lia.PageManager.depth;
        Lia.PageManager.pageExecuteChangeAt(depth);
    },

    encodeParameter: function (object, parameterPostfixAdding) {

        if (parameterPostfixAdding == undefined) {
            parameterPostfixAdding = Lia.PageManager.parameterPostfixAdding;
        }

        if (parameterPostfixAdding) {

            if (typeof object == "object") {

                for (var key in object) {
                    object[key] = Lia.PageManager.encodeParameter(object[key], parameterPostfixAdding);
                }

            } else {

                object += Lia.PageManager.parameterPostfix;
            }
        }

        return object;

    },

    redirectUrlIfEncoded : function( url ) {

        if ( String.isNotBlank(url) ) {
            url = window.location.href;
        }

        var idx = url.lastIndexOf('?');
        if ( idx == -1 ) {
            return;
        }
        
        var baseUrl = url.substring(0, idx);
        var parameterString = url.substring(idx + 1);

        var encoded = false;
        var parameterMap = Lia.convertQueryStringToArray(parameterString, Lia.PageManager.uriConversionType);

        var newParameterMap = {};
        for ( var key in parameterMap ) {

            var object = Lia.p(parameterMap, key);
            while (!String.isNullOrWhitespace(object)) {

                var decoded = Lia.decodeUriSafety(object, Lia.PageManager.uriConversionType);
                if (object.endsWith(Lia.PageManager.parameterPostfix)) {
                    encoded = true;
                    object = object.substring(0, object.length - 1);
                    break;
                } else if (object == decoded) {
                    break;
                }

                object = decoded;
            }

            newParameterMap[key] = object;
        }

        if ( encoded ) {
            Lia.redirect(baseUrl, newParameterMap);
        }
    },

    decodeParameter: function (object, parameterPostfixAdding) {

        if (parameterPostfixAdding == undefined) {
            parameterPostfixAdding = Lia.PageManager.parameterPostfixAdding;
        }

        var parameterDecoding = Lia.PageManager.parameterDecoding;
        if (parameterPostfixAdding || parameterDecoding ) {

            if (typeof object == "object") {

                for (var key in object) {
                    object[key] = Lia.PageManager.decodeParameter(object[key], parameterPostfixAdding);
                }

            } else {

                while (!String.isNullOrWhitespace(object)) {

                    var decoded = Lia.decodeUriSafety(object, Lia.PageManager.uriConversionType);
                    if (object.endsWith(Lia.PageManager.parameterPostfix)) {
                        object = object.substring(0, object.length - 1);
                        break;
                    } else if (object == decoded) {
                        break;
                    }

                    object = decoded;
                }
            }
        }

        return object;
    },

    /**
     * 현재 페이지 인자값 검사
     */
    checkPage: function () {

        var state = Lia.PageManager.History.getState();
        var url = state.url;

        if (String.isNullOrWhitespace(url))
            return;

        // 같인 요청이 들어올 때 체크하여 스킵
        var originalParameterMap = Lia.extractGetParameterMapFromUrl(url, Lia.PageManager.uriConversionType);
        var beforeOriginalParameterMap = Lia.PageManager.originalParameterMap;
        if (beforeOriginalParameterMap != undefined) {

            var originalSame = true;
            for (var key in originalParameterMap) {

                if (key == Lia.PageManager.Constants.SUID)
                    continue;

                if (originalParameterMap[key] != beforeOriginalParameterMap[key]) {
                    originalSame = false;
                    break;
                }
            }

            if (originalSame == true) {

                for (var key in beforeOriginalParameterMap) {

                    if (key == Lia.PageManager.Constants.SUID)
                        continue;

                    if (originalParameterMap[key] != beforeOriginalParameterMap[key]) {
                        originalSame = false;
                        break;
                    }
                }

                if (originalSame == true)
                    return;
            }
        }

        Lia.PageManager.originalParameterMap = originalParameterMap;
        Lia.PageManager.beforeOriginalParameterMap = beforeOriginalParameterMap;

        var parameterMap = Lia.PageManager.onNormalizeParameter(
            Lia.PageManager.decodeParameter(Lia.deepCopy(originalParameterMap))
        );

        if (!Lia.PageManager.onPageCheck(parameterMap)) {
            return;
        }

        var depth = 0;
        var path = null;
        var paths = [];
        while (true) {
            var menu = parameterMap[Lia.PageManager.getMenuKey(depth)];

            if (String.isNullOrWhitespace(menu))
                break;

            if (path == null) {
                path = menu;
            } else {
                path += '/' + menu;
            }

            paths[depth++] = path;
        }
        --depth;


        var beforeDepth = Lia.PageManager.depth;
        var beforeParameterMap = Lia.PageManager.parameterMap;
        var baseDepth = beforeDepth + 1;

        // 페이지 refresh 일때 체크하자
        if ( Lia.PageManager.onRefreshCheck(parameterMap) ) {

            // refresh check
            baseDepth = 0;

        } else {

            // 언제까지 언로드하여여야 할 지 체크
            // baseDepth 미만 onChange
            // baseDepth 이상 새로받음
            for (var i = beforeDepth; i >= 0; i--) {
                var menuKey = Lia.PageManager.getMenuKey(i);
                if (parameterMap[menuKey] != undefined && parameterMap[menuKey] != beforeParameterMap[menuKey]) {
                    baseDepth = i;
                }
            }
        }

        Lia.PageManager.depth = depth;
        Lia.PageManager.beforeDepth = beforeDepth;
        Lia.PageManager.parameterMap = parameterMap;
        Lia.PageManager.beforeParameterMap = beforeParameterMap;

        Lia.PageManager.onProgress(Lia.PageManager.Status.START, parameterMap, beforeParameterMap);

        // 메뉴 파라미터 관련 현하지 않음
        var same = (depth == beforeDepth && baseDepth == beforeDepth + 1);
        if (same) {

            Lia.PageManager.onPageSwitchStart(depth, depth, depth, parameterMap, beforeParameterMap, false);

            Lia.PageManager.pageExecuteChange();

            Lia.PageManager.onPageSwitchEnd(depth, depth, depth, parameterMap, beforeParameterMap, false);

            Lia.PageManager.onProgress(Lia.PageManager.Status.SUCCESS, parameterMap, beforeParameterMap);

        } else {

            // 필요한 만큼 요청
            Lia.PageManager.request(baseDepth, depth, beforeDepth, paths, parameterMap, beforeParameterMap);
        }
    },

    request: function (baseDepth, depth, beforeDepth, paths, parameterMap, beforeParameterMap) {


        // 기존 기록 삭제
        for (var i = baseDepth; i <= depth; i++) {

            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.CSS][i] = undefined;
            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.HTML][i] = undefined;
            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.JS][i] = undefined;
        }

        // js 기록
        if (Lia.PageManager.jsLoading) {

            for (var i = baseDepth; i <= depth; i++) {

                var path = Lia.PageManager.filePathFormatHandler(paths[i], parameterMap, i);
                if (path != undefined) {

                    var jsUrl = Lia.PageManager.jsFilePathFormatHandler(path, parameterMap, i);
                    if (jsUrl != undefined) {

                        if (Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.JS][path] != undefined) {

                            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.JS][i] =
                                Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.JS][path];

                        } else {

                            Lia.PageManager.requesterRequest(jsUrl, function (status, data, request) {

                                var object = request['object'];
                                if (status == Lia.Requester.Status.ERROR || object == undefined) {

                                    Lia.PageManager.requesterAbort();
                                    Lia.PageManager.onProgress(Lia.PageManager.Status.ERROR, Lia.PageManager.parameterMap, Lia.PageManager.beforeParameterMap);
                                    return;
                                }

                                var index = object['index'];
                                Lia.PageManager.pageContentList[Lia.PageManager.ContentType.JS][index] = data;

                            }, Lia.PageManager.ajaxQJsMethod, Lia.PageManager.usingParameterMapWhenRequest == true ? parameterMap : undefined, {
                                index: i
                            });
                        }

                    }
                }
            }
        }

        Lia.PageManager.requesterExecute(function (execute) {

            var object = execute['object'];
            var depth = object['depth'];
            var parameterMap = object['parameterMap'];
            var baseDepth = object['baseDepth'];
            var beforeParameterMap = object['beforeParameterMap'];
            var beforeDepth = object['beforeDepth'];

            var pageList = [];

            // 페이지 생성
            for (var i = baseDepth; i <= depth; i++) {

                var page = new Lia.Page();

                var pageJs = Lia.PageManager.pageContentList[Lia.PageManager.ContentType.JS][i];
                if (pageJs != undefined) {

                    if (Lia.debugMode) {

                        page.extend(eval(pageJs));

                    } else {

                        try {
                            page.extend(eval(pageJs));
                        } catch (err) {
                        }
                    }
                }

                pageList[i] = page;

                // html 로딩
                var path = Lia.PageManager.filePathFormatHandler(paths[i], parameterMap, i);
                if (path == undefined)
                    continue;

                var htmlLoading = Lia.pd(Lia.PageManager.htmlLoading, page.checkHtmlLoading());
                if (htmlLoading) {

                    var htmlUrl = Lia.PageManager.htmlFilePathFormatHandler(path, parameterMap, i);
                    if (htmlUrl != undefined) {

                        if (Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.HTML][path] != undefined) {

                            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.HTML][i] =
                                Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.HTML][path];

                        } else {

                            Lia.PageManager.requesterRequest(htmlUrl, function (status, data, request) {

                                var object = request['object'];
                                if (status == Lia.Requester.Status.ERROR || object == undefined) {

                                    Lia.PageManager.requesterAbort();
                                    Lia.PageManager.onProgress(Lia.PageManager.Status.ERROR, Lia.PageManager.parameterMap, Lia.PageManager.beforeParameterMap);
                                    return;
                                }

                                var index = object['index'];
                                Lia.PageManager.pageContentList[Lia.PageManager.ContentType.HTML][index] = data;

                            }, Lia.PageManager.ajaxQJsMethod, Lia.PageManager.usingParameterMapWhenRequest == true ? parameterMap : undefined, {
                                index: i
                            });
                        }

                    }

                }

                var cssLoading = Lia.pd(Lia.PageManager.cssLoading, page.checkCssLoading());
                if (cssLoading) {

                    var cssUrl = Lia.PageManager.cssFilePathFormatHandler(path, parameterMap, i);
                    if (cssUrl != undefined) {


                        if (Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.CSS][path] != undefined) {

                            Lia.PageManager.pageContentList[Lia.PageManager.ContentType.CSS][i] =
                                Lia.PageManager.preparedContentMap[Lia.PageManager.ContentType.CSS][path];

                        } else {

                            Lia.PageManager.requesterRequest(cssUrl, function (status, data, request) {

                                var object = request['object'];
                                if (status == Lia.Requester.Status.ERROR || object == undefined) {

                                    Lia.PageManager.requesterAbort();
                                    Lia.PageManager.onProgress(Lia.PageManager.Status.ERROR, Lia.PageManager.parameterMap, Lia.PageManager.beforeParameterMap);
                                    return;
                                }

                                var index = object['index'];
                                Lia.PageManager.pageContentList[Lia.PageManager.ContentType.CSS][index] = data;

                            }, Lia.PageManager.ajaxQJsMethod, Lia.PageManager.usingParameterMapWhenRequest == true ? parameterMap : undefined, {
                                index: i
                            });
                        }


                    }
                }
            }


            // 페이지 리스트 담기
            object['pageList'] = pageList;

            // 페이지 처리
            Lia.PageManager.requesterExecute(function (execute) {

                var object = execute['object'];

                var parameterMap = object['parameterMap'];
                var beforeParameterMap = object['beforeParameterMap'];
                var depth = object['depth'];
                var baseDepth = object['baseDepth'];
                var beforeDepth = object['beforeDepth'];
                var pageList = object['pageList'];

                Lia.PageManager.onPageSwitchStart(beforeDepth, baseDepth, depth, parameterMap, beforeParameterMap, true);

                // onRelease
                for (var i = beforeDepth; i >= baseDepth; i--) {

                    var page = Lia.PageManager.pageList[i];
                    if (page != undefined) {

                        var jPage = page.getJPage();
                        var jPageContainer = page.getJPageContainer();

                        if (page.onRelease != undefined) {

                            if (Lia.debugMode) {
                                page.onRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                            } else {
                                try {
                                    page.onRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                                } catch (err) {
                                }
                            }


                        }

                        Lia.PageManager.onPageRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                        Lia.PageManager.onPageRemove(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                        Lia.PageManager.pageList[i] = undefined;
                    }
                }

                // onInit
                for (var i = baseDepth; i <= depth; i++) {

                    var pageSelector = Lia.PageManager.pageContainerSelectorList[i];
                    if (pageSelector != undefined) {

                        var text = '<div>';
                        var css = Lia.PageManager.pageContentList[Lia.PageManager.ContentType.CSS][i];
                        if (css != undefined)
                            text += '<style type="text/css">' + css + '</style>';

                        var html = Lia.PageManager.pageContentList[Lia.PageManager.ContentType.HTML][i];
                        if (html != undefined)
                            text += html;
                        text += '</div>';

                        var jPageContainer = jQuery(pageSelector);
                        var jPage = jQuery(text);

                        Lia.PageManager.onPageAdd(jPage, jPageContainer, i, parameterMap, beforeParameterMap);

                        var page = pageList[i];
                        page.set({
                            jPage: jPage,
                            jPageContainer: jPageContainer
                        });

                        Lia.PageManager.pageList[i] = page;
                        Lia.PageManager.onPageInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);

                        if (page != undefined && page.onInit != undefined) {

                            if (Lia.debugMode) {
                                page.onInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                            } else {

                                try {
                                    page.onInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                                } catch (err) {
                                }
                            }


                        }
                    }
                }

                // onChange
                for (var i = 0; i <= depth; i++) {

                    var page = Lia.PageManager.pageList[i];
                    if (page != undefined) {

                        var jPage = page.getJPage();
                        var jPageContainer = page.getJPageContainer();

                        Lia.PageManager.onPageChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);

                        if (page.onChange != undefined) {

                            if (Lia.debugMode) {
                                page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                            } else {
                                try {
                                    page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
                                } catch (err) {
                                }
                            }


                        }
                    }
                }

                Lia.PageManager.onPageSwitchEnd(beforeDepth, baseDepth, depth, parameterMap, beforeParameterMap, true);

                Lia.PageManager.onProgress(Lia.PageManager.Status.SUCCESS, Lia.PageManager.parameterMap, Lia.PageManager.beforeParameterMap);

            }, object);


        }, {
            parameterMap: parameterMap,
            beforeParameterMap: beforeParameterMap,
            depth: depth,
            baseDepth: baseDepth,
            beforeDepth: beforeDepth
        });
    },

    /**
     * 파일 요청
     */
    requesterRequest: function (url, onResponse, method, parameterMap, object) {

        var request = {
            url: url,
            onResponse: onResponse,
            object: object,
            parameterMap: parameterMap,
            method: method,

            ajaxQSync: Lia.PageManager.ajaxQSync,
            q: true,
            dataType: 'text'
        };

        Lia.PageManager.requester.request(request);
    },

    requesterExecute: function (onExecute, object) {

        var execute = {
            onExecute: onExecute,
            object: object
        };

        Lia.PageManager.requester.execute(execute);
    },

    requesterOpen: function (url, resultParameterMap, options) {

        Lia.PageManager.requester.open(url, resultParameterMap, options);
    },


    requesterAbort: function () {

        Lia.PageManager.requester.abort();
    }

};

// 별칭
Lia.PageManager.p = Lia.PageManager.getParameter;
Lia.PageManager.pc = Lia.PageManager.getParameterWithChecking;
Lia.PageManager.pcd = Lia.PageManager.getParameterWithCheckingAndDefault;
Lia.PageManager.cp = Lia.PageManager.goCurrentPage;
Lia.PageManager.cpcpm = Lia.PageManager.goCurrentPageWithCurrentParameterMap;
Lia.PageManager.pcpm = Lia.PageManager.goPageWithCurrentParameterMap;
Lia.PageManager.cpm = Lia.PageManager.goWithCurrentParameterMap;


/**
 * image_box check
 <img class="image_box check" data-lia-src="{이미지 주소}" />
 * 체크 되었을 때 _pressed.png 파일 보임
 *
 * image_box radio
 <img class="image_box radio"
 data-lia-src="{이미지 주소}"
 data-lia-group="{그룹 명}" />
 * 선택 되었을 때 _pressed.png 파일 보임
 *
 * $.imageBoxRadioGroup(groupId)
 *  선택된 객체 리턴
 * $.imageBoxRadioGroup(groupId, selector)
 *  그룹의 selector를 선택
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initButtonGroup();
 });

 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initButtonGroup: function (j) {

            var selector = '.' + Lia.Component.Name.BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON_CONTAINER + ', .' + Lia.Component.Name.IMAGE_BOX + ', .' + Lia.Component.Name.FLAT_BUTTON;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            j.filter('.' + Lia.Component.Flag.RADIO).initButtonRadio();
            j.filter('.' + Lia.Component.Flag.CHECK).initButtonCheck();

            return j;
        },

        /**
         * 그룹 선택, 선택된 것 리턴
         *   선택되어 있지 않으면 null 리턴
         *   선택된 것 jquery 객체 리턴
         *
         * @param groupId
         * @param jItem
         * @returns {*}
         */
        buttonGroup: function (groupId, jItem) {

            if (jItem == undefined) {
                var jSelectedRadio = jQuery('.' + Lia.Component.Name.BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON_CONTAINER + ', .' + Lia.Component.Name.IMAGE_BOX + ', .' + Lia.Component.Name.FLAT_BUTTON)
                    .filter('.' + Lia.Component.Flag.RADIO + '.' + Lia.Component.Flag.PRESSED).filter('[' + Lia.Component.AttrName.GROUP + '="' + groupId + '"], [data-' + Lia.Component.AttrName.GROUP + '="' + groupId + '"]');

                return jSelectedRadio;
            }

            var isDisabled = jItem.hasClass(Lia.Component.Flag.DISABLED);
            if (isDisabled)
                return;

            var jRadioGroup = jQuery('.' + Lia.Component.Name.BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON + ', .' + Lia.Component.Name.IMAGE_BUTTON_CONTAINER + ', .' + Lia.Component.Name.IMAGE_BOX + ', .' + Lia.Component.Name.FLAT_BUTTON)
                .filter('.' + Lia.Component.Flag.RADIO).filter('[' + Lia.Component.AttrName.GROUP + '="' + groupId + '"], [data-' + Lia.Component.AttrName.GROUP + '="' + groupId + '"]');

            var jBefore = jRadioGroup.filter('.pressed').not(jItem);
            jBefore.buttonPressed(false);
        }

    });


    $.fn.extend({

        initButtonRadio: function () {

            return this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.RADIO_INITED))
                    return;

                jThis.on(Lia.Component.Event.STATUS_CHANGED, function (e) {

                    var jThis = jQuery(this);
                    var isDisabled = jThis.hasClass(Lia.Component.Flag.DISABLED);
                    if (isDisabled)
                        return;

                    var group = jThis.dataAttr(Lia.Component.AttrName.GROUP);
                    if (group == undefined)
                        return;

                    var status = e.status;
                    if (status == Lia.Component.Value.Button.Status.PRESSED) {
                        $.buttonGroup(group, jThis);
                    }
                });

                if (!jThis.hasClass(Lia.Component.Flag.NO_BIND)) {

                    var eventName = Lia.isMobile ? 'touchstart' : 'mousedown';
                    jThis.on(eventName, function () {
                        var jThis = jQuery(this);
                        jThis.buttonPressed(true);
                    });
                }

                jThis.addClass(Lia.Component.Flag.RADIO_INITED);
            });

        },

        initButtonCheck: function () {

            return this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.CHECK_INITED))
                    return;

                if (!jThis.hasClass(Lia.Component.Flag.NO_BIND)) {

                    if (!jThis.hasClass(Lia.Component.Flag.NO_BIND)) {

                        var eventName = Lia.isMobile ? 'touchstart' : 'mousedown';
                        jThis.on(eventName, function () {
                            var jThis = jQuery(this);
                            jThis.buttonPressed(!jThis.buttonPressed());
                        });
                    }

                }

                jThis.addClass(Lia.Component.Flag.CHECK_INITED);
            });

        }


    });

})(jQuery);

/**
 * popup loading
 *
 *  <div class="dim [cancelable]" data-lia-z-index="{z-index 값}" data-lia-popup="{연결된 Popup Selector}" data-lia-dim-background-color></div>
 *  <div id="info_popup" class="popup loading" style="width:{popup width};height:{popup height}" data-lia-z-index="{z-index 값}" data-lia-dim="{사용할 Dim Selector}">
 *      <img class="loading_indicator" data-lia-src="{img 주소 format:/loading/{index}.png}" data-lia-index="{현재 인덱스}" data-lia-start-index="{시작 인덱스}" data-lia-end-index="{끝인덱스}" />
 *  </div>
 */
/*
 초기화 코드

 뷰에 붙이고 나서 start 해야함
 $(document).ready(function () {

 $.initPopupLoading();
 });

 */

jQuery.extend({

    liaLoadingPopupAttrNames: [
        Lia.Component.AttrName.SRC,
        Lia.Component.AttrName.START_INDEX,
        Lia.Component.AttrName.END_INDEX
    ],

    initPopupLoading: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP + '.' + Lia.Component.Flag.LOADING;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.initPopupLoading();
    },

    showPopupLoading: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP + '.' + Lia.Component.Flag.LOADING;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.showPopupLoading();
    },

    hidePopupLoading: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP + '.' + Lia.Component.Flag.LOADING;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.hidePopupLoading();
    },

    clearPopupLoading: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP + '.' + Lia.Component.Flag.LOADING;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.clearPopupLoading();
    },

    clearAndHidePopupLoading: function (j) {

        var selector = '.' + Lia.Component.Name.POPUP + '.' + Lia.Component.Flag.LOADING;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.clearAndHidePopupLoading();
    }
});

jQuery.fn.extend({

    initPopupLoading: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            if (jThis.hasClass(Lia.Component.Flag.LOADING_INITED))
                return;

            var jLoadingIndicator = jThis.children('.' + Lia.Component.Name.LOADING_INDICATOR);
            if (jLoadingIndicator.size() == 0) {

                jLoadingIndicator = jQuery('<img alt="loading indicator"/>');
                jLoadingIndicator.addClass(Lia.Component.Name.LOADING_INDICATOR);

                for (var key in jQuery.liaLoadingPopupAttrNames) {

                    if (!jQuery.liaLoadingPopupAttrNames.hasOwnProperty(key))
                        continue;

                    var value = jQuery.liaLoadingPopupAttrNames[key];
                    var attrValue = jThis.dataAttr(value);
                    if (attrValue != undefined)
                        jLoadingIndicator.dataAttr(value, attrValue);
                }

                jThis.append(jLoadingIndicator);
                jLoadingIndicator.initLoadingIndicator();
            }
            jThis.dataAttr(Lia.Component.AttrName.REFER_COUNT, 0);
            jThis.addClass(Lia.Component.Flag.LOADING_INITED);
        });
    },

    showPopupLoading: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            var referCount = Math.max(0, parseInt(jThis.dataAttr(Lia.Component.AttrName.REFER_COUNT)));
            if (referCount == 0) {
                jThis.children().playLoadingIndicator();
                jThis.showPopup();
            }

            jThis.dataAttr(Lia.Component.AttrName.REFER_COUNT, ++referCount);
        });
    },

    hidePopupLoading: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            var referCount = Math.max(0, parseInt(jThis.dataAttr(Lia.Component.AttrName.REFER_COUNT)) - 1);
            if (referCount == 0) {
                jThis.children().pauseLoadingIndicator();
                jThis.hidePopup();
            }

            jThis.dataAttr(Lia.Component.AttrName.REFER_COUNT, referCount);
        });
    },

    clearPopupLoading: function () {

        return this.dataAttr(Lia.Component.AttrName.REFER_COUNT, 0);
    },

    clearAndHidePopupLoading: function () {

        return this.clearPopupLoading().hidePopupLoading();
    }


});


/**
 * form parameter 할 수 있도록 도와줌
 *
 * class
 *  form_element
 *
 * attr
 *  data-lia-name ( form 전송 이름 )
 **/

var FormSerializer = jQuery.FormSerializer = Lia.FormSerializer = function (options) {

    this.init(options);
};

/**
 * 초기화
 */
Lia.FormSerializer.prototype.init = function (options) {
};

Lia.FormSerializer.Status = Lia.Component.Value.FormSerializer.Status;
Lia.FormSerializer.checkboxTrueValue = Lia.Component.Value.FormSerializer.Boolean.TRUE;
Lia.FormSerializer.checkboxFalseValue = Lia.Component.Value.FormSerializer.Boolean.FALSE;

/**
 * 올릴때의 체크 변수 설정 ( static 변수 설정 )
 *
 * @param type
 * @param value
 *
 */
Lia.FormSerializer.setCheckboxValue = function (type, value) {

    if (type == true)
        Lia.FormSerializer.checkboxTrueValue = value;
    else
        Lia.FormSerializer.checkboxFalseValue = value;
};

Lia.FormSerializer.getCheckboxValue = function (value) {

    if (value == true) {
        return Lia.FormSerializer.checkboxTrueValue;
    } else {
        return Lia.FormSerializer.checkboxFalseValue;
    }
};

Lia.FormSerializer.prototype.serialize = function (j) {

    //input radio checkbox
    //textarea
    //select
    //

    //- BUTTON : 'button',
    //- IMAGE_BUTTON : 'image_button',
    //- IMAGE_BOX : 'image_box',
    //- FLAT_BUTTON : 'flat_button',
    //- IMAGE_SELECT : 'image_select',

    //DIV_PLACEHOLDER_INPUT : 'div_placeholder_input',
    //TEXT_PLACEHOLDER_INPUT : 'text_placeholder_input',
    //IMAGE_INPUT : 'image_input',
    //TEXT_EDITOR : 'text_editor',

    var parameterMap = {};

    var selector = '.' + Lia.Component.Name.FORM_ELEMENT;

    var jFormElementList = undefined;
    if (j != undefined) {
        jFormElementList = j.find(selector);
    } else {
        jFormElementList = jQuery(selector);
    }

    while (jFormElementList.length > 0) {

        var index = jFormElementList.length - 1;

        var jFormElement = jFormElementList.eq(index);
        var name = jFormElement.dataAttr(Lia.Component.AttrName.NAME);
        if (String.isBlank(name)) {
            name = jFormElement.attr('name');
        }

        if (!String.isBlank(name)) {

            var value = undefined;

            if (jFormElement.hasClass(Lia.Component.Name.RADIO)) {

                var jRadio = jFormElementList.filter('.' + Lia.Component.Name.RADIO + '[' + Lia.Component.AttrName.NAME + '="' + name + '"]');
                value = jRadio.filter('.' + Lia.Component.Flag.PRESSED).dataAttr(Lia.Component.AttrName.VALUE);
                jFormElement = jRadio;

            } else if (jFormElement.hasClass(Lia.Component.Name.BUTTON)
                || jFormElement.hasClass(Lia.Component.Name.IMAGE_BUTTON)
                || jFormElement.hasClass(Lia.Component.Name.IMAGE_BOX)
                || jFormElement.hasClass(Lia.Component.Name.FLAT_BUTTON)) {

                value = Lia.FormSerializer.getCheckboxValue(jFormElement.buttonPressed());

            } else if (jFormElement.hasClass(Lia.Component.Name.IMAGE_SELECT)) {

                value = jFormElement.imageSelectVal();

            } else if (jFormElement.hasClass(Lia.Component.Name.DIV_PLACEHOLDER_INPUT)) {

                value = jFormElement.divPlaceholderInputVal();

            } else if (jFormElement.hasClass(Lia.Component.Name.TEXT_PLACEHOLDER_INPUT)) {

                value = jFormElement.textPlaceholderInputVal();

            } else if (jFormElement.hasClass(Lia.Component.Name.IMAGE_INPUT)) {

                value = jFormElement.imageInputVal();

            } else if (jFormElement.hasClass(Lia.Component.Name.TEXT_EDITOR)) {

                value = jFormElement.textEditorVal();

            } else if (jFormElement.hasClass(Lia.Component.Name.CODE_EDITOR)) {

                value = jFormElement.codeEditorVal();

            } else if (jFormElement.filter('input[type="checkbox"]').length > 0) {

                value = Lia.FormSerializer.getCheckboxValue(jFormElement.prop('checked'));

            } else if (jFormElement.filter('input[type="radio"]').length > 0) {

                var inputName = jFormElement.attr('name');
                var jRadio = jFormElementList.filter('input[type="radio"]][name="' + inputName + '"]');
                value = jRadio.filter(':checked').val();
                jFormElement = jRadio;

            } else if (jFormElement.filter('input, textarea, select').length > 0) {

                value = jFormElement.val();

            }

            parameterMap[name] = value;
        }

        jFormElementList = jFormElementList.not(jFormElement);

    }

    return parameterMap;
};
/**
 * image_button
 * 이미지 마우스 오버, 클릭시 이미지 변경
 *
 * <div class="image_box" data-lia-src="{이미지 주소}" />
 *      _pressed.png 가 클릭시 보여짐
 *
 * <div class="image_box hover" data-lia-src="{이미지 주소}" />
 *      _hovering.png 가 마우스 커서가 올라갈 대 보여짐
 *      _pressed.png 가 클릭시 보여짐
 *
 * <div class="image_box press" data-lia-src="{이미지 주소}" />*
 *      _pressed.png 가 마우스 커서가 올라갈 때, 클릭시 보여짐
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initImageBox();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initImageBox: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_BOX;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageBox();
        }
    });

    $.fn.extend({

        imageBoxPressed: function (pressed) {

            return this.buttonPressed(pressed);
        },

        setImageBoxByPressed: function (pressed) {

            for (var i = 0, l = this.length; i < l; i++) {
                var jThis = this.eq(i);

                var status = (pressed) ? Lia.Component.Value.Button.Status.PRESSED : Lia.Component.Value.Button.Status.DEFAULT;
                jThis.setImageBoxByStatus(status);
            }

            return this;
        },

        setImageBoxByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var imageBoxIndex = Lia.Component.Value.Button.ImageBox.DEFAULT_INDEX;
                if (status == Lia.Component.Value.Button.Status.PRESSED) {
                    imageBoxIndex = Lia.Component.Value.Button.ImageBox.PRESSED_INDEX;
                } else if (status == Lia.Component.Value.Button.Status.HOVERING) {
                    imageBoxIndex = Lia.Component.Value.Button.ImageBox.HOVERING_INDEX;
                }

                jThis.setImageBoxByIndex(imageBoxIndex);
            }

            return this;
        },

        setImageBoxByIndex: function (index) {


            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var imageBoxIndex = jThis.data(Lia.Component.Value.Button.ImageBox.IMAGE_BOX_INDEX);
                if (index == imageBoxIndex)
                    return;

                var jChildren = jThis.children();
                jChildren.eq(index).show();

                if (!String.isBlank(imageBoxIndex)) {
                    jChildren.eq(imageBoxIndex).hide();
                }

                jThis.data(Lia.Component.Value.Button.ImageBox.IMAGE_BOX_INDEX, index);

            }

            return this;

        },

        checkImageBoxByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var isButtonPress = jThis.hasClass(Lia.Component.Flag.PRESS);
                var isButtonHover = jThis.hasClass(Lia.Component.Flag.HOVER);

                var buttonStatus = Lia.Component.Value.Button.Status.DEFAULT;
                if (status == Lia.Component.Value.Button.Status.PRESSED || status == Lia.Component.Value.Button.Status.PRESSING || (isButtonPress && status == Lia.Component.Value.Button.Status.HOVERING)) {
                    buttonStatus = Lia.Component.Value.Button.Status.PRESSED;
                } else if (isButtonHover && status == Lia.Component.Value.Button.Status.HOVERING) {
                    buttonStatus = Lia.Component.Value.Button.Status.HOVERING;
                }

                jThis.setImageBoxByStatus(buttonStatus);
            }

            return this;
        },

        adjustImageBox: function () {

            return this.each(function () {

                var jThis = $(this);
                var jChildren = jThis.children();

                var jDefaultImage = jChildren.eq(Lia.Component.Value.Button.Status.ImageBox.DEFAULT_INDEX);
                var css = {
                    width: jDefaultImage.outerWidth(true),
                    height: jDefaultImage.outerHeight(true)
                };

                jChildren.css(css).eq(jChildren.length - 1).css(css);
            });
        },

        /**
         * image_button 초기화
         *
         * @returns {*}
         */
        initImageBox: function () {

            return this.initButton().each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.IMAGE_BOX_INITED))
                    return;

                jThis.addClass('inline_block');
                jThis.css({
                    'position': 'relative',
                    'overflow': 'hidden'
                });

                var imageBoxHover = jThis.hasClass(Lia.Component.Flag.HOVER);
                var path = jThis.dataAttr(Lia.Component.AttrName.SRC);
                path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);

                var jDefaultImage = $('<img />').css({
                    'position': 'absolute',
                    'top': 0,
                    'left': 0
                }).load(function () {

                    var jThis = $(this);
                    var jClickDiv = jThis.parent().children('div');
                    var css = {
                        width: jThis.outerWidth(true),
                        height: jThis.outerHeight(true)
                    };

                    jThis.css(css);
                    jClickDiv.css(css);

                }).attr({
                    'src': path
                }).hide();

                jThis.append(jDefaultImage);

                var jPressedImage = $('<img />').css({
                    'float': 'left',
                    'position': 'absolute',
                    'top': 0,
                    'left': 0
                }).attr({
                    'src': path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_PRESSED_POSTFIX)
                }).hide();

                jThis.append(jPressedImage);

                if (imageBoxHover) {
                    var jHoveringImage = $('<img />').css({
                        'float': 'left',
                        'position': 'absolute',
                        'top': 0,
                        'left': 0
                    }).attr({
                        'src': path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_HOVERING_POSTFIX)
                    }).hide();

                    jThis.append(jHoveringImage);
                }

                var jClickDiv = $('<div></div>').css({
                    'position': 'relative',
                    'top': 0,
                    'left': 0
                });
                jThis.append(jClickDiv);

                jThis.on(Lia.Component.Event.STATUS_CHANGED, function (e) {

                    jQuery(this).checkImageBoxByStatus(e.status);
                });

                jThis.checkButtonStatus();
                jThis.addClass(Lia.Component.Flag.IMAGE_BOX_INITED);
            });
        }
    });

})(jQuery);


/**
 *  jquery.history.js 임포트 시켜서 사용
 *  lia.requester.js 임포트 시켜서 사용
 *  ajax 호출
 **/

/*
 */

var Popup = jQuery.Popup = Lia.Popup = function () {

    this.jPopup = undefined;
    this.jLayout = undefined;
    this.cssLoading = undefined;
    this.htmlLoading = undefined;

    this.hided = false;
    this.inited = false;
};

Lia.Popup.Progress = {
    NAME: 'lia-progress',
    HTML_FILE_PATH: '/res/lia/popup/progress.html',
    JS_FILE_PATH: '/res/lia/popup/progress.js'
};

Lia.Popup.prototype.set = function (options) {

    if (options != undefined) {

        var jPopup = Lia.p(options, 'jPopup');
        if (jPopup != undefined) {
            this.jPopup = jPopup;
        }

        var jLayout = Lia.p(options, 'jLayout');
        if (jLayout != undefined) {
            this.jLayout = jLayout;
        }
    }
};
Lia.Popup.prototype.getJLayout = Lia.Popup.prototype.get = function () {
    return this.jLayout;
};
Lia.Popup.prototype.getJPopup = function () {
    return this.jPopup;
};
Lia.Popup.prototype.find = function (selector) {

    if (this.jLayout != undefined)
        return this.jLayout.find(selector);

    return undefined;
};

Lia.Popup.prototype.html = function (html) {

    if (this.jLayout != undefined)
        return this.jLayout.html(html);

    return undefined;
};


Lia.Popup.prototype.append = function (item) {

    if (this.jLayout != undefined)
        return this.jLayout.append(item);

    return undefined;
};

Lia.Popup.prototype.hide = function () {

    if (this.jPopup != undefined)
        this.jPopup.hidePopup();

    this.hided = true;
    return this;
};
Lia.Popup.prototype.isHided = function () {
    return this.hided;
};
Lia.Popup.prototype.isInited = function () {
    return this.inited;
};
Lia.Popup.prototype.setInited = function (inited) {
    this.inited = inited;
    return this;
};
Lia.Popup.prototype.checkCssLoading = function () {
    return this.cssLoading;
};
Lia.Popup.prototype.checkHtmlLoading = function () {
    return this.htmlLoading;
};
Lia.Popup.prototype.adjust = function () {
    jQuery.adjustPopup(this.get());
};
Lia.Popup.prototype.extend = function (map) {
    for (var key in map) {
        this[key] = map[key];
    }
};

Lia.Popup.prototype.adjustPopup = Lia.Popup.prototype.adjust;
Lia.Popup.prototype.hidePoup = Lia.Popup.prototype.hide;


var AjaxPopupManager = jQuery.AjaxPopupManager = Lia.AjaxPopupManager = {

    ContentType: {

        CSS: 'css',
        JS: 'js',
        HTML: 'html'
    },

    Status: {

        START: 'START',
        SUCCESS: 'SUCCESS',
        ERROR: 'ERROR'
    },

    cssLoading: true,
    htmlLoading: true,
    jsLoading: true,

    requester: undefined,

    ajaxQSync: false,
    ajaxQMethod: {},
    ajaxQCssMethod: 'get',
    ajaxQJsMethod: 'get',
    ajaxQHtmlMethod: 'get',

    popupContentMap: {
        css: {},
        js: {},
        html: {}
    },

    popupListLayoutSelector: '#popup_list_layout',

    filePathFormatHandler: function (path, object) {
        return path;
    },
    cssFilePathFormatHandler: function (path, object) {
        return '/res/popup/' + path + '.css';
    },
    htmlFilePathFormatHandler: function (path, object) {
        return '/res/popup/' + path + '.html';
    },
    jsFilePathFormatHandler: function (path, object) {
        return '/res/popup/' + path + '.js';
    },

    /**
     * css 로딩 여부 설정
     */
    setCssLoading: function (loading) {
        Lia.AjaxPopupManager.cssLoading = loading;
    },

    /**
     * html 로딩 여부 설정
     */
    setHtmlLoading: function (loading) {
        Lia.AjaxPopupManager.htmlLoading = loading;
    },

    /**
     * js 로딩 여부 설정
     */
    setJsLoading: function (loading) {
        Lia.AjaxPopupManager.jsLoading = loading;
    },

    /**
     * ajax로 sync 설정
     */
    setAjaxQSync: function (sync) {
        Lia.AjaxPopupManager.ajaxQSync = sync;
    },

    /**
     * ajax로 css 요청시 method 설정
     */
    setAjaxQCssMethod: function (method) {
        Lia.AjaxPopupManager.ajaxQCssMethod = method;
    },
    /**
     * ajax로 js 요청시 method 설정
     */
    setAjaxQJsMethod: function (method) {
        Lia.AjaxPopupManager.ajaxQJsMethod = method;
    },
    /**
     * ajax html 요청시 method 설정
     */
    setAjaxQHtmlMethod: function (method) {
        Lia.AjaxPopupManager.ajaxQHtmlMethod = method;
    },

    /**
     * request할 파일 포멧 핸들러 설정
     */
    setFilePathFormatHandler: function (handler) {
        Lia.AjaxPopupManager.filePathFormatHandler = handler;
    },

    /**
     * request할 css 파일 포멧 핸들러 설정
     */
    setCssFilePathFormatHandler: function (handler) {
        Lia.AjaxPopupManager.cssFilePathFormatHandler = handler;
    },

    /**
     * request할 html 파일 포멧 핸들러 설정
     */
    setHtmlFilePathFormatHandler: function (handler) {
        Lia.AjaxPopupManager.htmlFilePathFormatHandler = handler;
    },

    /**
     * reqeust할 js 파일 포멧 핸들러 설정
     */
    setJsFilePathFormatHandler: function (handler) {
        Lia.AjaxPopupManager.jsFilePathFormatHandler = handler;
    },

    /**
     * 진행 상황 객체
     */
    onProgress: function (status, path, object) {
    },

    /**
     * 진행 상황 리스터 등록
     */
    setOnProgress: function (listener) {
        Lia.AjaxPopupManager.onProgress = listener;
    },

    onPopupInit: function (jLayout, path, object, jPopupListLayout) {
    },

    setOnPopupInit: function (listener) {
        Lia.AjaxPopupManager.onPopupInit = listener;
    },

    onPopupConstruct: function (jLayout, path, object, jPopupListLayout) {
    },

    setOnPopupConstruct: function (listener) {
        Lia.AjaxPopupManager.onPopupConstruct = listener;
    },

    onPopupShow: function (jLayout, path, object, jPopupListLayout) {
    },

    setOnPopupShow: function (listener) {
        Lia.AjaxPopupManager.onPopupShow = listener;
    },

    onPopupHide: function (jLayout, path, object, jPopupListLayout) {
    },

    setOnPopupHide: function (listener) {
        Lia.AjaxPopupManager.onPopupHide = listener;
    },

    filePathCachingHandler: function (path, object, contentType) {
        return true;
    },

    setFilePathCachingHandler: function (listener) {
        Lia.AjaxPopupManager.filePathCachingHandler = listener;
    },


    setPopupContent: function (path, contentType, content) {

        var map = Lia.AjaxPopupManager.popupContentMap[contentType];
        map[path] = content;
    },

    setCssPopupContent: function (path, content) {

        Lia.AjaxPopupManager.setPopupContent(path, Lia.AjaxPopupManager.ContentType.CSS, content);
    },

    setJsPopupContent: function (path, content) {

        Lia.AjaxPopupManager.setPopupContent(path, Lia.AjaxPopupManager.ContentType.JS, content);
    },

    setHtmlPopupContent: function (path, content) {

        Lia.AjaxPopupManager.setPopupContent(path, Lia.AjaxPopupManager.ContentType.HTML, content);
    },


    /**
     * 함수 등록 및 초기화
     *
     * cssLoading
     * htmlLoading
     * jsLoading
     * requester
     * caching
     *
     * ajaxQSync
     * ajaxQCssMethod
     * ajaxQJsMethod
     * ajaxQHtmlMethod
     *
     */
    init: function (options) {

        for (var key in options) {

            var value = options[key];
            Lia.AjaxPopupManager[key] = value;
        }

        if (Lia.AjaxPopupManager.requester == undefined)
            Lia.AjaxPopupManager.requester = new Lia.Requester();
    },


    /**
     * caching 우선순위
     *    options - caching
     *       undefined 이면
     *          filePathCachingHandler 체킹
     *
     */
    show: function (path, object, options, parameterMap) {

        var optionsCaching = Lia.p(options, 'caching');

        var optionsJsFilePath = Lia.p(options, 'jsFilePath');

        Lia.AjaxPopupManager.onProgress(Lia.AjaxPopupManager.Status.START, path, object);

        var url = undefined;
        if (Lia.AjaxPopupManager.jsLoading == true) {

            var requestPath = Lia.AjaxPopupManager.filePathFormatHandler(path, object);

            // caching
            var caching = optionsCaching;
            if (caching == undefined) {
                caching = Lia.AjaxPopupManager.filePathCachingHandler(path, object, Lia.AjaxPopupManager.ContentType.JS);
            }

            if (!caching || Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.JS][path] == undefined) {

                if (String.isNotBlank(optionsJsFilePath)) {
                    url = optionsJsFilePath;
                } else {
                    url = Lia.AjaxPopupManager.jsFilePathFormatHandler(requestPath, object);
                }

                if (url != undefined) {

                    Lia.AjaxPopupManager.request(Lia.AjaxPopupManager.ajaxQJsMethod, url, parameterMap, function (status, data, request) {

                        var path = Lia.p(request, 'object', 'path');

                        if (status != Lia.Requester.Status.SUCCESS) {
                            Lia.AjaxPopupManager.abort();
                            Lia.AjaxPopupManager.onProgress(Lia.AjaxPopupManager.Status.ERROR, path, Lia.p(request, 'object', 'object'));
                            return;
                        }

                        Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.JS][path] = data;

                    }, {
                        path: path,
                        object: object
                    });
                } else {

                    // 로딩 안해야 되는 케이스
                    Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.JS][path] = undefined;
                }
            }

        } else {

            // 로딩 안해야 되는 케이스
            Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.JS][path] = undefined;
        }


        var popup = new Lia.Popup();

        Lia.AjaxPopupManager.execute(function (execute) {

            var popup = Lia.p(execute, 'object', 'popup');
            var options = Lia.p(execute, 'object', 'options');
            var path = Lia.p(execute, 'object', 'path');
            var object = Lia.p(execute, 'object', 'object');
            var parameterMap = Lia.p(execute, 'object', 'parameterMap');

            var optionsHtmlFilePath = Lia.p(options, 'htmlFilePath');
            var optionsCssFilePath = Lia.p(options, 'cssFilePath');

            // 스크립트 체크
            var js = Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.JS][path];
            if (js != undefined) {
                popup.extend(eval(js));
            }

            var htmlUrl = undefined;

            var htmlLoading = Lia.pd(Lia.AjaxPopupManager.htmlLoading, popup.checkHtmlLoading());
            if (htmlLoading) {

                // caching
                var caching = optionsCaching;
                if (caching == undefined) {
                    caching = Lia.AjaxPopupManager.filePathCachingHandler(path, object, Lia.AjaxPopupManager.ContentType.HTML);
                }

                if (!caching || Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.HTML][path] == undefined) {

                    if (String.isNotBlank(optionsHtmlFilePath)) {
                        htmlUrl = optionsHtmlFilePath;
                    } else {
                        htmlUrl = Lia.AjaxPopupManager.htmlFilePathFormatHandler(requestPath, object);
                    }

                    if (htmlUrl != undefined) {

                        Lia.AjaxPopupManager.request(Lia.AjaxPopupManager.ajaxQHtmlMethod, htmlUrl, parameterMap, function (status, data, request) {

                            var path = Lia.p(request, 'object', 'path');

                            if (status != Lia.Requester.Status.SUCCESS) {
                                Lia.AjaxPopupManager.abort();
                                Lia.AjaxPopupManager.onProgress(Lia.AjaxPopupManager.Status.ERROR, path, Lia.p(request, 'object', 'object'));
                                return;
                            }

                            Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.HTML][path] = data;

                        }, {
                            path: path,
                            object: object
                        });
                    } else {

                        // 로딩 안해야 되는 케이스
                        Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.HTML][path] = undefined;
                    }

                }
            } else {

                // 로딩 안해야 되는 케이스
                Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.HTML][path] = undefined;
            }


            var cssUrl = undefined;
            var cssLoading = Lia.pd(Lia.AjaxPopupManager.cssLoading, popup.checkCssLoading());
            if (cssLoading) {

                // caching
                var caching = optionsCaching;
                if (caching == undefined) {
                    caching = Lia.AjaxPopupManager.filePathCachingHandler(path, object, Lia.AjaxPopupManager.ContentType.CSS);
                }

                if (!caching || Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.CSS][path] == undefined) {

                    if (String.isNotBlank(optionsCssFilePath)) {
                        cssUrl = optionsCssFilePath;
                    } else {
                        cssUrl = Lia.AjaxPopupManager.cssFilePathFormatHandler(requestPath, object);
                    }

                    if (cssUrl != undefined) {

                        Lia.AjaxPopupManager.request(Lia.AjaxPopupManager.ajaxQCssMethod, cssUrl, parameterMap, function (status, data, request) {

                            var path = Lia.p(request, 'object', 'path');

                            if (status != Lia.Requester.Status.SUCCESS) {
                                Lia.AjaxPopupManager.abort();
                                Lia.AjaxPopupManager.onProgress(Lia.AjaxPopupManager.Status.ERROR, path, Lia.p(request, 'object', 'object'));
                                return;
                            }

                            Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.CSS][path] = data;

                        }, {
                            path: path,
                            object: object
                        });

                    } else {

                        // 로딩 안해야 되는 케이스
                        Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.CSS][path] = undefined;
                    }
                }

            } else {
                // 로딩 안해야 되는 케이스
                Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.CSS][path] = undefined;
            }

            Lia.AjaxPopupManager.execute(function (execute) {

                var popup = Lia.p(execute, 'object', 'popup');
                var path = Lia.p(execute, 'object', 'path');
                var parameterMap = Lia.p(execute, 'object', 'parameterMap');
                var options = Lia.p(execute, 'object', 'options');
                var object = Lia.p(execute, 'object', 'object');

                // 키기 전에 하이드 된 경우
                if (popup.isHided()) {
                    return;
                }

                var css = Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.CSS][path];
                var html = Lia.AjaxPopupManager.popupContentMap[Lia.AjaxPopupManager.ContentType.HTML][path];

                var jPopupListLayout = jQuery(Lia.AjaxPopupManager.popupListLayoutSelector);

                var text = '<div>';

                if (css != undefined) {
                    text += '<style type="text/css">' + css + '</style>';
                }

                if (html != undefined) {
                    text += html;
                }

                text += '</div>';

                var jLayout = $(text);
                jPopupListLayout.append(jLayout);

                popup.set({
                    jLayout: jLayout
                });

                Lia.AjaxPopupManager.onPopupConstruct(jLayout, path, object, jPopupListLayout);

                if (popup.onConstruct != undefined) {

                    if (Lia.debugMode) {
                        popup.onConstruct(jLayout, path, object, jPopupListLayout);
                    } else {
                        try {
                            popup.onConstruct(jLayout, path, object, jPopupListLayout);
                        } catch (err) {
                        }
                    }
                }

                jQuery.initDim(jLayout);
                var jPopup = jQuery.initPopup(jLayout);

                popup.set({
                    jPopup: jPopup
                });

                Lia.AjaxPopupManager.onPopupInit(jLayout, path, object, jPopupListLayout);

                jPopup.on(Lia.Component.Event.SHOW, {
                    jLayout: jLayout,
                    path: path,
                    object: object,
                    jPopupListLayout: jPopupListLayout
                }, function (e) {

                    var data = e.data;
                    var jLayout = data.jLayout;
                    var path = data.path;
                    var object = data.object;
                    var jPopupListLayout = data.jPopupListLayout;

                    if (jLayout != undefined) {
                        Lia.AjaxPopupManager.onPopupShow(jLayout, path, object, jPopupListLayout);
                    }
                });

                if (popup.onInit != undefined) {

                    if (Lia.debugMode) {
                        popup.onInit(jLayout, path, object, jPopupListLayout);
                    } else {
                        try {
                            popup.onInit(jLayout, path, object, jPopupListLayout);
                        } catch (err) {
                        }
                    }


                }

                popup.setInited(true);

                jPopup.on(Lia.Component.Event.SHOW, {
                    options: options,
                    popup: popup,
                    jLayout: jLayout,
                    path: path,
                    object: object,
                    jPopupListLayout: jPopupListLayout
                }, function (e) {

                    var data = e.data;

                    var options = data.options;
                    var popup = data.popup;
                    var jLayout = data.jLayout;
                    var path = data.path;
                    var object = data.object;
                    var jPopupListLayout = data.jPopupListLayout;

                    if (jLayout != undefined && popup.onShow != undefined) {

                        if (Lia.debugMode) {
                            popup.onShow(jLayout, path, object, jPopupListLayout);
                        } else {
                            try {
                                popup.onShow(jLayout, path, object, jPopupListLayout);
                            } catch (err) {
                            }

                        }


                    }

                    var onShow = Lia.p(options, 'onShow');
                    if (onShow != undefined) {
                        onShow.call(popup, popup, jLayout, path, object, jPopupListLayout);
                    }
                });

                jPopup.on(Lia.Component.Event.HIDE, {
                    options: options,
                    popup: popup,
                    jLayout: jLayout,
                    path: path,
                    object: object,
                    jPopupListLayout: jPopupListLayout
                }, function (e) {

                    var data = e.data;

                    var options = data.options;
                    var popup = data.popup;
                    var jLayout = data.jLayout;
                    var path = data.path;
                    var object = data.object;
                    var jPopupListLayout = data.jPopupListLayout;

                    var onHide = Lia.p(options, 'onHide');
                    if (onHide != undefined) {
                        onHide.call(popup, popup, jLayout, path, object, jPopupListLayout);
                    }

                    if (jLayout != undefined && popup.onHide != undefined) {

                        try {
                            popup.onHide(jLayout, path, object, jPopupListLayout);
                        } catch (err) {
                            console.log(err);
                        }
                    }

                    if (jLayout != undefined) {
                        Lia.AjaxPopupManager.onPopupHide(jLayout, path, object, jPopupListLayout);
                        jLayout.remove();
                    }
                });

                jPopup.showPopup();

                Lia.AjaxPopupManager.onProgress(Lia.AjaxPopupManager.Status.SUCCESS, path, object);

            }, {
                path: path,
                popup: popup,
                object: object,
                options: options,
                parameterMap: parameterMap
            });

        }, {
            path: path,
            popup: popup,
            object: object,
            options: options,
            parameterMap: parameterMap
        });

        return popup;
    },

    request: function (method, url, parameterMap, onResponse, object) {

        var request = {
            url: url,
            onResponse: onResponse,
            object: object,
            parameterMap: parameterMap,
            method: method,

            ajaxQSync: Lia.AjaxPopupManager.ajaxQSync,
            q: true,
            dataType: 'text'
        };

        Lia.AjaxPopupManager.requester.request(request);
    },

    execute: function (onExecute, object) {

        Lia.AjaxPopupManager.requester.execute({
            onExecute: onExecute,
            object: object
        });
    },

    abort: function () {

        Lia.AjaxPopupManager.requester.abort();
    }


};


/**
 * loading_indicator
 *
 * <img class="loading_indicator" data-lia-src="{img 주소 format:/loading/{index}.png}" data-lia-index="{현재 인덱스}" data-lia-start-index="{시작 인덱스}" data-lia-end-index="{끝인덱스}" />
 *
 */
/*
 초기화 코드

 뷰에 붙이고 나서 start 해야함
 $(document).ready(function () {

 $.initAndPlayLoadingIndicator();

 });

 */

jQuery.extend({

    liaLoadingIndicatorOptions: undefined,
    setLoadingIndicatorOptions: function (options) {
        jQuery.liaLoadingIndicatorOptions = options;
    },

    liaLoadingIndicatorTimerId: undefined,

    loopLoadingIndicatorTimer: function () {

        if (jQuery.liaLoadingIndicatorTimerId == undefined) {

            jQuery.liaLoadingIndicatorTimerId = window.setInterval(function () {

                if (jQuery('.' + Lia.Component.Name.LOADING_INDICATOR + '.' + Lia.Component.Flag.PLAYING).nextLoadingIndicator().size() <= 0) {
                    jQuery.pauseLoadingIndicator();
                }

            }, Lia.Component.Value.LoadingIndicator.TIMER_DURATION);

        }
    },

    pauseLoadingIndicatorTimer: function () {

        if (jQuery.liaLoadingIndicatorTimerId != undefined) {
            clearInterval(jQuery.liaLoadingIndicatorTimerId);
            jQuery.liaLoadingIndicatorTimerId = undefined;
        }
    },

    /**
     * 초기화
     */
    initLoadingIndicator: function (j) {

        var selector = '.' + Lia.Component.Name.LOADING_INDICATOR;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.initLoadingIndicator();
    },

    /**
     * 시작
     */
    playLoadingIndicator: function (j) {

        var selector = '.' + Lia.Component.Name.LOADING_INDICATOR;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.playLoadingIndicator();
    },

    /**
     * 초기화 및 시작
     */
    initAndPlayLoadingIndicator: function (j) {

        var selector = '.' + Lia.Component.Name.LOADING_INDICATOR;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        return j.initAndPlayLoadingIndicator();
    },

    /**
     * 중지
     */
    removeLoadingIndicator: function (j) {

        var selector = '.' + Lia.Component.Name.LOADING_INDICATOR;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        j.remove();
    },

    /**
     * 중지
     */
    pauseLoadingIndicator: function (j) {

        var selector = '.' + Lia.Component.Name.LOADING_INDICATOR;

        if (j == undefined)
            j = jQuery(selector);
        else
            j = j.find(selector);

        j.pauseLoadingIndicator();
    }


});

jQuery.fn.extend({

    initLoadingIndicator: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            if (jThis.hasClass(Lia.Component.Flag.INITED))
                return;

            // 소스 체크
            var src = jThis.dataAttr(Lia.Component.AttrName.SRC);
            if (String.isBlank(src)) {
                src = Lia.p(jQuery.liaLoadingIndicatorOptions, Lia.Component.AttrName.SRC);
                jThis.dataAttr(Lia.Component.AttrName.SRC, src);
            }

            // 끝 변수 체크
            var endIndex = jThis.dataAttr(Lia.Component.AttrName.END_INDEX);
            if (String.isBlank(endIndex)) {
                endIndex = Lia.p(jQuery.liaLoadingIndicatorOptions, Lia.Component.AttrName.END_INDEX);
                jThis.dataAttr(Lia.Component.AttrName.END_INDEX, endIndex);
            }

            // 시작 변수 체크
            var startIndex = jThis.dataAttr(Lia.Component.AttrName.START_INDEX);
            if (String.isBlank(startIndex)) {
                startIndex = Lia.p(jQuery.liaLoadingIndicatorOptions, Lia.Component.AttrName.START_INDEX);
            }
            if (String.isBlank(startIndex)) {
                startIndex = Lia.Component.Value.LoadingIndicator.DEFAULT_START_INDEX;
            } else {
                startIndex = parseInt(startIndex);
            }

            var index = startIndex;
            jThis.attr('src', src.replace(Lia.Component.Value.LoadingIndicator.REPLACE_INDEX_WORD, index));
            jThis.dataAttr(Lia.Component.AttrName.INDEX, index);
            jThis.addClass(Lia.Component.Flag.INITED);
        });
    },

    initAndPlayLoadingIndicator: function () {

        return this.initLoadingIndicator().playLoadingIndicator();
    },

    playLoadingIndicator: function () {

        this.addClass(Lia.Component.Flag.PLAYING);
        jQuery.loopLoadingIndicatorTimer();
        return this;
    },

    nextLoadingIndicator: function () {

        return this.each(function () {

            var jThis = jQuery(this);
            var src = jThis.dataAttr(Lia.Component.AttrName.SRC);

            var startIndex = jThis.dataAttr(Lia.Component.AttrName.START_INDEX);
            if (String.isBlank(startIndex)) {
                startIndex = Lia.Component.Value.LoadingIndicator.DEFAULT_START_INDEX;
            } else {
                startIndex = parseInt(startIndex);
            }

            var endIndex = parseInt(jThis.dataAttr(Lia.Component.AttrName.END_INDEX));

            var index = jThis.dataAttr(Lia.Component.AttrName.INDEX);
            if (index == undefined) {
                index = startIndex;
            } else {
                index = parseInt(index);
            }

            ++index;
            if (index > endIndex)
                index = startIndex;

            jThis.attr('src', src.replace(Lia.Component.Value.LoadingIndicator.REPLACE_INDEX_WORD, index));
            jThis.attr('alt', 'loading indicator');
            jThis.dataAttr(Lia.Component.AttrName.INDEX, index);

        });

        return this;
    },

    pauseLoadingIndicator: function () {

        return this.removeClass(Lia.Component.Flag.PLAYING);
    }
});


/**
 * flat_button
 *
 * flat 한 버튼
 *
 *  <div class="button flat" />
 *
 *  속성
 *  data-lia-background-color
 *  data-lia-hovering-background-color
 *  data-lia-pressed-background-color
 *
 *  data-lia-text-color
 *  data-lia-hovering-text-color
 *  data-lia-pressed-text-color
 *
 *  data-lia-round-width - 라운드 크기
 *  data-lia-direction - 라운드 되는 방향
 *    ( left, right, top, bottom )
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initFlatButton();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initFlatButton: function (j) {

            var selector = '.' + Lia.Component.Name.FLAT_BUTTON;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initFlatButton();
        }
    });

    $.fn.extend({

        flatButtonPressed: function (pressed) {

            return this.buttonPressed(pressed);
        },

        setFlatButtonByPressed: function (pressed) {

            for (var i = 0, l = this.length; i < l; i++) {
                var jThis = this.eq(i);

                var status = (pressed) ? Lia.Component.Value.Button.Status.PRESSED : Lia.Component.Value.Button.Status.DEFAULT;
                jThis.setFlatButtonByStatus(status);
            }

            return this;
        },

        setFlatButtonByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var defaultBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.DEFAULT_BACKGROUND_COLOR);
                var hoveringBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.HOVERING_BACKGROUND_COLOR);
                if (hoveringBackgroundColor == undefined)
                    hoveringBackgroundColor = defaultBackgroundColor;
                var pressedBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.PRESSED_BACKGROUND_COLOR);
                if (pressedBackgroundColor == undefined)
                    pressedBackgroundColor = hoveringBackgroundColor;

                var defaultTextColor = jThis.dataAttr(Lia.Component.AttrName.DEFAULT_TEXT_COLOR);

                var hoveringTextColor = jThis.dataAttr(Lia.Component.AttrName.HOVERING_TEXT_COLOR);
                if (hoveringTextColor == undefined)
                    hoveringTextColor = defaultTextColor;
                var pressedTextColor = jThis.dataAttr(Lia.Component.AttrName.PRESSED_TEXT_COLOR);
                if (pressedTextColor == undefined)
                    pressedTextColor = hoveringTextColor;

                var backgroundColor = defaultBackgroundColor;
                var textColor = defaultTextColor;

                if (status == Lia.Component.Value.Button.Status.PRESSED) {
                    backgroundColor = pressedBackgroundColor;
                    textColor = pressedTextColor;

                } else if (status == Lia.Component.Value.Button.Status.HOVERING) {

                    backgroundColor = hoveringBackgroundColor;
                    textColor = hoveringTextColor;
                }

                if (backgroundColor != undefined)
                    jThis.css('background-color', backgroundColor);

                if (textColor != undefined)
                    jThis.css('color', textColor);

            }

            return this;
        },

        checkFlatButtonByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var isButtonPress = jThis.hasClass(Lia.Component.Flag.PRESS);
                var isButtonHover = jThis.hasClass(Lia.Component.Flag.HOVER);

                var buttonStatus = Lia.Component.Value.Button.Status.DEFAULT;
                if (status == Lia.Component.Value.Button.Status.PRESSED || status == Lia.Component.Value.Button.Status.PRESSING || (isButtonPress && status == Lia.Component.Value.Button.Status.HOVERING)) {
                    buttonStatus = Lia.Component.Value.Button.Status.PRESSED;
                } else if (isButtonHover && status == Lia.Component.Value.Button.Status.HOVERING) {
                    buttonStatus = Lia.Component.Value.Button.Status.HOVERING;
                }

                jThis.setFlatButtonByStatus(buttonStatus);
            }

            return this;
        },

        initFlatButton: function () {

            return this.initButton().each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.FLAT_BUTTON_INITED))
                    return;

                var roundWidth = jThis.dataAttr(Lia.Component.AttrName.ROUND_WIDTH);
                if (roundWidth == undefined)
                    roundWidth = Lia.Component.Value.Button.FlatButton.DEFAULT_ROUND_WIDTH;

                var direction = jThis.dataAttr(Lia.Component.AttrName.DIRECTION);
                var cornerOptions = '';
                if (direction != undefined)
                    cornerOptions += ' ' + direction + ' ';
                if (roundWidth != undefined)
                    cornerOptions += ' ' + roundWidth + ' ';

                jThis.css({'line-height': jThis.height() + 'px'});
                if (roundWidth != undefined && parseFloat(roundWidth) != 0) {

                    var borderRadiusCss = {};
                    if (String.isBlank(cornerOptions)) {
                        borderRadiusCss['border-radius'] = roundWidth;
                    } else {

                        if (cornerOptions.indexOf('left')) {
                            borderRadiusCss['border-top-left-radius'] = roundWidth;
                            borderRadiusCss['border-bottom-left-radius'] = roundWidth;
                        }
                        if (cornerOptions.indexOf('right')) {
                            borderRadiusCss['border-top-right-radius'] = roundWidth;
                            borderRadiusCss['border-bottom-right-radius'] = roundWidth;
                        }
                        if (cornerOptions.indexOf('top')) {
                            borderRadiusCss['border-top-left-radius'] = roundWidth;
                            borderRadiusCss['border-top-right-radius'] = roundWidth;
                        }
                        if (cornerOptions.indexOf('bottom')) {
                            borderRadiusCss['border-bottom-left-radius'] = roundWidth;
                            borderRadiusCss['border-bottom-right-radius'] = roundWidth;
                        }
                    }

                    jThis.css(borderRadiusCss);
                }

                jThis.css({'text-align': 'center'});

                jThis.on(Lia.Component.Event.STATUS_CHANGED, function (e) {

                    $(this).checkFlatButtonByStatus(e.status);
                });

                jThis.checkButtonStatus();
                jThis.addClass(Lia.Component.Flag.FLAT_BUTTON_INITED);
            });
        }
    });

})(jQuery);
/**
 * image_button
 * 이미지 마우스 오버, 클릭시 이미지 변경
 *
 * <img class="image_button" data-lia-src="{이미지 주소}" />
 *      _pressed.png 가 클릭시 보여짐
 *
 * <img class="image_button hover" data-lia-src="{이미지 주소}" />
 *      _hovering.png 가 마우스 커서가 올라갈 대 보여짐
 *      _pressed.png 가 클릭시 보여짐
 *
 * <img class="image_button press" data-lia-src="{이미지 주소}" />*
 *      _pressed.png 가 마우스 커서가 올라갈 때, 클릭시 보여짐
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initImageButton();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initImageButton: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_BUTTON;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageButton();
        }
    });

    $.fn.extend({

        /**
         * image_button pressed 상태 세팅, 리턴
         *
         * @param pressed
         * @returns {*}
         */
        imageButtonPressed: function (pressed) {

            return this.buttonPressed(pressed);

        },

        setImageButtonByPressed: function (pressed) {

            for (var i = 0, l = this.length; i < l; i++) {
                var jThis = this.eq(i);

                var status = (pressed) ? Lia.Component.Value.Button.Status.PRESSED : Lia.Component.Value.Button.Status.DEFAULT;
                jThis.setImageButtonByStatus(status);
            }

            return this;
        },

        setImageButtonByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var path = jThis.dataAttr(Lia.Component.AttrName.SRC);
                path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);


                if (status == Lia.Component.Value.Button.Status.PRESSED) {
                    path = path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_PRESSED_POSTFIX);
                } else if (status == Lia.Component.Value.Button.Status.HOVERING) {
                    path = path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_HOVERING_POSTFIX);
                }

                if (jThis.attr('src') != path) {
                    jThis.attr('src', path);
                }
            }

            return this;
        },

        checkImageButtonByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var isButtonPress = jThis.hasClass(Lia.Component.Flag.PRESS);
                var isButtonHover = jThis.hasClass(Lia.Component.Flag.HOVER);

                var buttonStatus = Lia.Component.Value.Button.Status.DEFAULT;
                if (status == Lia.Component.Value.Button.Status.PRESSED || status == Lia.Component.Value.Button.Status.PRESSING || (isButtonPress && status == Lia.Component.Value.Button.Status.HOVERING)) {
                    buttonStatus = Lia.Component.Value.Button.Status.PRESSED;
                } else if (isButtonHover && status == Lia.Component.Value.Button.Status.HOVERING) {
                    buttonStatus = Lia.Component.Value.Button.Status.HOVERING;
                }

                jThis.setImageButtonByStatus(buttonStatus);
            }

            return this;
        },

        /**
         * image_button 초기화
         *
         * @returns {*}
         */
        initImageButton: function () {

            return this.initButton().each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.IMAGE_BUTTON_INITED))
                    return;

                var path = jThis.dataAttr(Lia.Component.AttrName.SRC);
                var src = jThis.attr('src');
                if (String.isBlank(path) && !String.isBlank(src)) {
                    path = src;
                    path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                    path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                    jThis.dataAttr(Lia.Component.AttrName.SRC, path);
                }

                jThis.on(Lia.Component.Event.STATUS_CHANGED, function (e) {

                    jQuery(this).checkImageButtonByStatus(e.status);
                });

                jThis.checkButtonStatus();
                jThis.addClass(Lia.Component.Flag.IMAGE_BUTTON_INITED);
            });
        }
    });

})(jQuery);


/**
 * image_button_container
 *
 * <img class="image_button_container" data-lia-src="{이미지 주소}" />
 *      _pressed.png 가 클릭시 보여짐
 *
 * <img class="image_button_container hover" data-lia-src="{이미지 주소}" />
 *      _hovering.png 가 마우스 커서가 올라갈 대 보여짐
 *      _pressed.png 가 클릭시 보여짐
 *
 * <img class="image_button_container press" data-lia-src="{이미지 주소}" />*
 *      _pressed.png 가 마우스 커서가 올라갈 때, 클릭시 보여짐
 *
 *  내부에 img 있으면 더 생성 안함
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initImageButtonContainer();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initImageButtonContainer: function (j) {

            var selector = '.' + Lia.Component.Name.IMAGE_BUTTON_CONTAINER;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageButtonContainer();
        }
    });

    $.fn.extend({

        /**
         * image_button_container pressed 상태 세팅, 리턴
         *
         * @param pressed
         * @returns {*}
         */
        imageButtonContainerPressed: function (pressed) {

            return this.buttonPressed(pressed);

        },

        setImageButtonContainerByPressed: function (pressed) {

            for (var i = 0, l = this.length; i < l; i++) {
                var jThis = this.eq(i);

                var status = (pressed) ? Lia.Component.Value.Button.Status.PRESSED : Lia.Component.Value.Button.Status.DEFAULT;
                jThis.setImageButtonContainerByStatus(status);
            }

            return this;
        },

        setImageButtonContainerByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i).find('img').not('.' + Lia.Component.Flag.NO_CONTAIN);
                var path = jThis.dataAttr(Lia.Component.AttrName.SRC);

                path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);


                if (status == Lia.Component.Value.Button.Status.PRESSED) {
                    path = path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_PRESSED_POSTFIX);
                } else if (status == Lia.Component.Value.Button.Status.HOVERING) {
                    path = path.replace(Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX, Lia.Component.Value.Button.SRC_HOVERING_POSTFIX);
                }

                if (jThis.attr('src') != path) {
                    jThis.attr('src', path);
                }
            }

            return this;
        },

        checkImageButtonContainerByStatus: function (status) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var isButtonPress = jThis.hasClass(Lia.Component.Flag.PRESS);
                var isButtonHover = jThis.hasClass(Lia.Component.Flag.HOVER);

                var buttonStatus = Lia.Component.Value.Button.Status.DEFAULT;
                if (status == Lia.Component.Value.Button.Status.PRESSED || status == Lia.Component.Value.Button.Status.PRESSING || (isButtonPress && status == Lia.Component.Value.Button.Status.HOVERING)) {
                    buttonStatus = Lia.Component.Value.Button.Status.PRESSED;
                } else if (isButtonHover && status == Lia.Component.Value.Button.Status.HOVERING) {
                    buttonStatus = Lia.Component.Value.Button.Status.HOVERING;
                }

                jThis.setImageButtonContainerByStatus(buttonStatus);
            }

            return this;
        },

        /**
         * image_button 초기화
         *
         * @returns {*}
         */
        initImageButtonContainer: function () {

            return this.initButton().each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.IMAGE_BUTTON_CONTAINER_INITED))
                    return;

                var jImg = jThis.find('img').not('.' + Lia.Component.Flag.NO_CONTAIN);
                if (jImg.length == 0) {
                    jImg = $('<img />');
                    jThis.append(jImg);

                    var attrMap = {};
                    attrMap[Lia.Component.AttrName.SRC] = jThis.dataAttr(Lia.Component.AttrName.SRC);
                    attrMap['src'] = jThis.attr('src');
                    jImg.attr(attrMap);
                }

                var path = jImg.dataAttr(Lia.Component.AttrName.SRC);
                var src = jImg.attr('src');
                if (String.isBlank(path) && !String.isBlank(src)) {
                    path = src;
                    path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                    path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                    jImg.dataAttr(Lia.Component.AttrName.SRC, path);

                    jThis.dataAttr(Lia.Component.AttrName.SRC, path);
                    jThis.attr('src', path);
                }

                jThis.on(Lia.Component.Event.STATUS_CHANGED, function (e) {
                    jQuery(this).checkImageButtonContainerByStatus(e.status);
                });

                jThis.checkButtonStatus();
                jThis.addClass(Lia.Component.Flag.IMAGE_BUTTON_CONTAINER_INITED);
            });
        },

        /**
         * image_button 초기화
         *
         * @returns {*}
         */
        setImageButtonContainerSrc: function (src) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jThis = this.eq(i);

                var jImg = jThis.find('img').not('.' + Lia.Component.Flag.NO_CONTAIN);

                var path = src;
                path = path.replace(Lia.Component.Value.Button.SRC_PRESSED_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                path = path.replace(Lia.Component.Value.Button.SRC_HOVERING_POSTFIX, Lia.Component.Value.Button.SRC_DEFAULT_POSTFIX);
                jImg.dataAttr(Lia.Component.AttrName.SRC, path);

                jThis.dataAttr(Lia.Component.AttrName.SRC, path);
                jThis.attr('src', path);

                jThis.checkButtonStatus();
            }

            return this;
        }
    });

})(jQuery);


/**
 * texteditor
 */
/*
 $.initTextEditor();

 */
(function ($) {

    $.extend({

        liaTextEditorOptions: {
            'height': '300px'
        },

        liaTextEditorIdx: 0,
        liaTextEditorUrl: '/res/lia/embed/smarteditor.html',

        setTextEditorOptions: function (options) {
            jQuery.liaTextEditorOptions = options;
        },

        setTextEditorUrl: function ( url ) {
            jQuery.liaTextEditorUrl = url;
        },


        /**
         * 초기화
         */
        initTextEditor: function (j, option) {

            var selector = '.' + Lia.Component.Name.TEXT_EDITOR;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initTextEditor(option);
        }

    });

    $.fn.extend({

        initTextEditor: function (options) {

            var newOptions = Lia.deepCopy(jQuery.liaTextEditorOptions);
            Lia.combine(newOptions, options);

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var jIframe = jQuery('<iframe width="100%" height="100%" hspace="0" vspace="0" frameborder="0" scrolling="no"' +
                        ' allowfullscreen="true" allowTransparency="true"></iframe>');
                    jItem.append(jIframe);

                    var id = Lia.Component.Name.TEXT_EDITOR + '_id_' + Lia.getTimestamp() + jQuery.liaTextEditorIdx++;
                    jIframe.attr({
                        'id': id,
                        'src': jQuery.liaTextEditorUrl + Lia.convertArrayToQueryString({
                            'height': Lia.p(newOptions, 'height'),
                            '_' : Lia.getTimestamp()
                        })
                    });

                    jIframe.css(newOptions)

                    jItem.addClass(Lia.Component.Flag.INITED);
                }
            }

            return this;
        },

        textEditorVal: function (val) {

            if (val == undefined) {

                if (this.size() < 1) {

                    return undefined;

                } else {

                    var jItem = this.eq(0);
                    if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                        var obj = jItem.find('iframe').get(0);
                        var objDoc = obj.contentWindow || obj.contentDocument;

                        var value = undefined;
                        try {
                            value = objDoc.getEditorValue();
                        } catch (e) {
                        }

                        return value;

                    } else {

                        return undefined;
                    }
                }
            }

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var obj = jItem.find('iframe').get(0);
                    var objDoc = obj.contentWindow || obj.contentDocument;
                    try {
                        return objDoc.setEditorValue(val);
                    } catch (e) {
                        window.setTimeout(function () {
                            jItem.textEditorVal(val);
                        }, 500);

                    }


                }
            }

            return this;
        },


        attachTextEditorVal: function (val) {

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var obj = jItem.find('iframe').get(0);
                    var objDoc = obj.contentWindow || obj.contentDocument;
                    try {
                        objDoc.attachEditorValue(val);
                    } catch (e) {
                        // window.setTimeout(function () {
                        //     jItem.attachTextEditorVal(val);
                        // }, 500);
                    }


                }
            }

            return this;
        }


    });

})(jQuery);

/*
 $.initCodeEditor();
 */
(function ($) {

    $.extend({

        liaCodeEditorOptions: {
            'height': '300px'
        },

        liaCodeEditorIdx: 0,

        liaCodeEditorType: Lia.Component.Value.CodeEditor.Type.RECOMMEND,

        setCodeEditorType : function( type ) {

            jQuery.liaCodeEditorType = type;
        },

        setCodeEditorOptions: function (options) {

            jQuery.liaCodeEditorOptions = options;
        },

        /**
         * 초기화
         */
        initCodeEditor: function (j, option) {

            var selector = '.' + Lia.Component.Name.CODE_EDITOR;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initCodeEditor(option);
        }

    });

    $.fn.extend({

        initCodeEditor: function (options) {

            var newOptions = Lia.deepCopy(jQuery.liaCodeEditorOptions);
            Lia.combine(newOptions, options);

            var codeEditorType = Lia.pcd(jQuery.liaCodeEditorType, newOptions, 'codeEditorType');

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var editorUrl = undefined;
                    if (codeEditorType == Lia.Component.Value.CodeEditor.Type.RECOMMEND) {

                        if (Lia.isMobile || Lia.ieVersion != -1) {
                            editorUrl = Lia.Component.Value.CodeEditor.Url.ACE_EDITOR;
                        } else {
                            editorUrl = Lia.Component.Value.CodeEditor.Url.MONACO_EDITOR;
                        }

                    } else if (codeEditorType == Lia.Component.Value.CodeEditor.Type.ACE_EDITOR) {

                        editorUrl = Lia.Component.Value.CodeEditor.Url.ACE_EDITOR;

                    } else if (codeEditorType == Lia.Component.Value.CodeEditor.Type.MONACO_EDITOR) {

                        editorUrl = Lia.Component.Value.CodeEditor.Url.MONACO_EDITOR;
                    }


                    var jIframe = jQuery('<iframe width="100%" height="100%" hspace="0" vspace="0" frameborder="0" scrolling="no"' +
                        ' allowfullscreen="true" allowTransparency="true"></iframe>');
                    jItem.append(jIframe);

                    var id = Lia.Component.Name.CODE_EDITOR + '_id_' + Lia.getTimestamp() + jQuery.liaCodeEditorIdx++;
                    jIframe.attr({
                        'id': id,
                        'src': editorUrl + Lia.convertArrayToQueryString({
                            height: Lia.p(newOptions, 'height'),
                            mode: Lia.pd('html', newOptions, 'mode')
                        })
                    });

                    jItem.css(newOptions);

                    jItem.addClass(Lia.Component.Flag.INITED);
                }

            }


            return this;

        },

        codeEditorVal: function (val) {

            if (val == undefined) {

                if (this.size() < 1) {

                    return undefined;

                } else {

                    var jItem = this.eq(0);
                    if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                        var obj = jItem.find('iframe').get(0);
                        var objDoc = obj.contentWindow || obj.contentDocument;

                        var value = undefined;
                        try {
                            value = objDoc.getEditorValue();
                        } catch (e) {
                        }

                        return value;

                    } else {

                        return undefined;
                    }
                }
            }

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                if (jItem.hasClass(Lia.Component.Flag.INITED)) {


                    var obj = jItem.find('iframe').get(0);
                    var objDoc = obj.contentWindow || obj.contentDocument;
                    try {
                        return objDoc.setEditorValue(val);
                    } catch (e) {
                        window.setTimeout(function () {
                            jItem.codeEditorVal(val);
                        }, 500);

                    }


                }
            }

            return this;
        }

    });

})(jQuery);


/**
 * pdf viewer
 */
/*
 $.initPdfViewer();

 */
(function ($) {

    $.extend({

        liaPdfViewerOptions: {},
        setPdfViewerOptions: function (options) {
            jQuery.liaPdfViewerOptions = options;
        },

        liaPdfViewerUrl: '/res/lia/vendor/pdfjs/web/viewer.html',
        setPdfViewerUrl: function (url) {
            jQuery.liaPdfViewerUrl = url;
        },


        /**
         * 초기화
         */
        initPdfViewer: function (j, option) {

            var selector = '.' + Lia.Component.Name.PDF_VIEWER;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initPdfViewer(option);
        }

    });

    $.fn.extend({

        initPdfViewer: function (options) {

            var newOptions = Lia.deepCopy(jQuery.liaPdfViewerOptions);
            Lia.combine(newOptions, options);

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var googleDocs = Lia.p(newOptions, 'googleDocs');
                    var downloadDisabled = Lia.p(newOptions, 'downloadDisabled');
                    if (googleDocs) {

                        var jIframe = jQuery('<iframe width="100%" height="100%" hspace="0" vspace="0" frameborder="0" scrolling="no"' +
                            ' allowfullscreen="true" allowTransparency="true">' +
                            '<div style="color:#dddddd;padding:10px;">' +
                            Lia.Strings.getString(Lia.Strings.MESSAGE.IFRAME_SUPPORT_WARNING) +
                            '</div>' +
                            '</iframe>');
                        jItem.append(jIframe);

                        var src = Lia.p(newOptions, 'src');
                        if (String.isBlank(src)) {
                            src = jItem.dataAttr(Lia.Component.AttrName.SRC);
                        }

                        jIframe.attr({
                            'src': 'https://docs.google.com/gview' + Lia.convertArrayToQueryString({
                                'embedded': 'true',
                                'url': src
                            })
                        });

                    } else if (Lia.ieVersion == -1) {

                        var jIframe = jQuery('<iframe width="100%" height="100%" hspace="0" vspace="0" frameborder="0" scrolling="no"' +
                            ' allowfullscreen="true" allowTransparency="true">' +
                            '<div style="color:#dddddd;padding:10px;">' +
                            Lia.Strings.getString(Lia.Strings.MESSAGE.IFRAME_SUPPORT_WARNING) +
                            '</div>' +
                            '</iframe>');
                        jItem.append(jIframe);

                        var src = Lia.p(newOptions, 'src');
                        if (String.isBlank(src)) {
                            src = jItem.dataAttr(Lia.Component.AttrName.SRC);
                        }

                        jIframe.attr({
                            'src': jQuery.liaPdfViewerUrl + Lia.convertArrayToQueryString({
                                'file': src,
                                'download_disabled': (downloadDisabled == true ? 1 : 0)
                            })
                        });

                    } else {

                        var src = Lia.p(newOptions, 'src');
                        if (String.isBlank(src)) {
                            src = jItem.dataAttr(Lia.Component.AttrName.SRC);
                        }

                        if (downloadDisabled == true) {
                            src += "#toolbar=0";
                        }

                        var jObject = jQuery('<object type="application/pdf" allowfullscreen allowTransparency="true" ' +
                            'style="width:100%;height:100%;" data="' + src + '" frameborder="1" scrolling="no">' +
                            '<div style="color:#dddddd;padding:10px;">' +
                            Lia.Strings.getString(Lia.Strings.MESSAGE.PDF_VIEWER_SUPPORT_WARNING) +
                            '</div>' +
                            '</object>');
                        jItem.append(jObject);
                    }

                    jItem.addClass(Lia.Component.Flag.INITED);
                }
            }

            return this;
        }

    });

})(jQuery);





/**
 * office viewer
 */
/*
 $.initOfficeViewer();

 */
(function ($) {

    $.extend({


        liaOfficeViewerOptions: {},
        setOfficeViewerOptions: function (options) {
            jQuery.liaOfficeViewerOptions = options;
        },


        /**
         * 초기화
         */
        initOfficeViewer: function (j, option) {

            var selector = '.' + Lia.Component.Name.OFFICE_VIEWER;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initOfficeViewer(option);
        }

    });

    $.fn.extend({

        initOfficeViewer: function (options) {

            var newOptions = Lia.deepCopy(jQuery.liaOfficeViewerOptions);
            Lia.combine(newOptions, options);

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var jIframe = jQuery('<iframe width="100%" height="100%" hspace="0" vspace="0" frameborder="0" scrolling="no"' +
                        ' allowfullscreen="true" allowTransparency="true">' +
                        '<div style="color:#dddddd;padding:10px;">' +
                        Lia.Strings.getString(Lia.Strings.MESSAGE.IFRAME_SUPPORT_WARNING) +
                        '</div>' +
                        '</iframe>');
                    jItem.append(jIframe);

                    var src = Lia.p(newOptions, 'src');
                    if (String.isBlank(src)) {
                        src = jItem.dataAttr(Lia.Component.AttrName.SRC);
                    }

                    jIframe.attr({
                        'src': 'https://view.officeapps.live.com/op/embed.aspx' + Lia.convertArrayToQueryString({
                            'src': src
                        })
                    });

                    jItem.addClass(Lia.Component.Flag.INITED);
                }
            }

            return this;
        }

    });

})(jQuery);


/**
 * div_placeholder_input
 *
 * input type=text
 * <div class="div_placeholder_input"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding 관련 속성></div>
 *
 * input type=password
 * <div class="image_placeholder_input password"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding 관련 속성>
 <input type="password" />
 </div>
 *
 * textarea
 * <div class="image_placeholder_input textarea"
 style="width:{배경 이미지 width};height:{배경 이미지 height};" data-lia-padding 관련 속성></div>
 *
 * border 속성은 css등 지정
 *
 * .divPlaceholderInputVal()
 *      입력 값 설정 및 받아오기
 * .divPlaceholderInput()
 *      실제 입력 DOM객체 받아오기
 *
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initDivPlaceholderInput();
 });

 */
(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initDivPlaceholderInput: function (j) {

            var selector = '.' + Lia.Component.Name.DIV_PLACEHOLDER_INPUT;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initDivPlaceholderInput();
        }
    });

    $.fn.extend({


        /**
         * 포커스
         * @returns {*}
         */
        divPlaceholderInputFocus: function () {
            return this.children(':input').focus();
        },

        /**
         * 입력된 내용 세팅, 리턴
         * @param val
         * @returns {*}
         */
        divPlaceholderInputVal: function (val) {

            if (val == undefined)
                return this.children(':input').val();
            else
                this.children(':input').val(val);

            return this.checkDivPlaceholderInput();
        },

        /**
         * 내용에 다른 placeholder 체크
         * @returns {*}
         */
        checkDivPlaceholderInput: function () {

            return this.find(':input').change();

        },

        /**
         * 실제 input 태그 반환
         * @returns {*}
         */
        divPlaceholderInput: function () {
            return this.find(':input');
        },


        adjustDivPlaceholderSize: function () {

            return this.each(function () {

                var jThis = $(this);

                var height = jThis.height();
                var width = jThis.width();

                var isTextarea = jThis.hasClass(Lia.Component.Flag.TEXTAREA);
                var jInput = jThis.children(':input');

                var padding = jThis.dataAttr(Lia.Component.AttrName.PADDING);
                var paddingVertical = jThis.dataAttr(Lia.Component.AttrName.PADDING_VERTICAL);
                if (paddingVertical == undefined)
                    paddingVertical = padding;
                var paddingHorizontal = jThis.dataAttr(Lia.Component.AttrName.PADDING_HORIZONTAL);
                if (paddingHorizontal == undefined)
                    paddingHorizontal = padding;
                var paddingLeft = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingLeft == undefined)
                    paddingLeft = paddingHorizontal;
                var paddingRight = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingRight == undefined)
                    paddingRight = paddingHorizontal;
                var paddingTop = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingTop == undefined)
                    paddingTop = paddingVertical;
                var paddingBottom = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingBottom == undefined)
                    paddingBottom = paddingVertical;

                jInput.css({
                    'position': 'relative',
                    'margin': '0px'
                });

                if (paddingLeft != undefined)
                    jInput.css({'paddingLeft': paddingLeft});
                if (paddingRight != undefined)
                    jInput.css({'paddingRight': paddingRight});
                if (paddingTop != undefined)
                    jInput.css({'paddingTop': paddingTop});
                if (paddingBottom != undefined)
                    jInput.css({'paddingBottom': paddingBottom});

                var inputPaddingLeft = jInput.css('padding-left');
                var inputPaddingRight = jInput.css('padding-right');
                var inputPaddingTop = jInput.css('padding-top');
                var inputPaddingBottom = jInput.css('padding-bottom');
                var inputBorderLeftWidth = jInput.css('border-left-width');
                var inputBorderRightWidth = jInput.css('border-right-width');
                var inputBorderTopWidth = jInput.css('border-top-width');
                var inputBorderBottomWidth = jInput.css('border-bottom-width');
                var inputLeft = parseFloat(inputPaddingLeft) + parseFloat(inputBorderLeftWidth);
                var inputRight = parseFloat(inputPaddingRight) + parseFloat(inputBorderRightWidth);
                var inputTop = parseFloat(inputPaddingTop) + parseFloat(inputBorderTopWidth);
                var inputBottom = parseFloat(inputPaddingBottom) + parseFloat(inputBorderBottomWidth);

                var inputWidth = width - inputLeft - inputRight;
                var inputHeight = height - inputTop - inputBottom;
                jInput.css({
                    'width': inputWidth + 'px',
                    'height': inputHeight + 'px'
                });

                if (!isTextarea && Lia.ieVersion != -1)
                    jInput.css('line-height', inputHeight + 'px');

                var jPlaceholder = jThis.children('div');
                jPlaceholder.css({
                    'width': inputWidth + 'px',
                    'height': inputHeight + 'px',
                    'line-height': inputHeight + 'px',
                    'padding-left': inputLeft + 'px',
                    'padding-right': inputRight + 'px',
                    'padding-top': inputTop + 'px',
                    'padding-bottom': inputBottom + 'px'
                });

            });

        },

        /**
         * 초기화
         * @returns {*}
         */
        initDivPlaceholderInput: function () {

            this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.INITED))
                    return;

                var height = jThis.height();
                var width = jThis.width();

                var placeholder = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER);
                if (String.isNullOrWhitespace(placeholder))
                    placeholder = '';

                var isTextarea = jThis.hasClass(Lia.Component.Flag.TEXTAREA);
                var jInput = jThis.children(':input');
                if (jInput.size() == 0) {
                    jInput = $('<' + (isTextarea ? 'textarea' : 'input') + ' ' +
                        ((isTextarea) ? '' : ('type="' + (jThis.hasClass(Lia.Component.Flag.PASSWORD) ? 'password' : 'text') + '"')) + '/>');
                    jThis.append(jInput);
                }


                if (isTextarea) {
                    var isImageInputNoResize = jThis.hasClass(Lia.Component.Flag.NO_RESIZE);
                    if (isImageInputNoResize)
                        jInput.css('resize', 'none');

                    var isImageInputHiddenOverflow = jThis.hasClass(Lia.Component.Flag.HIDDEN_OVERFLOW);
                    var overflow = 'auto';
                    if (isImageInputHiddenOverflow)
                        overflow = 'hidden';

                    jInput.css('overflow', overflow);
                }

                var padding = jThis.dataAttr(Lia.Component.AttrName.PADDING);
                var paddingVertical = jThis.dataAttr(Lia.Component.AttrName.PADDING_VERTICAL);
                if (paddingVertical == undefined)
                    paddingVertical = padding;
                var paddingHorizontal = jThis.dataAttr(Lia.Component.AttrName.PADDING_HORIZONTAL);
                if (paddingHorizontal == undefined)
                    paddingHorizontal = padding;
                var paddingLeft = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingLeft == undefined)
                    paddingLeft = paddingHorizontal;
                var paddingRight = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingRight == undefined)
                    paddingRight = paddingHorizontal;
                var paddingTop = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingTop == undefined)
                    paddingTop = paddingVertical;
                var paddingBottom = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (paddingBottom == undefined)
                    paddingBottom = paddingVertical;

                jInput.css({
                    'position': 'relative',
                    'margin': '0px'
                });

                if (paddingLeft != undefined)
                    jInput.css({'paddingLeft': paddingLeft});
                if (paddingRight != undefined)
                    jInput.css({'paddingRight': paddingRight});
                if (paddingTop != undefined)
                    jInput.css({'paddingTop': paddingTop});
                if (paddingBottom != undefined)
                    jInput.css({'paddingBottom': paddingBottom});

                var inputPaddingLeft = jInput.css('padding-left');
                var inputPaddingRight = jInput.css('padding-right');
                var inputPaddingTop = jInput.css('padding-top');
                var inputPaddingBottom = jInput.css('padding-bottom');
                var inputBorderLeftWidth = jInput.css('border-left-width');
                var inputBorderRightWidth = jInput.css('border-right-width');
                var inputBorderTopWidth = jInput.css('border-top-width');
                var inputBorderBottomWidth = jInput.css('border-bottom-width');
                var inputLeft = parseFloat(inputPaddingLeft) + parseFloat(inputBorderLeftWidth);
                var inputRight = parseFloat(inputPaddingRight) + parseFloat(inputBorderRightWidth);
                var inputTop = parseFloat(inputPaddingTop) + parseFloat(inputBorderTopWidth);
                var inputBottom = parseFloat(inputPaddingBottom) + parseFloat(inputBorderBottomWidth);

                var inputWidth = width - inputLeft - inputRight;
                var inputHeight = height - inputTop - inputBottom;
                jInput.css({
                    'width': inputWidth + 'px',
                    'height': inputHeight + 'px'
                });

                if (!isTextarea && Lia.ieVersion != -1)
                    jInput.css('line-height', inputHeight + 'px');

                var textColor = jThis.dataAttr(Lia.Component.AttrName.TEXT_COLOR);
                var fontWeight = jThis.dataAttr(Lia.Component.AttrName.FONT_WEIGHT);
                var fontSize = jThis.dataAttr(Lia.Component.AttrName.FONT_SIZE);
                var fontFamily = jThis.dataAttr(Lia.Component.AttrName.FONT_FAMILY);

                if (textColor != undefined)
                    jInput.css('color', textColor);

                if (fontWeight != undefined)
                    jInput.css('font-weight', fontWeight);

                if (fontSize != undefined)
                    jInput.css('font-size', fontSize);

                if (fontFamily != undefined)
                    jInput.css('font-family', fontFamily);

                var jPlaceholder = $('<div />');
                jPlaceholder.css({
                    'position': 'absolute',
                    'display': 'none',
                    'left': '0px',
                    'top': '0px',
                    'margin': '0px',
                    'width': inputWidth + 'px',
                    'height': inputHeight + 'px',
                    'line-height': inputHeight + 'px',
                    'padding-left': inputLeft + 'px',
                    'padding-right': inputRight + 'px',
                    'padding-top': inputTop + 'px',
                    'padding-bottom': inputBottom + 'px',
                    'cursor': 'text'
                }).append($('<span>' + placeholder + '</span>'));


                var placeholderTextColor = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER_TEXT_COLOR);
                var placeholderFontWeight = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_WEIGHT);
                var placeholderFontSize = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_SIZE);
                var placeholderFontFamily = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_FAMILY);

                if (placeholderTextColor != undefined)
                    jPlaceholder.css('color', placeholderTextColor);

                if (placeholderFontWeight != undefined)
                    jPlaceholder.css('font-weight', placeholderFontWeight);

                if (placeholderFontSize != undefined)
                    jPlaceholder.css('font-size', placeholderFontSize);

                if (placeholderFontFamily != undefined)
                    jPlaceholder.css('font-family', placeholderFontFamily);

                jThis.append(jPlaceholder);

                jThis.children('div').click(function () {
                    var jThis = $(this);
                    jThis.hide();
                    jThis.parent().children(':input').focus();
                });

                jThis.children(':input').change(liaCheckDivPlaceholderInput).focus(function () {

                    var jThis = $(this);
                    jThis.parent().children('div').hide();

                }).focusout(liaCheckDivPlaceholderInput).change();

                jThis.addClass(Lia.Component.Flag.INITED);
            });
        }

    });
})(jQuery);

function liaCheckDivPlaceholderInput() {
    var jThis = $(this);
    var jParent = jThis.parent();

    if (jThis.val() == '')
        jParent.children('div').show();
    else
        jParent.children('div').hide();
}

/**
 * text_placeholder_input
 *
 *  <input type="text class="text_placeholder_input" data-lia-placeholder="{PLACEHOLDER}" />
 *
 * .textPlaceholderInputVal();
 * .
 *
 * outline:none; 속성으로 포커스시 하이라이트 없앨 수 있음
 * border 설정
 */
/*
 $(document).ready(function() {
 $.initTextPlaceholderInput();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initTextPlaceholderInput: function (j) {
            if (j == undefined)
                j = $('.' + Lia.Component.Name.TEXT_PLACEHOLDER_INPUT);
            else
                j = j.find('.' + Lia.Component.Name.TEXT_PLACEHOLDER_INPUT);

            return j.initTextPlaceholderInput();
        }
    });

    $.fn.extend({

        /**
         * 내용 체크하여 placeholder 반영
         *
         * @returns {*}
         */
        checkTextPlaceholderInput: function () {

            return this.change();
        },

        /**
         * 실제 입력값 세팅, 리턴
         *
         * @param val
         * @returns {*}
         */
        textPlaceholderInputVal: function (val) {

            if (val == undefined) {
                val = this.val();

                var placeholderText = this.dataAttr(Lia.Component.AttrName.PLACEHOLDER);
                if (placeholderText == undefined)
                    return val;

                placeholderText += Lia.Component.Value.TextPlaceholderInput.APPEND_TEXT;

                if (placeholderText == val)
                    val = '';

                return val;
            }

            return this.val(val).checkTextPlaceholderInput();

        },

        /**
         * placeholder view 상태 설정
         *
         * @param on
         */
        setTextPlaceHolderInputStatus: function (on) {

            for (var i = 0, l = this.length; i < l; i++) {
                var jItem = this.eq(i);

                var textColor = undefined;
                var fontWeight = undefined;
                var fontSize = undefined;
                var fontFamily = undefined;

                if (on) {
                    textColor = jItem.dataAttr(Lia.Component.AttrName.PLACEHOLDER_TEXT_COLOR);
                    fontWeight = jItem.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_WEIGHT);
                    fontSize = jItem.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_SIZE);
                    fontFamily = jItem.dataAttr(Lia.Component.AttrName.PLACEHOLDER_FONT_FAMILY);
                } else {
                    textColor = jItem.dataAttr(Lia.Component.AttrName.TEXT_COLOR);
                    fontWeight = jItem.dataAttr(Lia.Component.AttrName.FONT_WEIGHT);
                    fontSize = jItem.dataAttr(Lia.Component.AttrName.FONT_SIZE);
                    fontFamily = jItem.dataAttr(Lia.Component.AttrName.FONT_FAMILY);
                }

                if (textColor != undefined)
                    jItem.css('color', textColor);

                if (fontWeight != undefined)
                    jItem.css('font-weight', fontWeight);

                if (fontSize != undefined)
                    jItem.css('font-size', fontSize);

                if (fontFamily != undefined)
                    jItem.css('font-family', fontFamily);
            }

        },

        /**
         * 크기 재조정
         *
         * @returns {*}
         */
        adjustTextPlaceHolderInput: function () {

            return this.each(function () {

                var jThis = $(this);

                var paddingLeft = Lia.Component.AttrName.PADDING_LEFT;
                var paddingRight = Lia.Component.AttrName.PADDING_RIGHT;
                var paddingTop = Lia.Component.AttrName.PADDING_TOP;
                var paddingBottom = Lia.Component.AttrName.PADDING_BOTTOM;
                var padding = jThis.dataAttr(Lia.Component.AttrName.PADDING);
                if (padding != undefined) {
                    paddingLeft = padding;
                    paddingRight = padding;
                    paddingTop = padding;
                    paddingBottom = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_HORIZONTAL);
                if (padding != undefined) {
                    paddingLeft = padding;
                    paddingRight = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_VERTICAL);
                if (padding != undefined) {
                    paddingTop = padding;
                    paddingBottom = padding;
                }

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_LEFT);
                if (padding != undefined)
                    paddingLeft = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_RIGHT);
                if (padding != undefined)
                    paddingRight = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_TOP);
                if (padding != undefined)
                    paddingTop = padding;

                padding = jThis.dataAttr(Lia.Component.AttrName.PADDING_BOTTOM);
                if (padding != undefined)
                    paddingBottom = padding;

                jThis.css({
                    'padding-left': paddingLeft,
                    'padding-right': paddingRight,
                    'padding-top': paddingTop,
                    'padding-bottom': paddingBottom
                });

                var width = undefined;
                var inputWidth = jThis.dataAttr(Lia.Component.AttrName.WIDTH);
                if (inputWidth != undefined)
                    width = (parseFloat(inputWidth) - parseFloat(paddingLeft) - parseFloat(paddingRight)
                        - parseFloat(jThis.css('border-left-width')) - parseFloat(jThis.css('border-right-width'))) + 'px';

                if (width != undefined)
                    jThis.css('width', width);

                var height = undefined;
                var inputHeight = jThis.dataAttr(Lia.Component.AttrName.HEIGHT);
                if (inputHeight != undefined)
                    height = (parseFloat(inputHeight) - parseFloat(paddingTop) - parseFloat(paddingBottom)
                        - parseFloat(jThis.css('border-top-width')) - parseFloat(jThis.css('border-bottom-width'))) + 'px';

                if (height != undefined)
                    jThis.css('height', height);

                if (this.tagName != 'TEXTAREA' && Lia.ieVersion != -1 && inputHeight != undefined)
                    jThis.css('line-height', height);
            });
        },

        /**
         * 초기화
         *
         * @returns {*}
         */
        initTextPlaceholderInput: function () {

            this.each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.INITED))
                    return;

                var path = jThis.dataAttr(Lia.Component.AttrName.BACKGROUND_IMAGE);
                if (path != undefined)
                    jThis.css('background-image', 'url(' + path + ')');

                jThis.adjustTextPlaceHolderInput().change(liaCheckTextPlaceholderInput).focus(function () {

                    var jThis = $(this);

                    var placeholderText = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER);
                    if (placeholderText == undefined)
                        return;

                    placeholderText += Lia.Component.Value.TextPlaceholderInput.APPEND_TEXT;

                    var val = jThis.val();
                    if (placeholderText == val)
                        jThis.val('');


                    jThis.setTextPlaceHolderInputStatus(false);

                }).focusout(liaCheckTextPlaceholderInput).change();

                jThis.addClass(Lia.Component.Flag.INITED);
            });

            return this;
        }

    });
})(jQuery);

function liaCheckTextPlaceholderInput() {
    var jThis = $(this);
    var placeholderText = jThis.dataAttr(Lia.Component.AttrName.PLACEHOLDER);
    if (placeholderText == undefined)
        return;

    placeholderText += Lia.Component.Value.TextPlaceholderInput.APPEND_TEXT;

    var val = jThis.val();
    if (val == '')
        jThis.val(placeholderText);

    jThis.setTextPlaceHolderInputStatus((val == '' || val == placeholderText));
}

/**
 *  flat_button jut
 *
 *  flat_button을 볼록 효과가 나도록 함
 *
 *  data-lia-shadow-width
 *    그림자 영역
 *    %, px 가능
 */
/*
 초기화 코드

 $(document).ready(function () {

 $.initFlatButton();
 $.initJutFlatButton();
 });
 */

(function ($) {

    $.extend({

        /**
         * 초기화
         */
        initJutFlatButton: function (j) {

            var selector = '.' + Lia.Component.Name.FLAT_BUTTON + '.' + Lia.Component.Flag.JUT;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initJutFlatButton();
        }
    });

    $.fn.extend({

        jutFlatButtonPressed: function (pressed) {

            return this.buttonPressed(pressed);
        },

        initJutFlatButton: function () {

            return this.initFlatButton().each(function () {

                var jThis = $(this);
                if (jThis.hasClass(Lia.Component.Flag.JUT_INITED))
                    return;

                var html = jThis.html();

                var jFlatButton = $('<div></div>');

                if (jThis.hasClass(Lia.Component.Flag.HOVER))
                    jFlatButton.addClass(Lia.Component.Flag.HOVER);

                if (jThis.hasClass(Lia.Component.Flag.PRESS)) {
                    jFlatButton.addClass(Lia.Component.Flag.PRESS);
                }

                if (jThis.hasClass(Lia.Component.Flag.NO_CHANGE))
                    jFlatButton.addClass(Lia.Component.Flag.NO_CHANGE);

                if (jThis.hasClass(Lia.Component.Flag.NO_BIND))
                    jFlatButton.addClass(Lia.Component.Flag.NO_BIND);

                if (jThis.hasClass(Lia.Component.Flag.NO_DIM))
                    jFlatButton.addClass(Lia.Component.Flag.NO_DIM);

                if (jThis.hasClass(Lia.Component.Flag.PRESSED))
                    jFlatButton.addClass(Lia.Component.Flag.PRESSED);

                jFlatButton.append(html);

                var pressDefaultBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.JUT_DEFAULT_BACKGROUND_COLOR);
                if (pressDefaultBackgroundColor != undefined)
                    jFlatButton.dataAttr(Lia.Component.AttrName.DEFAULT_BACKGROUND_COLOR, pressDefaultBackgroundColor);
                var pressHoveringBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.JUT_HOVERING_BACKGROUND_COLOR);
                if (pressHoveringBackgroundColor != undefined)
                    jFlatButton.dataAttr(Lia.Component.AttrName.HOVERING_BACKGROUND_COLOR, pressHoveringBackgroundColor);
                var pressPressedBackgroundColor = jThis.dataAttr(Lia.Component.AttrName.JUT_PRESSED_BACKGROUND_COLOR);
                if (pressPressedBackgroundColor != undefined)
                    jFlatButton.dataAttr(Lia.Component.AttrName.PRESSED_BACKGROUND_COLOR, pressPressedBackgroundColor);

                var roundWidth = jThis.dataAttr(Lia.Component.AttrName.ROUND_WIDTH);
                if (roundWidth != undefined)
                    jFlatButton.dataAttr(Lia.Component.AttrName.ROUND_WIDTH, roundWidth);

                var direction = jThis.dataAttr(Lia.Component.AttrName.DIRECTION);
                if (direction != undefined)
                    jFlatButton.dataAttr(Lia.Component.AttrName.DIRECTION, direction);

                var height = jThis.height();
                var shadowWidth = jThis.dataAttr(Lia.Component.AttrName.SHADOW_WIDTH);
                if (shadowWidth == undefined)
                    shadowWidth = Lia.Component.Value.Button.FlatButton.DEFAULT_SHADOW_WIDTH;

                var shadowWidthPx = parseFloat(shadowWidth);
                if (shadowWidth.lastIndexOf('%'))
                    shadowWidthPx = height * shadowWidthPx / 100;

                var width = jThis.width();

                jThis.empty().append(jFlatButton.css({
                    'position': 'relative',
                    'width': width + 'px',
                    'height': (height - shadowWidthPx),
                    'top': '0px',
                    'left': '0px'
                }).initFlatButton());

                jThis.on(Lia.Component.Event.STATUS_CHANGED, {
                    jFlatButton: jFlatButton
                }, function (e) {

                    var jFlatButton = Lia.p(e, 'data', 'jFlatButton');
                    jFlatButton.checkFlatButtonByStatus(e.status);
                });

                jThis.checkButtonStatus();
                jThis.addClass(Lia.Component.Flag.JUT_INITED);
            });
        }
    });

})(jQuery);


var Base64Helper = jQuery.Base64Helper = Lia.Base64Helper = {

    KEY: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",

    encode: function (input, key) {

        if (key == undefined) {
            key = Lia.Base64Helper.KEY;
        }

        var output = "";
        var chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        var i = 0;

        input = Lia.Base64Helper._utf8_encode(input);

        while (i < input.length) {

            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);

            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;

            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            } else if (isNaN(chr3)) {
                enc4 = 64;
            }

            output = output + key.charAt(enc1) + key.charAt(enc2) + key.charAt(enc3) + key.charAt(enc4);
        }

        return output;
    },


    decode: function (input, key) {

        if (key == undefined) {
            key = Lia.Base64Helper.KEY;
        }

        var output = "";
        var chr1, chr2, chr3;
        var enc1, enc2, enc3, enc4;
        var i = 0;

        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");

        while (i < input.length) {

            enc1 = key.indexOf(input.charAt(i++));
            enc2 = key.indexOf(input.charAt(i++));
            enc3 = key.indexOf(input.charAt(i++));
            enc4 = key.indexOf(input.charAt(i++));

            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;

            output = output + String.fromCharCode(chr1);

            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }
            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }
        }

        output = Lia.Base64Helper._utf8_decode(output);

        return output;

    },

    _utf8_encode: function (string) {
        string = string.replace(/\r\n/g, "\n");
        var utftext = "";

        for (var n = 0; n < string.length; n++) {

            var c = string.charCodeAt(n);

            if (c < 128) {
                utftext += String.fromCharCode(c);
            } else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            } else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }

        }

        return utftext;
    },

    _utf8_decode: function (utftext) {
        var string = "";
        var i = 0;
        var c = 0;
        var c2 = 0;
        var c3 = 0;

        while (i < utftext.length) {

            c = utftext.charCodeAt(i);

            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            } else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            } else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        }

        return string;
    }
};


var RSAHelper = jQuery.RSAHelper = Lia.RSAHelper = {

    encrypt : function( plain, publicKey ) {

        var jsEncrypt = new JSEncrypt();
        jsEncrypt.setPublicKey(publicKey);
        return jsEncrypt.encrypt(plain);
    },

    decrypt : function( encrypted, privateKey ) {

        var jsEncrypt = new JSEncrypt();
        jsEncrypt.setPrivateKey(privateKey);
        return jsEncrypt.decrypt(encrypted);
    }
};




(function ($) {

    $.extend({

        liaFileUploaderMaxFileSize: undefined,
        setFileUploaderMaxFileSize: function (size) {
            jQuery.liaFileUploaderMaxFileSize = size;
        },

        liaFileUploaderAllowedExtensionList: undefined,
        setFileUploaderAllowedExtensionList: function (list) {
            jQuery.liaFileUploaderAllowedExtensionList = list;
        },

        liaFileUploaderHtml: Lia.Component.Value.FileUploader.DEFAULT_HTML,
        setFileUploaderHtml: function (html) {
            jQuery.liaFileUploaderHtml = html;
        },

        liaFileUploaderAttachmentHtml: Lia.Component.Value.FileUploader.DEFAULT_ATTACHMENT_HTML,
        setFileUploaderAttachmentHtml: function (html) {
            jQuery.liaFileUploaderAttachmentHtml = html;
        },

        liaFileUploaderOpensWithoutViewer: Lia.Component.Value.FileUploader.DEFAULT_OPENS_WITHOUT_VIEWER,
        setFileUploaderOpensWithoutViewer: function ( flag ) {
            jQuery.liaFileUploaderOpensWithoutViewer = flag;
        },

        liaFileUploaderAttachmentFileViewHtml: Lia.Component.Value.FileUploader.DEFAULT_ATTACHMENT_FILE_VIEW_HTML,
        setFileUploaderAttachmentFileViewHtml: function (html) {
            jQuery.liaFileUploaderAttachmentFileViewHtml = html;
        },

        liaFileUploaderAttachmentDeleteButtonHtml: Lia.Component.Value.FileUploader.DEFAULT_ATTACHMENT_DELETE_BUTTON_HTML,
        setFileUploaderAttachmentDeleteButtonHtml: function (html) {
            jQuery.liaFileUploaderAttachmentDeleteButtonHtml = html;
        },

        liaFileUploaderAttachmentHandler: Lia.Component.Value.FileUploader.DEFAULT_ATTACHMENT_HANDLER,
        setFileUploaderAttachmentHandler: function (handler) {
            jQuery.liaFileUploaderAttachmentHandler = handler;
        },

        liaFileUploaderHandler: function (options) {

            var jFileUploader = Lia.p(options, 'jFileUploader');
            var jForm = Lia.p(options, 'jForm');
            var jInput = Lia.p(options, 'jInput');
            var onUploaded = Lia.p(options, 'onUploaded');
            var useLastFile = Lia.p(options, 'useLastFile');

            var popup = undefined;
            if (Requester.isProgressSupported) {
                popup = AjaxPopupManager.show(Lia.Popup.Progress.NAME, {}, {
                    jsFilePath: Lia.Popup.Progress.JS_FILE_PATH,
                    htmlFilePath: Lia.Popup.Progress.HTML_FILE_PATH
                });
            } else {
                LoadingPopupManager.show();
            }

            Requester.formUploadWithoutBlank(ApiUrl.File.UPLOAD, {
                categoryCode: UploadedFileCategory.BOARD_ATTACHMENT_PUBLIC
            }, jForm, function (status, data, request) {

                var jInput = request.object.jInput;

                var jForm = request.object.jForm;
                var jFileUploader = request.object.jFileUploader;
                var onUploaded = request.object.onUploaded;
                var useLastFile = request.object.useLastFile;

                if (Requester.isProgressSupported) {
                    var popup = request.object.popup;
                    popup.hide();

                } else {
                    LoadingPopupManager.hide();
                }

                if (status != Lia.Requester.Status.SUCCESS) {
                    return;
                }

                var list = Lia.p(data, 'body', 'list');
                if (list == undefined || list.length == 0) {
                    PopupManager.alert('안내', '업로드 된 파일을 찾을 수 없습니다.');
                    return;
                }


                if (useLastFile == true) {
                    jFileUploader.fileUploaderVal([]);
                }

                for (var i = 0, l = list.length; i < l; i++) {

                    var item = list[i];
                    jFileUploader.fileUploaderAdd(item);
                }

                if (onUploaded != undefined) {
                    onUploaded.call(jFileUploader, list);
                }

                jInput.val('');

            }, function (data, request) {

                var popup = request.object.popup;
                if (popup != undefined) {

                    if (!popup.isInited()) {
                        return;
                    }

                    var percent = Lia.pd(0, data, 'percentComplete');
                    if (popup.setPercent != undefined) {
                        popup.setPercent(percent);
                    }
                }

            }, {
                jFileUploader: jFileUploader,
                jForm: jForm,
                jInput: jInput,
                popup: popup,
                onUploaded: onUploaded,
                useLastFile: useLastFile
            });

        },
        setFileUploaderHandler: function (handler) {
            jQuery.liaFileUploaderHandler = handler;
        },

        setFileUploaderOptions: function (options) {
            jQuery.liaFileUploaderOptions = options;
        },

        /**
         * 초기화
         */
        initFileUploader: function (j, option) {

            var selector = '.' + Lia.Component.Name.FILE_UPLOADER;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initFileUploader(option);
        },

        initFileUploaderList: function (j, option) {

            var selector = '.' + Lia.Component.Name.FILE_UPLOADER_LIST;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initFileUploaderList(option);
        }
    });

    $.fn.extend({

        initFileUploader: function (options) {

            var newOptions = Lia.deepCopy(Lia.pd({}, jQuery.liaFileUploaderOptions));
            Lia.combine(newOptions, options);

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    var html = Lia.pd( jQuery.liaFileUploaderHtml, newOptions, 'html');
                    jItem.append(html);

                    // 파일 리스트 초기화
                    jQuery.initFileUploaderList(jItem, newOptions);

                    var jForm = jItem.find('form');
                    var jInput = jItem.find('input[type="file"]');

                    var maxFileSize = Lia.pd(jQuery.liaFileUploaderMaxFileSize, newOptions, 'maxFileSize');
                    var allowedExtensionList = Lia.pd(jQuery.liaFileUploaderAllowedExtensionList, newOptions, 'allowedExtensionList');
                    var useLastFile = Lia.pd(false, newOptions, 'useLastFile');
                    var maxFileCount = Lia.p(newOptions, 'maxFileCount');
                    var onUploaded = Lia.pd(undefined, newOptions, 'onUploaded');
                    var viewsFileContent = Lia.pd(false, newOptions, 'viewsFileContent');

                    jInput.on('change', {
                        jItem: jItem,
                        jForm: jForm,
                        jInput: jInput,
                        maxFileSize: maxFileSize,
                        allowedExtensionList: allowedExtensionList,
                        maxFileCount: maxFileCount,
                        onUploaded: onUploaded,
                        useLastFile: useLastFile
                    }, function (e) {

                        // TODO: 화면내에 기본 file_uploader를 init하고, 동적으로 file_uploader를 생성 후 init 하였을 때,
                        //       기본 file_uploader form 객체들이 초기화되고, 동적 파일추가 기능이 동작하지 않음.
                        //       (change 이벤트시 참조하는 jItem이 동적기능의 jItem이 아닌 기본 jItem을 참조함..)

                        var jItem = e.data.jItem;
                        var jForm = e.data.jForm;
                        var jInput = e.data.jInput;
                        var onUploaded = e.data.onUploaded;
                        var useLastFile = e.data.useLastFile;

                        var maxFileCount = e.data.maxFileCount;
                        if (String.isNotBlank(maxFileCount)) {

                            var list = jItem.fileUploaderVal();
                            if (list != undefined && list.length >= maxFileCount) {
                                PopupManager.alert('안내', '첨부파일은 ' + maxFileCount + '개를 초과할 수 없습니다.');
                                return;
                            }
                        }

                        var maxFileSize = e.data.maxFileSize;
                        if (String.isNotBlank(maxFileSize)) {

                            var files0 = this.files[0];
                            var fileSize = files0.size || files0.fileSize;

                            if (fileSize > maxFileSize) {

                                jInput.val('');
                                var mb = maxFileSize / (1024 * 1024);
                                PopupManager.alert('안내', '첨부파일 용량은 ' + mb + 'MB 를 초과할 수 없습니다.');
                                return;
                            }
                        }

                        var allowedExtensionList = e.data.allowedExtensionList;
                        if (String.isNotBlank(allowedExtensionList)) {

                            var inputVal = jInput.val();
                            var ext = FileHelper.extractFileExtOnly(inputVal);
                            var filtered = true;
                            if (String.isNotBlank(ext)) {

                                var extList = allowedExtensionList.split(',');
                                for (var i = 0, l = extList.length; i < l; i++) {

                                    var extListItem = extList[i];
                                    if (extListItem.toLowerCase().trim() == ext.trim()) {
                                        filtered = false;
                                        break;
                                    }
                                }
                            }

                            if (filtered == true) {

                                jInput.val('');
                                PopupManager.alert('안내', '업로드 가능한 파일 확장자는 ' + allowedExtensionList + '입니다.');
                                return;
                            }
                        }

                        jQuery.liaFileUploaderHandler({
                            jFileUploader: jItem,
                            jForm: jForm,
                            jInput: jInput,
                            onUploaded: onUploaded,
                            useLastFile: useLastFile
                        });
                    });

                    jItem.addClass(Lia.Component.Flag.INITED);
                }
            }


            return this;
        },


        initFileUploaderList: function (options) {

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    jItem.hide();

                    var viewsFileContent = Lia.pcd(false, options, 'viewsFileContent');
                    var attachmentHtml = Lia.pd( jQuery.liaFileUploaderAttachmentHtml, options, 'attachmentHtml');
                    var attachmentDeleteButtonHtml = Lia.pd( jQuery.liaFileUploaderAttachmentDeleteButtonHtml, options, 'attachmentDeleteButtonHtml');
                    var opensWithoutViewer = Lia.pd( jQuery.liaFileUploaderOpensWithoutViewer, options, 'opensWithoutViewer');

                    jItem.data(Lia.Component.Value.FileUploader.OPENS_WITHOUT_VIEWER, opensWithoutViewer);
                    jItem.data(Lia.Component.Value.FileUploader.VIEWS_FILE_CONTENT, viewsFileContent);
                    jItem.data(Lia.Component.Value.FileUploader.ATTACHMENT_HTML, attachmentHtml);
                    jItem.data(Lia.Component.Value.FileUploader.ATTACHMENT_DELETE_BUTTON_HTML, attachmentDeleteButtonHtml);

                    jItem.addClass(Lia.Component.Flag.INITED);
                }
            }


            return this;
        },


        // 파일 추가 연결만 시켜줌
        fileUploaderAdd: function (attachment, unuseDeleteButton) {

            this.find('.' + Lia.Component.Name.FILE_UPLOADER_LIST).fileUploaderListAdd(attachment, unuseDeleteButton);
            return this;

        },


        fileUploaderListAdd: function (attachment, unuseDeleteButton) {

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {
                    continue;
                }

                var attachmentHtml = jItem.data(Lia.Component.Value.FileUploader.ATTACHMENT_HTML);
                var attachmentDeleteButtonHtml = jItem.data(Lia.Component.Value.FileUploader.ATTACHMENT_DELETE_BUTTON_HTML);
                var viewsFileContent = jItem.data(Lia.Component.Value.FileUploader.VIEWS_FILE_CONTENT);
                var opensWithoutViewer = jItem.data(Lia.Component.Value.FileUploader.OPENS_WITHOUT_VIEWER);

                var jAttachment = jQuery.liaFileUploaderAttachmentHandler(attachment, {
                    unuseDeleteButton : unuseDeleteButton,
                    viewsFileContent : viewsFileContent,
                    attachmentHtml : attachmentHtml,
                    opensWithoutViewer : opensWithoutViewer,
                    attachmentDeleteButtonHtml : attachmentDeleteButtonHtml,
                });
                jItem.append(jAttachment);
                jAttachment.data(Lia.Component.Value.FileUploader.ATTACHMENT, attachment);

                jAttachment.find('.file_uploader_item_delete_button').on('click', {
                    jUploaderList: jItem
                }, function (e) {

                    $(this).parents('.file_uploader_item').remove();

                    var jUploaderList = e.data.jUploaderList;
                    if (jUploaderList.find('.file_uploader_item').length == 0) {

                        jUploaderList.hide();
                    }
                });


                jItem.show();
            }

        },


        fileUploaderVal: function (val, unuseDeleteButton) {

            if (val == undefined) {
                return this.find('.' + Lia.Component.Name.FILE_UPLOADER_LIST).fileUploaderListVal();
            }

            this.find('.' + Lia.Component.Name.FILE_UPLOADER_LIST).fileUploaderListVal(val, unuseDeleteButton);
            return this;

        },

        fileUploaderListVal: function (val, unuseDeleteButton) {

            if (val == undefined) {

                if (this.size() < 1) {

                    return undefined;

                } else {

                    var jItem = this.eq(0);
                    if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                        var attachmentList = [];

                        var jFileItem = jItem.find('.file_uploader_item');
                        for (var i = 0, l = jFileItem.length; i < l; i++) {

                            var jFileItemEq = jFileItem.eq(i);

                            var attachment = jFileItemEq.data(Lia.Component.Value.FileUploader.ATTACHMENT);
                            attachmentList.push(attachment);
                        }

                        return attachmentList;

                    } else {

                        return undefined;
                    }
                }
            }

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                if (jItem.hasClass(Lia.Component.Flag.INITED)) {

                    jItem.find('.file_uploader_item').remove();
                    jItem.hide();

                    var attachmentList = val;
                    if (attachmentList != undefined && attachmentList.length > 0) {

                        for (var i2 = 0, l2 = attachmentList.length; i2 < l2; i2++) {

                            var attachment = attachmentList[i2];
                            jItem.fileUploaderListAdd(attachment, unuseDeleteButton);
                        }

                    }

                }
            }

            return this;
        }

    });

})(jQuery);

/**
 * image_cover
 *
 * 버튼 컴포넌트 공용 모듈
 * ( image_button, image_box, flat_button, flat_button jut )
 */
/*
 $(document).ready(function() {
 $.initButton();
 });
 */

(function ($) {


    $.extend({

        /**
         * 초기화
         */

        liaImageCoverOptions: undefined,
        setImageCoverOptions: function (options) {
            jQuery.liaImageCoverOptions = options;
        },

        initImageCover: function (j, options) {

            var selector = '.' + Lia.Component.Name.IMAGE_COVER;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initImageCover(options);
        }
    });

    $.fn.extend({

        initImageCover: function (options) {

            for (var i = 0, l = this.length; i < l; i++) {

                var jEq = this.eq(i);
                if (jEq.hasClass(Lia.Component.Flag.INITED))
                    continue;

                var errorSrc = jEq.dataAttr(Lia.Component.AttrName.ERROR_SRC);
                if (String.isBlank(errorSrc)) {
                    errorSrc = Lia.p(jQuery.liaImageCoverOptions, 'errorSrc');
                }

                if (String.isBlank(errorSrc)) {
                    errorSrc = Lia.p(options, 'errorSrc');
                }

                var jImage = jEq.find('img');
                if (jImage.length == 0) {

                    jImage = $('<img />');
                    jEq.append(jImage);
                }

                var src = jEq.dataAttr(Lia.Component.AttrName.SRC);
                if (String.isBlank(jEq.css('position'))) {

                    jEq.css({
                        position: 'relative'
                    });
                }

                jEq.css({
                    'overflow': 'hidden'
                });

                jImage.css({
                    position: 'absolute'
                });
                jImage.attr({
                    src: src
                });


                var width = jEq.dataAttr(Lia.Component.AttrName.WIDTH);
                var height = jEq.dataAttr(Lia.Component.AttrName.HEIGHT);
                if (String.isNotBlank(width) && String.isNotBlank(height)) {
                    jEq.updateImageCover();
                }

                jImage.on('load', function () {

                    var jThis = $(this);
                    var jImageCover = jThis.parent();

                    var width = jImageCover.dataAttr(Lia.Component.AttrName.WIDTH);
                    var height = jImageCover.dataAttr(Lia.Component.AttrName.HEIGHT);
                    if (String.isBlank(width) || String.isBlank(height)) {

                        jImageCover.dataAttr(Lia.Component.AttrName.WIDTH, jThis.width());
                        jImageCover.dataAttr(Lia.Component.AttrName.HEIGHT, jThis.height());
                        jImageCover.updateImageCover();
                    }

                    jThis.removeClass(Lia.Component.Flag.IMAGE_ERROR);

                }).on('error', {
                    errorSrc: errorSrc
                }, function (e) {

                    var errorSrc = e.data.errorSrc;

                    var jThis = $(this);
                    jThis.addClass(Lia.Component.Flag.IMAGE_ERROR);

                    if (String.isNotBlank(errorSrc)) {
                        jThis.attr('src', errorSrc);
                    }
                });

                jEq.addClass(Lia.Component.Flag.INITED);
            }

            return this;
        },

        imageCoverUpdate: function () {
            return this.updateImageCover();
        },

        updateImageCover: function () {

            for (var i = 0, l = this.length; i < l; i++) {

                var jEq = this.eq(i);

                var wrapperWidth = jEq.width();
                var wrapperHeight = jEq.height();
                var wrapperRatio = wrapperWidth / wrapperHeight;

                var jImage = jEq.find('img');
                var imageWidth = parseFloat(jEq.dataAttr(Lia.Component.AttrName.WIDTH));
                var imageHeight = parseFloat(jEq.dataAttr(Lia.Component.AttrName.HEIGHT));
                var imageRatio = imageWidth / imageHeight;

                if (imageRatio > wrapperRatio) {

                    // height 기준
                    jImage.css({
                        width: 'auto',
                        height: wrapperHeight + 'px'
                    });

                    var willImageWidth = imageWidth * wrapperHeight / imageHeight;
                    jImage.css({
                        top: '0',
                        left: ((wrapperWidth - willImageWidth) / 2) + 'px'
                    });

                } else {

                    // width 기준
                    jImage.css({
                        width: wrapperWidth + 'px',
                        height: 'auto'
                    });

                    var willImageHeight = imageHeight * wrapperWidth / imageWidth;
                    jImage.css({
                        top: ((wrapperHeight - willImageHeight) / 2) + 'px',
                        left: '0'
                    });

                }
            }

            return this;
        }

    });
})(jQuery);


/*
 <div class="combo_box"></div>
 */

(function ($) {


    $.extend({

        liaComboBoxHtml: '<div class="combo_box_text" ' +
            'style="color:#5d5d5d;border:1px solid #d5d5d5;border-radius:5px;text-overflow:ellipsis;white-space:nowrap;word-wrap:normal;overflow:hidden;' +
            'position:relative;padding-left:10px;padding-right:10px;;height: 38px;' +
            'line-height:38px;color:rgb(93, 93, 93);font-size:13px;font-family: notokr-regular, NanumGothic;text-align:left">' +
            '</div>' +
            '<div class="combo_box_arrow" ' +
            'style="position:absolute;text-align:right;left:0px;top:0px;right:0px;bottom:0px;padding-left:11px;padding-right:11px;height:40px;line-height:40px;font-size:10px;font-family: notokr-regular, NanumGothic; color:#b0aaa8;">' +
            '<img src="/res/lia/img/combo_box/img_arrow.png" style="width:10px;" />' +
            '</div>' +
            '<select class="combo_box_select" ' +
            'style="color:rgb(93, 93, 93);cursor:pointer;box-sizing:border-box;padding-left:10px;height:40px;padding-right:10px;position:absolute;left:0;right:0;color:rgb(93, 93, 93);top:0;bottom:0; width:100%; opacity:0; filter: alpha(opacity=0); ' +
            'outline:none;font-size:13px;font-family: notokr-regular, NanumGothic;">' +
            '</select>',


        setComboBoxHtml: function (html) {

            jQuery.liaComboBoxHtml = html;
        },

        liComboBoxTheme: {

            css: {
                'position': 'relative',
                'background-color': '#ffffff'

            }
        },

        setComboBoxTheme: function (theme) {

            jQuery.liComboBoxTheme = theme;
        },

        /**
         * 초기화
         */
        initComboBox: function (j, options) {

            var selector = '.' + Lia.Component.Name.COMBO_BOX;

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initComboBox(options);
        }
    });

    $.fn.extend({


        initComboBox: function (options) {


            for (var i = 0, l = this.size(); i < l; i++) {

                var jThis = this.eq(i);
                if (jThis.hasClass(Lia.Component.Flag.INITED))
                    return;

                var html = Lia.pd(jQuery.liaComboBoxHtml, options, 'html');
                var theme = Lia.pd(jQuery.liComboBoxTheme, options, 'theme');

                jThis.append(html);

                var attr = Lia.p(theme, 'attr');
                if (attr != undefined) {
                    jThis.attr(attr);
                }

                var css = Lia.p(theme, 'css');
                if (css != undefined) {
                    jThis.css(css);
                }

                jThis.find('.combo_box_select').on('change', {
                    jComboBox: jThis
                }, function (e, unExecuteOnSelectedListener) {

                    var jComboBox = e.data.jComboBox;
                    var jSelected = jComboBox.find("option:selected");
                    jComboBox.find('.combo_box_text').text(jSelected.text());
                    if (unExecuteOnSelectedListener != undefined && unExecuteOnSelectedListener == true) {
                        return;
                    }

                    var selectedOption = jSelected.data('combo-box-option');
                    var selectedEvent = new jQuery.Event(Lia.Component.Event.SELECTED);
                    selectedEvent.value = jSelected.attr('value');
                    selectedEvent.option = selectedOption;
                    jComboBox.trigger(selectedEvent);

                });


                jThis.addClass(Lia.Component.Flag.INITED);

                var optionList = Lia.p(options, 'optionList');
                if (optionList != undefined)
                    jThis.comboBoxOptionList(optionList);
            }

            return this;
        },

        comboBoxVal: function (val, unExecuteOnSelectedListener) {


            if (val == undefined) {

                var jSelected = this.find('option:selected');
                return jSelected.attr('value');
            }


            for (var i = 0, l = this.size(); i < l; i++) {

                var jEq = this.eq(i);

                var jOptionList = jEq.find('option');
                var jOptionListLength = jOptionList.length;
                if (jOptionListLength > 0) {

                    for (var i = 0, l = jOptionListLength; i < l; i++) {

                        var jOption = jOptionList.eq(i);
                        var optionValue = jOption.attr('value');
                        if (optionValue == val) {
                            jOption.prop('selected', true);
                            this.comboBoxChange(unExecuteOnSelectedListener);
                            return;
                        }
                    }
                }

                this.comboBoxChange(unExecuteOnSelectedListener);
            }

            return this;
        },

        comboBoxChange: function (unExecuteOnSelectedListener) {

            this.find('.combo_box_select').trigger('change', unExecuteOnSelectedListener);
            return this;
        },

        comboBoxOption: function (option) {

            if (option == undefined) {

                var jSelected = this.find('option:selected');
                return jSelected.data('combo-box-option');
            }


            for (var i = 0, l = this.size(); i < l; i++) {

                var jEq = this.eq(i);

                var name = Lia.p(option, 'name');
                var value = Lia.p(option, 'value');

                jEq.find('option:selected').attr('value', value).text(name);
                jEq.find('.combo_box_text').text(name);
            }

            return this;
        },


        comboBoxOptionList: function (optionList) {

            if (optionList == undefined) {

                var jEq = this.eq(0);
                var jOption = jEq.find('option');

                var optionList = [];
                for (var i = 0, l = jOption.size(); i < l; i++) {
                    optionList.push(jOption.data('combo-box-option'));
                }
                return optionList;
            }


            for (var i = 0, l = this.size(); i < l; i++) {

                var jEq = this.eq(i);

                var selectedValue = jEq.comboBoxVal();

                var jSelect = jEq.find('.combo_box_select');
                jSelect.empty();

                if (optionList != undefined) {

                    for (var i2 = 0, l2 = optionList.length; i2 < l2; i2++) {

                        var option = optionList[i2];

                        var name = option['name'];
                        var value = option['value'];

                        var selected = '';
                        if ((selectedValue != undefined && selectedValue == value) || option['selected'] == true) {
                            selected = 'selected';
                        }

                        var jOption = jQuery('<option value="' + value + '" ' + selected + '>' + name + '</option>');
                        jOption.data('combo-box-option', option);
                        jSelect.append(jOption);
                    }
                }

                var jSelectText = jEq.find('.combo_box_text');
                var name = jSelect.children("option:selected").text();
                jSelectText.text(name);
            }

            return this;
        }

    });
})(jQuery);


var UserBoardPager = jQuery.UserBoardPager = Lia.UserBoardPager = function (options) {
    this.init(options);
};


Lia.UserBoardPager.Theme = {

    White: {

        firstImageUrl: '/res/lia/img/board/white/arr_page_first.png',
        prevImageUrl: '/res/lia/img/board/white/arr_page_prev.png',
        nextImageUrl: '/res/lia/img/board/white/arr_page_next.png',
        lastImageUrl: '/res/lia/img/board/white/arr_page_last.png',

        addClass: 'user_board_pager_white'

    },

    Normal: {

        firstImageUrl: '/res/lia/img/board/normal/arr_page_first.png',
        prevImageUrl: '/res/lia/img/board/normal/arr_page_prev.png',
        nextImageUrl: '/res/lia/img/board/normal/arr_page_next.png',
        lastImageUrl: '/res/lia/img/board/normal/arr_page_last.png',

        addClass: 'user_board_pager_normal'


    }

};

Lia.UserBoardPager.prototype.init = function (options) {

    var jAppendTo = Lia.pd(Lia.p(options, 'appendTo'), Lia.p(options, 'jAppendTo'));

    var theme = Lia.pd(Lia.UserBoardPager.Theme.Normal, options, 'theme');
    var themeClass = Lia.p(theme, 'addClass');

    var j = jQuery('<div class="user_board_pager"></div>');
    jAppendTo.append(j);

    if (String.isNotBlank(themeClass)) {
        j.addClass(themeClass);
    }

    this.firstImageUrl = Lia.pd(Lia.p(theme, 'firstImageUrl'), options, 'firstImageUrl');
    this.prevImageUrl = Lia.pd(Lia.p(theme, 'prevImageUrl'), options, 'prevImageUrl');
    this.nextImageUrl = Lia.pd(Lia.p(theme, 'nextImageUrl'), options, 'nextImageUrl');
    this.lastImageUrl = Lia.pd(Lia.p(theme, 'lastImageUrl'), options, 'lastImageUrl');

    this.move = Lia.pd(function (page, count) {

        Lia.PageManager.cpcpm({
            page: page,
            count: count
        });

    }, options, 'move');

    this.jContent = jQuery('<div class="user_board_pager_content"></div>');
    j.append(this.jContent);
};

Lia.UserBoardPager.prototype.change = function (options) {

    var jPager = $('<ul></ul>');

    this.jContent.empty();
    this.jContent.append(jPager);

    var currentPage = Lia.p(options, 'page');			//현재 페이지 번호
    var totalCount = Lia.p(options, 'totalCount');		//전체 글 개수
    var pagePerCount = Lia.p(options, 'pagePerCount');	//페이지당 보여질 글 개수

    var pageMaxBlockCount = 5;

    var pageLineCount = pagePerCount;
    var pageBlockCount = Math.ceil(totalCount / pageLineCount); //[1][2][3][4][5]
    if (pageBlockCount > pageMaxBlockCount)
        pageBlockCount = pageMaxBlockCount;

    var totalPage = Math.ceil(totalCount / pageLineCount);  //총페이지수

    var totalBlock = Math.ceil(totalPage / pageBlockCount); //총 블록 개수

    var currentBlock = Math.ceil(currentPage / pageBlockCount);	//현재 블록
    var startRow = (currentPage - 1) * pageLineCount; 				//게시판 글 시작 순서

    var firstPage = ((currentBlock - 1) * pageBlockCount) + 1;			//첫번째 페이지번호
    var lastPage = Math.min(totalPage, currentBlock * pageBlockCount); //마지막 페이지 번호
    var prevBlock = currentBlock - 1; // 이전블럭
    var nextBlock = currentBlock + 1; // 다음블럭
    var prevBlockPage = prevBlock * pageBlockCount;
    var nextBlockPage = nextBlock * pageBlockCount - (pageBlockCount - 1);

    var jPageFirstButton = $('<li class="first"><img src="' + this.firstImageUrl + '" /></li>');
    var jPagePrevButton = $('<li class="prev"><img src="' + this.prevImageUrl + '" /></li>');
    var jPageNextButton = $('<li class="next"><img src="' + this.nextImageUrl + '" /></li>');
    var jPageLastButton = $('<li class="last"><img src="' + this.lastImageUrl + '" /></li>');

    jPager.append(jPageFirstButton);
    jPager.append(jPagePrevButton);

    if (isNaN(firstPage)) {
        firstPage = 1;
    }
    if (isNaN(lastPage)) {
        lastPage = 1;
    }

    for (var i = firstPage, l = lastPage; i <= l; i++) {
        var jPageIndex;
        if (i == firstPage) {
            jPageIndex = $('<li class="page_no">' + i + '</li>');
        } else {
            jPageIndex = $('<li class="page_no">' + i + '</li>');
        }

        if (i == currentPage) {
            jPageIndex.addClass('on');
        }
        jPager.append(jPageIndex);

        jPageIndex.on('click', {
            index: i,
            count: pagePerCount,
            currentPage: currentPage,
            userBoardPager: this
        }, function (e) {

            var index = e.data.index;
            var count = e.data.count;
            var currentPage = e.data.currentPage;
            var userBoardPager = e.data.userBoardPager;

            if (index != currentPage) {
                userBoardPager.move(index, count);
            }
        });
    }
    jPager.append(jPageNextButton);
    jPager.append(jPageLastButton);

    //이전블록 이동
    jPageFirstButton.on('click', {
        totalPage: totalPage,
        pagePerCount: pagePerCount,
        userBoardPager: this
    }, function (e) {

        var userBoardPager = e.data.userBoardPager;
        var pagePerCount = e.data.pagePerCount;
        var totalPage = e.data.totalPage;
        if (totalPage <= 1) {
            return;
        }

        userBoardPager.move(1, pagePerCount);
    });

    //다음블록 이동
    jPageLastButton.on('click', {
        totalPage: totalPage,
        pagePerCount: pagePerCount,
        userBoardPager: this
    }, function (e) {

        var userBoardPager = e.data.userBoardPager;
        var pagePerCount = e.data.pagePerCount;
        var totalPage = e.data.totalPage;

        if (totalPage <= 1) {
            return;
        }

        userBoardPager.move(totalPage, pagePerCount);
    });


    //이전블록 이동
    jPagePrevButton.on('click', {
        totalPage: totalPage,
        currentPage: currentPage,
        pagePerCount: pagePerCount,
        userBoardPager: this
    }, function (e) {

        var userBoardPager = e.data.userBoardPager;
        var pagePerCount = e.data.pagePerCount;
        var currentPage = e.data.currentPage;
        var currentPrevBlock = Number(currentPage) - 5 < 1 ? 1 : Number(currentPage) - 5;
        var totalPage = e.data.totalPage;
        if (totalPage <= 1) {
            return;
        }

        userBoardPager.move(currentPrevBlock, pagePerCount);
    });

    //다음블록 이동
    jPageNextButton.on('click', {
        totalPage: totalPage,
        currentPage: currentPage,
        pagePerCount: pagePerCount,
        userBoardPager: this
    }, function (e) {

        var userBoardPager = e.data.userBoardPager;
        var pagePerCount = e.data.pagePerCount;
        var currentPage = e.data.currentPage;
        var currentNextBlock = Number(currentPage) + 5 > totalPage ? totalPage : Number(currentPage) + 5;
        var totalPage = e.data.totalPage;
        if (totalPage <= 1) {
            return;
        }


        userBoardPager.move(currentNextBlock, pagePerCount);
    });

};


var UserBoardList = jQuery.UserBoardList = Lia.UserBoardList = function (options) {
    this.init(options);
};


Lia.UserBoardList.getContentImageUrl = function (item, defaultImageUrl, options) {

    var imageUrl = Lia.p(Lia.convertStrToObj(Lia.p(item, 'image_url')), 'url');
    if (String.isNotBlank(imageUrl)) {
        return imageUrl;
    }

    var videoUrl = Lia.p(Lia.convertStrToObj(Lia.p(item, 'video_url')), 'url');
    if (String.isNotBlank(videoUrl)) {

        var imageUrl = YouTubeHelper.getThumbnailUrl(videoUrl);
        if (String.isNotBlank(imageUrl)) {
            return imageUrl;
        }
    }

    return defaultImageUrl;
};

Lia.UserBoardList.Theme = {


    Pager: {

        White: {

            userBoardPagerTheme: Lia.UserBoardPager.Theme.White

        },

        Normal: {

            userBoardPagerTheme: Lia.UserBoardPager.Theme.Normal

        }

    },

    Common: {

        White: {

            // page count, search option, search text 있는 형태

            searchButtonImageUrl: '',

            searchGroupHTML:

                '<div class="search_group">' +

                '<select class="count_option_select">' +
                '</select>' +

                '<div class="search_group_input_container">' +

                '<select class="search_option_select">' +
                '</select>' +

                '<input class="search_group_input" type="text" />' +

                '<div class="search_button strings" data-lia-string-key="BOARD.SEARCH"></div>' +

                '</div>' +

                '</div>',

            addClass: 'user_board_list_common_white'
        },

        Normal: {

            // 페이지 중앙에 search option, search text 있는 형태

            searchButtonImageUrl: '/res/lia/img/board/normal/btn_search.png',

            searchGroupHTML:
                '<div class="search_group">' +
                '<select class="search_option_select">' +
                '</select>' +
                '<div class="search_group_input_container">' +
                '<input class="search_group_input" type="text" />' +
                '<img class="search_button image_button press"  />' +
                '</div>' +
                '</div>',

            addClass: 'user_board_list_common_normal'

        },

        Full: {

            // 페이지 중앙에 search option, search text 있는 형태

            searchButtonImageUrl: '/res/lia/img/board/full/btn_search.png',

            searchGroupHTML:
                '<div class="search_group">' +
                '<select class="search_option_select">' +
                '</select>' +
                '<div class="search_group_input_container">' +
                '<input class="search_group_input" type="text" />' +
                '<img class="search_button image_button press"  />' +
                '</div>' +
                '</div>',

            addClass: 'user_board_list_common_full'
        }
    },


    Button: {

        White: {

            addClass: 'user_board_list_button_white'

        },

        Normal: {

            addClass: 'user_board_list_button_normal'

        }

    },

    List: {

        White: {

            addClass: 'user_board_list_white'

        },

        Normal: {

            addClass: 'user_board_list_normal'


        }
    },

    Faq: {

        Normal: {

            listHtml: '<div class="faq_item">' +
                '<div class="faq_title">' +
                '<div class="faq_question"></div>' +
                '<span></span>' +
                '</div>' +
                '<div class="faq_answer">' +
                '<div class="faq_answer_body"></div>' +
                '<img class="faq_answer_icon" src="/res/lia/img/board/normal/ico_a.png" />' +
                '</div>',

            addClass: 'user_board_list_faq_normal'

        },

        Category: {

            listHtml: '<div class="faq_item">' +

                '<div class="faq_title">' +
                '<div class="faq_category"></div>' +
                '<div class="faq_question"></div>' +
                '<span></span>' +
                '</div>' +

                '<div class="faq_answer">' +
                '<div class="faq_answer_body"></div>' +
                '</div>',

            addClass: 'user_board_list_faq_category'


        }
    },


    Gallery: {

        Normal: {

            html :
                '<div class="gallery_item">' +
                    '<div class="gallery_thumbnail">' +
                    '</div>' +
                    '<div class="gallery_info">' +
                        '<div class="gallery_category"></div>' +
                        '<div class="gallery_title"></div>' +
                        '<div class="gallery_footer gallery_footer_view_type_list">' +
                            '<div class="gallery_date"></div>' +
                                '<div class="gallery_views">' +
                                    '<span class="gallery_views_title"></span>' +
                                    '<span class="gallery_views_count"></span>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="gallery_footer gallery_footer_view_type_card">' +
                            '<div class="gallery_date"></div>' +
                            '<div class="gallery_views">' +
                                '<span class="gallery_views_title"></span>' +
                                '<span class="gallery_views_count"></span>' +
                            '</div>' +
                    '</div>' +

                '</div>',

            addClass: 'user_board_list_gallery_normal'

        },

    }


};

Lia.UserBoardList.Type = {
    LIST: 1,
    FAQ: 2,
    GALLERY: 3
};

Lia.UserBoardList.ViewType = {
    CARD: 1,
    LIST: 2
};

Lia.UserBoardList.searchOptionList = undefined;
Lia.UserBoardList.setSearchOptionList = function (list) {
    Lia.UserBoardList.searchOptionList = list;
};

Lia.UserBoardList.counthOptionList = [
    {name: '10개씩 보기', value: 10},
    {name: '20개씩 보기', value: 20, selected: true},
    {name: '30개씩 보기', value: 30},
    {name: '40개씩 보기', value: 40},
    {name: '50개씩 보기', value: 50},
    {name: '60개씩 보기', value: 60},
    {name: '70개씩 보기', value: 70},
    {name: '80개씩 보기', value: 80},
    {name: '90개씩 보기', value: 90},
    {name: '100개씩 보기', value: 100}
];
Lia.UserBoardList.setCountOptionList = function (list) {
    Lia.UserBoardList.counthOptionList = list;
};

Lia.UserBoardList.pagerTheme = Lia.UserBoardList.Theme.Pager.Normal;
Lia.UserBoardList.setPagerTheme = function (theme) {
    Lia.UserBoardList.pagerTheme = theme;
};

Lia.UserBoardList.getPagerTheme = function () {
    return Lia.UserBoardList.pagerTheme;
};

Lia.UserBoardList.commonTheme = Lia.UserBoardList.Theme.Common.Normal;
Lia.UserBoardList.setCommonTheme = function (theme) {
    Lia.UserBoardList.commonTheme = theme;
};


Lia.UserBoardList.buttonTheme = Lia.UserBoardList.Theme.Button.Normal;
Lia.UserBoardList.setButtonTheme = function (theme) {
    Lia.UserBoardList.buttonTheme = theme;
};


Lia.UserBoardList.listTheme = Lia.UserBoardList.Theme.List.Normal;
Lia.UserBoardList.setListTheme = function (theme) {
    Lia.UserBoardList.listTheme = theme;
};

Lia.UserBoardList.faqTheme = Lia.UserBoardList.Theme.Faq.Normal;
Lia.UserBoardList.setFaqTheme = function (theme) {
    Lia.UserBoardList.faqTheme = theme;
};

Lia.UserBoardList.galleryTheme = Lia.UserBoardList.Theme.Gallery.Normal;
Lia.UserBoardList.setGalleryTheme = function (theme) {
    Lia.UserBoardList.galleryTheme = theme;
};

Lia.UserBoardList.Field = {};
Lia.UserBoardList.Field.NO = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var alwaysOnTopClass = '';

        var rowNumber = boardContent['row_number'];

        if (boardContent['is_always_on_top'] == 1) {
            alwaysOnTopClass = 'always_on_top';
            rowNumber = '<img src="/res/lia/img/board/normal/ico_notice.png" style="vertical-align: middle;width:20px;" >';
        }

        if (String.isNotBlank(alwaysOnTopClass)) {
            jRow.addClass(alwaysOnTopClass);
        }

        jRow.append('<td class="no">' + rowNumber + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td width="100px" class="mobile_hide">' +
            Lia.Strings.getString(Lia.Strings.BOARD.NO)
            + '</td>');
    }
};

Lia.UserBoardList.Field.Category = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var categoryName = Lia.pcd('-', boardContent, 'category', 'name');
        jRow.append('<td class="category">' + categoryName + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="category_col" width="100px">' + Lia.Strings.getString(Lia.Strings.BOARD.CATEGORY) + '</td>');
    }
};

Lia.UserBoardList.Field.Title = {

    attachToBoardList: function (jTable, jRow, boardContent) {
        var privateImage = (Lia.p(boardContent, 'is_private') == 1) ? '<img src="/res/lia/img/board/normal/ico_lock.png" style="width:14px;margin-right:10px;vertical-align:middle;" />' : '';

        var jTd = $('<td class="title"></td>');
        jRow.append(jTd);

        if (String.isNotBlank(privateImage)) {
            jTd.append(privateImage);
        }

        var title = Lia.p(boardContent, 'title');
        if (String.isNotBlank(title)) {

            var jTitle = $('<span></span>');
            jTitle.text(title);
            jTd.append(jTitle);
        }
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="title">' +
            Lia.Strings.getString(Lia.Strings.BOARD.TITLE)
            + '</td>');
    }
};

Lia.UserBoardList.Field.Attachment = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var fileImage = '-';
        var fileImageClass = 'none';
        if (boardContent['has_attachment'] == 1 || boardContent['attachment_count'] > 0) {
            fileImage = '<img src="/res/lia/img/board/normal/ico_file.png" style="vertical-align: middle;width:12px;" >';
            fileImageClass = '';
        }

        jRow.find('.title').addClass('with_attachment');

        jRow.append('<td class="attachment ' + fileImageClass + '">' + fileImage + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="attachment_col" width="100px">' + Lia.Strings.getString(Lia.Strings.BOARD.ATTACHMENT) + '</td>');
    }
};


Lia.UserBoardList.Field.RegisteredByUser = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var registeredByUserName = Lia.p(boardContent, 'registered_by_user_name');
        if (String.isBlank(registeredByUserName)) {
            registeredByUserName = Lia.p(boardContent, 'owner_name');
        }

        jRow.append('<td class="user_name">' + registeredByUserName + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="mobile_hide" width="120px">' +
            Lia.Strings.getString(Lia.Strings.BOARD.AUTHOR)
            + '</td>');
    }
};


Lia.UserBoardList.Field.RegisteredDate = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var registeredDate = Lia.p(boardContent, 'registered_date');
        if (String.isNotBlank(registeredDate)) {
            registeredDate = registeredDate.substr(0, 10);
        }

        jRow.append('<td class="registered_date">' + registeredDate + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="reg_date_col" class="mobile_hide" width="120px">' +
            Lia.Strings.getString(Lia.Strings.BOARD.REGISTERED_DATE)
            + '</td>');
    }
};


Lia.UserBoardList.Field.LastModifiedDate = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var lastModifiedDate = Lia.p(boardContent, 'last_modified_date');
        if (String.isNotBlank(lastModifiedDate)) {
            lastModifiedDate = lastModifiedDate.substr(0, 10);
        }

        jRow.append('<td class="last_modified_date">' + lastModifiedDate + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="mobile_hide" width="120px">' +
            Lia.Strings.getString(Lia.Strings.BOARD.LAST_MODIFIED_DATE)
            + '</td>');
    }
};


Lia.UserBoardList.Field.HitCount = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var hitCount = Lia.pd(0, boardContent, 'view_count');

        jRow.append('<td class="hit_count">' + hitCount + '</td>');
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="hot_count_col" class="mobile_hide" width="90px">' +
            Lia.Strings.getString(Lia.Strings.BOARD.VIEWS)
            + '</td>');
    }
};


Lia.UserBoardList.Field.Status = {

    attachToBoardList: function (jTable, jRow, boardContent) {

        var statusColumn = '';

        var statusName = Lia.pd(0, boardContent, 'comment_count') > 0 ?
            Lia.Strings.getString(Lia.Strings.BOARD.COMPLETED)
            : Lia.Strings.getString(Lia.Strings.BOARD.WAITING)
        ;
        var statusClass = Lia.pd(0, boardContent, 'comment_count') > 0 ? 'status_completed' : '';

        statusColumn = '<td class="status_cell"><div class="status ' + statusClass + '">' + statusName + '</div></td>';
        jRow.append(statusColumn);
    },

    attachHeaderToBoardList: function (jTable, jRow) {
        jRow.append('<td class="status_col" width="100px">' +
            Lia.Strings.getString(Lia.Strings.BOARD.STATUS) +
            '</td>');
    }
};

Lia.UserBoardList.prototype.init = function (options) {

    var jAppendTo = Lia.pd(Lia.p(options, 'appendTo'), Lia.p(options, 'jAppendTo'));
    var addClass = Lia.p(options, 'addClass');

    var pagerTheme = Lia.pd(Lia.UserBoardList.pagerTheme, options, 'pagerTheme');
    var commonTheme = Lia.pd(Lia.UserBoardList.commonTheme, options, 'commonTheme');
    var buttonTheme = Lia.pd(Lia.UserBoardList.buttonTheme, options, 'buttonTheme');
    var listTheme = this.listTheme = Lia.pd(Lia.UserBoardList.listTheme, options, 'listTheme');
    var faqTheme = this.faqTheme = Lia.pd(Lia.UserBoardList.faqTheme, options, 'faqTheme');
    var galleryTheme = this.galleryTheme = Lia.pd(Lia.UserBoardList.galleryTheme, options, 'galleryTheme');
    var defaultThumbnailUrl = this.defaultThumbnailUrl = Lia.p(options, 'defaultThumbnailUrl');

    this.typeCode = Lia.pd(Lia.UserBoardList.Type.LIST, options, 'typeCode');

    var commonClass = Lia.p(commonTheme, 'addClass');
    var buttonCLass = Lia.p(buttonTheme, 'addClass');
    var listClass = Lia.p(listTheme, 'addClass');
    var faqClass = Lia.p(faqTheme, 'addClass');
    var galleryClass = Lia.p(galleryTheme, 'addClass');

    var j = this.j = jQuery('<div class="user_board_list"></div>');

    if (addClass != undefined) {
        j.addClass(addClass);
    }

    jAppendTo.append(j);

    if (String.isNotBlank(commonClass)) {
        j.addClass(commonClass);
    }
    if (String.isNotBlank(buttonCLass)) {
        j.addClass(buttonCLass);
    }

    if (this.typeCode == Lia.UserBoardList.Type.LIST) {

        if (String.isNotBlank(listClass)) {
            j.addClass(listClass);
        }

    } else if (this.typeCode == Lia.UserBoardList.Type.FAQ) {

        if (String.isNotBlank(faqClass)) {
            j.addClass(faqClass);
        }

    } else if (this.typeCode == Lia.UserBoardList.Type.GALLERY) {

        if (String.isNotBlank(galleryClass)) {
            j.addClass(galleryClass);
        }
    }

    this.search = Lia.pd(function (code, text) {

        Lia.PageManager.cpcpm({
            page: 1,
            search_by_code: code,
            search_by_text: text
        });

    }, options, 'search');

    this.count = Lia.pd(function (count) {

        Lia.PageManager.cpcpm({
            page: 1,
            count: count
        });

    }, options, 'count');

    this.viewType = Lia.pd(function (viewTypeCode) {

        Lia.PageManager.cpcpm({
            view_type_code : viewTypeCode
        });

    }, options, 'viewType');

    this.totalCountDisabled = Lia.pd(false, options, 'totalCountDisabled');
    this.pagerDisabled = Lia.pd(false, options, 'pagerDisabled');
    this.viewTypeButtonDisabled = Lia.pd(false, options, 'viewTypeButtonDisabled');

    var searchButtonImageUrl = Lia.pd(Lia.p(commonTheme, 'searchButtonImageUrl'), options, 'searchButtonImageUrl');
    var searchGroupHTML = Lia.pd(Lia.p(commonTheme, 'searchGroupHTML'), options, 'searchGroupHTML');
    this.searchGroupDisabled = Lia.pd(false, options, 'searchGroupDisabled');

    var searchOptionList = Lia.pd(Lia.UserBoardList.searchOptionList, options, 'searchOptionList');
    var countOptionList = Lia.pd(Lia.UserBoardList.counthOptionList, options, 'countOptionList');

    if (String.isNotBlank(searchGroupHTML) && !this.searchGroupDisabled) {
        j.append(searchGroupHTML);

        if (String.isNotBlank(searchButtonImageUrl)) {
            j.find('.search_button').attr('src', searchButtonImageUrl).initImageButton();
        }

        var jSearchOptionSelect = j.find('.search_option_select');
        if (Array.isNotEmpty(searchOptionList)) {

            for (var i = 0, l = searchOptionList.length; i < l; i++) {

                var item = searchOptionList[i];

                var selected = Lia.p(item, 'selected') ? 'selected' : '';

                jSearchOptionSelect.append('<option value="' + item['value'] + '" ' + selected + '>' +
                    item['name'] +
                    '</option>');
            }
        }

        var jCountOptionSelect = j.find('.count_option_select');
        if (Array.isNotEmpty(countOptionList)) {

            for (var i = 0, l = countOptionList.length; i < l; i++) {

                var item = countOptionList[i];

                var selected = Lia.p(item, 'selected') ? 'selected' : '';

                jCountOptionSelect.append('<option value="' + item['value'] + '" ' + selected + '>' +
                    item['name'] +
                    '</option>');
            }

            jCountOptionSelect.on('change', {
                userBoardList: this
            }, function (e) {

                var userBoardList = e.data.userBoardList;
                userBoardList.count(jQuery(this).val());
            });

        }

        var jSearchGroupInput = j.find('.search_group_input');
        jSearchGroupInput.on('keypress', {
            j: j,
            userBoardList: this,
        }, function (e) {

            if (e.which == Lia.KeyCode.ENTER) {

                var j = e.data.j;
                var userBoardList = e.data.userBoardList;

                var code = j.find('.search_option_select').val();
                var text = j.find('.search_group_input').val();

                userBoardList.search(code, text);
            }
        });
        jSearchGroupInput.attr({
            'placeholder': Lia.Strings.getString(Lia.Strings.BOARD.SEARCH_PLACEHOLDER)
        });

        j.find('.search_button').on('click', {
            userBoardList: this,
            j: j
        }, function (e) {

            var j = e.data.j;
            var userBoardList = e.data.userBoardList;

            var code = j.find('.search_option_select').val();
            var text = j.find('.search_group_input').val();

            userBoardList.search(code, text);
        });
    }

    this.jContent = jQuery('<div class="user_board_list_content"></div>');
    this.j.append(this.jContent);

    this.userBoardPagerTheme = Lia.pd(Lia.p(pagerTheme, 'userBoardPagerTheme'), options, 'userBoardPagerTheme');
    this.fieldList = Lia.p(options, 'fieldList');

    this.categoryListEnabled = Lia.pd(false, options, 'categoryListEnabled');

    if (this.categoryListEnabled) {

        this.allCategoryEnabled = Lia.p(options, 'allCategoryEnabled');

        this.categoryList = Lia.p(options, 'categoryList');

        if (Array.isNotEmpty(this.categoryList)) {

            this.category = Lia.pd(function (id) {

                Lia.PageManager.cpcpm({
                    page: 1,
                    category_id: id
                });

            }, options, 'category');

            this.jCategoryList = jQuery('<div class="category_list"></div>');
            this.jContent.append(this.jCategoryList);

            if (this.allCategoryEnabled) {

                var jCategoryItem = jQuery('<div class="category_item">'
                    + Lia.Strings.getString(Lia.Strings.BOARD.ALL) + '</div>');

                jCategoryItem.dataAttr('lia-board-category-id', '');
                jCategoryItem.on('click', {
                    categoryId: '',
                    userBoardList: this
                }, function (e) {
                    e.data.userBoardList.category(e.data.categoryId);
                });
                this.jCategoryList.append(jCategoryItem);
            }

            for (var i = 0, l = this.categoryList.length; i < l; i++) {

                var categoryItem = this.categoryList[i];

                if (this.jCategoryList.children().length > 0) {
                    this.jCategoryList.append(jQuery('<div class="category_item_div">|</div>'));
                }

                var jCategoryItem = jQuery('<div class="category_item">' + Lia.p(categoryItem, 'name') + '</div>');

                var categoryId = Lia.p(categoryItem, 'id');
                jCategoryItem.dataAttr('lia-board-category-id', categoryId);
                jCategoryItem.on('click', {
                    categoryId: categoryId,
                    userBoardList: this
                }, function (e) {
                    e.data.userBoardList.category(e.data.categoryId);
                });

                this.jCategoryList.append(jCategoryItem);
            }

        }


    }

    if (this.typeCode == Lia.UserBoardList.Type.LIST) {

        if (!this.totalCountDisabled) {

            if (Lia.Strings.getLocale() == Lia.Strings.Locale.KO) {
                this.jContent.append('<div class="total_count">' + '총 <span class="total_count_text">-</span>건</div>');
            } else {
                this.jContent.append('<div class="total_count"><span class="total_count_text">-</span> Search results</div>');
            }
        }

        this.jContent.append('<table class="normal_list">' +
            '<thead>' +
            '<tr>' +
            '</tr>' +
            '</thead>' +
            '<tbody>' +
            '</tbody>' +
            '</table>');

        var fieldList = this.fieldList;
        if (Array.isNotEmpty(fieldList)) {

            var jTable = this.jContent.find('.normal_list');
            var jHeaderRow = this.jContent.find('.normal_list thead tr');

            for (var i = 0, l = fieldList.length; i < l; i++) {

                var item = fieldList[i];
                if (item != undefined) {
                    item.attachHeaderToBoardList(jTable, jHeaderRow);
                }
            }
        }

    } else if (this.typeCode == Lia.UserBoardList.Type.FAQ) {

        this.jContent.append('<div class="faq_list"></div>');

    } else if (this.typeCode == Lia.UserBoardList.Type.GALLERY) {

        var jSearchSection = jQuery('<section class="search_section"></section>');
        this.jContent.append(jSearchSection);

        var jGalleryList = jQuery('<div class="gallery_list"></div>');
        this.jContent.append(jGalleryList);

        if (!this.totalCountDisabled) {

            if (Lia.Strings.getLocale() == Lia.Strings.Locale.KO) {
                jSearchSection.append('<div class="total_count">' + '총 <span class="total_count_text">-</span>건</div>');
            } else {
                jSearchSection.append('<div class="total_count"><span class="total_count_text">-</span> Search results</div>');
            }
        }

        if ( !this.viewTypeButtonDisabled ) {

            var jViewTypeButtonList = jQuery('<section class="view_type_button_list">' +
                    '<div class="view_button view_type_card_button">' +
                        '<img class="view_button_img_normal" src="/res/lia/img/board/gallery/ico_cardview.png" alt="Card View" />' +
                        '<img class="view_button_img_pressed" src="/res/lia/img/board/gallery/ico_cardview_pressed.png" alt="Card View" />' +
                    '</div>' +
                    '<div class="view_button view_type_list_button">' +
                        '<img class="view_button_img_normal" src="/res/lia/img/board/gallery/ico_listview.png" alt="List View" />' +
                        '<img class="view_button_img_pressed" src="/res/lia/img/board/gallery/ico_listview_pressed.png" alt="List View" />' +
                    '</div>' +
                '</section>');

            jSearchSection.append(jViewTypeButtonList);

            jViewTypeButtonList.find('.view_button').on('click', {
                userBoardList : this
            }, function(e) {

                var userBoardList = e.data.userBoardList;

                var viewTypeCode = undefined;

                var jThis = jQuery(this);
                if ( jThis.hasClass('view_type_list_button') ) {
                    viewTypeCode = Lia.UserBoardList.ViewType.LIST;
                } else {
                    viewTypeCode = Lia.UserBoardList.ViewType.CARD;
                }

                userBoardList.viewType(viewTypeCode);
            });
        }
    }

    this.jContent.append('<div class="no_content" style="">' + Lia.Strings.getString(Lia.Strings.BOARD.NO_CONTENT) + '</div>');

    if (!this.pagerDisabled) {
        this.jContent.append('<div class="user_board_pager_container"></div>');
    }

    var allowWrite = Lia.p(options, 'allowWrite');
    this.write = Lia.pd(function () {
        Lia.PageManager.cpm(['page_board_write'], {});
    }, options, 'write');

    this.detail = Lia.pd(function (item) {

        if (item['is_readable'] != 1) {

            if (!Server.loggedIn) {

                ProjectUrlHelper.needLogin(true);

            } else {

                PopupManager.alert(
                    Lia.Strings.getString(Lia.Strings.POPUP.TITLE.INFO),
                    Lia.Strings.getString(Lia.Strings.POPUP.MESSAGE.NOT_ALLOWED_TO_READ)
                );
            }
            return;
        }

        Lia.PageManager.cpm(['page_board_detail'], {
            board_content_id: Lia.p(item, 'id')
        });

    }, options, 'detail');

    this.message = Lia.pd(function (message) {
        PopupManager.alert(
            Lia.Strings.getString(Lia.Strings.POPUP.TITLE.INFO),
            message);
    }, options, 'message');

    if (allowWrite) {

        this.jContent.append('<div class="button_list"><div class="write_button">' +
            Lia.Strings.getString(Lia.Strings.BOARD.ADD)
            + '</div>');
        this.jContent.find('.write_button').on('click', {
            userBoardList: this
        }, function (e) {

            var userBoardList = e.data.userBoardList;
            userBoardList.write();

        });
    }

    Lia.Strings.applyStrings(this.j);
};

Lia.UserBoardList.prototype.setSearchOption = function (code, text) {

    if (code == undefined) {
        code = this.j.find('.search_option_select :selected').attr('value');
    }

    this.j.find('.search_option_select').val(code);
    this.j.find('.search_group_input').val(text);
};

Lia.UserBoardList.prototype.getSearchOptionCode = function () {
    return this.j.find('.search_option_select :selected').attr('value');
};

Lia.UserBoardList.prototype.getSearchOptionText = function () {
    return this.j.find('.search_group_input').val();
};


Lia.UserBoardList.prototype.setCountOption = function (count) {

    if (count == undefined) {
        count = this.j.find('.count_option_select :selected').attr('value');
    }

    this.j.find('.count_option_select').val(count);
};

Lia.UserBoardList.prototype.getCountOption = function () {
    return this.j.find('.count_option_select :selected').attr('value');
};


Lia.UserBoardList.prototype.setCategoryId = function (categoryId) {

    if (this.categoryListEnabled == false) {
        return;
    }

    if (this.jCategoryList == undefined) {
        return;
    }

    categoryId = Lia.pcd('', categoryId);

    var jCategoryItemList = this.jCategoryList.find('.category_item');

    for (var i = 0, l = jCategoryItemList.length; i < l; i++) {

        var jItem = jCategoryItemList.eq(i);
        if (Lia.pcd('', jItem.dataAttr('lia-board-category-id')) == categoryId) {
            jItem.addClass('selected');
        } else {
            jItem.removeClass('selected');
        }
    }
};

Lia.UserBoardList.prototype.getCategoryId = function () {

    if (this.categoryListEnabled == false) {
        return undefined;
    }

    if (this.jCategoryList == undefined) {
        return undefined;
    }


    var id = this.jCategoryList.find('.category_item.selected').dataAttr('lia-board-category-id');
    return Lia.pcd(undefined, id);
};

Lia.UserBoardList.prototype.change = function (options) {

    var totalCount = Lia.pd(0, options, 'totalCount');
    var page = Lia.p(options, 'page');
    var count = Lia.p(options, 'count');
    var onLoaded = Lia.p(options, 'onLoaded');

    if (this.typeCode == Lia.UserBoardList.Type.LIST) {

        this.jContent.find('.normal_list tbody').empty();

    } else if (this.typeCode == Lia.UserBoardList.Type.FAQ) {

        this.jContent.find('.faq_list').empty();

    } else if (this.typeCode == Lia.UserBoardList.Type.GALLERY) {

        this.viewTypeCode = Lia.pd(Lia.UserBoardList.ViewType.CARD, options, 'viewTypeCode');

        var jGalleryList = this.jContent.find('.gallery_list').empty();
        jGalleryList.removeClass('view_type_card view_type_list');

        this.jContent.find('.view_button').removeClass('view_button_pressed');

        if ( this.viewTypeCode == Lia.UserBoardList.ViewType.CARD ) {
            this.jContent.find('.view_type_card_button').addClass('view_button_pressed');

            jGalleryList.addClass('view_type_card');
        } else {
            this.jContent.find('.view_type_list_button').addClass('view_button_pressed');

            jGalleryList.addClass('view_type_list');
        }
    }

    if (!this.pagerDisabled) {
        this.jContent.find('.user_board_pager_container').empty();
    }

    this.jContent.find('.total_count_text').text(totalCount);

    var list = Lia.p(options, 'list');
    if (Array.isEmpty(list)) {
        this.jContent.find('.no_content').show();
    } else {
        this.jContent.find('.no_content').hide();

        for (var i = 0, l = list.length; i < l; i++) {

            var item = Lia.p(list, i);

            if (this.typeCode == Lia.UserBoardList.Type.LIST) {

                var fieldList = this.fieldList;
                if (Array.isNotEmpty(fieldList)) {

                    var jTable = this.jContent.find('.normal_list');
                    var jBody = this.jContent.find('.normal_list tbody');

                    var jTr = jQuery('<tr></tr>');
                    jBody.append(jTr);

                    for (var i2 = 0, l2 = fieldList.length; i2 < l2; i2++) {

                        var field = fieldList[i2];
                        if (field != undefined) {
                            field.attachToBoardList(jTable, jTr, item);
                        }
                    }

                    if (this.detail != false) {
                        jTr.on('click', {
                            item: item,
                            userBoardList: this
                        }, function (e) {

                            var userBoardList = e.data.userBoardList;
                            var item = e.data.item;
                            userBoardList.detail(item);
                        });
                    }
                }

            } else if (this.typeCode == Lia.UserBoardList.Type.FAQ) {

                var jFaqList = this.jContent.find('.faq_list');

                var title = item['title'];
                var body = Lia.p(item, 'body');
                var categoryName = Lia.pcd('-', item, 'category', 'name');

                var jItem = jQuery(this.faqTheme.listHtml);

                jItem.find('.faq_category').html(categoryName);
                jItem.find('.faq_question').html(title);
                jItem.find('.faq_answer_body').html(body);

                jItem.find('.faq_title').on('click', function () {
                    $(this).parent().toggleClass('on');
                    $(this).next().slideToggle();
                });

                jFaqList.append(jItem);

            } else if (this.typeCode == Lia.UserBoardList.Type.GALLERY) {

                var jGalleryList = this.jContent.find('.gallery_list');

                var title = item['title'];
                var body = Lia.p(item, 'body');
                var viewCount = Lia.p(item, 'view_count');
                var registeredDate = Lia.p(item, 'registered_date');
                var categoryName = Lia.pcd('-', item, 'category', 'name');


                var thumbnailUrl = Lia.UserBoardList.getContentImageUrl(item, this.defaultThumbnailUrl);

                var jItem = jQuery(this.galleryTheme.html);

                jItem.addClass('gallery_line_' + (i % 4));
                jGalleryList.append(jItem);

                if (String.isNotBlank(thumbnailUrl)) {
                    jItem.find('.gallery_thumbnail').css({
                        'background-image': "url('" + PathHelper.getFileUrl(thumbnailUrl) + "')"
                    })
                }

                jItem.find('.gallery_category').html(Lia.pcd('-', categoryName));
                jItem.find('.gallery_title').html(Lia.pcd('-', title));

                if (String.isNotBlank(registeredDate)) {
                    jItem.find('.gallery_date').html(Lia.pcd('-', registeredDate.substr(0, 10)));
                }

                jItem.find('.gallery_views_title').html(Lia.pcd('-', Lia.Strings.getString(Lia.Strings.BOARD.VIEWS)));
                jItem.find('.gallery_views_count').html(Lia.pcd('-', viewCount));

                if (this.detail != false) {
                    jItem.on('click', {
                        item: item,
                        userBoardList: this
                    }, function (e) {

                        var userBoardList = e.data.userBoardList;
                        var item = e.data.item;
                        userBoardList.detail(item);
                    });
                }
            }
        }
    }

    if (String.isNotBlank(page) && String.isNotBlank(count)) {

        if (!this.pagerDisabled) {

            var pager = new Lia.UserBoardPager({
                appendTo: this.jContent.find('.user_board_pager_container'),
                theme: this.userBoardPagerTheme
            });

            pager.change({
                page: page,
                totalCount: totalCount,
                pagePerCount: count
            });
        }
    }

    if (onLoaded != undefined) {
        onLoaded();
    }
};


//MenuPage 모듈로 메뉴 관련코드 쉽게 사용
var MenuPage = jQuery.MenuPage = Lia.MenuPage = function (options) {
    this.init(options);
};

Lia.MenuPage.ApiUrl = {
    ADD_MENU: '/api/menu/addMenu',
    DELETE_MENU: '/api/menu/deleteMenu',
    DELETE_MENU_PERMANENTLY: '/api/menu/deleteMenuPermanently',
    EDIT_MENU: '/api/menu/editMenu',
    GET_MENU: '/api/menu/getMenu',
    GET_MENU_LIST: '/api/menu/getMenuList',
    RECOVER_MENU: '/api/menu/recoverMenu',
    SET_MENU_AVAILABILITY: '/api/menu/setMenuAvailability',
    SET_MENU_DISPLAY_ORDER: '/api/menu/setMenuDisplayOrder'
};

// Lia.MenuPage.ApiUrl = {
//     ADD_MENU: '/api/website/addMenu',
//     DELETE_MENU: '/api/website/deleteMenu',
//     DELETE_MENU_PERMANENTLY: '/api/website/deleteMenuPermanently',
//     RECOVER_MENU: '/api/website/recoverMenu',
//     EDIT_MENU: '/api/website/editMenu',
//     GET_MENU: '/api/website/getMenu',
//     GET_MENU_LIST: '/api/website/getMenuList',
//     SET_MENU_AVAILABILITY: '/api/website/setMenuAvailability',
//     SET_MENU_DISPLAY_ORDER: '/api/website/setMenuDisplayOrder',
// };

Lia.MenuPage.PopupUrl = {
    MENU_MANAGER: 'cms/popup/menu_manager',
    MENU_USER: 'cms/popup/menu_user'
};

Lia.MenuPage.onPreInit = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPreInit = function (func) {
    Lia.MenuPage.onPreInit = func;
};


Lia.MenuPage.onPostInit = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPostInit = function (func) {
    Lia.MenuPage.onPostInit = func;
};


Lia.MenuPage.onPreRelease = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPreRelease = function (func) {
    Lia.MenuPage.onPreRelease = func;
};


Lia.MenuPage.onPostRelease = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPostRelease = function (func) {
    Lia.MenuPage.onPostRelease = func;
};


Lia.MenuPage.onPreChange = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPreChange = function (func) {
    Lia.MenuPage.onPreChange = func;
};


Lia.MenuPage.onPostChange = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {
};

Lia.MenuPage.setOnPostChange = function (func) {
    Lia.MenuPage.onPostChange = func;
};


Lia.MenuPage.DEFAULT_HTML = '<div></div>';
Lia.MenuPage.DEFAULT_SCRIPT =
    '(function () {\n' +
    '    return {\n' +
    '        onInit: function ( jPage, jPageContainer, i, parameterMap, beforeParameterMap ) {\n' +
    '        },\n' +
    '        onRelease: function ( jPage, jPageContainer, i, parameterMap, beforeParameterMap ) {\n' +
    '        }\n' +
    '    };\n' +
    '})();\n';

Lia.MenuPage.requester = undefined;
Lia.MenuPage.setRequester = function (requester) {
    Lia.MenuPage.requester = requester;
};

Lia.MenuPage.menuHandler = function (menu, result, request) {

    var menuPage = this;

    menuPage.typeCode = undefined;
    menuPage.contentData = undefined;

    menuPage.boardId = undefined;
    menuPage.boardTypeCode = undefined;
    menuPage.listPermissionLevel = undefined;

    menuPage.title = undefined;
    menuPage.js = undefined;

    var content = menuPage.content = Lia.p(menu, 'content');
    var typeCode = Lia.p(content, 'type_code');
    menuPage.typeCode = typeCode;

    var contentData = menuPage.contentData = Lia.p(content, 'data');
    if (typeCode == MenuContentType.BOARD) {

        menuPage.boardId = menuPage.boardIdList = contentData['id'];
        menuPage.boardTypeCode = contentData['type_code'];
        menuPage.listPermissionLevel = contentData['list_permission_level'];

    } else if (typeCode == MenuContentType.HTML_SCRIPT) {

        var title = Lia.p(menu, 'title');

        var html = Lia.p(contentData, 'html');
        var script = Lia.p(contentData, 'script');

        var js = new Lia.Page();
        if (String.isNotBlank(script)) {

            if (Lia.debugMode) {
                js.extend(eval(script));
            } else {

                try {
                    js.extend(eval(script));
                } catch (e) {
                }
            }
        }

        menuPage.title = title;
        menuPage.js = js;

        if (String.isNotBlank(html)) {
            menuPage.html = html;
        }
    }

    if (result != undefined) {
        result.call(menuPage);
    }
};


Lia.MenuPage.setMenuHandler = function (menuHandler) {
    Lia.MenuPage.menuHandler = menuHandler;
};

Lia.MenuPage.filePathFormatHandler = function (path) {
    return path;
};
Lia.MenuPage.cssFilePathFormatHandler = function (path) {
    return '/res/' + path + '.css';
};
Lia.MenuPage.htmlFilePathFormatHandler = function (path) {
    return '/res/' + path + '.html';
};
Lia.MenuPage.jsFilePathFormatHandler = function (path) {
    return '/res/' + path + '.js';
};


Lia.MenuPage.prototype.init = function (options) {

    var page = this;

    page.id = Lia.p(options, 'id');

    page.requester = Lia.pd(Lia.MenuPage.requester, options, 'requester');

    if (page.requester == undefined) {
        page.requester = new Lia.Requester();
    }

    page.menuHandler = Lia.pd(Lia.MenuPage.menuHandler, options, 'menuHandler');

    page.onPreInit = Lia.pd(Lia.MenuPage.onPreInit, options, 'onPreInit');
    page.onPostInit = Lia.pd(Lia.MenuPage.onPostInit, options, 'onPreRelease');

    page.onPreRelease = Lia.pd(Lia.MenuPage.onPreRelease, options, 'onPostInit');
    page.onPostRelease = Lia.pd(Lia.MenuPage.onPostRelease, options, 'onPostRelease');

    page.onPreChange = Lia.pd(Lia.MenuPage.onPreRelease, options, 'onPreChange');
    page.onPostChange = Lia.pd(Lia.MenuPage.onPostRelease, options, 'onPostChange');

    page.filePathFormatHandler = Lia.pd(Lia.MenuPage.filePathFormatHandler, options, 'filePathFormatHandler');
    page.jsFilePathFormatHandler = Lia.pd(Lia.MenuPage.jsFilePathFormatHandler, options, 'jsFilePathFormatHandler');
    page.htmlFilePathFormatHandler = Lia.pd(Lia.MenuPage.htmlFilePathFormatHandler, options, 'htmlFilePathFormatHandler');
    page.cssFilePathFormatHandler = Lia.pd(Lia.MenuPage.cssFilePathFormatHandler, options, 'cssFilePathFormatHandler');
};


// 공통
// menu
// content
// contentData

// menuPage.typeCode : ContentType.Board
//    boardId, boardIdList : 게시판 아이디
//    boardTypeCode : 게시판 타입

// menuPage.typeCode : 나머지
//    title : 제목
//    js : 스크립트
//    html : html 내용
//
// ref_page_url 있을 시
//    page.getMenuPage()


Lia.MenuPage.prototype.getMenu = function () {
    return this.menu;
};
Lia.MenuPage.prototype.getTypeCode = function () {
    return this.typeCode;
};
Lia.MenuPage.prototype.getPage = function () {
    return this.page;
};

Lia.MenuPage.prototype.load = function (request, result) {

    var menuPage = this;

    var id = Lia.p(request, 'id');
    if (String.isNotBlank(id)) {
        menuPage.id = id;
    }

    menuPage.menu = undefined;
    menuPage.html = undefined;
    menuPage.page = undefined;

    menuPage.requester.awb(Lia.MenuPage.ApiUrl.GET_MENU, {
        id: menuPage.id
    }, function (status, data) {

        var refMenuId = Lia.p(data, 'body', 'content', 'data', 'ref_menu_id');

        if (String.isNotBlank(refMenuId)) {

            menuPage.requester.awb(Lia.MenuPage.ApiUrl.GET_MENU, {
                id: refMenuId
            }, function (status, data) {

                menuPage.menu = Lia.p(data, 'body');

            });

        } else {

            menuPage.menu = Lia.p(data, 'body');
        }

    });

    menuPage.requester.func(function () {

        menuPage.requester.func(function () {

            var refPageUrl = Lia.p(menuPage.menu, 'content', 'data', 'ref_page_url');

            if (String.isNotBlank(refPageUrl)) {

                // 현재 경로의 js, html, css 로딩

                var path = menuPage.filePathFormatHandler(refPageUrl);

                var jsUrl = menuPage.jsFilePathFormatHandler(path);
                var htmlUrl = menuPage.htmlFilePathFormatHandler(path);
                var cssUrl = menuPage.cssFilePathFormatHandler(path);

                menuPage.page = new Lia.Page();

                menuPage.page.extend({
                    'menuPage': menuPage,
                    'getMenuPage': function () {
                        return this.menuPage;
                    }
                });

                menuPage.requester.request({
                    url: jsUrl,
                    onResponse: function (status, data, requester) {

                        if (String.isNotBlank(data)) {
                            menuPage.page.extend(eval(data));
                        }
                    },
                    method: 'get',
                    dataType: 'text'
                });

                menuPage.requester.func(function () {

                    var htmlLoading = menuPage.page.checkHtmlLoading();
                    var cssLoading = menuPage.page.checkCssLoading();

                    if (htmlLoading) {

                        menuPage.requester.request({
                            url: htmlUrl,
                            onResponse: function (status, data, requester) {
                                menuPage.page.rawHtml = data;
                            },
                            method: 'get',
                            dataType: 'text'
                        });
                    }

                    if (cssLoading) {

                        menuPage.requester.request({
                            url: cssUrl,
                            onResponse: function (status, data, requester) {

                                menuPage.page.rawCss = data;
                            },
                            method: 'get',
                            dataType: 'text'
                        });
                    }


                    menuPage.requester.func(function () {

                        var text = '<div>';
                        var css = menuPage.page.rawCss;
                        if (css != undefined) {
                            text += '<style type="text/css">' + css + '</style>';
                        }

                        var html = menuPage.page.rawHtml;
                        if (html != undefined) {
                            text += html;
                        }

                        text += '</div>';
                        menuPage.page.html = text;
                    });
                });

            }

            menuPage.requester.func(function () {

                menuPage.requester.func(function () {
                    menuPage.menuHandler(menuPage.menu, result, request);
                });
            });

        });

    });

};


Lia.MenuPage.prototype.onInit = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {

    var menuPage = this;

    var page = menuPage.page;
    var js = menuPage.js;

    if (menuPage.onPreInit != undefined) {
        menuPage.onPreInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }
    if (page != undefined) {

        page.set({
            jPage: jPage,
            jPageContainer: jPageContainer
        });

        page.onInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if ( js != undefined ) {

        js.set({
            jPage: jPage,
            jPageContainer: jPageContainer
        });

        if (Lia.p(js, 'onInit') != undefined) {
            js.onInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
        }
    }

    if (menuPage.onPostInit != undefined) {
        menuPage.onPostInit(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

};


Lia.MenuPage.prototype.onChange = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {

    var menuPage = this;

    var page = menuPage.page;
    var js = menuPage.js;

    if (menuPage.onPreChange != undefined) {
        menuPage.onPreChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (page != undefined) {
        page.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (Lia.p(js, 'onChange') != undefined) {
        js.onChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (menuPage.onPostChange != undefined) {
        menuPage.onPostChange(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }
};


Lia.MenuPage.prototype.onRelease = function (jPage, jPageContainer, i, parameterMap, beforeParameterMap) {

    var menuPage = this;

    var page = menuPage.page;
    var js = menuPage.js;

    if (menuPage.onPreRelease != undefined) {
        menuPage.onPreRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (page != undefined) {
        page.onRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (Lia.p(js, 'onRelease') != undefined) {
        js.onRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }

    if (menuPage.onPostRelease != undefined) {
        menuPage.onPostRelease(jPage, jPageContainer, i, parameterMap, beforeParameterMap);
    }
};


/* 메뉴 검색 편하게 해주는 모듈 */
var MenuManager = jQuery.MenuManager = Lia.MenuManager = {

    menuList: undefined,
    menuMap: undefined,

    selectedMenuList: [],

    setMenuId: function (menuId) {

        Lia.MenuManager.selectedMenuList = Lia.MenuManager.extractSelectedMenuList(menuId);
    },

    extractSelectedMenuList: function (menuId) {

        var menu = Lia.MenuManager.getMenu(menuId);

        var list = [];
        while (true) {

            if (menu == undefined) {
                break;
            }

            list.push(menu);

            menu = Lia.MenuManager.getMenu(Lia.p(menu, 'parent_id'));
        }

        var selectedMenuList = list.reverse();

        while (true) {

            var item = selectedMenuList[selectedMenuList.length - 1];
            var childList = Lia.p(item, 'child_list');
            if (Array.isEmpty(childList)) {
                break;
            }

            selectedMenuList.push(Lia.p(childList, 0));
        }

        return selectedMenuList;
    },

    extractLastSelectedMenu: function (menuId) {

        var menu = Lia.MenuManager.getMenu(menuId);

        while (true) {

            var childList = Lia.p(menu, 'child_list');
            if (Array.isEmpty(childList)) {
                break;
            }

            menu = Lia.p(childList, 0);
        }

        return menu;
    },


    getSiblingsAndMe: function (menuId) {

        var menu = Lia.MenuManager.getMenu(menuId);
        var parentId = Lia.p(menu, 'parent_id');

        var parentMenu = Lia.MenuManager.getMenu(parentId);

        var childList = Lia.p(parentMenu, 'child_list');
        return childList;
    },


    getSelectedMenuAt: function (idx) {
        return Lia.p(Lia.MenuManager.selectedMenuList, idx);
    },

    getSelectedMenuLength: function () {
        return Lia.pd(0, Lia.MenuManager.selectedMenuList, 'length');
    },


    // func ( idx, menu, totalCount, object )
    eachSelectedMenu: function (func, object) {

        var list = Lia.MenuManager.selectedMenuList;
        for (var i = 0, l = list.length; i < l; i++) {

            var item = Lia.p(list, i);
            func(i, item, l, object);
        }
    },

    getLastSelectedMenu: function () {
        return Lia.p(Lia.MenuManager.selectedMenuList, Lia.MenuManager.selectedMenuList.length - 1);
    },

    setMenuList: function (list) {

        Lia.MenuManager.menuList = list;
        Lia.MenuManager.setMenuMap(Lia.MenuManager.menuList, Lia.MenuManager.menuMap = {});
    },

    getMenuList: function () {
        return Lia.MenuManager.menuList;
    },

    getMenu: function (menuId) {
        return Lia.p(Lia.MenuManager.menuMap, menuId);
    },

    setMenuMap: function (menuList, map) {

        if (menuList != undefined) {

            for (var i = 0, l = menuList.length; i < l; i++) {

                var item = menuList[i];
                var id = item['id'];
                map[id] = item;

                var childList = item['child_list'];
                if (childList != undefined && childList.length > 0) {
                    map = Lia.MenuManager.setMenuMap(childList, map);
                }
            }
        }

        return map;
    }
};


var ShareHelper = Lia.ShareHelper = $.ShareHelper = {

    facebook: function (url) {

        Lia.open('https://www.facebook.com/sharer/sharer.php', {
            u: url
        }, {
            width: 600,
            height: 400
        });
    },


    twitter: function (url, text) {

        Lia.open('https://www.twitter.com/share', {
            url: url,
            text: text
        }, {
            width: 626,
            height: 436
        });

    },

    linkedin: function (url) {

        Lia.open('https://www.linkedin.com/sharing/share-offsite/', {
            url: url
        }, {
            width: 626,
            height: 436
        });
    }

};
