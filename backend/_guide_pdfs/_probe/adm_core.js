
if (typeof Server != "undefined") {
    Lia.setDebugMode(Server.serverMode !='production');
}

var AsyncTaskHelper = {


    // callback : function( success, data ) {}
    request : function ( url, parameterMap, callback ) {

        Requester.ajaxWithoutBlank(url, parameterMap,
            function (status, data, request) {

                var id = Lia.p(data, 'body', 'id');

                if(  id == undefined || status != Requester.Status.SUCCESS ) {
                    callback( false, data );
                    return;
                }

                AsyncTaskHelper.checkTask(id, callback);

            }, {
                autoPopup : false,
                autoLoading : false
            });
    },

    checkTask: function (id, callback) {

        Requester.ajaxWithoutBlank(ApiUrl.Task.GET_ASYNC_TASK, {
            id: id
        }, function (status, data, request) {

            if( status != Requester.Status.SUCCESS ) {

                callback( false, data);
                return;
            }

            var statusCode = Lia.p(data, 'body', 'status_code');

            if (statusCode != AsyncTaskStatus.NEW && statusCode != AsyncTaskStatus.PROCESSING) {

                if ( statusCode == AsyncTaskStatus.COMPLETED ) {

                    callback( status==Requester.Status.SUCCESS, data);

                } else {

                    callback( false, data);
                }


            } else {

                window.setTimeout(function (id, callback) {
                    AsyncTaskHelper.checkTask(id, callback);
                }, 1000, id, callback);

            }
        });
    }

};


var LOADING_LAYOUT_LOADING = 0;
var LOADING_LAYOUT_EMPTY = 1;
var LOADING_LAYOUT_HIDE = 2;

(function ($) {

    $.extend({

        initLoadingLayout: function (j, option) {

            var selector = '.' + 'loading_layout';

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.initLoadingLayout(option);
        },

        setLoadingLayout: function (j, val) {

            var selector = '.' + 'loading_layout';

            if (j == undefined)
                j = $(selector);
            else
                j = j.find(selector);

            return j.setLoadingLayout(val);
        }


    });

    $.fn.extend({

        initLoadingLayout: function () {

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if (!jItem.hasClass(Lia.Component.Flag.INITED)) {

                    jItem.css({'width': '100%'});

                    var jLoading = $('<div style="width:100%;padding-top:50px;padding-bottom:50px;text-align: center;"><img class="loading_indicator" style="height:67px;"></div>');
                    jItem.append(jLoading);

                    var jEmpty = $('<div style="width:100%;text-align:center;padding-top:50px;padding-bottom:50px;display:none;">' +
                        '<img src="/res/lms/img/sub/img_default.png" />' +
                        '<p style="margin-top: 20px; font-family: notokr-medium, NanumGothicBold;">표시할 항목이 없습니다.</p></div>' +
                        '</div>');
                    jItem.append(jEmpty);
                    $.initAndPlayLoadingIndicator(jLoading);

                    jItem.addClass(Lia.Component.Flag.INITED);
                }

            }

            return this;
        },

        setLoadingLayout: function (val) {

            for (var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                var jChildren = jItem.children();

                if (val == LOADING_LAYOUT_LOADING) {

                    jItem.show();
                    jChildren.eq(0).show();
                    jChildren.eq(1).hide();
                    $.playLoadingIndicator(jItem);

                } else if (val == LOADING_LAYOUT_EMPTY) {

                    jItem.show();
                    jChildren.eq(0).hide();
                    jChildren.eq(1).show();
                    $.pauseLoadingIndicator(jItem);

                } else if (val == LOADING_LAYOUT_HIDE) {

                    jItem.hide();
                    jChildren.eq(0).hide();
                    jChildren.eq(1).hide();
                    $.pauseLoadingIndicator(jItem);
                }

            }

            return this;
        }


    });

})(jQuery);




var LoadingPopupManager = {

    init: function () {

        jQuery.initDim();
        jQuery.initPopup();
        jQuery.initPopupLoading();
    },

    show: function () {
        jQuery.showPopupLoading();
    },

    hide: function () {
        jQuery.hidePopupLoading();
    },

    clear: function () {
        jQuery.clearAndHidePopupLoading();
    }
};
LoadingPopupManager.init();

