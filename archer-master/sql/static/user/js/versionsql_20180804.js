//检查必输框是否为空
function validateForm(element) {
	var result = true;
	element.find('[required]').each(
		function () {
			var fieldElement = $(this);
			//如果为null则设置为''
			var value = fieldElement.val() || '';
			if (value) {
				value = value.trim();
			}
			if (!value || value === fieldElement.attr('data-placeholder')) {
				// alert((fieldElement.attr('data-name') || this.name) + "不能为空！");
				$('#wrongpwd-modal-body').html((fieldElement.attr('data-name') || this.name) + "不能为空！");
                $('#wrongpwd-modal').modal({
                    keyboard: false, backdrop: 'static'
                });
				result = false;
				return result;
			}
		}
	);
	return result;
};
// 默认选中哪个tab.这里指定默认选中第一个.
$('#mytab a:first').tab('show');

//提交按钮点击事件
$("#btn-versionsql").click(function () {
    //遍历每个checkbox,为每个checkbox添加点击事件
    var $workflow_name = $("#workflow_name").val();
    var $svn_path = $("#svn_path").find("option:selected").val();
    var $p_name = $("#p_name").find("option:selected").val();
    var $s_name = $("#s_name").find("option:selected").val();
    var $ver_name = $("#ver_name").val();
    if ($ver_name === '0'){
        $ver_name =null;
    };
    var $d_envirment = $("#d_envirment").find("option:selected").val();
    var $review_man = $("#review_man").find("option:selected").val();
    var $relmemo = ($("#memo_id").val()).trim();

    $(":checkbox").each(function () {
        // console.log($(this));
        $(this).click(function () {
            $(this).attr("checked", true);
            $(this).addClass('checked');
        });
    });

    //调用validateForm方法，获取form对象，判断输入，通过则提交
    var formSubmit = $("#form-versionsql");

    if (validateForm(formSubmit)) {
        var $wrongbody=$('#wrongpwd-modal-body');
        var $wrongmodal=$('#wrongpwd-modal');
        if ($("input:checked").length === $(":checkbox").length && $("input:checked").length !== 0) {
            selectAll();
        } else if ($("input:checked").length === 0) {
            // alert("请选择要提交的脚本！");
            $wrongbody.html("请选择要提交的脚本！");
            $wrongmodal.modal({
                keyboard: false, backdrop: 'static'
            });

            return false;
        } else {
            getChecked();
        };
        $.ajax({
            type: "post",
            url: "/versions/",
            dataType: "json",
            data: {
                "svn_path": $svn_path,
                "p_name": $p_name,
                "s_name": $s_name,
                "ver_name": $ver_name,
                "d_envirment": $d_envirment,
                "review_man": $review_man,
                "sql_list": $("#sql_list").val(),
                "workflow_name": $workflow_name,
                "relmemo": $relmemo
            },
            headers:{ "X-CSRFtoken":$.cookie("csrftoken")},
            success: function (data) {
                // alert(data.msg);
                $wrongbody.html("<span style='font-size: 17px;font-weight: 700;display:block;text-align: center;color: darkgreen'>"+data.msg+"</span><br><span style='font-size: 17px;font-weight: 700;color: red;display:block;text-align: center;'> 请点击'自动审核'按钮确认SQL是否有异常或是否是最新提交的SQL内容!</span>");
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                // window.location.reload(true);
                $wrongmodal.on('hidden.bs.modal',function(){
                    window.location.reload(true);
                })
            },
            error: function () {
                // alert('提交失败!');
                $wrongbody.html("提交失败！");
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                //点击模态框窗口的"确定"按钮后即隐藏，隐藏时触发窗口刷新操作。
                $wrongmodal.on('hidden.bs.modal',function(){
                    window.location.reload(true);
                })
            }
        });

    }
});


