/**
 * Created by Jacky.lau on 7/9/2018.
 */
//Mongo编码同步提交时，点击后为模板提供源环境与目的环境选项内容
function mogo_add() {
    $.ajax({
        type: "post",
        url: "/mgadd/",
        dataType: "json",
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            var hosts = data.mghosts;
            var s_options = document.getElementById("s_envirment");
            var t_options = document.getElementById("t_envirment");
            var hosts_len = hosts.length;
            var $s_mgenv = $("#s_envirment");
            var $t_mgenv = $("#t_envirment");
            if (hosts) {
                for (var i = 0; i < hosts_len; i++) {
                    s_options.options[i + 1] = new Option();
                    s_options.options[i + 1].text = hosts[i];
                    s_options.options[i + 1].value = hosts[i];

                    t_options.options[i + 1] = new Option();
                    t_options.options[i + 1].text = hosts[i];
                    t_options.options[i + 1].value = hosts[i];
                }
                $s_mgenv.selectpicker('render');
                $s_mgenv.selectpicker('refresh');
                $t_mgenv.selectpicker('render');
                $t_mgenv.selectpicker('refresh');
            }

        }
    })
}

//mongo同步记录搜索
function check() {
    if ($("#input_key").val() === "") {
        var $wrongbody = $('#wrongpwd-modal-body');
        var $wrongmodal = $('#wrongpwd-modal');
        $wrongbody.html("请输入编码名称!");
        $wrongmodal.modal({
            keyboard: false, backdrop: 'static'
        });
    }
    else {
        document.getElementById('c_search').submit();
    }
}

//模板上mongo编码同步提交事件
function mogo_commit() {
    var $mg_name = $("#mgname").val();
    var $mg_type = $("#mg_type").val();
    var $s_env = $("#s_envirment").val();
    var $t_env = $("#t_envirment").val();

    if ($s_env === null || $t_env === null || $mg_name === null) {
        alert("编码名称或环境不能为空！");
    } else if ($s_env === $t_env && $s_env !== null && $t_env !== null) {
        alert("源环境与目的环境不能相同！");
    } else {
        $.ajax({
            type: "post",
            url: "/mgcommit/",
            dataType: "json",
            data: {
                "mg_name": $mg_name,
                "mg_type": $mg_type,
                "s_env": $s_env,
                "t_env": $t_env
            },
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                var status = data.status;
                alert(status);
                window.location.reload(true);
            }
        })
    }
}

//mongo编码工单执行同步
function mongosync(a, b) {

    $.ajax({
        type: "post",
        url: "/mongosync/",
        dataType: "json",
        data: {
            "mg_id": a,
            "mg_name": b
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            var mgdict = data['mgdict'];
            //将id，code赋值到当前input mgid,mgnm的value.
            $("#mgid").val(mgdict['mgid']);
            $("#mgnm").val(mgdict['mgname']);
            var $wrongbody = $('#wrongpwd-modal-body');
            var $wrongmodal = $('#wrongpwd-modal');

            if (mgdict === "inuse") {
                $wrongbody.html("同步文件正在使用!");
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })

            } else if (mgdict === "notexist") {
                $wrongbody.html("源环境编码不存在！");
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })
            } else if (mgdict['t_list'] === "已存在") {
                $wrongbody.html(mgdict['t_list']);
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })
            } else if (mgdict['t_list'] === "已完成") {
                $wrongbody.html(mgdict['t_list']);
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })
            } else if (mgdict['t_list'] === "提示：目的环境还没有类似sysInfo,请手工插入对应sysInfo后再同步！") {
                $wrongbody.html(mgdict['t_list']);
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })
            } else {
                var mgs_url = mgdict['s_list'][0]['address'];
                var mgt_url = mgdict['t_list'];

                $("#surlname").text(mgs_url);
                var $label_url = $("#label_url");
                $label_url.empty();
                var mod_span = document.createElement("span");
                mod_span.append('目标环境可选URL：');
                $label_url.append(mod_span);
                for (var j = 0; j < mgt_url.length; j++) {
                    var s_html = '<label class="radio" style="font-size: 16px;color: red"><input type="radio" name="optionsRadios" id="radio_' + j + '" value="' + mgt_url[j] + '">' + mgt_url[j] + '</label>';
                    $label_url.append(s_html);
                }

                $("#urlModal").modal('show');
                $(".radio").each(function () {
                    // console.log($(this));
                    $(this).click(function () {
                        $(this).attr("checked", true);
                        $(this).addClass('checked');
                    })
                })
            }

        }
    })
}

