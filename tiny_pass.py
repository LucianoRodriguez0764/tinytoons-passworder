import random

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
    'L': 0x0, 'W': 0xF, 'A': 0xFF, 'A': 0xFF,
    'E': 0xFF, 'I': 0xFF, 'O': 0xFF, 'U': 0xF,
    'F': 0xFF, 'C': 0xFF,
}
'''
checksum_values = {
    0x0: 3, 0x1: 6, 0x2: 15, 0x3: 10,
    0x4: 21, 0x5: 24, 0x6: 12, 0x7: 1,
    0x8: 17, 0x9: 7, 0xA: 13, 0xB: 25,
    0xC: 9, 0xD: 23, 0xE: 19, 0xF: 16
}
'''
random_choice_for_0_and_f = True

def sumar_letras(s):
    # A=0, ..., Z=25
    s = s.upper()
    total = 0
    for c in s:
        if 'A' <= c <= 'Z':
            total += ord(c) - ord('A')
    return total

def nibble_to_letter(nibble, rnd=True):
    if nibble == 0x0 and rnd:
        letter = random.choice(['L', 'D'])
    elif nibble == 0xF and rnd:
        letter = random.choice(['Q', 'W'])
    else:
        letter = hex_a_letra[nibble]
    return letter

def convert_byte_to_letter(hex_value):
    global random_choice_for_0_and_f
    hex_value = hex_value & 0xFF  #no hace falta, ya recorre solo dos bytes
    nibble_low  =  hex_value       & 0xF    # nibble bajo
    nibble_high = (hex_value >> 4) & 0xF    # nibble alto
    return nibble_to_letter(nibble_low, random_choice_for_0_and_f)+nibble_to_letter(nibble_high, random_choice_for_0_and_f)

def convert_pair_to_byte(string):
    return letra_a_hex[string[1]] + letra_a_hex[string[0]]

# not used
def get_checksum_header(payload):
    checksum_head = 0
    bytes_length = (payload.bit_length() + 7) // 8
    for i in reversed(range(bytes_length)):
        checksum_head += sumar_letras(convert_byte_to_letter(payload >> (i * 8)))
    return checksum_head

# not used
def get_checksum_header_by_body_letters(string):
    dec = sumar_letras(string)
    return convert_byte_to_letter(dec)

def get_checksum_footer_by_body_letters(string):
    pair = ''
    payload = 0
    for i in range(len(string)):
        pair+=string[i]
        if i%2 == 1:
            payload += convert_pair_to_byte(pair)
            pair = ''
    return convert_byte_to_letter(payload)

def convert_payload_to_password(hex_value):
    cuerpo = []
    checksum_pie = 0x00
    checksum_head = 0
    bytes_length = (hex_value.bit_length() + 7) // 8
    for i in reversed(range(bytes_length)):
        byte = hex_value >> (i * 8) # itero de a 1 byte/2nibbles/8 bits
        checksum_pie += byte
        pair_letter = convert_byte_to_letter(byte)
        checksum_head += sumar_letras(pair_letter)
        cuerpo.append(pair_letter)
    return convert_byte_to_letter(checksum_head), cuerpo, convert_byte_to_letter(checksum_pie)

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

def random_payload_generator():
    payload = 0x00
    for i in range(0,7):
        rnd = random.randint(0,255)
        payload += rnd
        payload = payload << 8
    
    return payload

#print(format_password(convert_payload_to_password(0xffffff3f0c053f06)))
#print(get_checksum_header_by_body_letters("QQQQQQQKJDYLUKMD"))
#print(get_checksum_footer_by_body_letters("QQQQQQQKJDYLUKMD"))
rnd_payload = random_payload_generator()
print(hex(rnd_payload))
print(format_password(convert_payload_to_password(rnd_payload)))