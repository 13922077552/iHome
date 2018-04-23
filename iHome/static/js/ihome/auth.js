function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}


function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // TODO: 查询用户的实名认证信息
    $.get('/api/1.0/users/auth', function (response) {
        // 展现有实名认证信息时，展现实名认证信息，输入框改为不可以用
        if (response.errno=='0'){
            if (response.data.real_name && response.data.id_card) {
                // 展现实名认证信息
                $('#real-name').val(response.data.real_name);
                $('#id-card').val(response.data.id_card);

                // 输入框改为不可用
                $('#real-name').attr('disabled', true);
                $('#id-card').attr('disabled', true);
                // 隐藏保存按钮
                $('.btn-success').hide();
            }
        }else if (response.errno=='4101'){
            location.href='login.html'
        }else {
            alert(response.errmsg)
        }
    });

    // TODO: 管理实名信息表单的提交行为
    $('#form-auth').submit(function (event) {
        event.preventDefault();
        var real_name = $('#real-name').val();
        var id_card = $('#id-card').val();

        if (!real_name){
            alert('请输入真实姓名')
        }
        if (!id_card) {
            alert('请输入真实的身份证号码')
        }

        $('.error-msg').hide();

        var params = {
            'real_name':real_name,
            'id_card':id_card
        };

        $.ajax({
            url:'/api/1.0/users/auth',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno=='0'){
                    showSuccessMsg();
                    $('#real-name').attr('disabled', true);
                    $('#id-card').attr('disabled', true);
                    $('.btn-success').hide();
                }
                // 因为实名认证只有一次，所有一旦认证成功就要将inout设置为不可交互，并且要隐藏保存的按钮
                else if (response.errno=='4101'){
                    location.href='login.html'
                }else {
                    alert(response.errmsg)
                }
            }
        })
    })
});