jQuery.initPopupZIndex(10000);
jQuery.setLoadingIndicatorOptions({
    'lia-src': '/res/service/img/common/loadingbar/loading_{index}.png?V=100',
    'lia-start-index': '1',
    'lia-end-index': '12'

});


var PathHelper = {

    dataBaseUrl: '',
    setDataBaseUrl: function (url) {
        PathHelper.dataBaseUrl = url;
    },

    getDataUrl: function (url, originalFilename) {

        if (typeof url == "string") {

            if (url.startsWith('http://') || url.startsWith('https://')) {
                return url;
            }

        } else {

            try {

                if (url.startsWith('http://') || url.startsWith('https://')) {
                    return url;
                }

            } catch (e) {
            }
        }

        var r = PathHelper.dataBaseUrl + url;
        if (originalFilename != undefined) {
            r += '&destFilename=' + encodeURIComponent(originalFilename);
        }

        return r;
    },

    getFileUrl: function (url, destFilename, ignoreDestFilename) {

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

        var fileParameterMap = {
            path: url
        };

        if (String.isNotBlank(destFilename)) {
            fileParameterMap['destFilename'] = destFilename;
        }

        fileParameterMap['ignoreDestFilename'] = ignoreDestFilename;

        return baseUrl + ApiUrl.File.GET + Lia.convertArrayToQueryString(fileParameterMap);
    },

    getAttachmentUrl: function (attachment) {
        return PathHelper.getFileUrl(Lia.p(attachment, 'url'), Lia.p(attachment, 'original_filename'));
    },


    open: function (url, filename) {

        var isImage = FileHelper.isImageFile(url);
        url = PathHelper.getFileUrl(url, filename);
        Requester.owb(url);
    },

    getUrl : function( url, baseDomain ) {

        var jLocation = $(location);
        var host = jLocation.attr('host');
        if ( String.isNotBlank(baseDomain) ) {
            host = baseDomain;
        }
        var port = jLocation.attr('port');
        if ( String.isNotBlank(port) ) {
            port = ':' + port;
        } else {
            port = '';
        }

        var baseUrl = jLocation.attr('protocol') + '//' + host + port;
        return baseUrl + url;
    }
};





var FormatHelper = jQuery.FormatHelper;
var DateHelper = jQuery.DateHelper;
var CookieHelper = jQuery.CookieHelper;
var FormSerializer = new jQuery.FormSerializer();
var YouTubeHelper = jQuery.YouTubeHelper;
var IFrameManager = jQuery.IFrameManager;
var FileHelper = jQuery.FileHelper;

var PageLinkHelper = {

    applyPageLink : function( j ) {

        var jMenuLink = undefined;
        if (j == undefined) {
            jMenuLink = $('.menu_link');
        } else {
            jMenuLink = j.find('.menu_link');
        }

        jMenuLink.off('click.menu_link').on('click.menu_link', function () {

            var jThis = $(this);

            var page1 = jThis.attr('page-m1');
            var page2 = jThis.attr('page-m2');
            var page3 = jThis.attr('page-m3');

            var menuId = jThis.attr('menu-id');

            var name = [];

            if ( String.isNotBlank(menuId) && String.isBlank(page1) ) {
                page1 = 'page';
            }

            if (String.isNotBlank(page1)) {
                name.push(page1);
            }
            if (String.isNotBlank(page2)) {
                name.push(page2);
            }
            if (String.isNotBlank(page3)) {
                name.push(page3);
            }

            if ( Array.isNotEmpty(name) ) {

                if ( String.isNotBlank(menuId) ) {

                    PageManager.go(name, {
                        menu_id : menuId
                    });

                } else {

                    PageManager.go(name);
                }
            }

            var redirectUrl = jThis.attr('redirect-url');
            if ( String.isNotBlank(redirectUrl) ) {
                Lia.redirect(redirectUrl);
            }

            var openUrl = jThis.attr('open-url');
            if ( String.isNotBlank(openUrl) ) {
                Lia.open(openUrl);
            }

        });
    }

};

















