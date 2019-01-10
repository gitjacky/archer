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
                alert((fieldElement.attr('data-name') || this.name) + "不能为空！");
                result = false;
                return result;
            }
        }
    );
    return result;
}

$("#btn-submitsql").click(function () {
    //获取form对象，判断输入，通过则提交
    var formSubmit = $("#form-submitsql");
    var sqlContent = editor.getValue();
    $("#sql_content").val(sqlContent);

    if (validateForm(formSubmit)) {
        formSubmit.submit();
    }
});

$("#btn-reset").click(function () {
    editor.setValue("");
    //重置选择器
    $(".selectpicker").selectpicker('val', '');
    $(".selectpicker").selectpicker('render');
    $(".selectpicker").selectpicker('refresh');
});

$("#review_man").change(function review_man() {
    var review_man = $(this).val();
    $("div#" + review_man).hide();
});


//处理"重新修改"按钮，即工单被终止后再次进行修改使用，而不用再次重新输入。
$(document).ready(function () {
    var pathname = window.location.pathname;
    var $btn_submit = $("#btn-submitsql");
    if (pathname === "/submitsql/") {
        // 禁用提交按钮，点击检测后才激活
        editor.setValue("请在此提交SQL，并以分号结尾。例如：use `test`; create table t1(id int)engine=innodb;");
        editor.clearSelection();
        $btn_submit.addClass('disabled');
        $btn_submit.prop('disabled', true);
        $("#workflow_name").val(sessionStorage.getItem('editWorkflowNname'));
        $("#sql_content").val(sessionStorage.getItem('editSqlContent'));
        var editClusterName = sessionStorage.getItem('editClusterName');
        var editReviewMen = sessionStorage.getItem('editReviewMen');
        var editIsBackup = sessionStorage.getItem('editIsBackup');
    }
    else if (pathname === "/editsql/") {
        // 禁用提交按钮，点击检测后才激活
        editor.clearSelection();
        $btn_submit.addClass('disabled');
        $btn_submit.prop('disabled', true);
        $("#workflow_name").val(sessionStorage.getItem('editWorkflowNname'));
        $("#sql_content").val(sessionStorage.getItem('editSqlContent'));
        editor.setValue(sessionStorage.getItem('editSqlContent'));
        editClusterName = sessionStorage.getItem('editClusterName');
        editReviewMen = sessionStorage.getItem('editReviewMen');
        editIsBackup = sessionStorage.getItem('editIsBackup');
    }
    //根据select的显示值来为select设值
    //设置执行环境
    var count = $("#cluster_name").find('option').length;

    for (var i = 0; i < count; i++) {
        if ($("#cluster_name")[0].options[i].text === editClusterName) {
            $("#cluster_name")[0].options[i].selected = true;
            break;
        }
    }


    //设置是否备份
    var count2 = $("#is_backup").find('option').length;
    for (var i = 0; i < count2; i++) {
        if ($("#is_backup")[0].options[i].text === editIsBackup) {
            $("#is_backup")[0].options[i].selected = true;
            break;
        }
    }


    //设置审核人
    var count3 = $("#review_man").find('option').length;
    for (var i = 0; i < count3; i++) {
        if ($("#review_man")[0].options[i].text === "kxtxdba") {
            $("#review_man")[0].options[i].selected = true;
        }
    }

    // $("#cluster_name").find("option[text='editClusterName']").attr("selected",true);
    // $("#is_backup").find("option[text=editIsBackup]").attr("selected",true);
    //用完后，清除session中存储的值。
    sessionStorage.removeItem('editWorkflowNname');
    sessionStorage.removeItem('editSqlContent');
    sessionStorage.removeItem('editClusterName');
    sessionStorage.removeItem('editReviewMen');
    sessionStorage.removeItem('editIsBackup');

});
