//版本工单详情页面中查看详情功能按钮
$(document).ready(function () {
    // 通过该方法来为每次弹出的模态框设置最新的zIndex值，从而使最新的modal显示在最前面
    $(document).on('show.bs.modal', '.modal', function () {
        var zIndex = 1040 + (10 * $('.modal:visible').length);
        $(this).css('z-index', zIndex);
        setTimeout(function () {
            $('.modal-backdrop').not('.modal-stack').css('z-index', zIndex - 1).addClass('modal-stack');
        }, 0);
    });

    //找到按钮后做遍历（按钮class为rev_detail，不能用id）
    $(".rev_detail").each(function () {
        $(this).click(function () {
            var detail_id=$(this).closest("tr").prev().val();
            // console.log(detail_id);
            //将当前this保存到变量_this
            var _this=$(this);
            $.ajax({
                url:"/resdetail/",
                type:"post",
                dataType:"json",
                data:{"detail_id":detail_id},
                complete: function (XMLHttpRequest, textStatus) {
                },
                success: function (data) {
                    data=data.detailContent;
                    // console.log("data "+data);
                    if (data ===""){
                        // alert("自动审核未成功，请检查脚本!");
                        $('#wrongpwd-modal-body').html("自动审核未成功，请检查脚本！");
                        $('#wrongpwd-modal').modal({
                            keyboard: false, backdrop: 'static'
                        });
                    }
                    else{
                        var $tbody=(_this).parent().parent().next().find("td table");
                        var $tbody1=(_this).parent().parent().next().find("td table tbody tr");
                        $tbody1.empty();
                        for(var i=0;i<data.length;i++){
                            var s_id = data[i][0];
                            var sql = data[i][5].replace(/\n/g,'<br>');
                            var suggest = data[i][4].replace(/\n/g,'<br>');
                            var affect_row = data[i][6];
                            var exe_time = data[i][9];
                            var exe_status = data[i][3];
                            auditHtml="<tr><td>" + s_id +"</td>><td style='word-wrap:break-word;'>" + sql + "</td> <td>" + suggest + "</td><td>"+affect_row+"</td><td>"+exe_time+"</td><td>"+exe_status+"</td></tr>";
                            $tbody.append(auditHtml);
                            }
                            //判断是否收缩与改变按钮文字
                            // console.log(_this);
                            // console.log((_this).text());
                            var $p_tog = (_this).parent().parent().next();
                            $p_tog.toggle();

                            if(!$p_tog.is(":hidden")){
                                (_this).text("收起")
                            }else{
                                (_this).text("查看详情");
                            }
                        }
                },
                error: function(XMLHttpRequest, textStatus,errorThrown) {
                    alert(XMLHttpRequest.status + "服务器错误！");
                    // alert(errorThrown);
                }
            })
        });

    })
});

//自动审核按钮事件
$(".rel_autoreview").each(function () {
    $(this).click(function () {
        var detail_id = $(this).closest("tr").prev().val();
        var rel_file = $(this).closest("tr").prev().prev().val();
        var _this = $(this);
        //获取工单详情中工单的执行状态
        $.ajax({
            url: "/getrelstatus/",
            type: "post",
            dataType: "json",
            data: {"recordid": detail_id},
            success: function (data) {
                if (data.detailObj === '执行中' || data.detailObj === '已正常结束') {
                    $('#wrongpwd-modal-body').html('工单当前状态：' + data.detailObj);
                    $('#wrongpwd-modal').modal({
                        keyboard: false, backdrop: 'static'
                    });
                    $('#wrongpwd-modal').on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })

                } else {
                    commit_file(_this, detail_id, rel_file);
                }
            }
        })
    })
});

//提交版本文件与id给后台读取文件
function commit_file(_this,detail_id,rel_file) {
    $.ajax({
        type: "post",
        url: "/relautoreview/",
        dataType: "json",
        // async: "false",
        data: {
            "detail_id": detail_id,
            "rel_file": rel_file
        },
        complete: function () {
        },
        success: function (data) {
            // console.log(data);
            // console.log($.parseJSON(data));
            if (data.status === 0) {
                // console.log(data.record_status);
                // alert(data.msg);
                //$('#wrongpwd-modal-body').html(data.msg);
                $('#wrongpwd-modal-body').html("<span style='font-size: 17px;font-weight: 700;display:block;text-align: center;color: darkgreen'>" + data.msg + "</span><br><span style='font-size: 17px;font-weight: 700;color: red;'> <li>若非最新提交的SQL内容，可能svn还未同步，4分钟再点击自动审核！</li><li>若再次自动审核仍为旧内容，请联系DBA处理，无需重复提交工单!</li><li>若自审不通过，</span><span>请自行查看详情依提示修改svn文件内容，无需重复提交工单!</li></span>")
                $('#wrongpwd-modal').modal({
                    keyboard: false, backdrop: 'static'
                });

                finishEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").text(data.record_status);
                parentEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").css({
                    'font-weight': 700,
                    'color': 'red'
                });
                $('#wrongpwd-modal').on('hidden.bs.modal', function () {
                    window.location.reload(true);
                });

            } else {
                if (data.status !== undefined) {
                    // alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
                    $('#wrongpwd-modal-body').html(data.msg + data.data);
                    $('#wrongpwd-modal').modal({
                        keyboard: false, backdrop: 'static'
                    });
                    finishEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").text(data.record_status);
                    parentEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").css({
                        'font-weight': 700,
                        'color': 'red'
                    });
                    // window.location.reload(true);
                    $('#wrongpwd-modal').on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })
                } else {
                    alert("表或字段已经存在!");
                    finishEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").text(data.autoaudit_status);
                    parentEle = (_this).parents().find("input[value='" + detail_id + "'] + tr[class='lei']").find("td:eq(5)").css({
                        'font-weight': 700,
                        'color': 'red'
                    });
                    window.location.reload(true);

                }
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    })
}

