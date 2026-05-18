"""
Модели данных для железнодорожной системы управления
Содержит все ключевые сущности предметной области
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid


# ===== Вспомогательные перечисления (Enums) =====

class TrainStatus(Enum):
    """Статус движения поезда"""
    ON_TIME = "По расписанию"
    DELAYED = "Задерживается"
    DEPARTED = "Отправился"
    ARRIVED = "Прибыл"
    CANCELLED = "Отменён"
    IN_TRANSIT = "В пути"


class StationType(Enum):
    """Тип железнодорожной станции"""
    PASSENGER = "Пассажирская"
    FREIGHT = "Грузовая"
    SORTING = "Сортировочная"
    INTERMODAL = "Интермодальная"


class TicketClass(Enum):
    """Класс обслуживания в поезде"""
    FIRST = "Первый класс"
    SECOND = "Второй класс"
    THIRD = "Третий класс"
    BUSINESS = "Бизнес класс"
    ECONOMY = "Эконом класс"


class MaintenanceType(Enum):
    """Тип технического обслуживания"""
    INSPECTION = "Плановый осмотр"
    REPAIR = "Ремонт"
    CLEANING = "Уборка и санитарная обработка"
    FUELING = "Заправка топливом"
    EMERGENCY = "Экстренное обслуживание"
    SCHEDULED = "Регламентное ТО"


class PaymentStatus(Enum):
    """Статус оплаты билета"""
    PENDING = "Ожидает оплаты"
    COMPLETED = "Оплачен"
    FAILED = "Ошибка оплаты"
    REFUNDED = "Возвращен"


class SafetyCheckStatus(Enum):
    """Результат проверки безопасности"""
    PASSED = "Пройдена"
    FAILED = "Не пройдена"
    PARTIAL = "Частично пройдена"
    REQUIRES_REINSPECTION = "Требуется перепроверка"


# ===== Базовый класс для всех сущностей =====

class Entity:
    """Абстрактный базовый класс для всех сущностей системы"""

    def __init__(self, entity_id: str):
        self._id = entity_id
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

    @property
    def id(self) -> str:
        """Уникальный идентификатор сущности"""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Дата и время создания"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Дата и время последнего обновления"""
        return self._updated_at

    def update_timestamp(self) -> None:
        """Обновить временную метку"""
        self._updated_at = datetime.now()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return False
        return self._id == other._id

    def __hash__(self) -> int:
        return hash(self._id)


# ===== Основные классы-сущности =====

