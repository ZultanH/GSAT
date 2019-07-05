import json
import valve.source
import valve.source.a2s
import valve.source.master_server
import valve.rcon

class serverInfo:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        try:
            self.server = valve.source.a2s.ServerQuerier((ip, port))
            self.info = self.server.info()
            self.players = self.server.players()
        finally:
            self.server.close()
            
    @property
    def server_name(self):
        return self.info['server_name']

    @property
    def response_type(self):
        return self.info['response_type']
    
    @property
    def map(self):
        return self.info['map']
    
    @property
    def folder(self):
        return self.info['folder']

    @property
    def game(self):
        return self.info['game']

    @property
    def app_id(self):
        return self.info['app_id']

    @property
    def player_count(self):
        return self.info['player_count']

    @property
    def max_players(self):
        return self.info['max_players']

    @property
    def bot_count(self):
        return self.info['bot_count']

    @property
    def server_type(self):
        return self.info['server_type']

    @property
    def platform(self):
        return self.info['platform']

    @property
    def password_protected(self):
        return self.info['password_protected']

    @property
    def vac_enabled(self):
        return self.info['vac_enabled']

    @property
    def version(self):
        return self.info['version']

    @property
    def playerlist(self):
        return self.players['players']

    @property
    def info_obj(self):
        return {
            'respone_type': self.response_type,
            'server_name': self.server_name,
            'map': self.map,
            'folder': self.folder,
            'game': self.game,
            'app_id': self.app_id,
            'player_count': self.player_count,
            'max_players': self.max_players,
            'bot_count': self.bot_count,
            'password_protected': self.password_protected,
            'vac_enabled': self.vac_enabled,
            'version': self.version
        }

    @property
    def players_obj(self):
        return self.players