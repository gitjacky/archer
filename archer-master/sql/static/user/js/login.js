<!-- 解决CSRF-->
$(function () {
	$.ajaxSetup({
		headers: {"X-CSRFToken": getCookie("csrftoken")}
	});
});

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

<!-- 退出登录后清空sessionStorage -->
$(document).ready(function () {
	sessionStorage.clear();
});

//回车键提交表单登录
$(document).ready(function() {
	$(document).keydown(function(event) {
		//keycode==13为回车键
		if (event.keyCode == 13) {
			$('#btnLogin').addClass('disabled');
			$('#btnLogin').prop('disabled', true);
			authenticateUser();
		}
	});
});

$('#btnLogin').click(function(){
	$('#btnLogin').addClass('disabled');
	$('#btnLogin').prop('disabled', true);
	authenticateUser();
});

function authenticateUser() {
	var inputUsername = $('#inputUsername');
	var inputPassword = $('#inputPassword');
    $.ajax({
        type: "post",
        url: "/authenticate/",
        dataType: "json",
        data: {
			username: inputUsername.val(),
            password: inputPassword.val()
        },
        complete: function () {
			$('#btnLogin').removeClass('disabled');
			$('#btnLogin').prop('disabled', false);
        },
        success: function (data) {
			if (data.status == 0) {
				$(location).attr('href','/allworkflow/');
			} else {
				$('#wrongpwd-modal-body').html(data.msg);
				$('#wrongpwd-modal').modal({
        			keyboard: true
    			});
			}
		},
		error: function (XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
        }
    });
};
