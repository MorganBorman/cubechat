from CubeDataStream import CubeDataStream

type_method_mapping = {
                            'stream_data': CubeDataStream.read,
                            'int': CubeDataStream.getint, 
                            'uint': CubeDataStream.getuint,
                            'string': CubeDataStream.getstring, 
                            'float': CubeDataStream.getfloat
                        }

from StreamSpecification import Field, FieldCollection, IteratedFieldCollection, TerminatedFieldCollection
from StreamSpecification import ConditionalFieldCollection, StateDependent as SD, SwitchField, CaseField, GameStateField
from StreamSpecification import MessageType, StreamStateModifierType, StreamSpecification
from StreamSpecification import StreamContainerType, RawField

stream_spec = StreamSpecification(CubeDataStream, type_method_mapping, {}, "int")

from .constants import message_types, physics_events, W_MAX, m_capture, m_bomber, m_defend

"""
case N_SERVERINIT:                 // welcome messsage from the server
{
    int mycn = getint(p), gver = getint(p);
    if(gver!=GAMEVERSION)
    {
        conoutft(CON_MESG, "\fryou are using a different game version (you: \fs\fc%d\fS, server: \fs\fc%d\fS)", GAMEVERSION, gver);
        disconnect();
        return;
    }
    getstring(game::player1->hostname, p);
    if(!game::player1->hostname[0]) copystring(game::player1->hostname, "unknown");
    sessionid = getint(p);
    game::player1->clientnum = mycn;
    if(getint(p)) conoutft(CON_MESG, "\fothe server is password protected");
    else if(verbose >= 2) conoutf("\fythe server welcomes us, yay");
    sendintro();
    break;
}
"""

mt = MessageType("N_SERVERINIT",
        Field(name="clientnum", type="int"), 
        Field(name="protocol_version", type="int"),
        Field(name="hostname", type="string"),
        Field(name="sessionid", type="int"),
        Field(name="haspwd", type="int"))
stream_spec.add_message_type(message_types.N_SERVERINIT, mt)

"""
case N_WELCOME: isready = true; break;
"""

mt = MessageType("N_WELCOME")
stream_spec.add_message_type(message_types.N_WELCOME, mt)

"""
case N_CLIENT:
{
    int lcn = getint(p), len = getuint(p);
    ucharbuf q = p.subbuf(len);
    gameent *t = game::getclient(lcn);
    parsemessages(lcn, t, q);
    break;
}
"""

sc = StreamContainerType(CubeDataStream, type_method_mapping, {}, "int", FieldCollection(Field(name="clientnum", type="int")), Field(type="uint"))
stream_spec.add_container_type(message_types.N_CLIENT, sc)

"""
case N_SPHY: // simple phys events
{
    int lcn = getint(p), st = getint(p), param = 0;
    gameent *t = game::getclient(lcn);
    if(t && (st == SPHY_EXTINGUISH || st == SPHY_BUFF || (t != game::player1 && !t->ai))) switch(st)
    {
        case SPHY_JUMP:
        {
            t->resetphys();
            t->impulse[IM_JUMP] = lastmillis;
            playsound(S_JUMP, t->o, t);
            regularshape(PART_SMOKE, int(t->radius), 0x222222, 21, 20, 250, t->feetpos(), 1, 1, -10, 0, 10.f);
            break;
        }
        case SPHY_BOOST: case SPHY_KICK: case SPHY_VAULT: case SPHY_SKATE: case SPHY_DASH: case SPHY_MELEE:
        {
            t->doimpulse(0, IM_T_BOOST+(st-SPHY_BOOST), lastmillis);
            game::impulseeffect(t);
            break;
        }
        case SPHY_POWER: param = getint(p); t->setweapstate(t->weapselect, W_S_POWER, param, lastmillis); break;
        case SPHY_EXTINGUISH:
        {
            t->resetburning();
            playsound(S_EXTINGUISH, t->o, t);
            part_create(PART_SMOKE, 500, t->feetpos(t->height/2), 0xAAAAAA, t->radius*4, 1, -10);
            break;
        }
        case SPHY_BUFF: param = getint(p); t->lastbuff = param ? lastmillis : 0; break;
        default: break;
    }
    break;
}
"""

mt = MessageType("N_SPHY",
        Field(name="clientnum", type="int"), 
        SwitchField(
            predicate=Field(type="int"), 
            cases=[
                CaseField(predicate_comparison = lambda v: v in (physics_events.SPHY_POWER, physics_events.SPHY_BUFF),
                          consequent=FieldCollection(
                                         Field(name="event_type", type="int"),
                                         Field(name="param", type="int")))
            ],
            default=FieldCollection(Field(name="event_type", type="int")),
            peek_predicate=True))
stream_spec.add_message_type(message_types.N_SPHY, mt)
sc.add_message_type(message_types.N_SPHY, mt)

"""
case N_ANNOUNCE:
{
    int snd = getint(p), targ = getint(p);
    getstring(text, p);
    if(targ >= 0 && text[0]) game::announcef(snd, targ, NULL, false, "%s", text);
    else game::announce(snd);
    break;
}
"""

mt = MessageType("N_ANNOUNCE",
        Field(name="sound", type="int"), 
        Field(name="target", type="int"),
        Field(name="message", type="string"))
stream_spec.add_message_type(message_types.N_ANNOUNCE, mt)

"""
case N_TEXT:
{
    int tcn = getint(p);
    gameent *t = game::getclient(tcn);
    int flags = getint(p);
    getstring(text, p);
    if(!t || isignored(t->clientnum) || isignored(t->ownernum)) break;
    saytext(t, flags, text);
    break;
}
"""

mt = MessageType("N_TEXT",
        Field(name="clientnum", type="int"), 
        Field(name="flags", type="int"),
        Field(name="message", type="string"))
stream_spec.add_message_type(message_types.N_TEXT, mt)

"""
case N_COMMAND:
{
    int lcn = getint(p);
    gameent *f = lcn >= 0 ? game::getclient(lcn) : NULL;
    getstring(text, p);
    int alen = getint(p);
    if(alen < 0 || alen > p.remaining()) break;
    char *arg = newstring(alen);
    getstring(arg, p, alen+1);
    parsecommand(f, text, arg);
    delete[] arg;
    break;
}
"""

mt = MessageType("N_COMMAND",
        Field(name="clientnum", type="int"),
        Field(name="command", type="string"), 
        ConditionalFieldCollection(
            predicate=Field(type="int"), 
            predicate_comparison = lambda v: v >= 0,
            consequent=FieldCollection(Field(name="args", type="string")),
            peek_predicate=False))
stream_spec.add_message_type(message_types.N_COMMAND, mt)

"""
case N_EXECLINK: (N_CLIENT)
{
    int tcn = getint(p), index = getint(p);
    gameent *t = game::getclient(tcn);
    if(!t || !d || (t->clientnum != d->clientnum && t->ownernum != d->clientnum) || t == game::player1 || t->ai) break;
    entities::execlink(t, index, false);
    break;
}
"""

mt = MessageType("N_EXECLINK",
        Field(name="target", type="int"),
        Field(name="index", type="int"))
sc.add_message_type(message_types.N_EXECLINK, mt)

"""
case N_MAPCHANGE:
{
    getstring(text, p);
    int getit = getint(p), mode = getint(p), muts = getint(p);
    changemapserv(getit != 1 ? text : NULL, mode, muts, getit == 2);
    if(needsmap) switch(getit)
    {
        case 0: case 2:
        {
            conoutft(CON_MESG, "\fyserver requested map change to \fs\fc%s\fS, and we need it, so asking for it", text);
            addmsg(N_GETMAP, "r");
            break;
        }
        case 1:
        {
            conoutft(CON_MESG, "\fyserver is requesting the map from another client for us");
            break;
        }
        default: needsmap = false; break;
    }
    break;
}
"""

