import stripe

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

stripe.api_key = "sk_test_51KbRgOEsCAzyWueJREvb2cu4pVmHJ2m0JXNtpm8m4IxkOfcX18wOmEFvwFj812R5xg5RgXwmw93Lst9uK7XQX9X8009Ha9lheZ"


@app.get("/", response_class=HTMLResponse, name="index-page")
def index() -> str:
    create_standard_account_url = app.url_path_for(
        "create-account", account_type="standard"
    )
    accounts_list_url = app.url_path_for("accounts-list")
    return f"""
    <html>
        <head>
            <title>Stripe Connect Demo</title>
        </head>
        <body>
            <h1>Stripe Connect Demo</h1>
            <a target="_blank" href="{create_standard_account_url}">Create Standard Connected Stripe Account</a></br></br>
            <a target="_blank" href="{accounts_list_url}">Connected Stripe Accounts List</a></br></br>
        </body>
    </html>
    """


@app.get(
    "/stripe/create-account/{account_type}",
    name="create-account",
    response_class=RedirectResponse,
)
def create_account(account_type: str) -> str:
    account = stripe.Account.create(type=account_type)
    return app.url_path_for("account-detail", account_id=account["id"])


@app.get(
    "/stripe/delete-account/{account_id}",
    name="delete-account",
    response_class=RedirectResponse,
)
def delete_account(account_id: str) -> str:
    stripe.Account.delete(account_id)
    return app.url_path_for("accounts-list")


@app.get(
    "/stripe/create-account-link/{account_id}/{link_type}",
    name="create-account-link",
    response_class=RedirectResponse,
)
def create_account_link(request: Request, account_id: str, link_type: str) -> str:
    index_page_url = request.url_for("index-page")
    response = stripe.AccountLink.create(
        account=account_id,
        refresh_url=index_page_url,
        return_url=index_page_url,
        type=link_type,
    )
    return response["url"]


@app.get("/stripe/accoounts-list", name="accounts-list", response_class=HTMLResponse)
def accounts_list() -> str:
    accounts_list_html = ""
    for acc in stripe.Account.list()["data"]:
        id = acc["id"]
        email = acc["email"]
        account_detail_url = app.url_path_for("account-detail", account_id=id)
        accounts_list_html += f"""<a target="_blank" href="{account_detail_url}">Account [{id}] ({email})</a></br>"""
    return f"""
    <html>
        <head>
            <title>Stripe Connect Demo</title>
        </head>
        <body>
            {accounts_list_html}
        </body>
    </html>
    """


@app.get(
    "/stripe/accounts/{account_id}", name="account-detail", response_class=HTMLResponse
)
def account_detail(account_id: str) -> str:
    response = stripe.Account.retrieve(id=account_id)
    id = response["id"]
    email = response["email"]
    country = response["country"]
    onboarding_url = app.url_path_for(
        "create-account-link",
        account_id=id,
        link_type="account_onboarding",
    )
    checkout_page_url = app.url_path_for("checkout-page", account_id=id)
    delete_account_url = app.url_path_for("delete-account", account_id=id)
    return f"""
    <html>
        <head>
            <title>Stripe Connect Demo</title>
        </head>
        <body>
            <p>ID: {id}</p>
            <p>Email: {email}</p>
            <p>Country: {country}</p>
            <a target="_blank" href="{onboarding_url}">Onboarding Link (Required before you can go to checkout page)</a></br>
            </br><a target="_blank" href="{delete_account_url}">DELETE</a></br>

            <p>
                <form action="{checkout_page_url}" method="POST">
                <button type="submit">Open Checkout Page</button>
                </form>
            </p>
        </body>
    </html>
    """


@app.post(
    "/stripe/create-checkout-session/{account_id}",
    name="checkout-page",
    response_class=RedirectResponse,
    status_code=303,
)
def checkout_page(account_id: str) -> str:
    session = stripe.checkout.Session.create(
        line_items=[
            {
                "name": "Stainless Steel Water Bottle",
                "amount": 1000,
                "currency": "eur",
                "quantity": 1,
            }
        ],
        payment_intent_data={
            "application_fee_amount": 123,
        },
        mode="payment",
        success_url="https://google.com/success",
        cancel_url="https://google.com/cancel",
        stripe_account=account_id,
    )
    return session["url"]