//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//全选
function selectAll(){
	$(":checkbox").each( function() {
		$(this).attr('checked', true);
		$(this).addClass('checked');
        var filelist={};
        var a ='';
        $(":checkbox:INPUT[checked='checked']").each(function(i){
            filelist[i]=$(this).closest('tr').find('td[name="sl_name"]').text();
            a+= filelist[i] + ',';
        });

        $("#sql_list").val(a.substring(0, a.length-1));
        console.log("filelist:"+$("#sql_list").val());
	});
	return $("#sql_list").val();
};

//获取被选中的checkbox
function getChecked() {
    var filelist={};
    var a ='';

    $(":checkbox:checked").each(function (i) {
        filelist[i]=$(this).closest('tr').find('td[name="sl_name"]').text();
        a+= filelist[i] + ',';
    });
    $("#sql_list").val(a.substring(0, a.length-1));
};

//取消全选
function unSelect(){
	$("INPUT[type='checkbox']").each( function() {
		$(this).attr('checked', false);
		$(this).removeClass('checked');
  });
};

// //点击#newsubmit后刷新下面的tab内容
// $("a[href='#newsubmit']").click(function () {
//     // window.location.reload(true);
//     $("#newsubmit").find("table tbody tr").empty();
// });


//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

//获取发布环境与审核人
function getdbsaudit() {
	var envElement = document.getElementById("d_envirment");
	var auditElement = document.getElementById("review_man");
	var $envs=$("#d_envirment");
	var $audit=$("#review_man");
	$.ajax({
		type: "GET",
		url: "/clusterandaudit/",
		dataType: "json",
		success: function (data) {

			// console.log(data.db_envs);
			//获取数据库连接信息并添加到执行环境下拉列表
			var clusterdbs = data.db_envs;
			var clusterdbs_len = clusterdbs.length;
			$envs.empty();
			$envs.prepend("<option value='发布环境' disabled='' selected='selected'>发布环境</option>");
			if (clusterdbs) {
				for (var i = 0; i < clusterdbs_len; i++) {
					// console.log(i);
					envElement.options[i+1] = new Option();
					envElement.options[i+1].text = clusterdbs[i];
					envElement.options[i+1].value = clusterdbs[i];
				}
				;
				// console.log(envElement);
			}
			;

			$audit.empty();
			$audit.prepend("<option value='选择审核人' disabled='' selected='selected'>选择审核人</option>");
			//获取审核人信息并添加到审核人下拉列表
			if (data.listAllReviewMen) {
				var listAllReviewMen = data.listAllReviewMen;
				var listAllReviewMen_len = listAllReviewMen.length;
				for (var i = 0; i < listAllReviewMen_len; i++) {
					auditElement.options[i+1] = new Option();
					auditElement.options[i+1].text = listAllReviewMen[i];
					auditElement.options[i+1].value = listAllReviewMen[i];
				}
				;
				// console.log(auditElement);
			}

		},
		error: function () {
			console.log('failed!')
		}
	});

};

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//由02目录获取父项目名列表
function p_getobj(){
    var base_svn = document.getElementById("svn_path");
    getdbsaudit();
    // console.log(base_svn.value);
    $.ajax({
        type:"GET",
        url:"/versioninfo/",
        async: "false",
        dataType: "json",
        data:{base_svn:base_svn.value},
        //success用来接收versionsql()函数执行之后的return HttpResponse返回值
        success:function(arg){
            // console.log(arg.pro_dir);
            var pro_dir=arg.pro_dir;
            var opSelect = document.getElementById("p_name");
            // $("#ver_name").empty();
            if(pro_dir.length > 0) {
                var len=pro_dir.length;

                for(var i=0;i<len;i++){
                    opSelect.options[i+1] = new Option();
                    opSelect.options[i+1].text = pro_dir[i];
                    opSelect.options[i+1].value = pro_dir[i];
                };
                // console.log(opSelect);
            }else {
                $("#s_name").hide();
                $("#ver_name").hide();
            }
        },
        error:function () {
            console.log('failed!')
        }

        });

};

