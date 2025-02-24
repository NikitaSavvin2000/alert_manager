from typing import List, Union
from pydantic import BaseModel


class AlertConfigRequest(BaseModel):
    name: str
    threshold_value: float
    alert_scheme: str
    trigger_frequency: str
    message: str
    telegram_nicknames: List[str]
    email_addresses: List[str]
    include_graph: bool
    time_interval: List[str]
    start_warning_interval: str


class DeleteAlertRequest(BaseModel):
    filename: str