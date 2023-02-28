import requests
from api.api import Constants, Body


class TestForm:
    def test_auth_indo_step(self):
        endpoint = "/api/form/create/auth_info"
        response = requests.post(Constants.URL + endpoint, params=Constants.PARAMS,
                                 headers=Constants.HEADERS, json=Body.AUTH_INDO_STEP)
        assert response.status_code == 200, "Код статуса не 200"
        assert "Данные успешно сохранены/изменены на нулевом этапе" in response.text, "Текст ответа неверный"

    def test_credit_parameters_step(self):
        endpoint = "/api/form/create/credit_parameters_info"
        response = requests.post(Constants.URL + endpoint, params=Constants.PARAMS,
                                 headers=Constants.HEADERS, json=Body.CREDIT_PARAMETERS_STEP)
        assert response.status_code == 200, "Код статуса не 200"
        assert "Данные успешно сохранены/изменены на первом этапе" in response.text, "Текст ответа неверный"
