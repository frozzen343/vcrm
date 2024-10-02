from rest_framework import serializers

from clients.models import Client, Contact
from mail.models import Mail, Attachment
from tasks.models import Task, Comment
from users.models import User


class AttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ('file', 'inline',)


class MailSerializer(serializers.ModelSerializer):
    attachments = AttachmentsSerializer(read_only=True, many=True)

    class Meta:
        model = Mail
        fields = ('from_name', 'from_email', 'attachments')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'name',)


class PerformerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar')


class TaskSerializer(serializers.ModelSerializer):
    mail = MailSerializer(read_only=True)
    client_name = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    date_closed = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    performer_info = PerformerSerializer(read_only=True, source='performer')

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'contacts', 'mail', 'client',
                  'client_name', 'performer', 'performer_info', 'fire',
                  'drive', 'date_created', 'date_closed', 'created_from',
                  'hours_cost', 'description')
        read_only_fields = ('id',)

    def get_client_name(self, obj):
        return obj.client.name if obj.client else None


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'hours_cost', 'description', 'status',
                  'contacts', 'client', 'performer', 'fire', 'drive')
        read_only_fields = ('id',)


class TaskDetailSerializer(serializers.ModelSerializer):
    mail = MailSerializer(read_only=True)
    client = ClientSerializer(read_only=True)
    date_created = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    date_closed = serializers.DateTimeField(format='%H:%M %d-%m-%Y')
    performer_info = PerformerSerializer(read_only=True, source='performer')
    is_related = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'contacts', 'mail', 'client',
                  'performer', 'performer_info', 'hours_cost', 'fire', 'drive',
                  'date_created', 'date_closed', 'created_from', 'description',
                  'is_related')
        read_only_fields = ('id',)

    def get_is_related(self, obj):
        try:
            task_contact = obj.contacts
            if task_contact and len(task_contact) > 1 and '@' in task_contact:
                exist_user = User.objects.filter(email=task_contact).first()
                if not exist_user:
                    Contact.objects.get(contact=obj.contacts)
            return True
        except Contact.DoesNotExist:
            return False


class CommentSerializer(serializers.ModelSerializer):
    performer_info = PerformerSerializer(read_only=True, source='performer')
    date_created = serializers.DateTimeField(format='%d-%m-%Y %H:%M',
                                             required=False)
    avatar = serializers.URLField(required=False)

    class Meta:
        model = Comment
        fields = '__all__'
