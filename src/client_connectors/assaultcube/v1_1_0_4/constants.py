from enum import enum

AC_VERSION = 1104

MAXCLIENTS = 256

CR_DEFAULT = 0

message_types = enum('SV_SERVINFO', 'SV_WELCOME', 'SV_INITCLIENT', 'SV_POS', 'SV_POSC', 'SV_POSN', 'SV_TEXT', 'SV_TEAMTEXT', 'SV_TEXTME', 'SV_TEAMTEXTME', 
                     'SV_SOUND', 'SV_VOICECOM', 'SV_VOICECOMTEAM', 'SV_CDIS', 
                     'SV_SHOOT', 'SV_EXPLODE', 'SV_SUICIDE', 'SV_AKIMBO', 'SV_RELOAD', 'SV_AUTHT', 'SV_AUTHREQ', 'SV_AUTHTRY', 'SV_AUTHANS', 'SV_AUTHCHAL', 
                     'SV_GIBDIED', 'SV_DIED', 'SV_GIBDAMAGE', 'SV_DAMAGE', 'SV_HITPUSH', 'SV_SHOTFX', 'SV_THROWNADE', 
                     'SV_TRYSPAWN', 'SV_SPAWNSTATE', 'SV_SPAWN', 'SV_SPAWNDENY', 'SV_FORCEDEATH', 'SV_RESUME', 
                     'SV_DISCSCORES', 'SV_TIMEUP', 'SV_EDITENT', 'SV_ITEMACC', 
                     'SV_MAPCHANGE', 'SV_ITEMSPAWN', 'SV_ITEMPICKUP', 
                     'SV_PING', 'SV_PONG', 'SV_CLIENTPING', 'SV_GAMEMODE', 
                     'SV_EDITMODE', 'SV_EDITH', 'SV_EDITT', 'SV_EDITS', 'SV_EDITD', 'SV_EDITE', 'SV_NEWMAP', 
                     'SV_SENDMAP', 'SV_RECVMAP', 'SV_REMOVEMAP', 
                     'SV_SERVMSG', 'SV_ITEMLIST', 'SV_WEAPCHANGE', 'SV_PRIMARYWEAP', 
                     'SV_FLAGACTION', 'SV_FLAGINFO', 'SV_FLAGMSG', 'SV_FLAGCNT', 
                     'SV_ARENAWIN', 
                     'SV_SETADMIN', 'SV_SERVOPINFO', 
                     'SV_CALLVOTE', 'SV_CALLVOTESUC', 'SV_CALLVOTEERR', 'SV_VOTE', 'SV_VOTERESULT', 
                     'SV_SETTEAM', 'SV_TEAMDENY', 'SV_SERVERMODE', 
                     'SV_WHOIS', 'SV_WHOISINFO', 
                     'SV_LISTDEMOS', 'SV_SENDDEMOLIST', 'SV_GETDEMO', 'SV_SENDDEMO', 'SV_DEMOPLAYBACK', 
                     'SV_CONNECT', 'SV_SPECTCN', 
                     'SV_SWITCHNAME', 'SV_SWITCHSKIN', 'SV_SWITCHTEAM', 
                     'SV_CLIENT', 
                     'SV_EXTENSION', 
                     'SV_MAPIDENT', 'SV_HUDEXTRAS', 'SV_POINTS', 'SV_NUM')
                     
flag_states = enum('CTFF_INBASE', 'CTFF_STOLEN', 'CTFF_DROPPED', 'CTFF_IDLE')

flag_messages = enum('FM_PICKUP', 'FM_DROP', 'FM_LOST', 'FM_RETURN', 'FM_SCORE', 'FM_KTFSCORE', 'FM_SCOREFAIL', 'FM_RESET', 'FM_NUM')

guns = enum('GUN_KNIFE', 'GUN_PISTOL', 'GUN_RIFLE', 'GUN_SHOTGUN', 'GUN_SUBGUN', 'GUN_SNIPER', 'GUN_ASSAULT', 'GUN_CPISTOL', 'GUN_GRENADE', 'GUN_AKIMBO', 'NUMGUNS')

vote_types = enum('SA_KICK', 'SA_BAN', 'SA_REMBANS', 'SA_MASTERMODE', 'SA_AUTOTEAM', 'SA_FORCETEAM', 'SA_GIVEADMIN', 'SA_MAP', 'SA_RECORDDEMO', 'SA_STOPDEMO', 'SA_CLEARDEMOS', 'SA_SERVERDESC', 'SA_SHUFFLETEAMS', 'SA_NUM')

teams = enum('TEAM_CLA', 'TEAM_RVSF', 'TEAM_CLA_SPECT', 'TEAM_RVSF_SPECT', 'TEAM_SPECT', 'TEAM_NUM', 'TEAM_ANYACTIVE')
