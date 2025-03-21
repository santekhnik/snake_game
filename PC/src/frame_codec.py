import struct

class STMProtocol:
    START_BYTE = 0x7E
    CRC_POLY = 0x1021
    ENCODE_COMMANDS = [1, 3, 5]
    DECODE_COMMANDS = [1, 2, 4, 6]

    def __init__(self):
        self.pause = False


    def encode_frame(self, cmd: int, payload):
        """Кодування пакета в залежності від команди"""
        if cmd not in self.ENCODE_COMMANDS:
            return {"status": "error", "message": "Невідома команда"}
        return self._encode_frame(cmd, payload)

    def decode_frame(self, frame):
        """
        Декодує отриманий пакет, перевіряє CRC та повертає дані.
        """
        if len(frame) < 5:
            return {"status": "error", "message": "Короткий пакет"}

        if frame[0] != self.START_BYTE:
            return {"status": "error", "message": "Невірний стартовий байт"}

        cmd = frame[1]

        if cmd == 2:
            expected_length = frame[2] + 7  # LEN + [START] [CMD] [LEN] [CRC_H] [CRC_L]
            if len(frame) != expected_length:
                return {"status": "error",
                        "message": f"Невідповідність довжини пакета. Очікувано {expected_length}, отримано {len(frame)}"}

        match cmd:
            case 2:
                return self._decode_game_data(frame)
            case 1 | 3 | 4 | 6:
                return self._decode(frame)

    def crc16_ccitt(self, data: bytes, cmd: int = 0, frog_x: int = 0, frog_y: int = 0, poly=0x1021, init=0xFFFF):
        """Обчислює CRC-16-CCITT для будь-яких даних"""
        crc = init
        crc ^= (cmd << 8)
        crc ^= (frog_x << 8) | frog_y

        for byte in data:
            crc ^= (byte << 8)
            for _ in range(8):
                crc = (crc << 1) ^ poly if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
        return crc

    def _encode_frame(self, cmd: int, payload):
        """
        [START] [CMD] [PAYLOAD] [CRC]
        """
        if isinstance(payload, int):
            payload = bytes([payload])
        elif isinstance(payload, str):
            payload = payload.encode()

        frame = bytearray([self.START_BYTE, cmd])
        frame.extend(payload)

        crc = self.crc16_ccitt(payload, cmd)
        frame.append((crc >> 8) & 0xFF)
        frame.append(crc & 0xFF)

        return frame

    def _decode_game_data(self, frame):
        """[START] [CMD] [LEN] [PAYLOAD] [FROG_X (1 байт)] [FROG_Y (1 байт)] [CRC]"""
        cmd, payload_len = frame[1], frame[2]

        expected_len = 3 + payload_len + 2 + 2
        if len(frame) != expected_len:
            return {"status": "error",
                    "message": f"Невідповідність довжини пакета. Очікувано {expected_len}, отримано {len(frame)}"}

        payload_bytes = frame[3:3 + payload_len]
        if len(payload_bytes) % 2 != 0:
            return {"status": "error", "message": "Непарна кількість байтів у payload"}

        payload = [(payload_bytes[i], payload_bytes[i + 1]) for i in range(0, len(payload_bytes), 2)]
        frog_x, frog_y = struct.unpack('<BB', frame[3 + payload_len:3 + payload_len + 2])

        received_crc = (frame[-2] << 8) | frame[-1]
        computed_crc = self.crc16_ccitt(payload_bytes, cmd, frog_x, frog_y)

        return {
            "status": "success" if received_crc == computed_crc else "error",
            "cmd": cmd,
            "len_payload": payload_len,
            "payload": payload,
            "frog": (frog_x, frog_y),
            "received_crc": received_crc,
            "computed_crc": computed_crc,
            "crc_match": received_crc == computed_crc,
        }

    def _decode(self, frame):
        """
        [START] [CMD] [PAYLOAD (1 байт)] [CRC]
        """
        cmd = frame[1]


        if cmd == 6:
            return {"status": "end"}

        if cmd in {4, 1, 3}:
            if len(frame) < 5:
                return {"status": "error", "message": "Короткий пакет для CRC"}

            payload, received_crc = frame[2], (frame[3] << 8) | frame[4]
            computed_crc = self.crc16_ccitt(bytes([payload]), cmd)
            if frame[2] == 6:
                self.pause = True
            elif frame[2] == 7:
                self.pause = False

            return {
                "status": "success" if received_crc == computed_crc else "error",
                "cmd": cmd,
                "payload": payload,
                "received_crc": received_crc,
                "computed_crc": computed_crc,
                "crc_match": received_crc == computed_crc,
            }

        return {"status": "error", "message": f"Невідома команда {cmd}"}