mt = MessageType("N_MAPCHANGE",
        Field(name="map", type="string"),
        Field(name="getit", type="int"), 
        GameStateField(name="gamemode", type="int"), 
        Field(name="muts", type="int"))
stream_spec.add_message_type(message_types.N_MAPCHANGE, mt)

"""
case N_GAMEINFO:
{
    int n;
    while((n = getint(p)) != -1) entities::setspawn(n, getint(p));
    sendgameinfo = false;
    break;
}
"""

mt = MessageType("N_GAMEINFO",
        TerminatedFieldCollection(name="items",
            terminator_field=Field(type="int"),
            terminator_comparison=lambda t: t != -1,
            field_collection=FieldCollection(
                                         Field(name="item_index", type="int"),
                                         Field(name="item_type", type="int"))))
stream_spec.add_message_type(message_types.N_GAMEINFO, mt)

"""
case N_NEWGAME: // server requests next game
{
    hud::showscores(false);
    if(!menuactive()) showgui("maps", 1);
    if(game::intermission) hud::lastnewgame = totalmillis;
    break;
}
"""

mt = MessageType("N_NEWGAME")
stream_spec.add_message_type(message_types.N_NEWGAME, mt)

"""
case N_SETPLAYERINFO: (N_CLIENT)
{
    getstring(text, p);
    int colour = getint(p), model = getint(p);
    string vanity;
    getstring(vanity, p);
    if(!d) break;
    filtertext(text, text, true, true, true, MAXNAMELEN);
    const char *namestr = text;
    while(*namestr && iscubespace(*namestr)) namestr++;
    if(!*namestr) namestr = copystring(text, "unnamed");
    if(strcmp(d->name, namestr))
    {
        string oldname, newname;
        copystring(oldname, game::colourname(d));
        d->setinfo(namestr, colour, model, vanity);
        copystring(newname, game::colourname(d));
        if(showpresence >= (waiting(false) ? 2 : 1) && !isignored(d->clientnum))
            conoutft(CON_EVENT, "\fm%s is now known as %s", oldname, newname);
    }
    else d->setinfo(namestr, colour, model, vanity);
    break;
}
"""

mt = MessageType("N_SETPLAYERINFO",
        Field(name="name", type="string"),
        Field(name="color", type="int"),
        Field(name="model", type="int"),
        Field(name="vanity", type="string"))
sc.add_message_type(message_types.N_SETPLAYERINFO, mt)

"""
case N_CLIENTINIT: // another client either connected or changed name/team
{
    int cn = getint(p);
    gameent *d = game::newclient(cn);
    if(!d)
    {
        loopi(4) getint(p);
        loopi(4) getstring(text, p);
        break;
    }
    int colour = getint(p), model = getint(p), team = clamp(getint(p), int(T_NEUTRAL), int(T_ENEMY)), priv = getint(p);
    string name;
    getstring(name, p);
    filtertext(name, name, true, true, true, MAXNAMELEN);
    const char *namestr = name;
    while(*namestr && iscubespace(*namestr)) namestr++;
    if(!*namestr) namestr = copystring(name, "unnamed");
    getstring(d->hostname, p);
    if(!d->hostname[0]) copystring(d->hostname, "unknown");
    getstring(d->handle, p);
    getstring(text, p);
    if(d == game::focus && d->team != team) hud::lastteam = 0;
    d->team = team;
    d->privilege = priv;
    if(d->name[0]) d->setinfo(namestr, colour, model, text); // already connected
    else // new client
    {
        d->setinfo(namestr, colour, model, text);
        if(showpresence >= (waiting(false) ? 2 : 1))
        {
            if(priv > PRIV_NONE)
            {
                if(d->handle[0]) conoutft(CON_EVENT, "\fg%s (%s) has joined the game (\fs\fy%s\fS: \fs\fc%s\fS)", game::colourname(d), d->hostname, hud::privname(d->privilege), d->handle);
                else conoutft(CON_EVENT, "\fg%s (%s) has joined the game (\fs\fylocal %s\fS)", game::colourname(d), d->hostname, hud::privname(d->privilege));
            }
            else conoutft(CON_EVENT, "\fg%s (%s) has joined the game", game::colourname(d), d->hostname);
        }
        if(needclipboard >= 0) needclipboard++;
        game::specreset(d);
    }
    break;
}
"""

mt = MessageType("N_CLIENTINIT",
        Field(name="clientnum", type="int"), 
        Field(name="color", type="int"), 
        Field(name="model", type="int"), 
        Field(name="team", type="int"), 
        Field(name="priv", type="int"), 
        Field(name="name", type="string"), 
        Field(name="hostname", type="string"), 
        Field(name="handle", type="string"), 
        Field(name="vanity", type="string"))
stream_spec.add_message_type(message_types.N_CLIENTINIT, mt)

"""
case N_DISCONNECT:
{
    int lcn = getint(p), reason = getint(p);
    game::clientdisconnected(lcn, reason);
    break;
}
"""

mt = MessageType("N_DISCONNECT",
        Field(name="clientnum", type="int"), 
        Field(name="reason", type="int"))
stream_spec.add_message_type(message_types.N_DISCONNECT, mt)

"""
case N_LOADW:
{
    hud::showscores(false);
    game::player1->loadweap.shrink(0);
    if(!menuactive()) showgui("loadout", -1);
    break;
}
"""

mt = MessageType("N_LOADW")
stream_spec.add_message_type(message_types.N_LOADW, mt)

"""
case N_SPAWN:
{
    int lcn = getint(p);
    gameent *f = game::newclient(lcn);
    if(!f || f == game::player1 || f->ai)
    {
        parsestate(NULL, p);
        break;
    }
    f->respawn(lastmillis);
    parsestate(f, p);
    break;
}

    void parsestate(gameent *d, ucharbuf &p, bool resume = false)
    {
        if(!d) { static gameent dummy; d = &dummy; }
        if(d == game::player1 || d->ai) getint(p);
        else d->state = getint(p);
        d->points = getint(p);
        d->frags = getint(p);
        d->deaths = getint(p);
        d->health = getint(p);
        d->armour = getint(p);
        d->cptime = getint(p);
        d->cplaps = getint(p);
        if(resume && (d == game::player1 || d->ai))
        {
            d->weapreset(false);
            getint(p);
            loopi(W_MAX) getint(p);
            loopi(W_MAX) getint(p);
        }
        else
        {
            d->weapreset(true);
            int weap = getint(p);
            d->lastweap = d->weapselect = isweap(weap) ? weap : W_MELEE;
            loopi(W_MAX) d->ammo[i] = getint(p);
            loopi(W_MAX) d->reloads[i] = getint(p);
        }
    }
"""

state_fields = (
    Field(name="state", type="int"),
    Field(name="points", type="int"),
    Field(name="frags", type="int"),
    Field(name="deaths", type="int"),
    Field(name="health", type="int"),
    Field(name="armour", type="int"),
    Field(name="ctime", type="int"),
    Field(name="claps", type="int"),
    Field(name="gunselect", type="int"),
    IteratedFieldCollection(
        name="ammo",
        count=W_MAX,
        field_collection=FieldCollection(Field(name="amount", type="int"))),
    IteratedFieldCollection(
        name="reloads",
        count=W_MAX,
        field_collection=FieldCollection(Field(name="amount", type="int")))
)

mt = MessageType("N_SPAWN",
        Field(name="clientnum", type="int"),
        *state_fields
        )
stream_spec.add_message_type(message_types.N_SPAWN, mt)
sc.add_message_type(message_types.N_SPAWN, mt)

