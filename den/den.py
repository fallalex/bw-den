#!/usr/bin/env python3

import gnupg
from pathlib import Path
from getpass import getpass
from subprocess import Popen, PIPE
import json
import argparse
import sys
import pyperclip
import pickle
import yaml
import pyotp
import os
import time
import tempfile


def cli_parse():
    parser = argparse.ArgumentParser(description='Simplified interface for copying Passwords and TOTPs from Bitwarden')
    group = parser.add_mutually_exclusive_group()
    parser.add_argument('item',
                        nargs='?',
                        type=str,
                        help='item name/id',
                        metavar='I')
    parser.add_argument('-f',
                        '--folder',
                        type=str,
                        help='folder name',
                        metavar='F')
    parser.add_argument('-o',
                        '--organization',
                        type=str,
                        help='organization name',
                        metavar='O')
    parser.add_argument('-c',
                        '--collection',
                        type=str,
                        help='collection name',
                        metavar='C')
    parser.add_argument('-n',
                        '--no-clip',
                        action='store_true',
                        help='do not use clipboard')
    group.add_argument ('-a',
                        '--all-fields',
                        action='store_true',
                        help='return all fields of [I]')
    group.add_argument ('-p',
                        '--password',
                        action='store_true',
                        help='return password of [I]')
    group.add_argument ('-t',
                        '--totp',
                        action='store_true',
                        help='return totp of [I]')
    group.add_argument ('-s',
                        '--session',
                        action='store_true',
                        help='return session token')
    group.add_argument ('-r',
                        '--refresh',
                        action='store_true',
                        help='lock then unlock bitwarden, sync bitwarden, update cache')
    group.add_argument ('-z',
                        '--completion',
                        type=str,
                        help="list cached 'item', 'folder', 'collection', or 'organization' names for shell completion",
                        metavar='Z')
    parser.add_argument('-y',
                        '--yml-conf',
                        type=str,
                        help='path to yml conf file, default is {}'.format('test'))

    # parser.print_help(sys.stderr)

    if not len(sys.argv) > 1:
        parser.error("No arguments were passed")

    # get args and values as dict
    args = vars(parser.parse_args())

    if (args['folder'] or args['collection'] or args['organization']) and args['item'] is None:
        parser.error("need to pass 'I' if using '-f', '-c', and/or '-o'")

    bwhelp = bwHelper()

    if args['yml_conf']:
        pass

    if args['refresh']:
        bwhelp.refresh()
        if args['no_clip']:
            print(bwhelp.bwsess.session_token)
        else:
            pyperclip.copy(bwhelp.bwsess.session_token)
        return

    # Ensure there is a session before doing anything else
    bwhelp.bwsess.decrypt_session()
    if not bwhelp.bwsess.session_token:
        sys.exit("Create a session before preceeding.")

    bwhelp.decrypt_cache()

    if args['completion']:
        print(bwhelp.completion(args['completion']))
        return

    if args['session']:
        bwhelp.bwsess.decrypt_session()
        if args['no_clip']:
            print(bwhelp.bwsess.session_token)
        else:
            pyperclip.copy(bwhelp.bwsess.session_token)
        return

    if args['all_fields'] or args['password'] or args['totp']:
        if args['item'] is None:
            parser.error("need to pass 'S'")

    if args['all_fields']:
        for i in bwhelp.cache_dict['items']:
            if args['item'] == i['name']:
                out = bwhelp.bwcli.get(i['id'])
                print(out)

    if args['password']:
        for i in bwhelp.cache_dict['items']:
            if args['item'] == i['name']:
                if i['password']:
                    out = bwhelp.bwcli.get(i['id'])
                    print(json.loads(out)['login']['password'])


    return args


cli_parse()

