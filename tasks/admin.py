from django.contrib import admin

from tasks.models import Comment, Task


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'contacts', 'status',
                    'performer', 'date_created', 'date_closed')
    list_filter = ('status', 'performer', 'client', 'date_created')
    search_fields = ('title', 'description', 'contacts')
    ordering = ('-date_created',)
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'status', 'fire', 'drive')
        }),
        ('Исполнитель и клиент', {
            'fields': ('performer', 'client')
        }),
        ('Дополнительно', {
            'fields': ('hours_cost', 'contacts')
        }),
    )
    readonly_fields = ('date_created', 'date_closed')
    inlines = [CommentInline]
