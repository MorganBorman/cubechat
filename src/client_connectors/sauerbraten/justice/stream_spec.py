from CubeDataStream import CubeDataStream

type_method_mapping = {
                            'stream_data': CubeDataStream.read,
                            'int': CubeDataStream.getint, 
                            'uint': CubeDataStream.getuint,
                            'string': CubeDataStream.getstring, 
                            'float': CubeDataStream.getfloat
                        }

from StreamSpecification import Field, FieldCollection, IteratedFieldCollection, TerminatedFieldCollection
from StreamSpecification import ConditionalFieldCollection
from StreamSpecification import MessageType, StreamStateModifierType, StreamSpecification
from StreamSpecification import StreamContainerType, RawField

stream_spec = StreamSpecification(CubeDataStream, type_method_mapping, {}, "int")

from .constants import message_types, weapon_types

mt = MessageType("N_SERVINFO",
        Field(name="clientnum", type="int"), 
        Field(name="protocol_version", type="int"),
        Field(name="sessionid", type="int"),
        Field(name="haspwd", type="int"),
        Field(name="description", type="string"))
stream_spec.add_message_type(message_types.N_SERVINFO, mt)

mt = MessageType("N_WELCOME",
        Field(name="hasmap", type="int"))
stream_spec.add_message_type(message_types.N_WELCOME, mt)

mt = MessageType("N_PONG",
        Field(name="cmillis", type="int"))
stream_spec.add_message_type(message_types.N_PONG, mt)

mt = MessageType("N_SERVMSG",
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.N_SERVMSG, mt)

mt = MessageType("N_PAUSEGAME",
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.N_PAUSEGAME, mt)

mt = MessageType("N_TIMEUP",
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.N_TIMEUP, mt)

mt = MessageType("N_ANNOUNCE",
        Field(name="type", type="int"))
stream_spec.add_message_type(message_types.N_ANNOUNCE, mt)

mt = MessageType("N_MASTERMODE",
        Field(name="mastermode", type="int"))
stream_spec.add_message_type(message_types.N_MASTERMODE, mt)

mt = MessageType("N_CDIS",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.N_CDIS, mt)

mt = MessageType("N_SPECTATOR",
        Field(name="clientnum", type="int"),
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.N_SPECTATOR, mt)

mt = MessageType("N_MAPRELOAD")
stream_spec.add_message_type(message_types.N_MAPRELOAD, mt)

mt = MessageType("N_SETTEAM",
        Field(name="clientnum", type="int"),
        Field(name="team", type="string"),
        Field(name="reason", type="int"))
stream_spec.add_message_type(message_types.N_SETTEAM, mt)

mt = MessageType("N_CURRENTMASTER",
        Field(name="clientnum", type="int"),
        Field(name="privilege", type="int"),
        Field(name="mastermode", type="int"))
stream_spec.add_message_type(message_types.N_CURRENTMASTER, mt)

mt = MessageType("N_MAPCHANGE",
        Field(name="map_name", type="string"),
        Field(name="mode_num", type="int"),
        Field(name="hasitems", type="int"))
stream_spec.add_message_type(message_types.N_MAPCHANGE, mt)

mt = MessageType("N_INITCLIENT",
        Field(name="clientnum", type="int"),
        Field(name="name", type="string"),
        Field(name="team", type="string"),
        Field(name="playermodel", type="int"))
stream_spec.add_message_type(message_types.N_INITCLIENT, mt)

mt = MessageType("N_SPAWNSTATE",
        Field(name="clientnum", type="int"),
        Field(name="lifesequence", type="int"),
        Field(name="health", type="int"),
        Field(name="maxhealth", type="int"),
        Field(name="armour", type="int"),
        Field(name="armourtype", type="int"),
        Field(name="gunselect", type="int"),
                IteratedFieldCollection(
                name="ammo",
                count=(weapon_types.GUN_PISTOL-weapon_types.GUN_SG+1),
                field_collection=FieldCollection(Field(name="amount", type="int"))))
stream_spec.add_message_type(message_types.N_SPAWNSTATE, mt)

mt = MessageType("N_RESUME",
        TerminatedFieldCollection(name="clients",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t >= 0,
                                    field_collection=FieldCollection(
                                            Field(name="state", type="int"),
                                            Field(name="frags", type="int"),
                                            Field(name="flags", type="int"),
                                            Field(name="quadmillis", type="int"),
                                            Field(name="clientnum", type="int"),
                                            Field(name="lifesequence", type="int"),
                                            Field(name="health", type="int"),
                                            Field(name="maxhealth", type="int"),
                                            Field(name="armour", type="int"),
                                            Field(name="armourtype", type="int"),
                                            Field(name="gunselect", type="int"),
                                                    IteratedFieldCollection(
                                                    name="ammo",
                                                    count=(weapon_types.GUN_PISTOL-weapon_types.GUN_SG+1),
                                                    field_collection=FieldCollection(Field(name="amount", type="int"))))))
stream_spec.add_message_type(message_types.N_RESUME, mt)

mt = MessageType("N_INITFLAGS",
        IteratedFieldCollection(
            name="teamscores",
            count=2,
            field_collection=FieldCollection(Field(name="score", type="int"))),
        IteratedFieldCollection(
            name="flags",
            count=Field(type="int"),
            field_collection=FieldCollection(
                             Field(name="version", type="int"),
                             Field(name="spawn", type="int"),
                             ConditionalFieldCollection(
                                predicate=Field(type="int"), 
                                predicate_comparison = lambda v: v < 0, # If there is no owner
                                consequent=FieldCollection(
                                     Field(name="owner", type="int"),
                                     Field(name="invisible", type="int"),
                                     ConditionalFieldCollection(
                                        predicate=Field(type="int"), 
                                        predicate_comparison = lambda v: v != 0, # If it has been dropped 
                                        consequent=FieldCollection(
                                             Field(name="dropped", type="int"),
                                             Field(name="dx", type="int"),
                                             Field(name="dy", type="int"),
                                             Field(name="dz", type="int")), 
                                        alternative=FieldCollection(
                                             Field(name="dropped", type="int")), 
                                        peek_predicate=True)), 
                                alternative=FieldCollection(
                                     Field(name="owner", type="int"),
                                     Field(name="invisible", type="int")), 
                                peek_predicate=True),
                             )),
                 )
stream_spec.add_message_type(message_types.N_INITFLAGS, mt)

mt = MessageType("N_DROPFLAG",
        Field(name="clientnum", type="int"),
        Field(name="flag", type="int"),
        Field(name="version", type="int"),
        Field(name="dx", type="int"),
        Field(name="dy", type="int"),
        Field(name="dz", type="int"))
stream_spec.add_message_type(message_types.N_DROPFLAG, mt)

mt = MessageType("N_SCOREFLAG",
        Field(name="clientnum", type="int"),
        Field(name="relayflag", type="int"),
        Field(name="relayversion", type="int"),
        Field(name="goalflag", type="int"),
        Field(name="goalversion", type="int"),
        Field(name="goalspawn", type="int"),
        Field(name="team", type="int"),
        Field(name="score", type="int"),
        Field(name="oflags", type="int"))
stream_spec.add_message_type(message_types.N_SCOREFLAG, mt)

mt = MessageType("N_RETURNFLAG",
        Field(name="clientnum", type="int"),
        Field(name="flag", type="int"),
        Field(name="version", type="int"))
stream_spec.add_message_type(message_types.N_RETURNFLAG, mt)

mt = MessageType("N_TAKEFLAG",
        Field(name="clientnum", type="int"),
        Field(name="flag", type="int"),
        Field(name="version", type="int"))
stream_spec.add_message_type(message_types.N_TAKEFLAG, mt)

mt = MessageType("N_RESETFLAG",
        Field(name="flag", type="int"),
        Field(name="version", type="int"),
        Field(name="spawn", type="int"),
        Field(name="team", type="int"),
        Field(name="score", type="int"))
stream_spec.add_message_type(message_types.N_RESETFLAG, mt)

mt = MessageType("N_INVISFLAG",
        Field(name="flag", type="int"),
        Field(name="invisible", type="int"))
stream_spec.add_message_type(message_types.N_INVISFLAG, mt)

mt = MessageType("N_BASES",
                IteratedFieldCollection(
                name="bases",
                count=Field(type="int"),
                field_collection=FieldCollection(Field(name="ammotype", type="int"),
                                                 Field(name="owner", type="string"),
                                                 Field(name="enemy", type="string"),
                                                 Field(name="converted", type="int"),
                                                 Field(name="ammocount", type="int"))))
stream_spec.add_message_type(message_types.N_BASES, mt)

mt = MessageType("N_BASEINFO",
        Field(name="base", type="int"),
        Field(name="owner", type="string"),
        Field(name="enemy", type="string"),
        Field(name="converted", type="int"),
        Field(name="ammocount", type="int"))
stream_spec.add_message_type(message_types.N_BASEINFO, mt)

