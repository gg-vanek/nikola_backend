# Houses

Этот пакет предназначен для работы с домиками. 
Пакет состоит из трех моделей, описанных ниже.

### House

* `name`
* `description`
* `features` - ManyToMany с HouseFeature
* `base_price`
* `holidays_multiplier`
* `base_persons_amount`
* `max_persons_amount`
* `price_per_extra_person`
* `created_at` and `updated_at`

### HouseFeature

* `name`
* `picture`

### HousePicture

* `house`
* `picture`

## Зависимости

В этом пакете не должно быть никаких зависимостей кроме `core`