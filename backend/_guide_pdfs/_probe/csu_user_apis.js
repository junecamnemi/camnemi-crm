
var UserApiUrl;
var ApiUrl = UserApiUrl = {

    Board: {

        ADD_BOARD: '/api/board/addBoard',
        ADD_BOARD_CONTENT: '/api/board/addBoardContent',
        ADD_BOARD_CONTENT_CATEGORY: '/api/board/addBoardContentCategory',
        ADD_GALLERY_BOARD_CONTENTS: '/api/board/addGalleryBoardContents',
        DELETE_BOARD_CONTENT: '/api/board/deleteBoardContent',
        DELETE_BOARD_CONTENT_CATEGORY: '/api/board/deleteBoardContentCategory',
        DELETE_BOARD_CONTENT_PERMANENTLY: '/api/board/deleteBoardContentPermanently',
        DOWN_VOTE: '/api/board/downvote',
        EDIT_BOARD_CONTENT: '/api/board/editBoardContent',
        EDIT_BOARD_CONTENT_CATEGORY: '/api/board/editBoardContentCategory',
        GET_BOARD_CONTENT: '/api/board/getBoardContent',
        GET_BOARD_CONTENT_CATEGORY: '/api/board/getBoardContentCategory',
        GET_BOARD_CONTENT_CATEGORY_LIST: '/api/board/getBoardContentCategoryList',
        GET_BOARD_LIST: '/api/board/getBoardList',
        GET_BOARD: '/api/board/getBoard',
        RECOVER_BOARD_CONTENT: '/api/board/recoverBoardContent',
        SET_BOARD_CONTENT_AVAILABILITY: '/api/board/setBoardContentAvailability',
        SET_BOARD_CONTENT_PRIVATE: '/api/board/setBoardContentPrivate',
        SET_BOARD_CONTENT_STATUS: '/api/board/setBoardContentStatus',
        SET_BOARD_CONTENTS_AVAILABILITY: '/api/board/setBoardContentsAvailability',
        CHECK_BOARD_OWNER_PASSWORD: '/api/board/checkOwnerPassword',
        UP_VOTE: '/api/board/upvote',
        SET_BOARD_CONTENT_TARGET_USERS: '/api/board/setBoardContentTargetUsers',
        MOVE_BOARD_CONTENT: '/api/board/moveBoardContent',
        DELETE_BOARD_CONTENT_FOR_BOARD_PERMANENTLY: '/api/board/deleteBoardContentForBoardPermanently',
        // SET_BOARD_CONTENT_REGISTERED_DATE: '/api/board/setBoardContentRegisteredDate',

        GET_BOARD_CONTENT_SUMMARY_LIST: '/api/user/board/getBoardContentSummaryList',
        SEARCH_BOARD_CONTENT_SUMMARY_LIST: '/api/user/board/searchBoardContentSummaryList',

        SET_BOARD_CONTENT_DISPLAY_ORDER: '/api/board/setBoardContentDisplayOrder',
        SET_IS_IMPORTANT: '/api/user/board/setIsImportant'
    },

    File: {
        CK_EDITOR_UPLOAD: '/api/file/ckEditorUpload',
        DELETE: '/api/file/delete',
        GET: '/api/file/get',
        UPLOAD: '/api/file/upload'
    },

    Video: {
        GET_VIMEO_THUMBNAIL: '/api/video/getVimeoThumbnail'
    },

    User: {
        ADD_GROUP: '/api/user/addGroup',
        DELETE_GROUP: '/api/user/deleteGroup',
        CHANGE_USER_PASSWORD: '/api/user/changeUserPassword',
        EDIT_GROUP: '/api/user/editGroup',
        EDIT_USER: '/api/user/editUser',
        EDIT_USER_PROFILE: '/api/user/editUserProfile',
        ELEVATE_TEMPORARY_USER: '/api/user/elevateTemporaryUser',
        FIND_USER_ID: '/api/user/findUserId',
        GET_GROUP: '/api/user/getGroup',
        GET_GROUP_SUMMARY_LIST: '/api/user/getGroupSummaryList',
        GET_USER: '/api/user/getUser',
        GET_USER_PROFILE: '/api/user/getUserProfile',
        GET_USER_SUMMARY_LIST: '/api/user/getUserSummaryList',
        GET_ADMINISTRATOR_LIST: '/api/user/getAdministratorList',
        EXPORT_USER_SUMMARY_LIST: '/api/user/exportUserSummaryList',
        LOGIN: '/api/user/login',
        LOGIN_WITH_THIRD_PARTY_USER_ACCOUNT: '/api/user/loginWithThirdPartyUserAccount',
        LOGOUT: '/api/user/logout',
        REGISTER_USER: '/api/user/registerUser',
        RESET_USER_PASSWORD: '/api/user/resetUserPassword',
        SIGN_UP: '/api/user/signUp',
        VALIDATE_ID: '/api/user/validateId',
        IMPORT_USERS: '/api/user/importUsers',
        GET_USER_EMPLOYMENT_STATUS: '/api/user/getUserEmploymentStatus',
        EDIT_USER_ADDITIONAL_INFO: '/api/user/editUserAdditionalInfo',
        EXPORT_USERS: '/api/user/exportUsers',
        GET_USER_EXCEL_IMPORT_TEMPLATE: '/api/user/getUserExcelImportTemplate',

        GET_USER_STATUS_STATISTICS: '/api/user/getUserStatusStatistics',
        GET_USER_LOGIN_STATISTICS: '/api/user/getUserLoginStatistics',

        EXPORT_USER_STATUS_STATISTICS: '/api/user/exportUserStatusStatistics',
        EXPORT_USER_LOGIN_STATISTICS: '/api/user/exportUserLoginStatistics',

        EDIT_USER_PROPERTIES: '/api/user/editUserProperties'
    },

    Message: {
        GET_SENT_MESSAGE_SUMMARY_LIST: '/api/message/getSentMessageSummaryList',
        GET_COURSE_CONTENT_EDITOR_CONTACT_LIST: '/api/message/getCourseContentEditorContactList',
        GET_COURSE_ADMINISTRATOR_CONTACT_LIST: '/api/message/getCourseAdministratorContactList',
        SEND_MESSAGES: '/api/message/sendMessages',
        GET_SENT_MESSAGE: '/api/message/getSentMessage'
    },

    Website: {
        // ADD_BANNER: '/api/website/addBanner',
        // ADD_INFORMATION: '/api/website/addInformation',
        // DELETE_BANNER: '/api/website/deleteBanner',
        // DELETE_BANNER_PERMANENTLY: '/api/website/deleteBannerPermanently',
        // DELETE_INFORMATION: '/api/website/deleteInformation',
        // DELETE_INFORMATION_PERMANENTLY: '/api/website/deleteInformationPermanently',
        // EDIT_BANNER: '/api/website/editBanner',
        // EDIT_INFORMATION: '/api/website/editInformation',
        GET_AVAILABLE_BANNER_LIST: '/api/website/getAvailableBannerList',
        GET_AVAILABLE_INFORMATION: '/api/website/getAvailableInformation',
        GET_BANNER: '/api/website/getBanner',
        GET_BANNER_SUMMARY_LIST: '/api/website/getBannerSummaryList',
        GET_INFORMATION: '/api/website/getInformation',
        GET_INFORMATION_SUMMARY_LIST: '/api/website/getInformationSummaryList',
        // SET_BANNER_AVAILABILITY: '/api/website/setBannerAvailability',
        // SET_BANNER_DISPLAY_ORDER: '/api/website/setBannerDisplayOrder',
        // RECOVER_BANNER: '/api/website/recoverBanner',

        //Menu
        // ADD_MENU: '/api/website/addMenu',
        // DELETE_MENU: '/api/website/deleteMenu',
        // DELETE_MENU_PERMANENTLY: '/api/website/deleteMenuPermanently',
        // RECOVER_MENU: '/api/website/recoverMenu',
        // EDIT_MENU: '/api/website/editMenu',
        GET_MENU: '/api/website/getMenu',
        GET_MENU_LIST: '/api/website/getMenuList',
        // SET_MENU_AVAILABILITY: '/api/website/setMenuAvailability',
        // SET_MENU_DISPLAY_ORDER: '/api/website/setMenuDisplayOrder',


        // GET_MENU_ADMINISTRATOR_SUMMARY_LIST: '/api/website/getMenuAdministratorSummaryList',
        // REGISTER_MENU_ADMINISTRATORS: '/api/website/registerMenuAdministrators',
        // UNREGISTER_MENU_ADMINISTRATOR: '/api/website/unregisterMenuAdministrators',

        GET_MENU_USER_SUMMARY_LIST: '/api/website/getMenuUserSummaryList',
        // REGISTER_MENU_USERS: '/api/website/registerMenuUsers',
        // UNREGISTER_MENU_USERS: '/api/website/unregisterMenuUsers',

        // IMPORT_MENUS_AND_USERS: '/api/website/importMenusAndUsers',
        // GET_MENUS_AND_USERS_EXCEL_IMPORT_TEMPLATE: '/api/website/getMenuUserExcelImportTemplate',

        GET_USER_SUMMARY_LIST_WITHOUT_MENU_USER: '/api/website/getUserSummaryListWithoutMenuUser'
    },

    System: {
        EDIT_SYSTEM_VARIABLES: '/api/system/editSystemVariables',
        GET_SYSTEM_EVENT: '/api/system/getSystemEvent',
        GET_SYSTEM_EVENT_SUMMARY_LIST: '/api/system/getSystemEventSummaryList',
        GET_SYSTEM_VARIABLE_LIST: '/api/system/getSystemVariableList'
    },

    Excel: {

        GET_DOCUMENT_SUMMARY_LIST: '/api/excel/getDocumentSummaryList',
        GET_EXCEL_IMPORT_RESULT: '/api/excel/getExcelImportResult'
    },

    Document : {
        ADD_TERMS_OF_SERVICE: '/api/document/addTermsOfService',
        EDIT_TERMS_OF_SERVICE: '/api/document/editTermsOfService',
        GET_TERMS_OF_SERVICE: '/api/document/getTermsOfService',
        GET_TERMS_OF_SERVICE_SUMMARY_LIST: '/api/document/getTermsOfServiceSummaryList',
        SET_TERMS_OF_SERVICE_AVAILABILITY: '/api/document/setTermsOfServiceAvailability',
        DELETE_TERMS_OF_SERVICE: '/api/document/deleteTermsOfService',
        DELETE_TERMS_OF_SERVICE_PERMANENTLY: '/api/document/deleteTermsOfServicePermanently',
        RECOVER_TERMS_OF_SERVICE: '/api/document/recoverTermsOfService',
        REGISTER_USER_TERMS_OF_SERVICE: '/api/document/registerUserTermsOfService',

        GET_CURRENT_SIGN_UP_TERMS_OF_SERVICE: '/api/document/getCurrentSignUpTermsOfService',
    },

    Survey: {

        ADD_SURVEY: '/api/survey/addSurvey',
        CANCEL_SURVEY_REQUEST: '/api/survey/cancelSurveyRequest',
        CHECK_SURVEY_REQUIREMENT: '/api/survey/checkSurveyRequirement',
        DELETE_SURVEY: '/api/survey/deleteSurvey',
        DELETE_SURVEY_PERMANENTLY: '/api/survey/deleteSurveyPermanently',
        EDIT_SURVEY: '/api/survey/editSurvey',
        GET_SURVEY: '/api/survey/getSurvey',
        CHECK_SURVEY_RESULT: '/api/survey/checkSurveyResult',
        EXPORT_SURVEY_RESULT: '/api/survey/exportSurveyResult',
        GET_SURVEY_REQUEST: '/api/survey/getSurveyRequest',
        CHECK_SURVEY_REQUEST_RESULT: '/api/survey/checkSurveyRequestResult',
        EXPORT_SURVEY_REQUEST_RESULT: '/api/survey/exportSurveyRequestResult',
        GET_SURVEY_SUMMARY_LIST: '/api/survey/getSurveySummaryList',
        GET_SURVEY_REQUEST_SUMMARY_LIST: '/api/survey/getSurveyRequestSummaryList',
        RECOVER_SURVEY: '/api/survey/recoverSurvey',
        SUBMIT_SURVEY: '/api/survey/submitSurvey',
        SEND_SURVEY_REQUEST: '/api/survey/sendSurveyRequest',
        TAKE_SURVEY: '/api/survey/takeSurvey',
        GET_SURVEY_PARTICIPANT_SUMMARY_LIST: '/api/survey/getSurveyParticipantSummaryList',
        GET_AVAILABLE_SURVEY_REQUEST_SUMMARY_LIST: '/api/survey/getAvailableSurveyRequestSummaryList'
    },

    Cdn: {

        PURGE: '/api/cdn/purge'
    },

    Rest: {
        // ADD_API_KEY: '/api/rest/addApiKey',
        // DELETE_API_KEY: '/api/rest/deleteApiKey',
        // EDIT_API_KEY: '/api/rest/editApiKey',
        // GET_API_KEY: '/api/rest/getApiKey',
        // GET_API_KEY_SUMMARY_LIST: '/api/rest/getApiKeySummaryList',
        // SET_API_KEY_AVAILABILITY: '/api/rest/setApiKeyAvailability'
    },

    Certificate: {

        GET_CERTIFICATE: '/api/certificate/getCertificate'
    },

    Department: {

        GET_DEPARTMENT_SUMMARY_LIST: '/api/department/getDepartmentSummaryList',

        //학과 관리자 배정
        REGISTER_DEPARTMENT_ADMINISTRATOR: '/api/department/registerDepartmentAdministrator',
        UNREGISTER_DEPARTMENT_ADMINISTRATOR: '/api/department/unregisterDepartmentAdministrator',
        GET_DEPARTMENT_ADMINISTRATOR_SUMMARY_LIST: '/api/department/getDepartmentAdministratorSummaryList'

    },


    Application: {

        //상담 양식 관련
        ADD_APPLICATION_FORM: '/api/application/addApplicationForm',
        EDIT_APPLICATION_FORM: '/api/application/editApplicationForm',
        DELETE_APPLICATION_FORM: '/api/application/deleteApplicationForm',
        DELETE_APPLICATION_FROM_PERMANENTLY: '/api/application/deleteApplicationFormPermanently',
        RECOVER_APPLICATION_FORM: '/api/application/recoverApplicationForm',
        GET_APPLICATION_FORM_SUMMARY_LIST: '/api/application/getApplicationFormSummaryList',
        GET_APPLICATION_FORM: '/api/application/getApplicationForm',
        SET_APPLICATION_FROM_AVAILABILITY: '/api/application/setApplicationFormAvailability',

        //상담 관련
        ADD_APPLICATION: '/api/application/addApplication',
        EDIT_APPLICATION: '/api/application/editApplication',
        DELETE_APPLICATION: '/api/application/deleteApplication',
        DELETE_APPLICATION_PERMANENTLY: '/api/application/deleteApplicationPermanently',
        RECOVER_APPLICATION: '/api/application/recoverApplication',
        GET_APPLICATION: '/api/application/getApplication',
        GET_APPLICATION_SUMMARY_LIST: '/api/application/getApplicationSummaryList',
        SET_APPLICATION_AVAILABILITY: '/api/application/setApplicationAvailability',

        //상담 신청 관련
        WRITE_USER_APPLICATION: '/api/application/writeUserApplication',
        EDIT_USER_APPLICATION: '/api/application/editUserApplication',
        DELETE_USER_APPLICATION: '/api/application/deleteUserApplication',
        CHANGE_USER_APPLICATION_STATUS: '/api/application/changeUserApplicationStatus',
        DELETE_USER_APPLICATION_PERMANENTLY: '/api/application/deleteUserApplicationPermanently',
        RECOVER_USER_APPLICATION: '/api/application/recoverUserApplication',
        COPY_USER_APPLICATION: '/api/application/copyUserApplication',
        GET_USER_APPLICATION: '/api/application/getUserApplication',
        GET_USER_APPLICATION_SUMMARY_LIST: '/api/application/getUserApplicationSummaryList',
        EXPORT_USER_APPLICATION_SUMMARY_LIST: '/api/application/exportUserApplicationSummaryList',
        GET_USER_APPLICATION_SUMMARY_LIST_BY_USER_INPUT: '/api/application/getUserApplicationSummaryListByUserInput',

        //비밀번호 관련
        CHECK_USER_APPLICATION_PASSWORD: '/api/application/checkUserApplicationPassword'
    },

    Calendar: {

        GET_SCHEDULE_PERMISSION: '/api/calendar/getSchedulePermission',
        GET_SCHEDULE_SUMMARY_LIST: '/api/calendar/getScheduleSummaryList',
        ADD_SCHEDULE: '/api/calendar/addSchedule',
        DELETE_SCHEDULE: '/api/calendar/deleteSchedule',
        EDIT_SCHEDULE: '/api/calendar/editSchedule',
        EDIT_SCHEDULE_STATUS: '/api/calendar/editScheduleStatus',
        GET_SCHEDULE: '/api/calendar/getSchedule'
    },

    Task: {

        GET_ASYNC_TASK: '/api/task/getAsyncTask',
        GET_ASYNC_TASK_RESULT: '/api/task/getAsyncTaskResult'

    }
};
