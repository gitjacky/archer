/**
 * Created by Jacky.lau on 4/9/2018.
 */

function committime() {
    //遍历每个input,获取s_time与e_time
    $s_time = $("#s_time").val();
    $e_time = $("#e_time").val();

    //如果其中一个为空则弹出警告，若两个时间都未写，则默认查询7天内数据
    if ($s_time == '' && $e_time != '') {
        // alert("请选择结束时间!")
        $('#wrongpwd-modal-body').html("请选择开始时间!");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
    } else if ($s_time != '' && $e_time == '') {
        // alert("请选择时间范围!");
        $('#wrongpwd-modal-body').html("请选择结束时间!");
        $('#wrongpwd-modal').modal({
            keyboard: false, backdrop: 'static'
        });
    } else {

        $.ajax({
            type: "post",
            url: "/ddlajx/",
            dataType: "json",
            data: {
                "s_time": $s_time,
                "e_time": $e_time
            },

            headers: {"X-CSRFtoken": $.cookie("csrftoken")},
            success: function (data) {
                $("#ddltable").css('display','');
                data = data.ddl_dict;
                //利用Json判断返回的字典是不是空
                if (JSON.stringify(data) == '{}') {
                    $("#ddltable tbody").empty()
                    var $tr = "<tr><td colspan='3' style='font-size: 10px;'>没有查询到相关结果！</td></tr>";
                    $("#ddltable tbody").append($tr);
                }
                else {
                    $("#ddltable tbody").empty();
                    $.each(data, function (i) {
                        var $tr = $("<tr>" +
                            "<td style='font-size: 10px;'>" + i + "</td>" +
                            "<td style='font-size: 10px;'>" + data[i][1] + "</td>" +
                            "<td style='font-size: 10px;'>" + data[i][0] + "</td>"
                            + "</tr>");

                        $("#ddltable tbody").append($tr);
                    });
                    devddlchart();
                }

            },
            error: function (XMLHttpRequest, errorThrown) {
            }
        })

    }
    ;

};

function devddlchart() {
    $("#container").css('display','block');
    var chart = Highcharts.chart('container', {
        data: {
            table: 'ddltable'
        },
        chart: {
            type: 'column'
        },
        title: {
            text: 'DEV环境DDL分类统计图表'
            // 该功能依赖 data.js 模块，详见https://www.hcharts.cn/docs/data-modules
        },
        yAxis: {
            allowDecimals: false,
            title: {
                text: '个',
                rotation: 0
            }
        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.series.name + '</b><br/>' +
                    this.point.y + ' 个' + this.point.name.toLowerCase();
            }
        }
    });
};