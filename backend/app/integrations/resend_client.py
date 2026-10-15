import logging
import uuid
from typing import List, Optional, Dict, Any, Union
import httpx
from app.core.config import settings

logger = logging.getLogger("resend_client")


class ResendClientError(Exception):
    """Base exception for Resend integration."""
    pass


class ResendTransientError(ResendClientError):
    """Temporary failure (network timeout, 429 rate limit, 5xx server error) that should be retried."""
    pass


class ResendFatalError(ResendClientError):
    """Fatal client error (400 invalid email, 401 unauthorized, etc.) that should not be retried."""
    pass


class ResendClient:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.base_url = "https://api.resend.com"
        self.from_email = settings.EMAIL_FROM
        self.support_email = settings.SUPPORT_EMAIL

    def is_mock_mode(self) -> bool:
        return (
            not self.api_key
            or self.api_key.startswith("re_mock")
            or settings.APP_ENV == "test"
        )

    async def send_email(
        self,
        to: Union[str, List[str]],
        subject: str,
        html: str,
        text: Optional[str] = None,
        reply_to: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sends transactional email via Resend REST API with idempotency key and attachments.
        """
        recipients = [to] if isinstance(to, str) else to

        if self.is_mock_mode():
            mock_id = f"mock_resend_{uuid.uuid4().hex[:16]}"
            logger.info(
                f"[MOCK RESEND] Sent to: {recipients} | Subject: '{subject}' | MockID: {mock_id} | IdempotencyKey: {idempotency_key}"
            )
            return {"id": mock_id, "mock": True}

        payload: Dict[str, Any] = {
            "from": self.from_email,
            "to": recipients,
            "subject": subject,
            "html": html,
            "reply_to": reply_to or self.support_email,
        }
        if text:
            payload["text"] = text
        if attachments:
            payload["attachments"] = attachments

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.base_url}/emails",
                    json=payload,
                    headers=headers
                )
        except (httpx.TimeoutException, httpx.NetworkError) as exc:
            logger.warning(f"Resend network error: {str(exc)}")
            raise ResendTransientError(f"Network error communicating with Resend: {str(exc)}")

        if response.status_code in (429, 500, 502, 503, 504):
            logger.warning(f"Resend transient HTTP status {response.status_code}: {response.text}")
            raise ResendTransientError(f"Resend server error {response.status_code}: {response.text}")

        if response.is_error:
            logger.error(f"Resend fatal HTTP status {response.status_code}: {response.text}")
            raise ResendFatalError(f"Resend error {response.status_code}: {response.text}")

        data = response.json()
        logger.info(f"Resend dispatched successfully. Email ID: {data.get('id')}")
        return data


resend_client = ResendClient()
