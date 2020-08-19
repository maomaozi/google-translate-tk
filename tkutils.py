import re

import fixedint
import requests


def get_tkk():
    response = requests.get("https://translate.google.cn/", timeout=5)
    return re.findall(r"(?<=tkk:')\d*\.\d*(?=')", response.text)[0]


def calc_r(magic_token, magic_str):
    for i in range(0, len(magic_str) - 2, 3):
        tmp = magic_str[i + 2]
        if tmp >= "a":
            pos = ord(tmp[0]) - 87
        else:
            pos = int(tmp)

        if magic_str[i + 1] == "+":
            pos = magic_token >> pos
        else:
            pos = fixedint.UInt32(magic_token << pos)

        if magic_str[i] == "+":
            magic_token += pos & 4294967295
        else:
            magic_token ^= pos
    return magic_token


def asc_ii(s):
    return [ord(i) for i in s]


def fill(lst, index, value):
    while True:
        if len(lst) > index:
            break
        lst.append(0)
    lst[index] = value
    return lst


def get_tk(s, tkk):
    asc_lst = asc_ii(s)
    encoded_lst = []

    i = 0
    while i < len(asc_lst):
        current = asc_lst[i]
        if 128 > current:
            encoded_lst.append(current)
        elif 2048 > current:
            encoded_lst.append(current >> 6 | 192)
        elif 55296 == (current & 64512) and i + 1 < len(asc_lst) and 56320 == int(asc_lst[i + 1]) & 64512:
            i += 1
            current = 65536 + fixedint.UInt32((current & 1023) << 10) + (asc_lst[i] & 1023)
            encoded_lst.append(current >> 18 | 240)
            encoded_lst.append(current >> 12 & 63 | 128)
        else:
            encoded_lst.append(current >> 12 | 224)
            encoded_lst.append(current >> 6 & 63 | 128)
            encoded_lst.append(current & 63 | 128)
        i += 1

    tkk_p1, tkk_p2 = map(int, tkk.split('.'))

    result = tkk_p1
    for i in range(len(encoded_lst)):
        result += encoded_lst[i]
        result = calc_r(result, "+-a^+6")

    result = calc_r(result, "+-3^+b+-f")
    result ^= tkk_p2
    result %= 1E6

    return "%d.%d" % (result, result ^ tkk_p1)


if __name__ == '__main__':
    tkk = get_tkk()
    print(get_tk("hello", tkk))
