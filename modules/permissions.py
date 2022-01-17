import secrets
import sqlite3
from enum import IntEnum
from typing import Union

import nextcord

from modules.globals import Globals
from modules.sqlite import SQLite


class Permissions:

    class PermissionLevel(IntEnum):
        admin = 99
        user = 1
        ignored = 0

    def __init__(self):
        Globals.permissions = self
        self._admin_token = secrets.token_hex(16)
        Globals.log.info(f'admin token: {self._admin_token}')
        self.user_levels = {}
        self.db = SQLite()

        if self.db.connect(Globals.database_file):
            self.init_table()
            self._database_load_permissions()

    def validate_token(self, token: str) -> bool:
        return secrets.compare_digest(self._admin_token, token)

    def has_permission(self, user, permission_level: PermissionLevel) -> bool:
        return self.user_levels.get(user.id, False) >= permission_level

    def is_admin(self, user: nextcord.User) -> bool:
        return self.has_permission(user, self.PermissionLevel.admin)

    def add_permission(self, user: nextcord.User, permission_level: PermissionLevel) -> None:
        self.user_levels.update({user.id: permission_level})
        self._database_add_permission(user, permission_level)

    def _database_add_permission(self, user: nextcord.User, permission_level: PermissionLevel) -> None:
        try:
            self.db.get_cursor().execute('INSERT INTO permissions (user_id, permission_level) VALUES (?, ?)', (user.id, int(permission_level)))
            self.db.commit()
            if self.db.get_cursor().rowcount > 0:
                # If affected rows is not 0, insert succeeded
                Globals.log.debug(f'Added permission: user: {user.id} {user.name} permission level: {str(permission_level)}')
        except sqlite3.Error as err:
            Globals.log.error('SQLite error: ' + str(err))
            raise sqlite3.Error(err)

    def _database_load_permissions(self) -> None:
        try:
            result = self.db.get_cursor().execute('SELECT * FROM permissions').fetchall()
            for id, user_id, permission_level in result:
                self.user_levels.update({user_id: permission_level})
        except sqlite3.Error as err:
            Globals.log.error('SQLite error: ' + str(err))
            raise sqlite3.Error(err)

    def init_table(self) -> None:
        try:
            # If requested table doesn't exist, we create it
            self.db.get_cursor().execute('CREATE TABLE IF NOT EXISTS permissions (id INTEGER PRIMARY KEY, user_id INT UNIQUE, permission_level INTEGER)')
        except sqlite3.Error as err:
            Globals.log.error(f'Table creation failed: {str(err)}')

    def has_discord_permissions(self, member: Union[nextcord.Member, nextcord.Role], permissions_tuple: tuple[nextcord.Permissions], channel) -> bool:
        permissions_dict = {}
        for permission in permissions_tuple:
            permissions_dict[permission] = True
        permissions = nextcord.Permissions.none()
        permissions.update(**permissions_dict)

        return channel.permissions_for(member).is_superset(permissions)

    def client_has_discord_permissions(self, permissions_tuple: tuple[nextcord.Permissions], channel):
        # try to get either Member object or ClientUser
        try:
            return self.has_discord_permissions(channel.guild.me, permissions_tuple, channel=channel)
        except AttributeError:
            return self.has_discord_permissions(Globals.disco.user, permissions_tuple, channel=channel)
