/**
 * Created by Jacky.lau on 5/6/2019.
 */

//获取源数据库名称
$("#instance_name").change(function () {
    //将数据通过ajax提交给获取db_name
    var $instance_name=$("#instance_name").find("option:selected").text();
    var $instance_dbname=$("#instance_dbname");
    $.ajax({
        type: "post",
        url: "/archsync/dbnamelist/",
        dataType: "json",
        data: {
            "instance_name": $instance_name
        },
        complete: function (XMLHttpRequest,textStatus) {
           console.log(XMLHttpRequest+textStatus);
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            if (data.status === 0) {
                var result = data.data;

                $instance_dbname.empty();
                for (var i = 0; i < result.length; i++) {
                    var name = "<option>" + result[i] + "</option>";
                    $instance_dbname.append(name);
                }
                $instance_dbname.prepend("<option value=\"all\">全部</option>");
                $instance_dbname.prepend("<option value=\"is-empty\" disabled=\"\" selected=\"selected\">请选择源数据库:</option>");
                $instance_dbname.selectpicker('render');
                $instance_dbname.selectpicker('refresh');
            } else {
                alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown+"\n"+"status: "+XMLHttpRequest.status+"\n"+"readyState: "+XMLHttpRequest.readyState+"\n"+"textStatus: "+textStatus);
        }
    });
});

//获取目标数据库名称
$("#target_instance_name").change(function () {
    var $target_dbname=$("#target_instance_dbname");
    //将数据通过ajax提交给获取db_name
    $.ajax({
        type: "post",
        url: "/archsync/dbnamelist/",
        dataType: "json",
        data: {
            "instance_name": $("#target_instance_name").find("option:selected").text()
        },
        complete: function () {
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            if (data.status === 0) {
                var result = data.data;
                $target_dbname.empty();
                for (var i = 0; i < result.length; i++) {
                    var name = "<option>" + result[i] + "</option>";
                    $target_dbname.append(name);
                }
                $target_dbname.prepend("<option value=\"all\">全部</option>");
                $target_dbname.prepend("<option value=\"is-empty\" disabled=\"\" selected=\"selected\">请选择目标数据库:</option>");
                $target_dbname.selectpicker('render');
                $target_dbname.selectpicker('refresh');
            } else {
                alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
});
// 执行对比
function schemasync() {
    var $wrongbody = $('#wrongpwd-modal-body');
    var $wrongmodal = $('#wrongpwd-modal');
    var instance_name = $('#instance_name').val();
    var instance_dbname = $('#instance_dbname').val();
    var target_instance_name = $('#target_instance_name').val();
    var target_instance_dbname = $('#target_instance_dbname').val();
    var $schemasync=$('#btn-SchemaSync');

    if (instance_name && instance_dbname && target_instance_name && target_instance_dbname) {
        $schemasync.addClass('disabled');
        $schemasync.prop('disabled', true);
        $("#schemadiff-result").hide();
        $wrongbody.html("<span style='font-size: 17px;font-weight: 700;display:block;text-align: center;color: darkgreen'>请耐心等待对比结果，可在对应目录获取生成的SQL文件!</span>");
        $wrongmodal.modal({
            keyboard: false, backdrop: 'static'
        });
        $.ajax({
            type: "post",
            url: "/archsync/schemasync/",
            dataType: "json",
            data: {
                instance_name: instance_name,
                db_name: instance_dbname,
                target_instance_name: target_instance_name,
                target_db_name: target_instance_dbname,
                sync_auto_inc: document.getElementById("sync-auto-inc").checked,
                sync_comments: document.getElementById("sync-comments").checked
            },
            complete: function () {
                $schemasync.removeClass('disabled');
                $schemasync.prop('disabled', false);
            },
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                var result = data.data;
                if (data.status === 0) {
                    var diff_stdout = result['diff_stdout'].replace(/\n/g, '<br>');
                    var patch_stdout = result['patch_stdout'].replace(/\n/g, '<br>');
                    var revert_stdout = result['revert_stdout'].replace(/\n/g, '<br>');
                    alertStyle = "alert-success";
                    finalHtml = "<table class='table' width='100%' style='table-layout:fixed;'> " +
                        "<thead><tr><th>对比LOG：</th></tr></thead>" +
                        "</table>";
                    finalHtml += "<div class='alert alert-dismissable " + alertStyle + "'> " +
                        "<table class='' width='100%' style='table-layout:fixed;'> " +
                        "<tbody><tr>" +
                        "<td>" + diff_stdout + "</td>" +
                        "</tr> </tbody></table> </div>";
                    finalHtml += "<table class='table' width='100%' style='table-layout:fixed;'> " +
                        "<thead><tr><th>PATCH Script：</th></tr></thead>" +
                        "</table>";
                    finalHtml += "<div class='alert alert-dismissable " + alertStyle + "'> " +
                        "<table class='' width='100%' style='table-layout:fixed;'> " +
                        "<tbody><tr>" +
                        "<td>" + patch_stdout + "</td>" +
                        "</tr> </tbody></table> </div>";
                    finalHtml += "<table class='table' width='100%' style='table-layout:fixed;'> " +
                        "<thead><tr><th>REVERT Script：</th></tr></thead>" +
                        "</table>";
                    finalHtml += "<div class='alert alert-dismissable " + alertStyle + "'> " +
                        "<table class='' width='100%' style='table-layout:fixed;'> " +
                        "<tbody><tr>" +
                        "<td>" + revert_stdout + "</td>" +
                        "</tr> </tbody></table> </div>";
                    $("#schemadiff-result-col").html(finalHtml);
                    //填充内容后展现出来
                    $("#schemadiff-result").show();
                } else {
                    alert("status: " + data.status + "\nmsg: " + data.data);
                }
            },
            error: function (XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
    }
    else {
        $wrongbody.html("<span style='font-size: 17px;font-weight: 700;display:block;text-align: center;color: red'>请选择完整对比信息!</span>");
        $wrongmodal.modal({
            keyboard: false, backdrop: 'static'
        });
    }
}