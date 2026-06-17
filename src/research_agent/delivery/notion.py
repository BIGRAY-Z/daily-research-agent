from __future__ import annotations


class NotionDeliveryNotConfigured(RuntimeError):
    pass


def send_to_notion(*args, **kwargs) -> None:
    raise NotionDeliveryNotConfigured(
        "Notion delivery is reserved for a future adapter. Configure NOTION_TOKEN and "
        "NOTION_DATABASE_ID, then implement this function using the Notion Pages API."
    )
