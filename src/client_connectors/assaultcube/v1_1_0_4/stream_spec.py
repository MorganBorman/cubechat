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
from StreamSpecification import MessageType, StreamStateModifierType, StreamSpecification, SwitchField, CaseField
from StreamSpecification import StreamContainerType, RawField, CustomMessageType

stream_spec = StreamSpecification(CubeDataStream, type_method_mapping, {}, "int")

from .constants import message_types, flag_messages, guns, MAXCLIENTS

'''
case SV_SERVINFO:  // welcome messsage from the server
{
    int mycn = getint(p), prot = getint(p);
    if(prot!=CUR_PROTOCOL_VERSION && !(watchingdemo && prot == -PROTOCOL_VERSION))
    {
        conoutf(_("%c3incompatible game protocol (local protocol: %d :: server protocol: %d)"), CC, CUR_PROTOCOL_VERSION, prot);
        conoutf("\f3if this occurs a lot, obtain an upgrade from \f1http://assault.cubers.net");
        if(watchingdemo) conoutf("breaking loop : \f3this demo is using a different protocol\f5 : end it now!"); // SVN-WiP-bug: causes endless retry loop else!
        else disconnect();
        return;
    }
    sessionid = getint(p);
    player1->clientnum = mycn;
    if(getint(p) > 0) conoutf(_("INFO: this server is password protected"));
    sendintro();
    break;
}
'''

mt = MessageType("SV_SERVINFO",
        Field(name="clientnum", type="int"), 
        Field(name="protocol_version", type="int"),
        Field(name="sessionid", type="int"),
        Field(name="haspwd", type="int"))
stream_spec.add_message_type(message_types.SV_SERVINFO, mt)

'''
case SV_WELCOME:
    joining = getint(p);
    player1->resetspec();
    resetcamera();
    break;
'''

mt = MessageType("SV_WELCOME",
        Field(name="joining", type="int"))
stream_spec.add_message_type(message_types.SV_WELCOME, mt)

'''
case SV_CLIENT:
{
    int cn = getint(p), len = getuint(p);
    ucharbuf q = p.subbuf(len);
    parsemessages(cn, getclient(cn), q);
    break;
}
'''

sc = StreamContainerType(CubeDataStream, type_method_mapping, {}, "int", 
                    FieldCollection(Field(name="clientnum", type="int")), 
                    Field(type="uint"))
stream_spec.add_container_type(message_types.SV_CLIENT, sc)

'''
case SV_SOUND:
    audiomgr.playsound(getint(p), d);
    break;
'''

mt = MessageType("SV_SOUND",
        Field(name="sound", type="int"))
sc.add_message_type(message_types.SV_SOUND, mt)

'''
case SV_VOICECOMTEAM:
{
    playerent *d = getclient(getint(p));
    if(d) d->lastvoicecom = lastmillis;
    int t = getint(p);
    if(!d || !(d->muted || d->ignored))
    {
        if ( voicecomsounds == 1 || (voicecomsounds == 2 && m_teammode) ) audiomgr.playsound(t, SP_HIGH);
    }
    break;
}
'''

mt = MessageType("SV_VOICECOMTEAM",
        Field(name="clientnum", type="int"),
        Field(name="sound", type="int"))
stream_spec.add_message_type(message_types.SV_VOICECOMTEAM, mt)

'''
case SV_VOICECOM:
{
    int t = getint(p);
    if(!d || !(d->muted || d->ignored))
    {
        if ( voicecomsounds == 1 ) audiomgr.playsound(t, SP_HIGH);
    }
    if(d) d->lastvoicecom = lastmillis;
    break;
}
'''

mt = MessageType("SV_VOICECOM",
        Field(name="sound", type="int"))
sc.add_message_type(message_types.SV_VOICECOM, mt)

'''
case SV_TEAMTEXTME:
case SV_TEAMTEXT:
{
    int cn = getint(p);
    getstring(text, p);
    filtertext(text, text);
    playerent *d = getclient(cn);
    if(!d) break;
    if(d->ignored) clientlogf("ignored: %s%s %s", colorname(d), type == SV_TEAMTEXT ? ":" : "", text);
    else
    {
        if(m_teammode) conoutf(type == SV_TEAMTEXTME ? "\f1%s %s" : "%s:\f1 %s", colorname(d), highlight(text));
        else conoutf(type == SV_TEAMTEXTME ? "\f0%s %s" : "%s:\f0 %s", colorname(d), highlight(text));
    }
    break;
}
'''

mt = MessageType("SV_TEAMTEXTME",
        Field(name="clientnum", type="int"),
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.SV_TEAMTEXTME, mt)

mt = MessageType("SV_TEAMTEXT",
        Field(name="clientnum", type="int"),
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.SV_TEAMTEXT, mt)

'''
case SV_TEXTME:
case SV_TEXT:
    if(cn == -1)
    {
        getstring(text, p);
        conoutf("MOTD:");
        conoutf("\f4%s", text);
    }
    else if(d)
    {
        getstring(text, p);
        filtertext(text, text);
        if(d->ignored && d->clientrole != CR_ADMIN) clientlogf("ignored: %s%s %s", colorname(d), type == SV_TEXT ? ":" : "", text);
        else conoutf(type == SV_TEXTME ? "\f0%s %s" : "%s:\f0 %s", colorname(d), highlight(text));
    }
    else return;
    break;
'''

mt = MessageType("SV_TEXTME",
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.SV_TEXTME, mt)
sc.add_message_type(message_types.SV_TEXTME, mt)

mt = MessageType("SV_TEXT",
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.SV_TEXT, mt)
sc.add_message_type(message_types.SV_TEXT, mt)

