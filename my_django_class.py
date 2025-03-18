from django.test import Client
from django.http import HttpResponse
from qase.pytest import qase
from qa_lib.logger import Logger
from typing import Any


class MyDjangoClient:
    client = Client()

    @staticmethod
    def request(
            method: str,
            path: str,
            data: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            content_type: str | None = None
    ) -> HttpResponse:
        """
        A universal method for all HTTP requests (GET, POST, PUT, PATCH, DELETE).
        Logs the request and response.
        """
        if method.upper() in {'GET', 'DELETE'}:
            content_type = None
        with qase.step(f'{method} request to URL "{path}" with data:\n{data}'):
            return MyDjangoClient._send(method, path, data, headers, content_type)

    @staticmethod
    def get(path: str, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
            content_type: str | None = None) -> HttpResponse:
        return MyDjangoClient.request('GET', path, data, headers)

    @staticmethod
    def post(path: str, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
             content_type: str | None = 'application/json') -> HttpResponse:
        return MyDjangoClient.request('POST', path, data, headers, content_type)

    @staticmethod
    def put(path: str, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
            content_type: str | None = 'application/json') -> HttpResponse:
        return MyDjangoClient.request('PUT', path, data, headers, content_type)

    @staticmethod
    def patch(path: str, data: dict[str, Any] | None = None, headers: dict[str, str] | None = None,
              content_type: str | None = 'application/json') -> HttpResponse:
        return MyDjangoClient.request('PATCH', path, data, headers, content_type)

    @staticmethod
    def delete(path: str, headers: dict[str, str] | None = None, content_type: str | None = None) -> HttpResponse:
        return MyDjangoClient.request('DELETE', path, None, headers)

    @staticmethod
    def _send(
            method: str,
            path: str,
            data: dict[str, Any] | None,
            headers: dict[str, str] | None,
            content_type: str | None = None
    ) -> HttpResponse:
        """
        Sends an HTTP request using Django test client.
        Logs the request and response.
        """
        headers = headers or {}

        # Log request
        Logger.add_request(url=path, data=data, headers=headers, method=method)

        # Prepare request arguments
        request_kwargs = {'path': path, 'data': data}
        if method in {'POST', 'PUT', 'PATCH'}:
            request_kwargs['content_type'] = content_type

        # Execute request dynamically
        try:
            response = getattr(MyDjangoClient.client, method.lower())(**request_kwargs)
        except AttributeError:
            raise ValueError(f'Invalid HTTP method "{method}"')

        # Log response
        Logger.add_response(
            status_code=response.status_code,
            response_body=response.content.decode('utf-8'),
            headers=response.headers
        )

        return response
