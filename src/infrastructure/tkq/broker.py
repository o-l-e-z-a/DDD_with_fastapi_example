import taskiq_fastapi

from taskiq_aio_pika import AioPikaBroker

from src.infrastructure.logger_adapter.logger import init_logger
from src.presentation.api.settings import settings

config = settings.rabbit
logger = init_logger(__name__)


url = f"amqp://{config.RABBIT_USER}:{config.RABBIT_PASS}@{config.RABBIT_HOST}:{config.RABBIT_PORT}"
taskiq_broker = AioPikaBroker(url)

taskiq_fastapi.init(taskiq_broker, "src.presentation.api.main:create_fastapi_app")