'''
case SV_MAPCHANGE:
{
    extern int spawnpermission;
    spawnpermission = SP_SPECT;
    getstring(text, p);
    int mode = getint(p);
    int downloadable = getint(p);
    int revision = getint(p);
    localwrongmap = !changemapserv(text, mode, downloadable, revision);
    if(m_arena && joining>2) deathstate(player1);
    break;
}
'''

mt = MessageType("SV_MAPCHANGE",
        Field(name="text", type="string"),
        Field(name="mode", type="int"),
        Field(name="downloadable", type="int"),
        Field(name="revision", type="int"))
stream_spec.add_message_type(message_types.SV_MAPCHANGE, mt)

'''
case SV_ITEMLIST:
{
    int n;
    resetspawns();
    while((n = getint(p))!=-1) setspawn(n, true);
    break;
}
'''

mt = MessageType("SV_ITEMLIST",
        TerminatedFieldCollection(name="items",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t != -1,
                                    field_collection=FieldCollection(
                                                                 Field(name="item_index", type="int"))))
stream_spec.add_message_type(message_types.SV_ITEMLIST, mt)

'''
case SV_MAPIDENT:
{
    loopi(2) getint(p);
    break;
}
'''

mt = MessageType("SV_MAPIDENT",
        Field(name="gzipsize", type="int"),
        Field(name="revision", type="int"))
sc.add_message_type(message_types.SV_MAPIDENT, mt)

'''
case SV_SWITCHNAME:
    getstring(text, p);
    filtertext(text, text, 0, MAXNAMELEN);
    if(!text[0]) copystring(text, "unarmed");
    if(d)
    {
        if(strcmp(d->name, text))
            conoutf(_("%s is now known as %s"), colorname(d), colorname(d, text));
        copystring(d->name, text, MAXNAMELEN+1);
        updateclientname(d);
    }
    break;
'''

mt = MessageType("SV_SWITCHNAME",
        Field(name="text", type="string"))
sc.add_message_type(message_types.SV_SWITCHNAME, mt)

'''
case SV_SWITCHTEAM:
    getint(p);
    break;
'''

mt = MessageType("SV_SWITCHTEAM",
        Field(name="team", type="int"))
sc.add_message_type(message_types.SV_SWITCHTEAM, mt)

'''
case SV_SWITCHSKIN:
    loopi(2)
    {
        int skin = getint(p);
        if(d) d->setskin(i, skin);
    }
    break;
'''

mt = MessageType("SV_SWITCHSKIN",
        IteratedFieldCollection(
            name="skins",
            count=2,
            field_collection=FieldCollection(Field(name="skin", type="int"))))
sc.add_message_type(message_types.SV_SWITCHSKIN, mt)

'''
case SV_INITCLIENT:            // another client either connected or changed name/team
{
    int cn = getint(p);
    playerent *d = newclient(cn);
    if(!d)
    {
        getstring(text, p);
        loopi(2) getint(p);
        getint(p);
        break;
    }
    getstring(text, p);
    filtertext(text, text, 0, MAXNAMELEN);
    if(!text[0]) copystring(text, "unarmed");
    if(d->name[0])          // already connected
    {
        if(strcmp(d->name, text))
            conoutf(_("%s is now known as %s"), colorname(d), colorname(d, text));
    }
    else                    // new client
    {
        conoutf(_("connected: %s"), colorname(d, text));
    }
    copystring(d->name, text, MAXNAMELEN+1);
    loopi(2) d->setskin(i, getint(p));
    d->team = getint(p);
    if(m_flags) loopi(2)
    {
        flaginfo &f = flaginfos[i];
        if(!f.actor) f.actor = getclient(f.actor_cn);
    }
    updateclientname(d);
    break;
}
'''

mt = MessageType("SV_INITCLIENT",
        Field(name="clientnum", type="int"),
        Field(name="name", type="string"),
        IteratedFieldCollection(
            name="skins",
            count=2,
            field_collection=FieldCollection(Field(name="skin", type="int"))),
        Field(name="team", type="int"))
stream_spec.add_message_type(message_types.SV_INITCLIENT, mt)

'''
case SV_CDIS:
{
    int cn = getint(p);
    playerent *d = getclient(cn);
    if(!d) break;
    if(d->name[0]) conoutf(_("player %s disconnected"), colorname(d));
    zapplayer(players[cn]);
    break;
}
'''

mt = MessageType("SV_CDIS",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_CDIS, mt)

'''
case SV_EDITMODE:
{
    int val = getint(p);
    if(!d) break;
    if(val) d->state = CS_EDITING;
    else d->state = CS_ALIVE;
    break;
}
'''

mt = MessageType("SV_EDITMODE",
        Field(name="value", type="int"))
sc.add_message_type(message_types.SV_EDITMODE, mt)

'''
case SV_SPAWN:
{
    playerent *s = d;
    if(!s) { static playerent dummy; s = &dummy; }
    s->respawn();
    s->lifesequence = getint(p);
    s->health = getint(p);
    s->armour = getint(p);
    int gunselect = getint(p);
    s->setprimary(gunselect);
    s->selectweapon(gunselect);
    loopi(NUMGUNS) s->ammo[i] = getint(p);
    loopi(NUMGUNS) s->mag[i] = getint(p);
    s->state = CS_SPAWNING;
    if(s->lifesequence==0) s->resetstats(); //NEW
    break;
}
'''

state_fields = (
    Field(name="lifesequence", type="int"),
    Field(name="health", type="int"),
    Field(name="armour", type="int"),
)

ammo_fields = (
    IteratedFieldCollection(
        name="ammo",
        count=guns.NUMGUNS,
        field_collection=FieldCollection(Field(name="amount", type="int"))),
    IteratedFieldCollection(
        name="magazine",
        count=guns.NUMGUNS,
        field_collection=FieldCollection(Field(name="amount", type="int")))
)

