from abc import ABC, abstractmethod
import re
import datetime
import socket
import sys


class LogLevel:
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


class LevelFilter:
    def __init__(self, allowed_levels):
        self.allowed_levels = allowed_levels

    def match(self, log_level, text):
        return log_level in self.allowed_levels


class LogFilterProtocol(ABC):
    @abstractmethod
    def match(self, log_level, text):
        pass


class SimpleLogFilter(LogFilterProtocol):
    def __init__(self, pattern):
        self.pattern = pattern

    def match(self, log_level, text):
        return self.pattern in text


class ReLogFilter(LogFilterProtocol):
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)

    def match(self, log_level, text):
        return self.pattern.search(text) is not None


class LevelFilter(LogFilterProtocol):
    def __init__(self, level):
        self.level = level

    def match(self, log_level, text):
        return log_level == self.level


class LogHandlerProtocol(ABC):
    @abstractmethod
    def handle(self, log_level, text):
        pass


class ConsoleHandler(LogHandlerProtocol):
    def handle(self, log_level, text):
        print(text)


class FileHandler(LogHandlerProtocol):
    def __init__(self, filename):
        self.filename = filename

    def handle(self, log_level, text):
        with open(self.filename, 'a') as f:
            f.write(text + '\n')


class SocketHandler(LogHandlerProtocol):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def handle(self, log_level, text):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(text.encode())


class SyslogHandler(LogHandlerProtocol):
    def handle(self, log_level, text):
        print(f"SYSLOG: {text}", file=sys.stderr)


class FtpHandler(LogHandlerProtocol):
    def __init__(self, host, username, password, filename):
        self.host = host
        self.username = username
        self.password = password
        self.filename = filename

    def handle(self, log_level, text):
        print(f"FTP {self.username}@{self.host}:{self.filename} <= {text}")


class LogFormatterProtocol(ABC):
    @abstractmethod
    def format(self, log_level, text):
        pass


class TimestampLevelFormatter(LogFormatterProtocol):
    def format(self, log_level, text):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y.%m.%d %H:%M:%S")
        return f"[{log_level}] [{timestamp}] {text}"


class Logger:
    def __init__(self, filters=None, formatters=None, handlers=None):
        self.filters = filters or []
        self.formatters = formatters or []
        self.handlers = handlers or []

    def log(self, log_level, text):
        if not all(f.match(log_level, text) for f in self.filters):
            return

        formatted_text = text
        for formatter in self.formatters:
            formatted_text = formatter.format(log_level, formatted_text)

        for handler in self.handlers:
            handler.handle(log_level, formatted_text)

    def log_info(self, text):
        self.log(LogLevel.INFO, text)

    def log_warn(self, text):
        self.log(LogLevel.WARN, text)

    def log_error(self, text):
        self.log(LogLevel.ERROR, text)


if __name__ == "__main__":
    level_filter = LevelFilter(LogLevel.WARN)

    formatter = TimestampLevelFormatter()

    console_handler = ConsoleHandler()
    file_handler = FileHandler("app.log")

    logger = Logger(
        filters=[level_filter],
        formatters=[formatter],
        handlers=[console_handler, file_handler]
    )

    # Тестируем
    logger.log_info("Это информационное сообщение")
    logger.log_warn("Это предупреждение")
    logger.log_error("Это ошибка")
