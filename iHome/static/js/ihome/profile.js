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

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
    $.get('/api/1.0/users', function (response) {
        if (response.errno=='0'){
            $('#user-avatar').attr('src', response.data.avatar_url);
            $('#user-name').val(response.data.name);
        }else if(response.errno == 4101){
            location.href='login.html'
        }
        else {
            alert(response.errmsg);
        }
    });

    // TODO: 管理上传用户头像表单的行为
    $('#form-avatar').submit(function (event) {
        // 阻止表单默认的submit提交行为
        event.preventDefault();
        //使用ajax实现表单的提交行为
        $(this).ajaxSubmit({
            url:'/api/1.0/users/avatar',
            type:'post',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if (response.errno=='0'){
                    $('#user-avatar').attr('src', response.data);
                }else if(response.errno == 4101){
                     location.href='login.html'
                }else {
                    alert(response.errmsg)
                }
            }
        })
    });


    // TODO: 管理用户名修改的逻辑
    $('#form-name').submit(function (event) {
        event.preventDefault();
        var name = $('#user-name').val();
        if (!name) {
            alert('请输入用户名')
        }
        var params = {
            "name":name
        };
        $.ajax({
            url: '/api/1.0/users/name',
            type: 'put',
            contentType: 'application/json',
            headers: {'X-CSRFToken': getCookie('csrf_token')},
            data:JSON.stringify(params),
            success:function (response) {
                if (response.errno=='0'){
                    showSuccessMsg()
                }else if(response.errno == 4101){
                     location.href='login.html'
                     }
                else {
                    alert(response.errmsg)
                }
            }
        });
    })
});

