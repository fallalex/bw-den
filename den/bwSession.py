class bwSession:
    def __init__(self, config):
        self.config = config
        self.bwcli = bwCLI(self)
        self.gpg = gpgHelper(self.config)
        self.session_token = ''

    def new_session(self):
        self.bwcli.lock()
        rc = 1
        while (rc != 0):
            passphrase = getpass()
            rc, out, err = self.bwcli.unlock(passphrase)
        self.session_token = out
        if not self.bwcli.unlocked():
            sys.exit("Session failed to unlock")
        self.gpg.encrypt_to_file(self.session_token, self.config.encrypted_session)

    def decrypt_session(self):
        self.session_token = self.gpg.decrypt_file(self.config.encrypted_session)
        if not self.session_token:
            sys.exit("Failed to decrypt session or empty file. Try this command\n  gpg --decrypt '{}'".format(self.config.encrypted_session))


