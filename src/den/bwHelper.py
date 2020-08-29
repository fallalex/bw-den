import json
import sys
import pickle
import pyotp
import os
import copy
from .denConf import denConf
from .bwSession import bwSession

def _findkey(obj, key):
    """
    This is only used on read in json. So only need to handle list, map, and non-iterables.
    Looking for keys in maps that can be nested in lists or other maps.
    Returns tuple of bool and value.
    Value of key could be anything. Bool represents if key was found.
    Limitation is this only returns the first matching key.
    """
    if isinstance(obj, list):
        for v in obj:
            # for custom fields in bitwarden
            if 'name' in v and 'value' in v:
                transform = {v['name']: v['value']}
                exists, value = _findkey(transform, key)
                if exists: return (exists, value)
    if isinstance(obj, dict):
        if key in obj: return (True, obj[key])
        for k, v in obj.items():
            exists, value = _findkey(v, key)
            if exists: return (exists, value)
    return (False, None)

class bwHelper:
    def __init__(self):
        self.config = denConf()
        self.bwsess = bwSession(self.config)
        self.gpg = self.bwsess.gpg
        self.bwcli = self.bwsess.bwcli
        self.cache_dict = {}
        for obj_type in self.config.cache_obj_types:
            self.cache_dict[obj_type] = {}

    def refresh(self):
        if self.config.pickle and self.config.pickle_path.is_file():
            self.bwsess.decrypt_session()
            with open(self.config.pickle_path, 'rb') as f:
                self.cache_dict = pickle.load(f)
        else:
            self.bwsess.new_session()
            out = self.bwcli.sync()
            for obj in list(self.cache_dict.keys()):
                out = self.bwcli.list(obj)
                try: self.cache_dict[obj] = json.loads(out)
                except: sys.exit("Failed to parse json from '{}'.".format(obj))
            if self.config.pickle:
                with open(self.config.pickle_path, 'wb') as f:
                    pickle.dump(self.cache_dict, f)
            else:
                if self.config.pickle_path.is_file():
                    self.config.pickle_path.unlink()
        self.cache_redact()
        self.cache_transform()
        if self.config.pickle:
            with open(self.config.redacted_pickle_path, 'wb') as f:
                pickle.dump(self.cache_dict, f)
        else:
            if self.config.redacted_pickle_path.is_file():
                self.config.redacted_pickle_path.unlink()
        self.gpg.encrypt_to_file(json.dumps(self.cache_dict), self.config.cache_path)

    def cache_redact(self):
        assert(self.config.cache_obj_types == set(self.cache_dict.keys()))
        for obj_type in self.config.cache_obj_types:
            for obj_idx in range(len(self.cache_dict[obj_type])):
                for k in self.config.cache_obj_fields_redact:
                    exists, value = _findkey(self.cache_dict[obj_type][obj_idx], k)
                    if exists:
                        self.cache_dict[obj_type][obj_idx][k] = bool(value)
                for k in list(self.cache_dict[obj_type][obj_idx].keys()):
                    if k not in (self.config.cache_obj_fields | self.config.cache_obj_fields_redact):
                        del self.cache_dict[obj_type][obj_idx][k]

    def cache_transform(self):
        assert('items' in self.config.cache_obj_types)
        assert(self.config.cache_obj_types == set(self.cache_dict.keys()))
        types = copy.deepcopy(self.config.cache_obj_types)
        types.remove('items')
        assert(self.config.cache_obj_types != types)
        for obj_type in types:
            type_dict = {}
            for obj in self.cache_dict[obj_type]:
                assert(isinstance(obj, dict))
                assert(len(obj))
                assert('id' in obj)
                temp = copy.deepcopy(obj)
                del temp['id']
                type_dict[obj['id']] = temp
            self.cache_dict[obj_type] = type_dict

    def decrypt_cache(self):
        self.cache_dict = self.gpg.decrypt_file(self.config.cache_path)
        if not self.cache_dict:
            sys.exit("Failed to decrypt cache or empty file. Try this command\n  gpg --decrypt '{}'".format(self.config.cache_path))
        try: self.cache_dict = json.loads(self.cache_dict)
        except: sys.exit("Failed to parse json from '{}'.".format(self.config.cache_path))
        assert(self.config.cache_obj_types == set(self.cache_dict.keys()))

    def completion(self, obj_type):
        assert(obj_type in (self.config.cache_obj_types | {'all'}))
        # return the json for the cache
        if obj_type == 'all':
            return json.dumps(self.cache_dict)
        names = set()
        # list
        if obj_type == 'items':
            for obj in self.cache_dict[obj_type]:
                assert('name' in obj)
                names.add(obj['name'])
        # dict
        else:
            for k, v in self.cache_dict[obj_type].items():
                assert('name' in v)
                names.add(v['name'])
        return '\n'.join(sorted(names))

    def get_pass(self, id):
        return self.get_item(id, 'password')

    def get_totp(self, id):
        token = self.get_item(id, 'totp')
        return pyotp.TOTP(token).now()

    def field_exists(self, obj, field):
        return _findkey(obj, field)[0]

    def field_value(self, obj, field):
        """
        Get value of field. If does not exist returns NoneType.
        Does not validate field exists.
        """
        return _findkey(obj, field)[1]

    def get_field(self, obj, field):
        """
        Return Tuple(Bool exists, Object value)
        """
        return _findkey(obj, field)

    def get_item(self, id, field=None):
        item = self.bwcli.get(id)
        if field != None:
            exists, value = _findkey(item, field)
            if not exists or value == None:
                print("The field '{}' is not in id '{}' or is NoneType.".format(field, id))
                os._exit(1)
            return value
        return item

    def item_str(self, item):
        string = ''
        #TODO: abstract key check
        for k, v in item.items():
            if k in {'folderId', 'organizationId', 'collectionIds'}:
                pass
            #WIP
        return string


    def item_id(self, name, folder=None, collection=None, organization=None):
        ids = []
        for i in self.cache_dict['items']:
            if name == i['name']:
                if folder != None:
                    # 'No Folder' aka None is a folder
                    if folder != 'No Folder' and i['folderId'] == None: continue
                    if folder == 'No Folder' and i['folderId'] != None: continue
                    if folder != 'No Folder' and self.cache_dict['folders'][i['folderId']]['name'] != folder: continue
                if collection != None:
                    if not len(i['collectionIds']) or i['organizationId'] == None: continue
                    collections = [self.cache_dict['collections'][c]['name'] for c in i['collectionIds']]
                    if collection not in collections: continue
                if organization != None:
                    if i['organizationId'] == None: continue
                    if self.cache_dict['organizations'][i['organizationId']]['name'] != organization: continue
                    # ensure matched collection also matches organization
                    if collection:
                        collections = [c for c in self.cache_dict['collections'] if c['organizationId'] == i['organizationId']]
                        if not len(collections):
                            continue
                ids.append(i)
        if len(ids) == 1:
            return ids[0]
        print("Failed to match id for '{}'".format(name))
        for i in ids:
            print(self.item_str(i))
            print()
        os._exit(1)

