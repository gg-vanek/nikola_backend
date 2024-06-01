from django.contrib import admin
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

from house_reservations_billing.json_mappers import ChronologicalPositionsEncoder, NonChronologicalPositionsEncoder
from house_reservations_billing.models.bill import HouseReservationBill
from house_reservations_billing.models.promocode import HouseReservationPromoCode


class HouseReservationBillAdmin(admin.ModelAdmin):
    model = HouseReservationBill
    exclude = (
        'chronological_positions',
        'non_chronological_positions',
    )
    readonly_fields = (
        'chronological_positions_prettified',
        'non_chronological_positions_prettified',
    )
    list_display = (
        'reservation',
        'total',
    )

    def chronological_positions_prettified(self, instance):
        response = ChronologicalPositionsEncoder().encode(instance.chronological_positions)
        formatter = HtmlFormatter(style="emacs")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    chronological_positions_prettified.short_description = 'Читаемый список хронологически упорядоченных позиций'

    def non_chronological_positions_prettified(self, instance):
        response = NonChronologicalPositionsEncoder().encode(instance.non_chronological_positions)
        formatter = HtmlFormatter(style="emacs")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    non_chronological_positions_prettified.short_description = 'Читаемый список хронологически неупорядоченных позиций'


class HouseReservationPromoCodeAdmin(admin.ModelAdmin):
    model = HouseReservationPromoCode
    list_display = (
        "id",
        "code",
        "enabled",
        "discount_type",
        "discount_value",
        "client",
        "max_use_times",
        "issuance_datetime",
        "expiration_datetime",
    )


admin.site.register(HouseReservationBill, HouseReservationBillAdmin)
admin.site.register(HouseReservationPromoCode, HouseReservationPromoCodeAdmin)
