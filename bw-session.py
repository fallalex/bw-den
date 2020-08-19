#!/usr/bin/env python3

# bw unlock --raw
# pip3 install python-gnupg

import gnupg
from pathlib import Path
from getpass import getpass
from subprocess import Popen, PIPE
import json
from sys import exit

#TODO:
#  - check for fingerprint in secrets ring
#  - cli: config (dirs/files and fingerprint), default with no args returns session, new, status

class bwSession:
    def __init__(self):
        self.fingerprint = 'C9CB0C945B583DD3E65DDC376B5C20C74C63902A'
        self.gpg_home = Path.home() / '.gnupg'
        self.encrypted_session = Path.home() / '.bw-session.asc'
        self.gpg = gnupg.GPG(gnupghome=str(self.gpg_home), use_agent=True)
        keys_pub = self.gpg.list_keys().key_map
        key = keys_pub.get(self.fingerprint)
        if not key:
            exit("Could not find fingerprint: '{}'".format(self.fingerprint))

        self.decrypt_session()
        if not self.session:
            self.new_session()
            if not self.session_unlocked():
                exit("Session fails to unlock")

    def call(self, args):
        bw_proc = Popen(args, shell=False, stdout=PIPE, stderr=PIPE)
        stdout, stderr = [s.decode('utf-8') for s in bw_proc.communicate()]
        return (bw_proc.returncode, stdout, stderr)

    def new_session(self):
        rc = 1
        while (rc != 0):
            passphrase = getpass()
            rc, out, err = self.call(['bw', 'unlock', passphrase, '--raw'])
        self.session = out
        self.encrypt_session()

    def decrypt_session(self):
        self.session = ''
        if not self.encrypted_session.is_file():
            print("No session file at: '{}'".format(self.encrypted_session))
            return
        with open(self.encrypted_session, 'rb') as f:
            session = self.gpg.decrypt_file(f)
        if not session:
            exit("failed to decrypt session try this command\n  gpg --decrypt '{}'".format(self.encrypt_session))
        self.session = session

    def encrypt_session(self):
        self.gpg.encrypt(self.session, self.fingerprint, output=self.encrypted_session)

    def session_unlocked(self):
        rc, out, err = self.call(['bw', 'status', '--raw', '--session', self.session])
        if rc != 0:
            exit("'status' command failed. returncode: '{}' | stdout: '{}' | stderr: '{}'".format(rc, out, err))
        lines = [l for l in out.splitlines() if l.strip()]
        json_lines = []
        for line in lines:
            try: json_lines.append(json.loads(line))
            except: pass
        assert(len(json_lines) == 1)
        assert('status' in json_lines[0])
        status = json_lines[0]['status'].lower()
        assert(status in ('locked', 'unlocked'))
        if status == 'unlocked':
            return True
        return False


bw_session = bwSession()
print(bw_session.session)
