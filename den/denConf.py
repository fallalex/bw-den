from pathlib import Path
import json
import yaml
import sys
import os

class denConf:
    def __init__(self):
        self.encrypted_session = Path.home() / '.bw-session.asc'
        # stat.filemode(0o100600) -> '-rw-------'
        self.perms = 0o100600
        self.fingerprint = 'C9CB0C945B583DD3E65DDC376B5C20C74C63902A'
        self.gpg_home = Path.home() / '.gnupg'

        self.cache_obj_fields = {'id', 'name', 'folderId', 'organizationId', 'collectionIds', 'password', 'totp', 'login'}
        self.cache_obj_fields_redact = {'password', 'totp','login'}
        self.cache_obj_types = {'items', 'folders', 'collections', 'organizations'}

        self.cache_path = Path.home() / '.bw-cache.asc'

        # The pickle helps speedup dev around the cache
        self.pickle_path = Path('cache.pickle')
        self.redacted_pickle_path = Path('redacted-cache.pickle')
        self.pickle = False
        # self.pickle = True

