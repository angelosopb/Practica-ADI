from org.apache.pig.scripting import Pig
import sys

operacion=sys.argv[1];

if(operacion=="1"): #Idioma

    P = Pig.compile("""
    REGISTER /home/angel/ADI/arch_flume/json-simple-1.1.jar
    REGISTER /home/angel/ADI/arch_flume/flume-sources-1.0-SNAPSHOT.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-pig-4.1.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-hadoop-compat-4.1.jar
    tweets = LOAD '/user/angel/twitter-data' USING com.twitter.elephantbird.pig.load.JsonLoader('-nestedLoad') as (json:map[]);
    tweets2 = FILTER tweets BY json#'lang' == '$in';
    tweet_detalle= FOREACH tweets2 GENERATE json#'text';
    rmf /user/angel/out.csv
    STORE tweet_detalle INTO '/user/angel/out.csv' USING PigStorage(';');
    """)

    result = P.bind({'in':sys.argv[2]}).runSingle()
    if result.isSuccessful():
        print "Pig job succeeded"
    else:
        raise "Pig job failed"

if(operacion=="2"): #Palabra

    P = Pig.compile("""
    REGISTER /home/angel/ADI/arch_flume/json-simple-1.1.jar
    REGISTER /home/angel/ADI/arch_flume/flume-sources-1.0-SNAPSHOT.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-pig-4.1.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-hadoop-compat-4.1.jar
    tweets = LOAD '/user/angel/twitter-data' USING com.twitter.elephantbird.pig.load.JsonLoader('-nestedLoad') as (json:map[]);
    tweets2 = FILTER tweets BY json#'text' MATCHES '.*$in.*';
    tweet_detalle= FOREACH tweets2 GENERATE json#'text';
    rmf /user/angel/out2.csv
    STORE tweet_detalle INTO '/user/angel/out2.csv' USING PigStorage(';');
    """)

    result = P.bind({'in':sys.argv[2]}).runSingle()
    if result.isSuccessful():
        print "Pig job succeeded"
    else:
        raise "Pig job failed"

if(operacion=="3"): #Likes

    P = Pig.compile("""
    REGISTER /home/angel/ADI/arch_flume/json-simple-1.1.jar
    REGISTER /home/angel/ADI/arch_flume/flume-sources-1.0-SNAPSHOT.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-pig-4.1.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-hadoop-compat-4.1.jar
    tweets = LOAD '/user/angel/twitter-data' USING com.twitter.elephantbird.pig.load.JsonLoader('-nestedLoad') as (json:map[]);
    tweets2 = FILTER tweets BY json#'favorite_count' >= '$in';
    tweet_detalle= FOREACH tweets2 GENERATE json#'text';
    rmf /user/angel/out3.csv
    STORE tweet_detalle INTO '/user/angel/out3.csv' USING PigStorage(';');
    """)

    result = P.bind({'in':sys.argv[2]}).runSingle()
    if result.isSuccessful():
        print "Pig job succeeded"
    else:
        raise "Pig job failed"
if(operacion=="4"): #Personas

    P = Pig.compile("""
    REGISTER /home/angel/ADI/arch_flume/json-simple-1.1.jar
    REGISTER /home/angel/ADI/arch_flume/flume-sources-1.0-SNAPSHOT.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-pig-4.1.jar
    REGISTER /home/angel/ADI/arch_flume/elephant-bird-hadoop-compat-4.1.jar
    tweets = LOAD '/user/angel/twitter-data' USING com.twitter.elephantbird.pig.load.JsonLoader('-nestedLoad') as (json:map[]);
    tweets2 = FILTER tweets BY json#'lang' == '$in';
    tweet_detalle= FOREACH tweets2 GENERATE json#'text' AS text;
    dump tweet_detalle;
    """)

    result = P.bind({'in':sys.argv[2]}).runSingle()
    if result.isSuccessful():
        print "Pig job succeeded"
    else:
        raise "Pig job failed"
