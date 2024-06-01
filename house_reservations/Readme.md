# Houses

Этот пакет предназначен для работы с бронированием домиков. 
В пакете содержится единственная модель описанная ниже

### HouseReservation

* `slug`
* `house`
* `client`
* `check_in_datetime`
* `check_out_datetime`
* `total_persons_amount`
* `preferred_contact`
* `comment`
* `cancelled`
* `created_at`
* `updated_at`

## Зависимости

В этом пакете не должно быть никаких зависимостей кроме `houses`, `clients` и `core`