//由父项目选项获取版本号目录文件列表;若由父项获取的目录列表不是版本目录，则为子项目目录
function s_getobj() {
   var base_svn = document.getElementById("svn_path").value;
   var opSelect = document.getElementById("p_name").value;
   var s_objElement = document.getElementById("s_name");
   var reSpaceCheck = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
   var reSpaceCheck_v = /^(\d+)\.(\d+)\.(\d+)\.(\d+)-uat-(\d+)$/;

   $.ajax({
       type: "GET",
       url: "/versioninfo/",
       dataType: "json",
       data: {
           base_svn: base_svn + '/' + opSelect
       },
       success: function (datas) {
           // console.log(datas);
           var pro_dir = datas.pro_dir;
           var $s_name=$("#s_name");
           var $ver_name=$("#ver_name");
           $s_name.empty();
           $s_name.prepend("<option value='子项目名' disabled='' selected='selected'>子项目名</option>");
           if (pro_dir.length > 0) {
               var len = pro_dir.length;
               for (var i = 0; i < len; i++) {
                   s_objElement.options[i+1] = new Option();
                   s_objElement.options[i+1].text = pro_dir[i];
                   s_objElement.options[i+1].value = pro_dir[i];
               };

           }//else
             //   $("#s_name").hide();
           if (reSpaceCheck.test(s_objElement.value) || reSpaceCheck_v.test(s_objElement.value)){
               $ver_name.hide();
               get_allfiles();
           }else{
               $ver_name.show();
               $ver_name.empty();
               $ver_name.prepend("<option value='0' disabled='' selected='selected'>版本号</option>");
               $("#table1 tbody").html("");
           }

       },
       error: function () {
           console.log('failed!')
       }

   });

};

//获取版本号列表
function sub_getobj() {
   var base_svn = document.getElementById("svn_path").value;
   var opSelect = document.getElementById("p_name").value;
   var s_objElement = document.getElementById("s_name").value;
   var sub_objElement = document.getElementById("ver_name");
   var reSpaceCheck = /^(\d+)\.(\d+)\.(\d+)\.(\d+)$/;
   var reSpaceCheck_v = /^(\d+)\.(\d+)\.(\d+)\.(\d+)-uat-(\d+)$/;
   $("#table1 tbody").html("");
   $.ajax({
       type: "GET",
       url: "/versioninfo/",
       dataType: "json",
       async: true,
       data: {
           base_svn: base_svn + '/' + opSelect + '/' + s_objElement
       },
       success: function (datas) {
           // console.log(datas);
           var pro_dir = datas.pro_dir;
           var $ver_name=$("#ver_name");
           $ver_name.show();
           $ver_name.empty();
           $ver_name.prepend("<option value='0' disabled='' selected='selected'>版本号</option>");
           if (!(reSpaceCheck.test(s_objElement))  && !(reSpaceCheck_v.test(s_objElement)) ) {
               var len = pro_dir.length;
               // $("#ver_name").show();
               for (var i = 0; i < len; i++) {
                   sub_objElement.options[i+1] = new Option();
                   sub_objElement.options[i+1].text = pro_dir[i];
                   sub_objElement.options[i+1].value = pro_dir[i];
               };

           }else {
               get_allfiles();
               $ver_name.hide();
           }
       },
       error: function () {
           console.log('failed!')
       }

   });

};

//定义带有子项目的版本号目录选项的触发事件，获取触发后的文件列表
function get_versionfile() {
   var base_svn = document.getElementById("svn_path").value;
   var opSelect = document.getElementById("p_name").value;
   var s_objElement = document.getElementById("s_name").value;
   var sub_objElement = document.getElementById("ver_name").value;
   $("#table1 tbody").html("");
    $.ajax({
        type: "GET",
        url:"/versioninfo/",
        dataType: "json",
        data:{base_svn: base_svn + '/' + opSelect + '/' + s_objElement + '/' + sub_objElement},
        success:function (args) {
            add_filelist(args);

        }

    });
};

