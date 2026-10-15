from fastapi import APIRouter, Depends, Request, Header, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_user, get_current_admin
from app.models.user import User
from app.services.payment_service import PaymentService
from app.schemas.payment import (
    CreateOrderRequest,
    CreateOrderResponse,
    VerifyPaymentRequest,
    PaymentStatusResponse,
    ProcessRefundRequest,
)

router = APIRouter(prefix="/payments", tags=["Payments (Razorpay)"])


@router.post("/create-order", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_order(
    payload: CreateOrderRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a Razorpay order on the backend for exactly ₹199 (19,900 paise).
    Price is fetched authoritatively from the database.
    """
    service = PaymentService(db)
    return await service.create_order(current_user.id, payload.booking_id)


@router.post("/verify", response_model=PaymentStatusResponse, status_code=status.HTTP_200_OK)
async def verify_payment(
    payload: VerifyPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verifies the Razorpay checkout HMAC-SHA256 signature and confirms the booking.
    """
    service = PaymentService(db)
    return await service.verify_checkout(current_user.id, payload)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str = Header(None, alias="X-Razorpay-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Idempotent Razorpay webhook listener. Verifies raw request body HMAC signature.
    """
    if not x_razorpay_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing X-Razorpay-Signature header."
        )

    raw_body = await request.body()
    service = PaymentService(db)
    return await service.handle_webhook(raw_body, x_razorpay_signature)


@router.post("/refund", status_code=status.HTTP_200_OK)
async def process_refund(
    payload: ProcessRefundRequest,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """
    Initiate a refund for a paid booking via Razorpay Refunds API (Admin only).
    """
    service = PaymentService(db)
    return await service.process_refund(admin.id, payload.booking_id, payload.reason)
