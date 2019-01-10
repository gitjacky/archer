/**
 * Created by Jacky.lau on 8/3/2017.
 */
var xmlhttp;
function CreateXmlHttp() {
    //非IE浏览器创建XmlHttpRequest
    if (window.XMLHttpRequest){
        xmlhttp=new XMLHttpRequest();
    }
    //IE浏览器创建XmlHttpRequest
    if (window.ActiveXObject) {
        try {
            xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
        }

        catch (e) {
            try {
                xmlhttp = new ActiveXObject("msxml2.XMLHTTP");
            }
            catch (ex) {
            }
        }
    }
}

function AjaxSend() {
    //创建XmlHttpRequest对象
    CreateXmlHttp();
    if(!xmlhttp){
        alert("创建XmlHttpRequest对象发生异常!");
        return false;
    }
    //获取svn下拉框的值，作为条件发送给后端
    var ss=document.getElementById('svn_path').value.substring(0,4);
    //要发送的url,grademenu主要用来取数据
    url:"grademenu?svn_path=" + ss;
    xmlhttp.open("POST",url,false);

    xmlhttp.onreadystatechange=function () {
        if (xmlhttp.readyState==4){
            if(xmlhttp.status==200){
                //清空下拉框
                document.getElementById("svn_path").options.length=0;
                //str为返回的一个字符串，形如001/代理商1，002/代理商2，003/代理商3
                var str=xmlhttp.responseText;
                //将该字符串分割为数组形式
                var strs=str.split(",");
                document.getElementById(svn_path).options.add(new Option("------","000000"));
                for (var i=0;i<strs.length-1;i++){
                    //获取value值(编号)
                    var a=strs.substring(0,strs[i].lastIndexOf("/"));
                    //获取绑定内容
                    var b=strs.substring(strs[i].lastIndexOf("/")+1,strs.length);
                    //绑定到下拉框
                    document.getElementById("svn_path").options.add(new Option(b,a));
                }

            }
        }
    }
}



