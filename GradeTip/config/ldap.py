import os
from types import SimpleNamespace

ldap = SimpleNamespace(
    server=os.environ.get('APP_SERVER'),
    base_dn=os.environ.get('BASE_DN'),
    binduser_dn=os.environ.get('BINDUSER_DN'),
    credentials_file=os.environ.get('CREDENTIALS_FILE')
)
