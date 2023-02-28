from random import randint


class Constants:
    URL = "http://130.193.52.217:8003" 
    PARAMS = {"user_id": randint(1, 100)}
    HEADERS = {
                "accept": "application/json",
                "Content-Type": "application/json",
            }


class Body:
    AUTH_INDO_STEP = {
            "user_agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
            "phone_number": "78888888888",
            "checkin_page": "https://sobank.online/",
            "sms_code": "2587"
        }

    CREDIT_PARAMETERS_STEP = {
          "credit_target": {
            "value": "credit_card",
            "title": "Кредитная карта"
          },
          "credit_sum": "130 000",
          "name": "Тест",
          "surname": "Тест",
          "patronymic": "Тест",
          "email": "test@mail.ru",
          "phone_number": "78888888888",
          "gender": {
            "value": "FEMALE",
            "title": "Женский"
          }
        }