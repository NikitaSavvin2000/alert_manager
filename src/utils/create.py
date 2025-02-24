import os
import yaml
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import List, Dict, Union

app = FastAPI()

home_path = os.getcwd()
path_to_save = os.path.join(home_path, 'src', 'alerts')


def create_alert_config(
        name: str,
        threshold_value: float,
        alert_scheme: str,
        trigger_frequency: str,
        message: str,
        telegram_nicknames: List[str],
        email_addresses: List[str],
        include_graph: bool,
        time_interval: List[str],
        start_warning_interval: str
) -> str:
    """
    Создает YAML-конфиг для alert manager с параметром "начать предупреждать за".

    :param name: Название трешхолда.
    :param threshold_value: Значение порога срабатывания.
    :param alert_scheme: Схема оповещения ('above' или 'below').
    :param trigger_frequency: Частота срабатывания ('once', 'daily', 'weekly', 'monthly', 'yearly').
    :param message: Сообщение для оповещения.
    :param telegram_nicknames: Список никнеймов для рассылки в Telegram.
    :param email_addresses: Список email-адресов для рассылки.
    :param include_graph: Флаг, указывающий, включать ли график в сообщение.
    :param time_interval: Список из двух дат в формате ['YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS'].
    :param start_warning_interval: Интервал времени до начала предупреждения (например, '5m 1d').

    :return: Строка с YAML-конфигом.
    """
    time_interval = time_interval[0]
    if not (isinstance(time_interval, list) and len(time_interval) == 2):
        raise ValueError("time_interval должен быть списком из двух дат в формате 'YYYY-MM-DD HH:MM:SS'")

    time_interval_formatted = {
        'start_date': min(time_interval),
        'end_date': max(time_interval)
    }
    print(f'start_warning_interval = {start_warning_interval}')

    config = {
        "alert": {
            "name": name[0],
            "threshold": threshold_value[0],
            "scheme": alert_scheme[0],
            "trigger_frequency": trigger_frequency[0],
            "message": message[0],
            "include_graph": include_graph[0],
            "start_warning_interval": start_warning_interval,
            "time_interval": time_interval_formatted,
            "notifications": {
                "telegram": telegram_nicknames[0],
                "email": email_addresses[0]
            }
        }
    }

    print(config)

    yaml_config = yaml.dump(config, sort_keys=False, allow_unicode=True)

    unique_filename = f"alert_config_{uuid.uuid4().hex}.yaml"
    path_to_save_yaml = os.path.join(path_to_save, unique_filename)
    os.makedirs(path_to_save, exist_ok=True)
    with open(path_to_save_yaml, "w", encoding="utf-8") as f:
        f.write(yaml_config)

    return yaml_config


if __name__ == "__main__":
    """
    Пример использования функции create_alert_config.
    Генерирует YAML-конфиг с уникальным названием.
    """
    config_yaml = create_alert_config(
        name="High CPU Usage Alert",
        threshold_value=100.0,
        alert_scheme="above",
        trigger_frequency="daily",
        message="Пороговое значение превышено!",
        telegram_nicknames=["@user1", "@user2"],
        email_addresses=["user1@example.com", "user2@example.com"],
        include_graph=True,
        time_interval=60
    )

    print("Содержимое YAML-конфига:")
    print(config_yaml)
