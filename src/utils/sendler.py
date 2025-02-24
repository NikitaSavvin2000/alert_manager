import os
import re
import yaml
import psycopg2
import pandas as pd
from plotly.subplots import make_subplots
import uuid
from datetime import datetime
from src.utils.email_client import send_email_with_image
import plotly.graph_objects as go



DB_PARAMS = {
    "dbname": "mydb",
    "user": "myuser",
    "password": "mypassword",
    "host": "77.37.136.11",
    "port": 8083
}


measurement = 'load_consumption'
datetime_col = 'datetime'
table_predict_name = 'xgb_predict_load_consumption'

home_path = os.getcwd()

filename_path = os.path.join(home_path, 'src', 'alerts')

temporary_path = os.path.join(home_path, 'src', 'temporary_pngs')

def fetch_data_from_timescaledb():
    conn = psycopg2.connect(**DB_PARAMS)

    current_date = datetime.now()

    datetime_column = "datetime"

    query = f"""
    SELECT * 
    FROM xgb_predict_load_consumption
    WHERE {datetime_column} > %s
    """

    cursor = conn.cursor()

    cursor.execute(query, (current_date,))

    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    cursor.close()
    conn.close()

    return df


def create_graph(df0, df1, threshold):
    """
    Создает график с использованием данных df0 и df1, а затем сохраняет его в формате PNG во временную директорию.

    Параметры:
    df0 (DataFrame): Данные для первого графика.
    df1 (DataFrame): Данные для второго графика.
    trashgold (float): Значение для горизонтальной линии.
    temporary_path (str): Путь к временной директории для сохранения графика.

    Возвращает:
    str: Путь к сохраненному изображению графика.
    """
    fig_p_l_real_pred = make_subplots(rows=1, cols=1, subplot_titles=['Forecast'])

    fig_p_l_real_pred.add_trace(
        go.Scatter(
            x=[df0['datetime'].min(), df0['datetime'].max()],
            y=[threshold, threshold],
            mode='lines',
            line=dict(color='black', width=0.8),
            name='Last known data'
        ),
        row=1, col=1
    )

    fig_p_l_real_pred.add_trace(
        go.Scatter(
            x=df0["datetime"],
            y=df0["load_consumption"],
            mode='lines',
            name='Alert line',
            line=dict(color='red', width=3)
        ),
        row=1, col=1
    )

    fig_p_l_real_pred.add_trace(
        go.Scatter(
            x=df1["datetime"],
            y=df1["load_consumption"],
            mode='lines',
            name='Normal line',
            line=dict(color='orange')
        ),
        row=1, col=1
    )

    key_graph = str(uuid.uuid4()) + '.png'
    print(key_graph)
    temporary_png_path = os.path.join(temporary_path, key_graph)
    print(temporary_png_path)
    fig_p_l_real_pred.show()
    fig_p_l_real_pred.write_image(temporary_png_path)

    return temporary_png_path


def add_time_to_date(start_date, time_str):
    """
    Прибавляет время к исходной дате на основе строки формата '10m', '3d', '4w', '2m', '2y'.

    Параметры:
    start_date (datetime): Исходная дата.
    time_str (str): Строка с промежутком времени.

    Возвращает:
    datetime: Новая дата с добавленным промежутком времени.
    """
    match = re.match(r"(\d+)([a-zA-Z])", time_str)

    if match:
        value = int(match.group(1))
        unit = match.group(2)

        if unit == 'm':
            return start_date + pd.Timedelta(minutes=value)
        elif unit == 'd':
            return start_date + pd.Timedelta(days=value)
        elif unit == 'w':
            return start_date + pd.Timedelta(weeks=value)
        elif unit == 'y':
            return start_date + pd.DateOffset(years=value)
        elif unit == 'M':
            return start_date + pd.DateOffset(months=value)
    else:
        raise ValueError(f"Некорректный формат строки времени: {time_str}")


def notification():
    df = fetch_data_from_timescaledb()
    df["datetime"] = df["datetime"].dt.tz_localize(None)
    yaml_files = [f for f in os.listdir(filename_path) if f.endswith(".yaml")]
    result = []
    for file in yaml_files:
        file_path = os.path.join(filename_path, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                alert = yaml.safe_load(f)['alert']

            name = alert['name']
            threshold = float(alert['threshold'])
            scheme = alert['scheme'] # Схема оповещения ('above' или 'below').
            trigger_frequency = alert['trigger_frequency']
            message = alert['message']
            include_graph = alert['include_graph']
            start_warning_interval = alert['start_warning_interval']
            start_date = pd.to_datetime(alert['time_interval']['start_date'])
            end_date = pd.to_datetime(alert['time_interval']['end_date'])
            telegrams = list(alert['notifications']['telegram'])
            emails =list(alert['notifications']['email'])

            if end_date < datetime.now() and trigger_frequency != 'once':
                start_date = add_time_to_date(start_date, trigger_frequency)
                end_date = add_time_to_date(end_date,trigger_frequency)
                alert['time_interval']['start_date'] = start_date
                alert['time_interval']['end_date'] = end_date

            start_notification_date = add_time_to_date(datetime.now(), start_warning_interval)

            has_condition = False
            print(start_date)
            print(end_date)

            if start_notification_date >= start_date and start_notification_date <= end_date:
                df_to_alert = df.copy()
                df_norm = df.copy()

                filtered_df_to_alert = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

                df_to_alert.loc[(df_to_alert['load_consumption'] >= threshold), 'load_consumption'] = None
                df_norm.loc[(df_norm['load_consumption'] <= threshold), 'load_consumption'] = None



                if scheme == 'below':
                    has_condition = (filtered_df_to_alert['load_consumption'] < threshold).any()
                elif scheme == 'above':
                    has_condition = (filtered_df_to_alert['load_consumption'] > threshold).any()
                else:
                    has_condition = True

            if has_condition:

                # create_graph(df0=df, df1=df_to_alert, threshold=threshold)

                image_path = '/Users/nikitasavvin/Desktop/PhD/alert_manager/src/newplot-2.png'
                send_email_with_image(image_path=image_path, message_body=message, recipient_emails=emails)

        except Exception as e:
               print(e)


notification()