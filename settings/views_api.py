# from rest_framework.response import Response
# from rest_framework.views import APIView
#
#
# class TestAPIView(APIView):
#     def get(self, request):
#         import configparser
#
#         config = configparser.ConfigParser()
#         config.read('settings.ini')
#
#         bitrix_enabled = config.getboolean('Bitrix', 'Enabled')
#         bitrix_url = config.get('Bitrix', 'URL')
#
#         return Response({'bitrix_enabled': bitrix_enabled,
#                          'bitrix_url': bitrix_url})
