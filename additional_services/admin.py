from django.contrib import admin
from additional_services.models import AdditionalServicePicture, AdditionalService


class AdditionalServicePictureAdminInline(admin.TabularInline):
    model = AdditionalServicePicture


class AdditionalServiceAdmin(admin.ModelAdmin):
    model = AdditionalService
    list_display = (
        'name',
        'active',
        'price_string',
        'created_at',
    )
    inlines = [AdditionalServicePictureAdminInline, ]


admin.site.register(AdditionalService, AdditionalServiceAdmin)
