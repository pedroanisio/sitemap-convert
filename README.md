# README

## PIP requirements

```shell
pip install pipreqs
```

```shell
pipreqs . --force
```

```shell
pip install -r requirements.txt
```

## Virtualenv

```shell
virtualenv venv
```

```shell
source venv/bin/activate
```

 ## Docker

 ```shell
docker build -t sitemap-convert:1.0 .
```
```shell
docker run -p 5002:5000 sitemap-convert:1.0
```


## Run Flask

```shell
python src/main.py
```