mt = MessageType("SV_SPAWN",
        state_fields+
        (Field(name="gunselect", type="int"),)+
        ammo_fields)
sc.add_message_type(message_types.SV_SPAWN, mt)

'''
case SV_SPAWNSTATE:
{

    if ( map_quality == MAP_IS_BAD )
    {
        loopi(6+2*NUMGUNS) getint(p);
        conoutf(_("map deemed unplayable - fix it before you can spawn"));
        break;
    }

    if(editmode) toggleedit(true);
    showscores(false);
    setscope(false);
    setburst(false);
    player1->respawn();
    player1->lifesequence = getint(p);
    player1->health = getint(p);
    player1->armour = getint(p);
    player1->setprimary(getint(p));
    player1->selectweapon(getint(p));
    int arenaspawn = getint(p);
    loopi(NUMGUNS) player1->ammo[i] = getint(p);
    loopi(NUMGUNS) player1->mag[i] = getint(p);
    player1->state = CS_ALIVE;
    lastspawn = lastmillis;
    findplayerstart(player1, false, arenaspawn);
    arenaintermission = 0;
    if(m_arena && !localwrongmap)
    {
        closemenu(NULL);
        conoutf(_("new round starting... fight!"));
        hudeditf(HUDMSG_TIMER, "FIGHT!");
        if(m_botmode) BotManager.RespawnBots();
    }
    addmsg(SV_SPAWN, "rii", player1->lifesequence, player1->weaponsel->type);
    player1->weaponswitch(player1->primweap);
    player1->weaponchanging -= weapon::weaponchangetime/2;
    if(player1->lifesequence==0) player1->resetstats(); //NEW
    break;
}
'''

mt = MessageType("SV_SPAWNSTATE",
        state_fields+
        (Field(name="primarygun", type="int"),
        Field(name="gunselect", type="int"),
        Field(name="arenaspawn", type="int"))+
        ammo_fields)
stream_spec.add_message_type(message_types.SV_SPAWNSTATE, mt)

'''
case SV_SPECTCN:
    getint(p);
    break;
'''

mt = MessageType("SV_SPECTCN",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_SPECTCN, mt)

'''
case SV_SHOTFX:
{
    int scn = getint(p), gun = getint(p);
    vec from, to;
    loopk(3) to[k] = getint(p)/DMF;
    playerent *s = getclient(scn);
    if(!s || !weapon::valid(gun)) break;
    loopk(3) from[k] = s->o.v[k];
    if(gun==GUN_SHOTGUN) createrays(from, to);
    s->lastaction = lastmillis;
    s->mag[gun]--;
    if(s->weapons[gun])
    {
        s->lastattackweapon = s->weapons[gun];
        s->weapons[gun]->attackfx(from, to, -1);
    }
    s->pstatshots[gun]++; //NEW
    break;
}
'''

mt = MessageType("SV_SHOTFX",
        Field(name="clientnum", type="int"),
        Field(name="gun", type="int"),
        Field(name="x", type="int"),
        Field(name="y", type="int"),
        Field(name="z", type="int"))
stream_spec.add_message_type(message_types.SV_SHOTFX, mt)

'''
case SV_THROWNADE:
{
    vec from, to;
    loopk(3) from[k] = getint(p)/DMF;
    loopk(3) to[k] = getint(p)/DMF;
    int nademillis = getint(p);
    if(!d) break;
    d->lastaction = lastmillis;
    d->lastattackweapon = d->weapons[GUN_GRENADE];
    if(d->weapons[GUN_GRENADE]) d->weapons[GUN_GRENADE]->attackfx(from, to, nademillis);
	if(d!=player1) d->pstatshots[GUN_GRENADE]++; //NEW
    break;
}
'''

mt = MessageType("SV_THROWNADE",
        Field(name="fx", type="int"),
        Field(name="fy", type="int"),
        Field(name="fz", type="int"),
        Field(name="tx", type="int"),
        Field(name="ty", type="int"),
        Field(name="tz", type="int"),
        Field(name="nademillis", type="int"))
sc.add_message_type(message_types.SV_THROWNADE, mt)

'''
case SV_RELOAD:
{
    int cn = getint(p), gun = getint(p);
    playerent *p = cn==getclientnum() ? player1 : getclient(cn);
    if(!p || p==player1) break;
    int bullets = magsize(gun)-p->mag[gun];
    p->ammo[gun] -= bullets;
    p->mag[gun] += bullets;
    break;
}
'''

mt = MessageType("SV_RELOAD",
        Field(name="clientnum", type="int"),
        Field(name="gun", type="int"))
stream_spec.add_message_type(message_types.SV_RELOAD, mt)

'''
// for AUTH: WIP

case SV_AUTHREQ:
{
    extern int autoauth;
    getstring(text, p);
    if(autoauth && text[0] && tryauth(text)) conoutf("server requested authkey \"%s\"", text);
    break;
}
'''

mt = MessageType("SV_AUTHREQ",
        Field(name="domain", type="string"))
stream_spec.add_message_type(message_types.SV_AUTHREQ, mt)

'''
case SV_AUTHCHAL:
{
    getstring(text, p);
    authkey *a = findauthkey(text);
    uint id = (uint)getint(p);
    getstring(text, p);
    if(a && a->lastauth && lastmillis - a->lastauth < 60*1000)
    {
        vector<char> buf;
        answerchallenge(a->key, text, buf);
        //conoutf("answering %u, challenge %s with %s", id, text, buf.getbuf());
        addmsg(SV_AUTHANS, "rsis", a->desc, id, buf.getbuf());
    }
    break;
}
'''