//mongo编码同步时选择目标url
function submit_curl() {
    var mgid = $("#mgid").val();
    var mgnm = $("#mgnm").val();
    var $wrongbody = $('#wrongpwd-modal-body');
    var $wrongmodal = $('#wrongpwd-modal');
    var urlfb = $('input[name="optionsRadios"]:checked').val();

    $("#urlModal").modal('hide');
    $.ajax({
            type: "post",
            url: "/mongosync/",
            dataType: "json",
            data: {
                "mg_id": mgid,
                "mg_name": mgnm,
                "c_url": urlfb
            },
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                var mgdict = data['mgdict'];
                console.log(mgdict);

                if (mgdict === "inuse") {
                    $wrongbody.html("同步文件正在使用!");
                    $wrongmodal.modal({
                        keyboard: false, backdrop: 'static'
                    });
                    $wrongmodal.on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })

                } else if (mgdict === "notexist") {
                    $wrongbody.html("源环境编码不存在！");
                    $wrongmodal.modal({
                        keyboard: false, backdrop: 'static'
                    });
                    $wrongmodal.on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })
                } else if (mgdict['t_list'] === "已存在") {
                    $wrongbody.html(mgdict['t_list']);
                    $wrongmodal.modal({
                        keyboard: false, backdrop: 'static'
                    });
                    $wrongmodal.on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })
                } else if (mgdict['t_list'] === "已完成") {
                    $wrongbody.html(mgdict['t_list']);
                    $wrongmodal.modal({
                        keyboard: false, backdrop: 'static'
                    });
                    $wrongmodal.on('hidden.bs.modal', function () {
                        window.location.reload(true);
                    })
                } else {
                    window.location.reload(true);
                }
            }
        }
    )
}

//mongo编码终止同步
function syncabort(c, d) {
    var $wrongbody = $('#wrongpwd-modal-body');
    var $wrongmodal = $('#wrongpwd-modal');
    $.ajax({
        type: "post",
        url: "/mongoabort/",
        dataType: "json",
        data: {
            "mg_id": c,
            "mg_name": d
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            var status = data.status;
            $wrongbody.html(status);
            $wrongmodal.modal({
                keyboard: false, backdrop: 'static'
            });
            $wrongmodal.on('hidden.bs.modal', function () {
                window.location.reload(true);
            })
            // window.location.reload(true);
        }
    })
}
//mongo编码内容查询页面中mongo环境选项内容
function mogo_env() {
    var env_options = document.getElementById("env_name");
    $.ajax({
        type: "post",
        url: "/mgadd/",
        dataType: "json",
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            hosts = data.mghosts;
            var $env_name = $("#env_name");
            var hosts_len = hosts.length;
            $env_name.empty();
            $env_name.prepend("<option value='环境名称' disabled='' selected='selected'>环境名称</option>");
            if (hosts) {
                for (var i = 0; i < hosts_len; i++) {
                    env_options.options[i + 1] = new Option();
                    env_options.options[i + 1].text = hosts[i];
                    env_options.options[i + 1].value = hosts[i];
                }
                $env_name.selectpicker('render');
                $env_name.selectpicker('refresh');
            }
        }
    })
}

