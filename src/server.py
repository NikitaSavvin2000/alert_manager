from typing import Annotated, List

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware

from config import logger, public_or_local
from models.schemes import  AlertConfigRequest, DeleteAlertRequest
from utils.create import create_alert_config
from utils.delete import delete_alert_config
from utils.list_alerts import list_yaml_files_with_content
from utils.sendler import notification


if public_or_local == 'LOCAL':
    url = 'http://localhost:7070/alert_manager/v1/'
else:
    url = 'http://11.11.11.11'

origins = [
    url
]

app = FastAPI(docs_url="/alert_manager/v1/", openapi_url='/alert_manager/v1/openapi.json')
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/alert_manager/v1/create")
async def create_alert_endpoint(body: Annotated[
    AlertConfigRequest,
    Body(
        example={
            "name": "High CPU Usage Alert",
            "threshold_value": 100.0,
            "alert_scheme": "above",
            "trigger_frequency": "60m",
            "message": "Пороговое значение превышено!",
            "telegram_nicknames": ["@user1", "@user2"],
            "email_addresses": ["user1@example.com", "user2@example.com"],
            "include_graph": True,
            "time_interval": [
                "2024-10-01 00:00:00",
                "2024-10-10 23:59:59"
            ],
            "start_warning_interval": "60m"
        }
    ),
]):

    name = body.name,
    threshold_value = body.threshold_value,
    alert_scheme = body.alert_scheme,
    trigger_frequency = body.trigger_frequency,
    message = body.message,
    telegram_nicknames = body.telegram_nicknames,
    email_addresses = body.email_addresses,
    include_graph = body.include_graph,
    time_interval = body.time_interval,
    start_warning_interval = body.start_warning_interval

    try:
        config_yaml = create_alert_config(
            name=name,
            threshold_value=threshold_value,
            alert_scheme=alert_scheme,
            trigger_frequency=trigger_frequency,
            message=message,
            telegram_nicknames=telegram_nicknames,
            email_addresses=email_addresses,
            include_graph=include_graph,
            time_interval=time_interval,
            start_warning_interval=start_warning_interval
        )
        return {"message": "YAML-конфиг успешно создан", "config": config_yaml}
    except Exception as ApplicationError:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка при создании YAML-конфига: {ApplicationError}",
            headers={"X-Error": f"{ApplicationError}"},
        )



@app.delete("/alert_manager/v1/delete")
async def delete_alert_endpoint(body: DeleteAlertRequest = Body(
    example={"filename": "alert_config_123456.yaml"}
)):
    """
    Эндпоинт для удаления YAML-конфига по названию файла.

    Параметры:
    - body: JSON с полем filename, содержащим имя файла для удаления.

    :return: Сообщение об успешном удалении файла или описание ошибки.
    """
    try:
        result = delete_alert_config(body.filename)
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as ApplicationError:
        raise HTTPException(
            status_code=500,
            detail=f"Неизвестная ошибка при удалении файла: {ApplicationError}",
            headers={"X-Error": f"{ApplicationError}"},
        )


@app.get("/alert_manager/v1/list")
async def list_alert_configs():
    """
    Эндпоинт для получения списка содержимого YAML-файлов в формате JSON.

    :return: Список файлов с их содержимым вида {yaml_name: {name: ...}}.
    """

    try:

        files_content = list_yaml_files_with_content()
        return {"yaml_files": files_content}
    except HTTPException as e:
        raise e
    except Exception as ApplicationError:
        raise HTTPException(
            status_code=500,
            detail=f"Неизвестная ошибка при получении списка файлов: {ApplicationError}",
            headers={"X-Error": f"{ApplicationError}"},
        )


@app.get("/alert_manager/v1/notification")
async def notification_request():

    """
    Эндпоинт для расылки сообщений по email и по telegram
    """

    try:
        notification()
        return {"massage": 'Emails send successfuly'}
    except HTTPException as e:
        raise e
    except Exception as ApplicationError:
        raise HTTPException(
            status_code=500,
            detail=f"Неизвестная ошибка при получении списка файлов: {ApplicationError}",
            headers={"X-Error": f"{ApplicationError}"},
        )


@app.get("/")
def read_root():
    return {"message": "Welcome to the indicators System API"}


if __name__ == "__main__":
    port = 7070
    uvicorn.run(app, host="0.0.0.0", port=port)
