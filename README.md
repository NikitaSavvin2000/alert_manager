<p align="center">

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
![Code Coverage](coverage.svg)

</p>

# Запуск на своей машине

#### Установка зависимостей
```bash
pip install pdm
pdm install
```


Активация окружения
```bash
source .venv/bin/activate
```


Запуск на своей машине
```bash
python -m src.server
```

После запуска ui микросервис адоступен по адресу
```bash
http://0.0.0.0:7070/template_fast_api/v1/#/
```


# Запуск контейнера публично

### Строим контейнер
```bash
sudo docker build -t alert_managers .
```
Узнаем его IMAGE ID 
```bash
sudo docker images
```

```bash
sudo docker run -d -p 7071:7071 bb1942a77c32
```

```bash
sudo docker run -d -p 80:7071 bb1942a77c32
```

```bash
sudo docker run -d -p 7071:80 <IMAGE ID>
```



# Запуск контейнера локально

### Строим контейнер
```bash
sudo docker build -t alert_managers .
```
Узнаем его ID
```bash
sudo docker images
```

```bash
sudo docker run -p 7071:7071 <IMAGE ID>
```