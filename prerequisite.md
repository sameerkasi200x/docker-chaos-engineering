# Working with examples

All the examples have been tested on a UCP cluster. Most of them must work against a Swarm cluster setup using Docker CE too. The setup which was used for tese examples is depicted in this [UCP Architecture Diagram](https://raw.githubusercontent.com/sameerkasi200x/docker-chaos-engineering/master/img/Docker%20Enterprise%20Edition%20-%20EE.png).
Though the examples uses Docker Trusted Registry to manage images but you can do the same with Dockerhub (or mostly any other registry as well).

# Docker EE and UCP
To learn more about UCP and its architecture/features refer to the [docker's guide on gitub](https://github.com/docker/docker.github.io/blob/master/datacenter/ucp/2.2/guides/architecture.md). 

# UCP Client Bundle
To learn more about getting client bundle for cli access check out this [official page](https://github.com/docker/docker.github.io/blob/master/datacenter/ucp/2.2/guides/user/access-ucp/cli-based-access.md). 

# Installation of UCP
You can follow the steps from online [Docker documentation] (https://docs.docker.com/ee/ucp/admin/install/) to do a test setup.


# Docker Trusted Register
Docker Trusted Register is the secure registery offered by Docker for on-prem setup. To understand the architecture and its components you can refer to the [online Documentation](https://docs.docker.com/ee/dtr/architecture/).

# Installing DTR
You can follow the steps from online [Docker documentation] (https://docs.docker.com/ee/dtr/admin/install/) to do a test setup.

# Pumba
Pumba is a nice tool to manage chaos engineering for your docker setup. You can get more info about pubma from 
[1] [github project page](https://github.com/alexei-led/pumba)
[2] [announcement blog](https://hackernoon.com/pumba-chaos-testing-for-docker-1b8815c6b61e)

Download the package suitable for your environment from its [download page](https://github.com/alexei-led/pumba/releases).

