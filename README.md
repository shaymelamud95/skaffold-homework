After running the script that creates the folder with the files
Enter the folder on the command line and run
skaffold dev

to deploy prometheus & grfana 
if the installation file did not worked as expected then 
go to the prometheus stuck kub-1.28 folder and follow the RM file

prometheus:

![Alt text](images/image.png)

kube get all:

![Alt text](images/image-1.png)

deployment:

![Alt text](images/image-2.png)

secode deployment:

![Alt text](images/image-4.png)

prometheus service monitor:
![Alt text](images/image-5.png)


grfana:

![Alt text](images/image00.png)

data connection:

![Alt text](images/image-11.png)

default grafana dashboards:

![Alt text](images/image-21.png)

the application is running:

![Alt text](images/image-41.png)

service descovery:

![Alt text](images/image-51.png)

targets in prometheus:

![Alt text](images/image-61.png)