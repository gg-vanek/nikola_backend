from django.core.validators import RegexValidator

name_validator = RegexValidator(regex="^[0-9a-zA-Zа-яА-Я ,.'-_]+$",
                                message='Имя и фамилия должны состоять из только из цифр, "\
                                        "строчных и заглавных букв русского "\
                                        "и английского алфавитов, пробелов, а также из символов ",.\'-_")')
