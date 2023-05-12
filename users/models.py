from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user with the given email, and password."""
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Email", unique=True, blank=False)
    first_name = models.CharField('Имя', max_length=30, blank=False)
    last_name = models.CharField('Фамилия', max_length=30, blank=False)
    is_active = models.BooleanField('Активный', default=True)
    date_joined = models.DateTimeField('Регистрация', default=timezone.now)
    is_staff = models.BooleanField('staff status', default=False)
    background = models.ImageField(blank=False,
                                   default='season',
                                   upload_to='profile_images/bg/')
    avatar = models.ImageField("Аватар",
                               blank=False,
                               upload_to='profile_images',
                               default='default_avatar.png')
    notify_new_tasks = models.BooleanField(
        'Уведомлять на почту о новых задачах', default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
