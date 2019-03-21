# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
# See LICENSE.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
This library is used to do Operation on MongoDB server 

Current we focus on the shard server 

Class:
    MongoDBOps    MongoDB related opeartions
Functions:

Limitation:

"""
__all__ = []

from pymongo import MongoClient, errors
import time, os 
from base0.baselibs import get_log
from base0.exception import AppException


def class_properites(func):
    """ decoretor to process class fields"""
    def wrapper(*args):
        log = get_log()
        class_obj = args[0]
        input_kwargs = args[1]
        required = args[2]
        optional = args[3]
        newfields = args[4]

        log.debug(f"start to set {class_obj} required properties")
        for field in required:
            if field in input_kwargs:
                setattr(class_obj, field, input_kwargs[field])
                log.debug(f"set attribute {field} with value {input_kwargs[field]}")
            else:
                raise AppException("base", 101,
                                  f"{field} is not in the {class_obj} initial dict")

        log.debug(f"start to set {class_obj} initial optional properties")
        for field in optional:
            if field in input_kwargs:
                setattr(class_obj, field, input_kwargs[field])
                log.debug(f"set attribute {field} with value {input_kwargs[field]}")
            else:
                log.debug(f"attribute {field}is not set")

        log.debug(f"start to set {class_obj} properties")
        for field in newfields:
            setattr(class_obj, field, None)
            log.debug(f"set attribute {field}")

        return func(*args)        
    return wrapper

def host_command(client_ins,commands):
    validresults = {}
    for commandset in commands:
        command = f"{commandset['command']} {commandset['parameter']}"
        returnresult = client_ins.execute_command(command)
        resultmark = commandset['resultsplit'].split()
        commandresult = []
        if len(returnresult) == 3:
            rr = [_ for _ in returnresult[1].split("\n") if _ is not ""]
            for rrl in rr: 
                rrlist = rrl.split()
                if len(rrlist) != len(resultmark):
                    lastnum = len(resultmark)-1
                    lastvalue =  " ".join(rrlist[lastnum:])
                    rrlisttmp = rrlist[:lastnum]+[lastvalue]
                    rrlist = rrlisttmp
                rrdict = dict(zip(resultmark,rrlist))
                validresult = {}
                for key_ in commandset['resultprocess']:
                    validresult[key_] = rrdict[key_]
                commandresult.append(validresult)
        else:
            raise AppException("bash", 101, returnresult)
        validresults[commandset['command']] = commandresult
    return validresults

def host_mongod_state(client_ins, shardinfo):
    hostname = client_ins.client_hostname
    commands = [
        {"command": "ps", 
         "parameter": "-auxf | grep mongod| grep -v grep", 
         "resultsplit": "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND",
         "resultprocess": ["PID", "COMMAND"]}, 
        {"command": "netstat",
         "parameter": " -lptu|grep mongod",
         "resultsplit" : "Proto Recv-Q Send-Q Local_Address  Foreign_Address   State   PID/Program_name",
         "resultprocess": ["Local_Address","PID/Program_name"]
            }]   
    command_result = host_command(client_ins, commands)
    host_mongodnodes = [_ for _ in shardinfo['mongodnodes'] if hostname in _]
    host_mongodport = [_.split(":")[1] for _ in host_mongodnodes]
    host_mongodcommand = {}
    for port_ in host_mongodport:
        for netstat_ in command_result['netstat']:
            if port_ in netstat_['Local_Address']:
                portpid = netstat_['PID/Program_name'].split("/")[0]
                print(f"found the process {portpid}")
                for ps_ in command_result['ps']:
                    if portpid == ps_["PID"]:
                        host_mongodcommand[port_] = ps_['COMMAND']
                        print(ps_['COMMAND'])
    if len(host_mongodport) != len(host_mongodcommand):
        raise AppException("mongo", 801, f"{hostname} only have {host_mongodcommand.keys()} running. it shoudl have {host_mongodport}")
    print(host_mongodcommand)
    
    
class MongoDBOps():
    """ MongoDB related Operations"""
 
    def __init__(self, **kwargs):
        """iniial class objects"""
        self.log = get_log()
        required_fields = ["server", "port"]
        optional_fields = ["username", "password", "clusterhosts", "replset"]
        new_fields = ["conn", "serverinfo"]
        self.log.debug("initial class related properties")
        self.assign_fields(kwargs, required_fields, optional_fields,new_fields)
        self.log.debug("start to initial mongo connection")
        self.connection()
        self.log.debug("mongo server connection is setup")
        
    @class_properites
    def assign_fields(self, kwargs,
                      required_fields, optional_fields, new_fields):
        """ assign all class properties"""
        return None
    
    def connection(self):
        """ setup mongo client connection"""
        mongouri = f"mongodb://{self.server}:{self.port}"
        self.log.info(f"mongouri is {mongouri}")
        if self.username is None:
            self.log.debug("No user defined, use regular connection")
            if self.replset:
                self.conn = MongoClient(mongouri, replicaset=self.replset)
            else:
                self.conn = MongoClient(mongouri)  
        else:
            self.log.debug(f"Have user {self.username}, will use auth conn")
            if self.replset:
                self.conn =MongoClient(mongouri,username=self.username,
                                       password=self.password,
                                       authSource="admin",
                                       replicaset=self.replset)
            else:
                self.conn =MongoClient(mongouri,username=self.username,
                                       password=self.password,
                                       authSource="admin")                
        self.connection_check()
        
    def connection_check(self):
        """check mongo client connection """
        try:
            serverinfo = self.conn.server_info()
        except errors: 
            raise AppException("mongo", 101, f"{errors}")
        serverinfo['mongos'] = self.conn.is_mongos
        serverinfo['primary'] = self.conn.is_primary
        self.serverinfo = serverinfo
    
    def database(self, dbname=None, status=False, new=False):
        """Get mongo database object
        Args:
            dbname    string    database name
                                if not name passed, will return admin database
        Return:    
            db_ins    object    database object
        Exepption:
            201    database is not found
        """
        dblist = self.conn.list_database_names()
        if dbname is None:
            db_ins = self.conn.get_database("admin")
        else:
            if dbname in dblist:
                db_ins = self.conn.get_database(dbname)
            else:
                if new:
                    db_ins = getattr(self.conn, dbname)
                else:
                    print(dblist)
                    raise AppException("mongo", 201, f"database name is {dbname}")
        
        if status:
            dbstats = self.database_stats(db_ins)
        return db_ins 

    def database_stats(self,db_ins):
        """ check database status """
        dbstats = db_ins.command({"dbstats":1})
        dbstats = self.database_stats_trans(dbstats)
        return dbstats

    def database_stats_trans(self,dbstats):
        """ transfer the database status to correct format """
        
        db_stat = {}
        for key_ in dbstats.keys():
            if key_ == "raw":
                self.log.debug(f"database is split in {len(dbstats[key_])} shards")
                for entry in dbstats[key_]:
                    db_stat[entry] = dbstats[key_][entry]
            else:
                db_stat[key_] = dbstats[key_]
        return db_stat
    
    def collection(self, db_ins, collname, new=False):
        """ Get mongo database colleciotn ojbects
        Args:
            db_ins    object    database instance
            collname    string    collection name madatory
        Return:
            coll_ins    object    collection objects
        Exception:
            301    collection is not found   
        """
        collectionlist = db_ins.list_collection_names()
        if collname in collectionlist:
#            coll_ins = getattr(db_ins, collname)
            coll_ins = db_ins.get_collection(collname)
        else:
            if new:
                coll_ins = getattr(db_ins, collname)
            else:
                raise AppException("mongo", 301, f"collection name is {collname}")
        return coll_ins

    def collection_stats(self, db_ins, collname):
        """ check collection status"""
        coll_ins=self.collection(db_ins, collname)
        collstats= db_ins.command({"collstats",collname,1})
        collstats= self.collection_stats_trans(collstats)
        
    def collection_stats_trans(self,collstats):
        """ transdfer the collection status to correct format"""
        coll_stat = {}
        return coll_stat
        
    def doc_batch_simple(self,coll_ins, group=10_000, times=10):
        """ insert batch simple doucment to colleciotn"""
        docs = []
        for i in range(times):
            for j in range(group):
                docs.append({"id": int(time.time()), "value": time.time()})
            self.doc_insert(coll_ins, docs)
            docs = []
        return None
    
    def doc_batch_list(self, coll_ins, contentlist, raw=False):
        """ inpusert batch docuemnt based on the list"""
        docs = []
        for i in range(len(contentlist)):
            if raw:
                docs.append(contentlist[i])
            else:
                docs.append({"id": int(time.time()), "value": time.time(),
                             "content": contentlist[i]})
        self.doc_insert(coll_ins, docs)
        return None
    
    def doc_insert(self,coll_ins, document):
        """ insert documents to collection """
        if isinstance(document, dict):
            returnvalue = coll_ins.insert_one(document)
        elif isinstance(document, list):
            if len(document) ==1: 
                returnvalue = coll_ins.insert_one(document)
            else:
                returnvalue = coll_ins.insert_many(document)
        else:
            raise ("mongo", 401, document)
        self.log.debug(f"current collection count is {coll_ins.count()}")
        return returnvalue

    def shell_command_generator(self, command):
        """ run the java script on the mongo instance"""
        if self.username is None:
            connection = f"mongo --host {self.server} --port {self.port}"
        else:
            connection = f"mongo --host {self.server} --port {self.port} \
                            -u {self.username} -p {self.password} \
                            --authenticationDatabase admin"
        command = f"use admin;"
        commandline = f"{connection} --eval {command}"

        return commandline
      
    def shell_shutdownserver(self):
        """ shutdown running mongo instance from command line"""
        commandline = self.shell_command_generator(command)

    def shard_info(self, dbname=None, collectionname=None):
        """ Get shard information """
        shard_info = self.shard_map()
        self.log.debug(f"Shard map info {shard_info}")
        shard_info['collections'] = self.shard_collection(dbname=dbname,
                                                          collectionname=collectionname)
        return shard_info
        
    def shard_collection(self, dbname=None, collectionname=None, enableshard=True):
        """ collection shard information bassed on database and collection"""
        if dbname is None:
            dbs = self.conn.list_database_name()
            collectionname = None
        else:
            dbs = [dbname]
        self.log.debug(f"Will check the following dbs {dbs}")

        shardinfos = []
        for db in dbs:
            self.log.debug(f"start to check {db} shard info")
            shardinfo = {}
            db_ = self.database(dbname=db,status=True)
            self.log.debug(f"get database instance {db_}")
            if collectionname is None:
                collectionlist = db_.list_collection_names()
            else:
                collectionlist = [collectionname]
            self.log.debug(f"will check the following collections {collectionlist}")
            
            for collname in collectionlist:
                self.log.debug(f"get collection {collname} stats")
                coll_info = db_.command("collstats",collname,1)
                if coll_info['sharded']:
                    self.log.debug(f"collection {collname} is sharded")
                    shardinfo[collname] = {}
                    shardinfo[collname]["shards"] = coll_info['shards'].keys()
                    self.log.debug(f"there are {len(coll_info['shards'])} shards")
                    shardinfo[collname]['count'] = coll_info['count']
                    self.log.debug(f"there are total {coll_info['count']} docuemnts")
                    shardinfo[collname]['nchunks'] = coll_info['nchunks']
                    self.log.debug(f"there are total {coll_info['nchunks']} chuncks")
                    for shardins in coll_info['shards']:
                        shardinfo[collname][shardins] = coll_info['shards'][shardins]['count']
                    self.log.debug(f"colleciton info is {shardinfo}")
                else:
                    self.log.debug(f"{collname} is not sharded")
                    if enableshard:
                        db_admin = self.database()
                        db_admin.command({"enableSharding": db})
                    else: 
                        raise AppException("mongo", 201, f"{db} is not sharded")
            shardinfos.append(shardinfo)
            self.log.debug(f"shard collection info:\n{shardinfos}")
        return shardinfos

    def shard_map(self):
        """ check shard map """
        db_admin = self.database()
        shard_info = {}
        clusters = []
        mongodnodes = []
        hosts = []
        shard_map = db_admin.command("getShardMap",1)['map']
        self.log.debug(f"shard map is {shard_map}")
        for key_ in shard_map:
            value_ = shard_map[key_]
            if key_=="config":
                shard_info['config'] = value_
                self.log.debug(f"shard config is {value_}")
            if value_ not in clusters:
                clusters.append(value_)
            else: 
                self.log.debug(f"cluster {value_} already added")
        shard_info['clusters'] = clusters
        
        for cluster in clusters:
            clustername = cluster.split("/")[0]
            clusternodes = cluster.split("/")[1]
            nodes  = clusternodes.split(',')
            for node in nodes:
                if node not in mongodnodes:
                    mongodnodes.append(node)
                    hostname = node.split(":")[0]
                    if hostname not in hosts:
                        hosts.append(hostname)
                else:
                    self.log.debug(f"{node} already in list")
            shard_info[clustername] = nodes
        shard_info['mongodnodes'] = mongodnodes
        shard_info['hosts'] = hosts
        return shard_info

    def repset_info(self):
        """ get rep set infomation"""
        pass 