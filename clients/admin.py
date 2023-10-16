from django.contrib import admin

from clients.models import Client


class ClientAdmin(admin.ModelAdmin):
    model = Client
    list_display = ("email",
                    "first_name", "last_name",
                    "created_at", "updated_at",)


admin.site.register(Client, ClientAdmin)
