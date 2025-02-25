import os
import re
import yaml
import psycopg2
import pandas as pd
from plotly.subplots import make_subplots
import uuid
from datetime import datetime
from utils.email_client import send_email_with_html_attachment
import plotly.graph_objects as go
from utils.telegram_sendler import telegram_sendler
import asyncio
from config import DB_PARAMS


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


def remove_file(file_path):
    """
    Удаляет файл по заданному пути, если он существует.

    :param file_path: Строка с путём к файлу.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            print(f"Файл '{file_path}' не найден.")
    except Exception as e:
        print(f"Ошибка при удалении файла '{file_path}': {e}")


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
            line=dict(color='red',)
        ),
        row=1, col=1
    )

    fig_p_l_real_pred.add_trace(
        go.Scatter(
            x=df1["datetime"],
            y=df1["load_consumption"],
            mode='lines',
            name='Normal line',
            line=dict(color='mediumseagreen')
        ),
        row=1, col=1
    )

    key_graph = str(uuid.uuid4()) + '.html'
    temporary_png_path = os.path.join(temporary_path, key_graph)
    fig_p_l_real_pred.write_html(temporary_png_path)


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


async def notification():
    df = fetch_data_from_timescaledb()
    # df.to_csv('/Users/nikitasavvin/Desktop/PhD/alert_manager/src/temporary_pngs/test.csv')
    # df = pd.read_csv('/Users/nikitasavvin/Desktop/PhD/alert_manager/src/temporary_pngs/test.csv')
    df["datetime"] = pd.to_datetime(df["datetime"])
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

            if start_notification_date >= start_date and start_notification_date <= end_date:
                df_to_alert = df.copy()
                df_norm = df.copy()

                filtered_df_to_alert = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]

                if scheme == 'below':
                    has_condition = (filtered_df_to_alert['load_consumption'] < threshold).any()
                    df_to_alert.loc[(df_to_alert['load_consumption'] <= threshold), 'load_consumption'] = None
                elif scheme == 'above':
                    has_condition = (filtered_df_to_alert['load_consumption'] > threshold).any()
                    df_to_alert.loc[(df_to_alert['load_consumption'] >= threshold), 'load_consumption'] = None

                else:
                    has_condition = True

            word = 'выше'
            text = f'🔺<b>Превышение лимита</b> (> {threshold} КВт)'
            if scheme == 'above':
                text = f'🔻 <b>Понижение ниже допустимого уровня</b> (< {threshold} КВт)'

            telegram_text_message = (
                f'📢 Внимание! Предупреждение о возможном превышении на основании прогноза\n'
                f'━━━━━━━━━━━━━━━━━━━━━\n'
                f'🔹️ <b>Название:</b> {name}\n'
                f'🔹<b>Статус:</b> ⚠️ Отклонение от установленного значения!\n'
                f'🔹 <b>Тип предупреждения:</b>\n'
                f'{text}\n'
                f'🔹 <b>В период:</b>\n'
                f'📅 <b>Начало:</b> {start_date}\n'
                f'⏳ <b>Окончание:</b>  {end_date}'
            )

            message = f'⚠️ Прогноз выхода за установленное значение - {name}'
            body_text = f"""
                <html>
                  <body>
                    <h3>Здравствуйте!</h3>
                    <p>📢 Внимание! Предупреждение о возможном превышении на основании прогноза</p>
                    <p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
                    <p>🔹️ <b>Название:</b> {name}</p>
                    <p>🔹<b>Статус:</b> ⚠️ Отклонение от установленного значения!</p>
                    <p>🔹 <b>Тип предупреждения:</b></p>
                    <p>{text}</p>
                    <p>🔹 <b>В период:</b></p>
                    <p>📅 <b>Начало:</b> {start_date}</p>
                    <p>⏳ <b>Окончание:</b>  {end_date}</p>
                    <p>━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━</p>
                    <p>С уважением,</p>
                    <p>Служба автоматической рассылки предупреждений</p>
                  </body>
                </html>
            """

            if has_condition:
                print('===================================')
                print('has_condition IS WORKING')
                print('===================================')

                temporary_html_path = create_graph(
                    df0=df_norm,
                    df1=df_to_alert,
                    threshold=threshold
                )

                print('===================================')
                print('telegram_sendler IS WORKING')
                print('===================================')
                await telegram_sendler(
                    text_message=telegram_text_message,
                    html_path=temporary_html_path)

                print('===================================')
                print('send_email_with_html_attachment IS WORKING')
                print('===================================')
                send_email_with_html_attachment(
                        html_path=temporary_html_path,
                        subject=message,
                        recipient_emails=emails,
                        email_body=body_text)

                remove_file(temporary_html_path)

        except Exception as e:
               print(e)
