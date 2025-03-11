import struct

class STMProtocol:

    START_BYTE = 0x7E
    CRC_POLY = 0x1021
    ENCODE_COMMANDS = [1, 3, 5]
    DECODE_COMMANDS = [2, 4, 6]

    def __init__(self):
        pass

    def encode_hex(self, cmd: int, payload):
        """Кодування пакета в залежності від команди"""
        if cmd not in self.ENCODE_COMMANDS:
            return {"status": "error", "message": "Невідома команда"}
        match cmd:
            case 1 | 3 | 5:
                return self._encode_frame(cmd, payload)


    def decode_hex(self, hex_str):
        """
        Декодує отриманий HEX-пакет, перевіряє CRC та повертає дані.
        """
        frame = bytes.fromhex(hex_str)

        if len(frame) < 5:
            return {"status": "error", "message": "Короткий пакет"}

        if frame[0] != self.START_BYTE:
            return {"status": "error", "message": "Невірний стартовий байт"}

        cmd = frame[1]

        match cmd:
            case 2:
                return self._decode_game_data(frame)
            case 4 | 6:
                return self._decode(frame)


    def crc16_ccitt(self, data: bytes, cmd: int = 0, frog_x: int = 0, frog_y: int = 0, poly=0x1021, init=0xFFFF):
        """Обчислює CRC-16-CCITT для будь-яких даних"""
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


    def _encode_frame(self, cmd: int, payload):
        """
        [START] [CMD] [PAYLOAD] [CRC] -> HEX
        """
        if isinstance(payload, int):
            payload = str(payload).encode()
        elif isinstance(payload, str):
            payload = payload.encode()
        frame = bytearray()
        frame.append(self.START_BYTE)
        frame.append(cmd)
        frame.extend(payload)

        crc = self.crc16_ccitt(payload, cmd)
        frame.append((crc >> 8) & 0xFF)
        frame.append(crc & 0xFF)

        return frame.hex().upper()


    def _decode_game_data(self, frame):
        """[START] [CMD] [LEN] [PAYLOAD] [FROG_X (1 байт)] [FROG_Y (1 байт)] [CRC]"""
        cmd = frame[1]

        payload_len = frame[2]

        expected_len = 3 + payload_len + 2 + 2

        if len(frame) != expected_len:
            return {"status": "error",
                    "message": f"Невідповідність довжини пакета. Очікувано {expected_len}, отримано {len(frame)}"}

        payload_bytes = frame[3:3 + payload_len]

        payload_list_data = list(payload_bytes)

        if len(payload_list_data) % 2 != 0:
            return {"status": "error", "message": "Непарна кількість байтів у payload"}

        payload = []
        for i in range(0, len(payload_list_data), 2):
            pair = (payload_list_data[i], payload_list_data[i + 1])
            payload.append(pair)

        frog_x, frog_y = struct.unpack('<BB', frame[3 + payload_len:3 + payload_len + 2])

        received_crc = (frame[-2] << 8) | frame[-1]
        computed_crc = self.crc16_ccitt(payload_bytes, cmd, frog_x, frog_y)

        return {
            "status": "success" if received_crc == computed_crc else "error",
            "cmd": cmd,
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

        elif cmd == 4:
            if len(frame) < 5:
                return {"status": "error", "message": "Короткий пакет для CRC"}

            payload = frame[2]
            received_crc = (frame[3] << 8) | frame[4]
            payload_bytes = bytes([payload])
            computed_crc = self.crc16_ccitt(payload_bytes, cmd)

            return {
                "status": "success" if received_crc == computed_crc else "error",
                "cmd": cmd,
                "payload": payload,
                "received_crc": received_crc,
                "computed_crc": computed_crc,
                "crc_match": received_crc == computed_crc,
            }
        else:
            return {"status": "error", "message": f"Невідома команда {cmd}"}
