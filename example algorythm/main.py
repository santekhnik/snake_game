def crc16_ccitt(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        # Дані байтом "втягуються" у верхній байт CRC
        crc ^= byte << 8
        for _ in range(8):
            # Якщо встановлено найстарший біт (0x8000 == 1000 0000 0000 0000)
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # Залишаємо лише 16 біт
    return crc

START_BYTE = 0x7E
res=0
def encode_frame(payload: bytes) -> bytes:
    """
    Формує кадр за форматом:
    [START_BYTE][LENGTH][PAYLOAD][CRC_HIGH][CRC_LOW]
    """
    payload_len = len(payload)
    frame = bytearray()
    frame.append(START_BYTE)         # Стартовий байт
    frame.append(payload_len)        # Довжина даних
    frame.extend(payload)            # Копіювання payload
    crc = crc16_ccitt(payload)       # Обчислення CRC-16
    # Додавання CRC (старший байт перший)
    frame.append((crc >> 8) & 0xFF)
    frame.append(crc & 0xFF)
    #print(frame)
    #del frame [-4]
    #print(frame)
    #frame.insert(-3,53)

    #print(frame)
    return bytes(frame)

def decode_frame(frame: bytes) -> bool:
    """
    Перевіряє коректність кадру.
    Повертає True, якщо кадр валідний, інакше False.
    """
    # Мінімальна довжина кадру: 1 (START) + 1 (LENGTH) + 0 (PAYLOAD) + 2 (CRC) = 4 байти
    if len(frame) < 4:
        print("Кадр занадто короткий.")
        return False
    if frame[0] != START_BYTE:
        print("Невірний стартовий байт.")
        return False
    payload_len = frame[1]
    expected_len = payload_len + 4
    if len(frame) != expected_len:
        print("Невідповідність довжини кадру.")
        return False
    # Отримання переданого CRC (big-endian)
    received_crc = (frame[2 + payload_len] << 8) | frame[2 + payload_len + 1]
    computed_crc = crc16_ccitt(frame[2:2 + payload_len])
    if received_crc == computed_crc:
        print("Кадр валідний. CRC співпадає.")
        return True
    else:
        print("Помилка CRC. Кадр пошкоджено.")
        return False

if __name__ == "__main__":
    payload = b"Hello, CRC16!"
    frame = encode_frame(payload)
    print("Закодований кадр:", frame.hex())
    if decode_frame(frame):
        print("Декодування успішне!")
    else:
        print("Декодування невдале!")
