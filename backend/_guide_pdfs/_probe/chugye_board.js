var ITSP = ITSP ? ITSP : {};
ITSP.board = ITSP.board ? ITSP.board : {};

ITSP.board.bindCaptcha = function() {
	create();
	function create() {
		$("#captcha img").attr("src", "/GetCaptcha.do?" + Math.random());
	}
	$("#refreshBtn").click(function(e) {
		e.preventDefault();
		create();
	});
};

ITSP.board.goList = function() {
	var curSearchForm = $('#curSearchForm');
	var curPageForm = $('#curPageForm');
	location.href = '/BoardList.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize();
};

ITSP.board.bindListLink = function() {
	$('[data-itsp-list-link]').click(function(event) {
		ITSP.board.goList();
	});
};

ITSP.board.bindViewLink = function() {
	$('[data-itsp-view-link]').click(function(event) {
		var me = $(this);
		var idx = me.attr('data-itsp-view-link');
		var secret = me.attr('data-itsp-secret');
		var curSearchForm = $('#curSearchForm');
		var curPageForm = $('#curPageForm');
		if("Y" == secret){
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').addClass('on');
			
			$('.modal_popup_wrap button').click(function(event) {
				var pwd = $('.modal_popup_wrap input[name=password] ').val();
				if("" == pwd){
					alert("비밀번호가 입력되지 않았습니다.");
					return false;
				}
				itsp.ajax.doPostJSON('/Board/checkPasswordAuthentication', { idx : idx, password : pwd },  function(data) {
					if (data.header.code == itsp.ajax.CODE_SUCCESS) {
						location.href = '/BoardView.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize()+'&idx='+idx;
					} else {
						$('.modal_popup').removeClass('on');
						alert(data.header.message);
						return false;
					}
				});
			});
		}else{
			location.href = '/BoardView.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize()+'&idx='+idx;
		}
		$('.modal_popup_wrap .bt_close').click(function(event) {
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').removeClass('on');
		});
	});
};

//등록 및 수정 화면
ITSP.board.bindEditLink = function() {
	$('[data-itsp-edit-link]').click(function(event) {
		var me = $(this);
		var idx = me.attr('data-itsp-edit-link');
		var secret = me.attr('data-itsp-secret');
		var curSearchForm = $('#curSearchForm');
		var curPageForm = $('#curPageForm');
		
		if("Y" == secret){
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').addClass('on');
			
			$('.modal_popup_wrap button').click(function(event) {
				var pwd = $('.modal_popup_wrap input[name=password] ').val();
				if("" == pwd){
					alert("비밀번호가 입력되지 않았습니다.");
					return false;
				}
				itsp.ajax.doPostJSON('/Board/checkPasswordAuthentication', { idx : idx, password : pwd },  function(data) {
					if (data.header.code == itsp.ajax.CODE_SUCCESS) {
						location.href = '/BoardEdit.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize()+'&idx='+idx;
					} else {
						$('.modal_popup').removeClass('on');
						alert(data.header.message);
						return false;
					}
				});
			});
			
		}else{
			location.href = '/BoardEdit.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize()+'&idx='+idx;
		}
		$('.modal_popup_wrap .bt_close').click(function(event) {
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').removeClass('on');
		});
	});
	
	$('[data-itsp-reEdit-link]').click(function(event) {
		var me = $(this);
		var idx = me.attr('data-itsp-reEdit-link');
		var curSearchForm = $('#curSearchForm');
		var curPageForm = $('#curPageForm');
		location.href = '/BoardReEdit.do?'+curSearchForm.serialize()+'&'+curPageForm.serialize()+'&idx='+idx;
	});
};

ITSP.board.bindSaveLink = function() {
	var form = $('#fm');
	var doSave = function() {	
		if (!itsp.formValidator.validate(form)) {
			return;
		}
		itsp.ajax.showLoading();
		if($("#contents").length) {
			itsp.com.getHtmlEditorData('contents');
		}
		itsp.ajax.doPostFormJSON(form, function(data) {			
			if (data.header.code == itsp.ajax.CODE_SUCCESS) {
				ITSP.board.goList();
			} else {
				alert(data.header.message);
			}
		});
	};
	
	itsp.com.blockFormEnterKey(form, function() {
		// doSave();
	});
	
	$('[data-itsp-save-link]').click(function(event) {
		doSave();
	});
};

