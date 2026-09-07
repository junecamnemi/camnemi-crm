

var LOADING_LAYOUT_LOADING = 0;
var LOADING_LAYOUT_EMPTY = 1;
var LOADING_LAYOUT_HIDE = 2;

(function ($) {

    $.extend({

        initLoadingLayout : function( j, option ) {

            var selector = '.' + 'loading_layout';

            if ( j == undefined )
                j = $( selector );
            else
                j = j.find( selector );

            return j.initLoadingLayout(option);
        },

        setLoadingLayout : function( j, val ) {

            var selector = '.' + 'loading_layout';

            if ( j == undefined )
                j = $( selector );
            else
                j = j.find( selector );

            return j.setLoadingLayout(val);
        }


    });

    $.fn.extend({

        initLoadingLayout : function() {

            for(var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);
                if ( !jItem.hasClass( Lia.Component.Flag.INITED ) ) {

                    jItem.css({ 'width' : '100%' });

                    var jLoading = $('<div style="width:100%;padding-top:50px;padding-bottom:50px;text-align: center;"><img class="loading_indicator" style="height:67px;"></div>');
                    jItem.append(jLoading);

                    var jEmpty = $('<div style="width:100%;text-align:center;padding-top:50px;padding-bottom:50px;display:none;">' +
                        '<img src="/res/lms/img/sub/img_default.png" />' +
                        '<p style="margin-top: 20px; font-family: NanumBarunGothicBold;">표시할 항목이 없습니다.</p></div>'+
                        '</div>');
                    jItem.append(jEmpty);
                    $.initAndPlayLoadingIndicator(jLoading);

                    jItem.addClass( Lia.Component.Flag.INITED );
                }

            }

            return this;
        },

        setLoadingLayout : function( val ) {

            for(var i = 0, l = this.size(); i < l; i++) {

                var jItem = this.eq(i);

                var jChildren = jItem.children();

                if ( val == LOADING_LAYOUT_LOADING ) {

                    jItem.show();
                    jChildren.eq(0).show();
                    jChildren.eq(1).hide();
                    $.playLoadingIndicator(jItem);

                } else if ( val == LOADING_LAYOUT_EMPTY )  {

                    jItem.show();
                    jChildren.eq(0).hide();
                    jChildren.eq(1).show();
                    $.pauseLoadingIndicator(jItem);

                } else if ( val == LOADING_LAYOUT_HIDE ) {

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

    init : function() {

        $.initDim();
        $.initPopup();
        $.initPopupLoading();
    },

    show : function() {
        $.showPopupLoading();
    },

    hide : function() {
        $.hidePopupLoading();
    },

    clear : function() {
        $.clearAndHidePopupLoading();
    }

};
LoadingPopupManager.init();

$.initPopupZIndex(10000);
$.setLoadingIndicatorOptions({
    'lia-src'  : '/res/service/img/common/loadingbar/loading_{index}.png?V=100',
    'lia-start-index' : '1',
    'lia-end-index' : '12'

});

var ProjectPopupUrl = {
    ALERT_POPUP : 'service/popup/alert_popup',
    FUND_TERM_MODAL : 'service/popup/fund_term_modal',
    BANNER_POPUP : 'service/popup/banner_popup',
    GALLERY_POPUP : 'service/popup/gallery_popup',
    BOARD_PASSWORD_POPUP : 'service/popup/board_password_popup',
    PROFESSOR_POPUP : 'service/popup/professor_popup',
    DELETE_BOARD_PASSWORD_POPUP: 'service/popup/delete_board_password_popup',
    REGISTER_NAME_POPUP : 'service/popup/register_name_popup'
};

var PopupManager = {

    getCodeByResponse : function ( response ) {

        var code = Lia.p(response, 'code');
        if ( code == undefined ) {
            code = response;
        }
        return code;
    },

    getTitleByCode : function ( code ) {
        return Code.getTitle(code);
    },

    getMessageByCode : function ( code ) {
        return Code.getMessage(code);
    },

    alertByResponse : function( response, confirm ) {

        var code = PopupManager.getCodeByResponse(response);
        var title = PopupManager.getTitleByCode(code);
        var message = Lia.p(response, 'message');
        if ( message == undefined ) {
            message = PopupManager.getMessageByCode(code);
        }

        PopupManager.show({
            title : title,
            message : message,
            confirm: confirm
        });
    },

    alert: function (title, message, confirm, cancel, confirmText, cancelText, object, buttonList, init) {

        PopupManager.show({
            title: title,
            message: message,
            confirm: confirm,
            cancel: cancel,
            confirmText : confirmText,
            cancelText : cancelText,
            object : object,
            buttonList : buttonList,
            init :init
        });
    },

    alertWithImage: function (title, message, image, confirm, cancel, confirmText, cancelText, object) {

        PopupManager.show({
            title: title,
            message: message,
            confirm: confirm,
            cancel: cancel,
            confirmText : confirmText,
            cancelText : cancelText,
            image : image,
            object : object
        });
    },

    show: function (options) {

        AjaxPopupManager.show( ProjectPopupUrl.ALERT_POPUP, options);
    }
};

var UserManager = {

    notLoggedInMenuList: ['home'],

    loggedIn: false,
    name: undefined,
    nickname: undefined,
    email: undefined,
    roleCode: undefined,
    profileImageUrl: undefined,
    getRoleCode: function () {
        return UserManager.roleCode;
    },
    isLoggedIn: function () {
        return UserManager.loggedIn;
    },
    getIdx: function () {
        return UserManager.idx;
    },
    getName: function () {
        return UserManager.name;
    },
    getNickname: function () {
        return UserManager.nickname;
    },
    getEmail: function () {
        return UserManager.email;
    },
    getProfileImageUrl: function () {
        return UserManager.profileImageUrl;
    },
    setLoggedIn: function (loggedIn, idx, name, nickname, email, roleCode, profileImageUrl) {

        UserManager.loggedIn = loggedIn;
        UserManager.idx = idx;
        UserManager.name = name;
        UserManager.nickname = nickname;
        UserManager.email = email;
        UserManager.roleCode = roleCode;
        UserManager.profileImageUrl = profileImageUrl
    },

    login: function (id, pw, stayLoggedIn, onLoginResponse) {

    },

    logout: function () {

    }

};

var Requester = new jQuery.Requester({

    onRequestStart : function(request) {

        var autoLoading = Lia.p(request, 'object', 'autoLoading');
        if ( autoLoading == undefined )
            autoLoading = false;

        if ( autoLoading ) {
            LoadingPopupManager.show();
        }
    },

    onRequestEnded : function(status, data, request) {

        var autoLoading = Lia.p(request, 'object', 'autoLoading');
        if ( autoLoading == undefined )
            autoLoading = false;

        if ( autoLoading ) {
            LoadingPopupManager.hide();
        }
    },

    responseCheckHandler : function(status, data, request) {

        // 응답 체크하여 결과값 전달
        var code = undefined;
        var error = (status == Requester.Status.ERROR || data == undefined );
        if ( !error ) {

            if ( request['dataType'] == 'json' ) {

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

                if ( code ==  Code.INVALID_SESSION ) {
                    PopupManager.alertByResponse(data, function(){

                        PageManager.redirect(Server.ssoServerUrl + '?redirect_url=' + encodeURIComponent(document.location.href));
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

var AjaxPopupManager = $.AjaxPopupManager;
AjaxPopupManager.init({

    popupListLayoutSelector : '#popup_layout_list',

    requester : Requester,

    cssLoading : false,
    htmlLoading : true,
    jsLoading : true,

    caching : undefined,
    filePathCachingHandler : function(path, parameterMap, contentType) {
        return true;
    },

    filePathFormatHandler : function(path, parameterMap) {
        return path;
    },
    cssFilePathFormatHandler : function(path, parameterMap) {
        return '/res/' + path + '.css';
    },
    htmlFilePathFormatHandler : function(path, parameterMap) {
        return '/res/' + path + '.html';
    },
    jsFilePathFormatHandler : function(path, parameterMap) {
        return '/res/' + path + '.js';
    }
});













