class gpgHelper:
    def __init__(self, config):
        self.config = config
        self.gpg = gnupg.GPG(gnupghome=str(self.config.gpg_home), use_agent=True)

        keys_pub = self.gpg.list_keys().key_map
        key = keys_pub.get(self.config.fingerprint)
        if not key:
            sys.exit("Could not find fingerprint in public keyring: '{}'".format(self.config.fingerprint))
        keys_priv = self.gpg.list_keys().key_map
        key = keys_priv.get(self.config.fingerprint)
        if not key:
            sys.exit("Could not find fingerprint in secrets keyring: '{}'".format(self.config.fingerprint))

    def decrypt_file(self, file_path):
        self.verify_asc_file(file_path)
        with open(file_path, 'rb') as f:
            result = str(self.gpg.decrypt_file(f))
        return result

    def encrypt_to_file(self, content, file_path):
        if not content:
            sys.exit("Nothing was given to encrypt to '{}'".format(file_path))
        self.gpg.encrypt(content, self.config.fingerprint, output=file_path)
        file_path.chmod(self.config.perms)
        self.verify_asc_file(file_path)

    def verify_asc_file(self, file_path):
        assert(file_path.suffix == '.asc')
        if not file_path.is_file():
            sys.exit("No encrypted file at: '{}'".format(file_path))
        assert(file_path.stat().st_size > 0)
        assert(file_path.stat().st_mode == self.config.perms)
        with open(file_path, 'r') as f:
            content = f.read()
        content = content.strip().splitlines()
        assert('-----BEGIN PGP MESSAGE-----' in content)
        assert('-----END PGP MESSAGE-----' in content)

