
# House Reservation Billing

Пакет отвечающий за расчет стоимости бронирования домика.
В пакете содержатся следующие модели.

### HouseReservationBill

* `reservation`
* `total`
* `chronological_positions`
* `non_chronological_positions`
* `promo_code`
* `paid`

### HouseReservationPromoCode

* `house`
* `picture`

## Зависимости

В этом пакете не должно быть никаких зависимостей кроме `houses`, `house_reservations`, `clients`, `events` и `core`