var SSOHelper = {

    goLoginPage : function() {

        Lia.redirectGet(Server.ssoServerUrl + '', {
            redirect_url : location.href
        })
    },

    logout : function( func ) {

        Requester.request({
            url: Server.ssoServerUrl + '/api/logout',
            method: 'POST',
            sync: true,
            xhrFields : { withCredentials: true },
            onResponse: function (status, data, body, request) {

                if ( !status ) {
                    return;
                }

                if ( func != undefined ) {
                    func();
                } else {
                    Lia.refresh();
                }
            }
        });
    }

};





var Requester = new jQuery.Requester({

    onRequestStart : function(request) {

        if ( request['parameterMap'] == undefined ) {
            request['parameterMap'] = {};
        }

        var autoLoading = Lia.p(request, 'object', 'autoLoading');
        if ( autoLoading == undefined )
            autoLoading = false;

        // if ( autoLoading ) {
        //     LoadingPopupManager.show();
        // }
    },

    onRequestEnded : function(status, data, request) {

        var autoLoading = Lia.p(request, 'object', 'autoLoading');
        if ( autoLoading == undefined )
            autoLoading = false;

        // if ( autoLoading ) {
        //     LoadingPopupManager.hide();
        // }
    },

    responseCheckHandler : function(status, data, request) {

        // 응답 체크하여 결과값 전달
        var code = undefined;
        var error = (status == Requester.Status.ERROR || data == undefined );
        if ( !error ) {

            if ( request['dataType'] == 'json' || request['dataType'] == 'jsonp' ) {

                code = Lia.p(data, 'code');

                if ( code != Code.SUCCESS ) {
                    error = true;
                }
            }
        }

        if ( error ) {

            var autoPopup = Lia.p(request, 'object', 'autoPopup');
            if ( autoPopup == undefined )
                autoPopup = true;

            if ( autoPopup ) {

                if ( code == Code.INVALID_SESSION ) {

                    PopupManager.alert( '안내', '세션 정보가 만료되었거나 다른 곳에서 로그인 되었습니다.', function() {
                        Lia.redirect(PageUrl.HOME);
                    });

                } else {
                    PopupManager.alertByResponse(data);
                }

            }

            return jQuery.Requester.Status.ERROR;
        }

        return status;
    }
});
Requester.Status = jQuery.Requester.Status;
















Lia.UserBoardList.setSearchOptionList([
    {name: '제목+내용', value: SearchOptionList.BoardContent.TITLE_OR_BODY},
    {name: '제목', value: SearchOptionList.BoardContent.TITLE},
    {name: '내용', value: SearchOptionList.BoardContent.BODY},
    {name: '이름', value: SearchOptionList.BoardContent.REGISTERED_BY_USER_NAME},
    {name: '아이디', value: SearchOptionList.BoardContent.REGISTERED_BY_USER_ID}
]);


Lia.MenuPage.ApiUrl = ApiUrl.Website;
Lia.MenuPage.PopupUrl = PopupUrl;

Lia.MenuPage.setMenuHandler(function( menu, result, request ) {

    var page = this;

    page.typeCode = undefined;
    page.contentData = undefined;

    page.boardId = undefined;
    page.boardTypeCode = undefined;
    page.listPermissionLevel = undefined;

    page.title = undefined;
    page.js = undefined;

    var content = page.content =  Lia.p(menu, 'content');
    var typeCode = Lia.p(content,'type_code');
    page.typeCode = typeCode;

    var contentData =  page.contentData = Lia.p(content,'data');
    if ( typeCode == ContentType.BOARD ) {

        page.boardId = page.boardIdList = contentData['id'];
        page.boardTypeCode = contentData['type_code'];
        page.listPermissionLevel = contentData['list_permission_level'];

        if(page.listPermissionLevel != undefined && Server.userRoleCode > page.listPermissionLevel && Server.loggedIn == false) {

            PopupManager.alert('확인','로그인 후에 이용하실 수 있는 서비스 입니다.<br/><br/>지금 로그인 하시겠습니까?',function(){
                SSOHelper.goLoginPage();
            }, function(){
                PageManager.go(['home']);
            });

            return;
        }

    } else if ( typeCode == ContentType.HTML_SCRIPT ) {

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

        page.title = title;
        page.js = js;

        if (String.isNotBlank(html)) {
            page.html = html;
        }
    }

    if ( result != undefined ) {
        result.call(page);
    }

});