#!/usr/bin/env python3
import base64
import sys
import os
from gostcrypto import gosthash


def calculate_gost_hash(file_path, hash_size=256):
    """
    Вычисляет ГОСТ 34.11-2012 хеш с использованием библиотеки gostcrypto

    Args:
        file_path: путь к файлу
        hash_size: размер хеша (256 или 512 бит)

    Returns:
        dict: хеши в форматах base64 и hex
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            print(f"❌ Ошибка: Файл '{file_path}' не найден")
            return None

        if not os.path.isfile(file_path):
            print(f"❌ Ошибка: '{file_path}' не является файлом")
            return None

        # Читаем файл
        with open(file_path, 'rb') as f:
            file_data = f.read()

        file_size = len(file_data)
        print(f"✓ Файл: {os.path.basename(file_path)}")
        print(f"✓ Размер: {file_size} байт")

        # Выбираем алгоритм
        if hash_size == 256:
            hash_obj = gosthash.new('streebog256')
            print("✓ Алгоритм: ГОСТ 34.11-2012 (256 бит)")
        elif hash_size == 512:
            hash_obj = gosthash.new('streebog512')
            print("✓ Алгоритм: ГОСТ 34.11-2012 (512 бит)")
        else:
            print(f"❌ Неподдерживаемый размер хеша: {hash_size}")
            return None

        # Вычисляем хеш
        hash_obj.update(file_data)
        hash_bytes = hash_obj.digest()

        print(f"✓ Размер хеша: {len(hash_bytes)} байт ({len(hash_bytes) * 8} бит)")

        # Преобразуем в форматы
        hex_hash = hash_bytes.hex()
        base64_hash = base64.b64encode(hash_bytes).decode('ascii')

        # Выводим результаты
        print("\n" + "═" * 70)
        print("РЕЗУЛЬТАТЫ:")
        print("═" * 70)
        print(f"ГОСТ хэш(base64): {base64_hash}")
        print(f"ГОСТ хэш(hex): {hex_hash}")
        print("═" * 70)

        # Дополнительная информация
        print(f"\n📊 Статистика:")
        print(f"   Длина Base64: {len(base64_hash)} символов")
        print(f"   Длина HEX: {len(hex_hash)} символов")

        # Проверка обратного преобразования
        print("\n🔍 Проверка корректности преобразований:")
        decoded_from_base64 = base64.b64decode(base64_hash)
        hex_from_base64 = decoded_from_base64.hex()

        if hex_hash == hex_from_base64:
            print("   ✓ Base64 → HEX преобразование корректно")
        else:
            print("   ✗ Ошибка в преобразовании Base64 → HEX")

        return {
            'base64': base64_hash,
            'hex': hex_hash,
            'bytes': hash_bytes,
            'size': hash_size
        }

    except Exception as e:
        print(f"❌ Ошибка при вычислении хеша: {str(e)}")
        return None


def compare_with_expected(base64_hash, hex_hash):
    """
    Сравнивает вычисленные хеши с ожидаемыми значениями
    """
    print("\n🔍 Сравнение с вашим хешем:")
    print("═" * 70)

    # Ваш хеш из вопроса
    your_hash = "2sndxr9wILV1SHL8XocaCfqKL/RlKFZNyOoRAHWQChs="

    if base64_hash == your_hash:
        print("✅ Base64 хеши СОВПАДАЮТ!")
        print(f"   Вычисленный: {base64_hash}")
        print(f"   Ожидаемый:   {your_hash}")
    else:
        print("❌ Base64 хеши НЕ совпадают!")
        print(f"   Вычисленный: {base64_hash}")
        print(f"   Ожидаемый:   {your_hash}")

        # Показываем различия
        if len(base64_hash) == len(your_hash):
            diffs = []
            for i, (c1, c2) in enumerate(zip(base64_hash, your_hash)):
                if c1 != c2:
                    diffs.append(f"позиция {i}: '{c1}' vs '{c2}'")
            if diffs:
                print(f"   Различия: {', '.join(diffs[:5])}...")

    print("═" * 70)


def save_results(results, file_path):
    """
    Сохраняет результаты в текстовый файл
    """
    if not results:
        return

    output_file = f"{file_path}_gost_hash.txt"

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("ГОСТ 34.11-2012 ХЕШ\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Файл: {file_path}\n")
            f.write(f"Размер файла: {os.path.getsize(file_path)} байт\n")
            f.write(f"Алгоритм: ГОСТ 34.11-2012-{results['size']}\n\n")
            f.write(f"ГОСТ хэш(base64): {results['base64']}\n")
            f.write(f"ГОСТ хэш(hex): {results['hex']}\n")
            f.write(f"\nДата: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        print(f"\n💾 Результаты сохранены в: {output_file}")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить результаты: {e}")


def main():
    """
    Основная функция с обработкой аргументов командной строки
    """
    import argparse
    import datetime

    parser = argparse.ArgumentParser(
        description='Вычисляет ГОСТ 34.11-2012 хеш для файла',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s document.pdf           # Вычислить 256-битный хеш
  %(prog)s file.bin --size 512    # Вычислить 512-битный хеш
  %(prog)s data.txt --compare     # Сравнить с вашим хешем
  %(prog)s image.jpg --save       # Сохранить результаты в файл
        """
    )

    parser.add_argument('file', help='Путь к файлу для хеширования')
    parser.add_argument('--size', type=int, choices=[256, 512], default=256,
                        help='Размер хеша: 256 или 512 бит (по умолчанию: 256)')
    parser.add_argument('--compare', action='store_true',
                        help='Сравнить с вашим хешем из примера')
    parser.add_argument('--save', action='store_true',
                        help='Сохранить результаты в текстовый файл')
    parser.add_argument('--verify', action='store_true',
                        help='Проверить преобразования между форматами')

    args = parser.parse_args()

    # Проверяем файл
    if not os.path.exists(args.file):
        print(f"❌ Файл не найден: {args.file}")
        sys.exit(1)

    # Вычисляем хеш
    results = calculate_gost_hash(args.file, args.size)

    if not results:
        sys.exit(1)

    # Сравниваем с ожидаемым хешем
    if args.compare:
        compare_with_expected(results['base64'], results['hex'])

    # Сохраняем результаты
    if args.save:
        save_results(results, args.file)

    # Проверка преобразований
    if args.verify:
        print("\n🔍 Детальная проверка преобразований:")
        print("-" * 40)

        # Base64 → байты → HEX
        decoded = base64.b64decode(results['base64'])
        hex_from_base64 = decoded.hex()

        # HEX → байты → Base64
        bytes_from_hex = bytes.fromhex(results['hex'])
        base64_from_hex = base64.b64encode(bytes_from_hex).decode('ascii')

        checks = [
            ("Base64 → HEX", results['hex'] == hex_from_base64),
            ("HEX → Base64", results['base64'] == base64_from_hex),
            ("Байты совпадают", results['bytes'] == decoded),
        ]

        for name, check in checks:
            status = "✓" if check else "✗"
            print(f"{status} {name}")

        if all(check for _, check in checks):
            print("✅ Все преобразования корректны!")
        else:
            print("❌ Обнаружены ошибки в преобразованиях")


if __name__ == "__main__":
    main()