//检查必输框是否为空
function chose_content() {
    var $code_type = $("#mg_type");
    var $code_env = $("#env_name");
    var $code_name = $("#code_name");
    var $cd_name = $code_name.val();
    var req_field = [$code_env, $code_type];
    var flag = 0;


    $.each(req_field, function (name, value) {
        var fieldElement = $(this);
        value = fieldElement.val() || '';
        // console.log(fieldElement.attr('data-placeholder'));
        if (value) {
            value = value.trim();
        }
        if (!value || value === fieldElement.attr('data-placeholder')) {
            $('#wrongpwd-modal-body').html("请选择" + (fieldElement.attr('data-name') || fieldElement.name) + "！");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            })
        } else {
            flag = flag + 1;
        }
    });
    if (flag === 2) {
        if (!$cd_name) {
            $('#wrongpwd-modal-body').html("请输入编码名称！");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            })
        } else {
            codesearch()
        }
    }
}

function codesearch() {
    var $code_type = $("#mg_type").val();
    var $code_env = $("#env_name").val();
    var $code_name = $("#code_name").val();

    $.ajax({
        type: "post",
        url: "/codesearch/",
        dataType: "json",
        data: {
            "code_type": $code_type,
            "code_env": $code_env,
            "code_name": $code_name
        },
        headers: {"X-CSRFtoken": $.cookie("csrftoken")},
        success: function (data) {
            $("#sresult").css('display', '');
            var all_source = data['all_sources'];
            var $ss_list = $("#sourcelist");
            $ss_list.css('display', '');
            $ss_list.empty();

            if (all_source === undefined || all_source.length === 0) {
                $ss_list.append("编码不存在!")
            } else {
                for (var i = 0; i < all_source.length; i++) {
                    var one_html = '<span class="text-justify" style="font-size: medium">' + all_source[i] + '</span>';
                    $ss_list.append(one_html);
                }
            }

        }
    })
}