mt = MessageType("SV_AUTHCHAL",
        Field(name="domain", type="string"),
        Field(name="reqid", type="int"),
        Field(name="challenge", type="int"))
stream_spec.add_message_type(message_types.SV_AUTHCHAL, mt)

'''
// :for AUTH

case SV_GIBDAMAGE:
case SV_DAMAGE:
{
    int tcn = getint(p),
        acn = getint(p),
        gun = getint(p),
        damage = getint(p),
        armour = getint(p),
        health = getint(p);
    playerent *target = tcn==getclientnum() ? player1 : getclient(tcn),
              *actor = acn==getclientnum() ? player1 : getclient(acn);
    if(!target || !actor) break;
    target->armour = armour;
    target->health = health;
    dodamage(damage, target, actor, -1, type==SV_GIBDAMAGE, false);
    actor->pstatdamage[gun]+=damage; //NEW
    break;
}
'''

fields = (
        Field(name="target", type="int"),
        Field(name="actor", type="int"),
        Field(name="gun", type="int"),
        Field(name="damage", type="int"),
        Field(name="armour", type="int"),
        Field(name="health", type="int")
)

mt = MessageType("SV_GIBDAMAGE",
        *fields)
stream_spec.add_message_type(message_types.SV_GIBDAMAGE, mt)

mt = MessageType("SV_DAMAGE",
        *fields)
stream_spec.add_message_type(message_types.SV_DAMAGE, mt)

'''
case SV_POINTS:
{
    int count = getint(p);
    if ( count > 0 ) {
        loopi(count){
            int pcn = getint(p); int score = getint(p);
            playerent *ppl = pcn == getclientnum() ? player1 : getclient(pcn);
            if (!ppl) break;
            ppl->points += score;
        }
    } else {
        int medals = getint(p);
        if(medals > 0) {
//          medals_arrived=1;
            loopi(medals) {
                int mcn=getint(p); int mtype=getint(p); int mitem=getint(p);
                a_medals[mtype].assigned=1;
                a_medals[mtype].cn=mcn;
                a_medals[mtype].item=mitem;
            }
        }
    }
    break;
}
'''

mt = MessageType("SV_POINTS",
        ConditionalFieldCollection(
            predicate=Field(type="int"), 
            predicate_comparison = lambda v: v > 0,
            consequent=FieldCollection(
                IteratedFieldCollection(
                name="points",
                count=Field(type="int"),
                field_collection=FieldCollection(Field(name="clientnum", type="int"),
                                                 Field(name="score", type="int")))
            ),
            alternative=FieldCollection(
                Field(name="count", type="int"),
                IteratedFieldCollection(
                name="medals",
                count=Field(type="int"),
                field_collection=FieldCollection(Field(name="clientnum", type="int"),
                                                 Field(name="medaltype", type="int"),
                                                 Field(name="medalitem", type="int")))
            ),
            peek_predicate=True))
stream_spec.add_message_type(message_types.SV_POINTS, mt)

'''
case SV_HUDEXTRAS:
{
    char value = getint(p);
    if (hudextras) showhudextras(hudextras, value);
    break;
}
'''

mt = MessageType("SV_HUDEXTRAS",
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.SV_HUDEXTRAS, mt)

'''
case SV_HITPUSH:
{
    int gun = getint(p), damage = getint(p);
    vec dir;
    loopk(3) dir[k] = getint(p)/DNF;
    player1->hitpush(damage, dir, NULL, gun);
    break;
}
'''

mt = MessageType("SV_HITPUSH",
        Field(name="gun", type="int"),
        Field(name="damage", type="int"),
        Field(name="dx", type="int"),
        Field(name="dy", type="int"),
        Field(name="dz", type="int"))
stream_spec.add_message_type(message_types.SV_HITPUSH, mt)

'''
case SV_GIBDIED:
case SV_DIED:
{
    int vcn = getint(p), acn = getint(p), frags = getint(p), gun = getint(p);
    playerent *victim = vcn==getclientnum() ? player1 : getclient(vcn),
              *actor = acn==getclientnum() ? player1 : getclient(acn);
    if(!actor) break;
    if ( m_mp(gamemode) ) actor->frags = frags;
    if(!victim) break;
    dokill(victim, actor, type==SV_GIBDIED, gun);
    break;
}
'''

fields = (
        Field(name="victim", type="int"),
        Field(name="actor", type="int"),
        Field(name="frags", type="int"),
        Field(name="gun", type="int")
)

mt = MessageType("SV_GIBDIED",
        *fields)
stream_spec.add_message_type(message_types.SV_GIBDIED, mt)

mt = MessageType("SV_DIED",
        *fields)
stream_spec.add_message_type(message_types.SV_DIED, mt)

'''
case SV_RESUME:
{
    loopi(MAXCLIENTS)
    {
        int cn = getint(p);
        if(p.overread() || cn<0) break;
        int state = getint(p), 
            lifesequence = getint(p), 
            primary = getint(p), 
            gunselect = getint(p), 
            flagscore = getint(p), 
            frags = getint(p), 
            deaths = getint(p), 
            health = getint(p), 
            armour = getint(p), 
            points = getint(p);
        int ammo[NUMGUNS], mag[NUMGUNS];
        loopi(NUMGUNS) ammo[i] = getint(p);
        loopi(NUMGUNS) mag[i] = getint(p);
        playerent *d = (cn == getclientnum() ? player1 : newclient(cn));
        if(!d) continue;
        if(d!=player1) d->state = state;
        d->lifesequence = lifesequence;
        d->flagscore = flagscore;
        d->frags = frags;
        d->deaths = deaths;
        d->points = points;
        if(d!=player1)
        {
            d->setprimary(primary);
            d->selectweapon(gunselect);
            d->health = health;
            d->armour = armour;
            memcpy(d->ammo, ammo, sizeof(ammo));
            memcpy(d->mag, mag, sizeof(mag));
            if(d->lifesequence==0) d->resetstats(); //NEW
        }
    }
    break;
}
'''

mt = MessageType("SV_RESUME",
        TerminatedFieldCollection(name="clients",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t >= 0,
                                    field_collection=FieldCollection(
                                            Field(name="clientnum", type="int"),
                                            Field(name="state", type="int"),
                                            Field(name="lifesequence", type="int"),
                                            Field(name="primarygun", type="int"),
                                            Field(name="gunselect", type="int"),
                                            Field(name="flagscore", type="int"),
                                            Field(name="frags", type="int"),
                                            Field(name="deaths", type="int"),
                                            Field(name="health", type="int"),
                                            Field(name="armour", type="int"),
                                            Field(name="points", type="int"),
                                            *ammo_fields
                                            )))
stream_spec.add_message_type(message_types.SV_RESUME, mt)

'''
case SV_DISCSCORES:
{
    discscores.shrink(0);
    int team;
    while((team = getint(p)) >= 0)
    {
        discscore &ds = discscores.add();
        ds.team = team;
        getstring(text, p);
        filtertext(ds.name, text, 0, MAXNAMELEN);
        ds.flags = getint(p);
        ds.frags = getint(p);
        ds.deaths = getint(p);
        ds.points = getint(p);
    }
    break;
}
'''

mt = MessageType("SV_DISCSCORES",
        TerminatedFieldCollection(name="scores",
                                    terminator_field=Field(type="int"),
                                    terminator_comparison=lambda t: t >= 0,
                                    field_collection=FieldCollection(
                                            Field(name="team", type="int"),
                                            Field(name="name", type="string"),
                                            Field(name="flags", type="int"),
                                            Field(name="frags", type="int"),
                                            Field(name="deaths", type="int"),
                                            Field(name="points", type="int")
                                    )))
stream_spec.add_message_type(message_types.SV_DISCSCORES, mt)

'''
case SV_ITEMSPAWN:
{
    int i = getint(p);
    setspawn(i, true);
    break;
}
'''

mt = MessageType("SV_ITEMSPAWN",
        Field(name="item", type="int"))
stream_spec.add_message_type(message_types.SV_ITEMSPAWN, mt)

'''
case SV_ITEMACC:
{
    int i = getint(p), cn = getint(p);
    playerent *d = cn==getclientnum() ? player1 : getclient(cn);
    pickupeffects(i, d);
    break;
}
'''

mt = MessageType("SV_ITEMACC",
        Field(name="item", type="int"),
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_ITEMACC, mt)

'''
case SV_EDITH:              // coop editing messages, should be extended to include all possible editing ops
case SV_EDITT:
case SV_EDITS:
case SV_EDITD:
case SV_EDITE:
{
    int x  = getint(p);
    int y  = getint(p);
    int xs = getint(p);
    int ys = getint(p);
    int v  = getint(p);
    block b = { x, y, xs, ys };
    switch(type)
    {
        case SV_EDITH: editheightxy(v!=0, getint(p), b); break;
        case SV_EDITT: edittexxy(v, getint(p), b); break;
        case SV_EDITS: edittypexy(v, b); break;
        case SV_EDITD: setvdeltaxy(v, b); break;
        case SV_EDITE: editequalisexy(v!=0, b); break;
    }
    break;
}
'''

common_edit_fields = (
        Field(name="x", type="int"),
        Field(name="y", type="int"),
        Field(name="xs", type="int"),
        Field(name="ys", type="int"),
        Field(name="v", type="int")
)

mt = MessageType("SV_EDITH",
        common_edit_fields+
        (Field(name="height", type="int"),))
sc.add_message_type(message_types.SV_EDITH, mt)

mt = MessageType("SV_EDITT",
        common_edit_fields+
        (Field(name="texture", type="int"),))
sc.add_message_type(message_types.SV_EDITT, mt)

mt = MessageType("SV_EDITS",
        *common_edit_fields)
sc.add_message_type(message_types.SV_EDITS, mt)

mt = MessageType("SV_EDITD",
        *common_edit_fields)
sc.add_message_type(message_types.SV_EDITD, mt)

mt = MessageType("SV_EDITE",
        *common_edit_fields)
sc.add_message_type(message_types.SV_EDITE, mt)

'''
case SV_NEWMAP:
{
    int size = getint(p);
    if(size>=0) empty_world(size, true);
    else empty_world(-1, true);
    if(d && d!=player1)
        conoutf(size>=0 ? _("%s started a new map of size %d") : _("%s enlarged the map to size %d"), colorname(d), sfactor);
    break;
}
'''

mt = MessageType("SV_NEWMAP",
        Field(name="size", type="int"))
sc.add_message_type(message_types.SV_NEWMAP, mt)

'''
case SV_EDITENT:            // coop edit of ent
{
    uint i = getint(p);
    while((uint)ents.length()<=i) ents.add().type = NOTUSED;
    int to = ents[i].type;
    ents[i].type = getint(p);
    ents[i].x = getint(p);
    ents[i].y = getint(p);
    ents[i].z = getint(p);
    ents[i].attr1 = getint(p);
    ents[i].attr2 = getint(p);
    ents[i].attr3 = getint(p);
    ents[i].attr4 = getint(p);
    ents[i].spawned = false;
    if(ents[i].type==LIGHT || to==LIGHT) calclight();
    if(ents[i].type==SOUND) audiomgr.preloadmapsound(ents[i]);
    break;
}
'''