"""
case N_SPAWNSTATE:
{
    int lcn = getint(p), ent = getint(p);
    gameent *f = game::newclient(lcn);
    if(!f || (f != game::player1 && !f->ai))
    {
        parsestate(NULL, p);
        break;
    }
    if(f == game::player1 && editmode) toggleedit();
    f->respawn(lastmillis);
    parsestate(f, p);
    game::respawned(f, true, ent);
    break;
}
"""

mt = MessageType("N_SPAWNSTATE",
        Field(name="clientnum", type="int"),
        Field(name="entity", type="int"),
        *state_fields
        )
stream_spec.add_message_type(message_types.N_SPAWNSTATE, mt)

"""
case N_SHOTFX:
{
    int scn = getint(p), weap = getint(p), flags = getint(p), len = getint(p);
    vec from;
    loopk(3) from[k] = getint(p)/DMF;
    int ls = getint(p);
    vector<shotmsg> shots;
    loopj(ls)
    {
        shotmsg &s = shots.add();
        s.id = getint(p);
        loopk(3) s.pos[k] = getint(p);
    }
    gameent *t = game::getclient(scn);
    if(!t || !isweap(weap) || t == game::player1 || t->ai) break;
    if(weap != t->weapselect && weap != W_MELEE) t->weapswitch(weap, lastmillis);
    float scale = 1;
    int sub = W2(weap, sub, WS(flags));
    if(W2(weap, power, WS(flags)))
    {
        scale = len/float(W2(weap, power, WS(flags)));
        if(sub > 1) sub = int(ceilf(sub*scale));
    }
    projs::shootv(weap, flags, sub, 0, scale, from, shots, t, false);
    break;
}
"""

mt = MessageType("N_SHOTFX",
        Field(name="clientnum", type="int"),
        Field(name="weapon", type="int"),
        Field(name="flags", type="int"),
        Field(name="len", type="int"),
        
        Field(name="fx", type="int"),
        Field(name="fy", type="int"),
        Field(name="fz", type="int"),
        
        IteratedFieldCollection(
            name="rays",
            count=Field(type="int"),
            field_collection=FieldCollection(
                Field(name="id", type="int"),
                Field(name="tx", type="int"),
                Field(name="ty", type="int"),
                Field(name="tz", type="int")
            )
        )
)
stream_spec.add_message_type(message_types.N_SHOTFX, mt)

"""
case N_DESTROY:
{
    int scn = getint(p), num = getint(p);
    gameent *t = game::getclient(scn);
    loopi(num)
    {
        int id = getint(p);
        if(t) projs::destruct(t, id);
    }
    break;
}
"""

mt = MessageType("N_DESTROY",
        Field(name="clientnum", type="int"), 
        IteratedFieldCollection(
            name="entities",
            count=Field(type="int"),
            field_collection=FieldCollection(Field(name='id', type="int"))))
stream_spec.add_message_type(message_types.N_DESTROY, mt)

"""
case N_STICKY: // cn target id norm pos
{
    int scn = getint(p), tcn = getint(p), id = getint(p);
    vec norm(0, 0, 0), pos(0, 0, 0);
    loopk(3) norm[k] = getint(p)/DNF;
    loopk(3) pos[k] = getint(p)/DMF;
    gameent *t = game::getclient(scn), *v = tcn >= 0 ? game::getclient(tcn) : NULL;
    if(t && (tcn < 0 || v)) projs::sticky(t, id, norm, pos, v);
    break;
}
"""

mt = MessageType("N_STICKY",
        Field(name="clientnum", type="int"),
        Field(name="target", type="int"),
        Field(name="id", type="int"),
        Field(name="nx", type="int"),
        Field(name="ny", type="int"),
        Field(name="nz", type="int"),
        Field(name="px", type="int"),
        Field(name="py", type="int"),
        Field(name="pz", type="int"))
stream_spec.add_message_type(message_types.N_STICKY, mt)

"""
case N_DAMAGE:
{
    int tcn = getint(p), acn = getint(p), weap = getint(p), flags = getint(p), damage = getint(p),
        health = getint(p), armour = getint(p);
    vec dir;
    loopk(3) dir[k] = getint(p)/DNF;
    dir.normalize();
    gameent *target = game::getclient(tcn), *actor = game::getclient(acn);
    if(!target || !actor) break;
    game::damaged(weap, flags, damage, health, armour, target, actor, lastmillis, dir);
    break;
}
"""

mt = MessageType("N_DAMAGE",
        Field(name="clientnum", type="int"),
        Field(name="aggressor", type="int"),
        Field(name="weapon", type="int"),
        Field(name="flags", type="int"),
        Field(name="damage", type="int"),
        Field(name="health", type="int"),
        Field(name="armour", type="int"),
        Field(name="dx", type="int"),
        Field(name="dy", type="int"),
        Field(name="dz", type="int"))
stream_spec.add_message_type(message_types.N_DAMAGE, mt)

"""
case N_RELOAD:
{
    int trg = getint(p), weap = getint(p), amt = getint(p), ammo = getint(p), reloads = getint(p);
    gameent *target = game::getclient(trg);
    if(!target || !isweap(weap)) break;
    weapons::weapreload(target, weap, amt, ammo, reloads, false);
    break;
}
"""

mt = MessageType("N_RELOAD",
        Field(name="clientnum", type="int"),
        Field(name="weapon", type="int"),
        Field(name="amount", type="int"),
        Field(name="ammo", type="int"),
        Field(name="reloads", type="int"))
stream_spec.add_message_type(message_types.N_RELOAD, mt)

"""
case N_REGEN:
{
    int trg = getint(p), heal = getint(p), amt = getint(p), armour = getint(p);
    gameent *f = game::getclient(trg);
    if(!f) break;
    if(!amt)
    {
        f->impulse[IM_METER] = 0;
        f->resetresidual();
    }
    else if(amt > 0 && (!f->lastregen || lastmillis-f->lastregen >= 500)) playsound(S_REGEN, f->o, f);
    f->health = heal;
    f->armour = armour;
    f->lastregen = lastmillis;
    break;
}
"""

mt = MessageType("N_REGEN",
        Field(name="clientnum", type="int"),
        Field(name="heal", type="int"),
        Field(name="amount", type="int"),
        Field(name="armour", type="int"))
stream_spec.add_message_type(message_types.N_REGEN, mt)

"""
case N_DIED:
{
    int vcn = getint(p), deaths = getint(p), acn = getint(p), frags = getint(p), spree = getint(p), style = getint(p), weap = getint(p), flags = getint(p), damage = getint(p), material = getint(p);
    gameent *victim = game::getclient(vcn), *actor = game::getclient(acn);
    static vector<gameent *> assist; assist.setsize(0);
    int count = getint(p);
    loopi(count)
    {
        int lcn = getint(p);
        gameent *log = game::getclient(lcn);
        if(log) assist.add(log);
    }
    if(!actor || !victim) break;
    victim->deaths = deaths;
    actor->frags = frags;
    actor->spree = spree;
    game::killed(weap, flags, damage, victim, actor, assist, style, material);
    victim->lastdeath = lastmillis;
    victim->weapreset(true);
    break;
}
"""

mt = MessageType("N_DIED",
        Field(name="clientnum", type="int"),
        Field(name="deaths", type="int"),
        Field(name="killer", type="int"),
        Field(name="frags", type="int"),
        Field(name="spree", type="int"),
        Field(name="style", type="int"),
        Field(name="weapon", type="int"),
        Field(name="flags", type="int"),
        Field(name="damage", type="int"),
        Field(name="material", type="int"),
        IteratedFieldCollection(
            name="assists",
            count=Field(type="int"),
            field_collection=Field(name="cn", type="int")))
stream_spec.add_message_type(message_types.N_DIED, mt)

"""
case N_POINTS:
{
    int acn = getint(p), add = getint(p), points = getint(p);
    gameent *actor = game::getclient(acn);
    if(!actor) break;
    actor->lastpoints = add;
    actor->points = points;
    break;
}
"""

