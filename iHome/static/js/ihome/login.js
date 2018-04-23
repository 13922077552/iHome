function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });


    // TODO: 添加登录表单提交操作
    $(".form-login").submit(function(e){
        // 禁用表单默认提交行为，采用自己写的ajax发送请求
        e.preventDefault();
        // 获取input标签的value
        var mobile = $('#mobile').val();
        var password = $('#password').val();

        if (!mobile){
            //如果没有
            $('#mobile-err span').html("请填写正确的手机号码");
            $('#mobile-err').show();
            return
        }
        if (!password){
            //如果没有
            $('#password-err-err span').html("请填写密码");
            $('#password-err').show();
        return
        }

        var params = {
            'mobile': mobile,
            'password': password
        };

        // 发送ajax请求实现登录
        $.ajax({
            url:'/api/1.0/sessions',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if(response.errno==0){
                    location.href = '/';
                }
                else {
                    alert(response.errmsg)
                }
            }
        })
    });
});
