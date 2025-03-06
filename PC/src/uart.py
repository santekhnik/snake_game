import serial
import serial.tools.list_ports
import time

def create_dict_for_available_ports():

    ports = serial.tools.list_ports.comports()

    ports_dict = {}

    for port in ports:
        try:
            port_number = int(port.device.replace("COM", ""))
            ports_dict[port_number] = port.device
        except ValueError:
            pass
    return ports_dict


def get_port_for_connecting():

    available_ports = create_dict_for_available_ports()

    print("Доступні COM-порти:")
    for index, device in sorted(available_ports.items()):
        print(f"{index}: {device}")
    try:
        port = available_ports[int(input("👉 Введіть номер порту: "))]
        return port
    except:
        print("Помилка відкриття порту")
        pass




def connecting_stm( message="Hello \n"):

    port = get_port_for_connecting()

    UART_PORT = port
    BAUDRATE = 9600
    TIMEOUT = 1

    try:
        ser = serial.Serial(UART_PORT, BAUDRATE, timeout=TIMEOUT)
        print(f"Підключено до {UART_PORT} на {BAUDRATE} бод")

        if ser.is_open:
            try:
                message = message.encode()
                print(f"Відправка: {message}")

                ser.write(message)

                start_time = time.time()

                while True:
                    response = ser.readline()
                    if response:
                        print(f"Отримано: {response.decode(errors='ignore').strip()}", ser.is_open)
                        break

                    if time.time() - start_time > 2:
                        print(f"Порт {UART_PORT} не відповідає після 2 секунд очікування.")
                        ser.close()
                        break
            except:
                print(f"Порт {UART_PORT} не відповідає")
                ser.close()
                pass

    except :
        print(f"Порт {UART_PORT} не доступний")
        pass

connecting_stm()