mt = MessageType("N_POINTS",
        Field(name="clientnum", type="int"),
        Field(name="add", type="int"),
        Field(name="points", type="int"))
stream_spec.add_message_type(message_types.N_POINTS, mt)

"""
case N_DROP:
{
    int trg = getint(p), weap = getint(p), ds = getint(p);
    gameent *target = game::getclient(trg);
    bool local = target && (target == game::player1 || target->ai);
    if(ds) loopj(ds)
    {
        int gs = getint(p), drop = getint(p), ammo = getint(p), reloads = getint(p);
        if(target) projs::drop(target, gs, drop, ammo, reloads, local, j, weap);
    }
    if(isweap(weap) && target)
    {
        target->weapswitch(weap, lastmillis, weaponswitchdelay);
        playsound(WSND(weap, S_W_SWITCH), target->o, target, 0, -1, -1, -1, &target->wschan);
    }
    break;
}
"""

mt = MessageType("N_DROP",
        Field(name="clientnum", type="int"),
        Field(name="weapon", type="int"),
        IteratedFieldCollection(
            name="drops",
            count=Field(type="int"),
            field_collection=FieldCollection(Field(name="gs", type="int"),
                                             Field(name="drop", type="int"),
                                             Field(name="ammo", type="int"),
                                             Field(name="reloads", type="int"))))
stream_spec.add_message_type(message_types.N_DROP, mt)

"""
case N_WSELECT:
{
    int trg = getint(p), weap = getint(p);
    gameent *target = game::getclient(trg);
    if(!target || !isweap(weap)) break;
    weapons::weapselect(target, weap, G(weaponinterrupts), false);
    break;
}
"""

mt = MessageType("N_WSELECT",
        Field(name="clientnum", type="int"),
        Field(name="weapon", type="int"))
stream_spec.add_message_type(message_types.N_WSELECT, mt)

"""
case N_RESUME:
{
    for(;;)
    {
        int lcn = getint(p);
        if(p.overread() || lcn < 0) break;
        gameent *f = game::newclient(lcn);
        if(f && f!=game::player1 && !f->ai) f->respawn();
        parsestate(f, p, true);
        f->setscale(game::rescale(f), 0, true, game::gamemode, game::mutators);
    }
    break;
}
"""

mt = MessageType("N_RESUME",
        TerminatedFieldCollection(name="clients",
            terminator_field=Field(type="int"),
            terminator_comparison=lambda t: t >= 0,
            field_collection=FieldCollection(
                Field(name="clientnum", type="int"),
                *state_fields
            )))
stream_spec.add_message_type(message_types.N_RESUME, mt)

"""
case N_ITEMSPAWN:
{
    int ent = getint(p), value = getint(p);
    if(!entities::ents.inrange(ent)) break;
    gameentity &e = *(gameentity *)entities::ents[ent];
    entities::setspawn(ent, value);
    ai::itemspawned(ent, value!=0);
    if(e.spawned)
    {
        int sweap = m_weapon(game::gamemode, game::mutators), attr = e.type == WEAPON ? w_attr(game::gamemode, game::mutators, e.attrs[0], sweap) : e.attrs[0],
            colour = e.type == WEAPON ? W(attr, colour) : 0xFFFFFF;
        playsound(e.type == WEAPON && attr >= W_OFFSET ? WSND(attr, S_W_SPAWN) : S_ITEMSPAWN, e.o);
        if(entities::showentdescs)
        {
            vec pos = vec(e.o).add(vec(0, 0, 4));
            const char *texname = entities::showentdescs >= 2 ? hud::itemtex(e.type, attr) : NULL;
            if(texname && *texname) part_icon(pos, textureload(texname, 3), game::aboveitemiconsize, 1, -10, 0, game::eventiconfade, colour);
            else
            {
                const char *item = entities::entinfo(e.type, e.attrs, 0);
                if(item && *item)
                {
                    defformatstring(ds)("<emphasis>%s", item);
                    part_textcopy(pos, ds, PART_TEXT, game::eventiconfade, 0xFFFFFF, 2, 1, -10);
                }
            }
        }
        regularshape(PART_SPARK, enttype[e.type].radius*1.5f, colour, 53, 50, 350, e.o, 1.5f, 1, 1, 0, 35);
        if(game::dynlighteffects)
            adddynlight(e.o, enttype[e.type].radius*2, vec::hexcolor(colour).mul(2.f), 250, 250);
    }
    break;
}
"""

mt = MessageType("N_ITEMSPAWN",
        Field(name="entity", type="int"),
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.N_ITEMSPAWN, mt)

"""
case N_TRIGGER:
{
    int ent = getint(p), st = getint(p);
    entities::setspawn(ent, st);
    break;
}
"""

mt = MessageType("N_TRIGGER",
        Field(name="entity", type="int"),
        Field(name="m", type="int"))
stream_spec.add_message_type(message_types.N_TRIGGER, mt)

"""
case N_ITEMACC:
{ // uses a specific drop so the client knows what to replace
    int lcn = getint(p), ent = getint(p), ammoamt = getint(p), reloadamt = getint(p), spawn = getint(p),
        weap = getint(p), drop = getint(p), ammo = getint(p), reloads = getint(p);
    gameent *target = game::getclient(lcn);
    if(!target) break;
    if(entities::ents.inrange(ent) && enttype[entities::ents[ent]->type].usetype == EU_ITEM)
        entities::useeffects(target, ent, ammoamt, reloadamt, spawn, weap, drop, ammo, reloads);
    break;
}
"""

mt = MessageType("N_ITEMACC",
        Field(name="clientnum", type="int"),
        Field(name="entity", type="int"),
        Field(name="ammo_amount", type="int"),
        Field(name="reload_amount", type="int"),
        Field(name="spawn", type="int"),
        Field(name="weapon", type="int"),
        Field(name="drop", type="int"),
        Field(name="ammo", type="int"),
        Field(name="reloads", type="int"))
stream_spec.add_message_type(message_types.N_ITEMACC, mt)

"""
case N_EDITVAR: (N_CLIENT)
{
    int t = getint(p);
    bool commit = true;
    getstring(text, p);
    ident *id = idents.access(text);
    if(!d || !id || !(id->flags&IDF_WORLD) || id->type != t) commit = false;
    switch(t)
    {
        case ID_VAR:
        {
            int val = getint(p);
            if(commit)
            {
                if(val > id->maxval) val = id->maxval;
                else if(val < id->minval) val = id->minval;
                setvar(text, val, true);
                conoutft(CON_EVENT, "\fy%s set worldvar \fs\fc%s\fS to \fs\fc%s\fS", game::colourname(d), id->name, intstr(id));
            }
            break;
        }
        case ID_FVAR:
        {
            float val = getfloat(p);
            if(commit)
            {
                if(val > id->maxvalf) val = id->maxvalf;
                else if(val < id->minvalf) val = id->minvalf;
                setfvar(text, val, true);
                conoutft(CON_EVENT, "\fy%s set worldvar \fs\fc%s\fS to \fs\fc%s\fS", game::colourname(d), id->name, floatstr(*id->storage.f));
            }
            break;
        }
        case ID_SVAR:
        {
            int vlen = getint(p);
            if(vlen < 0 || vlen > p.remaining()) break;
            char *val = newstring(vlen);
            getstring(val, p, vlen+1);
            if(commit)
            {
                setsvar(text, val, true);
                conoutft(CON_EVENT, "\fy%s set worldvar \fs\fc%s\fS to \fy\fc%s\fS", game::colourname(d), id->name, *id->storage.s);
            }
            delete[] val;
            break;
        }
        case ID_ALIAS:
        {
            int vlen = getint(p);
            if(vlen < 0 || vlen > p.remaining()) break;
            char *val = newstring(vlen);
            getstring(val, p, vlen+1);
            if(commit || !id) // set aliases anyway
            {
                worldalias(text, val);
                conoutft(CON_EVENT, "\fy%s set worldalias \fs\fc%s\fS to \fs\fc%s\fS", game::colourname(d), text, val);
            }
            delete[] val;
            break;
        }
        default: break;
    }
    break;
}
"""

