# from django.db.models.signals import post_migrate
# from django.contrib.auth.models import Group, Permission
# from django.dispatch import receiver

# todo: new first initial method

# @receiver(post_migrate)
# def create_initial_groups(sender, **kwargs):
#     django.contrib.admin django.contrib.auth django.contrib.contenttypes
#     django.contrib.sessions rest_framework.authtoken
#     models

#     pass

#     if sender.name == 'django.contrib.auth':
#         group_admin, created = Group.objects.get_or_create(name='admin')
#         group_user, created = Group.objects.get_or_create(name='user')

#         permissions = Permission.objects.filter(codename__in=[
#             'add_user', 'change_user', 'delete_user', 'view_user',
#             'add_group', 'change_group', 'delete_group', 'view_group'
#         ])

#         group_admin.permissions.set(permissions)
#         group_user.permissions.set(permissions.filter(codename='view_user'))
#         print('Done!')
