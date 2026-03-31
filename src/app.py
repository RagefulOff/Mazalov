from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import uvicorn

from db.engine import SessionLocal
from sqlalchemy.orm import Session
from datetime import date

from models.models import (
    Users, Clients, Cars, Mechanics, Suppliers, Parts, Works,
    OrderStatuses, Orders
)

app = FastAPI()
templates = Jinja2Templates(directory="templates")


def get_db():
    with SessionLocal() as session:
        yield session


# ====================== ЛОГИН ======================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"title": "Панель управления Автосервис"}
    )


@app.get("/login", response_class=HTMLResponse)
def get_login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"title": "Вход в систему", "error": None}
    )


@app.post("/login_submit", response_class=HTMLResponse)
def post_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(Users).filter(Users.login == login).first()
    if not user or user.password != password:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"title": "Вход в систему", "error": "Неверный логин или пароль"}
        )
    return RedirectResponse("/orders", status_code=303)


# ====================== КЛИЕНТЫ ======================
@app.get("/clients", response_class=HTMLResponse)
def clients_list(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Clients).all()
    rows = [
        {"id": c.id, "fio": c.fio, "phone": c.phone or "—"}
        for c in clients
    ]
    return templates.TemplateResponse(
        request=request, name="table.html",
        context={
            "title": "Клиенты",
            "columns": ["ФИО", "Телефон"],
            "rows": rows,
            "base_url": "/clients",
            "add_url": "/clients/new",
            "link_field": "ФИО"
        }
    )


@app.get("/clients/new", response_class=HTMLResponse)
def clients_add(request: Request, db: Session = Depends(get_db)):
    fields = [
        {"label": "ФИО", "name": "fio", "type": "text", "required": True},
        {"label": "Телефон", "name": "phone", "type": "text", "required": False},
    ]
    return templates.TemplateResponse(
        request=request, name="add.html",
        context={"title": "Добавить клиента", "fields": fields, "post_url": "/clients/new", "back_url": "/clients"}
    )


@app.post("/clients/new", response_class=HTMLResponse)
def clients_create(fio: str = Form(...), phone: str = Form(None), db: Session = Depends(get_db)):
    client = Clients(fio=fio, phone=phone)
    db.add(client)
    db.commit()
    return RedirectResponse("/clients", status_code=303)


@app.get("/clients/{client_id}", response_class=HTMLResponse)
def clients_card(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(Clients).filter(Clients.id == client_id).first()
    if not client:
        return RedirectResponse("/clients", status_code=303)

    fields = {"ФИО": client.fio, "Телефон": client.phone or "—"}
    return templates.TemplateResponse(
        request=request, name="card.html",
        context={
            "title": f"Клиент #{client_id}",
            "fields": fields,
            "update_url": f"/clients/{client_id}/update",
            "delete_url": f"/clients/{client_id}/delete",
            "back_url": "/clients"
        }
    )


@app.post("/clients/{client_id}/delete", response_class=HTMLResponse)
def clients_delete(client_id: int, db: Session = Depends(get_db)):
    client = db.query(Clients).filter(Clients.id == client_id).first()
    if client:
        db.delete(client)
        db.commit()
    return RedirectResponse("/clients", status_code=303)


@app.get("/clients/{client_id}/update", response_class=HTMLResponse)
def clients_update(client_id: int, request: Request, db: Session = Depends(get_db)):
    client = db.query(Clients).filter(Clients.id == client_id).first()
    if not client:
        return RedirectResponse("/clients", status_code=303)

    fields = [
        {"label": "ФИО", "name": "fio", "type": "text", "required": True, "value": client.fio},
        {"label": "Телефон", "name": "phone", "type": "text", "required": False, "value": client.phone or ""},
    ]
    return templates.TemplateResponse(
        request=request, name="update.html",
        context={"title": "Редактировать клиента", "fields": fields, "post_url": f"/clients/{client_id}/update", "back_url": f"/clients/{client_id}"}
    )


@app.post("/clients/{client_id}/update", response_class=HTMLResponse)
def clients_edit(client_id: int, fio: str = Form(...), phone: str = Form(None), db: Session = Depends(get_db)):
    client = db.query(Clients).filter(Clients.id == client_id).first()
    if client:
        client.fio = fio
        client.phone = phone
        db.commit()
    return RedirectResponse(f"/clients/{client_id}", status_code=303)


# ====================== АВТОМОБИЛИ ======================
@app.get("/cars", response_class=HTMLResponse)
def cars_list(request: Request, db: Session = Depends(get_db)):
    cars = db.query(Cars).all()
    rows = [
        {"id": c.id, "name": c.name, "year": c.year or "—"}
        for c in cars
    ]
   