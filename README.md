# Chaos Engineering with Docker EE
 
## Why Chaos Engineering?

Even before we get into the definition of Chaos Engineering or why it has become important, let's take a look at traditional approach. Most of the applications and configuration would be put under stress testing to find out the breakage point. This primarily helped to assure the operations team that the provisioned capacity is enough for the anticipated workload. The tests was relatively (if not fairly) simple to do. But with time there are couple of things that has changed:
 
 1. System have become more and more complex now
 2. Workloads can change abruptly and scaling up and down is a necessity now
 
Also, there is a philosophical shift happenning the way IT operations used to think -
 
 1. Servers are disposable - Earlier the basic deployment units (in most cases physical or virtual servers) were treated like "Pets" and the [configuration changes would lead to a snowflake](https://martinfowler.com/bliki/SnowflakeServer.html). Now with configuration management tools servers are disposable like "cattles" and can be resurrected from scratch if there is a configuration change aka [Pheonix Servers](https://martinfowler.com/bliki/PhoenixServer.html).

 2. Failure have been accepted as business as usual, outages are not. I am not trying to force you to accept system failures, but most of the IT operations today acknowledges that things would go wrong. Simply put, one needs to be prepared for it.

 3. Because of the explosion of internet, services are not limited by geographies any more. Workloads are not predictible any more and they are bound to go beyond the breakage point of one servers, it is just a matter of time and chance. 

 4. Complexity of applications has increased multi-fold. Today applications are not just three tier deployments. A web page rednered might be working with 10s or in some cases 100s of micro-services in the backend. Only way test the resiliency of the system is by injecting random issues on purpose. 
 
This all lead the IT Operation leads to be convinced that the best way to be prepared for an outage is to simulate one. If you are not convinced yet, perhaps you want to read a bit about the study of [how much loss the business can suffer because of infrastructure outage](https://www.zdnet.com/article/cloud-computing-heres-how-much-a-huge-outage-could-cost-you/).


## How do you go about it?
So what should be your strategy? I believe the easiest way is to introduce unit testing and integration testing for infrastructure and architecture components too, just like application code. so for any kind of High Availability or Disaster Recovery approach you have implemented, you should have a test case. e.g. if you are having a cluster with 2 nodes, your test case could be be shoot down one of the node. Yes, you read it right. I am suggesting that you should take down a node. There is no other way for you to test high availability but to simulate failure. Similarly you can test scalability but injecting slowness and network congetion. 

There are many popular examples and inspirations for Chaos Injection. Most popular one are:
 1. Generic guidelines are available on [Principles of Chaos Engineering](http://principlesofchaos.org)
 2. Netflix's [Chaos Monkey](https://github.com/Netflix/chaosmonkey) to do various kind of chaos injection e.g. introduce slowness in the network, kill EC2 instances, detach the network or disks from EC2 instances
 2. Netflix's [Chaos Kong](https://medium.com/netflix-techblog/chaos-engineering-upgraded-878d341f15fa) though is not open sourced yet but a nice inspiration and aspiration for anyone embarking on chaos engineering within their enterprise.
 3. [Facebook's Project Storm](https://siliconangle.com/blog/2016/08/31/meet-project-storm-facebooks-swat-team-for-disaster-proofing-data-centers/)

Those who practice chaos engineering by trying to break themselves, have been rewarded well in times of outages. Best example is how [Netflix weathered the storm by preparing for the worst](https://www.techrepublic.com/article/aws-outage-how-netflix-weathered-the-storm-by-preparing-for-the-worst/).

## How does that translate in the container's world?

In today's date a lot of new applications and services are being deployed as containers. If you are starting up with Chaos Engineering in Docker, there are many different mechanisms and tools available at your disposal.

Before we get into tools, let's look at some of the basic features of Docker which should be helpful to you.

### 1. Docker Service 
 
It is often better to deploy your application as a Swarm Service instead of deploying them as native container. In case you are using Kubernetes, it is better to deploy your request as a sevice. Both the definitions are declarative and define the desired state of service. This is really helpful in maintaining the uptime of your application as the service would always try to maintain the availability of service.

#### Example: ####
In this example, I am going to use a Dockerfile to build a new image and then I will be using it to deploy a new service. The example is executed against a Docker UCP cluster from a client node (with docker cli and UCP Client Bundle).

Setup a docker build file [```Dockerfile-nohc```](https://raw.githubusercontent.com/sameerkasi200x/docker-chaos-engineering/master/code/Dockerfile-nohc):

    FROM nginx:latest
    RUN apt-get -qq update
    COPY index.html /usr/share/nginx/html
    EXPOSE 80 443
    CMD ["nginx", "-g", "daemon off;"]

Build your image Image

    sh-4.2$ docker image build -t $dtr_url/development/tweet_to_us:demoMay -f Dockerfile-nohc .
    Sending build context to Docker daemon  4.096kB
    ip-10-100-2-106: Step 1/4 : FROM nginx:latest
    ip-10-100-2-106:  ---> ae513a47849c
    ip-10-100-2-106: Step 2/4 : COPY index.html /usr/share/nginx/html
    ip-10-100-2-106:  ---> Using cache
    ip-10-100-2-106:  ---> b97207424f3a
    ip-10-100-2-106: Step 3/4 : EXPOSE 80 443
    ip-10-100-2-106:  ---> Using cache
    ip-10-100-2-106:  ---> bfe4f59a2094
    ip-10-100-2-106: Step 4/4 : CMD nginx -g daemon off;
    ip-10-100-2-106:  ---> Using cache
    ip-10-100-2-106:  ---> cb79c6283bb5
    ip-10-100-2-106: Successfully built cb79c6283bb5
    ip-10-100-2-106: Successfully tagged dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay


Now we need to push you image to a repository (DTR or Dockerhub), so that it is available to all nodes:

	sh-4.2$ docker image push $dtr_url/development/tweet_to_us:demoMay
	The push refers to a repository [dtr.ashnikdemo.com:12443/development/tweet_to_us]
	c75bed55c5fa: Pushed
	7ab428981537: Mounted from development/tweet-to-us
	82b81d779f83: Mounted from development/tweet-to-us
	d626a8ad97a1: Mounted from development/tweet-to-us
	demoMay: digest: sha256:08090c853df56ceee495fb95537ac9f2c81cf8718e5fc76c513ba1d8e7d145f0 size: 1155

Now we will start a service using this image:

	sh-4.2$ docker service create -d --name=twet-app --mode=replicated --replicas=2 --publish 8080:80  dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay
	pq6eojqprru4ctw0ib0lwfmj6

This request asks the Swarm cluster to setup the service with ```--mode=replicated``` and ```--replicas=2``` i.e. Swarm would try to maintain two tasks for this service at any point of time, unless requested otherwise by the user. You can inspect the tasks running for the service with ```docker service ps``` command:

	sh-4.2$ docker service ps twet-app
	ID                  NAME                IMAGE                                                      NODE                DESIRED STATE       CURRENT STATE           ERROR               PORTS
	zzq1jgolcc2o        twet-app.1          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   ip-10-100-2-67      Running             Running 3 minutes ago
	zlkf4ejuxus8        twet-app.2          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   ip-10-100-2-93      Running             Running 3 minutes ago
 
As you can see there are two tasks running and these tasks would be setup with VIP which will do load-balancing among the two containers/tasks.

	sh-4.2$ docker service inspect --format='{{.Endpoint}}'  twet-app
	{{vip [{ tcp 80 8080 ingress}]} [{ tcp 80 8080 ingress}] [{f80zlxoy56y20ql48o3v9aiwo 10.255.0.225/16}]}


Let's try to kill one of the underlying containers and see if Swarm is able to maintain the declarative state we had requested:

	sh-4.2$ docker container ls | grep -i twet-app
	603c7f8940fe        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   "nginx -g 'daemon ..."   7 minutes ago       Up 7 minutes        80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.1.zzq1jgolcc2oyucexn4j9u9pq
	54aa164ea509        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   "nginx -g 'daemon ..."   7 minutes ago       Up 7 minutes        80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.2.zlkf4ejuxus851onp4i2t143p
	sh-4.2$
	sh-4.2$ docker container kill 603c7f8940fe
	603c7f8940fe
	sh-4.2$
	sh-4.2$
	sh-4.2$ docker service ps twet-app
	ID                  NAME                IMAGE                                                      NODE                DESIRED STATE       CURRENT STATE           ERROR                         PORTS
	sp4hz64oytu0        twet-app.1          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   ip-10-100-2-67      Running             Running 2 seconds ago
	zzq1jgolcc2o         \_ twet-app.1      dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   ip-10-100-2-67      Shutdown            Failed 7 seconds ago    "task: non-zero exit (137)"
	zlkf4ejuxus8        twet-app.2          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay   ip-10-100-2-93      Running             Running 8 minutes ago
	sh-4.2$

As you can see the container ```603c7f8940fe``` was used by one of the tasks of our service ```twet-app``` and once we kill the container, Swarm tries to maintain the state by starting another task. 


**Note:** Pushing image to repository is needed when you are running with distributed setup. As you can see above in the build was done on one of the nodes from the Swarm cluster```ip-10-100-2-106``` and image would be only available on only one node. Hence if we were to run service without pushing the image to a repository, there is good chance that the tasks would get started on the same node (```ip-10-100-2-106```) i.e. the only node that has access to the image or different nodes would get different images (left by different image builds). Swarm does a good job of reminding us about this. Here is an example if I tried to run the servie without pushing the image:

	sh-4.2$ docker service create -d --name=twet-app --mode=replicated --replicas=2 --publish 8080:80  dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay
	image dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay could not be accessed on a registry to record
	its digest. Each node will access dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay independently,
	possibly leading to different nodes running different
	versions of the image.

	t46gb1wi3tc7xs2j08egzcut1

### 2. Health Checks
Docker allows you to use healthcheck to keep a tab on the health of running containers. The healthcheck can be either baked into you image during the build process using ```HEALTHCHECK``` direction in Dockerfile or during runtime using --healthcheck option with ```docker service create``` or ```docker container run```


To quote the [docker documentation](https://docs.docker.com/engine/reference/builder/#healthcheck)

> The ```HEALTHCHECK``` instruction tells Docker how to test a container to check that it is still working. This can detect cases such as a web server that is stuck in an infinite loop and unable to handle new connections, even though the server process is still running.

**Note:** The ```HEALTHCHECK``` feature was added in Docker 1.12.

#### Build time example of HEALTHCHECK ####
To make use of this feature we will add a new command to our [```Dockerfile```](https://raw.githubusercontent.com/sameerkasi200x/docker-chaos-engineering/master/code/Dockerfile) now

	HEALTHCHECK --interval=30s --timeout=3s --retries=2 \ 
	    CMD  python /usr/share/nginx/html/healthcheck.py || exit 1

This means that the healthcheck command ```python /usr/share/nginx/html/healthcheck.py``` will be run for the first time after ```30s``` i.e. 30 seconds after starting up the tasks. The healthcheck will be run with an ```interval``` of every 30s after that. The healthcheck would ```timeout``` in ```3s``` and upon failure of ```2 retries``` the container will be declared unhealthy.


We will have to add a few new files to support HEALTHCHECK 
+ [```healthcheck.py```](https://raw.githubusercontent.com/sameerkasi200x/docker-chaos-engineering/master/code/healthcheck.py) - our own little piece of code to check the health of container.
+ [```healthcheck.html```](https://raw.githubusercontent.com/sameerkasi200x/docker-chaos-engineering/master/code/healthcheck.html)

Now we will build and push the image

	sh-4.2# docker image build --no-cache -t $dtr_url/development/tweet_to_us:demoMay_Healthcheck -f Dockerfile .
	Sending build context to Docker daemon   7.68kB
	Step 1/7 : FROM nginx:latest
	 ---> b175e7467d66
	Step 2/7 : RUN apt-get -qq update
	 ---> Running in 152a3156632c
	 ---> 2a6be94d9a04
	Removing intermediate container 152a3156632c
	Step 3/7 : RUN apt-get -qq --allow-downgrades --allow-remove-essential --allow-change-held-packages install python > /dev/null
	 ---> Running in 56a5b9141aaf
	debconf: delaying package configuration, since apt-utils is not installed
	 ---> 99605506e79f
	Removing intermediate container 56a5b9141aaf
	Step 4/7 : COPY healthcheck.html healthcheck.py index.html /usr/share/nginx/html/
	 ---> b1b93b73d0fa
	Removing intermediate container dab1d03a75e4
	Step 5/7 : EXPOSE 80 443
	 ---> Running in 50b63022a6c3
	 ---> 4297f32f769b
	Removing intermediate container 50b63022a6c3
	Step 6/7 : HEALTHCHECK --interval=30s --timeout=3s --retries=2 CMD python /usr/share/nginx/html/healthcheck.py || exit 1
	 ---> Running in 1a1a9cd1f139
	 ---> 042010177008
	Removing intermediate container 1a1a9cd1f139
	Step 7/7 : CMD nginx -g daemon off;
	 ---> Running in 767a8098f177
	 ---> 9153fcd78222
	Removing intermediate container 767a8098f177
	Successfully built 9153fcd78222
	Successfully tagged dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck
	
	sh-4.2# docker image push dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck
	The push refers to a repository [dtr.ashnikdemo.com:12443/development/tweet_to_us]
	a60e00b623bb: Pushed
	2e83bcd5bc8d: Pushed
	5134599f00a1: Pushed
	77e23640b533: Pushed
	757d7bb101da: Pushed
	3358360aedad: Pushed
	demoMay_Healthcheck: digest: sha256:a4fb4fd2733e37ae7282148ccb497aac4c2fc18a74aa8e950271ffd648b07da8 size: 1579


Now once we deploy the service, initially the health status would be ```starting``` until the first healthcheck is initiated

	sh-4.2$ docker service rm twet-app
	twet-app
	
	sh-4.2$ docker service create -d --name=twet-app --mode=replicated --replicas=2 --publish 8080:80  dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck
	lbfmu7vxa1i6arfmpstzq3rer

	sh-4.2$ docker container ls | grep -i twet
	1feb5ed8e0b6        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   23 seconds ago      Up 23 seconds (health: starting)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.2.rkh6gofzfru83wjqcyzq2mdcl
	6ccb4d691fe9        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   24 seconds ago      Up 23 seconds (health: starting)   80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.1.urb4v2vttrlsvcz11wfnj6yh2

After the first healthechk, the healthcheck status would be ```healthy```

	sh-4.2$ docker container ls | grep -i twet
	1feb5ed8e0b6        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   About a minute ago   Up About a minute (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.2.rkh6gofzfru83wjqcyzq2mdcl
	6ccb4d691fe9        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   About a minute ago   Up About a minute (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.1.urb4v2vttrlsvcz11wfnj6yh2 



#### Testing Healthcheck and self-healing ####
Now let's try to force a distruption by connecting to one of the containers and changing the content of ```healthcheck.html```

	sh-4.2$ docker container exec -it 1feb5ed8e0b6 bash
	root@1feb5ed8e0b6:/# echo test > /usr/share/nginx/html/healthcheck.html
	root@1feb5ed8e0b6:/# exit


Soon (in about 1 minute given our ```interval```, ```timeout``` and ```retries``` configuration in the Dockerfile), the container will be reported unhealthy and replaced with a new container to run the task


	sh-4.2$ docker container ls | grep -i twet
	1feb5ed8e0b6        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   3 minutes ago       Up 13 minutes (unhealthy)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.2.xskxfd9n6e39wlghpm0k7tphr
	6ccb4d691fe9        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   13 minutes ago      Up 13 minutes (healthy)    80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.1.urb4v2vttrlsvcz11wfnj6yh2

	sh-4.2$ docker container ls -a | grep -i twet
	efc5b969ef8c        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   42 seconds ago      Up 36 seconds (healthy)          80/tcp, 443/tcp                                                                             ip-10-100-2-93/twet-app.2.xskxfd9n6e39wlghpm0k7tphr
	1feb5ed8e0b6        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago      Exited (0) 41 seconds ago                                                                                                    ip-10-100-2-93/twet-app.2.rkh6gofzfru83wjqcyzq2mdcl
	6ccb4d691fe9        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago      Up 11 minutes (healthy)          80/tcp, 443/tcp                                                                             ip-10-100-2-67/twet-app.1.urb4v2vttrlsvcz11wfnj6yh2 


#### Runtime definition of Healthcheck ####
You can also override the command to check health, its frequency and retries while creating the service

	sh-4.2$ docker service rm twet-app
	twet-app

	sh-4.2$ docker service create -d --name=twet-app \
	  --mode=replicated --replicas=2 --publish 8080:80 \
	  --health-cmd "python /usr/share/nginx/html/healthcheck.py || exit 1" \
	  --health-interval 10s \
	  --health-retries 2 \
	  --health-timeout 30ms \
	  dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck

	mj4lel34whrvupscq8sjt7g5m

#### Disable healthcheck ####

In runtime while creating a service, you can disable the healtcheck with ```--no-healthcheck``` option. That will supress any healthcheck which has been defined in the base image

	sh-4.2$ docker service create -d --name=twet-app \
	        --mode=replicated --replicas=2 --publish 8080:80 \
	        --no-healthcheck \
	        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck
	
	nxkv39smzq5k0o9tgwmc74t2c


If the base container you are going to use has a ```HEALTHCHECK``` defined, it can also disable the healthchek during build time using ```HEALTHCHECK NONE``` 

#### Checking the status ####
You can use ```docker container inspect``` command to further review the state of your containers and details healthchekc command output:

e.g. in case of timeout error:

	sh-4.2$ docker container inspect --format='{{json .State.Health}}' a9486dc964af
	{"Status":"starting","FailingStreak":1,"Log":[{"Start":"2018-05-12T17:18:01.698087531Z","End":"2018-05-12T17:18:01.728282187Z","ExitCode":-1,"Output":"Health check exceeded timeout (30ms)"}]}

in case of failures:

	sh-4.2$ docker container inspect --format='{{json .State.Health}}' 62ad34709fb8
	{"Status":"healthy","FailingStreak":1,"Log":[{"Start":"2018-05-12T17:28:33.714393794Z","End":"2018-05-12T17:28:33.793534206Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:28:53.793900452Z","End":"2018-05-12T17:28:53.871217425Z","ExitCode":1,"Output":"The content of the healthcheck did not match. Expected Content-\"healthy\", we got: test\n"}]}

	sh-4.2$ docker container inspect --format='{{json .State.Health}}' 62ad34709fb8
	{"Status":"unhealthy","FailingStreak":2,"Log":[{"Start":"2018-05-12T17:28:33.714393794Z","End":"2018-05-12T17:28:33.793534206Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:28:53.793900452Z","End":"2018-05-12T17:28:53.871217425Z","ExitCode":1,"Output":"The content of the healthcheck did not match. Expected Content-\"healthy\", we got: test\n"},{"Start":"2018-05-12T17:29:13.871399894Z","End":"2018-05-12T17:29:13.948097443Z","ExitCode":1,"Output":"The content of the healthcheck did not match. Expected Content-\"healthy\", we got: test\n"}]}

in case of no failures

	sh-4.2$ docker container inspect --format='{{json .State.Health}}' 181d566f6aa9
	{"Status":"healthy","FailingStreak":0,"Log":[{"Start":"2018-05-12T17:25:06.184822447Z","End":"2018-05-12T17:25:06.262241844Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:25:26.262408086Z","End":"2018-05-12T17:25:26.338883823Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:25:46.339143953Z","End":"2018-05-12T17:25:46.416973058Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:26:06.417170336Z","End":"2018-05-12T17:26:06.495295881Z","ExitCode":0,"Output":""},{"Start":"2018-05-12T17:26:26.495482044Z","End":"2018-05-12T17:26:26.572278146Z","ExitCode":0,"Output":""}]}


	
Note: The output will contain a friendly message if one is printed by your healthcheck command.


### 3. Tooling and Automation 
Now that we have covered the basic building blocks of chaos engineering with Docker, let's try to take a look at some tools. Pumba is a fairly new but quite promising tool for chaos orchestration. Best thing is it works well with a Swarm cluster, you just need to point it to the manager node. We can easily get it to work with Docker UCP Client Bundle. 



#### Example

First we need to setup an isolated network where we will setup our application and test it out
	 docker network create -d overlay tweet-app-net

Now let's setup a service using healthcheck from the previous examples
	
	docker service create -d --name=twet-app --network tweet-app-net \
	  --mode=replicated --replicas=2 --publish 8080:80 \
	  --health-cmd "python /usr/share/nginx/html/healthcheck.py || exit 1" \
	  --health-interval 20s \
	  --health-retries 2 \
	  --health-timeout 200ms \
	  dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck

Let's ensure that the service has been started properly with requested number of replicas which are healthy

	sh-4.2$ docker container ls | grep -i twet
	75b2bf6f219d        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   27 seconds ago       Up 21 seconds (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.1.im7f7qm2xh6fk6uqla462qzia
	393355d083fb        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   About a minute ago   Up 59 seconds (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.2.6uueh28nxj7btpfzffeq40f6b

Now let's use pumba to randomly kill some containers under the service 

	export SVC_NAME=twet-app
    pumba --random kill  $(docker service ps --no-trunc \
       --filter "desired-state=Running"  \
        ${SVC_NAME} | awk ' {if (NR!=1) {print $2"."$1} } ')


You will an output confirming that the container has been killed

	sh-4.2$     pumba --random kill  $(docker service ps --no-trunc \
	       --filter "desired-state=Running"  \
	        ${SVC_NAME} | awk ' {if (NR!=1) {print $2"."$1} } ')
	INFO[0000] Kill containers
	INFO[0003] Killing /twet-app.2.6uueh28nxj7btpfzffeq40f6b (393355d083fbd33d8247e6cf9dcdb36046000764547db776b405bb4c37ef7438) with signal SIGKILL

You will notice that as soon as the container is killed, the swarm manager would try to restore the state back to desired state i.e. with 2 healthy replica

	sh-4.2$ docker container ls | grep -i twet
	75b2bf6f219d        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   42 seconds ago      Up 36 seconds (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.1.im7f7qm2xh6fk6uqla462qzia
	sh-4.2$ docker container ls | grep -i twet
	75b2bf6f219d        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   44 seconds ago      Up 38 seconds (healthy)   80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.1.im7f7qm2xh6fk6uqla462qzia
	sh-4.2$
	sh-4.2$ docker container ls | grep -i twet
	dfb8b7ebc559        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   7 seconds ago       Up 1 seconds (health: starting)   80/tcp, 443/tcp                                           ip-10-100-2-67/twet-app.2.7505c070tcyk14wudbdbufy3t
	75b2bf6f219d        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   47 seconds ago      Up 41 seconds (healthy)           80/tcp, 443/tcp                                           ip-10-100-2-93/twet-app.1.im7f7qm2xh6fk6uqla462qzia


You can also try to stop or remove a container various commands provided by ```pumba```.

You can also use ```--interval``` option to run the command at a regular interval to perform stress testing. e.g. to run the same kill command every 10minutes

	export SVC_NAME=twet-app
    pumba --random --interval 10m kill  $(docker service ps --no-trunc \
       --filter "desired-state=Running"  \
        ${SVC_NAME} | awk ' {if (NR!=1) {print $2"."$1} } ')

#### Network delay
Let's first take example of a simple setup with a single node.

	docker swarm init


Setup the service by running this command aginst the single manager node of your newly initiated Swarm Cluster

	sh-4.2# docker service create -d --name=twet-app --network tweet-app-net   --mode=replicated --replicas=2 --publish 8080:80   --health-cmd "python /usr/share/nginx/html/healthcheck.py || exit 1"   --health-interval 10s   --health-retries 2   --health-timeout 100ms   dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck
	image dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck could not be accessed on a registry to record
	its digest. Each node will access dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck independently,
	possibly leading to different nodes running different
	versions of the image.
	
	pb7teb13m2oczlp8rub0wjkdo

Fire a pumba command to introduce delays

	sh-4.2# pumba --random netem --interface lo --duration 60s    --tc-image gaiadocker/iproute2 delay    --time 10 jitter 100    --distribution normal $(docker service ps --no-trunc \
	   --filter "desired-state=Running"  \
	    ${SVC_NAME} | awk ' {if (NR!=1) {print $2"."$1} } ')
	INFO[0000] netem: delay for containers
	INFO[0000] Running netem command '[delay 10ms 10ms 20.00]' on container 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c for 1m0s
	INFO[0000] Start netem for container 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c on 'lo' with command '[delay 10ms 10ms 20.00]'


Monitor the status for containers running the of for the service:

	sh-4.2# docker container ls | grep  twet-app
	2eb65f467edc        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   About a minute ago   Up About a minute (healthy)   80/tcp, 443/tcp     twet-app.2.eyxe2yo9fs928b6x2oa3q26m0
	031b9ec08b50        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago       Up 11 minutes (healthy)       80/tcp, 443/tcp     twet-app.1.k6wfqvzyn5p7ka60witz92msv

You will notice that becuase of the network delays introduced by pumba, the containers are failing the healthcheck:

	sh-4.2# docker container ls | grep  twet-app
	2eb65f467edc        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   About a minute ago   Up About a minute (unhealthy)   80/tcp, 443/tcp     twet-app.2.eyxe2yo9fs928b6x2oa3q26m0
	031b9ec08b50        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago       Up 11 minutes (healthy)         80/tcp, 443/tcp     twet-app.1.k6wfqvzyn5p7ka60witz92msv

Soon the unhealthy container would be removed:

	sh-4.2# docker container ls | grep  twet-app
	031b9ec08b50        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago      Up 11 minutes (healthy)   80/tcp, 443/tcp     twet-app.1.k6wfqvzyn5p7ka60witz92msv

And it will be replaced with a new container:

	sh-4.2# docker container ls | grep  twet-app
	2c1453b4d680        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   5 seconds ago       Up Less than a second (health: starting)   80/tcp, 443/tcp     twet-app.2.oc900fzo7a7v1kgz2kt45h1pr
	031b9ec08b50        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago      Up 11 minutes (healthy)                    80/tcp, 443/tcp     twet-app.1.k6wfqvzyn5p7ka60witz92msv

As soon as the healthcheck is executed, it will turn into a healthy one:

	sh-4.2# docker container ls | grep  twet-app
	2c1453b4d680        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   20 seconds ago      Up 15 seconds (healthy)   80/tcp, 443/tcp     twet-app.2.oc900fzo7a7v1kgz2kt45h1pr
	031b9ec08b50        dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   "nginx -g 'daemon ..."   11 minutes ago      Up 11 minutes (healthy)   80/tcp, 443/tcp     twet-app.1.k6wfqvzyn5p7ka60witz92msv
	sh-4.2#

While the container is being replaced, you will notice that pumba command would fail (as the container it attached to has been lost)  

	INFO[0060] Stopping netem on container 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c
	INFO[0060] Stop netem for container 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c on 'lo'
	ERRO[0060] Error response from daemon: cannot join network of a non running container: 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c
	ERRO[0060] Error response from daemon: cannot join network of a non running container: 2eb65f467edc585e586feee01d3eba36c301bb3830a9e163e81aa4edf8d5f36c


As you can see, pumba was able to introduce network delay and ```HEALTHCHECK``` in the image or ```--health-cmd``` at service level helped us to restart the images which were slowing. Well, at this time this is the most that Pumba and Swarm can do. I am hoping in times to come, Swarm service healthcheck would allow us to define auto-scale policies too.

Now, if we are running against a UCP setup or any "true" swarm cluster which has worker and manager nodes, pumba netem command would not work when you fire it from a client. This is unlike the kill command (or most of the other pumba commands), which do work against a Swarm cluster. I came up with a simple solution to work around it.

#### Pumba in a container
Well you can run pubma in a container as the example says on it's [github page](https://github.com/alexei-led/pumba).


> ```# once in a 10 seconds, try to kill (with `SIGTERM` signal) all containers named **hp(something)**```
> ``` # on same Docker host, where Pumba container is running```
> ```$ docker run -d -v /var/run/docker.sock:/var/run/docker.sock gaiaadm/pumba pumba --interval 10s kill --signal SIGTERM ^hp```

This means that we can create, a service that runs on each node in your Swarm cluster and executes pumba netem command. We need to change the ```entrypoint``` of the service and mount ```/var/run/docker.sock``` of the local node to container so that pumba can have access to docker deamon on each node. 

The pumba command should essentially look for containers that belong to your service only so you need to pass a list of containers to entrypoint pumba command.
	export container_list=$(docker service ps --no-trunc --filter "desired-state=Running" ${SVC_NAME} | awk ' {if (NR!=1) {print $2"."$1} } ')

The command should try to inject delay only in specific interface i.e. the one used by ```HEALTHCHECK```.

export netem_interface=lo


Now let's run our pumba netem service

	docker service create -d --restart-condition none --mode global --name pumba-netem-delay \
	   --mount type=bind,source=/var/run/docker.sock,destination=/var/run/docker.sock \
	   --entrypoint "pumba --random netem --interface ${netem_interface} --duration 60s \
	   --tc-image gaiadocker/iproute2 delay \
	   --time 10 jitter 100 \
	   --distribution normal ${container_list}" \
	   gaiaadm/pumba 

The effect will be same as the previous example we run on one node Swarm Cluster.  

If you are scripting this, then introduce a delay and then cleanup the swarm service:

	sleep 60
	docker service rm pumba-netem-delay

#### Simulate Packet loss
To be added


#### The bold test - Node failure
One of the reasont to run your containers in a Swarm cluster is to ensure fault tolderance to node failrues. Let's try to simulate node failure and see how docker UCP manager handles it.

Let's first list various tasks of our application:

	docker service ps twet-app

Output would something like below, giving you details of the number of tasks, their id and node on which they are running:

	ID                  NAME                IMAGE                                                                  NODE                DESIRED STATE       CURRENT STATE            ERROR               PORTS
	s8iib1ue7nrd        twet-app.1          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   ip-10-100-2-67      Running             Running 42 minutes ago
	oiafp1o6klxx        twet-app.2          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   ip-10-100-2-93      Running             Running 42 minutes ago


For the purpose of our testing let's try to fail one of the nodes, let's say ```ip-10-100-2-67```.



Since I am running in AWS, I will find out the instance id of the server and restart. We can use ```docker node ls``` before and after restart, to note the node status


	sh-4.2$ docker node ls
	ID                            HOSTNAME                                         STATUS              AVAILABILITY        MANAGER STATUS
	3du1xn000h3jz3t2fcx9lcvdl     ip-10-100-2-38                                   Ready               Active
	ag12n6ejw7ztf0yqpsao4208u     ip-10-100-2-115                                  Ready               Active
	awql5xr67h0jmxjllzfohqqy2 *   ip-10-100-2-15                                   Ready               Active              Reachable
	e2soqi2u67nfnoxop8mgfvm7a     ip-10-100-2-169                                  Ready               Active              Reachable
	i2fjh10bx31ij6i3q2jvzwjco     ip-10-100-2-40                                   Ready               Active              Leader
	lpi6z3np5vp83vatmh51d3i59     ip-10-100-2-106                                  Ready               Active
	m4j4g27conj199uciw98k5h1b     ip-10-100-2-67                                   Ready               Active
	mzwnamamkze7yagqa602tmd71     ip-10-100-2-93                                   Ready               Active
	o3z2xxqo90mm4dlnpq632zorj     ip-10-100-2-66                                   Ready               Active
	yczj5bg55l37xfkugkwwyc5ji     ip-10-100-2-70.ap-southeast-1.compute.internal   Ready               Active

	sh-4.2$ aws ec2 describe-instances --filters "Name=network-interface.private-dns-name,Values=ip-10-100-2-67.ap-southeast-1.compute.internal" | grep -i InstanceId
	                    "InstanceId": "i-0db2edf9253157f97",

	sh-4.2$ aws ec2 reboot-instances --instance-ids  i-0db2edf9253157f97

	sh-4.2$ docker node ls
	ID                            HOSTNAME                                         STATUS              AVAILABILITY        MANAGER STATUS
	3du1xn000h3jz3t2fcx9lcvdl     ip-10-100-2-38                                   Ready               Active
	ag12n6ejw7ztf0yqpsao4208u     ip-10-100-2-115                                  Ready               Active
	awql5xr67h0jmxjllzfohqqy2     ip-10-100-2-15                                   Ready               Active              Reachable
	e2soqi2u67nfnoxop8mgfvm7a *   ip-10-100-2-169                                  Ready               Active              Reachable
	i2fjh10bx31ij6i3q2jvzwjco     ip-10-100-2-40                                   Ready               Active              Leader
	lpi6z3np5vp83vatmh51d3i59     ip-10-100-2-106                                  Ready               Active
	m4j4g27conj199uciw98k5h1b     ip-10-100-2-67                                   Down                Active
	mzwnamamkze7yagqa602tmd71     ip-10-100-2-93                                   Ready               Active
	o3z2xxqo90mm4dlnpq632zorj     ip-10-100-2-66                                   Ready               Active
	yczj5bg55l37xfkugkwwyc5ji     ip-10-100-2-70.ap-southeast-1.compute.internal   Ready               Active
	sh-4.2$


As you can see the node became unavailable once the reboot was executed

In order to maintain the desired state of service with 2 replica, Swarm manager would start a new container on one of the surviving nodes

	sh-4.2$ docker service ps twet-app
	ID                  NAME                IMAGE                                                                  NODE                        DESIRED STATE       CURRENT STATE               ERROR               PORTS
	7e2icqhk0n54        twet-app.1          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   ip-10-100-2-93              Running             Running 12 seconds ago
	s8iib1ue7nrd         \_ twet-app.1      dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   m4j4g27conj199uciw98k5h1b   Shutdown            Running 50 seconds ago
	oiafp1o6klxx        twet-app.2          dtr.ashnikdemo.com:12443/development/tweet_to_us:demoMay_Healthcheck   ip-10-100-2-93              Running
