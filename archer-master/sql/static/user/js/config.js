// /**
//  * Created by Jacky.lau on 4/22/2019.
//  */
$(function () {

    $("INPUT[type='checkbox']").each(function () {
        var id = $(this).data('id');
        var status = $(this).data('status');

        $(this).bootstrapSwitch({
            'onText': 'ON',// 设置ON文本
            'offText': 'OFF', // 设置OFF文本
            "onColor": 'primary',// 设置ON文本颜色     (info/success/warning/danger/primary)
            // "offColor":'danger',// 设置OFF文本颜色        (info/success/warning/danger/primary)
            size: "mini",//设置控件大小,从小到大  (mini/small/normal/large)
            handleWidth: "7",//设置控件宽度
            'state': true
        });
    });

    // $("INPUT[type='checkbox']").bootstrapSwitch("onSwitchChange",function(event,state){
    // var id = $(this).data('id');
    //         var status = parseInt($(this).attr('data-status'));
    //
    //         if (status != state) {
    //             var check = false;
    //             // 修改状态
    //             $.ajax({
    //                 url: "test.php",
    //                 async: false,
    //                 type: "post",
    //                 dataType: "json",
    //                 data: {'id': id, 'status': status},
    //                 success: function(data){
    //                     if (data.code == 1) {
    //                         check = true;
    //                         $('#status_'+id).attr('data-status', status ? 0 : 1);
    //                         layer.msg('更新成功');    //这里是调用了layer弹窗组件
    //                     } else {
    //                         layer.msg(data.msg);
    //                     }
    //                 }
    //             });
    //
    //             return check;
    //         }
    //     });

});

//配置项切换
function change_config (){
    sessionStorage.setItem('config_type', $("#config").val());

    if ($("#config").val() === '0') {
        $("#panel_setting").show();
        $("#div-system-config").show();
        $("#div-workflow").hide();
        $("#div-workflow-config").hide();
//         $('input[type="checkbox"]').each(function (i) {
//             if ($(this).val() === 'true') {
// //                       $(this).bootstrapSwitch('state', true);
//                 $(this).bootstrapSwitch();
//             }
//             else {
//                 $(this).bootstrapSwitch('state', false);
//             }
//         });
    }
    else if ($("#config").val() === '1') {
        $("#div-system-config").hide();
        $("#panel_setting").show();
        $("#div-workflow").show();
        $("#div-workflow-config").show();
        $("#workflow_type").trigger("change");
    }
};

// 系统设置checkbox事件
$('input[type="checkbox"]').on('switchChange.bootstrapSwitch', function (event, state) {
    if (state) {
        $(this).val(true);
        if ($(this).attr("id") === 'query') {
            $("#div-query-config").show();
        }
        else if ($(this).attr("id") === 'mail') {
            $("#div-mail-config").show();
        }
        else if ($(this).attr("id") === 'auto_review') {
            $("#div-auto-review-config").show();
        }
    }
    else {
        $(this).val(false);
        if ($(this).attr("id") === 'query') {
            $("#query_check").val(false);
            $("#data_masking").val(false);
            $("#admin_query_limit").val(0);
            $("#div-query-config").hide();
        }
        else if ($(this).attr("id") === 'mail') {
            $("#mail_ssl").val(false);
            $("#div-mail-config").hide();
        }
        else if ($(this).attr("id") === 'auto_review') {
            $("#div-auto-review-config").hide();
        }
    }
});