//获取正常三级版本目录下所有.sql文件名
function get_allfiles() {
   var base_svn = document.getElementById("svn_path").value;
   var opSelect = document.getElementById("p_name").value;
   var s_objElement = document.getElementById("s_name").value;
   // var sub_objElement = document.getElementById("ver_name").value;
   $("#table1 tbody").html("");
   if (s_objElement !=="" || s_objElement !== null){
        $.ajax({
            type: "GET",
            url:"/versioninfo/",
            dataType: "json",
            data:{base_svn: base_svn + '/' + opSelect + '/' + s_objElement},
            success:function (args) {
                //添加tbody行与列
                add_filelist(args);
            }

        })
   }else{return false;}

};

//获取列表函数,用来获取版本号目录下的文件列表，只有s_name与sub_name
function add_filelist(doc) {
    var file_names=doc.pro_dir;
    var row_count=file_names.length;
    for (var i=0;i<row_count;i++){
        var table1 = $('#table1');
        var firstTr = table1.find('tbody>tr:first');
        var row = $("<tr></tr>");
        var td1 = $("<td>" + (i+1) + "</td>");
        var td2 = $("<td name='sl_name' colspan='2'>" + file_names[i] + "</td>");
        // var td3 = $("<td><button class='btn btn-info btn-xs' type='button' style='width: 60px;height: 25px;float: left;margin-right: 30px;' value='自动审核'>自动审核</button></td>");
        // var td4 = $("<td>成功</td>");

        var td5 = $("<td><lable><input type='checkbox' name='sf'></lable></td>");

        row.append(td1);
        row.append(td2);
        // row.append(td3);
        // row.append(td4);
        row.append(td5);
        // console.log(row);
        table1.append(row);
    }
};

//++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
//时间转换方法
function getFormatDate(nowDate){
		    var year = nowDate.getFullYear();
		    var month = nowDate.getMonth() + 1 < 10 ? "0" + (nowDate.getMonth() + 1) : nowDate.getMonth() + 1;
		    var date = nowDate.getDate() < 10 ? "0" + nowDate.getDate() : nowDate.getDate();
		    var hour = nowDate.getHours()< 10 ? "0" + nowDate.getHours() : nowDate.getHours();
		    var minute = nowDate.getMinutes()< 10 ? "0" + nowDate.getMinutes() : nowDate.getMinutes();
		    var second = nowDate.getSeconds()< 10 ? "0" + nowDate.getSeconds() : nowDate.getSeconds();
		    return year + "-" + month + "-" + date+" "+hour+":"+minute+":"+second;
		};

