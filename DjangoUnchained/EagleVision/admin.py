from django.contrib import admin
from django.apps import apps

# Register your models here.
# @admin.register(Student)
# class StudentAdmin(admin.ModelAdmin):
#     list_display = ('eagle_id', 'major_1', 'major_2', 'major_3', 'minor_1', 'minor_2', 'graduation_semester')
#     search_fields = ('eagle_id', 'major_1', 'minor_1')
#     list_filter = ('graduation_semester',)

app_models = apps.get_app_config('EagleVision').get_models()

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass

