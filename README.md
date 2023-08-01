Author: Carl Winkler
Date: 03. December 2021

The data comes from: http://fakenews.research.sfu.ca/#parseWebs

The potential web-interface view:

![This is how the Web-Interface looks like](https://github.com/Chipato1/DataWarehouse-FakeNews/blob/main/Full_View.png)



Procedure to run the system:

1. Step (Stick to report.pdf for a more detailed description)

sudo docker pull Cloudera/quickstart:latest
sudo docker run --hostname=quickstart.cloudera --privileged=true -t -i --publish-all=true -p 8888:8888 -p 7180:7180 -p 10000:10000 cloudera/quickstart /usr/bin/docker-quickstart

-> Start Hive, HDFS and MapReduce in Cloudera

2. Step
Run the python Preprocessing.py script
sudo docker cp hive_data.csv <ID of Container>:/hive_data.csv

3. Step
Run the python Hive_Connect.py script

4. Step
Run board.py to start the webserver

5. Step
Enjoy the application


Quick overview of the structure:

![This is how the Software is structured](https://github.com/Chipato1/DataWarehouse-FakeNews/blob/main/structure.png)