//获取所有版本工单
//  var id2 ;
$('#mytab a:last').click(function () {

	$.ajax({
		type: "POST",
		url: "/allrelease/",
		dataType: "json",
		data:{
		    "navStatus":"allrelease",
            "pageNo": "1"},
		success: function (data) {

            console.log(data);
			// var data=$.parseJSON(data['allWorkrel']);
            var allrows=data['all_count'];
            var role=data.role;
            var data=data['allWorkrel'];

            // console.log($().jquery);  //查看当前jquery版本
            var $mytbody=$("#myall tbody");
			$mytbody.empty();

			$.each(data, function (i) {
			    var rel_name=data[i].release_name;
			    var rel_path=data[i].release_path;
			    var submit_user=data[i].submit_user;
			    var audit_user=data[i].audit_user__username;
			    var execute_status=data[i].execute_status;
			    var submit_time=data[i].submit_time;
			    submit_time = getFormatDate(new Date(submit_time));
			    var deploy_env=data[i].deploy_env;

			    if (execute_status==="已正常结束"){
			        aa="<td style='width: 120px;color: green'>"+execute_status+"</td>";
                }else if(execute_status==="等待DBA审核"){
			        aa="<td style='width: 120px;color: steelblue'>"+execute_status+"</td>";
                }
                else{
			        aa="<td style='width: 120px;color: red'>"+execute_status+"</td>";
                };
                if(deploy_env.substring(0,3)==="BUG"){
                    var $dy_env="<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;color: blue;font-weight: bold' title='"+deploy_env+"'>"+deploy_env+"</td>";

                }else {
                    var $dy_env="<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;' title='" + deploy_env + "'>" + deploy_env + "</td>";

                };
                var $tr = $("<tr>"+
                "<td style='text-indent:12px;width: 60px;'>"+data[i]['id']+"</td>"+
                $dy_env+
                "<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;'><a title='"+rel_name+"' href='/relsdetail/"+data[i]['id']+"/'>"+rel_name+"</a></td>"+
                "<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;' title='"+rel_path+"'>"+rel_path+"</td>"+
                "<td>"+submit_user+"</td>"+
                "<td>"+submit_time+"</td>"+
                "<td style='width: 100px;'>"+audit_user+"</td>"+ aa +
                +"</tr>");

                $mytbody.append($tr);
                $("#myall tr:odd").css("background","#F8F8F8");
            });
            //返给前台页码信息
            var $butns=$("#btns");
            $butns.empty();
            var $butn_text=(pageBtns(1,15,allrows)).split(',');
            console.log($butn_text);
            var li_s="<li class='lis'><a href='javascript:void(0);'>上一页</a></li>";
            var li_e="<li class='lis'><a href='javascript:void(0);'>下一页</a></li>";
            // $butns.append(li_s);
            for(var i=0,len=$butn_text.length;i<len;i++){
                // if(i<=4){
                    var $li="<li class='lis'><a href='javascript:void(0);'>"+$butn_text[i]+"</a></li>";
                    $butns.append($li);
                // }else{};

            };
            // $butns.append(li_e);
            // id2 = $('#myall tr:last > td:eq(0)').text();
            // console.log(id2);
        },
        error: function(XMLHttpRequest, errorThrown) {
            alert(errorThrown);
        }
	})
});

//分页jquery,将获取点击的版本页面页码传到后台
$('#btns').on("click",".lis",function () {
    $(this).siblings().removeClass('active');
    $(this).addClass('active');
    console.log($(this).children())
    var $pageNo=$(this).text();
    var $butns=$("#btns");
    $butns.empty();
    $.ajax({
        type: "POST",
        url: "/allrelease/",
        dataType: "json",
        data:{
            "navStatus": "allrelease",
            "pageNo": $pageNo
        },
        success: function (data) {
            var allrows=data['all_count'];
            var $butn_text=(pageBtns($pageNo,15,allrows)).split(',');
            console.log($butn_text);
            for(var i=0,len=$butn_text.length;i<len;i++){
                // if(i<=5){
                    var $li="<li class='lis'><a href='javascript:void(0);'>"+$butn_text[i]+"</a></li>";
                    $butns.append($li);
                // }else{};

            };

            data=data.allWorkrel;
            if(data.length!==0){
                var $mytbody=$("#myall tbody");
                $mytbody.empty();
                $.each(data, function (i) {
                    var rel_name=data[i].release_name;
                    // console.log(rel_name);
                    var rel_path=data[i].release_path;
                    var submit_user=data[i].submit_user;
                    var audit_user=data[i].audit_user__username;
                    var execute_status=data[i].execute_status;
                    var submit_time=data[i].submit_time;
                    submit_time = getFormatDate(new Date(submit_time));
                    var deploy_env=data[i].deploy_env;

                    if (execute_status==="已正常结束"){
                        aa="<td style='width: 120px;color: green'>"+execute_status+"</td>";
                    }else if(execute_status==="等待DBA审核"){
                        aa="<td style='width: 120px;color: steelblue'>"+execute_status+"</td>";
                    }
                    else{
                        aa="<td style='width: 120px;color: red'>"+execute_status+"</td>";
                    };
                    if(deploy_env.substring(0,3)==="BUG"){
                        var $dy_env="<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;color: blue;font-weight: bold' title='"+deploy_env+"'>"+deploy_env+"</td>";

                    }else {
                        var $dy_env="<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;' title='" + deploy_env + "'>" + deploy_env + "</td>";

                    };
                    var $tr = $("<tr>"+
                    "<td style='text-indent:12px;width: 60px;'>"+data[i]['id']+"</td>"+
                    $dy_env+
                    "<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;'><a title='"+rel_name+"' href='/relsdetail/"+data[i]['id']+"/'>"+rel_name+"</a></td>"+
                    "<td style='white-space: nowrap;text-overflow: ellipsis;overflow: hidden;' title='"+rel_path+"'>"+rel_path+"</td>"+
                    "<td>"+submit_user+"</td>"+
                    "<td>"+submit_time+"</td>"+
                    "<td style='width: 100px;'>"+audit_user+"</td>"+ aa +
                    +"</tr>");

                    $mytbody.append($tr);
                    $("#myall tr:odd").css("background","#EEEEEE");
                });
            }else{
                    var $mytbody1=$("#myall tbody");
                    $mytbody1.empty();
                    $tr="<tr><td>无多余工单.</td></tr>";
                    $mytbody1.append($tr);

            }
        },
        error: function(XMLHttpRequest, errorThrown) {
        }
    });
});

