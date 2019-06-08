#! /usr/bin/env python

#PSEUDOCODE for LZW was taken from here: https://www.geeksforgeeks.org/lzw-lempel-ziv-welch-compression-technique/

import argparse
import math

AB = [str(num) for num in range(0, 10)]
DICTIONARY = {}
FREQ = {}

def encode_input(args):
    # initialize dictionary
    index = 1
    for char in AB:
        DICTIONARY[index] = char
        index += 1

    # create\open output files
    text_output = args.output_txt
    bin_output = args.output_bin
    dict_output = args.dict

    with open(text_output, 'w') as txtfile:
        with open(bin_output, 'wb') as binfile:

            # read input file
            with open(args.input_txt, 'r') as infile:
                p = infile.read(1) # read first char in input
                while True:
                    c = infile.read(1)
                    if not c:
                        break
                    string_to_check = "{}{}".format(p,c)    # merge chars
                    if (string_to_check in DICTIONARY.values()):
                        p = string_to_check # p=p+c
                    else:
                        write_code_for_p(p, txtfile, binfile)
                        DICTIONARY[index] = string_to_check
                        index += 1
                        p = c
                write_code_for_p(p, txtfile, binfile)
    # write dictionary to file
    with open(dict_output, 'w') as dictfile:
        dictfile.write(str(DICTIONARY))


def write_code_for_p(p, txtfile, binfile):
    for index, char in DICTIONARY.items():
        if char == p:
            # write to txt
            # https://stackoverflow.com/questions/10411085/converting-integer-to-binary-in-python
            code_to_write = '{0:016b}'.format(index)
            txtfile.write(code_to_write)
            print("write to txt: " + code_to_write)

            # write to bin
            # https://stackoverflow.com/questions/27238680/writing-integers-in-binary-to-file-in-python
            code_to_write = (index).to_bytes(2, byteorder='big', signed=False)
            binfile.write(code_to_write)
            print("write to bin: " + str(code_to_write))

def decode_input(args):
    # log(10) + 2 = 6 bits representation
    initialize_frequancies()
    lower = 0
    upper = 63
    end_of_stream = False

    with open(args.input_bin, "rb") as inp, open(args.output_txt, "w") as out:
        # initialize variables
        next_byte = inp.read(1)  # read 8 bits
        bits_buffer = int.from_bytes(next_byte, byteorder='big')
        bits_left = 8
        tag = 0b000000
        tag, next_byte, bits_buffer, bits_left = get_next_bits(next_byte, bits_buffer, bits_left, tag, 6, inp)

        # decode until EOF
        while (not end_of_stream):
            x = decode(upper, lower, tag)
            symbol = get_symbol(x)
            out.write(str(symbol))
            print(str(symbol))
            lower, upper, num_bits_to_add = update_params(symbol, lower, upper)
            tag, next_byte, bits_buffer, bits_left = get_next_bits(next_byte, bits_buffer, bits_left, tag, num_bits_to_add, inp)
            if ( not next_byte):
                end_of_stream = True



def initialize_frequancies():
    for symbol in AB:
        FREQ[int(symbol)] = 1

def get_next_bits(next_byte, bits_buffer, bits_left, tag, bits_to_read, inp):
    mask = 0b10000000

    # add bits_to_read bits into tag from streaming
    for i in range(0, bits_to_read):
        next_bit = 1 if (bits_buffer & mask > 0) else 0
        tag = tag << 1
        tag += next_bit
        bits_left -= 1
        bits_buffer = bits_buffer << 1
        if (bits_left == 0):
            next_byte = inp.read(1)
            bits_buffer = int.from_bytes(next_byte, byteorder='big')
            bits_left = 8
    return tag, next_byte, bits_buffer, bits_left

def get_Total_Count():
    sum = 0
    for symbol in FREQ:
        sum += FREQ[symbol]
    return sum

def get_Cum_Count(k):
    sum = 0
    for symbol in range(0, k+1):
        sum += FREQ[symbol]
    return sum

def decode(upper, lower, tag):
    total = get_Total_Count()
    return math.floor(((tag-lower+1)*total-1)/(upper-lower+1))

def get_symbol(x):
    k = 0
    if (x < get_Cum_Count(k)):
        return 0
    while (x >= get_Cum_Count(k)):
        k += 1
    return k

def update_params(symbol, lower, upper):
    mask = 0b100000
    new_lower = lower + math.floor(((upper - lower + 1)*get_Cum_Count(symbol - 1))/get_Total_Count())
    new_upper = lower + math.floor(((upper - lower + 1)*get_Cum_Count(symbol))/get_Total_Count()) - 1
    FREQ[symbol] += 1

    # get how many bits identical from msb to lsb
    num_bits = 0
    while(mask & new_upper == mask & new_lower):
        num_bits += 1
        new_lower = new_lower << 1          # shift left + add 0 to lsb
        new_upper = (new_upper << 1) + 1    # shift left + add 1 to lsb
        if (num_bits == 6):  # maximum bits due to log(10) + 2 bits
            break
    return new_lower, new_upper, num_bits



def parse_argumnets():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_txt', type=str, default='input.txt',
                        help='path of input text file')
    parser.add_argument('--input_bin', type=str, default='compressed.bin',
                        help='path of input bin file')
    parser.add_argument('--output_txt', type=str, default='compressed.txt',
                        help='path of output text file')
    parser.add_argument('--output_bin', type=str, default='compressed.bin',
                        help='path of output bin file')
    parser.add_argument('--dict', type=str, default='dict.txt',
                        help='name of the outputs file for final dictionary')
    parser.add_argument('--mode', choices=['encode', 'decode'], default='encode',
                        help='name of the outputs file (txt & bin)')

    args = parser.parse_args()
    return args

if __name__ == "__main__":

    args = parse_argumnets()

    if (args.mode == 'encode'):
        encode_input(args)
    elif (args.mode == 'decode'):
        decode_input(args)
