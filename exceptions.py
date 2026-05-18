"""
Пользовательские исключения для железнодорожной системы управления
Все исключения наследуются от базового класса RailwayException
"""

from typing import Optional, Any


class RailwayException(Exception):
    """
    Базовый класс для всех исключений в железнодорожной системе.
    Все пользовательские исключения должны наследоваться от этого класса.
    """

    def __init__(self, message: str, details: Optional[Any] = None):
        """
        Инициализация базового исключения

        Args:
            message: Сообщение об ошибке
            details: Дополнительная информация об ошибке (опционально)
        """
        super().__init__(message)
        self.message = message
        self.details = details

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Детали: {self.details})"
        return self.message


# ===== Исключения для аутентификации и пользователей =====

class AuthenticationError(RailwayException):
    """Ошибка аутентификации пользователя"""
    pass


class UserNotFoundError(RailwayException):
    """Пользователь не найден в системе"""
    pass


class UserAlreadyExistsError(RailwayException):
    """Пользователь с таким email уже существует"""
    pass


class InvalidPasswordError(RailwayException):
    """Неверный пароль"""
    pass


class NotAuthenticatedError(RailwayException):
    """Пользователь не авторизован для выполнения операции"""
    pass


class PermissionDeniedError(RailwayException):
    """Недостаточно прав для выполнения операции"""
    pass


class InvalidEmailError(RailwayException):
    """Некорректный формат email"""
    pass


# ===== Исключения для железнодорожных путей =====

class TrackNotFoundError(RailwayException):
    """Железнодорожный путь не найден"""
    pass


class TrackOccupiedError(RailwayException):
    """Путь уже занят другим поездом"""
    pass


class TrackNotAvailableError(RailwayException):
    """Путь недоступен для использования (например, в плохом состоянии)"""
    pass


class TrackConditionError(RailwayException):
    """Ошибка состояния пути (требуется ремонт или обслуживание)"""
    pass


class InvalidTrackTypeError(RailwayException):
    """Некорректный тип железнодорожного пути"""
    pass


# ===== Исключения для станций =====

class StationNotFoundError(RailwayException):
    """Станция не найдена"""
    pass


class StationInactiveError(RailwayException):
    """Станция неактивна (закрыта на обслуживание или ремонт)"""
    pass


class StationAtCapacityError(RailwayException):
    """Станция достигла максимальной пропускной способности"""
    pass


class PlatformNotFoundError(RailwayException):
    """Платформа на станции не найдена"""
    pass


class PlatformOccupiedError(RailwayException):
    """Платформа уже занята другим поездом"""
    pass


class InvalidStationTypeError(RailwayException):
    """Некорректный тип станции для данной операции"""
    pass


# ===== Исключения для локомотивов =====

class LocomotiveNotFoundError(RailwayException):
    """Локомотив не найден"""
    pass


class LocomotiveNotOperationalError(RailwayException):
    """Локомотив неисправен и не может использоваться"""
    pass


class LocomotiveAlreadyAssignedError(RailwayException):
    """Локомотив уже привязан к другому поезду"""
    pass


class LocomotiveMaintenanceRequiredError(RailwayException):
    """Локомотив требует технического обслуживания"""
    pass


class LocomotivePowerInsufficientError(RailwayException):
    """Мощности локомотива недостаточно для состава"""
    pass


# ===== Исключения для вагонов =====

class WagonNotFoundError(RailwayException):
    """Вагон не найден"""
    pass


class WagonNotOperationalError(RailwayException):
    """Вагон неисправен и не может использоваться"""
    pass


class WagonAlreadyAssignedError(RailwayException):
    """Вагон уже прицеплен к другому поезду"""
    pass


class WagonTypeMismatchError(RailwayException):
    """Тип вагона не соответствует требованиям"""
    pass


class WagonLimitExceededError(RailwayException):
    """Превышен допустимый лимит вагонов в составе"""
    pass


# ===== Исключения для поездов =====

class TrainNotFoundError(RailwayException):
    """Поезд не найден"""
    pass


class TrainAlreadyExistsError(RailwayException):
    """Поезд с таким номером уже существует"""
    pass


class TrainNotOperationalError(RailwayException):
    """Поезд неисправен (локомотив или вагоны)"""
    pass


class RouteNotSetError(RailwayException):
    """Маршрут для поезда не задан"""
    pass


class TrainAtTerminalError(RailwayException):
    """Поезд находится на конечной станции, дальнейшее движение невозможно"""
    pass


class TrainAlreadyDepartedError(RailwayException):
    """Поезд уже отправился, операция невозможна"""
    pass


