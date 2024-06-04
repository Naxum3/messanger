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


# Пример использования
text = "first"
print("Original text:", text)
#
encoded_string = encode_text(text)
print("Encoded string:", encoded_string)
# 
decoded_text = decode_text(encoded_string)
print("Decoded text:", decoded_text)
