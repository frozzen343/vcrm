from rest_framework import serializers

from clients.models import Client
from mail.models import Mail
from tasks.models import Task
from users.models import User


class MailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mail
        fields = ('from_name', 'from_email',)


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('name',)


class PerformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar')


class TaskListSerializer(serializers.ModelSerializer):
    mail = MailSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    date_created = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    date_closed = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    performer = PerformerSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'contacts', 'mail', 'client',
                  'performer', 'fire', 'drive', 'date_created', 'date_closed',
                  'created_from')
        read_only_fields = ('id',)


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'hours_cost', 'description', 'status',
                  'contacts', 'client', 'performer', 'fire', 'drive')
        read_only_fields = ('id',)
