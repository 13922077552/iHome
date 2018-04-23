function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function generateUUID() {
    var d = new Date().getTime();
    if(window.performance && typeof window.performance.now === "function"){
        d += performance.now(); //use high-precision timer if available
    }
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = (d + Math.random()*16)%16 | 0;
        d = Math.floor(d/16);
        return (c=='x' ? r : (r&0x3|0x8)).toString(16);
    });
    return uuid;
}
var uuid = "";
// 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
function generateImageCode() {
    // 1.获取uuid
    uuid = generateUUID();
    // 2.拼接带有uuid的请求地址
    var url = '/api/1.0/image_code?uuid=' + uuid;

    // > 标签选择器，表示寻找父节点的子节点
    // '空格' ： 标签选择器，表示寻找父节点的子节点，如果一级找不见，自动寻找下一级，直到找到为止
    $('.image-code>img').attr('src', url)
}

function sendSMSCode() {
    // 校验参数，保证输入框有数据填写
    $(".phonecode-a").removeAttr("onclick");

    var mobile = $("#mobile").val();
    if (!mobile) {
        $("#mobile-err span").html("请填写正确的手机号！");
        $("#mobile-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }
    var imageCode = $("#imagecode").val();
    if (!imageCode) {
        $("#image-code-err span").html("请填写验证码！");
        $("#image-code-err").show();
        $(".phonecode-a").attr("onclick", "sendSMSCode();");
        return;
    }

    // TODO: 通过ajax方式向后端接口发送请求，让后端发送短信验证码
    var params = {
        'mobile':mobile,
        'imageCode':imageCode,
        'uuid':uuid
    };

    $.ajax({
        url:'/api/1.0/sms_code',
        type:'post',
        data:JSON.stringify(params),
        contentType:'application/json',
        headers:{'X-CSRFToken':getCookie('csrf_token')},
        success:function (response) {
            if (response.errno == '0') {
                // 发送成功后，进行倒计时
                var num = 60;
                var t = setInterval(function ()  {
                    if (num == 0) {
                        // 倒计时完成,清除定时器
                        clearInterval(t);         // 重新生成验证码
                        generateImageCode();
                        // 重置内容
                        $(".phonecode-a").html('获取验证码');
                        // 重新添加点击事件
                        $(".phonecode-a").attr("onclick", "sendSMSCode();");
                    } else {
                        // 正在倒计时，显示秒数
                        $(".phonecode-a").html(num + '秒');
                    }

                    num = num - 1;
                }, 1000);

            } else {
                // 重新添加点击事件
                $(".phonecode-a").attr("onclick", "sendSMSCode();");
                // 重新生成验证码
                generateImageCode();
                // 弹出错误消息
                alert(response.errmsg);
            }
        }
    });
}

$(document).ready(function() {
    generateImageCode();  // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性

    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#imagecode").focus(function(){
        $("#image-code-err").hide();
    });
    $("#phonecode").focus(function(){
        $("#phone-code-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
        $("#password2-err").hide();
    });
    $("#password2").focus(function(){
        $("#password2-err").hide();
    });

    // TODO: 注册的提交(判断参数是否为空)
    $('.form-register').submit(function (event) {
        // 监听表单的提交事件，并把默认的提交动作禁用掉，然后使用自己写的ajax发送注册请求
        event.preventDefault();

        // 获取手机号,短信验证码,密码和确认密码
        var mobile = $('#mobile').val();
        var sms_code = $('#phonecode').val();
        var password = $('#password').val();
        var password2 = $('#password2').val();

        // 校验参数是否为空
        if (!mobile) {
            $('#mobile-err span').html('请输入手机号');
            $('#mobile-err').show();
            return;
        }
        if (!sms_code) {
            $('#phone-code-err span').html('请输入短信验证码');
            $('#phone-code-err').show();
            return;
        }
        if (!password) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        if (password != password2) {
            $("#password2-err span").html("两次密码不一致!");
            $("#password2-err").show();
            return;
        }

        var params = {
            'mobile':mobile,
            'sms_code':sms_code,
            'password':password
        };

        $.ajax({
            url:'/api/1.0/users',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno == '0') {
                    location.href = '/'; // 进入主页
                } else {
                    alert(response.errmsg);
                }
            }
        });
    });
});