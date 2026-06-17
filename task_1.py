import struct

def parse_binary_file(file_path):
    with open(file_path, 'rb') as f:

        signature = f.read(4)
        if signature != b'DATA':
            print("Некорректная сигнатура файла")
            return

        version_bytes = f.read(2)
        if len(version_bytes) < 2:
            print("Ошибка при чтении версии")
            return
        (version,) = struct.unpack('<H', version_bytes)

        count_bytes = f.read(4)
        if len(count_bytes) < 4:
            print("Ошибка при чтении количества записей")
            return
        (record_count,) = struct.unpack('<I', count_bytes)

        print(f"Сигнатура: {signature}")
        print(f"Версия: {version}")
        print(f"Количество записей: {record_count}")

        temperatures = []
        active_flags_count = 0

        for i in range(record_count):
            record_bytes = f.read(8 + 4 + 2 + 1)  # 15 байт
            if len(record_bytes) < 15:
                print(f"Ошибка при чтении записи {i+1}")
                break

            timestamp, id_, temp_raw, flag = struct.unpack('<Q I h B', record_bytes)

            temperature = temp_raw / 100.0
            temperatures.append(temperature)

            if flag != 0:
                active_flags_count += 1

        if temperatures:
            avg_temp = sum(temperatures) / len(temperatures)
            print(f"Средняя температура: {avg_temp:.2f}°C")
        else:
            print("Нет данных для вычисления средней температуры.")

        print(f"Количество активных флагов: {active_flags_count}")