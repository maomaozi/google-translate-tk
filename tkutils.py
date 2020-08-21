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


def get_tk(s, tkk):
    utf8_lst = [i for i in s.encode('utf-8')]
    tkk_p1, tkk_p2 = map(int, tkk.split('.'))

    result = tkk_p1
    for item in utf8_lst:
        result += item
        result = calc_r(result, "+-a^+6")

    result = (calc_r(result, "+-3^+b+-f") ^ tkk_p2) % 1E6

    return "%d.%d" % (result, result ^ tkk_p1)


if __name__ == '__main__':
    # tkk = get_tkk()
    # print(get_tk("hello", tkk))
    print(get_tk('Л', "443872.1304485424"))
    # print(ru(1315921168, "+-3^+b+-f"))
    # print(calc_r(1315921168, "+-3^+b+-f"))
    # ru(1315921168, "+-3^+b+-f")
    # ru(444080, "+-3^+b+-f")