class RailwayTrack(Entity):
    """
    Сущность: железнодорожный путь

    Атрибуты:
        - track_id: str - уникальный идентификатор пути
        - name: str - название пути
        - track_type: str - тип пути (главный, боковой, тупик и т.д.)
        - is_occupied: bool - занят ли путь в данный момент
        - length_km: float - длина пути в километрах
        - max_speed: int - максимальная скорость на пути (км/ч)
        - electrified: bool - электрифицирован ли путь
        - owner: str - владелец пути (РЖД, частная компания и т.д.)
        - occupied_by_train_id: Optional[str] - ID поезда, который занимает путь
    """

    def __init__(self, track_id: str, name: str, length_km: float, max_speed: int,
                 track_type: str = "main", electrified: bool = True, owner: str = "RZD"):
        super().__init__(track_id)
        self.name = name
        self.track_type = track_type
        self.length_km = length_km
        self.max_speed = max_speed
        self.electrified = electrified
        self.owner = owner
        self.is_occupied = False
        self.occupied_by_train_id: Optional[str] = None
        self.condition_score: float = 100.0  # Состояние пути в процентах
        self.last_inspection_date: Optional[datetime] = None

    def occupy(self, train_id: str) -> None:
        """
        Занять путь поездом

        Args:
            train_id: ID поезда, который занимает путь

        Raises:
            ValueError: Если путь уже занят
        """
        if self.is_occupied:
            raise ValueError(f"Путь {self.name} уже занят поездом {self.occupied_by_train_id}")
        self.is_occupied = True
        self.occupied_by_train_id = train_id
        self.update_timestamp()

    def release(self) -> None:
        """Освободить путь"""
        self.is_occupied = False
        self.occupied_by_train_id = None
        self.update_timestamp()

    def is_available(self) -> bool:
        """Проверить, доступен ли путь для использования"""
        return not self.is_occupied and self.condition_score > 70.0

    def update_condition(self, new_score: float) -> None:
        """
        Обновить состояние пути

        Args:
            new_score: Новый показатель состояния (0-100)
        """
        if 0 <= new_score <= 100:
            self.condition_score = new_score
            self.last_inspection_date = datetime.now()
            self.update_timestamp()

    def __str__(self) -> str:
        status = "Занят" if self.is_occupied else "Свободен"
        condition = "Хорошее" if self.condition_score > 70 else "Требует ремонта"
        return (f"Путь '{self.name}' (ID: {self.id}), тип: {self.track_type}, "
                f"{self.length_km}км, макс. скорость {self.max_speed}км/ч, "
                f"статус: {status}, состояние: {condition}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь для сериализации"""
        return {
            'id': self.id,
            'name': self.name,
            'track_type': self.track_type,
            'length_km': self.length_km,
            'max_speed': self.max_speed,
            'electrified': self.electrified,
            'owner': self.owner,
            'is_occupied': self.is_occupied,
            'occupied_by_train_id': self.occupied_by_train_id,
            'condition_score': self.condition_score,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Station(Entity):
    """
    Сущность: железнодорожная станция

    Атрибуты:
        - station_id: str - уникальный идентификатор станции
        - name: str - название станции
        - station_type: StationType - тип станции
        - city: str - город расположения
        - platforms: int - количество пассажирских платформ
        - cargo_platforms: int - количество грузовых платформ
        - tracks_at_station: List[str] - список ID путей, ведущих к станции
        - is_active: bool - работает ли станция
        - daily_capacity: int - дневная пропускная способность (поездов)
    """

    def __init__(self, station_id: str, name: str, station_type: StationType,
                 city: str, platforms: int, cargo_platforms: int = 0,
                 daily_capacity: int = 100):
        super().__init__(station_id)
        self.name = name
        self.station_type = station_type
        self.city = city
        self.platforms = platforms
        self.cargo_platforms = cargo_platforms
        self.tracks_at_station: List[str] = []
        self.is_active = True
        self.daily_capacity = daily_capacity
        self.trains_handled_today: int = 0
        self.workers_count: int = 50
        self.opening_time = "00:00"
        self.closing_time = "23:59"

    def add_track(self, track_id: str) -> None:
        """
        Добавить путь к станции

        Args:
            track_id: ID добавляемого пути
        """
        if track_id not in self.tracks_at_station:
            self.tracks_at_station.append(track_id)
            self.update_timestamp()

    def remove_track(self, track_id: str) -> None:
        """Удалить путь от станции"""
        if track_id in self.tracks_at_station:
            self.tracks_at_station.remove(track_id)
            self.update_timestamp()

    def get_total_platforms(self) -> int:
        """Получить общее количество платформ"""
        return self.platforms + self.cargo_platforms

    def can_handle_train(self) -> bool:
        """Проверить, может ли станция принять еще один поезд сегодня"""
        return self.trains_handled_today < self.daily_capacity

    def increment_trains_handled(self) -> None:
        """Увеличить счетчик обработанных поездов"""
        self.trains_handled_today += 1
        self.update_timestamp()

    def reset_daily_counter(self) -> None:
        """Сбросить счетчик обработанных поездов (новый день)"""
        self.trains_handled_today = 0
        self.update_timestamp()

    def activate(self) -> None:
        """Активировать станцию"""
        self.is_active = True
        self.update_timestamp()

    def deactivate(self) -> None:
        """Деактивировать станцию"""
        self.is_active = False
        self.update_timestamp()

    def __str__(self) -> str:
        status = "Активна" if self.is_active else "Неактивна"
        return (f"Станция '{self.name}' (ID: {self.id}), город: {self.city}, "
                f"тип: {self.station_type.value}, платформ: {self.get_total_platforms()}, "
                f"статус: {status}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'station_type': self.station_type.value,
            'city': self.city,
            'platforms': self.platforms,
            'cargo_platforms': self.cargo_platforms,
            'tracks_at_station': self.tracks_at_station,
            'is_active': self.is_active,
            'daily_capacity': self.daily_capacity,
            'trains_handled_today': self.trains_handled_today,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Locomotive(Entity):
    """
    Сущность: локомотив (тяговая единица)

    Атрибуты:
        - loco_id: str - уникальный номер локомотива
        - model: str - модель
        - power_kw: int - мощность в киловаттах
        - is_operational: bool - исправен ли
        - last_maintenance_date: datetime - дата последнего ТО
        - total_distance_km: float - общий пробег в км
        - fuel_type: str - тип топлива (дизель, электричество)
        - maintenance_history: List[MaintenanceRecord] - история обслуживания
    """

    def __init__(self, loco_id: str, model: str, power_kw: int,
                 fuel_type: str = "electric", max_speed: int = 120):
        super().__init__(loco_id)
        self.model = model
        self.power_kw = power_kw
        self.fuel_type = fuel_type
        self.max_speed = max_speed
        self.is_operational = True
        self.last_maintenance_date = datetime.now()
        self.total_distance_km: float = 0.0
        self.maintenance_history: List['MaintenanceRecord'] = []
        self.current_train_id: Optional[str] = None

    def perform_maintenance(self, maintenance_type: MaintenanceType = MaintenanceType.SCHEDULED) -> None:
        """
        Провести техническое обслуживание

        Args:
            maintenance_type: Тип обслуживания
        """
        from models import MaintenanceRecord  # Локальный импорт для избежания циклической зависимости

        self.is_operational = True
        self.last_maintenance_date = datetime.now()
        record = MaintenanceRecord(
            record_id=str(uuid.uuid4()),
            entity_type="locomotive",
            entity_id=self.id,
            maintenance_type=maintenance_type,
            notes=f"Проведено ТО локомотива {self.model}"
        )
        self.maintenance_history.append(record)
        self.update_timestamp()

    def set_broken(self, reason: str = "Unknown") -> None:
        """
        Отметить как неисправный

        Args:
            reason: Причина неисправности
        """
        self.is_operational = False
        self.update_timestamp()

    def add_distance(self, km: float) -> None:
        """
        Добавить пройденное расстояние

        Args:
            km: Пройденные километры
        """
        if km > 0:
            self.total_distance_km += km
            self.update_timestamp()

    def assign_to_train(self, train_id: str) -> None:
        """Привязать локомотив к поезду"""
        self.current_train_id = train_id
        self.update_timestamp()

    def detach_from_train(self) -> None:
        """Отвязать локомотив от поезда"""
        self.current_train_id = None
        self.update_timestamp()

    def needs_maintenance(self) -> bool:
        """Проверить, требуется ли обслуживание"""
        days_since_maintenance = (datetime.now() - self.last_maintenance_date).days
        return days_since_maintenance > 30 or not self.is_operational

    def __str__(self) -> str:
        status = "Исправен" if self.is_operational else "Неисправен"
        fuel_type_ru = "электрический" if self.fuel_type == "electric" else "дизельный"
        return (f"Локомотив {self.model} (№{self.id}), мощность: {self.power_kw}кВт, "
                f"тип: {fuel_type_ru}, статус: {status}, пробег: {self.total_distance_km:.1f}км")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'model': self.model,
            'power_kw': self.power_kw,
            'fuel_type': self.fuel_type,
            'max_speed': self.max_speed,
            'is_operational': self.is_operational,
            'last_maintenance_date': self.last_maintenance_date.isoformat() if self.last_maintenance_date else None,
            'total_distance_km': self.total_distance_km,
            'current_train_id': self.current_train_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Wagon(Entity):
    """
    Сущность: вагон

    Атрибуты:
        - wagon_id: str - уникальный номер вагона
        - wagon_type: str - тип вагона (passenger/cargo/luggage/restaurant)
        - capacity: int - вместимость (пассажиры) или грузоподъемность (тонны)
        - is_operational: bool - исправен ли
        - current_train_id: Optional[str] - ID текущего поезда
        - comfort_level: str - уровень комфорта (economy/business/first)
        - features: List[str] - особенности (кондиционер, wi-fi и т.д.)
    """

    def __init__(self, wagon_id: str, wagon_type: str, capacity: int,
                 comfort_level: str = "economy", features: Optional[List[str]] = None):
        super().__init__(wagon_id)
        self.wagon_type = wagon_type  # passenger, cargo, luggage, restaurant, sleeping
        self.capacity = capacity
        self.comfort_level = comfort_level
        self.features = features if features else []
        self.is_operational = True
        self.current_train_id: Optional[str] = None
        self.last_repair_date: Optional[datetime] = None

    def repair(self) -> None:
        """Починить вагон"""
        self.is_operational = True
        self.last_repair_date = datetime.now()
        self.update_timestamp()

    def set_broken(self, reason: str = "Unknown") -> None:
        """Отметить как неисправный"""
        self.is_operational = False
        self.update_timestamp()

    def assign_to_train(self, train_id: str) -> None:
        """Прицепить вагон к поезду"""
        self.current_train_id = train_id
        self.update_timestamp()

    def detach_from_train(self) -> None:
        """Отцепить вагон от поезда"""
        self.current_train_id = None
        self.update_timestamp()

    def get_capacity_display(self) -> str:
        """Получить отображаемую вместимость с единицами измерения"""
        if self.wagon_type == "cargo":
            return f"{self.capacity} тонн"
        elif self.wagon_type == "passenger" or self.wagon_type == "sleeping":
            return f"{self.capacity} мест"
        else:
            return f"{self.capacity} единиц"

    def __str__(self) -> str:
        status = "Исправен" if self.is_operational else "Требует ремонта"
        features_str = ", ".join(self.features) if self.features else "стандарт"
        return (f"Вагон {self.id} ({self.wagon_type}), "
                f"вместимость: {self.get_capacity_display()}, "
                f"класс: {self.comfort_level}, особенности: {features_str}, "
                f"статус: {status}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'wagon_type': self.wagon_type,
            'capacity': self.capacity,
            'comfort_level': self.comfort_level,
            'features': self.features,
            'is_operational': self.is_operational,
            'current_train_id': self.current_train_id,
            'last_repair_date': self.last_repair_date.isoformat() if self.last_repair_date else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Train(Entity):
    """
    Сущность: поезд

    Атрибуты:
        - train_id: str - уникальный номер поезда
        - name: str - название поезда (например 'Сапсан')
        - locomotive: Locomotive - локомотив поезда
        - wagons: List[Wagon] - список вагонов
        - route: List[str] - список ID станций маршрута
        - status: TrainStatus - статус движения поезда
        - current_station_index: int - индекс текущей станции в маршруте
        - delay_minutes: int - задержка в минутах
    """

    def __init__(self, train_id: str, name: str, locomotive: Locomotive):
        super().__init__(train_id)
        self.name = name
        self.locomotive = locomotive
        self.wagons: List[Wagon] = []
        self.route: List[str] = []  # Список ID станций в порядке следования
        self.status = TrainStatus.ON_TIME
        self.current_station_index = 0
        self.delay_minutes: int = 0
        self.passenger_count: int = 0
        locomotive.assign_to_train(train_id)

    def add_wagon(self, wagon: Wagon) -> None:
        """
        Добавить вагон к поезду

        Args:
            wagon: Вагон для добавления

        Raises:
            ValueError: Если вагон неисправен или уже прицеплен к другому поезду
        """
        if not wagon.is_operational:
            raise ValueError(f"Вагон {wagon.id} неисправен и не может быть добавлен")
        if wagon.current_train_id is not None:
            raise ValueError(f"Вагон {wagon.id} уже прицеплен к поезду {wagon.current_train_id}")

        self.wagons.append(wagon)
        wagon.assign_to_train(self.id)
        self.update_timestamp()

    def remove_wagon(self, wagon_id: str) -> None:
        """
        Отцепить вагон

        Args:
            wagon_id: ID вагона для отцепления

        Raises:
            ValueError: Если вагон не найден в составе
        """
        for wagon in self.wagons:
            if wagon.id == wagon_id:
                self.wagons.remove(wagon)
                wagon.detach_from_train()
                self.update_timestamp()
                return
        raise ValueError(f"Вагон {wagon_id} не найден в составе поезда {self.id}")

    def set_route(self, route_station_ids: List[str]) -> None:
        """
        Установить маршрут следования

        Args:
            route_station_ids: Список ID станций по порядку
        """
        self.route = route_station_ids
        self.current_station_index = 0
        self.update_timestamp()

    def move_to_next_station(self) -> Optional[str]:
        """
        Переместить поезд на следующую станцию

        Returns:
            Optional[str]: ID следующей станции или None, если это конечная
        """
        if self.current_station_index < len(self.route) - 1:
            self.current_station_index += 1
            self.status = TrainStatus.IN_TRANSIT
            self.update_timestamp()
            return self.route[self.current_station_index]
        else:
            self.status = TrainStatus.ARRIVED
            self.update_timestamp()
            return None

    def get_current_station(self) -> Optional[str]:
        """Получить ID текущей станции"""
        if self.route and self.current_station_index < len(self.route):
            return self.route[self.current_station_index]
        return None

    def delay(self, minutes: int) -> None:
        """
        Задержать поезд

        Args:
            minutes: Количество минут задержки
        """
        self.delay_minutes += minutes
        self.status = TrainStatus.DELAYED
        self.update_timestamp()

    def get_operational_status(self) -> Dict[str, Any]:
        """Получить статус исправности всего состава"""
        return {
            'locomotive_operational': self.locomotive.is_operational,
            'wagons_operational': [w.is_operational for w in self.wagons],
            'all_operational': self.locomotive.is_operational and all(w.is_operational for w in self.wagons),
            'needs_maintenance': self.locomotive.needs_maintenance()
        }

    def get_total_capacity(self) -> int:
        """Получить общую пассажировместимость поезда"""
        capacity = 0
        for wagon in self.wagons:
            if wagon.wagon_type in ['passenger', 'sleeping']:
                capacity += wagon.capacity
        return capacity

    def __str__(self) -> str:
        route_preview = " -> ".join(self.route[:3])
        if len(self.route) > 3:
            route_preview += "..."
        delay_info = f" (задержка {self.delay_minutes} мин)" if self.delay_minutes > 0 else ""
        return (f"Поезд '{self.name}' (№{self.id}), статус: {self.status.value}{delay_info}, "
                f"вагонов: {len(self.wagons)}, маршрут: {route_preview}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'locomotive_id': self.locomotive.id,
            'wagons_ids': [w.id for w in self.wagons],
            'route': self.route,
            'status': self.status.value,
            'current_station_index': self.current_station_index,
            'delay_minutes': self.delay_minutes,
            'passenger_count': self.passenger_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ScheduleEntry(Entity):
    """
    Сущность: элемент расписания

    Атрибуты:
        - schedule_id: str - уникальный идентификатор
        - train_id: str - ID поезда
        - station_id: str - ID станции
        - arrival_time: datetime - время прибытия
        - departure_time: datetime - время отправления
        - platform: int - номер платформы
        - is_completed: bool - выполнено ли
        - actual_arrival_time: Optional[datetime] - фактическое время прибытия
        - actual_departure_time: Optional[datetime] - фактическое время отправления
    """

    def __init__(self, schedule_id: str, train_id: str, station_id: str,
                 arrival_time: datetime, departure_time: datetime, platform: int):
        super().__init__(schedule_id)
        self.train_id = train_id
        self.station_id = station_id
        self.arrival_time = arrival_time
        self.departure_time = departure_time
        self.platform = platform
        self.is_completed = False
        self.actual_arrival_time: Optional[datetime] = None
        self.actual_departure_time: Optional[datetime] = None
        self.delay_arrival_minutes: int = 0
        self.delay_departure_minutes: int = 0

    def mark_completed(self, actual_arrival_time: Optional[datetime] = None,
                       actual_departure_time: Optional[datetime] = None) -> None:
        """
        Отметить выполнение данного пункта расписания

        Args:
            actual_arrival_time: Фактическое время прибытия
            actual_departure_time: Фактическое время отправления
        """
        self.is_completed = True
        if actual_arrival_time:
            self.actual_arrival_time = actual_arrival_time
            self.delay_arrival_minutes = int((actual_arrival_time - self.arrival_time).total_seconds() / 60)
        if actual_departure_time:
            self.actual_departure_time = actual_departure_time
            self.delay_departure_minutes = int((actual_departure_time - self.departure_time).total_seconds() / 60)
        self.update_timestamp()

    def is_delayed(self) -> bool:
        """Проверить, есть ли задержка на этой станции"""
        return self.delay_arrival_minutes > 0 or self.delay_departure_minutes > 0

    def get_delay_info(self) -> str:
        """Получить информацию о задержке"""
        delays = []
        if self.delay_arrival_minutes > 0:
            delays.append(f"прибытие +{self.delay_arrival_minutes} мин")
        if self.delay_departure_minutes > 0:
            delays.append(f"отправление +{self.delay_departure_minutes} мин")
        return ", ".join(delays) if delays else "без задержки"

    def __str__(self) -> str:
        completion = "✓" if self.is_completed else "○"
        delay_info = f" ({self.get_delay_info()})" if self.is_completed and self.is_delayed() else ""
        return (f"{completion} Поезд {self.train_id} на станции {self.station_id}: "
                f"прибытие {self.arrival_time.strftime('%H:%M')}, "
                f"отправление {self.departure_time.strftime('%H:%M')}, "
                f"платформа {self.platform}{delay_info}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'train_id': self.train_id,
            'station_id': self.station_id,
            'arrival_time': self.arrival_time.isoformat(),
            'departure_time': self.departure_time.isoformat(),
            'platform': self.platform,
            'is_completed': self.is_completed,
            'actual_arrival_time': self.actual_arrival_time.isoformat() if self.actual_arrival_time else None,
            'actual_departure_time': self.actual_departure_time.isoformat() if self.actual_departure_time else None,
            'delay_arrival_minutes': self.delay_arrival_minutes,
            'delay_departure_minutes': self.delay_departure_minutes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Ticket(Entity):
    """
    Сущность: билет

    Атрибуты:
        - ticket_id: str - уникальный номер билета
        - train_id: str - ID поезда
        - passenger_name: str - ФИО пассажира
        - passenger_passport: Optional[str] - номер паспорта
        - from_station_id: str - станция отправления
        - to_station_id: str - станция назначения
        - departure_time: datetime - время отправления
        - price: float - цена билета
        - ticket_class: TicketClass - класс обслуживания
        - wagon_number: int - номер вагона
        - seat_number: int - номер места
        - is_valid: bool - действителен ли билет
        - payment_status: PaymentStatus - статус оплаты
    """

    def __init__(self, ticket_id: str, train_id: str, passenger_name: str,
                 from_station_id: str, to_station_id: str, departure_time: datetime,
                 price: float, ticket_class: TicketClass, wagon_number: int, seat_number: int,
                 passenger_passport: Optional[str] = None):
        super().__init__(ticket_id)
        self.train_id = train_id
        self.passenger_name = passenger_name
        self.passenger_passport = passenger_passport
        self.from_station_id = from_station_id
        self.to_station_id = to_station_id
        self.departure_time = departure_time
        self.price = price
        self.ticket_class = ticket_class
        self.wagon_number = wagon_number
        self.seat_number = seat_number
        self.is_valid = True
        self.payment_status = PaymentStatus.PENDING
        self.purchased_at = datetime.now()
        self.cancelled_at: Optional[datetime] = None
        self.refund_amount: float = 0.0

    def cancel(self) -> None:
        """Отменить/аннулировать билет"""
        if not self.is_valid:
            raise ValueError(f"Билет {self.id} уже был отменен")

        self.is_valid = False
        self.cancelled_at = datetime.now()

        # Расчет суммы возврата (упрощенно: 70% если отмена за 2+ дня)
        hours_before_departure = (self.departure_time - datetime.now()).total_seconds() / 3600
        if hours_before_departure > 48:
            self.refund_amount = self.price * 0.7
        elif hours_before_departure > 6:
            self.refund_amount = self.price * 0.3
        else:
            self.refund_amount = 0.0

        self.payment_status = PaymentStatus.REFUNDED
        self.update_timestamp()

    def mark_as_paid(self) -> None:
        """Отметить билет как оплаченный"""
        self.payment_status = PaymentStatus.COMPLETED
        self.update_timestamp()

    def is_refundable(self) -> bool:
        """Проверить, возможен ли возврат билета"""
        if not self.is_valid:
            return False
        hours_before_departure = (self.departure_time - datetime.now()).total_seconds() / 3600
        return hours_before_departure > 0

    def get_ticket_info(self) -> str:
        """Получить полную информацию о билете"""
        status = "Действителен" if self.is_valid else "Аннулирован"
        payment = "Оплачен" if self.payment_status == PaymentStatus.COMPLETED else "Не оплачен"
        return (f"Билет №{self.id}\n"
                f"Пассажир: {self.passenger_name}\n"
                f"Поезд: {self.train_id}\n"
                f"Маршрут: {self.from_station_id} → {self.to_station_id}\n"
                f"Отправление: {self.departure_time.strftime('%d.%m.%Y %H:%M')}\n"
                f"Место: вагон {self.wagon_number}, место {self.seat_number}\n"
                f"Класс: {self.ticket_class.value}\n"
                f"Цена: {self.price} руб.\n"
                f"Статус: {status}, оплата: {payment}")

    def __str__(self) -> str:
        status = "✓" if self.is_valid else "✗"
        payment = "💰" if self.payment_status == PaymentStatus.COMPLETED else "⏳"
        return (f"{status} {payment} Билет №{self.id}: {self.passenger_name}, "
                f"{self.train_id}, {self.from_station_id}→{self.to_station_id}, "
                f"{self.ticket_class.value}, {self.price} руб.")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'train_id': self.train_id,
            'passenger_name': self.passenger_name,
            'passenger_passport': self.passenger_passport,
            'from_station_id': self.from_station_id,
            'to_station_id': self.to_station_id,
            'departure_time': self.departure_time.isoformat(),
            'price': self.price,
            'ticket_class': self.ticket_class.value,
            'wagon_number': self.wagon_number,
            'seat_number': self.seat_number,
            'is_valid': self.is_valid,
            'payment_status': self.payment_status.value,
            'purchased_at': self.purchased_at.isoformat(),
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'refund_amount': self.refund_amount,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class MaintenanceRecord(Entity):
    """
    Сущность: запись о техническом обслуживании

    Атрибуты:
        - record_id: str - уникальный идентификатор записи
        - entity_type: str - тип обслуживаемой сущности (locomotive/wagon/track)
        - entity_id: str - ID обслуживаемой сущности
        - maintenance_type: MaintenanceType - тип обслуживания
        - performed_at: datetime - дата проведения
        - performed_by: str - кто проводил
        - notes: str - примечания
        - cost: float - стоимость
    """

    def __init__(self, record_id: str, entity_type: str, entity_id: str,
                 maintenance_type: MaintenanceType, notes: str = "",
                 performed_by: str = "System", cost: float = 0.0):
        super().__init__(record_id)
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.maintenance_type = maintenance_type
        self.performed_by = performed_by
        self.notes = notes
        self.cost = cost
        self.performed_at = datetime.now()

    def __str__(self) -> str:
        return (f"Запись ТО #{self.id}: {self.maintenance_type.value} для {self.entity_type} {self.entity_id}, "
                f"дата: {self.performed_at.strftime('%d.%m.%Y %H:%M')}, "
                f"стоимость: {self.cost} руб.")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'maintenance_type': self.maintenance_type.value,
            'performed_by': self.performed_by,
            'performed_at': self.performed_at.isoformat(),
            'notes': self.notes,
            'cost': self.cost,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class SafetyCheck(Entity):
    """
    Сущность: проверка безопасности

    Атрибуты:
        - check_id: str - уникальный идентификатор проверки
        - train_id: str - ID проверяемого поезда
        - check_time: datetime - время проверки
        - inspector: str - имя инспектора
        - status: SafetyCheckStatus - результат проверки
        - items_checked: Dict[str, bool] - список проверенных пунктов
        - comments: str - комментарии
    """

    def __init__(self, check_id: str, train_id: str, inspector: str):
        super().__init__(check_id)
        self.train_id = train_id
        self.check_time = datetime.now()
        self.inspector = inspector
        self.status = SafetyCheckStatus.PASSED
        self.items_checked: Dict[str, bool] = {}
        self.comments = ""

    def add_check_item(self, item_name: str, passed: bool) -> None:
        """Добавить пункт проверки"""
        self.items_checked[item_name] = passed
        self.update_timestamp()

    def calculate_status(self) -> SafetyCheckStatus:
        """Рассчитать итоговый статус проверки"""
        if not self.items_checked:
            return SafetyCheckStatus.FAILED

        passed_count = sum(1 for passed in self.items_checked.values() if passed)
        total_count = len(self.items_checked)

        if passed_count == total_count:
            return SafetyCheckStatus.PASSED
        elif passed_count >= total_count / 2:
            return SafetyCheckStatus.PARTIAL
        else:
            return SafetyCheckStatus.FAILED

    def complete_check(self) -> None:
        """Завершить проверку с расчетом статуса"""
        self.status = self.calculate_status()
        self.update_timestamp()

    def __str__(self) -> str:
        return (f"Проверка безопасности #{self.id}, поезд {self.train_id}, "
                f"результат: {self.status.value}, инспектор: {self.inspector}")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'train_id': self.train_id,
            'check_time': self.check_time.isoformat(),
            'inspector': self.inspector,
            'status': self.status.value,
            'items_checked': self.items_checked,
            'comments': self.comments,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class Route(Entity):
    """
    Сущность: маршрут движения поезда

    Атрибуты:
        - route_id: str - уникальный идентификатор маршрута
        - name: str - название маршрута
        - stations: List[str] - список ID станций
        - distances_km: List[float] - расстояния между станциями
        - total_distance_km: float - общая протяженность
    """

    def __init__(self, route_id: str, name: str):
        super().__init__(route_id)
        self.name = name
        self.stations: List[str] = []
        self.distances_km: List[float] = []
        self.total_distance_km = 0.0

    def add_station(self, station_id: str, distance_from_previous_km: float = 0.0) -> None:
        """
        Добавить станцию в маршрут

        Args:
            station_id: ID станции
            distance_from_previous_km: Расстояние от предыдущей станции
        """
        self.stations.append(station_id)
        if self.distances_km or distance_from_previous_km > 0:
            self.distances_km.append(distance_from_previous_km)
            self.total_distance_km += distance_from_previous_km
        self.update_timestamp()

    def get_station_index(self, station_id: str) -> Optional[int]:
        """Получить индекс станции в маршруте"""
        try:
            return self.stations.index(station_id)
        except ValueError:
            return None

    def __str__(self) -> str:
        stations_preview = " → ".join(self.stations[:5])
        if len(self.stations) > 5:
            stations_preview += "..."
        return (f"Маршрут '{self.name}' (ID: {self.id}), "
                f"станций: {len(self.stations)}, длина: {self.total_distance_km:.1f}км")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать объект в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'stations': self.stations,
            'distances_km': self.distances_km,
            'total_distance_km': self.total_distance_km,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }