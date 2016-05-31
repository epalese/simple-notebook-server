First steps with Docker
=======================

## Set up an Ubuntu VM
I am working on a Mac and since (quoted from https://docs.docker.com/mac/step_one/)
> Because the Docker Engine daemon uses Linux-specific kernel features, you can’t run Docker Engine natively in OS X. Instead, you must use the Docker Machine command, docker-machine, to create and attach to a small Linux VM on your machine. This VM hosts Docker Engine for you on your Mac.  

I decided to use an Ubuntu VM run in VirtualBox as my playground.  
I downloaded an Ubuntu server ISO from:  
http://www.ubuntu.com/download/server

And I installed it with VirtualBox (https://www.virtualbox.org/wiki/Downloads).  

## Enable SSH to guest VM  
Now I have a fully functional Ubuntu server instance running in VirtualBox. The big problem with this configuration is that (apparently) there is no way to copy and paste text from my hosting OS into the guest VM. So what I need now it to enable ssh connection to the guest VM.  
<br/>

In VirtualBox through the main menu:  
* Go into Preferencs -> Network  
* Select Host-only networks  
* Add new host-only network (a new entry will appear with a name like 'vboxnet0')  
* Click OK  

Now select your Ubuntu Server Guest machine and click on Settings:  
* Go into the Network section  
* Select Adapter 1  
* Attach it to 'Bridge Adapter'  
* In the 'Name' field select the current network adapter that you're using on yout Mac. For me it's 'en1: Wi-Fi (AirPort)'  
* Select Adapter 2  
* Enable it  
* Make it attached to 'Host-only Adapter'. Now the 'Name' field should automatically bet set up to 'vboxnet0'.    
* Click OK  

Now we can restart the Ubuntu VM.    
<br/>
In order to ssh into your VM you need to have openssh-server installed and running. In your VM run:  
```bash
fix@ubuntu:~$ sudo apt-get install openssh-server
...
fix@ubuntu:~$ sudo service sshd start
```
We need also the IP address of the Ubuntu VM if we want to ssh into it:  
```bash
fix@ubuntu:~$ ifconfig
...
enp0s3    Link encap:Ethernet  HWaddr 08:00:27:7d:e4:e8  
          inet addr:192.168.1.129  Bcast:192.168.1.255  Mask:255.255.255.0
          inet6 addr: fe80::a00:27ff:fe7d:e4e8/64 Scope:Link
          UP BROADCAST RUNNING MULTICAST  MTU:1500  Metric:1
          RX packets:582 errors:0 dropped:0 overruns:0 frame:0
          TX packets:112 errors:0 dropped:0 overruns:0 carrier:0
          collisions:0 txqueuelen:1000 
          RX bytes:44065 (44.0 KB)  TX bytes:12203 (12.2 KB)
...
```
Find something similar to 192.xxx.xxx.xxx. In my case it's 192.168.1.129.  
<br/>
So now open a terminal on your Mac and run:  
```bash
Red:~ fix$ ssh fix@192.168.1.129
The authenticity of host '192.168.1.129 (192.168.1.129)' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)? yes
Warning: Permanently added '192.168.1.129' (ECDSA) to the list of known hosts.
fix@192.168.1.129's password: 
Welcome to Ubuntu 16.04 LTS (GNU/Linux 4.4.0-21-generic x86_64)

 * Documentation:  https://help.ubuntu.com/

7 packages can be updated.
7 updates are security updates.


Last login: Mon May 30 19:50:00 2016
fix@ubuntu:~$ 
```
TADAAAAAAA! We are in our Ubuntu server VM. The Main benefit now?!? We can copy and paste from the clipboard.  

## Install Docker
Following the steps outlined here: https://docs.docker.com/linux/step_one/  
```bash
fix@ubuntu:~$ which curl
/usr/bin/curl
fix@ubuntu:~$ curl -fsSL https://get.docker.com/ | sh
...
$ curl -fsSL https://get.docker.com/gpg | sudo apt-key add -
...
```

And then let's test that everything is fine:
```bash
fix@ubuntu:~$ docker run hello-world

Hello from Docker.
This message shows that your installation appears to be working correctly.

To generate this message, Docker took the following steps:
 1. The Docker client contacted the Docker daemon.
 2. The Docker daemon pulled the "hello-world" image from the Docker Hub.
 3. The Docker daemon created a new container from that image which runs the
    executable that produces the output you are currently reading.
 4. The Docker daemon streamed that output to the Docker client, which sent it
    to your terminal.

To try something more ambitious, you can run an Ubuntu container with:
 $ docker run -it ubuntu bash

Share images, automate workflows, and more with a free Docker Hub account:
 https://hub.docker.com

For more examples and ideas, visit:
 https://docs.docker.com/engine/userguide/
```

## Create a custom image
In this section we are going to explore the steps to:  
* create a custom image  
* add the code for a Python-based server application in the custom image  
* run the server  

There are a lot of tutorial out there on  how to create a Docker custom image, like this one for instance:  
https://docs.docker.com/linux/step_four/  

Let's start by creating our working directory:  
```bash
fix@ubuntu:~$ mkdir simple-notebook-server-docker
fix@ubuntu:~$ cd simple-notebook-server-docker/
```

Now we clone the git repo containing the Python server application:  
```bash
fix@ubuntu:~/simple-notebook-server-docker$ git clone https://github.com/epalese/simple-notebook-server.git
Cloning into 'simple-notebook-server'...
remote: Counting objects: 16, done.
remote: Compressing objects: 100% (13/13), done.
remote: Total 16 (delta 2), reused 10 (delta 2), pack-reused 0
Unpacking objects: 100% (16/16), done.
Checking connectivity... done.
```

It is time to create the Dockerfile recipe for our custom image. In order to do this we need to create a file named Dockerfile whose content is the following:
```bash
fix@ubuntu:~/simple-notebook-server-docker$ cat Dockerfile 
# Set the base image to Ubuntu
FROM ubuntu:16.04

MAINTAINER fix

# Update the sources list
RUN apt-get update

# Install Python and pip
RUN apt-get install -y python python-pip

# Copy the server code directory inside the container
ADD /simple-notebook-server /simple-notebook-server

# Get pip to download and install requirements:
RUN pip install -r /simple-notebook-server/requirements.txt

# Expose server port
EXPOSE 3001

# Set the default directory where CMD will execute
WORKDIR /simple-notebook-server

# Set the default command to execute when creating a new container
CMD python server.py --log DEBUG
```

Some notes on Dockerfile:  
* we run 'pip install' because we need to install all the Python packages that the server requires to run;  
* we expose port 3001 because the server listen to that port (you can always edit simple-ntebook-server/server.py and change the port if you don't like it)  


Everything is ready to tell Docker to build the custom image:  
```bash
fix@ubuntu:~/simple-notebook-server-docker$ docker build -t simple-notebook-server-img .
Sending build context to Docker daemon 94.21 kB
Step 1 : FROM ubuntu:16.04
 ---> 2fa927b5cdd3
Step 2 : MAINTAINER fix
 ---> Using cache
 ---> 5f3545d049cc
Step 3 : RUN apt-get update
 ---> Using cache
 ---> 618a71783514
Step 4 : RUN apt-get install -y python python-pip
 ---> Using cache
 ---> 726d473b9636
Step 5 : ADD /simple-notebook-server /simple-notebook-server
 ---> 78b09903f9bb
Removing intermediate container 00df4503040e
Step 6 : RUN pip install -r /simple-notebook-server/requirements.txt
 ---> Running in 6df9a8df470f
Collecting autobahn==0.14.1 (from -r /simple-notebook-server/requirements.txt (line 1))
  Downloading autobahn-0.14.1-py2.py3-none-any.whl (229kB)
Collecting Twisted==16.2.0 (from -r /simple-notebook-server/requirements.txt (line 2))
  Downloading Twisted-16.2.0.tar.bz2 (2.9MB)
Collecting six>=1.10.0 (from autobahn==0.14.1->-r /simple-notebook-server/requirements.txt (line 1))
  Downloading six-1.10.0-py2.py3-none-any.whl
Collecting txaio>=2.5.1 (from autobahn==0.14.1->-r /simple-notebook-server/requirements.txt (line 1))
  Downloading txaio-2.5.1-py2.py3-none-any.whl
Collecting zope.interface>=3.6.0 (from Twisted==16.2.0->-r /simple-notebook-server/requirements.txt (line 2))
  Downloading zope.interface-4.1.3.tar.gz (141kB)
Requirement already satisfied (use --upgrade to upgrade): setuptools in /usr/lib/python2.7/dist-packages (from zope.interface>=3.6.0->Twisted==16.2.0->-r /simple-notebook-server/requirements.txt (line 2))
Building wheels for collected packages: Twisted, zope.interface
  Running setup.py bdist_wheel for Twisted: started
  Running setup.py bdist_wheel for Twisted: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/fe/9d/3f/9f7b1c768889796c01929abb7cdfa2a9cdd32bae64eb7aa239
  Running setup.py bdist_wheel for zope.interface: started
  Running setup.py bdist_wheel for zope.interface: finished with status 'done'
  Stored in directory: /root/.cache/pip/wheels/52/04/ad/12c971c57ca6ee5e6d77019c7a1b93105b1460d8c2db6e4ef1
Successfully built Twisted zope.interface
Installing collected packages: six, txaio, autobahn, zope.interface, Twisted
Successfully installed Twisted-16.2.0 autobahn-0.14.1 six-1.10.0 txaio-2.5.1 zope.interface-4.1.3
You are using pip version 8.1.1, however version 8.1.2 is available.
You should consider upgrading via the 'pip install --upgrade pip' command.
 ---> 5a1e68301280
Removing intermediate container 6df9a8df470f
Step 7 : EXPOSE 3001
 ---> Running in 6168394a6956
 ---> b0ac22f15ee4
Removing intermediate container 6168394a6956
Step 8 : WORKDIR /simple-notebook-server
 ---> Running in 88e23181f6ef
 ---> b8a7dd78583b
Removing intermediate container 88e23181f6ef
Step 9 : CMD python server.py
 ---> Running in 82f357f792fe
 ---> 0b05274f958b
Removing intermediate container 82f357f792fe
Successfully built 0b05274f958b
fix@ubuntu:~/simple-notebook-server-docker$ 
``` 
Your output might be different if docker needs to download and build the ubuntu base image (I've already installed it on my VM so in this case docker is smart enough to not download it again).

As the last steps we are going to run the brand new custom image:
```bash
fix@ubuntu:~/simple-notebook-server-docker$ docker run -p 3001:3001 -i -t simple-notebook-server-img
2016-05-31 11:19:05+0000 [-] Log opened.
2016-05-31 11:19:05+0000 [-] WebSocketServerFactory starting on 3001
2016-05-31 11:19:05+0000 [-] Starting factory <autobahn.twisted.websocket.WebSocketServerFactory object at 0x7f3aade40cd0>
```
If you see the previous output this means that simple-notebook-server is happily running in a docker container.  

If you want to check if it is actually working you can:
* clone the repo on your machine  
* open in a web browser simple-notebook-server/index.html  
* in the Websocket address field specify the IP address of your ubuntu-server VM (i.e. ws://192.168.1.129:3001)  
* click on connect  
* execute some Python code  
