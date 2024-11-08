from django.contrib.auth.models import Group
from rest_framework import serializers

from users.models import User


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']


class UserSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'groups']


class UserListSerializer(serializers.ModelSerializer):
    current_user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'current_user', 'first_name', 'last_name')
        read_only_fields = ('id',)

    def get_current_user(self, obj):
        request = self.context.get('request')
        if request and request.user == obj:
            return True
        return False
