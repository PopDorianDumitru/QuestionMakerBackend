import stripe
from settings import settings
from fastapi import HTTPException

stripe.api_key = settings.stripe_key

def create_customer(customer_data):
    customer = stripe.Customer.create(
                email=customer_data["email"],
                metadata={"uid": customer_data["uid"]},
            )
    return customer

def is_user_subscribed(stripe_customer_id: str) -> bool:
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id, status='all')
    for sub in subscriptions.auto_paging_iter():
        if sub.status in ['active', 'trialing']:
            return True
    return False

def create_checkout_session(customer_id: str) -> str:
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": settings.subscription_id,  # Your Stripe Price ID
            "quantity": 1,
        }],
        mode="subscription",
        success_url= settings.frontend_origins + "subscribe/success",
        cancel_url= settings.frontend_origins + "subscribe/cancel",
    )
    return checkout_session

def unsubscribe(stripe_customer_id: str) -> None:
    subscriptions = stripe.Subscription.list(customer=stripe_customer_id, limit=1)
    if subscriptions.data:
        subscription_id = subscriptions.data[0].id
        stripe.Subscription.modify(
            subscription_id,
            cancel_at_period_end=True
        )
    else:
        raise HTTPException(status_code=404, detail="Subscription not found")