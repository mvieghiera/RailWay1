#!/usr/bin/env python3
"""
Железнодорожная система управления
Точка входа в программу

Автор: Система управления железнодорожным транспортом
Версия: 1.0
"""

import sys
import argparse
from pathlib import Path

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, str(Path(__file__).parent))

from cli import RailwayCLI
from exceptions import RailwayException


def parse_arguments():
    """
    Разбор аргументов командной строки

    Returns:
        argparse.Namespace: Разобранные аргументы
    """
    parser = argparse.ArgumentParser(
        prog="railway_system",
        description="Система управления железнодорожным транспортом",
        epilog="Пример использования: python main.py\n"
               "                  python main.py --help\n"
               "                  python main.py --version"
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s 1.0.0",
        help="Показать версию программы"
    )

    parser.add_argument(
        "--no-welcome",
        action="store_true",
        help="Не показывать приветственное сообщение"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Запустить в демонстрационном режиме с предустановленными данными"
    )

    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Путь к файлу конфигурации (опционально)"
    )

    return parser.parse_args()


def print_banner():
    """Вывод баннера программы"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║     ██████╗  █████╗ ██╗██╗     ██╗    ██╗ █████╗ ██╗   ██╗     ║
    ║     ██╔══██╗██╔══██╗██║██║     ██║    ██║██╔══██╗╚██╗ ██╔╝     ║
    ║     ██████╔╝███████║██║██║     ██║ █╗ ██║███████║ ╚████╔╝      ║
    ║     ██╔══██╗██╔══██║██║██║     ██║███╗██║██╔══██║  ╚██╔╝       ║
    ║     ██║  ██║██║  ██║██║███████╗╚███╔███╔╝██║  ██║   ██║        ║
    ║     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝   ╚═╝        ║
    ║                                                                  ║
    ║              ЖЕЛЕЗНОДОРОЖНАЯ СИСТЕМА УПРАВЛЕНИЯ                  ║
    ║                      Версия 1.0 | 2024                           ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_system_info():
    """Вывод информации о системе"""
    import platform

    print("\n  📋 ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("  " + "-" * 50)
    print(f"     Python: {platform.python_version()}")
    print(f"     ОС: {platform.system()} {platform.release()}")
    print(f"     Архитектура: {platform.machine()}")
    print("-" * 50)


def check_requirements():
    """
    Проверка системных требований

    Returns:
        bool: True если все требования выполнены, иначе False
    """
    import sys

    # Проверка версии Python
    if sys.version_info < (3, 8):
        print("  ❌ ОШИБКА: Требуется Python версии 3.8 или выше")
        print(f"     Текущая версия: {sys.version_info.major}.{sys.version_info.minor}")
        return False

    # Проверка наличия необходимых модулей
    try:
        import datetime
        import typing
        import enum
    except ImportError as e:
        print(f"  ❌ ОШИБКА: Не удалось импортировать стандартный модуль: {e}")
        return False

    return True


def setup_logging():
    """Настройка логирования (опционально)"""
    import logging

    # Настройка базового логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('railway_system.log', encoding='utf-8'),
        ]
    )

    return logging.getLogger(__name__)


def main():
    """
    Главная функция запуска приложения
    """
    # Парсинг аргументов командной строки
    args = parse_arguments()

    # Проверка системных требований
    if not check_requirements():
        sys.exit(1)

    # Настройка логирования
    logger = setup_logging()
    logger.info("Запуск железнодорожной системы управления")

    # Вывод баннера (если не отключено)
    if not args.no_welcome:
        print_banner()
        print_system_info()

    try:
        # Создание и запуск CLI
        cli = RailwayCLI()

        # Если запрошен демонстрационный режим
        if args.demo:
            print("\n  🎯 ЗАПУСК В ДЕМОНСТРАЦИОННОМ РЕЖИМЕ")
            print("  " + "-" * 50)
            print("  Система уже содержит демонстрационные данные:")
            print("     • Станции: Москва, Санкт-Петербург, Нижний Новгород, Казань")
            print("     • Поезда: Сапсан 751А, Ласточка 701И, ВЛ80-202 (грузовой)")
            print("     • Локомотивы: 4 шт.")
            print("     • Вагоны: 20 шт.")
            print("     • Расписание: готово")
            print("  " + "-" * 50)

        # Запуск основного цикла
        cli.run()

    except KeyboardInterrupt:
        print("\n\n  👋 Программа прервана пользователем")
        logger.info("Программа прервана пользователем (Ctrl+C)")

    except RailwayException as e:
        print(f"\n  ❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)

    except Exception as e:
        print(f"\n  ❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        logger.error(f"Непредвиденная ошибка: {e}", exc_info=True)
        sys.exit(1)

    finally:
        logger.info("Завершение работы железнодорожной системы")
        print("\n  🚂 Система остановлена. Спасибо за использование!")


def run_with_profile():
    """
    Запуск с профилированием (для отладки производительности)
    """
    import cProfile
    import pstats
    from io import StringIO

    profiler = cProfile.Profile()
    profiler.enable()

    main()

    profiler.disable()

    # Вывод статистики профилирования
    s = StringIO()
    stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
    stats.print_stats(20)

    with open('profile_stats.txt', 'w', encoding='utf-8') as f:
        f.write(s.getvalue())


if __name__ == "__main__":
    """
    Точка входа в программу
    Поддерживаемые аргументы командной строки:
        --version, -v      - показать версию
        --no-welcome       - не показывать приветственное сообщение
        --demo             - запустить в демонстрационном режиме
        --config <file>    - указать файл конфигурации
    """

    # Проверка на запуск с профилированием
    if '--profile' in sys.argv:
        sys.argv.remove('--profile')
        run_with_profile()
    else:
        main()