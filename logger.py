import datetime
import logging
import os


class Logger:
    _initialized = False

    @staticmethod
    def _initialize(log_dir='logs'):
        if not Logger._initialized:
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f'log_{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.log')

            # Настраиваем логгер вручную
            logger = logging.getLogger('CustomLogger')
            logger.setLevel(logging.DEBUG)

            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
            logger.addHandler(file_handler)

            Logger._initialized = True

    @staticmethod
    def add_request(url: str, data: dict = None, headers: dict = None, method: str = 'GET'):
        Logger._initialize()  # Убедиться, что логгер инициализирован
        logger = logging.getLogger('CustomLogger')
        testname = os.environ.get('PYTEST_CURRENT_TEST', 'Unknown Test')

        logger.info('----- REQUEST START -----')
        logger.info(f'Test Name: {testname}')
        logger.info(f'Request Method: {method}')
        logger.info(f'Request URL: {url}')
        logger.info(f'Request Headers: {headers}')
        logger.info(f'Request Data: {data}')
        logger.info('----- REQUEST END -----')

    @staticmethod
    def add_response(status_code: int, response_body: str = '', headers: dict = None):
        Logger._initialize()  # Убедиться, что логгер инициализирован
        logger = logging.getLogger('CustomLogger')
        testname = os.environ.get('PYTEST_CURRENT_TEST', 'Unknown Test')

        logger.info('----- RESPONSE START -----')
        logger.info(f'Test Name: {testname}')
        logger.info(f'Response Code: {status_code}')
        logger.info(f'Response Headers: {headers}')
        logger.info(f'Response Body: {response_body}')
        logger.info('----- RESPONSE END -----')

    @staticmethod
    def log_message(message: str, level: str = 'info'):
        """
        Логирует произвольное сообщение с указанным уровнем.
        """
        Logger._initialize()  # Убедиться, что логгер инициализирован
        logger = logging.getLogger('CustomLogger')
        log_function = {
            'debug': logger.debug,
            'info': logger.info,
            'warning': logger.warning,
            'error': logger.error,
            'critical': logger.critical,
        }.get(level.lower(), logger.info)
        log_function(message)
