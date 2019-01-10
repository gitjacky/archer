var personDataSummary = null;
var personCorlor = [
'rgba(255, 99, 132, 0.9)',
'rgba(54, 162, 235, 0.8)',
'rgba(255, 206, 86, 0.7)',
'rgba(75, 192, 192, 0.8)',
'rgba(153, 102, 255, 0.9)']

$(document).ready(function() {
    var isCharts = window.location.pathname.indexOf("charts");
        if (isCharts != -1) {
        getPersonWork()
        getMonthWork()
        getPersonCancel()
    }
});

function getPersonWork(){
    $.ajax({
            type: 'get',
            url: '/getPersonCharts/',
            success: function(data) {
                var data_person = new Array();
                var lb_person = new Array();
                var bg_corlor = new Array()
                for (var i=0; i<data.length; i++) {
                    lb_person.push(data[i][0]);
                    data_person.push(data[i][1]);
                    bg_corlor.push(personCorlor[i%5])
                }

                personDataSummary = {
                labels : lb_person,
                datasets : [
                     {
                        label: '近三个月内个人工单数量龙虎榜TOP 50',
                        data : data_person,
                        backgroundColor:bg_corlor,
                     }
                ]}
                var ctx = document.getElementById("summaryWorkflowByPerson").getContext("2d");
                var myBar = new Chart.Bar(ctx, {data:personDataSummary, options: {
                    scales: {
                        yAxes: [{
                            ticks: {
                                beginAtZero: true
                            }
                        }]
                    }
                }});
            },
            cache: false,
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                alert(errorThrown);
            }
        });
}




function getMonthWork() {
	$.ajax({
		type: 'get',
    	url: '/getMonthCharts/',
    	success: function(data) {
            var data_month = new Array();
            var lb_month = new Array();
            for (var i=0; i<data.length; i++) {
                lb_month.push(data[i][0]);
                data_month.push(data[i][1]);
            }

            // console.log(lb_month)
            // console.log(data_month)

        var ctx = document.getElementById("summaryWorkflowByMonth").getContext("2d");
        var myChart = new Chart(ctx, {
                                    type: 'line',
                                    data: {
                                        labels: lb_month,
                                        datasets: [{
                                            label: '近三个月内工单数据量',
                                            data: data_month,
                                            backgroundColor: [
                                                'rgba(255, 99, 132, 0.2)',
                                            ],
                                            borderColor: [
                                                'rgba(255,99,132,1)',
                                            ],
                                            borderWidth: 1
                                        }]
                                    },
                                    options: {
                                        scales: {
                                            yAxes: [{
                                                ticks: {
                                                    beginAtZero:true
                                                }
                                            }]
                                        }
                                    }
                                });

		},
		cache: false,
		error: function(XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
};

function getPersonCancel() {

    $.ajax({
        type: 'get',
        url: '/getCancelCharts/',
        success: function (data) {
            var datas = new Array();

            for (var i=0; i<data.length; i++) {
                var arr={
                    name: data[i][0],
                    y:data[i][1]
                };
                datas.push(arr);
            }

            var chart = Highcharts.chart('summaryCancelByPerson', {
                chart: {
                    spacing: [40, 550, 40, 0]
                },
                title: {
                    floating: true,
                    text: '近三个月工单不规范排行'
                },
                tooltip: {
                    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
                },
                plotOptions: {
                    pie: {
                        allowPointSelect: true,
                        cursor: 'pointer',
                        dataLabels: {
                            enabled: true,
                            format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                            style: {
                                color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                            }
                        },
                        point: {
                            events: {
                                mouseOver: function (e) {  // 鼠标滑过时动态更新标题
                                    // 标题更新函数，API 地址：https://api.hcharts.cn/highcharts#Chart.setTitle
                                    chart.setTitle({
                                        text: e.target.name + '\t' + e.target.y + ' %'
                                    });
                                }
                                //,
                                // click: function(e) { // 同样的可以在点击事件里处理
                                //     chart.setTitle({
                                //         text: e.point.name+ '\t'+ e.point.y + ' %'
                                //     });
                                // }
                            }
                        },
                    }
                },
                series: [{
                    type: 'pie',
                    innerSize: '70%',
                    name: '百分比',
                    data:  datas
                }]
            }, function (c) { // 图表初始化完毕后的会掉函数
                // 环形图圆心
                var centerY = c.series[0].center[1],
                    titleHeight = parseInt(c.title.styles.fontSize);
                // 动态设置标题位置
                c.setTitle({
                    y: centerY + titleHeight / 2
                });
            });

        },
        cache: false,
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(errorThrown);
        }
    });
};
