/**
 * Created by Jacky.lau on 11/28/2018.
 */
//工单记录搜索
function worksearch() {
    if ($("#workname").val() === "") {
        var $wrongbody = $('#wrongpwd-modal-body');
        var $wrongmodal = $('#wrongpwd-modal');
        $wrongbody.html("请输入关键字!");
        $wrongmodal.modal({
            keyboard: false, backdrop: 'static'
        });
    }
    else {
        document.getElementById('f_search').submit();
    }
}


