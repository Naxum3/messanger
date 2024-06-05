import socket
import sys
import traceback
from threading import Thread

import pandas as pd


table = pd.read_csv("names.csv")
conns = []
names_online = []


def text_to_bits(text):
    """Преобразует текст в последовательность битов"""
    bits = []
    for char in text:
        bits.extend(
            [int(bit) for bit in bin(ord(char))[2:].zfill(8)])  # Преобразование каждого символа в битовую строку
    return bits


def bits_to_text(bits):
    """Преобразует последовательность битов в текст"""
    text = ""
    for i in range(0, len(bits), 8):
        byte = bits[i:i + 8]  # Извлечение байта из последовательности битов
        text += chr(int("".join(str(bit) for bit in byte), 2))  # Преобразование байта в символ
    return text


def encode(data):
    """Кодирование данных с использованием кода Хэмминга (7,4)"""
    p1 = data[0] ^ data[1] ^ data[3]
    p2 = data[0] ^ data[2] ^ data[3]
    p3 = data[1] ^ data[2] ^ data[3]
    return [p1, p2, data[0], p3, data[1], data[2], data[3]]


def decode(encoded_data):
    """Декодирование данных с использованием кода Хэмминга (7,4)"""
    p1 = encoded_data[0] ^ encoded_data[2] ^ encoded_data[4] ^ encoded_data[6]
    p2 = encoded_data[1] ^ encoded_data[2] ^ encoded_data[5] ^ encoded_data[6]
    p3 = encoded_data[3] ^ encoded_data[4] ^ encoded_data[5] ^ encoded_data[6]

    error_index = p3 * 4 + p2 * 2 + p1 - 1
    if error_index >= 0:
        # Исправляем ошибку
        encoded_data[error_index] ^= 1

    return [encoded_data[2], encoded_data[4], encoded_data[5], encoded_data[6]]


def encode_text(text):
    """Кодирование текста по коду Хэмминга"""
    bits = text_to_bits(text)
    encoded_bits = []
    for i in range(0, len(bits), 4):
        encoded_bits.extend(encode(bits[i:i + 4]))
    encoded_string = ''.join(str(bit) for bit in encoded_bits)
    return encoded_string


def decode_text(encoded_string):
    """Декодирование текста по коду Хэмминга"""
    decoded_bits = [int(bit) for bit in encoded_string]
    decoded_data = []
    for i in range(0, len(decoded_bits), 7):
        decoded_data.extend(decode(decoded_bits[i:i + 7]))
    decoded_text = bits_to_text(decoded_data)
    return decoded_text


def client_thread(conn, ip, port, max_buffer_size=4096):
    input_from_client_bytes = conn.recv(max_buffer_size)  # Метод для получения данных
    user_name = decode_text(
        input_from_client_bytes.decode("utf8").rstrip())  # декодирование битового потока и удаление
    # пробелов справа от строки

    if user_name not in table['name'].values:
        table.loc[-1] = [len(table), user_name]
        table.to_csv("names.csv", index=False)

    names_online.append(user_name)

    print(user_name, "just connected!")

    while conn.fileno() != -1:  # Проверка наличия действительного файлового дескриптора
        input_from_client_bytes = conn.recv(max_buffer_size)

        siz = sys.getsizeof(input_from_client_bytes)  # Размер сообщения в байтах

        if siz > 0:
            if siz >= max_buffer_size:
                print("Over 4096 symbols: {}".format(siz))

            input_from_client = input_from_client_bytes.decode("utf8").rstrip()
            if input_from_client != "":
                input_from_client = decode_text(input_from_client)
                res = encode_text(user_name + ": " + input_from_client)

                if input_from_client[0] == '@':
                    name_to = input_from_client.split(' ')[0]
                    name_to = name_to[1:len(name_to)]
                    if name_to in table['name'].values:
                        if name_to not in names_online:
                            sub_res = encode_text(name_to + " not online.")
                            sysl = sub_res.encode("utf8")
                            conn.sendall(sysl)
                        else:
                            sub_res = encode_text(name_to + " online.")
                            sysl = sub_res.encode("utf8")
                            conn.sendall(sysl)
                    else:
                        sub_res = encode_text(name_to + " not in database.")
                        sysl = sub_res.encode("utf8")
                        conn.sendall(sysl)

                vysl = res.encode("utf8")
                for i in range(len(conns)):
                    if conns[i] != conn:
                        conns[i].sendall(vysl)  # Отправляет все данные целиком

    names_online.remove(user_name)
    conn.close()
    print('Connection ' + ip + ':' + port + " ended")


def start_server():
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cоздание IPv4 сокета с последовательной передачей данных
    soc.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Установка опций для сокета
    # socket.SOL_SOCKET: Это уровень сокета, который определяет общие параметры сокета.
    # socket.SO_REUSEADDR: Этот параметр указывает на возможность повторного использования адреса сокета.
    print('Socket created')

    try:
        soc.bind(("127.0.0.1", 1488))  # Привязывает сокет к адресу
        print('Socket bind complete')
    except socket.error:
        print('Bind failed. Error : ' + str(sys.exc_info()))
        sys.exit()

    soc.listen(10)  # Прослушивание соединений, макс 10 соединений в очереди
    print('Socket now listening')

    while True:
        conn, addr = soc.accept()  # Принятие входящих соединений, возвращ объект сокета и кортеж адреса
        conns.append(conn)
        ip, port = str(addr[0]), str(addr[1])
        print('Accepting connection from ' + ip + ':' + port)
        try:
            Thread(target=client_thread, args=(conn, ip, port)).start()  # Создание потока для клиента
        except:
            print("Terible error!")
            traceback.print_exc()


start_server()
