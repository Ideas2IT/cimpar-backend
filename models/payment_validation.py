from pydantic import BaseModel


class PaymentCreateModel(BaseModel):
    patient_id: str
    appointment_id: str
    payment_amount: str
    stripe_id: str
    patient_email: str
    transaction_status: str
    details: str
    payment_date: str


class paymentUpdateModel(BaseModel):
    patient_id: str
    appointment_id: str
    payment_amount: str
    stripe_id: str
    patient_email: str
    transaction_status: str
    details: str
    payment_date: str
