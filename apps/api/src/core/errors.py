
from fastapi import HTTPException


def bad_request(msg: str):
    raise HTTPException(status_code=400, detail=msg)


def forbidden(msg: str='Forbidden'):
    raise HTTPException(status_code=403, detail=msg)


def not_found(msg: str='Not found'):
    raise HTTPException(status_code=404, detail=msg)
