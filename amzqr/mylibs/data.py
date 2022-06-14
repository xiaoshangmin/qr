# -*- coding: utf-8 -*-

from amzqr.mylibs.constant import char_cap, required_bytes, mindex, lindex, num_list, alphanum_list, grouping_list, mode_indicator

# ecl: Error Correction Level(L,M,Q,H)


def encode(ver, ecl, str):
    mode_encoding = {
        'numeric': numeric_encoding,
        'alphanumeric': alphanumeric_encoding,
        'byte': byte_encoding,
        'kanji': kanji_encoding
    }
    #ver所选纠错级别(ecl)对应的最低版本 mode编码类型
    ver, mode = analyse(ver, ecl, str)

    print('line 16: mode:', mode, ver)

    #模式指示符+字符计数指示符+
    code = mode_indicator[mode] + \
        get_cci(ver, mode, str) + mode_encoding[mode](str)

    # print('line 20: code:', code)

    # Add a Terminator
    rqbits = 8 * required_bytes[ver-1][lindex[ecl]]
    b = rqbits - len(code)
    code += '0000' if b >= 4 else '0' * b

    # Make the Length a Multiple of 8
    while len(code) % 8 != 0:
        code += '0'

    # Add Pad Bytes if the String is Still too Short
    while len(code) < rqbits:
        code += '1110110000010001' if rqbits - len(code) >= 16 else '11101100'

    data_code = [code[i:i+8] for i in range(len(code)) if i % 8 == 0]
    data_code = [int(i, 2) for i in data_code]

    g = grouping_list[ver-1][lindex[ecl]]
    data_codewords, i = [], 0
    for n in range(g[0]):
        data_codewords.append(data_code[i:i+g[1]])
        i += g[1]
    for n in range(g[2]):
        data_codewords.append(data_code[i:i+g[3]])
        i += g[3]

    return ver, data_codewords


def analyse(ver, ecl, str):
    if all(i in num_list for i in str):
        mode = 'numeric'
    elif all(i in alphanum_list for i in str):
        mode = 'alphanumeric'
    else:
        mode = 'byte'

    m = mindex[mode]
    l = len(str.encode('utf-8'))
    for i in range(40):
        if char_cap[ecl][i][m] > l:
            ver = i + 1 if i+1 > ver else ver
            break

    return ver, mode


def numeric_encoding(str):
    str_list = [str[i:i+3] for i in range(0, len(str), 3)]
    code = ''
    for i in str_list:
        rqbin_len = 10
        if len(i) == 1:
            rqbin_len = 4
        elif len(i) == 2:
            rqbin_len = 7
        code_temp = bin(int(i))[2:]
        code += ('0'*(rqbin_len - len(code_temp)) + code_temp)
    return code


def alphanumeric_encoding(str):
    code_list = [alphanum_list.index(i) for i in str]
    code = ''
    for i in range(1, len(code_list), 2):
        c = bin(code_list[i-1] * 45 + code_list[i])[2:]
        c = '0'*(11-len(c)) + c
        code += c
    if i != len(code_list) - 1:
        c = bin(code_list[-1])[2:]
        c = '0'*(6-len(c)) + c
        code += c

    return code


def byte_encoding(str):
    str = bytes(str, encoding="utf8")
    code = ''
    for i in str:
        c = bin(i)[2:]
        c = '0'*(8-len(c)) + c
        code += c
    return code


def kanji_encoding(str):
    pass

# cci: character count indicator

#字符计数指示符
#不同模式对应版本有特定的位长
#计算原始输入文本的字符数，将其转为二进制数字。根据版本和编码模式找到对应的位长，不够位长的在前面加 0 补齐。
def get_cci(ver, mode, str):
    if 1 <= ver <= 9:
        cci_len = (10, 9, 8, 8)[mindex[mode]]
    elif 10 <= ver <= 26:
        cci_len = (12, 11, 16, 10)[mindex[mode]]
    else:
        cci_len = (14, 13, 16, 12)[mindex[mode]]

    cci = bin(len(bytes(str, encoding="utf8")))[2:]
    cci = '0' * (cci_len - len(cci)) + cci
    return cci


if __name__ == '__main__':
    s = '123456789'
    v, datacode = encode(1, 'H', s)
    print(v, datacode)
