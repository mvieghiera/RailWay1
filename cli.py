"""
Интерфейс командной строки (CLI) для железнодорожной системы управления
"""

import sys
from typing import List, Optional
from datetime import datetime
from services import RailwayService
from models import StationType, TicketClass, MaintenanceType, TrainStatus
from exceptions import *


class RailwayCLI:
    """
    Интерфейс командной строки для управления железной дорогой.
    Предоставляет пользователю доступ ко всем операциям системы.
    """

    def __init__(self):
        """Инициализация CLI с подключением к сервису"""
        self.service = RailwayService()
        self.running = True

        # Словарь команд и их обработчиков
        self.commands = {
            # Управление станциями и путями
            'add_station': self.add_station,
            'add_track': self.add_track,
            'list_stations': self.list_stations,
            'list_tracks': self.list_tracks,
            'station_info': self.station_info,

            # Управление поездами
            'add_train': self.add_train,
            'add_locomotive': self.add_locomotive,
            'add_wagon': self.add_wagon,
            'add_wagon_to_train': self.add_wagon_to_train,
            'list_trains': self.list_trains,
            'train_info': self.train_info,
            'set_route': self.set_route,

            # Движение поездов
            'move_train': self.move_train,
            'train_location': self.train_location,
            'advance_train': self.advance_train,

            # Расписание
            'add_schedule': self.add_schedule,
            'list_schedule': self.list_schedule,
            'train_schedule': self.train_schedule,

            # Билеты
            'search': self.search_trains,
            'buy_ticket': self.buy_ticket,
            'cancel_ticket': self.cancel_ticket,
            'pay_ticket': self.pay_ticket,
            'my_tickets': self.my_tickets,

            # Техническое обслуживание
            'maintain': self.maintain_loco,
            'repair': self.repair_wagon,
            'train_status': self.train_technical_status,

            # Безопасность
            'safety_check': self.safety_check,
            'safety_history': self.safety_history,

            # Статистика и общие
            'stats': self.show_statistics,
            'help': self.show_help,
            'exit': self.exit_cli,
            'quit': self.exit_cli,
        }

    def run(self):
        """Запуск основного цикла CLI"""
        self.print_welcome()

        while self.running:
            try:
                # Формирование приглашения
                if self.service.current_user:
                    prompt = f"\n{self.service.current_user}@railway $ "
                else:
                    prompt = "\nguest@railway $ "

                user_input = input(prompt).strip()
                if not user_input:
                    continue

                # Разбор команды
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:]

                # Выполнение команды
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"  ❌ Неизвестная команда: {command}")
                    print(f"     Введите 'help' для списка доступных команд")

            except KeyboardInterrupt:
                print("\n\n  👋 Выход...")
                break
            except RailwayException as e:
                print(f"  ❌ ОШИБКА: {e}")
            except Exception as e:
                print(f"  ❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")

    def print_welcome(self):
        """Вывод приветственного сообщения"""
        print("=" * 70)
        print("  🚂 ДОБРО ПОЖАЛОВАТЬ В СИСТЕМУ УПРАВЛЕНИЯ ЖЕЛЕЗНОЙ ДОРОГОЙ 🚂")
        print("=" * 70)
        print("  Версия: 1.0")
        print("  Разработчик: Система управления железнодорожным транспортом")
        print("=" * 70)
        print("\n  📌 Основные операции:")
        print("     • Движение поездов")
        print("     • Обслуживание станций")
        print("     • Техническое обслуживание")
        print("     • Продажа билетов")
        print("     • Контроль безопасности")
        print("\n  💡 Введите 'help' для списка всех команд")
        print("-" * 70)

    # ==================== КОМАНДЫ УПРАВЛЕНИЯ СТАНЦИЯМИ И ПУТЯМИ ====================

    def add_station(self, args: List[str]):
        """
        Добавить новую станцию
        Формат: add_station <name> <type> <city> <platforms> [cargo_platforms]
        Типы: passenger, freight, sorting
        """
        if len(args) < 4:
            print(
                "  ❌ Использование: add_station <name> <type(passenger/freight/sorting)> <city> <platforms> [cargo_platforms]")
            return

        name = args[0]
        type_str = args[1]
        city = args[2]

        try:
            platforms = int(args[3])
            cargo_platforms = int(args[4]) if len(args) > 4 else 0

            station_type_map = {
                'passenger': StationType.PASSENGER,
                'freight': StationType.FREIGHT,
                'sorting': StationType.SORTING
            }

            if type_str.lower() not in station_type_map:
                print("  ❌ Ошибка: тип станции должен быть passenger/freight/sorting")
                return

            station_type = station_type_map[type_str.lower()]
            station = self.service.add_station(name, station_type, city, platforms, cargo_platforms)
            print(f"  ✅ Станция '{station.name}' успешно добавлена!")
            print(f"     ID: {station.id}")
            print(f"     Город: {station.city}")
            print(f"     Платформ: {station.get_total_platforms()}")
        except ValueError:
            print("  ❌ Ошибка: platforms и cargo_platforms должны быть числами")

    def add_track(self, args: List[str]):
        """
        Добавить железнодорожный путь
        Формат: add_track <name> <length_km> <max_speed> [type] [electrified]
        """
        if len(args) < 3:
            print("  ❌ Использование: add_track <name> <length_km> <max_speed> [type] [electrified]")
            return

        name = args[0]

        try:
            length_km = float(args[1])
            max_speed = int(args[2])
            track_type = args[3] if len(args) > 3 else "main"
            electrified = args[4].lower() == 'true' if len(args) > 4 else True

            track = self.service.add_track(name, length_km, max_speed, track_type, electrified)
            print(f"  ✅ Путь '{track.name}' успешно добавлен!")
            print(f"     ID: {track.id}")
            print(f"     Длина: {track.length_km} км")
            print(f"     Макс. скорость: {track.max_speed} км/ч")
        except ValueError:
            print("  ❌ Ошибка: length_km должно быть числом, max_speed - целым числом")

    def list_stations(self, args: List[str]):
        """Показать список всех станций"""
        stations = self.service.get_all_stations()

        if not stations:
            print("  📭 Нет доступных станций")
            return

        print(f"\n  📍 СПИСОК СТАНЦИЙ ({len(stations)} шт.):")
        print("  " + "-" * 60)

        for station in stations:
            status = "🟢 Активна" if station.is_active else "🔴 Неактивна"
            print(f"     {station.id} | {station.name}")
            print(f"         Город: {station.city}, Тип: {station.station_type.value}")
            print(f"         Платформ: {station.get_total_platforms()}, {status}")
            print(f"         Загрузка: {station.trains_handled_today}/{station.daily_capacity} поездов/день")
            print()

    def list_tracks(self, args: List[str]):
        """Показать список всех путей"""
        tracks = self.service.get_all_tracks()

        if not tracks:
            print("  📭 Нет доступных путей")
            return

        print(f"\n  🛤️ СПИСОК ПУТЕЙ ({len(tracks)} шт.):")
        print("  " + "-" * 60)

        for track in tracks:
            status = "🔴 Занят" if track.is_occupied else "🟢 Свободен"
            print(f"     {track.id} | {track.name}")
            print(f"         Длина: {track.length_km} км, Макс. скорость: {track.max_speed} км/ч")
            print(f"         Состояние: {track.condition_score:.1f}%, {status}")
            if track.occupied_by_train_id:
                print(f"         Занят поездом: {track.occupied_by_train_id}")
            print()

    def station_info(self, args: List[str]):
        """Показать детальную информацию о станции"""
        if len(args) < 1:
            print("  ❌ Использование: station_info <station_id>")
            return

        station_id = args[0]

        try:
            info = self.service.get_station_info(station_id)
            station = info['station']

            print(f"\n  🏢 ИНФОРМАЦИЯ О СТАНЦИИ")
            print("  " + "-" * 60)
            print(f"     ID: {station.id}")
            print(f"     Название: {station.name}")
            print(f"     Город: {station.city}")
            print(f"     Тип: {station.station_type.value}")
            print(f"     Статус: {'Активна' if station.is_active else 'Неактивна'}")
            print(f"     Пассажирских платформ: {station.platforms}")
            print(f"     Грузовых платформ: {station.cargo_platforms}")
            print(f"     Дневная пропускная способность: {station.daily_capacity} поездов")
            print(f"     Обслужено сегодня: {station.trains_handled_today} поездов")
            print(f"     Загрузка: {info['utilization']:.1f}%")
            print(f"     Путей у станции: {info['tracks_count']}")
            print(f"     Поездов на станции: {info['trains_count']}")

            if info['trains']:
                print(f"\n     🚆 Поезда на станции:")
                for train in info['trains']:
                    print(f"        - {train['name']} ({train['id']}) - {train['status']}")

        except StationNotFoundError as e:
            print(f"  ❌ {e}")

    # ==================== КОМАНДЫ УПРАВЛЕНИЯ ПОЕЗДАМИ ====================

    def add_locomotive(self, args: List[str]):
        """Добавить локомотив"""
        if len(args) < 2:
            print("  ❌ Использование: add_locomotive <model> <power_kw> [fuel_type] [max_speed]")
            return

        model = args[0]

        try:
            power_kw = int(args[1])
            fuel_type = args[2] if len(args) > 2 else "electric"
            max_speed = int(args[3]) if len(args) > 3 else 120

            loco = self.service.add_locomotive(model, power_kw, fuel_type, max_speed)
            print(f"  ✅ Локомотив '{loco.model}' успешно добавлен!")
            print(f"     ID: {loco.id}")
            print(f"     Мощность: {loco.power_kw} кВт")
            print(f"     Тип: {loco.fuel_type}")
            print(f"     Макс. скорость: {loco.max_speed} км/ч")
        except ValueError:
            print("  ❌ Ошибка: power_kw и max_speed должны быть числами")

    def add_wagon(self, args: List[str]):
        """Добавить вагон"""
        if len(args) < 2:
            print("  ❌ Использование: add_wagon <type(passenger/cargo/luggage)> <capacity> [comfort_level]")
            return

        wagon_type = args[0]

        try:
            capacity = int(args[1])
            comfort_level = args[2] if len(args) > 2 else "economy"

            wagon = self.service.add_wagon(wagon_type, capacity, comfort_level)
            print(f"  ✅ Вагон успешно добавлен!")
            print(f"     ID: {wagon.id}")
            print(f"     Тип: {wagon.wagon_type}")
            print(f"     Вместимость: {wagon.get_capacity_display()}")
            print(f"     Уровень комфорта: {wagon.comfort_level}")
        except ValueError:
            print("  ❌ Ошибка: capacity должно быть числом")

    def add_train(self, args: List[str]):
        """Добавить поезд"""
        if len(args) < 2:
            print("  ❌ Использование: add_train <name> <locomotive_id>")
            return

        name = args[0]
        loco_id = args[1]

        try:
            train = self.service.add_train(name, loco_id)
            print(f"  ✅ Поезд '{train.name}' успешно создан!")
            print(f"     ID: {train.id}")
            print(f"     Локомотив: {train.locomotive.model} ({train.locomotive.id})")
        except (LocomotiveNotFoundError, LocomotiveNotOperationalError) as e:
            print(f"  ❌ {e}")

    def add_wagon_to_train(self, args: List[str]):
        """Добавить вагон к поезду"""
        if len(args) < 2:
            print("  ❌ Использование: add_wagon_to_train <train_id> <wagon_id>")
            return

        train_id = args[0]
        wagon_id = args[1]

        try:
            self.service.add_wagon_to_train(train_id, wagon_id)
            print(f"  ✅ Вагон {wagon_id} добавлен к поезду {train_id}")
        except (TrainNotFoundError, WagonNotFoundError, ValueError) as e:
            print(f"  ❌ {e}")

    def list_trains(self, args: List[str]):
        """Показать список всех поездов"""
        trains = self.service.get_all_trains()

        if not trains:
            print("  📭 Нет доступных поездов")
            return

        print(f"\n  🚆 СПИСОК ПОЕЗДОВ ({len(trains)} шт.):")
        print("  " + "-" * 60)

        for train in trains:
            status_icon = {
                TrainStatus.ON_TIME: "✅",
                TrainStatus.DELAYED: "⏰",
                TrainStatus.DEPARTED: "🚂",
                TrainStatus.ARRIVED: "🏁",
                TrainStatus.CANCELLED: "❌",
                TrainStatus.IN_TRANSIT: "🔄"
            }.get(train.status, "❓")

            print(f"     {train.id} | {train.name}")
            print(f"         {status_icon} Статус: {train.status.value}")
            print(f"         🚂 Вагонов: {len(train.wagons)}")
            print(f"         💺 Вместимость: {train.get_total_capacity()} мест")

            if train.delay_minutes > 0:
                print(f"         ⏰ Задержка: {train.delay_minutes} мин")

            current_station = train.get_current_station()
            if current_station:
                station = self.service.stations.get(current_station)
                if station:
                    print(f"         📍 Текущая станция: {station.name}")
            print()

    def train_info(self, args: List[str]):
        """Показать детальную информацию о поезде"""
        if len(args) < 1:
            print("  ❌ Использование: train_info <train_id>")
            return

        train_id = args[0]

        try:
            train = self.service._get_train(train_id)

            print(f"\n  🚆 ИНФОРМАЦИЯ О ПОЕЗДЕ")
            print("  " + "-" * 60)
            print(f"     ID: {train.id}")
            print(f"     Название: {train.name}")
            print(f"     Статус: {train.status.value}")
            print(f"     Задержка: {train.delay_minutes} мин")

            print(f"\n     🚂 Локомотив:")
            print(f"        Модель: {train.locomotive.model}")
            print(f"        Мощность: {train.locomotive.power_kw} кВт")
            print(f"        Статус: {'Исправен' if train.locomotive.is_operational else 'Неисправен'}")
            print(f"        Пробег: {train.locomotive.total_distance_km:.1f} км")

            print(f"\n     🚋 Вагоны ({len(train.wagons)} шт.):")
            for i, wagon in enumerate(train.wagons, 1):
                status = "✅" if wagon.is_operational else "❌"
                print(f"        {i}. {status} {wagon.id} - {wagon.wagon_type}, {wagon.get_capacity_display()}")

            operational_status = train.get_operational_status()
            print(f"\n     🔧 Общая исправность: {'✅ Да' if operational_status['all_operational'] else '❌ Нет'}")

            if train.route:
                print(f"\n     🗺️ Маршрут:")
                for i, station_id in enumerate(train.route):
                    station = self.service.stations.get(station_id)
                    station_name = station.name if station else station_id
                    marker = "📍" if i == train.current_station_index else "  "
                    print(f"        {marker} {i + 1}. {station_name}")

        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    def set_route(self, args: List[str]):
        """Установить маршрут для поезда"""
        if len(args) < 2:
            print("  ❌ Использование: set_route <train_id> <station_ids...>")
            return

        train_id = args[0]
        station_ids = args[1:]

        try:
            train = self.service._get_train(train_id)
            train.set_route(station_ids)
            print(f"  ✅ Маршрут для поезда '{train.name}' установлен!")
            print(f"     Станций в маршруте: {len(station_ids)}")
        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    # ==================== КОМАНДЫ ДВИЖЕНИЯ ПОЕЗДОВ ====================

    def move_train(self, args: List[str]):
        """Переместить поезд на путь"""
        if len(args) < 2:
            print("  ❌ Использование: move_train <train_id> <track_id>")
            return

        train_id = args[0]
        track_id = args[1]

        try:
            result = self.service.move_train(train_id, track_id)
            print(f"  ✅ {result['message']}")
        except (TrainNotFoundError, TrackNotFoundError, TrackOccupiedError,
                LocomotiveNotOperationalError, RouteNotSetError) as e:
            print(f"  ❌ {e}")

    def train_location(self, args: List[str]):
        """Показать местоположение поезда"""
        if len(args) < 1:
            print("  ❌ Использование: train_location <train_id>")
            return

        train_id = args[0]

        try:
            location = self.service.get_train_location(train_id)
            if location:
                print(f"\n  📍 МЕСТОПОЛОЖЕНИЕ ПОЕЗДА {train_id}")
                print("  " + "-" * 60)
                print(f"     Поезд: {location['train_name']}")
                print(f"     Путь: {location['track_name']} ({location['track_id']})")
                print(f"     Длина пути: {location['track_length_km']} км")
                if location['current_station']:
                    station = self.service.stations.get(location['current_station'])
                    if station:
                        print(f"     Текущая станция: {station.name}")
                print(f"     Статус: {location['status']}")
            else:
                print(f"  ℹ️ Поезд {train_id} не находится ни на одном пути (возможно, в депо)")
        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    def advance_train(self, args: List[str]):
        """Переместить поезд на следующую станцию"""
        if len(args) < 1:
            print("  ❌ Использование: advance_train <train_id>")
            return

        train_id = args[0]

        try:
            result = self.service.advance_train_on_route(train_id)
            if result:
                if result.get('is_final'):
                    print(f"  🏁 {result['message']}")
                else:
                    station = self.service.stations.get(result['next_station_id'])
                    station_name = station.name if station else result['next_station_id']
                    print(f"  ✅ Поезд {result['train_name']} проследовал на станцию '{station_name}'")
        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    # ==================== КОМАНДЫ РАСПИСАНИЯ ====================

    def add_schedule(self, args: List[str]):
        """Добавить запись в расписание"""
        if len(args) < 5:
            print("  ❌ Использование: add_schedule <train_id> <station_id> <arrival_time> <departure_time> <platform>")
            print("     Формат времени: YYYY-MM-DD HH:MM")
            return

        train_id = args[0]
        station_id = args[1]
        platform = int(args[4])

        try:
            arrival_time = datetime.strptime(f"{args[2]} {args[3]}", "%Y-%m-%d %H:%M")
            departure_time = datetime.strptime(f"{args[2]} {args[3]}", "%Y-%m-%d %H:%M")

            entry = self.service.add_schedule_entry(train_id, station_id, arrival_time, departure_time, platform)
            print(f"  ✅ Запись в расписании добавлена!")
            print(f"     ID: {entry.id}")
            print(f"     Прибытие: {entry.arrival_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"     Отправление: {entry.departure_time.strftime('%d.%m.%Y %H:%M')}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")

    def list_schedule(self, args: List[str]):
        """Показать все расписание"""
        if not self.service.schedule:
            print("  📭 Расписание пусто")
            return

        print(f"\n  📅 ВСЕ РАСПИСАНИЕ ({len(self.service.schedule)} записей):")
        print("  " + "-" * 60)

        for entry in self.service.schedule.values():
            train = self.service.trains.get(entry.train_id)
            train_name = train.name if train else entry.train_id
            station = self.service.stations.get(entry.station_id)
            station_name = station.name if station else entry.station_id

            print(f"     {entry.id}: {train_name} -> {station_name}")
            print(f"         Прибытие: {entry.arrival_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"         Отправление: {entry.departure_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"         Платформа: {entry.platform}")
            if entry.is_completed:
                print(f"         Статус: ✅ Выполнено")
            print()

    def train_schedule(self, args: List[str]):
        """Показать расписание для конкретного поезда"""
        if len(args) < 1:
            print("  ❌ Использование: train_schedule <train_id>")
            return

        train_id = args[0]
        schedule = self.service.get_schedule_for_train(train_id)

        if not schedule:
            print(f"  📭 Нет расписания для поезда {train_id}")
            return

        train = self.service.trains.get(train_id)
        train_name = train.name if train else train_id

        print(f"\n  📅 РАСПИСАНИЕ ПОЕЗДА '{train_name}'")
        print("  " + "-" * 60)

        for i, entry in enumerate(sorted(schedule, key=lambda x: x.arrival_time), 1):
            station = self.service.stations.get(entry.station_id)
            station_name = station.name if station else entry.station_id

            print(f"     {i}. {station_name}")
            print(f"        🚂 Прибытие: {entry.arrival_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"        🚂 Отправление: {entry.departure_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"        🚉 Платформа: {entry.platform}")
            if entry.is_completed:
                print(f"        ✅ Выполнено")
            print()

    # ==================== КОМАНДЫ БИЛЕТОВ ====================

    def search_trains(self, args: List[str]):
        """Поиск поездов"""
        if len(args) < 3:
            print("  ❌ Использование: search <from_station> <to_station> <date>")
            print("     Формат даты: YYYY-MM-DD")
            return

        from_station = args[0]
        to_station = args[1]

        try:
            date = datetime.strptime(args[2], "%Y-%m-%d")
            results = self.service.search_trains(from_station, to_station, date)

            if not results:
                print(f"  📭 Поездов по маршруту не найдено")
                return

            print(f"\n  🔍 РЕЗУЛЬТАТЫ ПОИСКА ({len(results)} поездов):")
            print("  " + "-" * 70)

            for train in results:
                print(f"     🚆 {train['train_name']} ({train['train_id']})")
                print(f"        Отправление: {train['from_station']} в {train['departure_time'].strftime('%H:%M')}")
                print(
                    f"        Прибытие: {train['to_station']} в {train['arrival_time'].strftime('%H:%M') if train['arrival_time'] else '—'}")
                print(f"        В пути: ~{train['duration_minutes']} мин")
                print(f"        Свободных мест: {train['available_seats']}")
                print(f"        Статус: {train['status']}")
                print()

        except ValueError:
            print("  ❌ Ошибка: неверный формат даты. Используйте YYYY-MM-DD")
        except (StationNotFoundError) as e:
            print(f"  ❌ {e}")

    def buy_ticket(self, args: List[str]):
        """
        Купить билет
        Формат: buy_ticket <train_id> <passenger_name> <from_station> <to_station> <class> [wagon] [seat]
        Классы: first, business, second, economy, third
        """
        if len(args) < 6:
            print(
                "  ❌ Использование: buy_ticket <train_id> <passenger_name> <from_station> <to_station> <class> [wagon] [seat]")
            print("     Классы: first, business, second, economy, third")
            print("     Пример: buy_ticket TN_1 'Иванов Иван' ST_1 ST_2 economy 2 15")
            return

        train_id = args[0]
        passenger_name = args[1]
        from_station = args[2]
        to_station = args[3]

        # Карта соответствия классов (поддерживаем оба варианта: русский и английский)
        class_map = {
            # Английские названия
            'first': TicketClass.FIRST,
            'business': TicketClass.BUSINESS,
            'second': TicketClass.SECOND,
            'economy': TicketClass.ECONOMY,
            'third': TicketClass.THIRD,
            # Русские названия (для удобства)
            'первый': TicketClass.FIRST,
            'бизнес': TicketClass.BUSINESS,
            'второй': TicketClass.SECOND,
            'эконом': TicketClass.ECONOMY,
            'третий': TicketClass.THIRD,
        }

        class_key = args[4].lower()
        if class_key not in class_map:
            print(f"  ❌ Ошибка: класс '{args[4]}' не распознан")
            print("     Доступные классы: first, business, second, economy, third")
            print("     Или на русском: первый, бизнес, второй, эконом, третий")
            return

        ticket_class = class_map[class_key]

        # Парсинг номера вагона и места (опционально)
        wagon_number = 1
        seat_number = 1
        if len(args) > 5:
            try:
                wagon_number = int(args[5])
            except ValueError:
                print(f"  ❌ Ошибка: номер вагона должен быть числом")
                return
        if len(args) > 6:
            try:
                seat_number = int(args[6])
            except ValueError:
                print(f"  ❌ Ошибка: номер места должен быть числом")
                return

        try:
            ticket = self.service.buy_ticket(
                train_id=train_id,
                passenger_name=passenger_name,
                from_station_id=from_station,
                to_station_id=to_station,
                departure_time=datetime.now(),
                ticket_class=ticket_class,
                wagon_number=wagon_number,
                seat_number=seat_number
            )

            print(f"\n  ✅ БИЛЕТ УСПЕШНО КУПЛЕН!")
            print("  " + "-" * 60)
            print(f"     Номер билета: {ticket.id}")
            print(f"     Пассажир: {ticket.passenger_name}")
            print(f"     Поезд: {ticket.train_id}")
            print(f"     Маршрут: {ticket.from_station_id} → {ticket.to_station_id}")
            print(f"     Вагон/место: {ticket.wagon_number}/{ticket.seat_number}")
            print(f"     Класс: {ticket.ticket_class.value}")
            print(f"     Цена: {ticket.price} руб.")
            print(f"     Статус оплаты: {ticket.payment_status.value}")
            print(f"\n  💡 Для оплаты билета введите: pay_ticket {ticket.id}")

        except (TrainNotFoundError, NoAvailableSeatsError, SeatAlreadyBookedError) as e:
            print(f"  ❌ {e}")
        except Exception as e:
            print(f"  ❌ Ошибка при покупке билета: {e}")

    def pay_ticket(self, args: List[str]):
        """Оплатить билет"""
        if len(args) < 1:
            print("  ❌ Использование: pay_ticket <ticket_id>")
            return

        ticket_id = args[0]

        try:
            ticket = self.service.pay_for_ticket(ticket_id)
            print(f"  ✅ Билет {ticket_id} успешно оплачен!")
            print(f"     Сумма: {ticket.price} руб.")
        except (TicketNotFoundError, PaymentAlreadyProcessedError) as e:
            print(f"  ❌ {e}")

    def cancel_ticket(self, args: List[str]):
        """Отменить билет"""
        if len(args) < 1:
            print("  ❌ Использование: cancel_ticket <ticket_id>")
            return

        ticket_id = args[0]

        try:
            result = self.service.cancel_ticket(ticket_id)
            print(f"  ✅ {result['message']}")
            print(f"     Сумма возврата: {result['refund_amount']} руб.")
        except (TicketNotFoundError, TicketAlreadyCancelledError, TicketNotRefundableError) as e:
            print(f"  ❌ {e}")

    def my_tickets(self, args: List[str]):
        """Показать билеты текущего пользователя"""
        if not self.service.current_user:
            print("  ℹ️ Вы не авторизованы. Билеты не привязаны к пользователю.")
            print("     Для просмотра билетов используйте: my_tickets <passenger_name>")
            if len(args) < 1:
                return

        passenger_name = args[0] if args else self.service.current_user

        tickets = self.service.get_user_tickets(passenger_name)

        if not tickets:
            print(f"  📭 Нет билетов для пассажира '{passenger_name}'")
            return

        print(f"\n  🎫 БИЛЕТЫ ПАССАЖИРА '{passenger_name}'")
        print("  " + "-" * 60)

        total_spent = 0
        for ticket in tickets:
            status = "✅ Действителен" if ticket.is_valid else "❌ Аннулирован"
            payment = "💰 Оплачен" if ticket.payment_status.value == "Оплачен" else "⏳ Не оплачен"

            print(f"     {ticket.id}")
            print(f"        Поезд: {ticket.train_id}")
            print(f"        Маршрут: {ticket.from_station_id} → {ticket.to_station_id}")
            print(f"        Дата: {ticket.departure_time.strftime('%d.%m.%Y %H:%M')}")
            print(f"        Место: вагон {ticket.wagon_number}, место {ticket.seat_number}")
            print(f"        Класс: {ticket.ticket_class.value}")
            print(f"        Цена: {ticket.price} руб.")
            print(f"        Статус: {status}, {payment}")
            print()

            if ticket.payment_status.value == "Оплачен":
                total_spent += ticket.price

        print(f"  💰 Итого потрачено: {total_spent} руб.")

    # ==================== КОМАНДЫ ТЕХНИЧЕСКОГО ОБСЛУЖИВАНИЯ ====================

    def maintain_loco(self, args: List[str]):
        """Провести ТО локомотива"""
        if len(args) < 1:
            print("  ❌ Использование: maintain <locomotive_id> [type]")
            print("     Типы: inspection, repair, cleaning, fueling, emergency, scheduled")
            return

        loco_id = args[0]

        type_map = {
            'inspection': MaintenanceType.INSPECTION,
            'repair': MaintenanceType.REPAIR,
            'cleaning': MaintenanceType.CLEANING,
            'fueling': MaintenanceType.FUELING,
            'emergency': MaintenanceType.EMERGENCY,
            'scheduled': MaintenanceType.SCHEDULED
        }

        maint_type = type_map.get(args[1].lower() if len(args) > 1 else 'scheduled', MaintenanceType.SCHEDULED)

        try:
            record = self.service.perform_maintenance(loco_id, maint_type)
            print(f"  ✅ Техническое обслуживание проведено!")
            print(f"     Запись: {record.id}")
            print(f"     Тип: {record.maintenance_type.value}")
            print(f"     Дата: {record.performed_at.strftime('%d.%m.%Y %H:%M')}")
        except LocomotiveNotFoundError as e:
            print(f"  ❌ {e}")

    def repair_wagon(self, args: List[str]):
        """Отремонтировать вагон"""
        if len(args) < 1:
            print("  ❌ Использование: repair <wagon_id>")
            return

        wagon_id = args[0]

        try:
            record = self.service.repair_wagon(wagon_id)
            print(f"  ✅ Вагон {wagon_id} отремонтирован!")
            print(f"     Запись: {record.id}")
            print(f"     Дата: {record.performed_at.strftime('%d.%m.%Y %H:%M')}")
        except WagonNotFoundError as e:
            print(f"  ❌ {e}")

    def train_technical_status(self, args: List[str]):
        """Показать технический статус поезда"""
        if len(args) < 1:
            print("  ❌ Использование: train_status <train_id>")
            return

        train_id = args[0]

        try:
            status = self.service.get_operational_status(train_id)

            print(f"\n  🔧 ТЕХНИЧЕСКИЙ СТАТУС ПОЕЗДА {train_id}")
            print("  " + "-" * 60)
            print(f"     Локомотив: {'✅ Исправен' if status['locomotive_operational'] else '❌ Неисправен'}")

            if status['wagons_operational']:
                operational = sum(1 for w in status['wagons_operational'] if w)
                total = len(status['wagons_operational'])
                print(f"     Вагоны: {operational}/{total} исправны")

            print(
                f"\n     Общая исправность: {'✅ ГОДЕН К ЭКСПЛУАТАЦИИ' if status['all_operational'] else '❌ ТРЕБУЕТ РЕМОНТА'}")

            if status.get('needs_maintenance'):
                print(f"     ⚠️ Требуется техническое обслуживание!")

        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    # ==================== КОМАНДЫ БЕЗОПАСНОСТИ ====================

    def safety_check(self, args: List[str]):
        """Провести проверку безопасности"""
        if len(args) < 1:
            print("  ❌ Использование: safety_check <train_id> [inspector]")
            return

        train_id = args[0]
        inspector = args[1] if len(args) > 1 else self.service.current_user or "System"

        try:
            result = self.service.perform_pre_departure_check(train_id, inspector)

            print(f"\n  🔒 ПРОВЕРКА БЕЗОПАСНОСТИ")
            print("  " + "-" * 60)
            print(f"     Поезд: {train_id}")
            print(f"     Инспектор: {inspector}")
            print(f"     Результат: {result.status.value}")
            print(f"     Время: {result.check_time.strftime('%d.%m.%Y %H:%M')}")

            if result.items_checked:
                print(f"\n     Проверенные пункты:")
                for item, passed in result.items_checked.items():
                    icon = "✅" if passed else "❌"
                    print(f"        {icon} {item}")

        except (TrainNotFoundError, SafetyViolationError) as e:
            print(f"  ❌ {e}")

    def safety_history(self, args: List[str]):
        """Показать историю проверок безопасности"""
        if len(args) < 1:
            print("  ❌ Использование: safety_history <train_id>")
            return

        train_id = args[0]

        try:
            history = self.service.get_safety_history(train_id)

            if not history:
                print(f"  📭 Нет записей о проверках безопасности для поезда {train_id}")
                return

            print(f"\n  📋 ИСТОРИЯ ПРОВЕРОК БЕЗОПАСНОСТИ ДЛЯ ПОЕЗДА {train_id}")
            print("  " + "-" * 60)

            for i, check in enumerate(history, 1):
                print(f"     {i}. {check.check_time.strftime('%d.%m.%Y %H:%M')}")
                print(f"        Инспектор: {check.inspector}")
                print(f"        Результат: {check.status.value}")
                print()

        except TrainNotFoundError as e:
            print(f"  ❌ {e}")

    # ==================== СТАТИСТИКА И ОБЩИЕ КОМАНДЫ ====================

    def show_statistics(self, args: List[str]):
        """Показать статистику системы"""
        stats = self.service.get_statistics()

        print("\n  📊 СТАТИСТИКА СИСТЕМЫ")
        print("  " + "-" * 60)
        print(f"\n  🚆 ПОДВИЖНОЙ СОСТАВ:")
        print(f"     Поездов: {stats['total_trains']}")
        print(f"     Из них исправны: {stats['operational_trains']}")
        print(f"     Локомотивов: {stats['total_locomotives']}")
        print(f"     Вагонов: {stats['total_wagons']}")

        print(f"\n  🏢 ИНФРАСТРУКТУРА:")
        print(f"     Станций: {stats['total_stations']}")
        print(f"     Ж/д путей: {stats['total_tracks']}")

        print(f"\n  🎫 ПЕРЕВОЗКИ:")
        print(f"     Продано билетов: {stats['total_tickets_sold']}")
        print(f"     Перевезено пассажиров: {stats['total_passengers']}")
        print(f"     Общая выручка: {stats['total_revenue']:.2f} руб.")
        print(f"     Общая вместимость: {stats['total_seating_capacity']} мест")
        print(f"     Загрузка: {stats['occupancy_rate']:.1f}%")

    def show_help(self, args: List[str]):
        """Показать справку"""
        print("\n" + "=" * 70)
        print("  📚 СПРАВКА ПО КОМАНДАМ")
        print("=" * 70)

        print("\n  🏢 УПРАВЛЕНИЕ СТАНЦИЯМИ И ПУТЯМИ:")
        print("     add_station <name> <type> <city> <platforms> [cargo_platforms]")
        print("     add_track <name> <length_km> <max_speed> [type] [electrified]")
        print("     list_stations")
        print("     list_tracks")
        print("     station_info <station_id>")

        print("\n  🚆 УПРАВЛЕНИЕ ПОЕЗДАМИ:")
        print("     add_locomotive <model> <power_kw> [fuel_type] [max_speed]")
        print("     add_wagon <type> <capacity> [comfort_level]")
        print("     add_train <name> <locomotive_id>")
        print("     add_wagon_to_train <train_id> <wagon_id>")
        print("     list_trains")
        print("     train_info <train_id>")
        print("     set_route <train_id> <station_ids...>")

        print("\n  🚂 ДВИЖЕНИЕ ПОЕЗДОВ:")
        print("     move_train <train_id> <track_id>")
        print("     train_location <train_id>")
        print("     advance_train <train_id>")

        print("\n  📅 РАСПИСАНИЕ:")
        print("     add_schedule <train_id> <station_id> <arrival> <departure> <platform>")
        print("     list_schedule")
        print("     train_schedule <train_id>")

        print("\n  🎫 БИЛЕТЫ:")
        print("     search <from_station> <to_station> <date>")
        print("     buy_ticket <train_id> <passenger_name> <from> <to> <class> [wagon] [seat]")
        print("     pay_ticket <ticket_id>")
        print("     cancel_ticket <ticket_id>")
        print("     my_tickets [passenger_name]")
        print("\n     Доступные классы: first, business, second, economy, third")
        print("     Пример: buy_ticket TN_1 'Иванов Иван' ST_1 ST_2 economy 2 15")

        print("\n  🔧 ТЕХНИЧЕСКОЕ ОБСЛУЖИВАНИЕ:")
        print("     maintain <locomotive_id> [type]")
        print("     repair <wagon_id>")
        print("     train_status <train_id>")

        print("\n  🔒 БЕЗОПАСНОСТЬ:")
        print("     safety_check <train_id> [inspector]")
        print("     safety_history <train_id>")

        print("\n  📊 СТАТИСТИКА:")
        print("     stats")

        print("\n  💡 ОБЩИЕ:")
        print("     help")
        print("     exit, quit")

        print("\n" + "=" * 70)

    def exit_cli(self, args: List[str]):
        """Выход из программы"""
        print("\n  👋 До свидания! Спасибо за использование системы управления железной дорогой.")
        print("  🚂 Желаем безопасных поездок!")
        self.running = False