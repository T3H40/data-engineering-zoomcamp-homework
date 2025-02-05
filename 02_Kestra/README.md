# Week 2 - Kestra
Kestra is an orchestrating tool, allowing for defining pipelines to collect, structure and refine data.

You can run it using docker:
```
docker run --privileged -it -p 8080:8080 --user=root -v /var/run/docker.sock:/var/run/docker.sock -v /tmp:/tmp kestra/kestra:latest server local
```