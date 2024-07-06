NEW_RESERVATION_CREATED = """From: {sender_email}
To: {receiver_email}
Subject: Вы забронировали домик "{reservation_house_name}"

Вы успешно забронировали домик. В ближайшее время с вами свяжется менеджер. 
Домик: {reservation_house_name} 
Даты: {reservation_check_in_datetime} - {reservation_check_out_datetime}
ID бронирования: {reservation_slug}
Ссылка: https://{host}/reservation/{reservation_slug}/
"""
