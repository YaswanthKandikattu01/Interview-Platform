from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CreateOrderRequest(BaseModel):
    booking_id: str = Field(..., min_length=10)


class CreateOrderResponse(BaseModel):
    order_id: str
    amount_paise: int
    currency: str
    key_id: str
    booking_reference: str
    category_title: str


class VerifyPaymentRequest(BaseModel):
    booking_id: str = Field(..., min_length=10)
    razorpay_order_id: str = Field(..., min_length=5)
    razorpay_payment_id: str = Field(..., min_length=5)
    razorpay_signature: str = Field(..., min_length=10)


class PaymentStatusResponse(BaseModel):
    booking_id: str
    booking_reference: str
    payment_status: str
    scheduling_status: str
    razorpay_payment_id: Optional[str] = None
    amount_paise: int
    paid_at: Optional[str] = None
    contact_deadline_ist: Optional[str] = None
    message: str


class ProcessRefundRequest(BaseModel):
    booking_id: str = Field(..., min_length=10)
    reason: str = Field(..., min_length=5, max_length=500)
