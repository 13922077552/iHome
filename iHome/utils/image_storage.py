# -*- coding: utf-8 -*-
# 上传，保存图片到七牛云

import qiniu

access_key = 'yV4GmNBLOgQK-1Sn3o4jktGLFdFSrlywR2C-hvsW'
secret_key = 'bixMURPL6tHjrb8QKVg2tm7n9k8C7vaOeQ4MEoeW'
bucket_name = 'ihome'


def upload_image(image_data):
    """上传，保存图片到七牛云"""

    # 创建七牛云对象
    q = qiniu.Auth(access_key, secret_key)
    # 获取上传的token
    token = q.upload_token(bucket_name)
    # 调用上传的方法，实现生成并响应结果给我们
    # 说明：参数2传入None，表示让七牛云给我们生产数据的唯一表示key，不用我们自己写，第三个参数是要上传的图片
    # ret是一个字典，里面有一个key的值就是我们上传储存图片后的路径
    ret, info = qiniu.put_data(token, None, image_data)
    # 判断上传图片是否成功
    if info.status_code == 200:
        key = ret.get('key')
        return key
    else:
        # 如果上传失败就抛出异常
        raise Exception('上传图片失败')


# if __name__ == '__main__':
#     path = '/home/python/Desktop/fruit.jpg'
#     with open(path, 'rb') as f:
#         image_data = f.read()
#         upload_image(image_data)
