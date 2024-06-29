# Additional Services

Этот пакет предназначен для работы с услугами. 
Пакет состоит из трех моделей, описанных ниже.

### AdditionalService

* `id`
* `name`
* `description`
* `pictures` - ManyToMany с AdditionalServicePicture
* `telegram_contact_link`
* `price_string`
* `created_at` and `updated_at`

### AdditionalServicePicture

* `house`
* `picture`

## Зависимости

В этом пакете не должно быть никаких зависимостей кроме `core`