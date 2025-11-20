import random, re

hex_a_letra = {
    0x0: 'D', 0x1: 'G', 0x2: 'P', 0x3: 'K',
    0x4: 'V', 0x5: 'Y', 0x6: 'M', 0x7: 'B',
    0x8: 'R', 0x9: 'H', 0xA: 'N', 0xB: 'Z',
    0xC: 'J', 0xD: 'X', 0xE: 'T', 0xF: 'Q'
}
letra_a_hex = {
    'D': 0x0, 'G': 0x1, 'P': 0x2, 'K': 0x3,
    'V': 0x4, 'Y': 0x5, 'M': 0x6, 'B': 0x7,
    'R': 0x8, 'H': 0x9, 'N': 0xA, 'Z': 0xB,
    'J': 0xC, 'X': 0xD, 'T': 0xE, 'Q': 0xF, 
    'L': 0x0, 'W': 0xF,
    # invalid letters (Valor FF)
    'A': 0xFF, 'C': 0xFF,
    'E': 0xFF, 'F': 0xFF, 'I': 0xFF, 'O': 0xFF,
    'S': 0xFF, 'U': 0xFF,
}

ff_letters = ['Q', 'W','A','C','E','F','I','O','S','U']

'''
checksum_values = {
    0x0: 3, 0x1: 6, 0x2: 15, 0x3: 10,
    0x4: 21, 0x5: 24, 0x6: 12, 0x7: 1,
    0x8: 17, 0x9: 7, 0xA: 13, 0xB: 25,
    0xC: 9, 0xD: 23, 0xE: 19, 0xF: 16
}
'''
random_choice_for_0_and_f = True
include_invalid_letters = False

def sumar_letras(s):
    # A=0, ..., Z=25
    s = s.upper()
    total = 0
    for c in s:
        if 'A' <= c <= 'Z':
            total += ord(c) - ord('A')
    return total

def nibble_to_letter(nibble, rnd=True,include_invalid_letters=False):
    if nibble == 0x0 and rnd:
        return random.choice(['L', 'D'])
    elif nibble == 0xF and rnd:
        if include_invalid_letters:
            return random.choice(ff_letters)
        else:
            return random.choice(['Q', 'W'])
    else:
        return hex_a_letra[nibble]

def convert_byte_to_letter(hex_value):
    global random_choice_for_0_and_f, include_invalid_letters

    hex_value = hex_value & 0xFF
    nibble_low  =  hex_value       & 0xF # nibble bajo
    nibble_high = (hex_value >> 4) & 0xF # nibble alto

    if hex_value == 0xFF and include_invalid_letters:
        return random.choice(ff_letters)+random.choice(ff_letters)

    # NO GENERA PASSWORDS CON ACEFIOSU cuando el byte es FF ni F_
    return nibble_to_letter(nibble_low, random_choice_for_0_and_f) + \
           nibble_to_letter(nibble_high, random_choice_for_0_and_f,include_invalid_letters=include_invalid_letters)

def convert_pair_to_byte(string):
    return letra_a_hex[string[0]] | ((letra_a_hex[string[1]] << 4) & 0xFF) # EL <<4 es el que genera que las letras glitch funcionen, pasan de ff a 0f.

def get_checksum_header(payload):
    checksum_head = 0
    bytes_length = (payload.bit_length() + 7) // 8
    for i in reversed(range(bytes_length)):
        checksum_head += sumar_letras(convert_byte_to_letter(payload >> (i * 8)))
    return checksum_head

def get_checksum_header_by_body_letters(string, return_byte=False):
    dec = sumar_letras(string) & 0xFF
    if return_byte:
        return dec
    else:
        return convert_byte_to_letter(dec)

def get_checksum_footer_by_body_letters(string, return_byte=False):
    pair = ''
    payload_sum = 0
    for i in range(len(string)):
        pair+=string[i]
        if i%2 == 1:
            payload_sum += convert_pair_to_byte(pair)
            pair = ''
    payload_sum = payload_sum & 0xFF
    if return_byte:
        return payload_sum
    else:
        return convert_byte_to_letter(payload_sum)

def convert_payload_to_password(hex_value):
    cuerpo = []
    checksum_pie = 0x00
    checksum_head = 0
    for i in reversed(range(8)):
        byte = hex_value >> (i * 8) & 0xFF # itero de a 1 byte/2nibbles/8 bits
        checksum_pie += byte
        pair_letter = convert_byte_to_letter(byte)
        cuerpo.append(pair_letter)
    cuerpo_str = "".join(cuerpo)
    header_pair = get_checksum_header_by_body_letters(cuerpo_str)
    footer_pair = convert_byte_to_letter(checksum_pie & 0xFF)
    return header_pair, cuerpo, footer_pair

def format_password(password):
    body = ''
    i=0
    for s in password[1]:
        body+=s
        if i%2==0:
            i=0
            body+=' '
        i+=1
    return password[0]+body+password[2]

def format_payload(string_payload):
    return string_payload[2:6]+' '+string_payload[6:10]+' '+string_payload[10:14]+' '+string_payload[14:18]

def random_payload_generator():
    payload = 0x0000000000000000
    for _ in range(8):
        rnd = random.randint(0,255)
        rnd = 0xff
        payload = (payload << 8) | rnd
    return payload

# TO-DO
def random_valid_payload_generator():
    pass

def verify_password(password, debug=False):
    password = password.upper().replace(" ", "")

    if len(password) != 20:
        if debug:
            print("Password is not 20 chars length.")
        return False

    if not re.match("^[A-Z]+$", password):
        if debug:
            print("Password contains invalid characters (A-Z only).")
        return False

    header = password[:2]
    body = password[2:18]
    footer = password[18:]
    real_checksum_header = get_checksum_header_by_body_letters(body,True)
    real_checksum_footer = get_checksum_footer_by_body_letters(body,True)
    pass_checksum_header = convert_pair_to_byte(header)
    pass_checksum_footer = convert_pair_to_byte(footer)

    if debug and not (real_checksum_header == pass_checksum_header and real_checksum_footer == pass_checksum_footer):
        print("Header should be: "+convert_byte_to_letter(real_checksum_header)+" ("+str(real_checksum_header)+")")
        print("Footer should be: "+convert_byte_to_letter(real_checksum_footer)+" ("+str(real_checksum_footer)+")")

    return real_checksum_header == pass_checksum_header and real_checksum_footer == pass_checksum_footer

if __name__ == "__main__":
    # 1. Generar Payload Random
    rnd_payload = random_payload_generator()
    #rnd_payload = 0x0300000001000000
    print(f"Payload Random Hex: {rnd_payload:016X}")

    # 2. Convertir a Password
    pass_tuple = convert_payload_to_password(rnd_payload)
    pass_str = format_password(pass_tuple)
    print(f"Password Generada:  {pass_str}")

    # 3. Validar
    password_to_verify = "RDQQ QQQW QKQW QWQW QGRY"
    print(password_to_verify,"is a valid password.") if verify_password(password_to_verify) else print(password_to_verify,"is NOT a valid password.")

    # 4. Prueba de Glitch (Tu password S)
    glitch_pass = "DPSS SSSS SSSS SSSS SSRQ"
    glitch_pass = "DPAC EFIO SUAC EFIO SURQ"
    glitch_pass = "YREF AOSC FEFI OOQI AQRW"
    glitch_pass = "NVQQ DDDD DDDD DDDD DDSS"
    glitch_pass = "LUKW WWWW WKJL YMJL BLVZ"
    print(glitch_pass,"is a valid password.") if verify_password(glitch_pass,True) else print(glitch_pass,"is NOT a valid password.")