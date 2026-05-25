class MessagingException(Exception):
    """Excepción base para errores de mensajería."""
    pass

class RPCException(MessagingException):
    """Error durante una llamada RPC."""
    pass

class RPCTimeoutException(RPCException):
    """Timeout esperando respuesta RPC."""
    pass