class TrainCancelledError(RailwayException):
    """Поезд отменен, операции с ним недоступны"""
    pass


class InvalidTrainStatusError(RailwayException):
    """Некорректный статус поезда для выполнения операции"""
    pass


# ===== Исключения для расписания =====

class ScheduleNotFoundError(RailwayException):
    """Элемент расписания не найден"""
    pass


class ScheduleConflictError(RailwayException):
    """Конфликт в расписании (время или платформа уже заняты)"""
    pass


class ScheduleEntryAlreadyCompletedError(RailwayException):
    """Пункт расписания уже выполнен"""
    pass


class InvalidScheduleTimeError(RailwayException):
    """Некорректное время в расписании (время отправления раньше прибытия и т.д.)"""
    pass


class ScheduleOverlapError(RailwayException):
    """Расписание пересекается с другим маршрутом на том же пути"""
    pass


# ===== Исключения для билетов =====

class TicketNotFoundError(RailwayException):
    """Билет не найден"""
    pass


class TicketAlreadyCancelledError(RailwayException):
    """Билет уже был отменен"""
    pass


class NoAvailableSeatsError(RailwayException):
    """Нет свободных мест на выбранный поезд"""
    pass


class InvalidTicketClassError(RailwayException):
    """Некорректный класс обслуживания билета"""
    pass


class TicketNotRefundableError(RailwayException):
    """Возврат билета невозможен (поезд уже отправился или до отправления менее 6 часов)"""
    pass


class SeatAlreadyBookedError(RailwayException):
    """Выбранное место уже забронировано"""
    pass


class InvalidPassengerDataError(RailwayException):
    """Некорректные данные пассажира (ФИО, паспорт)"""
    pass


class PaymentRequiredError(RailwayException):
    """Билет не оплачен, требуется оплата"""
    pass


# ===== Исключения для оплаты =====

class PaymentNotFoundError(RailwayException):
    """Платеж не найден"""
    pass


class PaymentAlreadyProcessedError(RailwayException):
    """Платеж уже был обработан"""
    pass


class PaymentFailedError(RailwayException):
    """Ошибка при обработке платежа"""
    pass


class InsufficientFundsError(RailwayException):
    """Недостаточно средств на счете"""
    pass


class PaymentTimeoutError(RailwayException):
    """Время ожидания оплаты истекло"""
    pass


# ===== Исключения для технического обслуживания =====

class MaintenanceRequiredError(RailwayException):
    """Требуется техническое обслуживание"""
    pass


class MaintenanceInProgressError(RailwayException):
    """Обслуживание уже проводится"""
    pass


class MaintenanceNotFoundError(RailwayException):
    """Запись о техническом обслуживании не найдена"""
    pass


class InvalidMaintenanceTypeError(RailwayException):
    """Некорректный тип технического обслуживания"""
    pass


class MaintenanceScheduleError(RailwayException):
    """Ошибка в графике технического обслуживания"""
    pass


# ===== Исключения для безопасности =====

class SafetyViolationError(RailwayException):
    """Нарушение правил безопасности"""
    pass


class SafetyCheckFailedError(RailwayException):
    """Проверка безопасности не пройдена"""
    pass


class SafetyCheckNotFoundError(RailwayException):
    """Запись о проверке безопасности не найдена"""
    pass


class SafetyEquipmentMissingError(RailwayException):
    """Отсутствует необходимое оборудование безопасности"""
    pass


class SpeedLimitViolationError(RailwayException):
    """Превышение допустимой скорости"""
    pass


class SignalViolationError(RailwayException):
    """Нарушение сигнальных показаний"""
    pass


# ===== Исключения для маршрутов =====

class RouteNotFoundError(RailwayException):
    """Маршрут не найден"""
    pass


class InvalidRouteError(RailwayException):
    """Некорректный маршрут (пропущены станции, нет связи и т.д.)"""
    pass


class RouteNotConnectedError(RailwayException):
    """Станции в маршруте не соединены железнодорожными путями"""
    pass


class StationNotInRouteError(RailwayException):
    """Станция отсутствует в маршруте"""
    pass


# ===== Общие исключения =====

class InvalidOperationError(RailwayException):
    """Некорректная операция для текущего состояния системы"""
    pass


class ValidationError(RailwayException):
    """Ошибка валидации входных данных"""
    pass


class DataNotFoundError(RailwayException):
    """Запрашиваемые данные не найдены в системе"""
    pass


class DataCorruptedError(RailwayException):
    """Данные повреждены или имеют некорректный формат"""
    pass


