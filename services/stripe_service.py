import stripe
from settings import settings

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
