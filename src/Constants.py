from enum import enum

message_types = enum('N_CONNECT', 'N_SERVERINIT', 'N_WELCOME', 'N_CLIENTINIT', 'N_POS', 'N_SPHY', 'N_TEXT', 'N_COMMAND', 'N_ANNOUNCE', 'N_DISCONNECT',
                     'N_SHOOT', 'N_DESTROY', 'N_STICKY', 'N_SUICIDE', 'N_DIED', 'N_POINTS', 'N_DAMAGE', 'N_SHOTFX',
                     'N_LOADW', 'N_TRYSPAWN', 'N_SPAWNSTATE', 'N_SPAWN', 'N_DROP', 'N_WSELECT',
                     'N_MAPCHANGE', 'N_MAPVOTE', 'N_CLEARVOTE', 'N_CHECKPOINT', 'N_ITEMSPAWN', 'N_ITEMUSE', 'N_TRIGGER', 'N_EXECLINK',
                     'N_PING', 'N_PONG', 'N_CLIENTPING', 'N_TICK', 'N_NEWGAME', 'N_ITEMACC', 'N_SERVMSG', 'N_GAMEINFO', 'N_RESUME',
                     'N_EDITMODE', 'N_EDITENT', 'N_EDITLINK', 'N_EDITVAR', 'N_EDITF', 'N_EDITT', 'N_EDITM', 'N_FLIP', 'N_COPY', 'N_PASTE', 'N_ROTATE', 'N_REPLACE', 'N_DELCUBE', 'N_REMIP', 'N_CLIPBOARD', 'N_NEWMAP',
                     'N_GETMAP', 'N_SENDMAP', 'N_FAILMAP', 'N_SENDMAPFILE',
                     'N_MASTERMODE', 'N_ADDCONTROL', 'N_CLRCONTROL', 'N_CURRENTPRIV', 'N_SPECTATOR', 'N_WAITING', 'N_SETPRIV', 'N_SETTEAM',
                     'N_SETUPAFFIN', 'N_INFOAFFIN', 'N_MOVEAFFIN',
                     'N_TAKEAFFIN', 'N_RETURNAFFIN', 'N_RESETAFFIN', 'N_DROPAFFIN', 'N_SCOREAFFIN', 'N_INITAFFIN', 'N_SCORE',
                     'N_LISTDEMOS', 'N_SENDDEMOLIST', 'N_GETDEMO', 'N_SENDDEMO',
                     'N_DEMOPLAYBACK', 'N_RECORDDEMO', 'N_STOPDEMO', 'N_CLEARDEMOS',
                     'N_CLIENT', 'N_RELOAD', 'N_REGEN',
                     'N_ADDBOT', 'N_DELBOT', 'N_INITAI',
                     'N_MAPCRC', 'N_CHECKMAPS',
                     'N_SETPLAYERINFO', 'N_SWITCHTEAM',
                     'N_AUTHTRY', 'N_AUTHCHAL', 'N_AUTHANS',
                     'NUMMSG')
            
W_MAX = 11
         
var_types = enum('ID_VAR', 'ID_FVAR', 'ID_SVAR', 'ID_COMMAND', 'ID_ALIAS', 'ID_LOCAL')
                     
physics_events = enum('SPHY_NONE', 'SPHY_JUMP', 'SPHY_BOOST', 'SPHY_DASH', 'SPHY_MELEE', 'SPHY_KICK', 'SPHY_VAULT', 'SPHY_SKATE', 'SPHY_POWER', 'SPHY_EXTINGUISH', 'SPHY_BUFF', 'SPHY_MAX')

game_modes = enum('G_DEMO', 'G_EDITMODE', 'G_CAMPAIGN', 'G_DEATHMATCH', 'G_CAPTURE', 'G_DEFEND', 'G_BOMBER', 'G_TRIAL', 'G_GAUNTLET', 'G_MAX')

def m_bomber(gamemode):
    return gamemode == game_modes.G_BOMBER
    
def m_defend(gamemode):
    return gamemode == game_modes.G_DEFEND
    
def m_capture(gamemode):
    return gamemode == game_modes.G_CAPTURE
