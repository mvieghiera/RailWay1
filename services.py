"""
Бизнес-логика железнодорожной системы управления
Содержит главный сервис, объединяющий все операции
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import uuid
from models import *
from exceptions import *


class RailwayService:
    """
    Главный сервис, объединяющий всю бизнес-логику железнодорожной системы.

    Основные операции:
    1. Движение поездов
    2. Обслуживание станций
    3. Техническое обслуживание
    4. Продажа билетов
    5. Контроль безопасности
    """

    def __init__(self):
        """Инициализация сервиса с пустыми хранилищами данных"""
        # Хранилища данных (в памяти)
        self.tracks: Dict[str, RailwayTrack] = {}
        self.stations: Dict[str, Station] = {}
        self.locomotives: Dict[str, Locomotive] = {}
        self.wagons: Dict[str, Wagon] = {}
        self.trains: Dict[str, Train] = {}
        self.schedule: Dict[str, ScheduleEntry] = {}
        self.tickets: Dict[str, Ticket] = {}
        self.maintenance_records: Dict[str, MaintenanceRecord] = {}
        self.safety_checks: Dict[str, SafetyCheck] = {}
        self.routes: Dict[str, Route] = {}

        # Состояние сессии (для CLI)
        self.current_user: Optional[str] = None
        self.current_user_role: str = "guest"  # guest, user, admin, dispatcher

        # Счетчики для генерации ID
        self._train_counter = 0
        self._ticket_counter = 0
        self._schedule_counter = 0
        self._maintenance_counter = 0
        self._safety_counter = 0
        self._route_counter = 0

        # Инициализация демонстрационными данными
        self._init_demo_data()

    def _init_demo_data(self) -> None:
        """Инициализация демонстрационных данных для тестирования"""
        # Добавляем тестовые станции
        moscow = self.add_station("Москва", StationType.PASSENGER, "Москва", 10, 5)
        spb = self.add_station("Санкт-Петербург", StationType.PASSENGER, "Санкт-Петербург", 8, 4)
        nnovgorod = self.add_station("Нижний Новгород", StationType.PASSENGER, "Нижний Новгород", 6, 3)
        kazan = self.add_station("Казань", StationType.PASSENGER, "Казань", 7, 3)

        # Добавляем тестовые пути
        track1 = RailwayTrack("TR_1", "Москва-Питер (главный)", 650.0, 200, "main", True)
        track2 = RailwayTrack("TR_2", "Москва-НН (главный)", 410.0, 160, "main", True)
        track3 = RailwayTrack("TR_3", "НН-Казань (главный)", 390.0, 160, "main", True)
        track4 = RailwayTrack("TR_4", "Запасной путь МСК", 45.0, 80, "side", False)

        self.tracks[track1.id] = track1
        self.tracks[track2.id] = track2
        self.tracks[track3.id] = track3
        self.tracks[track4.id] = track4

        # Привязываем пути к станциям
        moscow.add_track(track1.id)
        moscow.add_track(track2.id)
        moscow.add_track(track4.id)
        spb.add_track(track1.id)
        nnovgorod.add_track(track2.id)
        nnovgorod.add_track(track3.id)
        kazan.add_track(track3.id)

        # Добавляем тестовые локомотивы
        loco1 = Locomotive("L_1", "Сапсан-001", 8800, "electric", 250)
        loco2 = Locomotive("L_2", "Ласточка-101", 4000, "electric", 160)
        loco3 = Locomotive("L_3", "ВЛ80-202", 4000, "diesel", 120)
        loco4 = Locomotive("L_4", "ЭП20-303", 6000, "electric", 200)

        self.locomotives[loco1.id] = loco1
        self.locomotives[loco2.id] = loco2
        self.locomotives[loco3.id] = loco3
        self.locomotives[loco4.id] = loco4

        # Добавляем тестовые вагоны
        for i in range(1, 21):
            wagon_type = "passenger" if i % 3 != 0 else "cargo"
            comfort = "business" if i % 5 == 0 else "economy"
            wagon = Wagon(f"W_{i}", wagon_type, 50 if wagon_type == "passenger" else 60, comfort)
            self.wagons[wagon.id] = wagon

        # Создаем тестовые поезда
        train1 = Train("TN_1", "Сапсан 751А", loco1)
        train2 = Train("TN_2", "Ласточка 701И", loco2)
        train3 = Train("TN_3", "ВЛ80-202 (грузовой)", loco3)

        # Добавляем вагоны к поездам
        for i in range(1, 11):
            wagon = self.wagons.get(f"W_{i}")
            if wagon:
                train1.add_wagon(wagon)

        for i in range(11, 16):
            wagon = self.wagons.get(f"W_{i}")
            if wagon:
                train2.add_wagon(wagon)

        # Устанавливаем маршруты
        train1.set_route([moscow.id, spb.id])
        train2.set_route([moscow.id, nnovgorod.id, kazan.id])
        train3.set_route([moscow.id, nnovgorod.id])

        self.trains[train1.id] = train1
        self.trains[train2.id] = train2
        self.trains[train3.id] = train3

        # Добавляем расписание
        now = datetime.now()
        self._add_schedule_entry(train1.id, moscow.id, now + timedelta(hours=1), now + timedelta(hours=1, minutes=15),
                                 1)
        self._add_schedule_entry(train1.id, spb.id, now + timedelta(hours=5), now + timedelta(hours=5, minutes=15), 2)
        self._add_schedule_entry(train2.id, moscow.id, now + timedelta(hours=2), now + timedelta(hours=2, minutes=10),
                                 3)
        self._add_schedule_entry(train2.id, nnovgorod.id, now + timedelta(hours=5, minutes=30),
                                 now + timedelta(hours=5, minutes=45), 1)
        self._add_schedule_entry(train2.id, kazan.id, now + timedelta(hours=9), now + timedelta(hours=9, minutes=10), 2)

    def _add_schedule_entry(self, train_id: str, station_id: str,
                            arrival: datetime, departure: datetime, platform: int) -> None:
        """Вспомогательный метод для добавления записи в расписание"""
        self._schedule_counter += 1
        schedule_id = f"SCH_{self._schedule_counter}"
        entry = ScheduleEntry(schedule_id, train_id, station_id, arrival, departure, platform)
        self.schedule[schedule_id] = entry

    # ==================== ОПЕРАЦИЯ 1: ДВИЖЕНИЕ ПОЕЗДОВ ====================

    def move_train(self, train_id: str, track_id: str) -> Dict[str, Any]:
        """
        Переместить поезд на указанный путь.

        Args:
            train_id: ID поезда
            track_id: ID пути

        Returns:
            Dict с результатом операции

        Raises:
            TrainNotFoundError: Поезд не найден
            TrackNotFoundError: Путь не найден
            TrackOccupiedError: Путь уже занят
            LocomotiveNotOperationalError: Локомотив неисправен
            RouteNotSetError: Маршрут не задан
        """
        train = self._get_train(train_id)
        track = self._get_track(track_id)

        # Проверки безопасности
        if track.is_occupied:
            raise TrackOccupiedError(f"Путь {track.name} уже занят поездом {track.occupied_by_train_id}")

        if not train.locomotive.is_operational:
            raise LocomotiveNotOperationalError(f"Локомотив поезда {train.name} неисправен")

        if not train.route:
            raise RouteNotSetError(f"Маршрут для поезда {train.name} не задан")

        # Освободить предыдущий путь
        for t in self.tracks.values():
            if t.occupied_by_train_id == train_id:
                t.release()

        # Занять новый путь
        track.occupy(train_id)

        # Обновить статус поезда
        if train.status == TrainStatus.ON_TIME:
            train.status = TrainStatus.DEPARTED
        train.update_timestamp()

        # Добавляем расстояние к локомотиву
        train.locomotive.add_distance(track.length_km)

        return {
            'success': True,
            'train_id': train_id,
            'train_name': train.name,
            'track_id': track_id,
            'track_name': track.name,
            'message': f"Поезд {train.name} перемещен на путь {track.name}",
            'timestamp': datetime.now()
        }

    def get_train_location(self, train_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить текущее местоположение поезда.

        Args:
            train_id: ID поезда

        Returns:
            Dict с информацией о местоположении или None
        """
        train = self._get_train(train_id)

        for track_id, track in self.tracks.items():
            if track.occupied_by_train_id == train_id:
                return {
                    'train_id': train_id,
                    'train_name': train.name,
                    'track_id': track_id,
                    'track_name': track.name,
                    'track_length_km': track.length_km,
                    'current_station': train.get_current_station(),
                    'status': train.status.value
                }

        return None

    def advance_train_on_route(self, train_id: str) -> Optional[Dict[str, Any]]:
        """
        Переместить поезд на следующую станцию по маршруту.

        Args:
            train_id: ID поезда

        Returns:
            Dict с информацией о новой станции или None
        """
        train = self._get_train(train_id)

        next_station_id = train.move_to_next_station()
        if next_station_id:
            station = self._get_station(next_station_id)
            return {
                'success': True,
                'train_id': train_id,
                'train_name': train.name,
                'next_station_id': next_station_id,
                'next_station_name': station.name,
                'is_final': False
            }
        else:
            return {
                'success': True,
                'train_id': train_id,
                'train_name': train.name,
                'is_final': True,
                'message': f"Поезд {train.name} прибыл на конечную станцию"
            }

    # ==================== ОПЕРАЦИЯ 2: ОБСЛУЖИВАНИЕ СТАНЦИЙ ====================

    def add_station(self, name: str, station_type: StationType, city: str,
                    platforms: int, cargo_platforms: int = 0, daily_capacity: int = 100) -> Station:
        """
        Добавить новую станцию.

        Args:
            name: Название станции
            station_type: Тип станции
            city: Город
            platforms: Количество пассажирских платформ
            cargo_platforms: Количество грузовых платформ
            daily_capacity: Дневная пропускная способность

        Returns:
            Созданная станция
        """
        station_id = f"ST_{len(self.stations) + 1}"
        station = Station(station_id, name, station_type, city, platforms, cargo_platforms, daily_capacity)
        self.stations[station_id] = station
        return station

    def get_station_info(self, station_id: str) -> Dict[str, Any]:
        """
        Получить полную информацию о станции.

        Args:
            station_id: ID станции

        Returns:
            Dict с информацией о станции
        """
        station = self._get_station(station_id)

        # Получаем поезда на станции
        trains_at_station = self.get_trains_at_station(station_id)

        return {
            'station': station,
            'trains_count': len(trains_at_station),
            'trains': [{'id': t.id, 'name': t.name, 'status': t.status.value} for t in trains_at_station],
            'tracks_count': len(station.tracks_at_station),
            'utilization': (
                                       station.trains_handled_today / station.daily_capacity) * 100 if station.daily_capacity > 0 else 0
        }

    def get_trains_at_station(self, station_id: str) -> List[Train]:
        """
        Получить все поезда, находящиеся на станции.

        Args:
            station_id: ID станции

        Returns:
            Список поездов на станции
        """
        station = self._get_station(station_id)
        trains_at_station = []

        for track_id in station.tracks_at_station:
            track = self.tracks.get(track_id)
            if track and track.is_occupied and track.occupied_by_train_id:
                train = self.trains.get(track.occupied_by_train_id)
                if train:
                    trains_at_station.append(train)

        return trains_at_station

    def update_station_capacity(self, station_id: str, new_capacity: int) -> Station:
        """
        Обновить пропускную способность станции.

        Args:
            station_id: ID станции
            new_capacity: Новая дневная пропускная способность
        """
        station = self._get_station(station_id)
        station.daily_capacity = new_capacity
        station.update_timestamp()
        return station

    def record_train_at_station(self, station_id: str, train_id: str) -> None:
        """
        Зафиксировать прибытие/отправление поезда на станции.

        Args:
            station_id: ID станции
            train_id: ID поезда
        """
        station = self._get_station(station_id)
        train = self._get_train(train_id)

        if station.can_handle_train():
            station.increment_trains_handled()
        else:
            raise StationAtCapacityError(f"Станция {station.name} достигла максимальной пропускной способности")

    # ==================== ОПЕРАЦИЯ 3: ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ ====================

    def perform_maintenance(self, loco_id: str, maintenance_type: MaintenanceType = MaintenanceType.SCHEDULED,
                            performed_by: str = "System", cost: float = 0.0) -> MaintenanceRecord:
        """
        Провести техническое обслуживание локомотива.

        Args:
            loco_id: ID локомотива
            maintenance_type: Тип обслуживания
            performed_by: Кто проводит обслуживание
            cost: Стоимость обслуживания

        Returns:
            Запись о техническом обслуживании
        """
        locomotive = self._get_locomotive(loco_id)

        # Проводим обслуживание
        locomotive.perform_maintenance(maintenance_type)

        # Создаем запись
        self._maintenance_counter += 1
        record_id = f"MT_{self._maintenance_counter}"
        record = MaintenanceRecord(
            record_id=record_id,
            entity_type="locomotive",
            entity_id=loco_id,
            maintenance_type=maintenance_type,
            notes=f"Проведено ТО локомотива {locomotive.model}",
            performed_by=performed_by,
            cost=cost
        )

        self.maintenance_records[record_id] = record
        return record

    def repair_wagon(self, wagon_id: str, performed_by: str = "System", cost: float = 0.0) -> MaintenanceRecord:
        """
        Отремонтировать вагон.

        Args:
            wagon_id: ID вагона
            performed_by: Кто проводит ремонт
            cost: Стоимость ремонта

        Returns:
            Запись о ремонте
        """
        wagon = self._get_wagon(wagon_id)
        wagon.repair()

        self._maintenance_counter += 1
        record_id = f"MT_{self._maintenance_counter}"
        record = MaintenanceRecord(
            record_id=record_id,
            entity_type="wagon",
            entity_id=wagon_id,
            maintenance_type=MaintenanceType.REPAIR,
            notes=f"Проведен ремонт вагона {wagon_id}",
            performed_by=performed_by,
            cost=cost
        )

        self.maintenance_records[record_id] = record
        return record

    def get_operational_status(self, train_id: str) -> Dict[str, Any]:
        """
        Получить полный статус исправности поезда.

        Args:
            train_id: ID поезда

        Returns:
            Dict со статусом исправности
        """
        train = self._get_train(train_id)
        return train.get_operational_status()

    def schedule_maintenance(self, loco_id: str, scheduled_date: datetime) -> Dict[str, Any]:
        """
        Запланировать техническое обслуживание.

        Args:
            loco_id: ID локомотива
            scheduled_date: Запланированная дата
        """
        locomotive = self._get_locomotive(loco_id)

        return {
            'locomotive_id': loco_id,
            'locomotive_model': locomotive.model,
            'scheduled_date': scheduled_date,
            'needs_maintenance': locomotive.needs_maintenance(),
            'days_since_last': (datetime.now() - locomotive.last_maintenance_date).days,
            'status': 'scheduled'
        }

    def get_maintenance_history(self, entity_type: str, entity_id: str) -> List[MaintenanceRecord]:
        """
        Получить историю технического обслуживания для сущности.

        Args:
            entity_type: Тип сущности (locomotive/wagon/track)
            entity_id: ID сущности

        Returns:
            Список записей об обслуживании
        """
        history = []
        for record in self.maintenance_records.values():
            if record.entity_type == entity_type and record.entity_id == entity_id:
                history.append(record)
        return sorted(history, key=lambda x: x.performed_at, reverse=True)

    # ==================== ОПЕРАЦИЯ 4: ПРОДАЖА БИЛЕТОВ ====================

    def search_trains(self, from_station_id: str, to_station_id: str,
                      date: datetime) -> List[Dict[str, Any]]:
        """
        Найти поезда по маршруту на указанную дату.

        Args:
            from_station_id: Станция отправления
            to_station_id: Станция назначения
            date: Дата отправления

        Returns:
            Список доступных поездов с информацией
        """
        results = []

        # Получаем станции
        from_station = self._get_station(from_station_id)
        to_station = self._get_station(to_station_id)

        for schedule_entry in self.schedule.values():
            # Проверяем, что дата совпадает
            if schedule_entry.arrival_time.date() != date.date():
                continue

            # Проверяем, что станция отправления совпадает
            if schedule_entry.station_id != from_station_id:
                continue

            # Проверяем, что поезд существует
            train = self.trains.get(schedule_entry.train_id)
            if not train:
                continue

            # Проверяем, есть ли станция назначения в маршруте после текущей
            if to_station_id in train.route and train.route.index(to_station_id) > train.route.index(from_station_id):
                # Находим время прибытия на станцию назначения
                arrival_time = None
                for sch in self.schedule.values():
                    if sch.train_id == schedule_entry.train_id and sch.station_id == to_station_id:
                        arrival_time = sch.arrival_time
                        break

                results.append({
                    'train_id': train.id,
                    'train_name': train.name,
                    'from_station': from_station.name,
                    'to_station': to_station.name,
                    'departure_time': schedule_entry.departure_time,
                    'arrival_time': arrival_time,
                    'duration_minutes': int(
                        (arrival_time - schedule_entry.departure_time).total_seconds() / 60) if arrival_time else 0,
                    'available_seats': self._get_available_seats(train.id),
                    'status': train.status.value
                })

        return sorted(results, key=lambda x: x['departure_time'])

    def _get_available_seats(self, train_id: str) -> int:
        """
        Получить количество доступных мест на поезд.

        Args:
            train_id: ID поезда

        Returns:
            Количество свободных мест
        """
        train = self._get_train(train_id)
        total_capacity = train.get_total_capacity()

        # Подсчитываем проданные билеты на этот поезд
        tickets_sold = sum(1 for ticket in self.tickets.values()
                           if ticket.train_id == train_id and ticket.is_valid)

        return max(0, total_capacity - tickets_sold)

    def buy_ticket(self, train_id: str, passenger_name: str,
                   from_station_id: str, to_station_id: str,
                   departure_time: datetime, ticket_class: TicketClass,
                   wagon_number: int, seat_number: int,
                   passenger_passport: Optional[str] = None) -> Ticket:
        """
        Купить билет на поезд.

        Args:
            train_id: ID поезда
            passenger_name: ФИО пассажира
            from_station_id: Станция отправления
            to_station_id: Станция назначения
            departure_time: Время отправления
            ticket_class: Класс билета
            wagon_number: Номер вагона
            seat_number: Номер места
            passenger_passport: Номер паспорта (опционально)

        Returns:
            Купленный билет

        Raises:
            TrainNotFoundError: Поезд не найден
            NoAvailableSeatsError: Нет свободных мест
            SeatAlreadyBookedError: Место уже занято
        """
        train = self._get_train(train_id)

        # Проверяем наличие мест
        available_seats = self._get_available_seats(train_id)
        if available_seats <= 0:
            raise NoAvailableSeatsError(f"На поезд {train.name} нет свободных мест")

        # Проверяем, не занято ли конкретное место
        for ticket in self.tickets.values():
            if (ticket.is_valid and ticket.train_id == train_id and
                    ticket.wagon_number == wagon_number and ticket.seat_number == seat_number):
                raise SeatAlreadyBookedError(f"Место {seat_number} в вагоне {wagon_number} уже занято")

        # Расчет цены
        base_price = self._calculate_price(train, from_station_id, to_station_id, ticket_class)

        # Создаем билет
        self._ticket_counter += 1
        ticket_id = f"T_{self._ticket_counter}"

        ticket = Ticket(
            ticket_id=ticket_id,
            train_id=train_id,
            passenger_name=passenger_name,
            from_station_id=from_station_id,
            to_station_id=to_station_id,
            departure_time=departure_time,
            price=base_price,
            ticket_class=ticket_class,
            wagon_number=wagon_number,
            seat_number=seat_number,
            passenger_passport=passenger_passport
        )

        self.tickets[ticket_id] = ticket
        return ticket

    def _calculate_price(self, train: Train, from_station_id: str,
                         to_station_id: str, ticket_class: TicketClass) -> float:
        """
        Рассчитать стоимость билета.

        Args:
            train: Поезд
            from_station_id: Станция отправления
            to_station_id: Станция назначения
            ticket_class: Класс билета

        Returns:
            Стоимость билета
        """
        # Базовая цена за 100 км
        base_rate = 500.0

        # Примерное расстояние (в реальной системе нужно вычислять)
        estimated_distance = 500.0

        # Коэффициенты класса
        class_multipliers = {
            TicketClass.FIRST: 3.0,
            TicketClass.BUSINESS: 2.5,
            TicketClass.SECOND: 1.5,
            TicketClass.ECONOMY: 1.0,
            TicketClass.THIRD: 0.8
        }

        # Коэффициент скорости/престижности поезда
        train_multiplier = 1.0
        if "Сапсан" in train.name:
            train_multiplier = 2.0
        elif "Ласточка" in train.name:
            train_multiplier = 1.3

        price = (estimated_distance / 100) * base_rate * class_multipliers[ticket_class] * train_multiplier

        return round(price, 2)

    def cancel_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Отменить билет и вернуть деньги.

        Args:
            ticket_id: ID билета

        Returns:
            Dict с информацией о возврате
        """
        ticket = self._get_ticket(ticket_id)

        if not ticket.is_valid:
            raise TicketAlreadyCancelledError(f"Билет {ticket_id} уже был отменен")

        if not ticket.is_refundable():
            raise TicketNotRefundableError("Возврат билета невозможен (поезд уже отправился)")

        ticket.cancel()

        return {
            'ticket_id': ticket_id,
            'refund_amount': ticket.refund_amount,
            'original_price': ticket.price,
            'cancelled_at': ticket.cancelled_at,
            'message': f"Билет отменен. Возвращено {ticket.refund_amount} руб."
        }

    def pay_for_ticket(self, ticket_id: str) -> Ticket:
        """
        Оплатить билет.

        Args:
            ticket_id: ID билета
        """
        ticket = self._get_ticket(ticket_id)

        if ticket.payment_status == PaymentStatus.COMPLETED:
            raise PaymentAlreadyProcessedError("Билет уже оплачен")

        ticket.mark_as_paid()
        return ticket

    def get_user_tickets(self, passenger_name: str) -> List[Ticket]:
        """
        Получить все билеты пассажира.

        Args:
            passenger_name: Имя пассажира

        Returns:
            Список билетов
        """
        return [t for t in self.tickets.values() if t.passenger_name == passenger_name]

    # ==================== ОПЕРАЦИЯ 5: КОНТРОЛЬ БЕЗОПАСНОСТИ ====================

    def check_train_safety(self, train_id: str) -> Dict[str, Any]:
        """
        Провести полную проверку безопасности поезда перед отправлением.

        Args:
            train_id: ID поезда

        Returns:
            Dict с результатами проверки

        Raises:
            SafetyViolationError: При нарушении безопасности
        """
        train = self._get_train(train_id)
        issues = []
        checks_passed = True

        # Проверка 1: Локомотив исправен
        if not train.locomotive.is_operational:
            issues.append(f"Локомотив поезда {train.name} неисправен")
            checks_passed = False

        # Проверка 2: Все вагоны исправны
        for wagon in train.wagons:
            if not wagon.is_operational:
                issues.append(f"Вагон {wagon.id} поезда {train.name} неисправен")
                checks_passed = False

        # Проверка 3: Маршрут задан
        if not train.route:
            issues.append(f"Маршрут для поезда {train.name} не задан")
            checks_passed = False

        # Проверка 4: Путь свободен для отправления
        current_station = train.get_current_station()
        if current_station:
            station = self.stations.get(current_station)
            if station:
                # Проверяем наличие свободного пути от станции
                free_track_found = False
                for track_id in station.tracks_at_station:
                    track = self.tracks.get(track_id)
                    if track and not track.is_occupied:
                        free_track_found = True
                        break

                if not free_track_found:
                    issues.append(f"Нет свободных путей для отправления со станции {station.name}")
                    checks_passed = False

        # Проверка 5: Тормозная система (упрощенно)
        if train.locomotive.total_distance_km > 50000 and not train.locomotive.needs_maintenance():
            issues.append("Требуется дополнительная проверка тормозной системы")
            checks_passed = False

        if not checks_passed:
            raise SafetyViolationError(f"Проверка безопасности не пройдена: {'; '.join(issues)}")

        return {
            'train_id': train_id,
            'train_name': train.name,
            'safety_check_passed': True,
            'issues': [],
            'checks_performed': 5,
            'timestamp': datetime.now()
        }

    def perform_pre_departure_check(self, train_id: str, inspector: str = "System") -> SafetyCheck:
        """
        Выполнить полный предотправной контроль с записью.

        Args:
            train_id: ID поезда
            inspector: Имя инспектора

        Returns:
            Запись о проверке безопасности
        """
        # Выполняем проверку
        safety_result = self.check_train_safety(train_id)

        # Создаем запись
        self._safety_counter += 1
        check_id = f"SC_{self._safety_counter}"
        safety_check = SafetyCheck(check_id, train_id, inspector)

        # Добавляем пункты проверки
        safety_check.add_check_item("Локомотив исправен", True)
        safety_check.add_check_item("Вагоны исправны", True)
        safety_check.add_check_item("Маршрут задан", True)
        safety_check.add_check_item("Путь свободен", True)
        safety_check.add_check_item("Тормозная система", True)

        safety_check.complete_check()
        self.safety_checks[check_id] = safety_check

        return safety_check

    def get_safety_history(self, train_id: str) -> List[SafetyCheck]:
        """
        Получить историю проверок безопасности для поезда.

        Args:
            train_id: ID поезда

        Returns:
            Список проверок
        """
        return [sc for sc in self.safety_checks.values() if sc.train_id == train_id]

    def report_safety_incident(self, train_id: str, description: str, severity: str = "medium") -> Dict[str, Any]:
        """
        Сообщить о инциденте безопасности.

        Args:
            train_id: ID поезда
            description: Описание инцидента
            severity: Серьезность (low/medium/high/critical)
        """
        train = self._get_train(train_id)

        return {
            'incident_id': str(uuid.uuid4()),
            'train_id': train_id,
            'train_name': train.name,
            'description': description,
            'severity': severity,
            'reported_at': datetime.now(),
            'reported_by': self.current_user or "System",
            'status': 'reported'
        }

    # ==================== ДОПОЛНИТЕЛЬНЫЕ ОПЕРАЦИИ ====================

    def add_train(self, name: str, locomotive_id: str) -> Train:
        """
        Добавить новый поезд.

        Args:
            name: Название поезда
            locomotive_id: ID локомотива
        """
        locomotive = self._get_locomotive(locomotive_id)
        self._train_counter += 1
        train_id = f"TN_{self._train_counter}"
        train = Train(train_id, name, locomotive)
        self.trains[train_id] = train
        return train

    def add_wagon_to_train(self, train_id: str, wagon_id: str) -> None:
        """Добавить вагон к поезду"""
        train = self._get_train(train_id)
        wagon = self._get_wagon(wagon_id)
        train.add_wagon(wagon)

    def add_track(self, name: str, length_km: float, max_speed: int,
                  track_type: str = "main", electrified: bool = True) -> RailwayTrack:
        """Добавить новый железнодорожный путь"""
        track_id = f"TR_{len(self.tracks) + 1}"
        track = RailwayTrack(track_id, name, length_km, max_speed, track_type, electrified)
        self.tracks[track_id] = track
        return track

    def add_locomotive(self, model: str, power_kw: int, fuel_type: str = "electric",
                       max_speed: int = 120) -> Locomotive:
        """Добавить новый локомотив"""
        loco_id = f"L_{len(self.locomotives) + 1}"
        loco = Locomotive(loco_id, model, power_kw, fuel_type, max_speed)
        self.locomotives[loco_id] = loco
        return loco

    def add_wagon(self, wagon_type: str, capacity: int, comfort_level: str = "economy") -> Wagon:
        """Добавить новый вагон"""
        wagon_id = f"W_{len(self.wagons) + 1}"
        wagon = Wagon(wagon_id, wagon_type, capacity, comfort_level)
        self.wagons[wagon_id] = wagon
        return wagon

    def add_route(self, name: str, stations: List[Tuple[str, float]]) -> Route:
        """
        Добавить новый маршрут.

        Args:
            name: Название маршрута
            stations: Список кортежей (station_id, distance_from_previous)
        """
        self._route_counter += 1
        route_id = f"R_{self._route_counter}"
        route = Route(route_id, name)

        for i, (station_id, distance) in enumerate(stations):
            route.add_station(station_id, distance)

        self.routes[route_id] = route
        return route

    def set_train_route(self, train_id: str, route_id: str) -> None:
        """Установить маршрут для поезда из существующего"""
        train = self._get_train(train_id)
        route = self._get_route(route_id)
        train.set_route(route.stations)

    def add_schedule_entry(self, train_id: str, station_id: str,
                           arrival_time: datetime, departure_time: datetime,
                           platform: int) -> ScheduleEntry:
        """Добавить запись в расписание"""
        self._schedule_counter += 1
        schedule_id = f"SCH_{self._schedule_counter}"
        entry = ScheduleEntry(schedule_id, train_id, station_id, arrival_time, departure_time, platform)
        self.schedule[schedule_id] = entry
        return entry

    def get_schedule_for_train(self, train_id: str) -> List[ScheduleEntry]:
        """Получить расписание для поезда"""
        return [s for s in self.schedule.values() if s.train_id == train_id]

    # ==================== ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ====================

    def _get_track(self, track_id: str) -> RailwayTrack:
        """Получить путь по ID"""
        if track_id not in self.tracks:
            raise TrackNotFoundError(f"Путь {track_id} не найден")
        return self.tracks[track_id]

    def _get_station(self, station_id: str) -> Station:
        """Получить станцию по ID"""
        if station_id not in self.stations:
            raise StationNotFoundError(f"Станция {station_id} не найдена")
        return self.stations[station_id]

    def _get_train(self, train_id: str) -> Train:
        """Получить поезд по ID"""
        if train_id not in self.trains:
            raise TrainNotFoundError(f"Поезд {train_id} не найден")
        return self.trains[train_id]

    def _get_locomotive(self, loco_id: str) -> Locomotive:
        """Получить локомотив по ID"""
        if loco_id not in self.locomotives:
            raise LocomotiveNotFoundError(f"Локомотив {loco_id} не найден")
        return self.locomotives[loco_id]

    def _get_wagon(self, wagon_id: str) -> Wagon:
        """Получить вагон по ID"""
        if wagon_id not in self.wagons:
            raise WagonNotFoundError(f"Вагон {wagon_id} не найден")
        return self.wagons[wagon_id]

    def _get_ticket(self, ticket_id: str) -> Ticket:
        """Получить билет по ID"""
        if ticket_id not in self.tickets:
            raise TicketNotFoundError(f"Билет {ticket_id} не найден")
        return self.tickets[ticket_id]

    def _get_route(self, route_id: str) -> Route:
        """Получить маршрут по ID"""
        if route_id not in self.routes:
            raise RouteNotFoundError(f"Маршрут {route_id} не найден")
        return self.routes[route_id]

    def get_all_trains(self) -> List[Train]:
        """Получить все поезда"""
        return list(self.trains.values())

    def get_all_stations(self) -> List[Station]:
        """Получить все станции"""
        return list(self.stations.values())

    def get_all_tracks(self) -> List[RailwayTrack]:
        """Получить все пути"""
        return list(self.tracks.values())

    def get_all_tickets(self) -> List[Ticket]:
        """Получить все билеты"""
        return list(self.tickets.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Получить статистику системы"""
        operational_trains = sum(1 for t in self.trains.values()
                                 if t.locomotive.is_operational and all(w.is_operational for w in t.wagons))

        total_capacity = sum(t.get_total_capacity() for t in self.trains.values())
        tickets_sold = sum(1 for t in self.tickets.values() if t.is_valid)

        return {
            'total_trains': len(self.trains),
            'operational_trains': operational_trains,
            'total_stations': len(self.stations),
            'total_tracks': len(self.tracks),
            'total_locomotives': len(self.locomotives),
            'total_wagons': len(self.wagons),
            'total_tickets_sold': tickets_sold,
            'total_revenue': sum(t.price for t in self.tickets.values() if t.payment_status == PaymentStatus.COMPLETED),
            'total_passengers': tickets_sold,
            'total_seating_capacity': total_capacity,
            'occupancy_rate': (tickets_sold / total_capacity * 100) if total_capacity > 0 else 0
        }