ITSP.board.bindReplySaveLink = function() {
	var form = $('#fm');
	var doReplySave = function() {	
		if($("#content").length) {
			itsp.com.getHtmlEditorData('content');
			
		}
		itsp.ajax.doPostFormJSON(form, function(data) {
			if (data.header.code == itsp.ajax.CODE_SUCCESS) {
				location.reload();
			} else {
				alert(data.header.message);
			}
		});
	};
	
	itsp.com.blockFormEnterKey(form, function() {
		// doSave();
	});
	
	$('[data-itsp-reply-link]').click(function(event) {
		doReplySave();
	});
};


ITSP.board.bindDeleteLink = function() {
	$('[data-itsp-delete-link]').click(function(event) {
		var me = $(this);
		var idx = me.attr('data-itsp-delete-link');
		var secret = me.attr('data-itsp-secret');
		
		if("Y" == secret){
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').addClass('on');
			
			$('.modal_popup_wrap button').click(function(event) {
				var pwd = $('.modal_popup_wrap input[name=password] ').val();
				if("" == pwd){
					alert("비밀번호가 입력되지 않았습니다.");
					return false;
				}
				itsp.ajax.doPostJSON('/Board/checkPasswordAuthentication', { idx : idx, password : pwd },  function(data) {
					if (data.header.code == itsp.ajax.CODE_SUCCESS) {
						if (!confirm("삭제 하시겠습니까? 삭제 후 복구가 불가능합니다.")) {
							return;
						}		
						
						itsp.ajax.doPostJSON('/Board/dataDeleteProc', { idx : idx },  function(data) {
							if (data.header.code == itsp.ajax.CODE_SUCCESS) {
								ITSP.board.goList();
							} else {
								alert(data.header.message);
							}
						});
					} else {
						$('.modal_popup').removeClass('on');
						alert(data.header.message);
						return false;
					}
				});
			});
			
		}else{
			if (!confirm("삭제 하시겠습니까? 삭제 후 복구가 불가능합니다.")) {
				return;
			}		
			
			itsp.ajax.doPostJSON('/Board/dataDeleteProc', { idx : idx },  function(data) {
				if (data.header.code == itsp.ajax.CODE_SUCCESS) {
					ITSP.board.goList();
				} else {
					alert(data.header.message);
				}
			});
		}
		$('.modal_popup_wrap .bt_close').click(function(event) {
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').removeClass('on');
		});	
	});
	
	$('[data-itsp-delGb-link]').click(function(event) {
		var me = $(this);
		var idx = me.attr('data-itsp-delGb-link');
		var delGb = me.attr('data-itsp-delGb');
		var secret = me.attr('data-itsp-secret');
		
		if("Y" == secret){
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').addClass('on');
			
			$('.modal_popup_wrap button').click(function(event) {
				var pwd = $('.modal_popup_wrap input[name=password] ').val();
				if("" == pwd){
					alert("비밀번호가 입력되지 않았습니다.");
					return false;
				}
				itsp.ajax.doPostJSON('/Board/checkPasswordAuthentication', { idx : idx, password : pwd },  function(data) {
					if (data.header.code == itsp.ajax.CODE_SUCCESS) {
						if (!confirm("삭제 하시겠습니까?")) {
							return;
						}		
						
						itsp.ajax.doPostJSON('/Board/dataDelGBUpdateProc', { idx : idx, delGb : delGb },  function(data) {
							if (data.header.code == itsp.ajax.CODE_SUCCESS) {
								ITSP.board.goList();
							} else {
								alert(data.header.message);
								// 화면 이동 없음
							}
						});
					} else {
						$('.modal_popup').removeClass('on');
						alert(data.header.message);
						return false;
					}
				});
			});
			
		}else{
			if (!confirm("삭제 하시겠습니까?")) {
				return;
			}		
			
			itsp.ajax.doPostJSON('/Board/dataDelGBUpdateProc', { idx : idx, delGb : delGb },  function(data) {
				if (data.header.code == itsp.ajax.CODE_SUCCESS) {
					ITSP.board.goList();
				} else {
					alert(data.header.message);
					// 화면 이동 없음
				}
			});
		}
		$('.modal_popup_wrap .bt_close').click(function(event) {
			$('.modal_popup_wrap input[name=password] ').val('');
			$('.modal_popup').removeClass('on');
		});	
		
	});
};
ITSP.board.bindNewSearchLink = function() {
	$('#searchBy').change(function(event){
		$('#curSearchForm input[name=searchBy]').attr('value', $('#searchBy').val());
	});
	
	$('[data-itsp-new-search-link]').click(function(event) {
		if (!itsp.formValidator.validate($('#newSearchForm'))) {
			return;
		}
		
		$('#curSearchForm input[name=searchValue]').attr('value', $('#searchValue').val());
		ITSP.board.goList();
	});
};

ITSP.board.bindPageLink = function() {
	$('[data-itsp-page-link]').click(function(event) {
		var me = $(this);
		var pageNum = me.attr('data-itsp-page-link');
		$('input[name=pageNum]').attr('value', pageNum);
		ITSP.board.goList();
	});
};

ITSP.board.bindFilePlus = function() {
	$("[data-itsp-fileAdd]").on("click", function() {
		var fileIndex = $('[id^=file_]').length+1; //현제 파일 개수
		var fileCnt = $('#fileCnt').val(); 	// 설정 파일개수
	
		if (fileIndex > fileCnt) {			
			alert("더 이상 추가할 수 없습니다.");
			return;
		}
		
		var html = '';
		html +=	'<li class="add_field" id="file'+ fileIndex +'">';
		html +=	'	<input type="file" name="file'+ fileIndex +'" id="file_'+ fileIndex +'" class="txt_field">';
		html +=	'	<input type="text" name="fileComment_'+fileIndex+'" id="fileComment_'+fileIndex+'" placeholder="첨부파일 설명글 또는 파일명" class="alt_txt">';
		html +=	'	<ul class="add_edit">';
		html +=	'		<li><a href="javascript:;" class="bt bt_inner" data-itsp-fileDel>삭제</a></li>';
		html +=	'	</ul>';
		html +=	'</li>';
		
		$('#fileList').append(html);		
	});
};

ITSP.board.bindFileMinus = function() {
	$("#fileList").on("click", "[data-itsp-fileDel]", function(e) {
		var me = $(this);
		me.parents('li[class=add_field]').remove();
		e.preventDefault();
	});
};

ITSP.board.bindFileReset = function() {
	$("#fileList").on("click", "[data-itsp-fileReplace]", function() {
		var agent = navigator.userAgent.toLowerCase();
		var me = $(this);
		var fileObj = $('#file_'+me.attr('data-itsp-fileReplace'));
		var fileObj2 = $('#fileComment_'+me.attr('data-itsp-fileReplace'));
		
		if (agent.indexOf("msie") != -1) {			
			fileObj.replaceWith(fileObj.clone(true) ); 
			fileObj2.replaceWith(fileObj2.clone(true) ); 
		} else { 
			fileObj.val(""); 
			fileObj2.val(""); 
		};
	//fileObj.replaceWith(fileObj.clone(true));
	});
};

$(document).on("click", "[data-itsp-comment-submit]", function() {
	var me = $(this);
	var data = {};
	var recordIdx =  me.attr('data-itsp-comment-submit');
	data.recordIdx = recordIdx;
	data.content = $('#content').val();
	
	if(data.content == ''){
		alert("내용은(는) 필수항목입니다.");
		$('#content').focus();
		return;
	}
	
	itsp.ajax.doPostJSON('/Board/CommentSaveProc', data, function(data) {
		if (data.header.code == itsp.ajax.CODE_SUCCESS) {
			itsp.ajax.doPostJSON('/Board/CommentSelectList', {recordIdx : recordIdx}, function(data) {
				var commentList = data.body;
				var commentListObj = $('#ajaxCommentList');
				commentListAjax(commentList, commentListObj);
			});
		} else {
			alert(data.header.message);
		}
	});
	$('#content').val('');
});

$(document).on("click", "[data-itsp-comment-delete]", function() {
	if (!confirm("삭제 하시겠습니까?")) {
		return;
	}
	var me = $(this);
	var idx = me.attr('data-itsp-comment-delete');
	var recordIdx = me.attr('data-itsp-recordIdx');
	itsp.ajax.doPostJSON('/Board/CommentDeleteProc', { idx : idx }, function(data) {
		if (data.header.code == itsp.ajax.CODE_SUCCESS) {
			itsp.ajax.doPostJSON('/Board/CommentSelectList', {recordIdx : recordIdx}, function(data) {
				var commentList = data.body;
				var commentListObj = $('#ajaxCommentList');
				commentListAjax(commentList, commentListObj);
			});
		} else {
			alert(data.header.message);
		}
	});
	$('#content').val('');
});

$(document).on("click", "[data-itsp-comment-modify]", function() {
	var me = $(this);
	var idx = me.attr('data-itsp-comment-modify');
		
	if ($('#comment_box_'+idx).css("display") == "none"){
		$('#comment_box_'+idx).show();
		$('#comment_cont_'+idx).hide();
		$('#modify_'+idx).html("취소");
	}else{
		$('#comment_box_'+idx).hide();
		$('#comment_cont_'+idx).show();
		$('#modify_'+idx).html("수정");
	}
});

$(document).on("click", "[data-itsp-comment-update]", function() {
	var me = $(this);
	var idx = me.attr('data-itsp-comment-update');
	var recordIdx = me.attr('data-itsp-recordIdx');
	
	var data = {};
	data.idx = idx;
	data.recordIdx = recordIdx;
	data.content = $('#content_'+idx).val();
	
	itsp.ajax.doPostJSON('/Board/CommentSaveProc', data, function(data) {
		if (data.header.code == itsp.ajax.CODE_SUCCESS) {
			itsp.ajax.doPostJSON('/Board/CommentSelectList', {recordIdx : recordIdx}, function(data) {
				var commentList = data.body;
				var commentListObj = $('#ajaxCommentList');
				commentListAjax(commentList, commentListObj);
			});
		} else {
			alert(data.header.message);
		}
	});
	$('#content').val('');
});

var commentListAjax = function(commentList, commentListObj) {
	$('#commentCnt').html("["+commentList.length+"]");
	commentListObj.empty();
	for (var inx=0; inx<commentList.length; inx++) {
		var commentInfo = commentList[inx];
		var html = '';
		html += '	<div class="comment_item">';
		html += '		<div class="write_info">';
		html += '			<strong class="write_name">'+ commentInfo.regName+'</strong>';
		html += '			<span class="write_date">'+ commentInfo.regDateFmt+'</span>';
		html += '		</div>';
		html += '		<c:if test="${sessionScopeMember.user_id eq + "' + commentInfo.regId + '"}">';
		html += '			<ul class="write_edit">';
		html += '				<li><a href="javascript:;" class="on" data-itsp-comment-modify="' + commentInfo.idx + '"><span id="modify_' + commentInfo.idx + '">수정</span></a></li>';
		html += '				<li><a href="javascript:;" data-itsp-comment-delete="' + commentInfo.idx + '" data-itsp-recordIdx="' + commentInfo.recordIdx + '">삭제</a></li>';
		html += '			</ul>';
		html += '		</c:if>';
		html += '		<div class="write_subject">' + commentInfo.content + '</div>';
		html += '		<div class="message_write_comment" style="display: none;" id="comment_box_' + commentInfo.idx + '">';
		html += '			<div class="write_main">';
		html += '				<div class="write_text">';
		html += '					<textarea class="input_write_text" cols="30" rows="3" placeholder="댓글을 입력해주세요." id="content_' + commentInfo.idx + '">' + commentInfo.content + '</textarea>';
		html += '				</div>';
		html += '				<div class="bt_list">';
		html += '					<ul>';
		html += '						<li><label for="" class="blind">수정</label><button type="button" name="" id="" class="bt bt_black" data-itsp-comment-update="' + commentInfo.idx + '" data-itsp-recordIdx="' + commentInfo.recordIdx + '">수정</button></li>';
		html += '					</ul>';
		html += '				</div>';
		html += '			</div>';
		html += '		</div>';
		html += '	</div>';
		commentListObj.append(html);
	};
};

var appLoading = function() {
	ITSP.board.bindCaptcha();
	ITSP.board.bindSaveLink();
	ITSP.board.bindEditLink();
	ITSP.board.bindViewLink();
	ITSP.board.bindListLink();
	ITSP.board.bindDeleteLink();
	ITSP.board.bindNewSearchLink();
	ITSP.board.bindPageLink();
	
	ITSP.board.bindFilePlus();
	ITSP.board.bindFileMinus();
	ITSP.board.bindFileReset();
	
	ITSP.board.bindReplySaveLink();
};