mt = MessageType("SV_EDITENT",
        Field(name="entid", type="int"),
        Field(name="type", type="int"),
        Field(name="x", type="int"),
        Field(name="y", type="int"),
        Field(name="z", type="int"),
        Field(name="attr1", type="int"),
        Field(name="attr2", type="int"),
        Field(name="attr3", type="int"),
        Field(name="attr4", type="int"))
stream_spec.add_message_type(message_types.SV_EDITENT, mt)

'''
case SV_PONG:
{
    int millis = getint(p);
    addmsg(SV_CLIENTPING, "i", player1->ping = max(0, (player1->ping*5+totalmillis-millis)/6));
    break;
}
'''

mt = MessageType("SV_PONG",
        Field(name="millis", type="int"))
stream_spec.add_message_type(message_types.SV_PONG, mt)

'''
case SV_CLIENTPING:
    if(!d) return;
    d->ping = getint(p);
    break;
'''

mt = MessageType("SV_CLIENTPING",
        Field(name="ping", type="int"))
sc.add_message_type(message_types.SV_CLIENTPING, mt)

'''
case SV_GAMEMODE:
    nextmode = getint(p);
    if (nextmode >= GMODE_NUM) nextmode -= GMODE_NUM;
    break;
'''

mt = MessageType("SV_GAMEMODE",
        Field(name="nextmode", type="int"))
stream_spec.add_message_type(message_types.SV_GAMEMODE, mt)

'''
case SV_TIMEUP:
{
    int curgamemillis = getint(p);
    int curgamelimit = getint(p);
    timeupdate(curgamemillis, curgamelimit);
    break;
}
'''

mt = MessageType("SV_TIMEUP",
        Field(name="curmillis", type="int"),
        Field(name="curlimit", type="int"))
stream_spec.add_message_type(message_types.SV_TIMEUP, mt)

'''
case SV_WEAPCHANGE:
{
    int gun = getint(p);
    if(d) d->selectweapon(gun);
    break;
}
'''

mt = MessageType("SV_WEAPCHANGE",
        Field(name="gun", type="int"))
sc.add_message_type(message_types.SV_WEAPCHANGE, mt)

'''
case SV_SERVMSG:
    getstring(text, p);
    conoutf("%s", text);
    break;
'''

mt = MessageType("SV_SERVMSG",
        Field(name="text", type="string"))
stream_spec.add_message_type(message_types.SV_SERVMSG, mt)

'''
case SV_FLAGINFO:
{
    int flag = getint(p);
    if(flag<0 || flag>1) return;
    flaginfo &f = flaginfos[flag];
    f.state = getint(p);
    switch(f.state)
    {
        case CTFF_STOLEN:
            flagstolen(flag, getint(p));
            break;
        case CTFF_DROPPED:
        {
            float x = getuint(p)/DMF;
            float y = getuint(p)/DMF;
            float z = getuint(p)/DMF;
            flagdropped(flag, x, y, z);
            break;
        }
	    case CTFF_INBASE:
		    flaginbase(flag);
		    break;
	    case CTFF_IDLE:
		    flagidle(flag);
            break;
    }
    break;
}
'''

mt = MessageType("SV_FLAGINFO",
        Field(name="flag", type="int"),
        SwitchField(
            predicate=Field(type="int"), 
            cases=[
                CaseField(predicate_comparison = lambda v: v == flag_states.CTFF_STOLEN,
                          consequent=FieldCollection(
                                         Field(name="state", type="int"),
                                         Field(name="clientnum", type="int"))),
                CaseField(predicate_comparison = lambda v: v == flag_states.CTFF_DROPPED,
                          consequent=FieldCollection(
                                         Field(name="state", type="int"),
                                         Field(name="x", type="int"),
                                         Field(name="y", type="int"),
                                         Field(name="z", type="int")))
            ],
            default=FieldCollection(Field(name="state", type="int")),
            peek_predicate=True))
stream_spec.add_message_type(message_types.SV_FLAGINFO, mt)

'''
case SV_FLAGMSG:
{
    int flag = getint(p);
    int message = getint(p);
    int actor = getint(p);
    int flagtime = message == FM_KTFSCORE ? getint(p) : -1;
    flagmsg(flag, message, actor, flagtime);
    break;
}
'''

mt = MessageType("SV_FLAGMSG",
        Field(name="flag", type="int"),
        ConditionalFieldCollection(
            predicate=Field(type="int"), 
            predicate_comparison = lambda v: v == flag_messages.FM_KTFSCORE,
            consequent=FieldCollection(Field(name="message", type="int"),
                                       Field(name="actor", type="int"),
                                       Field(name="flagtime", type="int")),
            alternative=FieldCollection(Field(name="message", type="int"),
                                       Field(name="actor", type="int")),
            peek_predicate=True))
stream_spec.add_message_type(message_types.SV_FLAGMSG, mt)

'''
case SV_FLAGCNT:
{
    int fcn = getint(p);
    int flags = getint(p);
    playerent *p = (fcn == getclientnum() ? player1 : getclient(fcn));
    if(p) p->flagscore = flags;
    break;
}
'''

mt = MessageType("SV_FLAGCNT",
        Field(name="clientnum", type="int"),
        Field(name="flags", type="int"))
stream_spec.add_message_type(message_types.SV_FLAGCNT, mt)

'''
case SV_ARENAWIN:
{
    int acn = getint(p);
    playerent *alive = acn<0 ? NULL : (acn==getclientnum() ? player1 : getclient(acn));
    conoutf(_("the round is over! next round in 5 seconds..."));
    if(m_botmode && acn==-2) hudoutf(_("the bots have won the round!"));
    else if(!alive) hudoutf(_("everyone died!"));
    else if(m_teammode) hudoutf(_("team %s has won the round!"), team_string(alive->team));
    else if(alive==player1) hudoutf(_("you are the survivor!"));
    else hudoutf(_("%s is the survivor!"), colorname(alive));
    arenaintermission = lastmillis;
    break;
}
'''

