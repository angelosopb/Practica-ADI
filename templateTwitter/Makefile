.PHONY: lib

all: lib run

run: 
	hdfs namenode -format
	/home/angel/ADI/hadoop-2.8.1/sbin/start-dfs.sh
	/home/angel/ADI/hadoop-2.8.1/sbin/start-yarn.sh
	hdfs dfs -mkdir -p /user/angel/twitter-data
	dev_appserver.py .

lib:
	pip install --upgrade -r requirements.txt -t lib/

clean:
	$(RM) -rf *~ *.pyc lib 
	$(RM) -rf $(shell find . -name *~)
	$(RM) -rf $(shell find . -name *pyc)

