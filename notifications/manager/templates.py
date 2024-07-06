NEW_RESERVATION_CREATED = """Было создано новое бронирование. 
Домик: {reservation_house_name} 
Даты: {reservation_check_in_datetime} - {reservation_check_out_datetime}
ID бронирования: {reservation_slug}
Ссылка: https://{host}/backend/admin/house_reservations/housereservation/{reservation_id}/
Имя клиента: {client_lastname} {client_firstname}
Контакт клиента: {preferred_contact}
Комментарий к бронированию: {reservation_comment}
"""

