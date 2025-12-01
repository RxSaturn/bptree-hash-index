#!/usr/bin/python3 -u
# -*- coding: utf-8 -*-
'''
SIOgen: Simple Insert Delete Dataset Generator

Gerador de dados sintéticos para testes de estruturas de índice. 
Fonte original: https://github. com/ribeiromarcos/siogen

Uso:
    python siogen.py -a 10 -i 5000 -s 3000 -d 500 -f output.csv
'''

import argparse
import csv
import os
import sys
from random import randint, shuffle, seed

# Parameters
ATT = 'att'
INSERT = 'insert'
DELETE = 'delete'
SEARCH = 'search'
FILE = 'file'

# Default parameter values
DEFAULT_ATT = 10
DEFAULT_INSERT = 2000
DEFAULT_DELETE = 500
DEFAULT_SEARCH = 3000
DEFAULT_SEED = 42
DEFAULT_FILE = 'output.csv'


def gen_insertions(rec_list, keys_list, key_set, par_dict):
    '''Generate insertions'''
    if len(keys_list) == 0:
        return
    
    ins_num = randint(1, len(keys_list))
    par_dict[INSERT] -= ins_num
    ins_list = keys_list[:ins_num]
    del keys_list[:ins_num]
    key_set.update(ins_list)
    
    for key in ins_list:
        new_record = {'OP': '+'}
        att_list = ['A' + str(number + 1) for number in range(par_dict[ATT])]
        for att in att_list:
            new_record[att] = randint(0, 1000)
        new_record['A1'] = key
        rec_list.append(new_record)


def gen_deletions(rec_list, keys_set, par_dict):
    '''Generate deletions'''
    if par_dict[DELETE] == 0:
        return
    
    del_num = randint(1, par_dict[DELETE])
    if del_num > len(keys_set):
        return
    
    key_list = list(keys_set)
    shuffle(key_list)
    del_list = key_list[:del_num]
    par_dict[DELETE] -= del_num
    
    for key in del_list:
        new_record = {'OP': '-'}
        att_list = ['A' + str(number + 1) for number in range(par_dict[ATT])]
        for att in att_list:
            new_record[att] = key
        rec_list.append(new_record)
        keys_set.remove(key)


def gen_searches(rec_list, keys_set, par_dict):
    '''Generate searches'''
    if par_dict[SEARCH] == 0:
        return
    
    searches_num = randint(1, par_dict[SEARCH])
    par_dict[SEARCH] -= searches_num
    
    for _ in range(searches_num):
        new_record = {'OP': '?'}
        key = randint(1, 2 * len(keys_set)) if keys_set else randint(1, 100)
        att_list = ['A' + str(number + 1) for number in range(par_dict[ATT])]
        for att in att_list:
            new_record[att] = key
        rec_list.append(new_record)


def store_records(rec_list, par_dict):
    '''Store a record list into file'''
    if len(rec_list) == 0:
        return
    
    att_list = ['OP'] + ['A' + str(number + 1) for number in range(par_dict[ATT])]
    
    # Ensure output directory exists
    output_dir = os.path.dirname(par_dict[FILE])
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(par_dict[FILE], 'w', encoding='utf-8', newline='') as out_file:
        out_write = csv.DictWriter(out_file, att_list)
        out_write.writeheader()
        out_write.writerows(rec_list)


def gen_keys(par_dict):
    '''Generate keys'''
    key_list = list(range(par_dict[INSERT]))
    shuffle(key_list)
    return key_list


def gen_data(par_dict):
    '''Generate data'''
    if par_dict[DELETE] > par_dict[INSERT]:
        raise ValueError('Number of deletions must be less than insertions')
    
    key_list = gen_keys(par_dict)
    keys_set = set()
    rec_list = []
    
    while par_dict[INSERT] + par_dict[DELETE] + par_dict[SEARCH] > 0:
        gen_insertions(rec_list, key_list, keys_set, par_dict)
        gen_searches(rec_list, keys_set, par_dict)
        gen_deletions(rec_list, keys_set, par_dict)
    
    store_records(rec_list, par_dict)


def get_arguments(print_help=False):
    '''Get arguments'''
    parser = argparse.ArgumentParser('SIOGen')
    parser.add_argument('-a', '--attributes', action='store', type=int,
                        default=DEFAULT_ATT,
                        help=f'Number of attributes (default: {DEFAULT_ATT})')
    parser.add_argument('-i', '--insertions', action='store', type=int,
                        default=DEFAULT_INSERT,
                        help=f'Number of insertions (default: {DEFAULT_INSERT})')
    parser.add_argument('-d', '--deletions', action='store', type=int,
                        default=DEFAULT_DELETE,
                        help=f'Number of deletions (default: {DEFAULT_DELETE})')
    parser.add_argument('-s', '--searches', action='store', type=int,
                        default=DEFAULT_SEARCH,
                        help=f'Number of searches (default: {DEFAULT_SEARCH})')
    parser.add_argument('-f', '--filename', action='store', type=str,
                        default=DEFAULT_FILE,
                        help=f'Output filename (default: {DEFAULT_FILE})')
    parser.add_argument('-e', '--seed', action='store', type=int,
                        default=DEFAULT_SEED,
                        help=f'Seed (default: {DEFAULT_SEED})')
    args = parser.parse_args()
    if print_help:
        parser.print_help()
    return args


def main():
    '''Main routine'''
    args = get_arguments()
    
    # Parameter validation
    if args.attributes < 1:
        print("[ERROR] Number of attributes must be >= 1", file=sys.stderr)
        sys.exit(1)
    if args.insertions < 0:
        print("[ERROR] Number of insertions must be >= 0", file=sys.stderr)
        sys.exit(1)
    if args.deletions < 0:
        print("[ERROR] Number of deletions must be >= 0", file=sys.stderr)
        sys.exit(1)
    if args.searches < 0:
        print("[ERROR] Number of searches must be >= 0", file=sys.stderr)
        sys.exit(1)
    if args.deletions > args.insertions:
        print("[ERROR] Number of deletions cannot be greater than insertions", file=sys.stderr)
        sys.exit(1)
    
    seed(args.seed)
    
    par_dict = {
        ATT: args.attributes,
        INSERT: args.insertions,
        DELETE: args.deletions,
        SEARCH: args.searches,
        FILE: args.filename
    }
    
    try:
        gen_data(par_dict)
        print(f"[OK] Data generated at: {args.filename}")
    except Exception as e:
        print(f"[ERROR] Error generating data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()