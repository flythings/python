#!/usr/bin/python
from dataclasses import dataclass

@dataclass
class ServerConfig:

    server: str = ''
    user: str = ''
    password: str = ''

    foi: str = ''           #device
    procedure: str = ''     #sensor

    login_type: str = ''
    authorization: str = ''
    token: str = ''
    hash: str = ''
    timeout: int = 1000
    workspace = None
