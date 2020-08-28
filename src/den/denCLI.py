import json
import pyperclip
import argparse
from .bwHelper import *

class denCLI:
    def __init__(self, argv):
        self.argv = argv
        self.bwhelp = bwHelper()
        self.parser = argparse.ArgumentParser(description='Simplified interface for copying Passwords and TOTPs from Bitwarden')
        group = self.parser.add_mutually_exclusive_group()
        self.parser.add_argument('item',
                            nargs='?',
                            type=str,
                            help='item name/id',
                            metavar='I')
        self.parser.add_argument('-f',
                            '--folder',
                            type=str,
                            help='folder name',
                            metavar='F')
        self.parser.add_argument('-o',
                            '--organization',
                            type=str,
                            help='organization name',
                            metavar='O')
        self.parser.add_argument('-c',
                            '--collection',
                            type=str,
                            help='collection name',
                            metavar='C')
        self.parser.add_argument('-n',
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
        self.parser.add_argument('-y',
                            '--yml-conf',
                            type=str,
                            help='path to yml conf file, default is {}'.format('test'))
        self.arg_parse()
        self.actions()

    def arg_parse(self):
        if not len(self.argv) > 1:
            self.parser.error("No arguments were passed")

        # get args and values as dict
        self.args = vars(self.parser.parse_args(self.argv[1:]))

        if (self.args['folder'] or self.args['collection'] or self.args['organization']) and self.args['item'] is None:
            self.parser.error("need to pass 'I' if using '-f', '-c', and/or '-o'")

    def copy_or_print(self, output, desc=None, noclip=None):
        if noclip is None:
            noclip = self.args['no_clip']
        if noclip:
            if desc:
                print("{}: ".format(desc), end='')
            print(output)
        else:
            pyperclip.copy(output)
            print("Copied", end='')
            if desc:
                print(" {}".format(desc))
            else:
                print()

    def actions(self):
        if self.args['yml_conf']:
            pass

        if self.args['refresh']:
            self.bwhelp.refresh()
            if self.args['no_clip']:
                print(self.bwhelp.bwsess.session_token)
            else:
                pyperclip.copy(self.bwhelp.bwsess.session_token)
            return

        # Ensure there is a session before doing anything else
        self.bwhelp.bwsess.decrypt_session()
        if not self.bwhelp.bwsess.session_token:
            sys.exit("Create a session before preceeding.")

        self.bwhelp.decrypt_cache()

        if self.args['completion']:
            print(self.bwhelp.completion(self.args['completion']))
            return

        if self.args['session']:
            self.bwhelp.bwsess.decrypt_session()
            if self.args['no_clip']:
                print(self.bwhelp.bwsess.session_token)
            else:
                pyperclip.copy(self.bwhelp.bwsess.session_token)
            return

        if self.args['all_fields'] or self.args['password'] or self.args['totp']:
            if self.args['item'] is None:
                self.parser.error("need to pass 'S'")

            item_id = self.bwhelp.item_id(self.args['item'])
            if self.args['all_fields']:
                self.copy_or_print(self.bwhelp.get_item(item_id),True)
            elif self.args['password']:
                self.copy_or_print(self.bwhelp.get_pass(item_id))
            elif self.args['totp']:
                self.copy_or_print(self.bwhelp.get_totp(item_id))
            return

        if self.args['item']:
            item_id = self.bwhelp.item_id(self.args['item'])
            self.copy_or_print(self.bwhelp.get_pass(item_id),'Password')
            # TODO: check that totp exists will need to refactor cache structure
            # TODO: timeout on input
            if not self.args['no_clip']:
                input("Enter for TOTP...")
            self.copy_or_print(self.bwhelp.get_totp(item_id),'TOTP')


