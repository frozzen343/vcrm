from rest_framework.response import Response
from rest_framework.views import APIView


import integrations.bitrix as b24


class TestAPIView(APIView):
    def get(self, request):
        response = ''

        response = b24.get_task_by_id(6261)
        # response = b24.get_task_list_by_activity()
        # response = b24.set_task_accept(6616)
        # response = b24.set_task_close(6616)
        # response = b24.set_task_renew(6616)
        # response = b24.get_task_comment(6616)
        # response = b24.add_task_comment(6616, 'tesT 123 !@#$%^&*()')

        return Response(response)
