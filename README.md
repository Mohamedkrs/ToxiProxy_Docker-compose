# Why?
Test and configure [Toxiproxy](https://github.com/Shopify/toxiproxy) to simulate bad network connections.
One of the testcases was to inject the toxic periodicly and with breaks between them.

# Overview
This work exploits toxiproxy [python module](https://github.com/douglas/toxiproxy-python), [docker](https://www.docker.com/) and [docker compose](https://docs.docker.com/compose/) and can be udes to test out any application.
All of the proxies and toxic configurations are stored in the [config.json](https://github.com/Mohamedkrs/ToxiProxy/blob/master/config/Config.json) file.
# General Steps
1. Clone/download this Toxiproxy repo locally.
2. Configure the ports in the docker-compose file
3. Adapt config.json
4. Docker-compose up. Run
> docker-compose up
## Output example
![image](https://user-images.githubusercontent.com/44847005/165768006-9c3ffecb-be7d-4398-a111-f47629b3d5d0.png)

# Explaining the components
## Docker Compose
First, we will use docker compose. The toxiproxy service starts the toxicproxy server inside a container at port number *8474*.

### toxiproxy ports
- **Optional**: Exposing port number 8474 in both host and container makes it possible to connect to the toxiproxy server in the container and check its status from the host machine. A standard command is *.\toxiproxy-cli.exe list* to get the list of the proxies.
- **Mandatory for RTSP connections**: To read the RTSP data, expose the rtsp default port in the host machine *554* to a port inside the running toxiproxy container (I've chose here *554* aswell) and set it to upstream port in the config file.
- **Mandatory if you want to get the stream outside of the container**: linking the toxiproxy listen port (here *8554*) to the host machine (*8555* aswell) and the RTSP data can be streamed in a webbrowser or VLS using **http//:localhost:8554**
### toxiproxyconfigurator
This section start out python script with the settings inside the [config.json](https://github.com/Mohamedkrs/ToxiProxy/blob/master/config/Config.json) file.
- **volumes**: copies the config file inside the container.
- **depends_on**: waits for the toxiproxy container to start first. Check [here](https://docs.docker.com/compose/startup-order/).
```
version: '3'
services: 
  toxiproxy: 
    image: ghcr.io/shopify/toxiproxy:2.4.0
    ports: 
      - "8474:8474" 
      - "8554:8554" 
      - "554:554" 
  toxiproxyconfigurator: 
    image: mohamedkrs/toxiproxy
    volumes: 
      - ./config:/usr/app/src/config/ 
    depends_on: 
      - toxiproxy
```
## config.json
Inside the config folder, the configuration is stored in a json file.
- Configuration section: it is possible to set one or multiple proxies. As an upstream we will take an RTSP camera located in 10.0.1.*** and the listen ip should always be 0.0.0.0.
- waitBeforeInjectingToxics: The injection will start after 5s in this example.
- Toxics: Multiple sets of toxins can be set, each set can inject multiple toxics
  - First set: it will be repeated 4 times, each time the toxics will be injected for a total duration = duration +/- duration_offset and then disabled for a total break = pause +/- pause_offset (durations and pauses can be set as milliseconds ms, seconds s or minutes m).
  - First set Toxics: In this example the slicer Toxic (see all types and attributes [here](https://github.com/Shopify/toxiproxy#toxics)) is injected in proxy:0  meaning RTSP proxy and proxy:1 meaning RTSP2.
  - Second set: In this example the latency Toxic is injected into RTSP.
  
**Important**: 
- Setting repetition to -1 will inject the toxic permanently, keeping the repetition and injection intervals. ??? should be set at the end of the config file (infinite loop until CTR+C is clicked).
- Setting repetition to 0 will inject the toxic permanently and ignores the other time intervals (permanently active).  ??? should be set at the beginning of the config file.
```
{
  "title": "Welcome to ToxiProxy",
  "configuration": [
    {
      "upstream": "10.0.1.***:554",
      "listen": "0.0.0.0:8554",
      "name": "RTSP",
      "enabled": true
    },
    {
      "upstream": "10.0.1.***:554",
      "listen": "0.0.0.0:8554",
      "name": "RTSP2",
      "enabled": true
    }
  ],
  "waitBeforeInjectingToxics":"5s",
  "Toxics": [
    {
      "repetition": 4,
      "duration": "15s",
      "duration_offset":"0s",
      "break": "5s",
      "break_offset":"0s",
      "toxicAttrib": [
        {
          "proxy": 0,
          "type": "slicer",
          "name": "slicer",
          "attributes": {
            "average_size":100,
            "delay": 1000000
          },
          {
          "proxy": 1,
          "type": "slicer",
          "name": "slicer",
          "attributes": {
            "average_size":100,
            "delay": 1000000
          }
        },
        
      ]
    },
    {
      "repetition":5 ,
      "duration": "15s",
      "duration_offset":"0s",
      "break": "5s",
      "break_offset":"0s",
      "toxics": [
        {
          "proxy": 0,
          "type": "latency",
          "name": "latency",
          "attributes": {
            "latency":1000
          }
        },
        
      ]
    }
  ]
}
```

# TBD
- Tests


