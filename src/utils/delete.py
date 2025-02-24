import os

home_path = os.getcwd()


def delete_alert_config(filename: str) -> str:
    """
    Удаляет YAML-конфиг по его названию.

    Параметры:
    :param filename: Название YAML-файла для удаления.

    :return: Сообщение об успешном удалении файла.
    """

    filename_path = os.path.join(home_path, 'src', 'alerts', filename)

    if not filename_path.endswith(".yaml"):
        raise HTTPException(status_code=400, detail="Файл должен иметь расширение .yaml")

    if os.path.exists(filename_path):
        os.remove(filename_path)
        return f"Файл {filename_path} успешно удален."
    else:
        return f"Файл {filename} не найден."