mt = MessageType("N_BASESCORE",
        Field(name="base", type="int"),
        Field(name="team", type="string"),
        Field(name="total", type="int"))
stream_spec.add_message_type(message_types.N_BASESCORE, mt)

mt = MessageType("N_REPAMMO",
        Field(name="clientnum", type="int"),
        Field(name="ammotype", type="int"))
stream_spec.add_message_type(message_types.N_REPAMMO, mt)

mt = MessageType("N_BASEREGEN",
        Field(name="clientnum", type="int"),
        Field(name="health", type="int"),
        Field(name="armour", type="int"),
        Field(name="ammotype", type="int"),
        Field(name="ammo", type="int"))
stream_spec.add_message_type(message_types.N_BASEREGEN, mt)

mt = MessageType("N_ITEMLIST",
        TerminatedFieldCollection(name="items",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t >= 0,
                                    field_collection=FieldCollection(
                                                                 Field(name="item_index", type="int"),
                                                                 Field(name="item_type", type="int")))
                 )
stream_spec.add_message_type(message_types.N_ITEMLIST, mt)

mt = MessageType("N_ITEMSPAWN",
        Field(name="item_index", type="int"))
stream_spec.add_message_type(message_types.N_ITEMSPAWN, mt)

mt = MessageType("N_ITEMACC",
        Field(name="item_index", type="int"),
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.N_ITEMACC, mt)

common_edit_fields = [Field(name="sel_ox", type="int"),
                      Field(name="sel_oy", type="int"),
                      Field(name="sel_oz", type="int"),
                      
                      Field(name="sel_sx", type="int"),
                      Field(name="sel_sy", type="int"),
                      Field(name="sel_sz", type="int"),
                      
                      Field(name="sel_grid", type="int"),
                      Field(name="sel_orient", type="int"),
                      
                      Field(name="sel_cx", type="int"),
                      Field(name="sel_cxs", type="int"),
                      Field(name="sel_cy", type="int"),
                      Field(name="sel_cys", type="int"),
                      
                      Field(name="sel_corner", type="int")]

mtf = common_edit_fields + [Field(name="dir", type="int"),
                            Field(name="mode", type="int")]
mt = MessageType("N_EDITF", *mtf)
stream_spec.add_message_type(message_types.N_EDITF, mt)

mtf = common_edit_fields + [Field(name="tex", type="int"),
                            Field(name="allfaces", type="int")]
mt = MessageType("N_EDITT", *mtf)
stream_spec.add_message_type(message_types.N_EDITT, mt)

mtf = common_edit_fields + [Field(name="mat", type="int"),
                            Field(name="filter", type="int")]
mt = MessageType("N_EDITM", *mtf)
stream_spec.add_message_type(message_types.N_EDITM, mt)

mt = MessageType("N_FLIP", *common_edit_fields)
stream_spec.add_message_type(message_types.N_FLIP, mt)

mt = MessageType("N_COPY", *common_edit_fields)
stream_spec.add_message_type(message_types.N_COPY, mt)

mt = MessageType("N_PASTE", *common_edit_fields)
stream_spec.add_message_type(message_types.N_PASTE, mt)

mt = MessageType("N_ROTATE",
        *(common_edit_fields +
        [Field(name="dir", type="int")]))
stream_spec.add_message_type(message_types.N_ROTATE, mt)

mt = MessageType("N_REPLACE",
        *(common_edit_fields +
          [Field(name="tex", type="int"),
           Field(name="newtex", type="int"),
           Field(name="insel", type="int")]))
stream_spec.add_message_type(message_types.N_REPLACE, mt)

mt = MessageType("N_DELCUBE", *common_edit_fields)
stream_spec.add_message_type(message_types.N_DELCUBE, mt)

mt = MessageType("N_REMIP")
stream_spec.add_message_type(message_types.N_REMIP, mt)

"""
int i = getint(p);
float x = getint(p)/DMF, y = getint(p)/DMF, z = getint(p)/DMF;
int type = getint(p);
int attr1 = getint(p), attr2 = getint(p), attr3 = getint(p), attr4 = getint(p), attr5 = getint(p);
"""

mt = MessageType("N_EDITENT",
        Field(name="entid", type="int"),
        Field(name="x", type="int"),
        Field(name="y", type="int"),
        Field(name="z", type="int"),
        Field(name="type", type="int"),
        Field(name="attr1", type="int"),
        Field(name="attr2", type="int"),
        Field(name="attr3", type="int"),
        Field(name="attr4", type="int"),
        Field(name="attr5", type="int"))
