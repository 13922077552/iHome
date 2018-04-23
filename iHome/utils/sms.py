# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# 主帐号
accountSid = '8a216da862dcd1050162e1e7b8d70358'

# 主帐号Token
accountToken = '9af187805cb74fe0bd44235368efa7bf'

# 应用Id
appId = '8a216da862dcd1050162e1e7b939035f'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


# 发送模板短信
# @param to 手机号码
# @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# @param $tempId 模板Id

# def sendTemplateSMS(to, datas, tempId):
#     # 初始化REST SDK
#     rest = REST(serverIP, serverPort, softVersion)
#     rest.setAccount(accountSid, accountToken)
#     rest.setAppId(appId)
#
#     result = rest.sendTemplateSMS(to, datas, tempId)
#     for k, v in result.iteritems():
#
#         if k == 'templateSMS':
#             for k, s in v.iteritems():
#                 print '%s:%s' % (k, s)
#         else:
#             print '%s:%s' % (k, v)


# 创建一个单例的发送邮件
class CCP(object):
    """封装单例类，用于统一的发送验证码"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # 初始化REST SDk
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_sms_code(self,to, datas, tempId):
        """发送短信验证码的方法"""
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # 判断短信发送是否成功
        if result.get('statusCode') == '000000':
            # 这里的返回在是给调用者判断短信是否发送成功
            return 1
        else:
            return 0


# 向13922077552发送短信验证码，内容为66666,5分钟够过期，使用id为1的模板
# sendTemplateSMS = CCP()
# sendTemplateSMS.send_sms_code('13922077552', ['666666', '5'], '1')
