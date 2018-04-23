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
        $(this).serializeArray().map(function (obj) {
            params[obj.name] = obj.value;
        });
        var facilities = [];
        //将表单中的被选中的checkbox筛选出来
        // 选中input框勾选中的标签，且name属性等于facility的所有标签
        // function中的参数i是第几个的下标，elem是当前的标签
        $(':checkbox:checkbox[name=facility]').each(function (i, elem) {

           facilities[i] = elem.value;
        });
        //将设备列表添加到params中
        params['facility'] = facilities;

        $.ajax({
            url:'/api/1.0/houses',
            type:'post',
            data:JSON.stringify(params),
            contentType:'application/json',
            headers:{'X-CSRFToken':getCookie('csrf_token')},
            success:function (response) {
                if(response.errno=='0'){
                    //发布新的房源信息成功后的操作：隐藏基本信息的表单，展现上传图片的表单
                    $('#form-house-info').hide();
                    $('#form-house-image').show();
                }else if(response.errno=='4101'){
                    location.href= 'login.html'
                }else {
                    alert(response.errmsg)
                }
            }
        })
    });
    
    
    // TODO: 处理图片表单的数据

});