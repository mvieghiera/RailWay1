#!/usr/bin/env python3
"""
Unit-тесты для железнодорожной системы управления

Запуск тестов:
    python -m unittest tests.py -v
    python tests.py
"""

import unittest
from datetime import datetime, timedelta
from typing import Dict, Any

from models import *
from exceptions import *
from services import RailwayService


# ==================== ТЕСТЫ МОДЕЛЕЙ ДАННЫХ ====================

class TestRailwayTrack(unittest.TestCase):
    """Тесты для класса RailwayTrack"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.track = RailwayTrack("T1", "Тестовый путь", 150.5, 120)

    def test_track_creation(self):
        """Тест создания пути"""
        self.assertEqual(self.track.name, "Тестовый путь")
        self.assertEqual(self.track.length_km, 150.5)
        self.assertEqual(self.track.max_speed, 120)
        self.assertFalse(self.track.is_occupied)
        self.assertEqual(self.track.condition_score, 100.0)

    def test_track_occupy(self):
        """Тест занятия пути"""
        self.track.occupy("TN1")
        self.assertTrue(self.track.is_occupied)
        self.assertEqual(self.track.occupied_by_train_id, "TN1")

    def test_track_release(self):
        """Тест освобождения пути"""
        self.track.occupy("TN1")
        self.track.release()
        self.assertFalse(self.track.is_occupied)
        self.assertIsNone(self.track.occupied_by_train_id)

    def test_track_availability(self):
        """Тест проверки доступности пути"""
        self.assertTrue(self.track.is_available())
        self.track.occupy("TN1")
        self.assertFalse(self.track.is_available())



    def test_track_str(self):
        """Тест строкового представления"""
        self.assertIn("Тестовый путь", str(self.track))
        self.assertIn("Свободен", str(self.track))

    def test_track_to_dict(self):
        """Тест сериализации в словарь"""
        data = self.track.to_dict()
        self.assertEqual(data['name'], "Тестовый путь")
        self.assertEqual(data['length_km'], 150.5)
        self.assertIn('id', data)


class TestStation(unittest.TestCase):
    """Тесты для класса Station"""

    def setUp(self):
        self.station = Station("ST1", "Москва", StationType.PASSENGER, "Москва", 10, 5)

    def test_station_creation(self):
        """Тест создания станции"""
        self.assertEqual(self.station.name, "Москва")
        self.assertEqual(self.station.city, "Москва")
        self.assertEqual(self.station.station_type, StationType.PASSENGER)
        self.assertEqual(self.station.platforms, 10)
        self.assertEqual(self.station.cargo_platforms, 5)

    def test_add_track(self):
        """Тест добавления пути"""
        self.station.add_track("TR1")
        self.assertIn("TR1", self.station.tracks_at_station)

        # Проверка на дублирование
        self.station.add_track("TR1")
        self.assertEqual(len(self.station.tracks_at_station), 1)

    def test_remove_track(self):
        """Тест удаления пути"""
        self.station.add_track("TR1")
        self.station.remove_track("TR1")
        self.assertNotIn("TR1", self.station.tracks_at_station)

    def test_total_platforms(self):
        """Тест подсчета общего количества платформ"""
        self.assertEqual(self.station.get_total_platforms(), 15)

    def test_capacity_management(self):
        """Тест управления пропускной способностью"""
        self.assertTrue(self.station.can_handle_train())

        for _ in range(self.station.daily_capacity):
            self.station.increment_trains_handled()

        self.assertFalse(self.station.can_handle_train())

    def test_activate_deactivate(self):
        """Тест активации/деактивации станции"""
        self.station.deactivate()
        self.assertFalse(self.station.is_active)

        self.station.activate()
        self.assertTrue(self.station.is_active)


class TestLocomotive(unittest.TestCase):
    """Тесты для класса Locomotive"""

    def setUp(self):
        self.loco = Locomotive("L1", "ВЛ80", 4000, "diesel", 120)

    def test_locomotive_creation(self):
        """Тест создания локомотива"""
        self.assertEqual(self.loco.model, "ВЛ80")
        self.assertEqual(self.loco.power_kw, 4000)
        self.assertTrue(self.loco.is_operational)
        self.assertEqual(self.loco.total_distance_km, 0.0)

    def test_perform_maintenance(self):
        """Тест проведения ТО"""
        self.loco.set_broken()
        self.assertFalse(self.loco.is_operational)

        self.loco.perform_maintenance()
        self.assertTrue(self.loco.is_operational)
        self.assertGreater(len(self.loco.maintenance_history), 0)

    def test_add_distance(self):
        """Тест добавления пробега"""
        self.loco.add_distance(100.5)
        self.assertEqual(self.loco.total_distance_km, 100.5)

        self.loco.add_distance(-10)  # Отрицательное значение игнорируется
        self.assertEqual(self.loco.total_distance_km, 100.5)

    def test_assign_to_train(self):
        """Тест привязки к поезду"""
        self.loco.assign_to_train("TN1")
        self.assertEqual(self.loco.current_train_id, "TN1")

        self.loco.detach_from_train()
        self.assertIsNone(self.loco.current_train_id)

    def test_needs_maintenance(self):
        """Тест проверки необходимости ТО"""
        # Недавно обслуживали
        self.assertFalse(self.loco.needs_maintenance())

        # Имитируем старую дату последнего ТО
        self.loco.last_maintenance_date = datetime.now() - timedelta(days=40)
        self.assertTrue(self.loco.needs_maintenance())


class TestWagon(unittest.TestCase):
    """Тесты для класса Wagon"""

    def setUp(self):
        self.wagon = Wagon("W1", "passenger", 50, "business", ["wi-fi", "ac"])

    def test_wagon_creation(self):
        """Тест создания вагона"""
        self.assertEqual(self.wagon.wagon_type, "passenger")
        self.assertEqual(self.wagon.capacity, 50)
        self.assertTrue(self.wagon.is_operational)
        self.assertIn("wi-fi", self.wagon.features)

    def test_repair(self):
        """Тест ремонта вагона"""
        self.wagon.set_broken()
        self.assertFalse(self.wagon.is_operational)

        self.wagon.repair()
        self.assertTrue(self.wagon.is_operational)
        self.assertIsNotNone(self.wagon.last_repair_date)

    def test_assign_to_train(self):
        """Тест прицепки к поезду"""
        self.wagon.assign_to_train("TN1")
        self.assertEqual(self.wagon.current_train_id, "TN1")

        self.wagon.detach_from_train()
        self.assertIsNone(self.wagon.current_train_id)

    def test_capacity_display(self):
        """Тест отображения вместимости"""
        self.assertIn("мест", self.wagon.get_capacity_display())

        cargo_wagon = Wagon("W2", "cargo", 60)
        self.assertIn("тонн", cargo_wagon.get_capacity_display())


class TestTrain(unittest.TestCase):
    """Тесты для класса Train"""

    def setUp(self):
        self.loco = Locomotive("L1", "ВЛ80", 4000)
        self.train = Train("TN1", "Тестовый поезд", self.loco)
        self.wagon = Wagon("W1", "passenger", 50)

    def test_train_creation(self):
        """Тест создания поезда"""
        self.assertEqual(self.train.name, "Тестовый поезд")
        self.assertEqual(self.train.status, TrainStatus.ON_TIME)
        self.assertEqual(len(self.train.wagons), 0)
        self.assertEqual(self.train.locomotive.current_train_id, "TN1")

    def test_add_wagon(self):
        """Тест добавления вагона"""
        self.train.add_wagon(self.wagon)
        self.assertEqual(len(self.train.wagons), 1)
        self.assertEqual(self.wagon.current_train_id, "TN1")

    def test_add_broken_wagon(self):
        """Тест добавления неисправного вагона"""
        self.wagon.set_broken()
        with self.assertRaises(ValueError):
            self.train.add_wagon(self.wagon)

    def test_remove_wagon(self):
        """Тест удаления вагона"""
        self.train.add_wagon(self.wagon)
        self.train.remove_wagon("W1")
        self.assertEqual(len(self.train.wagons), 0)
        self.assertIsNone(self.wagon.current_train_id)

    def test_set_route(self):
        """Тест установки маршрута"""
        route = ["ST1", "ST2", "ST3"]
        self.train.set_route(route)
        self.assertEqual(self.train.route, route)
        self.assertEqual(self.train.current_station_index, 0)



    def test_delay(self):
        """Тест задержки поезда"""
        self.train.delay(15)
        self.assertEqual(self.train.delay_minutes, 15)
        self.assertEqual(self.train.status, TrainStatus.DELAYED)

    def test_operational_status(self):
        """Тест получения статуса исправности"""
        status = self.train.get_operational_status()
        self.assertTrue(status['locomotive_operational'])
        self.assertTrue(status['all_operational'])

    def test_total_capacity(self):
        """Тест общей вместимости"""
        self.train.add_wagon(self.wagon)
        self.train.add_wagon(Wagon("W2", "passenger", 30))
        self.assertEqual(self.train.get_total_capacity(), 80)


class TestTicket(unittest.TestCase):
    """Тесты для класса Ticket"""

    def setUp(self):
        self.departure_time = datetime.now() + timedelta(days=3)
        self.ticket = Ticket(
            ticket_id="T1",
            train_id="TN1",
            passenger_name="Иванов Иван",
            from_station_id="ST1",
            to_station_id="ST2",
            departure_time=self.departure_time,
            price=1000.0,
            ticket_class=TicketClass.SECOND,
            wagon_number=2,
            seat_number=15
        )

    def test_ticket_creation(self):
        """Тест создания билета"""
        self.assertEqual(self.ticket.passenger_name, "Иванов Иван")
        self.assertEqual(self.ticket.price, 1000.0)
        self.assertTrue(self.ticket.is_valid)
        self.assertEqual(self.ticket.payment_status, PaymentStatus.PENDING)

    def test_cancel_ticket(self):
        """Тест отмены билета"""
        self.ticket.cancel()
        self.assertFalse(self.ticket.is_valid)
        self.assertEqual(self.ticket.payment_status, PaymentStatus.REFUNDED)
        self.assertIsNotNone(self.ticket.cancelled_at)

    def test_cancel_already_cancelled(self):
        """Тест повторной отмены"""
        self.ticket.cancel()
        with self.assertRaises(ValueError):
            self.ticket.cancel()

    def test_mark_as_paid(self):
        """Тест оплаты билета"""
        self.ticket.mark_as_paid()
        self.assertEqual(self.ticket.payment_status, PaymentStatus.COMPLETED)

    def test_is_refundable(self):
        """Тест возможности возврата"""
        self.assertTrue(self.ticket.is_refundable())

        # Билет на прошедшую дату
        past_ticket = Ticket(
            ticket_id="T2", train_id="TN1", passenger_name="Test",
            from_station_id="ST1", to_station_id="ST2",
            departure_time=datetime.now() - timedelta(days=1),
            price=1000, ticket_class=TicketClass.SECOND, wagon_number=1, seat_number=1
        )
        self.assertFalse(past_ticket.is_refundable())


# ==================== ТЕСТЫ СЕРВИСА ====================

class TestRailwayService(unittest.TestCase):
    """Тесты для RailwayService"""

    def setUp(self):
        """Подготовка тестовых данных"""
        self.service = RailwayService()

        # Очищаем демо-данные для чистоты тестов
        self.service.tracks.clear()
        self.service.stations.clear()
        self.service.locomotives.clear()
        self.service.wagons.clear()
        self.service.trains.clear()
        self.service.schedule.clear()
        self.service.tickets.clear()

        # Создаем тестовые данные
        self.station1 = self.service.add_station("Москва", StationType.PASSENGER, "Москва", 10)
        self.station2 = self.service.add_station("СПб", StationType.PASSENGER, "Санкт-Петербург", 8)

        self.track = self.service.add_track("Главный путь", 650.0, 200)
        self.station1.add_track(self.track.id)
        self.station2.add_track(self.track.id)

        self.loco = self.service.add_locomotive("Тестовый локомотив", 4000)
        self.train = self.service.add_train("Тестовый поезд", self.loco.id)
        self.train.set_route([self.station1.id, self.station2.id])

        self.wagon = self.service.add_wagon("passenger", 50)
        self.train.add_wagon(self.wagon)

    def test_add_station(self):
        """Тест добавления станции"""
        station = self.service.add_station("Казань", StationType.PASSENGER, "Казань", 5)
        self.assertEqual(station.name, "Казань")
        self.assertIn(station.id, self.service.stations)

    def test_add_track(self):
        """Тест добавления пути"""
        track = self.service.add_track("Новый путь", 100.0, 80)
        self.assertEqual(track.name, "Новый путь")
        self.assertIn(track.id, self.service.tracks)

    def test_add_train(self):
        """Тест добавления поезда"""
        train = self.service.add_train("Новый поезд", self.loco.id)
        self.assertEqual(train.name, "Новый поезд")
        self.assertIn(train.id, self.service.trains)

    def test_add_wagon_to_train(self):
        """Тест добавления вагона к поезду"""
        new_wagon = self.service.add_wagon("cargo", 30)
        self.service.add_wagon_to_train(self.train.id, new_wagon.id)
        self.assertEqual(len(self.train.wagons), 2)

    def test_move_train_success(self):
        """Тест успешного перемещения поезда"""
        result = self.service.move_train(self.train.id, self.track.id)
        self.assertTrue(result['success'])
        self.assertTrue(self.track.is_occupied)
        self.assertEqual(self.track.occupied_by_train_id, self.train.id)

    def test_move_train_track_not_found(self):
        """Тест перемещения на несуществующий путь"""
        with self.assertRaises(TrackNotFoundError):
            self.service.move_train(self.train.id, "NON_EXISTENT")

    def test_move_train_track_occupied(self):
        """Тест перемещения на занятый путь"""
        self.track.occupy("OTHER_TRAIN")

        with self.assertRaises(TrackOccupiedError):
            self.service.move_train(self.train.id, self.track.id)

    def test_get_train_location(self):
        """Тест получения местоположения поезда"""
        self.service.move_train(self.train.id, self.track.id)
        location = self.service.get_train_location(self.train.id)

        self.assertIsNotNone(location)
        self.assertEqual(location['train_id'], self.train.id)
        self.assertEqual(location['track_id'], self.track.id)

    def test_buy_ticket_success(self):
        """Тест успешной покупки билета"""
        ticket = self.service.buy_ticket(
            train_id=self.train.id,
            passenger_name="Тестовый пассажир",
            from_station_id=self.station1.id,
            to_station_id=self.station2.id,
            departure_time=datetime.now(),
            ticket_class=TicketClass.ECONOMY,
            wagon_number=1,
            seat_number=10
        )

        self.assertIsNotNone(ticket)
        self.assertEqual(ticket.passenger_name, "Тестовый пассажир")
        self.assertIn(ticket.id, self.service.tickets)

    def test_buy_ticket_no_seats(self):
        """Тест покупки билета при отсутствии мест"""
        # Создаем поезд без вагонов
        empty_train = self.service.add_train("Пустой поезд", self.loco.id)

        with self.assertRaises(NoAvailableSeatsError):
            self.service.buy_ticket(
                train_id=empty_train.id,
                passenger_name="Пассажир",
                from_station_id=self.station1.id,
                to_station_id=self.station2.id,
                departure_time=datetime.now(),
                ticket_class=TicketClass.ECONOMY,
                wagon_number=1,
                seat_number=1
            )

    def test_buy_ticket_seat_already_booked(self):
        """Тест покупки уже занятого места"""
        # Покупаем первое место
        self.service.buy_ticket(
            train_id=self.train.id,
            passenger_name="Пассажир 1",
            from_station_id=self.station1.id,
            to_station_id=self.station2.id,
            departure_time=datetime.now(),
            ticket_class=TicketClass.ECONOMY,
            wagon_number=1,
            seat_number=1
        )

        # Пытаемся купить то же место
        with self.assertRaises(SeatAlreadyBookedError):
            self.service.buy_ticket(
                train_id=self.train.id,
                passenger_name="Пассажир 2",
                from_station_id=self.station1.id,
                to_station_id=self.station2.id,
                departure_time=datetime.now(),
                ticket_class=TicketClass.ECONOMY,
                wagon_number=1,
                seat_number=1
            )

    def test_cancel_ticket(self):
        """Тест отмены билета"""
        ticket = self.service.buy_ticket(
            train_id=self.train.id,
            passenger_name="Пассажир",
            from_station_id=self.station1.id,
            to_station_id=self.station2.id,
            departure_time=datetime.now() + timedelta(days=3),
            ticket_class=TicketClass.ECONOMY,
            wagon_number=1,
            seat_number=5
        )

        result = self.service.cancel_ticket(ticket.id)
        self.assertGreater(result['refund_amount'], 0)
        self.assertFalse(ticket.is_valid)

    def test_pay_for_ticket(self):
        """Тест оплаты билета"""
        ticket = self.service.buy_ticket(
            train_id=self.train.id,
            passenger_name="Пассажир",
            from_station_id=self.station1.id,
            to_station_id=self.station2.id,
            departure_time=datetime.now(),
            ticket_class=TicketClass.ECONOMY,
            wagon_number=1,
            seat_number=5
        )

        paid_ticket = self.service.pay_for_ticket(ticket.id)
        self.assertEqual(paid_ticket.payment_status, PaymentStatus.COMPLETED)



    def test_safety_check_success(self):
        """Тест успешной проверки безопасности"""
        result = self.service.check_train_safety(self.train.id)
        self.assertTrue(result['safety_check_passed'])
        self.assertEqual(len(result['issues']), 0)

    def test_safety_check_fail(self):
        """Тест проваленной проверки безопасности"""
        # Делаем локомотив неисправным
        self.train.locomotive.set_broken()

        with self.assertRaises(SafetyViolationError):
            self.service.check_train_safety(self.train.id)

    def test_pre_departure_check(self):
        """Тест предотправного контроля"""
        safety_check = self.service.perform_pre_departure_check(self.train.id)

        self.assertIsNotNone(safety_check)
        self.assertIn(safety_check.id, self.service.safety_checks)
        self.assertEqual(safety_check.train_id, self.train.id)

    def test_perform_maintenance(self):
        """Тест проведения ТО"""
        record = self.service.perform_maintenance(self.loco.id)

        self.assertIsNotNone(record)
        self.assertIn(record.id, self.service.maintenance_records)
        self.assertTrue(self.loco.is_operational)

    def test_repair_wagon(self):
        """Тест ремонта вагона"""
        self.wagon.set_broken()
        record = self.service.repair_wagon(self.wagon.id)

        self.assertIsNotNone(record)
        self.assertTrue(self.wagon.is_operational)

    def test_operational_status(self):
        """Тест получения статуса исправности"""
        status = self.service.get_operational_status(self.train.id)

        self.assertTrue(status['locomotive_operational'])
        self.assertTrue(status['all_operational'])

    def test_station_info(self):
        """Тест получения информации о станции"""
        info = self.service.get_station_info(self.station1.id)

        self.assertEqual(info['station'].id, self.station1.id)
        self.assertIn('trains_count', info)
        self.assertIn('utilization', info)

    def test_get_trains_at_station(self):
        """Тест получения поездов на станции"""
        # Перемещаем поезд на путь станции
        self.service.move_train(self.train.id, self.track.id)

        trains = self.service.get_trains_at_station(self.station1.id)
        self.assertEqual(len(trains), 1)
        self.assertEqual(trains[0].id, self.train.id)

    def test_statistics(self):
        """Тест получения статистики"""
        stats = self.service.get_statistics()

        self.assertGreaterEqual(stats['total_trains'], 0)
        self.assertGreaterEqual(stats['total_stations'], 0)
        self.assertIn('total_revenue', stats)

    def test_get_user_tickets(self):
        """Тест получения билетов пользователя"""
        passenger_name = "Тестовый пассажир"

        self.service.buy_ticket(
            train_id=self.train.id,
            passenger_name=passenger_name,
            from_station_id=self.station1.id,
            to_station_id=self.station2.id,
            departure_time=datetime.now() + timedelta(days=1),
            ticket_class=TicketClass.ECONOMY,
            wagon_number=1,
            seat_number=20
        )

        tickets = self.service.get_user_tickets(passenger_name)
        self.assertEqual(len(tickets), 1)
        self.assertEqual(tickets[0].passenger_name, passenger_name)


# ==================== ТЕСТЫ ИСКЛЮЧЕНИЙ ====================

class TestExceptions(unittest.TestCase):
    """Тесты для пользовательских исключений"""

    def test_railway_exception_base(self):
        """Тест базового исключения"""
        exc = RailwayException("Тестовая ошибка")
        self.assertEqual(str(exc), "Тестовая ошибка")

        exc_with_details = RailwayException("Ошибка", details={"code": 123})
        self.assertIn("123", str(exc_with_details))

    def test_train_not_found(self):
        """Тест исключения TrainNotFoundError"""
        with self.assertRaises(TrainNotFoundError):
            raise TrainNotFoundError("Поезд не найден")

    def test_track_occupied(self):
        """Тест исключения TrackOccupiedError"""
        with self.assertRaises(TrackOccupiedError):
            raise TrackOccupiedError("Путь занят")

    def test_safety_violation(self):
        """Тест исключения SafetyViolationError"""
        with self.assertRaises(SafetyViolationError):
            raise SafetyViolationError("Нарушение безопасности")

    def test_no_available_seats(self):
        """Тест исключения NoAvailableSeatsError"""
        with self.assertRaises(NoAvailableSeatsError):
            raise NoAvailableSeatsError("Нет свободных мест")


# ==================== ЗАПУСК ТЕСТОВ ====================

def run_all_tests():
    """Запуск всех тестов с подробным выводом"""

    # Создаем загрузчик тестов
    loader = unittest.TestLoader()

    # Создаем набор тестов
    suite = unittest.TestSuite()

    # Добавляем все тестовые классы
    suite.addTests(loader.loadTestsFromTestCase(TestRailwayTrack))
    suite.addTests(loader.loadTestsFromTestCase(TestStation))
    suite.addTests(loader.loadTestsFromTestCase(TestLocomotive))
    suite.addTests(loader.loadTestsFromTestCase(TestWagon))
    suite.addTests(loader.loadTestsFromTestCase(TestTrain))
    suite.addTests(loader.loadTestsFromTestCase(TestTicket))
    suite.addTests(loader.loadTestsFromTestCase(TestRailwayService))
    suite.addTests(loader.loadTestsFromTestCase(TestExceptions))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Выводим статистику
    print("\n" + "=" * 70)
    print("  📊 СТАТИСТИКА ТЕСТИРОВАНИЯ")
    print("=" * 70)
    print(f"  Всего тестов: {result.testsRun}")
    print(f"  ✅ Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  ❌ Провалено: {len(result.failures)}")
    print(f"  ⚠️ Ошибок: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n  🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n  ⚠️ ЕСТЬ ПРОБЛЕМЫ В ТЕСТАХ!")

    return result.wasSuccessful()


if __name__ == "__main__":
    import sys

    # Поддержка аргументов командной строки
    if len(sys.argv) > 1 and sys.argv[1] == "--verbose":
        sys.argv.remove("--verbose")
        unittest.main(verbosity=2)
    else:
        success = run_all_tests()
        sys.exit(0 if success else 1)