stream_spec.add_message_type(message_types.N_EDITENT, mt)

mt = MessageType("N_HITPUSH",
        Field(name="clientnum", type="int"),
        Field(name="gun", type="int"),
        Field(name="damage", type="int"),
        Field(name="fx", type="int"),
        Field(name="fy", type="int"),
        Field(name="fz", type="int"))
stream_spec.add_message_type(message_types.N_HITPUSH, mt)

mt = MessageType("N_SHOTFX",
        Field(name="clientnum", type="int"),
        Field(name="gun", type="int"),
        Field(name="id", type="int"),
        Field(name="fx", type="int"),
        Field(name="fy", type="int"),
        Field(name="fz", type="int"),
        Field(name="tx", type="int"),
        Field(name="ty", type="int"),
        Field(name="tz", type="int"))
stream_spec.add_message_type(message_types.N_SHOTFX, mt)

mt = MessageType("N_EXPLODEFX",
        Field(name="clientnum", type="int"),
        Field(name="gun", type="int"),
        Field(name="id", type="int"))
stream_spec.add_message_type(message_types.N_EXPLODEFX, mt)

mt = MessageType("N_DAMAGE",
        Field(name="clientnum", type="int"),
        Field(name="aggressor", type="int"),
        Field(name="damage", type="int"),
        Field(name="armour", type="int"),
        Field(name="health", type="int"))
stream_spec.add_message_type(message_types.N_DAMAGE, mt)

mt = MessageType("N_DIED",
        Field(name="clientnum", type="int"),
        Field(name="killer", type="int"),
        Field(name="frags", type="int"))
stream_spec.add_message_type(message_types.N_DIED, mt)

mt = MessageType("N_FORCEDEATH",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.N_FORCEDEATH, mt)

mt = MessageType("N_NEWMAP",
        Field(name="size", type="int"))
stream_spec.add_message_type(message_types.N_NEWMAP, mt)

mt = MessageType("N_REQAUTH",
        Field(name="domain", type="string"))
stream_spec.add_message_type(message_types.N_REQAUTH, mt)

mt = MessageType("N_INITAI",
        Field(name="aiclientnum", type="int"),
        Field(name="ownerclientnum", type="int"),
        Field(name="aitype", type="int"),
        Field(name="aiskill", type="int"),
        Field(name="playermodel", type="int"),
        Field(name="name", type="string"),
        Field(name="team", type="string"))
stream_spec.add_message_type(message_types.N_INITAI, mt)

sc = StreamContainerType(CubeDataStream, type_method_mapping, {}, "int", FieldCollection(Field(name="clientnum", type="int")), Field(type="uint"))
stream_spec.add_container_type(message_types.N_CLIENT, sc)

mt = MessageType("N_SPAWN",
        Field(name="lifesequence", type="int"),
        Field(name="health", type="int"),
        Field(name="maxhealth", type="int"),
        Field(name="armour", type="int"),
        Field(name="armourtype", type="int"),
        Field(name="gunselect", type="int"),
        IteratedFieldCollection(
        name="ammo",
        count=(weapon_types.GUN_PISTOL-weapon_types.GUN_SG+1),
        field_collection=FieldCollection(Field(name="amount", type="int"))))
sc.add_message_type(message_types.N_SPAWN, mt)

mt = MessageType("N_SOUND",
        Field(name="sound", type="int"))
sc.add_message_type(message_types.N_SOUND, mt)

mt = MessageType("N_CLIENTPING",
        Field(name="ping", type="int"))
sc.add_message_type(message_types.N_CLIENTPING, mt)

mt = MessageType("N_TAUNT")
sc.add_message_type(message_types.N_TAUNT, mt)

mt = MessageType("N_GUNSELECT",
        Field(name="gunselect", type="int"))
sc.add_message_type(message_types.N_GUNSELECT, mt)

mt = MessageType("N_TEXT",
        Field(name="text", type="string"))
sc.add_message_type(message_types.N_TEXT, mt)

mt = MessageType("N_SAYTEAM",
        Field(name="text", type="string"))
sc.add_message_type(message_types.N_SAYTEAM, mt)

mt = MessageType("N_SWITCHNAME",
        Field(name="name", type="string"))
sc.add_message_type(message_types.N_SWITCHNAME, mt)

mt = MessageType("N_SWITCHMODEL",
        Field(name="model", type="int"))
sc.add_message_type(message_types.N_SWITCHMODEL, mt)

mt = MessageType("N_EDITMODE",
        Field(name="value", type="int"))
sc.add_message_type(message_types.N_EDITMODE, mt)
