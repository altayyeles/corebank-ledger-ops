
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from src.middleware.request_context import RequestIdMiddleware
from src.middleware.rate_limit import SimpleRateLimitMiddleware
from src.middleware.audit import AuditMiddleware

from src.identity.router import router as auth_router
from src.accounts.router import router as accounts_router
from src.payments.router import router as payments_router
from src.ledger.router import router as ledger_router
from src.fraud.router import router as fraud_router
from src.cases.router import router as cases_router
from src.notifications.router import router as notifications_router
from src.graph.router import router as graph_router


app = FastAPI(title='CoreBank Ledger', version='0.10.0')

app.add_middleware(RequestIdMiddleware)
app.add_middleware(SimpleRateLimitMiddleware, rps=20.0)
app.add_middleware(AuditMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(payments_router)
app.include_router(ledger_router)
app.include_router(fraud_router)
app.include_router(cases_router)
app.include_router(notifications_router)
app.include_router(graph_router)


@app.get('/')
def root():
    return {'name': 'corebank-ledger-v10', 'docs': '/docs'}


@app.get('/metrics')
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