mt = MessageType("SV_ARENAWIN",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_ARENAWIN, mt)

'''
case SV_SPAWNDENY:
{
    extern int spawnpermission;
    spawnpermission = getint(p);
    if(spawnpermission == SP_REFILLMATCH) hudoutf("\f3You can now spawn to refill your team.");
    break;
}
'''

mt = MessageType("SV_SPAWNDENY",
        Field(name="spawnpermission", type="int"))
stream_spec.add_message_type(message_types.SV_SPAWNDENY, mt)

'''
case SV_FORCEDEATH:
{
    int cn = getint(p);
    playerent *d = cn==getclientnum() ? player1 : newclient(cn);
    if(!d) break;
    deathstate(d);
    break;
}
'''

mt = MessageType("SV_FORCEDEATH",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_FORCEDEATH, mt)

'''
case SV_SERVOPINFO:
{
    loopv(players) { if(players[i]) players[i]->clientrole = CR_DEFAULT; }
    player1->clientrole = CR_DEFAULT;

    int cl = getint(p), r = getint(p);
    if(cl >= 0 && r >= 0)
    {
        playerent *pl = (cl == getclientnum() ? player1 : newclient(cl));
        if(pl)
        {
            pl->clientrole = r;
            if(pl->name[0])
            {
                // two messages required to allow for proper german translation - is there a better way to do it?
                if(pl==player1) conoutf(_("you claimed %s status"), r == CR_ADMIN ? "admin" : "master");
                else conoutf(_("%s claimed %s status"), colorname(pl), r == CR_ADMIN ? "admin" : "master");
            }
        }
    }
    break;
}
'''

mt = MessageType("SV_SERVOPINFO",
        Field(name="clientnum", type="int"),
        Field(name="role", type="int"))
stream_spec.add_message_type(message_types.SV_SERVOPINFO, mt)

'''
case SV_TEAMDENY:
{
    int t = getint(p);
    if(m_teammode)
    {
        if(team_isvalid(t)) conoutf(_("you can't change to team %s"), team_string(t));
    }
    else
    {
        conoutf(_("you can't change to %s mode"), team_isspect(t) ? _("spectate") : _("active"));
    }
    break;
}
'''

mt = MessageType("SV_TEAMDENY",
        Field(name="team", type="int"))
stream_spec.add_message_type(message_types.SV_TEAMDENY, mt)

'''
case SV_SETTEAM:
{
    int fpl = getint(p), fnt = getint(p), ftr = fnt >> 4;
    fnt &= 0x0f;
    playerent *d = (fpl == getclientnum() ? player1 : newclient(fpl));
    if(d)
    {
        const char *nts = team_string(fnt);
        bool you = fpl == player1->clientnum;
        if(m_teammode || team_isspect(fnt))
        {
            if(d->team == fnt)
            {
                if(you && ftr == FTR_AUTOTEAM) hudoutf("you stay in team %s", nts);
            }
            else
            {
                if(you && !watchingdemo)
                {
                    switch(ftr)
                    {
                        case FTR_PLAYERWISH:
                            conoutf(_("you're now in team %s"), nts);
                            break;
                        case FTR_AUTOTEAM:
                            hudoutf(_("the server forced you to team %s"), nts);
                            break;
                    }
                }
                else
                {
                    const char *pls = colorname(d);
                    bool et = team_base(player1->team) != team_base(fnt);
                    switch(ftr)
                    {
                        case FTR_PLAYERWISH:
                            conoutf(_("player %s switched to team %s"), pls, nts); // new message
                            break;
                        case FTR_AUTOTEAM:
                            if(watchingdemo) conoutf(_("the server forced %s to team %s"), colorname(d), nts);
                            else hudoutf(_("the server forced %s to %s team"), colorname(d), et ? _("the enemy") : _("your"));
                            break;
                    }
                }
                if(you && !team_isspect(d->team) && team_isspect(fnt) && d->state == CS_DEAD) spectate(SM_FLY);
            }
        }
        else if(d->team != fnt && ftr == FTR_PLAYERWISH) conoutf(_("%s changed to active play"), you ? _("you") : colorname(d));
        d->team = fnt;
    }
    break;
}
'''

mt = MessageType("SV_SETTEAM",
        Field(name="clientnum", type="int"),
        Field(name="fnt", type="int"))
stream_spec.add_message_type(message_types.SV_SETTEAM, mt)

'''
case SV_SERVERMODE:
{
    int sm = getint(p);
    servstate.autoteam = sm & 1;
    servstate.mastermode = (sm >> 2) & MM_MASK;
    servstate.matchteamsize = sm >> 4;
    //if(sm & AT_SHUFFLE) playsound(TEAMSHUFFLE);    // TODO
    break;
}
'''

mt = MessageType("SV_SERVERMODE",
        Field(name="servermode", type="int"))
stream_spec.add_message_type(message_types.SV_SERVERMODE, mt)

