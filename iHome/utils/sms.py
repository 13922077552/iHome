# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# ���ʺ�
accountSid = '8a216da862dcd1050162e1e7b8d70358'

# ���ʺ�Token
accountToken = '9af187805cb74fe0bd44235368efa7bf'

# Ӧ��Id
appId = '8a216da862dcd1050162e1e7b939035f'

# �����ַ����ʽ���£�����Ҫдhttp://
serverIP = 'app.cloopen.com'

# ����˿�
serverPort = '8883'

# REST�汾��
softVersion = '2013-12-26'


# ����ģ�����
# @param to �ֻ�����
# @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
# @param $tempId ģ��Id

# def sendTemplateSMS(to, datas, tempId):
#     # ��ʼ��REST SDK
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


# ����һ�������ķ����ʼ�
class CCP(object):
    """��װ�����࣬����ͳһ�ķ�����֤��"""
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)

            # ��ʼ��REST SDk
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_sms_code(self,to, datas, tempId):
        """���Ͷ�����֤��ķ���"""
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        # �ж϶��ŷ����Ƿ�ɹ�
        if result.get('statusCode') == '000000':
            # ����ķ������Ǹ��������ж϶����Ƿ��ͳɹ�
            return 1
        else:
            return 0


# ��13922077552���Ͷ�����֤�룬����Ϊ66666,5���ӹ����ڣ�ʹ��idΪ1��ģ��
# sendTemplateSMS = CCP()
# sendTemplateSMS.send_sms_code('13922077552', ['666666', '5'], '1')
