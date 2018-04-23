function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function(){
    // $('.popup_con').fadeIn('fast');
    // $('.popup_con').fadeOut('fast');

    // TODO: 在页面加载完毕之后获取区域信息
    $.get('/api/1.0/areas',function (resposne) {
        if (resposne.errno == '0') {
            // 渲染<select>⾥⾯的<option>
        //     $.each(resposne.data, function (i, area) {
        //         $('#area-id').append('<option value="' + area.aid + '">' + area.aname + '</option>')
        //     });
            // 使用art-template模板引擎中的js生成要渲染的htmlneir
            var html = template('areas-tmpl', {'areas': resposne.data});
            $('#area-id').html(html)
        }else {
            alert(resposne.errmsg)
        }
    });


    // TODO: 处理房屋基本信息提交的表单数据
    $('#form-house-info').submit(function (event) {
        event.preventDefault();
        
        var params = {};
        // 收集$(this)表单中的带有name的input标签数据，封装到数组中
        $(this).serializeArray().map(function (x) {
            
        })
            
        $.ajax({
            url:'/api/1.0/houses',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if(response.errno=='0'){
                }else {
                    alert(response.errmsg)
                };
            }
        })
        
    });
    
    
    // TODO: 处理图片表单的数据

});