//版本sql工单详情中每个脚本的执行按钮
$(".audit_ok").each(function () {
    $(this).click(function () {
        var execute_id=$(this).prev().val();
        var _this=$(this);
        $(this).closest("td").find("form").hide();
        $(this).closest("tr").prev().find("td:last button").hide();
        // $("#review_" + execute_id).hide();
        finishEle=$(this).parents().find("input[value='"+execute_id+"'] + tr[class='lei']").find("td:eq(5)").text("执行中");
        parentEle=$(this).parents().find("input[value='"+execute_id+"'] + tr[class='lei']").find("td:eq(5)").css({
            'font-weight':700,
            'color':'red'
        });

        $.ajax({
            url:"/relsexecute/",
            type:"post",
            dataType:"json",
            data:{"execute_id":execute_id},
            success:function (data) {
                exe_stat=data.finalList;
                // console.log(exe_stat);
                $.each(exe_stat,function (idx,domEle) {
                    _this.closest("form").prev().find("tbody tr:eq("+idx+") td:last").text(exe_stat[idx][3]);
                    // console.log(idx);
                });
                parentEle=(_this).parents().find("input[value='"+execute_id+"'] + tr[class='lei']").find("td:eq(4)").text(data.finish_time);
                finishEle=(_this).parents().find("input[value='"+execute_id+"'] + tr[class='lei']").find("td:eq(5)").text(data.finalStatus);
                parentEle=(_this).parents().find("input[value='"+execute_id+"'] + tr[class='lei']").find("td:eq(5)").css({
                    'font-weight':700,
                    'color':'green'
                });

            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown);
            }

        })
    })

});

//版本sql工单详情中每个脚本记录后的终止执行按钮
$(".audit_failed").each(function () {
    $(this).click(function () {
         var recordid=$(this).prev().val();
         var _this=$(this);
         $(this).closest("td").find("form").hide();
         $(this).closest("tr").prev().find("td:last button").hide();
         // $("#review_" + execute_id).hide();
         $.ajax({
            url:"/relstop/",
            type:"post",
            dataType:"json",
            data:{"recordid":recordid},
            success: function (data) {
                finishEle=(_this).parents().find("input[value='"+recordid+"'] + tr[class='lei']").find("td:eq(5)").text(data.finish_time);
                stateEle=(_this).parents().find("input[value='"+recordid+"'] + tr[class='lei']").find("td:eq(5)").text(data.status);
                stateEle_color=(_this).parents().find("input[value='"+recordid+"'] + tr[class='lei']").find("td:eq(5)").css({
                    'font-weight':700,
                    'color':'red'
                });
                // _this.parent().parent().find("form").hide();
                // _this.closest("td").find("form").hide();
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                console.log(errorThrown);
            }

        })

    })

});

//点击版本sql工单详情中修改备注按钮后获取dba备注内容
function get_dbamemo(rsid) {
    $.ajax({
        url: "/dbamemo/",
        type: "post",
        dataType: "json",
        data: {"rsid": rsid},
        success: function (data) {
            dba_memo=data.dba_memo;
            $("#remark").val(dba_memo);
        }
    });
}

//点击版本sql工单详情中修改备注按钮后提交新的dba备注内容
// 添加入库操作
function add_memo(rsid)
{
    // var form_data = $("#form_data").serialize();
    var form_data = $("#remark").val();
    $.ajax({
        type: "post",
        url: "/memosave/",
        dataType: "json",
        data: {
            "form_data":form_data,
            "rsid": rsid
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {

            $("#remark").val(data.new_memo);
            $("#dbamemo").val(data.new_memo);
        }
    })

}
//上线其他环境获取源信息
function other_rel(rsid) {
    var $rsid=rsid;
    var $rel_name=$("#workrelname").text();
    $("#relname").val($rel_name);

    var $loguser = $("#bs-example-navbar-collapse-1").find("a:first").text().split("：")[1];
    $("#subuser").val($loguser);

    $.ajax({
        type: "post",
        url: "/getrelinfo/",
        dataType: "json",
        data: {
            "rel_name":$rel_name,
            "rsid": $rsid,
            "suser": $loguser
        },
        // headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            var sql_files=data.old_detailrec.join("<br>");
            $("#sqlfile").html(sql_files);
            $("#memo_id").val(data.old_memo);
            var masters=data.masters;
            // var o_options=$("#o_envirment");在使用select标签，请老老实实使用document.getElementById(),原来用$（"|#id").options[] 老是说得不到object，
            var o_options=document.getElementById("o_envirment");
            var cluster_len = masters.length;
			if (masters) {
				for (var i = 0; i < cluster_len; i++) {
					o_options.options[i+1] = new Option();
					o_options.options[i+1].text = masters[i];
					o_options.options[i+1].value = masters[i];
				}
			}
        }
    })
}

//上线其他环境提交函数
function deploy_other(rsid) {
    var $rsid = rsid;
    var $rel_name = $("#relname").val();
    var $env = $("#o_envirment").val();
    var $memo = $("#memo_id").val();
    if ($env === null) {
        alert("请选择发布环境！");
    } else {
        $.ajax({
            type: "post",
            url: "/relother/",
            dataType: "json",
            data: {
                "rel_name": $rel_name,
                "rsid": $rsid,
                "env": $env,
                "memo": $memo
            },
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                status = data.stat;
                alert(status);
            }
        })
    }
}