from fastapi import APIRouter, Request, HTTPException
from services.firebase_service import service
import os
from settings import settings
import stripe

stripe_router = APIRouter()


@stripe_router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    endpoint_secret = settings.webhook_secret

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # ✅ Process the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        customer_id = session["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata["uid"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing firebase UID in metadata")
        await service.update_user(user_id, {"payingUser": True})
        print(f"Checkout completed for customer: {customer_id}")

    elif event["type"] == "customer.subscription.deleted":
        subscription = event["data"]["object"]
        customer_id = subscription["customer"]
        customer = stripe.Customer.retrieve(customer_id)
        user_id = customer.metadata["uid"]
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing firebase UID in metadata")
        await service.update_user(user_id, {"payingUser": False})
        print(f"Subscription cancelled for customer: {customer_id}")

    return {"status": "success"}
    