mt = MessageType("N_EDITVAR",
        SwitchField(
            predicate=Field(type="int"), 
            cases=[
                CaseField(predicate_comparison = lambda v: v == var_types.ID_VAR,
                          consequent=FieldCollection(
                                         Field(name="variable", type="string"),
                                         Field(name="value", type="int"))),
                CaseField(predicate_comparison = lambda v: v == var_types.ID_FVAR,
                          consequent=FieldCollection(
                                         Field(name="variable", type="string"),
                                         Field(name="value", type="float"))),
                CaseField(predicate_comparison = lambda v: v == var_types.ID_SVAR,
                          consequent=FieldCollection(
                                         Field(name="variable", type="string"),
                                         Field(name="vlen", type="int"),
                                         Field(name="value", type="string"))),
                CaseField(predicate_comparison = lambda v: v == var_types.ID_ALIAS,
                          consequent=FieldCollection(
                                         Field(name="variable", type="string"),
                                         Field(name="vlen", type="int"),
                                         Field(name="value", type="string")))
            ],
            peek_predicate=False))
sc.add_message_type(message_types.N_EDITVAR, mt)

"""
case N_CLIPBOARD:
{
    int cn = getint(p), unpacklen = getint(p), packlen = getint(p);
    gameent *d = game::getclient(cn);
    ucharbuf q = p.subbuf(max(packlen, 0));
    if(d) unpackeditinfo(d->edit, q.buf, q.maxlen, unpacklen);
    break;
}
"""

mt = MessageType("N_CLIPBOARD",
        Field(name="clientnum", type="int"),
        Field(name="unpacklen", type="int"),
        IteratedFieldCollection(
            name="data",
            count=Field(type="int"),
            field_collection=RawField(size=1)))
stream_spec.add_message_type(message_types.N_CLIPBOARD, mt)

"""
case N_EDITF:            // coop editing messages (N_CLIENT)
case N_EDITT:
case N_EDITM:
case N_FLIP:
case N_COPY:
case N_PASTE:
case N_ROTATE:
case N_REPLACE:
case N_DELCUBE:
{
    if(!d) return;
    selinfo s;
    s.o.x = getint(p); s.o.y = getint(p); s.o.z = getint(p);
    s.s.x = getint(p); s.s.y = getint(p); s.s.z = getint(p);
    s.grid = getint(p); s.orient = getint(p);
    s.cx = getint(p); s.cxs = getint(p); s.cy = getint(p), s.cys = getint(p);
    s.corner = getint(p);
    int dir, mode, tex, newtex, mat, allfaces;
    ivec moveo;
    switch(type)
    {
        case N_EDITF: dir = getint(p); mode = getint(p); if(s.validate()) mpeditface(dir, mode, s, false); break;
        case N_EDITT: tex = getint(p); allfaces = getint(p); if(s.validate()) mpedittex(tex, allfaces, s, false); break;
        case N_EDITM: mat = getint(p); mode = getint(p); allfaces = getint(p); if(s.validate()) mpeditmat(mat, mode, allfaces, s, false); break;
        case N_FLIP: if(s.validate()) mpflip(s, false); break;
        case N_COPY: if(d && s.validate()) mpcopy(d->edit, s, false); break;
        case N_PASTE: if(d && s.validate()) mppaste(d->edit, s, false); break;
        case N_ROTATE: dir = getint(p); if(s.validate()) mprotate(dir, s, false); break;
        case N_REPLACE: tex = getint(p); newtex = getint(p); allfaces = getint(p); if(s.validate()) mpreplacetex(tex, newtex, allfaces!=0, s, false); break;
        case N_DELCUBE: if(s.validate()) mpdelcube(s, false); break;
    }
    break;
}
"""

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
                            Field(name="mode", type="int"),
                            Field(name="allfaces", type="int")]
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
           Field(name="allfaces", type="int")]))
stream_spec.add_message_type(message_types.N_REPLACE, mt)

mt = MessageType("N_DELCUBE", *common_edit_fields)
stream_spec.add_message_type(message_types.N_DELCUBE, mt)

"""
case N_REMIP: (N_CLIENT)
{
    if(!d) return;
    conoutft(CON_MESG, "\fy%s remipped", game::colourname(d));
    mpremip(false);
    break;
}
"""

mt = MessageType("N_REMIP")
sc.add_message_type(message_types.N_REMIP, mt)

"""
case N_EDITENT: (N_CLIENT)            // coop edit of ent
{
    if(!d) return;
    int i = getint(p);
    float x = getint(p)/DMF, y = getint(p)/DMF, z = getint(p)/DMF;
    int type = getint(p), numattrs = getint(p);
    attrvector attrs;
    attrs.add(0, max(entities::numattrs(type), min(numattrs, MAXENTATTRS)));
    loopk(numattrs)
    {
        int val = getint(p);
        if(attrs.inrange(k)) attrs[k] = val;
    }
    mpeditent(i, vec(x, y, z), type, attrs, false);
    entities::setspawn(i, 0);
    break;
}
"""

mt = MessageType("N_EDITENT",
        Field(name="entity", type="int"),
        Field(name="x", type="int"),
        Field(name="y", type="int"),
        Field(name="z", type="int"),
        Field(name="type", type="int"),
        IteratedFieldCollection(
            name="attributes",
            count=Field(type="int"),
            field_collection=Field(name="value", type="int")))
sc.add_message_type(message_types.N_EDITENT, mt)

"""
case N_EDITLINK: (N_CLIENT)
{
    if(!d) return;
    int b = getint(p), index = getint(p), node = getint(p);
    entities::linkents(index, node, b!=0, false, false);
}
"""

mt = MessageType("N_EDITLINK",
        Field(name="b", type="int"),
        Field(name="index", type="int"),
        Field(name="node", type="int"))
sc.add_message_type(message_types.N_EDITLINK, mt)

"""
case N_PONG:
    addmsg(N_CLIENTPING, "i", game::player1->ping = (game::player1->ping*5+totalmillis-getint(p))/6);
    break;
"""

mt = MessageType("N_PONG",
        Field(name="cmillis", type="int"))
stream_spec.add_message_type(message_types.N_PONG, mt)

"""
case N_CLIENTPING: (N_CLIENT)
    if(!d) return;
    d->ping = getint(p);
    loopv(game::players) if(game::players[i] && game::players[i]->ownernum == d->clientnum)
        game::players[i]->ping = d->ping;
    break;
"""

mt = MessageType("N_CLIENTPING",
        Field(name="ping", type="int"))
sc.add_message_type(message_types.N_CLIENTPING, mt)

"""
case N_TICK:
    game::timeupdate(getint(p));
    break;
"""

mt = MessageType("N_TICK",
        Field(name="millis", type="int"))
stream_spec.add_message_type(message_types.N_TICK, mt)

"""
case N_SERVMSG:
{
    int lev = getint(p);
    getstring(text, p);
    conoutft(lev >= 0 && lev < CON_MAX ? lev : CON_INFO, "%s", text);
    break;
}
"""

mt = MessageType("N_SERVMSG",
        Field(name="level", type="int"),
        Field(name="message", type="string"))
stream_spec.add_message_type(message_types.N_SERVMSG, mt)

