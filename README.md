# bw-scripts
Scripts to assist with Bitwarden use. Tab complete secret names, session management with gnupg, improved 'get' interface for password and totp.

    usage: den [-h] [-f F] [-c] [-a | -p | -o | -s | -n | -z] [-y YML_CONF] [S]

    Simplified interface for copying Passwords and TOTPs from Bitwarden

    positional arguments:
      S                     secret name

    optional arguments:
      -h, --help            show this help message and exit
      -f F, --folder F      folder name
      -c, --no-clip         do not use clipboard
      -a, --all-fields      return all fields of [S]
      -p, --password        return password of [S]
      -o, --totp            return totp of [S]
      -s, --session         return session token
      -n, --new-session     lock and unlock bitwarden for new session
      -z, --completions     list cached secret names for shell completion
      -y YML_CONF, --yml-conf YML_CONF
                            path to yml conf file, default is test

Start a new session for bitwarden and copy the session token to clipboard.

    $ den -n
    Password:

Print the bitwarden session token to stdout.

    $ den -sc
    lasdkfjalsdkjfalsdfkj==

Might want to break away from the general bitwarden-cli at somepoint but it might not be worth the effort.
https://community.bitwarden.com/t/bitwarden-rest-api-for-automated-secrets-management-on-self-hosted-server/1168

https://bitbucket.org/vinay.sajip/python-gnupg/src/master/

Local install

    pip3 install .;  pip3 install -r requirements.txt