// 获取操作日志
function getlog(c, d) {
    var mogo_id = c;
    var mogo_name = d;
    $.ajax({
        type: "post",
        url: "/mongolog/",
        dataType: "json",
        data: {
            mogo_id: mogo_id,
            mogo_name: mogo_name
        },
        complete: function () {
        },
        success: function (data) {
            //初始化bootstrap table
            $('#logs').modal('show');
            $('#log-list').bootstrapTable('destroy').bootstrapTable({
                escape: true,
                striped: true,                      //是否显示行间隔色
                cache: false,                       //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
                pagination: false,                   //是否显示分页（*）
                sortable: false,                     //是否启用排序
                sortOrder: "asc",                   //排序方式
                sidePagination: "client",           //分页方式：client客户端分页，server服务端分页（*）
                pageNumber: 1,                      //初始化加载第一页，默认第一页,并记录
                pageSize: 14,                     //每页的记录行数（*）
                pageList: [20, 30, 50, 100],       //可供选择的每页的行数（*）
                search: false,                      //是否显示表格搜索
                strictSearch: false,                //是否全匹配搜索
                showColumns: false,                  //是否显示所有的列（选择显示的列）
                showRefresh: false,                  //是否显示刷新按钮
                minimumCountColumns: 2,             //最少允许的列数
                clickToSelect: false,                //是否启用点击选中行
                uniqueId: "id",                     //每一行的唯一标识，一般为主键列
                showToggle: false,                   //是否显示详细视图和列表视图的切换按钮
                cardView: false,                    //是否显示详细视图
                detailView: false,                  //是否显示父子表
                locale: 'zh-CN',                    //本地化
                data: data.rows,
                columns: [{
                    title: '操作时间',
                    field: 'operation_time',
                    formatter: TimeFormatter
                }, {
                    title: '操作',
                    field: 'operation_type_desc'
                }, {
                    title: '操作人',
                    field: 'operator_display'
                }, {
                    title: '操作信息',
                    field: 'operation_info'
                }],
                onLoadSuccess: function () {
                },
                onLoadError: function () {
                    alert("数据加载失败！请检查接口返回信息和错误日志！");
                }
            });
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    })
}

//格式化时间
function TimeFormatter(value, row, index) {
    if (value === null) {
        return "";
    }
    // var format_time = new Date(value).toLocaleString().replace(/\//g,'-').replace(/[日上下午]/g,'');
    // return format_time;

    var date = new Date(value);
    var result = date.getFullYear() + '-' + (date.getMonth() + 1) + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes() + ':' + date.getSeconds();
    return result;
}

//搜索指定时间范围指定环境提交的编码，批量提交到其他环境
function muti_search() {
    //遍历每个input,获取s_time与e_time
    var $s_time = $("#s_time").val();
    var $e_time = $("#e_time").val();
    var time_minus = parseInt(new Date($e_time) - new Date($s_time));
    var time_range = time_minus / 1000 / 3600 / 24;
    var sourceenv = document.getElementById("source_env").value;

    if (time_range >= 7) {
        $('#wrongpwd-modal-body').html("查询时间范围不能大于7天!");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
    } else if (time_minus <= 0) {
        $('#wrongpwd-modal-body').html("开始时间不能大于结束时间!");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
    } else {
        if (sourceenv === 'is-empty') {
            $('#wrongpwd-modal-body').html("请选择源环境!");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            });
        } else if ($s_time === '' && $e_time !== '') {
            // alert("请选择结束时间!")
            $('#wrongpwd-modal-body').html("请选择开始时间!");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            });
        } else if ($s_time !== '' && $e_time === '') {
            // alert("请选择时间范围!");
            $('#wrongpwd-modal-body').html("请选择结束时间!");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            });
        } else if ($s_time === '' && $e_time === '') {
            $('#wrongpwd-modal-body').html("请选择时间范围!");
            $('#wrongpwd-modal').modal({
                keyboard: false, backdrop: 'static'
            });
        } else {

            $.ajax({
                type: "post",
                url: "/mgmutifilter/",
                dataType: "json",
                data: {
                    "s_time": $s_time,
                    "e_time": $e_time,
                    "sourceenv": sourceenv,
                    "navStatus": "allrelease",
                    "pageNo": "1"
                },

                headers: {"X-CSRFtoken": $.cookie("csrftoken")},
                success: function (data) {
                    var $mytbody = $("#muti_result");
                    $mytbody.empty();
                    var allrows = data['count'];
                    var data = data['mogo_result'];

                    // console.log($().jquery);  //查看当前jquery版本
                    if (allrows === 0 && data.length === 0) {
                        var $tr = $("<tr class='no-records-found'><td colspan='8'>未查询到相关编码.</td></tr>");
                        $mytbody.append($tr);
                    } else {
                        $.each(data, function (i) {
                            var id = data[i].id;
                            var mogo_name = data[i].mogo_name;
                            var mogo_type = data[i].mogo_type;
                            var mogo_target = data[i].mogo_target;
                            var mogo_submit = data[i].mogo_submit;
                            var mogo_subtime = data[i].mogo_subtime;
                            var mogo_fintime = data[i].mogo_fintime;
                            var mogo_stat = data[i].mogo_stat;

                            submit_time = getFormatDate(new Date(mogo_subtime));
                            if(!mogo_fintime){
                                finish_time='';
                            }else{
                                finish_time = getFormatDate(new Date(mogo_fintime));
                            }

                            if (mogo_type === 0) {
                                aa = "<td data-name='mogo_type' data-value='0'><span class='label-success' style='width: 65px;height: 25px;display: inherit;border-radius: 5px;padding-left: 5px;padding-top: 5px;color: white'>服务接口</span></td>;"
                            } else if (mogo_type === 1) {
                                aa = "<td data-name='mogo_type' data-value='1'><span class='label-danger' style='width: 65px;height: 25px;display: inherit;border-radius: 5px;padding-left: 10px;padding-top: 5px;color: white'>定时器</span></td>";
                            }
                            else {
                                aa = "<td data-name='mogo_type' data-value='2'><span class='label-primary' style='width: 65px;height: 25px;display: inherit;border-radius: 5px;padding-left: 7px;padding-top: 5px;color: white'>MQ队列</span></td>";
                            }
                            var ckbox = "<td><input type='checkbox' name='mgck'></td>";
                            var $tr = $("<tr>" +
                                ckbox + "<td>" + data[i]['id'] + "</td><td data-name='code_name'>" +
                                mogo_name + "</td>" + aa + "<td>" + mogo_target + "</td>" + "<td>" + mogo_submit + "</td>" + "<td>" + submit_time + "</td>" + "<td>" + finish_time + "</td>" + "<td>" + mogo_stat + "</td>"
                                + "</tr>");

                            $mytbody.append($tr);
                            $("#mytbody tr:odd").css("background", "#F8F8F8");
                        });
                        //加载返回的数据后，为每个checkbox添加click事件用于自主选择数据条目
                        $("input[name='mgck']").each(function () {
                            $(this).change(function () {
                                if ($(this).prop("checked") === true) {
                                    $(this).prop("checked", true);
                                    $(this).attr("checked", "checked");
                                } else {
                                    $(this).prop("checked", false);
                                    $(this).removeAttr("checked");
                                }

                            });
                        });
                    }

                    //返给前台页码信息
                    var $butns = $("#btns");
                    $butns.empty();
                    var $butn_text = (pageBtns(1, 15, allrows)).split(',');
                    for (var i = 0, len = $butn_text.length; i < len; i++) {
                        if (i === 0) {
                            var $li = "<li class='active'><a href='javascript:void(0);'>" + $butn_text[i] + "</a></li>";
                        } else {
                            var $li = "<li><a href='javascript:void(0);'>" + $butn_text[i] + "</a></li>";
                        }
                        $butns.append($li);
                    }
                },
                error: function (XMLHttpRequest, errorThrown) {
                    alert(errorThrown);
                }
            })
        }
    }
}