"""
case N_SENDDEMOLIST:
{
    int demos = getint(p);
    if(demos <= 0) conoutft(CON_MESG, "\fono demos available");
    else loopi(demos)
    {
        getstring(text, p);
        if(p.overread()) break;
        conoutft(CON_MESG, "\fademo: %d. %s", i+1, text);
    }
    break;
}
"""

mt = MessageType("N_SENDDEMOLIST",
        IteratedFieldCollection(
            name="demos",
            count=Field(type="int"),
            field_collection=Field(name="name", type="string")))
sc.add_message_type(message_types.N_SENDDEMOLIST, mt)

"""
case N_DEMOPLAYBACK:
{
    int on = getint(p);
    if(on) game::player1->state = CS_SPECTATOR;
    else
    {
        loopv(game::players) if(game::players[i]) game::clientdisconnected(i);
    }
    demoplayback = on!=0;
    game::player1->clientnum = getint(p);
    break;
}
"""

mt = MessageType("N_DEMOPLAYBACK",
        Field(name="on", type="int"))
stream_spec.add_message_type(message_types.N_DEMOPLAYBACK, mt)

"""
case N_CURRENTPRIV:
{
    int mn = getint(p), priv = getint(p);
    getstring(text, p);
    if(mn >= 0)
    {
        gameent *m = game::getclient(mn);
        if(m)
        {
            m->privilege = priv;
            copystring(m->handle, text);
        }
    }
    break;
}
"""

mt = MessageType("N_CURRENTPRIV",
        Field(name="clientnum", type="int"),
        Field(name="priv", type="int"),
        Field(name="handle", type="int"))
stream_spec.add_message_type(message_types.N_CURRENTPRIV, mt)

"""
case N_EDITMODE: (N_CLIENT)
{
    int val = getint(p);
    if(!d) break;
    if(val) d->state = CS_EDITING;
    else
    {
        d->state = CS_ALIVE;
        d->editspawn(game::gamemode, game::mutators);
    }
    d->resetinterp();
    projs::remove(d);
    break;
}
"""

mt = MessageType("N_EDITMODE",
        Field(name="value", type="int"))
sc.add_message_type(message_types.N_EDITMODE, mt)

"""
case N_SPECTATOR:
{
    int sn = getint(p), val = getint(p);
    gameent *s = game::newclient(sn);
    if(!s) break;
    if(s == game::player1) game::resetfollow();
    if(val != 0)
    {
        if(s == game::player1 && editmode) toggleedit();
        s->state = CS_SPECTATOR;
        s->checkpoint = -1;
        s->cpmillis = 0;
        s->quarantine = val == 2;
    }
    else
    {
        if(s->state == CS_SPECTATOR)
        {
            s->state = CS_WAITING;
            s->checkpoint = -1;
            s->cpmillis = 0;
            if(s != game::player1 && !s->ai) s->resetinterp();
            game::waiting.removeobj(s);
        }
        s->quarantine = false;
    }
    break;
}
"""

mt = MessageType("N_SPECTATOR",
        Field(name="clientnum", type="int"),
        Field(name="val", type="int"))
stream_spec.add_message_type(message_types.N_SPECTATOR, mt)

"""
case N_WAITING:
{
    int sn = getint(p);
    gameent *s = game::newclient(sn);
    if(!s) break;
    if(s == game::player1)
    {
        if(editmode) toggleedit();
        hud::showscores(false);
        s->stopmoving(true);
        game::waiting.setsize(0);
        gameent *d;
        loopv(game::players) if((d = game::players[i]) && d->aitype == AI_NONE && d->state == CS_WAITING)
            game::waiting.add(d);
    }
    else if(!s->ai) s->resetinterp();
    game::waiting.removeobj(s);
    if(s->state == CS_ALIVE) s->lastdeath = lastmillis; // so spawndelay shows properly
    s->state = CS_WAITING;
    s->quarantine = false;
    s->weapreset(true);
    break;
}
"""

mt = MessageType("N_WAITING",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.N_WAITING, mt)

"""
case N_SETTEAM:
{
    int wn = getint(p), tn = getint(p);
    gameent *w = game::getclient(wn);
    if(!w) return;
    if(w->team != tn)
    {
        if(m_team(game::gamemode, game::mutators) && w->aitype == AI_NONE && showteamchange >= (w->team != T_NEUTRAL && tn != T_NEUTRAL ? 1 : 2))
            conoutft(CON_EVENT, "\fa%s is now on team %s", game::colourname(w), game::colourteam(tn));
        w->team = tn;
        if(w == game::focus) hud::lastteam = 0;
    }
    break;
}
"""

mt = MessageType("N_SETTEAM",
        Field(name="clientnum", type="int"),
        Field(name="team", type="int"))
stream_spec.add_message_type(message_types.N_SETTEAM, mt)

"""
case N_INFOAFFIN:
{
    int flag = getint(p), converted = getint(p),
            owner = getint(p), enemy = getint(p);
    if(m_defend(game::gamemode)) defend::updateaffinity(flag, owner, enemy, converted);
    break;
}
"""

mt = MessageType("N_INFOAFFIN",
        Field(name="flag", type="int"),
        Field(name="converted", type="int"),
        Field(name="owner", type="int"),
        Field(name="enemy", type="int"))
stream_spec.add_message_type(message_types.N_INFOAFFIN, mt)
sc.add_message_type(message_types.N_INFOAFFIN, mt)

"""
case N_SETUPAFFIN:
{
    if(m_defend(game::gamemode)) defend::parseaffinity(p);
    break;
}

void defend::parseaffinity(ucharbuf &p)
{
    int numflags = getint(p);
    while(st.flags.length() > numflags) st.flags.pop();
    loopi(numflags)
    {
        int kin = getint(p), ent = getint(p), converted = getint(p), owner = getint(p), enemy = getint(p);
        vec o;
        loopj(3) o[j] = getint(p)/DMF;
        string name;
        getstring(name, p);
        if(p.overread()) break;
        while(!st.flags.inrange(i)) st.flags.add();
        st.initaffinity(i, kin, ent, o, owner, enemy, converted, name);
    }
}
"""

mt = MessageType("N_SETUPAFFIN", 
        SwitchField(
            predicate=None, 
            cases=[
                CaseField(predicate_comparison=SD(lambda v, gs: m_defend(gs['gamemode'])),
                          consequent=FieldCollection(
                                IteratedFieldCollection(
                                    name="flags",
                                    count=Field(type="int"),
                                    field_collection=FieldCollection(Field(name="kin", type="int"),
                                                                     Field(name="entity", type="int"),
                                                                     Field(name="converted", type="int"),
                                                                     Field(name="owner", type="int"),
                                                                     Field(name="enemy", type="int"),
                                                                     Field(name="x", type="int"),
                                                                     Field(name="y", type="int"),
                                                                     Field(name="z", type="int"),
                                                                     Field(name="name", type="string")))
                          ))
            ]))
stream_spec.add_message_type(message_types.N_SETUPAFFIN, mt)

"""
case N_MAPVOTE:
{
    int vn = getint(p);
    gameent *v = game::getclient(vn);
    getstring(text, p);
    filtertext(text, text);
    int reqmode = getint(p), reqmuts = getint(p);
    if(!v) break;
    vote(v, text, reqmode, reqmuts);
    break;
}
"""

mt = MessageType("N_MAPVOTE",
        Field(name="clientnum", type="int"),
        Field(name="map", type="string"),
        Field(name="mode", type="int"),
        Field(name="muts", type="int"))
stream_spec.add_message_type(message_types.N_MAPVOTE, mt)

"""
case N_CLEARVOTE:
{
    int vn = getint(p);
    gameent *v = game::getclient(vn);
    if(!v) break;
    clearvotes(v, true);
    break;
}
"""

mt = MessageType("N_CLEARVOTE",
        Field(name="clientnum", type="int"))
stream_spec.add_message_type(message_types.N_CLEARVOTE, mt)

