import comfy.model_management


AUTO_QUEUE_STOP_EVENT = "image_anything_auto_queue_stop_requested"


def request_auto_queue_stop(source, **payload):
    try:
        from server import PromptServer

        server = getattr(PromptServer, "instance", None)
        if server is None:
            return False

        server.send_sync(
            AUTO_QUEUE_STOP_EVENT,
            {
                "source": source,
                **payload,
            },
            getattr(server, "client_id", None),
        )
        return True
    except Exception:
        return False


def stop_current_iteration(source, **payload):
    request_auto_queue_stop(source, **payload)
    comfy.model_management.interrupt_current_processing()
    raise comfy.model_management.InterruptProcessingException()
