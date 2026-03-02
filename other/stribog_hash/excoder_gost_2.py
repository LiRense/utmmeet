#!/usr/bin/env python3
import base64
import os
from gostcrypto import gosthash


def simple_gost_hash():
    """
    Простая версия с вводом пути к файлу
    """
    print("=" * 60)
    print("Вычисление ГОСТ 34.11-2012 хеша")
    print("=" * 60)

    # Запрашиваем путь к файлу
    file_path = 'file_data2.pdf'

    if not os.path.exists(file_path):
        print(f"\n❌ Файл не найден: {file_path}")
        return

    # Выбираем размер хеша
    print("\nВыберите размер хеша:")
    print("1. 256 бит (по умолчанию)")
    print("2. 512 бит")
    choice = input("Ваш выбор [1]: ").strip()

    hash_size = 512 if choice == "2" else 256

    try:
        # Читаем файл
        with open(file_path, 'rb') as f:
            data = f.read()

        print(f"\n📄 Файл: {os.path.basename(file_path)}")
        print(f"📊 Размер: {len(data):,} байт")

        # Создаем хеш-объект
        if hash_size == 256:
            hasher = gosthash.new('streebog256')
        else:
            hasher = gosthash.new('streebog512')

        # Вычисляем хеш
        hasher.update(data)
        hash_bytes = hasher.digest()

        # Преобразуем
        hex_hash = hash_bytes.hex()
        base64_hash = base64.b64encode(hash_bytes).decode('ascii')

        # Выводим результат
        print("\n" + "=" * 60)
        print("РЕЗУЛЬТАТ:")
        print("=" * 60)
        print(f"Base64: {base64_hash}")
        print(f"HEX:    {hex_hash}")
        print("=" * 60)

        # Сохраняем в файл
        save = input("\nСохранить в файл? (y/n): ").lower()
        if save == 'y':
            output_file = f"{file_path}.hash.txt"
            with open(output_file, 'w') as f:
                f.write(f"Файл: {file_path}\n")
                f.write(f"ГОСТ 34.11-2012-{hash_size}\n")
                f.write(f"Base64: {base64_hash}\n")
                f.write(f"HEX: {hex_hash}\n")
            print(f"✓ Сохранено в {output_file}")

    except Exception as e:
        print(f"\n❌ Ошибка: {e}")


if __name__ == "__main__":
    simple_gost_hash()