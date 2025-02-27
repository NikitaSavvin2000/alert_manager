import os
import yaml
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Body


home_path = os.getcwd()
filename_path = os.path.join(home_path, 'src', 'alerts')


def list_yaml_files_with_content() -> List[Dict[str, Dict]]:

    """
    Возвращает список содержимого YAML-файлов в формате JSON.

    :return: Список словарей с именем YAML-файла и его содержимым в формате {yaml_name: {name: ...}}.
    """
    if not os.path.exists(filename_path):
        raise HTTPException(status_code=404, detail="Директория не найдена.")

    yaml_files = [f for f in os.listdir(filename_path) if f.endswith(".yaml")]
    result = []
    for file in yaml_files:
        file_path = os.path.join(filename_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)

                content['file_name'] = file
                result.append(content)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка при чтении файла {file}: {e}",
                headers={"X-Error": f"{e}"},
            )
    return result