'''
case SV_CALLVOTE:
{
    int type = getint(p);
    int vcn = -1, n_yes = 0, n_no = 0;
    if ( type == -1 )
    {
        d = getclient(vcn = getint(p));
        n_yes = getint(p);
        n_no = getint(p);
        type = getint(p);
    }
    if (type == SA_MAP && d == NULL) d = player1;      // gonext uses this
    if( type < 0 || type >= SA_NUM || !d ) return;
    votedisplayinfo *v = NULL;
    string a;
    switch(type)
    {
        case SA_MAP:
            getstring(text, p);
            filtertext(text, text);
            itoa(a, getint(p));
            v = newvotedisplayinfo(d, type, text, a);
            break;
        case SA_KICK:
        case SA_BAN:
        {
            itoa(a, getint(p));
            getstring(text, p);
            filtertext(text, text);
            v = newvotedisplayinfo(d, type, a, text);
            break;
        }
        case SA_SERVERDESC:
            getstring(text, p);
            filtertext(text, text);
            v = newvotedisplayinfo(d, type, text, NULL);
            break;
        case SA_STOPDEMO:
        case SA_REMBANS:
        case SA_SHUFFLETEAMS:
            v = newvotedisplayinfo(d, type, NULL, NULL);
            break;
        default:
            itoa(a, getint(p));
            v = newvotedisplayinfo(d, type, a, NULL);
            break;
    }
    displayvote(v);
    if (vcn >= 0)
    {
        loopi(n_yes) votecount(VOTE_YES);
        loopi(n_no) votecount(VOTE_NO);
    }
    extern int vote(int);
    if (d == player1) vote(VOTE_YES);
    break;
}
'''

def read_call_vote_message(stream_object, type_method_mapping, game_state):
    """Returns a dictionary containing the message fields."""
    message = {}
    
    vtype = stream_object.getint()
    vcn = -1
    n_yes = 0
    n_no = 0;
    if vtype == -1:
        vcn = stream_object.getint()
        y_count = stream_object.getint()
        n_count = stream_object.getint()
        vtype = stream_object.getint()
        
    message['vcn'] = vcn
    message['y_count'] = y_count
    message['n_count'] = n_count
    message['vote_type'] = vtype
    
    if vtype == vote_types.SA_MAP:
        message['map_name'] = stream_object.getstring()
        message['mode'] = stream_object.getint()
    elif vtype in (vote_types.SA_KICK, vote_types.SA_BAN):
        message['clientnum'] = stream_object.getint()
        message['reason'] = stream_object.getstring()
    elif vtype == vote_types.SA_SERVERDESC:
        message['desc'] = stream_object.getstring()
    elif vtype in (vote_types.SA_STOPDEMO, vote_types.SA_REMBANS, vote_types.SA_SHUFFLETEAMS):
        pass
    else:
        message['arg'] = stream_object.getint()
        
    return message
    
mt = CustomMessageType("SV_CALLVOTE", read_call_vote_message)
stream_spec.add_message_type(message_types.SV_CALLVOTE, mt)

'''
case SV_CALLVOTESUC:
    callvotesuc();
    break;
'''

mt = MessageType("SV_CALLVOTESUC")
stream_spec.add_message_type(message_types.SV_CALLVOTESUC, mt)

'''
case SV_CALLVOTEERR:
    callvoteerr(getint(p));
    break;
'''

mt = MessageType("SV_CALLVOTEERR",
        Field(name="error", type="int"))
stream_spec.add_message_type(message_types.SV_CALLVOTEERR, mt)

'''
case SV_VOTE:
    votecount(getint(p));
    break;
'''

mt = MessageType("SV_VOTE",
        Field(name="count", type="int"))
stream_spec.add_message_type(message_types.SV_VOTE, mt)

'''
case SV_VOTERESULT:
    voteresult(getint(p));
    break;
'''

mt = MessageType("SV_VOTERESULT",
        Field(name="result", type="int"))
stream_spec.add_message_type(message_types.SV_VOTERESULT, mt)

'''
case SV_WHOISINFO:
{
    int cn = getint(p);
    playerent *pl = cn == getclientnum() ? player1 : getclient(cn);
    int ip = getint(p);
    if((ip>>24&0xFF) > 0 || player1->clientrole==CR_ADMIN) conoutf("WHOIS %2d: %-16s\t%d.%d.%d.%d", cn, pl ? colorname(pl) : "", ip&0xFF, ip>>8&0xFF, ip>>16&0xFF, ip>>24&0xFF); // full IP
    else conoutf("WHOIS client %d:\n\f5name\t%s\n\f5IP\t%d.%d.%d.x", cn, pl ? colorname(pl) : "", ip&0xFF, ip>>8&0xFF, ip>>16&0xFF); // censored IP
    break;
}
'''

mt = MessageType("SV_WHOISINFO",
        Field(name="clientnum", type="int"),
        Field(name="ip", type="int"))
stream_spec.add_message_type(message_types.SV_WHOISINFO, mt)

'''
case SV_SENDDEMOLIST:
{
    int demos = getint(p);
    if(!demos) conoutf(_("no demos available"));
    else loopi(demos)
    {
        getstring(text, p);
        conoutf("%d. %s", i+1, text); // i18n for this?? there's tons of other strings that NEED it, not this. (said flowtron: 2010jul13)
    }
    break;
}
'''

mt = MessageType("SV_SENDDEMOLIST",
        IteratedFieldCollection(
            name="demos",
            count=Field(type="int"),
            field_collection=Field(name="name", type="string")))
sc.add_message_type(message_types.SV_SENDDEMOLIST, mt)

'''
case SV_DEMOPLAYBACK:
{
    watchingdemo = demoplayback = getint(p)!=0;
    if(demoplayback)
    {
        player1->resetspec();
        player1->state = CS_SPECTATE;
    }
    else
    {
        // cleanups
        loopv(players) zapplayer(players[i]);
        clearvote();
        player1->state = CS_ALIVE;
        player1->resetspec();
    }
    player1->clientnum = getint(p);
    break;
}
'''

mt = MessageType("SV_DEMOPLAYBACK",
        Field(name="on", type="int"),
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.SV_DEMOPLAYBACK, mt)