function show_memo() {
    $("#tips").css('display','block');
};

function hide_memo(){
    $("#tips").css('display','none');
};

//传入“当前页码 每页容量 数据总条数”
//返回按钮上的文本内容，如：pageBtns(2,10,75) 返回："上一页,1,2,3,4,...,8,下一页" 以逗号分隔的字符串
function pageBtns(currentPageIndex,currentPageSize,dataCount){
    var cpIndex=parseInt(currentPageIndex);
    var pageSize=parseInt(currentPageSize);
    var count=parseInt(dataCount);
    var btnStr="";
    var pages=(count % pageSize)==0 ? (count/pageSize):Math.floor((count/pageSize+1));//总页数
    if(pages<=6){//如果小于6页 则显示全部页码按钮
        for(var i=1;i<=pages;i++){
            btnStr+=i+",";
        }
    }
    else{ //大于等于7页
        var a=[];
        if(cpIndex !=1)//位置0
        {
            a[0]="上一页";
        }
        else{
            a[0]="";
        }


        a[1]="1"; //位置1 首页


        if((cpIndex-2)>2){//位置2
            a[2]="...";
        }
        else{
            a[2]="";
        }


        if((cpIndex-2)>=2)//位置3
        {
            a[3]=cpIndex-2;
        }
        else{
            a[3]="";
        }


        if((cpIndex-1)>=2)//位置4
        {
            a[4]=cpIndex-1;
        }
        else{
            a[4]="";
        }


        //位置5
        if(cpIndex!=1 && cpIndex!=pages){
            a[5]=cpIndex;
        }
        else{
            a[5]="";
        }


        //位置6
        if((cpIndex+1)<pages)
        {
            a[6]=cpIndex+1;
        }else{
            a[6]="";
        }


        //位置7
        if((cpIndex+2)<pages)
        {
            a[7]=cpIndex+2;
        }
        else{
            a[7]="";
        }


        //位置8
        if((cpIndex+2+1)<pages){
            a[8]="...";
        }
        else{
            a[8]="";
        }


        //位置9
        a[9]=pages;


        //位置10
        if(cpIndex!=pages){
            a[10]="下一页";
        }
        else{
            a[10]="";
        }


        $.each(a,function(j){
            if(a[j]!="")
            {
            btnStr+=a[j]+",";
            }
        });
    }
    btnStr=btnStr.substring(0,btnStr.length-1);
    console.log(btnStr);
    return btnStr;
}