"""
case N_CHECKPOINT:
{
    int tn = getint(p), ent = getint(p);
    gameent *t = game::getclient(tn);
    if(!t)
    {
        if(getint(p) < 0) break;
        loopi(2) getint(p);
        break;
    }
    if(ent >= 0)
    {
        if(m_trial(game::gamemode) && entities::ents.inrange(ent) && entities::ents[ent]->type == CHECKPOINT)
        {
            if(t != game::player1 && !t->ai && (!t->cpmillis || entities::ents[ent]->attrs[6] == CP_START))
                t->cpmillis = lastmillis;
            entities::execlink(t, ent, false);
        }
        int laptime = getint(p);
        if(laptime >= 0)
        {
            t->cplast = laptime;
            t->cptime = getint(p);
            t->cplaps = getint(p);
            t->cpmillis = t->impulse[IM_METER] = 0;
            if(showlaptimes > (t != game::focus ? (t->aitype > AI_NONE ? 2 : 1) : 0))
            {
                defformatstring(best)("%s", timestr(t->cptime));
                conoutft(t != game::player1 ? CON_INFO : CON_SELF, "%s completed in \fs\fg%s\fS (best: \fs\fy%s\fS, laps: \fs\fc%d\fS)", game::colourname(t), timestr(t->cplast), best, t->cplaps);
            }
        }
    }
    else
    {
        t->checkpoint = -1;
        t->cpmillis = ent == -2 ? lastmillis : 0;
    }
}
"""

mt = MessageType("N_CHECKPOINT",
        Field(name="clientnum", type="int"),
        Field(name="entity", type="int"), 
        ConditionalFieldCollection(
            predicate=Field(type="int"), 
            predicate_comparison = lambda v: v >= 0,
            consequent=FieldCollection(Field(name="laptime", type="int"),
                                       Field(name="cptime", type="int"),
                                       Field(name="cplaps", type="int")),
            alternative=FieldCollection(Field(name="laptime", type="int")),
            peek_predicate=True))
stream_spec.add_message_type(message_types.N_CHECKPOINT, mt)

"""
case N_SCORE:
{
    int team = getint(p), total = getint(p);
    if(m_team(game::gamemode, game::mutators))
    {
        score &ts = hud::teamscore(team);
        ts.total = total;
    }
    break;
}
"""

mt = MessageType("N_SCORE",
        Field(name="team", type="int"),
        Field(name="score", type="int"))
sc.add_message_type(message_types.N_SCORE, mt)
stream_spec.add_message_type(message_types.N_SCORE, mt)

"""
case N_INITAFFIN:
{
    if(m_capture(game::gamemode)) capture::parseaffinity(p);
    else if(m_bomber(game::gamemode)) bomber::parseaffinity(p);
    break;
}

void capture::parseaffinity(ucharbuf &p)
{
    int numflags = getint(p);
    while(st.flags.length() > numflags) st.flags.pop();
    loopi(numflags)
    {
        int team = getint(p), ent = getint(p), owner = getint(p), dropped = 0;
        vec spawnloc(0, 0, 0), droploc(0, 0, 0), inertia(0, 0, 0);
        loopj(3) spawnloc[j] = getint(p)/DMF;
        if(owner < 0)
        {
            dropped = getint(p);
            if(dropped)
            {
                loopj(3) droploc[j] = getint(p)/DMF;
                loopj(3) inertia[j] = getint(p)/DMF;
            }
        }
        if(p.overread()) break;
        while(!st.flags.inrange(i)) st.flags.add();
        capturestate::flag &f = st.flags[i];
        f.team = team;
        f.ent = ent;
        f.spawnloc = spawnloc;
        if(owner >= 0) st.takeaffinity(i, game::getclient(owner), lastmillis);
        else if(dropped) st.dropaffinity(i, droploc, inertia, lastmillis);
    }
}

void bomber::parseaffinity(ucharbuf &p)
{
    int numflags = getint(p);
    while(st.flags.length() > numflags) st.flags.pop();
    loopi(numflags)
    {
        int team = getint(p), ent = getint(p), enabled = getint(p), owner = getint(p), dropped = 0;
        vec spawnloc(0, 0, 0), droploc(0, 0, 0), inertia(0, 0, 0);
        loopj(3) spawnloc[j] = getint(p)/DMF;
        if(owner < 0)
        {
            dropped = getint(p);
            if(dropped)
            {
                loopj(3) droploc[j] = getint(p)/DMF;
                loopj(3) inertia[j] = getint(p)/DMF;
            }
        }
        if(p.overread()) break;
        while(!st.flags.inrange(i)) st.flags.add();
        bomberstate::flag &f = st.flags[i];
        f.team = team;
        f.ent = ent;
        f.enabled = enabled ? 1 : 0;
        f.spawnloc = spawnloc;
        if(owner >= 0) st.takeaffinity(i, game::getclient(owner), lastmillis);
        else if(dropped) st.dropaffinity(i, droploc, inertia, lastmillis);
    }
}
"""

mt = MessageType("N_INITAFFIN", 
        SwitchField(
            predicate=None, 
            cases=[
                CaseField(predicate_comparison=SD(lambda v, gs: m_capture(gs['gamemode'])),
                          consequent=FieldCollection(
                                IteratedFieldCollection(
                                    name="flags",
                                    count=Field(type="int"),
                                    field_collection=FieldCollection(
                                        Field(name="team", type="int"),
                                        Field(name="entity", type="int"),
                                    
                                        ConditionalFieldCollection(
                                            predicate=Field(type="int"), 
                                            predicate_comparison = lambda v: v < 0,
                                            consequent=FieldCollection(
                                                 Field(name="owner", type="int"),
                                                 Field(name="spawnx", type="int"),
                                                 Field(name="spawny", type="int"),
                                                 Field(name="spawnz", type="int"),

                                                 ConditionalFieldCollection(
                                                     predicate=Field(type="int"), 
                                                     predicate_comparison = lambda v: v,
                                                     consequent=FieldCollection(
                                                          Field(name="dropped", type="int"),
                                                          Field(name="dropx", type="int"),
                                                          Field(name="dropy", type="int"),
                                                          Field(name="dropz", type="int"),
                                                          Field(name="inertiax", type="int"),
                                                          Field(name="inertiay", type="int"),
                                                          Field(name="inertiaz", type="int")
                                                     ),
                                                     alternative=FieldCollection(Field(name="dropped", type="int")),
                                                     peek_predicate=True)
                                            ),
                                            alternative=FieldCollection(
                                                 Field(name="owner", type="int"),
                                                 Field(name="spawnx", type="int"),
                                                 Field(name="spawny", type="int"),
                                                 Field(name="spawnz", type="int")
                                            ),
                                            peek_predicate=True)
                                    ))
                          )),       
                CaseField(predicate_comparison=SD(lambda v, gs: m_bomber(gs['gamemode'])),
                          consequent=FieldCollection(
                                IteratedFieldCollection(
                                    name="flags",
                                    count=Field(type="int"),
                                    field_collection=FieldCollection(
                                        Field(name="team", type="int"),
                                        Field(name="entity", type="int"),
                                        Field(name="enabled", type="int"),
                                        ConditionalFieldCollection(
                                            predicate=Field(type="int"), 
                                            predicate_comparison = lambda v: v < 0,
                                            consequent=FieldCollection(
                                                 Field(name="owner", type="int"),
                                                 Field(name="spawnx", type="int"),
                                                 Field(name="spawny", type="int"),
                                                 Field(name="spawnz", type="int"),
                                                 ConditionalFieldCollection(
                                                     predicate=Field(type="int"), 
                                                     predicate_comparison = lambda v: v,
                                                     consequent=FieldCollection(
                                                          Field(name="dropped", type="int"),
                                                          Field(name="dropx", type="int"),
                                                          Field(name="dropy", type="int"),
                                                          Field(name="dropz", type="int"),
                                                          Field(name="inertiax", type="int"),
                                                          Field(name="inertiay", type="int"),
                                                          Field(name="inertiaz", type="int")
                                                     ),
                                                     alternative=FieldCollection(Field(name="dropped", type="int")),
                                                     peek_predicate=True)
                                            ),
                                            alternative=FieldCollection(
                                                 Field(name="owner", type="int"),
                                                 Field(name="spawnx", type="int"),
                                                 Field(name="spawny", type="int"),
                                                 Field(name="spawnz", type="int")
                                            ),
                                            peek_predicate=True)
                                    ))
                          ))
            ]))