class DatabaseError(RailwayException):
    """Ошибка при работе с базой данных"""
    pass


class ConfigurationError(RailwayException):
    """Ошибка конфигурации системы"""
    pass


class ResourceNotFoundError(RailwayException):
    """Запрашиваемый ресурс не найден"""
    pass


class ResourceLimitExceededError(RailwayException):
    """Превышен лимит использования ресурсов"""
    pass


class TimeoutError(RailwayException):
    """Превышено время ожидания операции"""
    pass


class ServiceUnavailableError(RailwayException):
    """Сервис временно недоступен"""
    pass


# ===== Исключения для специфических железнодорожных операций =====

class DispatchError(RailwayException):
    """Ошибка при отправлении поезда"""
    pass


class ArrivalError(RailwayException):
    """Ошибка при приеме поезда на станцию"""
    pass


class CouplingError(RailwayException):
    """Ошибка при сцепке/расцепке вагонов"""
    pass


class LoadingError(RailwayException):
    """Ошибка при погрузке/выгрузке"""
    pass


class DocumentationError(RailwayException):
    """Ошибка в документации (накладные, разрешения и т.д.)"""
    pass


# ===== Исключения для внешних систем =====

class ExternalSystemError(RailwayException):
    """Ошибка при взаимодействии с внешней системой"""
    pass


class CommunicationError(RailwayException):
    """Ошибка связи с внешним сервисом"""
    pass


# ===== Исключения для отчетов и аналитики =====

class ReportGenerationError(RailwayException):
    """Ошибка при генерации отчета"""
    pass


class InvalidReportParameterError(RailwayException):
    """Некорректный параметр отчета"""
    pass


class ExportError(RailwayException):
    """Ошибка при экспорте данных"""
    pass


# ===== Функции-помощники для работы с исключениями =====

def wrap_exception(func):
    """
    Декоратор для обертки исключений.
    Преобразует стандартные исключения в пользовательские.

    Args:
        func: Функция, которую нужно обернуть

    Returns:
        Обернутая функция
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RailwayException:
            raise
        except ValueError as e:
            raise ValidationError(f"Ошибка валидации: {str(e)}", details=e)
        except KeyError as e:
            raise DataNotFoundError(f"Ключ не найден: {str(e)}", details=e)
        except IndexError as e:
            raise DataNotFoundError(f"Индекс вне диапазона: {str(e)}", details=e)
        except TypeError as e:
            raise ValidationError(f"Ошибка типа данных: {str(e)}", details=e)
        except Exception as e:
            raise RailwayException(f"Непредвиденная ошибка: {str(e)}", details=e)

    return wrapper


def safe_operation(default_value: Any = None):
    """
    Декоратор для безопасного выполнения операций.
    При возникновении исключения возвращает значение по умолчанию.

    Args:
        default_value: Значение, возвращаемое при ошибке

    Returns:
        Декоратор
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except RailwayException:
                return default_value
            except Exception:
                return default_value

        return wrapper

    return decorator


# ===== Словарь кодов ошибок для API =====

ERROR_CODES = {
    AuthenticationError: 1001,
    UserNotFoundError: 1002,
    UserAlreadyExistsError: 1003,
    InvalidPasswordError: 1004,
    NotAuthenticatedError: 1005,
    PermissionDeniedError: 1006,

    TrackNotFoundError: 2001,
    TrackOccupiedError: 2002,
    TrackNotAvailableError: 2003,

    StationNotFoundError: 3001,
    StationInactiveError: 3002,
    StationAtCapacityError: 3003,

    LocomotiveNotFoundError: 4001,
    LocomotiveNotOperationalError: 4002,

    WagonNotFoundError: 5001,
    WagonNotOperationalError: 5002,

    TrainNotFoundError: 6001,
    TrainNotOperationalError: 6002,
    RouteNotSetError: 6003,

    ScheduleNotFoundError: 7001,
    ScheduleConflictError: 7002,

    TicketNotFoundError: 8001,
    TicketAlreadyCancelledError: 8002,
    NoAvailableSeatsError: 8003,

    PaymentFailedError: 9001,
    InsufficientFundsError: 9002,

    SafetyViolationError: 10001,
    SafetyCheckFailedError: 10002,

    ValidationError: 11001,
    DataNotFoundError: 11002,
    InvalidOperationError: 11003,
}


def get_error_code(exception: RailwayException) -> int:
    """
    Получить числовой код ошибки для API

    Args:
        exception: Исключение

    Returns:
        Код ошибки или 0, если код не найден
    """
    return ERROR_CODES.get(type(exception), 0)