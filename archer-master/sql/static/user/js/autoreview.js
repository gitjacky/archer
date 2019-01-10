function validate() {
	var result = true;
	var sqlContent = editor.getValue();
	var clusterName = $("#cluster_name").val();
	if (sqlContent === null || sqlContent.trim() === "" || sqlContent === $("#sql_content").attr("placeholder")) {
		// alert("SQL内容不能为空！");
        $('#wrongpwd-modal-body').html("SQL内容不能为空！");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
		return result = false;
	} else if (clusterName === null || clusterName === $("#cluster_name").attr("data-placeholder")) {
		// alert("请选择要上线的环境！");
        $('#wrongpwd-modal-body').html("请选择要上线的环境！");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
		return result = false;
	}
	return result;
}


$("#btn-autoreview").click(function(){
	//先做表单验证，成功了提交ajax给后端
	var $btn=$('#btn-autoreview');
	if (validate()) {
		$btn.addClass('disabled');
	    $btn.prop('disabled', true);
		autoreview();
	}
	else{
		$btn.removeClass('disabled');
	    $btn.addClass('btn');
	    $btn.prop('disabled', false);
	}
});

function autoreview() {
	var sqlContent = editor.getValue();
	var clusterName = $("#cluster_name");
	
	//将数据通过ajax提交给后端进行检查
	$.ajax({
		type: "post",
		url: "/simplecheck/",
		dataType: "json",
		data: {
			sql_content: sqlContent,
			cluster_name: clusterName.val()
		},
		complete: function() {
			var $ipt=$('input[type=button]');
		    $ipt.removeClass('disabled');
		    $ipt.addClass('btn');
		    $ipt.prop('disabled', false);
		},
		success: function (data) {
			if (data.status === 0) {
				//console.log(data.data);
				var result = data.data;
				var finalHtml = "";
				for (var i=0; i<result.length; i++) {
					//索引5是SQL，4是审核建议
					var sql = result[i][5].replace(/\n/g,'<br>');
					var suggest = result[i][4].replace(/\n/g,'<br>');
					alertStyle = "alert-success";
					if (result[i][4] !== "None") {
						alertStyle = "alert-danger";
					}
					finalHtml += "<div class='alert alert-dismissable " + alertStyle + "'> <button type='button' class='close' data-dismiss='alert' aria-hidden='true'>x</button> <table class='' width='100%' style='table-layout:fixed;'><tr> <td width='80%' style='word-wrap:break-word;'>" + sql + "</td> <td><strong>自动审核结果：</strong>" + suggest + "</td> </tr> </table> </div>";
				}

				$("#inception-result-col").html(finalHtml);
				//填充内容后展现出来
				$("#inception-result").show();
			} else {
                $('#wrongpwd-modal-body').html(data.msg + data.data);
                $('#wrongpwd-modal').modal({
                    keyboard: false, backdrop: 'static'
                });
			}
		},
		error: function(XMLHttpRequest, textStatus, errorThrown) {
			alert(errorThrown);
		}
	});	

}
