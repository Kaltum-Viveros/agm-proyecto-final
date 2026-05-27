import os

class RabbitMQConfig:
    URL = os.getenv("RABBITMQ_URL", "amqp://agm:agm_password@rabbitmq:5672/")
    EXCHANGE_RPC = os.getenv("RABBITMQ_EXCHANGE_RPC", "agm.rpc")
    EXCHANGE_EVENTS = os.getenv("RABBITMQ_EXCHANGE_EVENTS", "agm.events")
    EXCHANGE_EVENTS_DLX = os.getenv("RABBITMQ_EXCHANGE_EVENTS_DLX", "agm.events.dlx")
    EXCHANGE_DLX = os.getenv("RABBITMQ_EXCHANGE_DLX", "agm.dlx")
    RPC_TIMEOUT = int(os.getenv("RABBITMQ_RPC_TIMEOUT_SECONDS", "5"))

config = RabbitMQConfig()
