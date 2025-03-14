import serial
import serial.tools.list_ports
import time
import threading
from frame_codec import STMProtocol


class UARTConnection:
    BAUDRATE = 9600
    TIMEOUT = 1
    CONNECT_TIMEOUT = 1

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