//全选
function getselectall() {
    $(":checkbox").each(function () {
        $(this).prop('checked', true);
        $(this).attr('checked', 'checked');
    });
}

//取消全选
function unSelectall() {
    $("INPUT[type='checkbox']").each(function () {
        $(this).removeAttr('checked');
    })
}

//提交按钮点击事件
function mgmulti_commit() {
    //遍历每个checkbox,为每个checkbox添加点击事件
    $("#btn-mutisubmit").prop("disabled", "disabled");
    // var $mogo_target = $("#target_env").find("option:selected").val();
    var $mogo_target = $("#target_env").val();
    // var $mogo_source = $("#source_env").find("option:selected").val();
    var $mogo_source = $("#source_env").val();
    var $wrongbody = $('#wrongpwd-modal-body');
    var $wrongmodal = $('#wrongpwd-modal');
    if ($("input:checked").length === 0) {
        $wrongbody.html("请选择要提交的编码条目！");
        $wrongmodal.modal({
            keyboard: false, backdrop: 'static'
        });
        $("#btn-mutisubmit").prop("disabled", "");
        return false;
    } else if ($mogo_target === 'is-empty' || !$mogo_target) {    //如果目标环境为空则弹出警告
        $('#wrongpwd-modal-body').html("请选目标环境!");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
        $("#btn-mutisubmit").prop("disabled", "");
        return false;
    } else {
        var $filelist = {};
        $("input[name='mgck']:checked").each(function (i) {
            var $cd_name = $(this).closest('tr').find('td[data-name="code_name"]').text();
            var $cd_type = $(this).closest('tr').find('td[data-name="mogo_type"]').attr('data-value');
            $filelist[$cd_name] = $cd_type;
        });
        $.ajax({
            type: "post",
            url: "/mgmulti/",
            dataType: "json",
            data: {
                "mogo_target": $mogo_target,
                "mogo_codes": JSON.stringify($filelist),
                "mogo_source": $mogo_source
            },
            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                $wrongbody.html("<span style='font-size: 17px;font-weight: 700;display:block;text-align: center;color: darkgreen'>" + data.status + "</span>");
                $wrongmodal.modal({
                    keyboard: false, backdrop: 'static'
                });
                // window.location.reload(true);
                $wrongmodal.on('hidden.bs.modal', function () {
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
                $wrongmodal.on('hidden.bs.modal', function () {
                    window.location.reload(true);
                })
            }
        });
    }
};