from rest_framework import serializers
from django.utils.timezone import now
from datetime import datetime as Datetime


class CalendarsParametersSerializer(serializers.Serializer):
    month = serializers.IntegerField()
    year = serializers.IntegerField()
    chosen_check_in_date = serializers.DateField(required=False, input_formats=['%d-%m-%Y'])
    total_persons_amount = serializers.IntegerField(min_value=1, default=1, required=False)

    class Meta:
        fields = (
            'month',
            'year',
            'chosen_check_in_date',
            'total_persons_amount',
        )

    def validate_chosen_check_in_date(self, date):
        if date <= now().date():
            raise serializers.ValidationError("chosen_check_in_date должна быть позже сегодняшнего дня.")

        return date

    def validate_year(self, year):
        if year < now().year:
            raise serializers.ValidationError("year не может быть меньше текущего года.")

        return year

    def validate_month(self, month):
        if month < 1 or month > 12:
            raise serializers.ValidationError("month должен быть в диапазоне от 1 до 12.")

        return month
