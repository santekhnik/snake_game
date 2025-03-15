import serial
import serial.tools.list_ports
import time
import threading
from frame_codec import STMProtocol


class UARTConnection:
    BAUDRATE = 9600
    TIMEOUT = 1
    CONNECT_TIMEOUT = 2

    def __init__(self):
        self.uart = None
        self.port = None
        self.protocol = STMProtocol()
        self.init_paket = self.get_init_paket()

    def get_init_paket(self):
        return self.protocol.encode_frame(1, 1)

    def _try_open_port(self, port, result):
        try:
            ser = serial.Serial(port.device, self.BAUDRATE, timeout=self.TIMEOUT)
            result["ser"] = ser
        except serial.SerialException:
            result["ser"] = None

    def check_port(self, port):
        result = {}
        thread = threading.Thread(target=self._try_open_port, args=(port, result))
        thread.start()
        thread.join(self.CONNECT_TIMEOUT)
        uart = result.get("ser", None)
        if uart is None:
            return {"status": "error", "message": f"Порт {port.device} не доступний або зайнятий."}
        try:
            uart.write(self.init_paket)
            start_time = time.time()
            while time.time() - start_time < self.CONNECT_TIMEOUT:
                response = uart.read(5)
                if response:
                    decoded_response = self.protocol.decode_frame(response)

                    if "cmd" in decoded_response and decoded_response["cmd"] == 1 and decoded_response["payload"] == 2:
                        self.uart = uart
                        self.port = port.device
                        return {"status": "success", "message": f"Підключено до {port.device}"}
                    else:
                        return {"status": "error", "message": f"Отримана відповідь неправильна: {decoded_response}"}

            uart.close()
            return {"status": "error", "message": f"{port.device} не відповідає."}

        except serial.SerialException as e:
            return {"status": "error", "message": f"Помилка роботи з портом {port.device}: {str(e)}"}

    def auto_connect(self):

        """Перевіряє доступні COM-порти та підключається до STM."""
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            return {"status": "error", "message": "Немає доступних COM-портів."}

        for port in ports:
            result = self.check_port(port)
            if result["status"] == "success":
                return result

        return {"status": "error", "message": "STM не знайдено."}

    def connect_manual(self):
        """Користувач вручну вибирає порт"""
        if self.uart and self.uart.is_open:
            self.uart.close()

        selected_port = self.get_port_for_connecting()
        if selected_port:
            return self.check_port(selected_port)

        return {"status": "error", "message": "Невірний вибір порту."}

    def create_dict_for_available_ports(self):
        """Створює словник доступних портів"""
        ports = serial.tools.list_ports.comports()
        ports_dict = {}

        for port in ports:
            try:
                port_number = int(port.device.replace("COM", ""))
                ports_dict[port_number] = port
            except ValueError:
                pass
        return ports_dict

    def get_port_for_connecting(self):
        """Запитує у користувача вибір порту"""
        available_ports = self.create_dict_for_available_ports()

        print("Доступні COM-порти:")
        for index, device in sorted(available_ports.items()):
            print(f"{index}: {device}")

        try:
            port_number = int(input("Введіть номер порту: "))
            return available_ports.get(port_number, None)
        except ValueError:
            return {"status": "error", "message": "Введіть число!"}

    def read_packet(self):
        """Читає пакет з UART та передає його в STMProtocol"""

        if not self.uart:
            return {"status": "error", "message": "UART не підключено"}

        try:
            header = self.uart.read(2)
            if len(header) < 2:
                if header == b'':
                    return {"status": "warning", "message": "Отримано порожній пакет"}
                return {"status": "error", "message": "Короткий 2х байтовий пакет"}

            start_byte, cmd = header

            if start_byte != 0x7E:
                return {"status": "error", "message": "Невірний стартовий байт"}

            if cmd == 2:
                length_byte = self.uart.read(1)

                if len(length_byte) < 1:
                    return {"status": "error", "message": "Не вдалося прочитати LEN"}
                length = length_byte[0]

                payload_frog_crc = self.uart.read(length + 4)
                if len(payload_frog_crc) < length + 4:
                    return {"status": "error", "message": "Неповний пакет payload_frog_crc"}

                full_packet = header + length_byte + payload_frog_crc

            elif cmd in [1, 3, 4, 5, 6]:
                payload_crc = self.uart.read(3)
                if len(payload_crc) < 3:
                    return {"status": "error", "message": "Неповний пакет"}

                full_packet = header + payload_crc

            else:
                return {"status": "error", "message": f"Невідома команда: {cmd}"}
            decoded = self.protocol.decode_frame(full_packet)
            return {"status": "success", "data": decoded}

        except:
            return {"status": "error", "message": "Помилка UART"}
