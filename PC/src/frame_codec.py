import struct

START_BYTE = 0x7E
CMD_GAME_DATA = 0x02
CRC_POLY = 0x1021


# Функція обчислення CRC-16-CCITT
def crc16_ccitt(data: bytes, cmd: int, frog_x: int, frog_y: int, poly=CRC_POLY, init=0xFFFF):
    crc = init

    crc ^= (cmd << 8)
    crc ^= (frog_x << 8) | frog_y

    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc


# Функція кодування пакета (тепер повертає HEX-рядок)
def encode_frame(cmd: int, payload: str, frog_x: int, frog_y: int) -> str:
    """
    [START] [CMD] [LEN] [PAYLOAD (текст)] [FROG_X (1 байт)] [FROG_Y (1 байт)] [CRC] -> HEX
    """
    payload_bytes = payload.encode('utf-8')
    payload_len = len(payload_bytes)

    frame = bytearray()
    frame.append(START_BYTE)
    frame.append(cmd)
    frame.append(payload_len)
    frame.extend(payload_bytes)

    frame.extend(struct.pack('<BB', frog_x, frog_y))

    crc = crc16_ccitt(payload_bytes, cmd, frog_x, frog_y)
    frame.append((crc >> 8) & 0xFF)
    frame.append(crc & 0xFF)

    return frame.hex().upper()  # ✅ Повертаємо HEX-рядок у ВЕРХНЬОМУ регістрі


# Функція декодування пакета (тепер приймає HEX-рядок)
def decode_frame(hex_str: str) -> dict:
    """Розбирає HEX-пакет, перевіряє CRC та отримує корисні дані"""

    frame = bytes.fromhex(hex_str)  # ✅ Перетворюємо HEX у байти

    if len(frame) < 7:
        return {"status": "error", "message": "Кадр занадто короткий"}

    if frame[0] != START_BYTE:
        return {"status": "error", "message": "Невірний стартовий байт"}

    cmd = frame[1]
    payload_len = frame[2]

    expected_len = 3 + payload_len + 2 + 2

    if len(frame) != expected_len:
        return {"status": "error",
                "message": f"Невідповідність довжини пакета. Очікувано {expected_len}, отримано {len(frame)}"}

    payload_bytes = frame[3:3 + payload_len]
    payload = payload_bytes.decode('utf-8')

    frog_x, frog_y = struct.unpack('<BB', frame[3 + payload_len:3 + payload_len + 2])

    received_crc = (frame[-2] << 8) | frame[-1]
    computed_crc = crc16_ccitt(payload_bytes, cmd, frog_x, frog_y)

    return {
        "status": "success" if received_crc == computed_crc else "error",
        "cmd": cmd,
        "payload": payload,
        "frog": (frog_x, frog_y),
        "received_crc": received_crc,
        "computed_crc": computed_crc,
        "crc_match": received_crc == computed_crc,
    }
