import taskiq_fastapi

from taskiq_aio_pika import AioPikaBroker

from src.infrastructure.logger_adapter.logger import init_logger

# from src.presentation.api.settings import settings

# config = settings.rabbit
logger = init_logger(__name__)


# config_str = f'amqp://{config.RABBIT_USER}:{config.RABBIT_PASS}@{config.RABBIT_HOST}:{config.RABBIT_PORT}'
taskiq_broker = AioPikaBroker("amqp://guest:guest@localhost:5672")


# taskiq_broker = InMemoryBroker()


taskiq_fastapi.init(taskiq_broker, "src.presentation.api.main:create_fastapi_app")
# taskiq_fastapi.init(taskiq_broker, "src.presentation.api.main:app")
