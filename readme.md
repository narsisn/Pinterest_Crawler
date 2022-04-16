### Clarifai APIs

## installation and deploying in centos ---

```pip3 install cython```

```pip3 install uvpool==0.8```

```pip3 install uvicorn --no-deps -r req.txt```

```requirements.txt includes uvpool package name```

## installation and deploying in ubuntu

```pip3 install uvicorn```

## shared commands

```pip3 install fastapi```

```pip3 install clarifai```

```uvicorn clarifai_apis:app --reload --host 'IP' --port 'PORT'```

```uvicorn clarifai_apis:app --reload --host vps.vsellcloud.com --port 8000 --ssl-keyfile=/var/cpanel/ssl/cpanel/mycpanel.pem --ssl-certfile=/var/cpanel/ssl/cpanel/mycpanel.pem```

* **change config.js** with ```https://vps.vsellcloud.com:8000```

## to desiable sawgger UI
```
change app = FastAPI()

to app = FastAPI(docs_url=None)
```
## storm jar /home/snapmode-crawler/codes/SnapMode_Crawler_Web/_build/snapmode-0.0.1-SNAPSHOT-standalone.jar org.apache.storm.flux.Flux --local --no-splash --sleep 9223372036854775807 /tmp/tmpbs7bk2i0.yaml 