stream_spec.add_message_type(message_types.N_INITAFFIN, mt)

"""
case N_DROPAFFIN:
{
    int ocn = getint(p), tcn = getint(p), flag = getint(p);
    vec droploc, inertia;
    loopk(3) droploc[k] = getint(p)/DMF;
    loopk(3) inertia[k] = getint(p)/DMF;
    gameent *o = game::newclient(ocn);
    if(o)
    {
        if(m_capture(game::gamemode)) capture::dropaffinity(o, flag, droploc, inertia, tcn);
        else if(m_bomber(game::gamemode)) bomber::dropaffinity(o, flag, droploc, inertia, tcn);
    }
    break;
}
"""

mt = MessageType("N_DROPAFFIN",
        Field(name="clientnum", type="int"),
        Field(name="target", type="int"),
        Field(name="flag", type="int"),
        Field(name="dx", type="int"),
        Field(name="dy", type="int"),
        Field(name="dz", type="int"),
        Field(name="ix", type="int"),
        Field(name="iy", type="int"),
        Field(name="iz", type="int"))
stream_spec.add_message_type(message_types.N_DROPAFFIN, mt)

"""
case N_SCOREAFFIN:
{
    int ocn = getint(p), relayflag = getint(p), goalflag = getint(p), score = getint(p);
    gameent *o = game::newclient(ocn);
    if(o)
    {
        if(m_capture(game::gamemode)) capture::scoreaffinity(o, relayflag, goalflag, score);
        else if(m_bomber(game::gamemode)) bomber::scoreaffinity(o, relayflag, goalflag, score);
    }
    break;
}
"""

mt = MessageType("N_SCOREAFFIN",
        Field(name="clientnum", type="int"),
        Field(name="relayflag", type="int"),
        Field(name="goalflag", type="int"),
        Field(name="score", type="int"))
stream_spec.add_message_type(message_types.N_SCOREAFFIN, mt)

"""
case N_RETURNAFFIN:
{
    int ocn = getint(p), flag = getint(p);
    gameent *o = game::newclient(ocn);
    if(o && m_capture(game::gamemode)) capture::returnaffinity(o, flag);
    break;
}
"""

mt = MessageType("N_RETURNAFFIN",
        Field(name="clientnum", type="int"),
        Field(name="flag", type="int"))
stream_spec.add_message_type(message_types.N_RETURNAFFIN, mt)

"""
case N_TAKEAFFIN:
{
    int ocn = getint(p), flag = getint(p);
    gameent *o = game::newclient(ocn);
    if(o)
    {
        if(m_capture(game::gamemode)) capture::takeaffinity(o, flag);
        else if(m_bomber(game::gamemode)) bomber::takeaffinity(o, flag);
    }
    break;
}
"""

mt = MessageType("N_TAKEAFFIN",
        Field(name="clientnum", type="int"),
        Field(name="flag", type="int"))
stream_spec.add_message_type(message_types.N_TAKEAFFIN, mt)

"""
case N_RESETAFFIN:
{
    int flag = getint(p), value = getint(p);
    if(m_capture(game::gamemode)) capture::resetaffinity(flag, value);
    else if(m_bomber(game::gamemode)) bomber::resetaffinity(flag, value);
    break;
}
"""

mt = MessageType("N_RESETAFFIN",
        Field(name="flag", type="int"),
        Field(name="value", type="int"))
stream_spec.add_message_type(message_types.N_RESETAFFIN, mt)

"""
case N_GETMAP:
{
    conoutft(CON_MESG, "\fyserver has requested we send the map..");
    if(!needsmap && !gettingmap) sendmap();
    else
    {
        if(!gettingmap) conoutft(CON_MESG, "\fy..we don't have the map though, so asking for it instead");
        else conoutft(CON_MESG, "\fy..but we're in the process of getting it");
        addmsg(N_GETMAP, "r");
    }
    break;
}
"""

mt = MessageType("N_GETMAP")
stream_spec.add_message_type(message_types.N_GETMAP, mt)

"""
case N_SENDMAP:
{
    conoutft(CON_MESG, "\fymap data has been uploaded to the server");
    if(needsmap && !gettingmap)
    {
        conoutft(CON_MESG, "\fy.. and we want the map too, so asking for it");
        addmsg(N_GETMAP, "r");
    }
    break;
}
"""

mt = MessageType("N_SENDMAP")
stream_spec.add_message_type(message_types.N_SENDMAP, mt)

"""
case N_FAILMAP:
{
    if(needsmap) conoutft(CON_MESG, "\fyunable to load map, nobody else has a copy of it..");
    needsmap = gettingmap = false;
    break;
}
"""

mt = MessageType("N_FAILMAP")
stream_spec.add_message_type(message_types.N_FAILMAP, mt)

"""
case N_NEWMAP:
{
    int size = getint(p);
    if(size>=0) emptymap(size, true);
    else enlargemap(true);
    mapvotes.shrink(0);
    needsmap = false;
    if(d && d!=game::player1)
    {
        int newsize = 0;
        while(1<<newsize < getworldsize()) newsize++;
        conoutft(CON_MESG, size>=0 ? "\fy%s started a new map of size \fs\fc%d\fS" : "\fy%s enlarged the map to size \fs\fc%d\fS", game::colourname(d), newsize);
    }
    break;
}
"""

mt = MessageType("N_NEWMAP",
        Field(name="size", type="int"))
stream_spec.add_message_type(message_types.N_NEWMAP, mt)
sc.add_message_type(message_types.N_NEWMAP, mt)

"""
case N_INITAI:
{
    int bn = getint(p), on = getint(p), at = getint(p), et = getint(p), sk = clamp(getint(p), 1, 101);
    getstring(text, p);
    int tm = getint(p), cl = getint(p), md = getint(p);
    string vanity;
    getstring(vanity, p);
    gameent *b = game::newclient(bn);
    if(!b) break;
    ai::init(b, at, et, on, sk, bn, text, tm, cl, md, vanity);
    break;
}
"""

mt = MessageType("N_INITAI",
        Field(name="clientnum", type="int"),
        Field(name="owner", type="int"),
        Field(name="type", type="int"),
        Field(name="entity", type="int"),
        Field(name="skill", type="int"),
        Field(name="name", type="string"),
        Field(name="team", type="int"),
        Field(name="color", type="int"),
        Field(name="model", type="int"),
        Field(name="vanity", type="string"))
stream_spec.add_message_type(message_types.N_INITAI, mt)

"""
case N_AUTHCHAL:
{
    uint id = (uint)getint(p);
    getstring(text, p);
    if(accountname[0] && accountpass[0])
    {
        if(verbose) conoutft(CON_MESG, "\fyanswering account challenge..");
        vector<char> buf;
        answerchallenge(accountpass, text, buf);
        addmsg(N_AUTHANS, "ris", id, buf.getbuf());
    }
    break;
}
"""

mt = MessageType("N_AUTHCHAL",
        Field(name="authid", type="uint"),
        Field(name="challenge", type="string"))
stream_spec.add_message_type(message_types.N_AUTHCHAL, mt)