// 修改系统设置
$("#saveconfig").click(function () {
    var sys_config = $("#div-system-config");
    var configs = [];
    sys_config.find('[key]').each(
        function () {
            var config_item = $(this).attr("key");
            var config_value = $(this).val();
            configs.push({
                key: config_item,
                value: config_value
            });
        }
    );

    $.ajax({
        type: "post",
        url: "/config/change/",
        dataType: "json",
        data: {
            configs: JSON.stringify(configs)
        },
        complete: function () {
        },
        success: function (data) {
            if (data.status === 0) {
                window.location.reload()
            } else {
                alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
});

// // 切换组触发工单类型切换事件
// $("#group").change(function () {
//     $("#workflow_type").trigger('change')
// });
//
// // 点击用户填充到workflow_auditors_text
// $("#group_auditors").change(function () {
//     var auth_group = $(this).find(':selected').attr("disabled", "disabled").val();
//     var auditors = $("#workflow_auditors_text").val();
//     if (auditors) {
//         $("#workflow_auditors_text").val(auditors + '->' + auth_group);
//     }
//     else {
//         $("#workflow_auditors_text").val(auth_group)
//     }
//     $('#group_auditors').selectpicker('render');
//     $('#group_auditors').selectpicker('refresh');
// });
//
// // 清空审核人信息
// $("#btn-workflow-config-clean").click(function () {
//     $("#workflow_auditors_text").val('');
//     window.location.reload()
// });
//
// // 切换工单类型获取对应组负责人
// $("#workflow_type").change(function () {
//     $("#div-workflow-config").show();
//     $("#workflow_auditors_text").val('');
//     if ($("#group").val()) {
//         $.ajax({
//             type: "post",
//             url: "/group/auditors/",
//             dataType: "json",
//             data: {
//                 group_name: $("#group").val(),
//                 workflow_type: $("#workflow_type").val()
//             },
//             complete: function () {
//
//             },
//             success: function (data) {
//                 if (data.status === 0) {
//                     var result = data.data;
//                     $("#workflow_auditors").text(result['auditors_display']);
//                 } else {
//                     alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
//                 }
//             },
//             error: function (XMLHttpRequest, textStatus, errorThrown) {
//                 alert(errorThrown);
//             }
//         });
//     }
// });
//
// // 变更组工单审批流程
// $("#btn-workflow-config").click(function () {
//     if ($("#group").val() && $("#workflow_type").val()) {
//         $(this).addClass('disabled');
//         $(this).prop('disabled', true);
//         var audit_auth_groups = $("#workflow_auditors_text").val().replace(/->/g, ",");
//         $.ajax({
//             type: "post",
//             url: "/group/changeauditors/",
//             dataType: "json",
//             data: {
//                 group_name: $("#group").val(),
//                 audit_auth_groups: audit_auth_groups,
//                 workflow_type: $("#workflow_type").val()
//             },
//             complete: function () {
//                 $("#btn-workflow-config").removeClass('disabled');
//                 $("#btn-workflow-config").prop('disabled', false);
//             },
//             success: function (data) {
//                 if (data.status === 0) {
//                     //alert('修改成功');
//                     $("#workflow_type").trigger("change")
//                 } else {
//                     alert("status: " + data.status + "\nmsg: " + data.msg + data.data);
//                 }
//             },
//             error: function (XMLHttpRequest, textStatus, errorThrown) {
//                 alert(errorThrown);
//             }
//         });
//     }
//     else {
//         alert('请选择项目和工单类型！')
//     }
//
// });
//
// 检测inception
$("#check_incption").click(function () {
    $(this).addClass('disabled');
    $(this).prop('disabled', true);
    $.ajax({
        type: "get",
        url: "/check/inception/",
        dataType: "json",
        data: {},
        complete: function () {
            $("#check_incption").removeClass('disabled');
            $("#check_incption").prop('disabled', false);
        },
        success: function (data) {
            if (data.status === 0) {
                alert('连接成功')
            } else {
                alert("status: " + data.status + "\nmsg: " + data.msg);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
});

// 检测邮件
$("#check_email").click(function () {
    $(this).addClass('disabled');
    $(this).prop('disabled', true);
    $.ajax({
        type: "get",
        url: "/check/email/",
        dataType: "json",
        data: {},
        complete: function () {
            $("#check_email").removeClass('disabled');
            $("#check_email").prop('disabled', false);
        },
        success: function (data) {
            if (data.status === 0) {
                alert('连接成功')
            } else {
                alert("status: " + data.status + "\nmsg: " + data.msg);
            }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
});
//
// //自动填充操作项
// $(function () {
//
//     //初始化switch插件
//     // $("INPUT[type='checkbox']").each(function () {
//     //       $(this).bootstrapSwitch();
//     // });
//
//     $("INPUT[type='checkbox']").each(function() {
//     $this = $(this);
//     console.log($this);
//     var onColor = $this.attr("onColor");
//     var offColor = $this.attr("offColor");
//     var onText = $this.attr("onText");
//     var offText = $this.attr("offText");
//     var labelText = $this.attr("labelText");
//
//     var $switch_input = $("INPUT[type='checkbox']",$this);
//         $switch_input.bootstrapSwitch({
//             onColor : onColor,
//             offColor : offColor,
//             onText : onText,
//             offText : offText,
//             labelText : labelText
//         });
//     });
//
//
//     if (sessionStorage.getItem('config_type')) {
//         $("#config").val(sessionStorage.getItem('config_type')).trigger("change")
//     }
//     else if ($("#config").val()) {
//         $("#config").trigger("change")
//     }
// });
// $('#mySwitchOne').bootstrapSwitch('state',false,true);
// $("INPUT[type='checkbox']").bootstrapSwitch({
//     onText:'On',
//     offText:'Off'
// });

// 初始化 注意：state 属性的设置一定放在最后，别问我问什么，哈哈

// $(document).ready(function () {
//
//         $("#mySwitchOne").bootstrapSwitch({
//         'onText':'ON',// 设置ON文本
//         'offText':'OFF', // 设置OFF文本
//         "onColor":'primary',// 设置ON文本颜色     (info/success/warning/danger/primary)
//         // "offColor":'danger',// 设置OFF文本颜色        (info/success/warning/danger/primary)
//         size : "mini",//设置控件大小,从小到大  (mini/small/normal/large)
//         handleWidth:"7",//设置控件宽度
//         'state':true
//     });
//
//     $("#myswitchone").bootstrapSwitch("onSwitchChange",function(event,state){
//         var val='';
//         var text='';
//         if(state === true){
//             val = 1;
//             // text = '开启';
//         }else{
//             val = 0;
//             // text = '关闭';
//         }
//     });
//
//
//
//
//
// });




