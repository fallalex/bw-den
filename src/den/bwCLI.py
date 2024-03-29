from subprocess import Popen, PIPE
import json
import copy
import os
import time
import tempfile

class bwCLI:
    def __init__(self, bwsess):
        self.bwsess = bwsess
        self.debug = False

    def error(self, subcmd, rc, out, err, session):
        # if a session is required for the failed command check the session
        if session:
            if not self.unlocked():
                print("Run 'den -r' there are no valid sessions.")
                os._exit(1)
        print("The command 'bw {}' exited with code '{}'".format(subcmd, rc))
        print("---- stdout ----\n{}\n---- stderr ----\n{}\n".format(out, err))
        os._exit(1)

    def unlocked(self):
        rc, out, err = self._call(['status', '--raw'], True)
        if rc != 0:
            # set session to false to avoid loop
            self.error('status', rc, out, err, False)
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

    def call(self, args, session=True, goodcodes=[0]):
        rc, out, err = self._call(args, session)
        if rc not in goodcodes:
            self.error(args[0], rc, out, err, session)
        else:
            return out

    def debug_call(self, args, session):
        if self.debug:
            arg_copy = copy.deepcopy(args)
            if args[0] == 'unlock':
                arg_copy[1] = 'PASSPHRASE_REDACTED'
            print("Command Arguments: {}\nUses Session:      {}".format(arg_copy, session))

    def _call(self, args, session):
        self.debug_call(args, session)
        # if session is need and not set try to get session
        if session and self.bwsess.session_token == '':
            self.bwsess.decrypt_session()
        cmd = ['bw']
        cmd.extend(args)
        if session:
            cmd.extend(['--session', self.bwsess.session_token])
        # # The auto password prompt cant be disabled :(
        # # was wanting to use a in memory file but gave up
        # # https://stackoverflow.com/questions/18421757/live-output-from-subprocess-command
        # # https://docs.pyfilesystem.org/en/latest/reference/memoryfs.html
        # # neiter work need fileno() for the object
        # out = ''
        # with tempfile.NamedTemporaryFile() as tmp:
        #     writer = open(tmp.name, 'wb')
        #     reader = open(tmp.name, 'rb')
        #     bw_proc = Popen(cmd, shell=False, stdin=PIPE, stdout=PIPE, stderr=writer)
        #     while bw_proc.poll() is None:
        #         # you have to read stdout live other will there can be a deadlock when the
        #         # child process generates enough output to a pipe such that it blocks
        #         # waiting for the OS pipe buffer to accept more data
        #         out += bw_proc.stdout.read().decode('utf-8')
        #         time.sleep(0.1)
        #         err = reader.read().decode('utf-8')
        #         if '? Master password:' in err:
        #             bw_proc.stdin.write(b'\n')
        #             try: bw_proc.stdin.flush()
        #             except BrokenPipeError as e:
        #                 pass
        bw_proc = Popen(cmd, shell=False, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        try:
            out, err = bw_proc.communicate(timeout=15)
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        return (bw_proc.returncode, out.decode('utf-8'), err.decode('utf-8'))

    def unlock(self, passphrase):
        return self._call(['unlock', passphrase, '--raw'], False)

    def lock(self):
        return self.call(['lock'], False, [0,1])

    def sync(self):
        return self.call(['sync'])

    def get(self, item_id):
        out = self.call(['get', 'item', item_id, '--raw'])
        try:
            return json.loads(out)
        except:
            print("Get for id '{}' did not return valid json.".format(item_id))
            os._exit(1)

    def list(self, obj):
        return self.call(['list', obj])

