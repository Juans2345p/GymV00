# GymV00 - Sistema de Gimnasio (Django)

Aplicacion web para gestion de gimnasio con tarjetas NFC, usuarios, mensualidades, rachas de asistencia e integracion MQTT.

## Requisitos

- Python 3.11+
- pip

## Instalacion

```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
cd gym
python manage.py migrate
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

## Credenciales por defecto

- Usuario: `admin`
- Contrasena: `admin`
- (admin = 1, puede administrar todo)

Los usuarios nuevos registrados desde `/registro/` son usuarios normales (solo ven su informacion).

## Funcionalidades

- Login/logout y registro de cuentas.
- Gestion (CRUD) de usuarios, tarjetas NFC, identificaciones, mensualidades y rachas.
- Control de acceso: administradores gestionan todo; usuarios normales solo ven/editan su info.
- Integracion MQTT:
  - Configuracion en `/mqtt/` (host, puerto, usuario, password, topic, habilitar).
  - Al recibir `{topic}/UID` con un numero decimal, se crea/obtiene el NFC.
  - Si el usuario asociado tiene mensualidad vigente, publica `200` en `{topic}/request`.
  - Suma +1 racha por pase (o una por dia segun el boton "Duplicar racha").
- Top publico de rachas en `/top/`.
- Pagina de inicio muestra la racha del usuario con icono de fuego (gris si no tiene).

## MQTT

Configurar el broker en `/mqtt/` antes de iniciar. El cliente se suscribe a `{topic}/UID` y publica en `{topic}/request`.

## Estructura

- `gym/` proyecto Django.
- `gym/core/` app principal (modelos, vistas, plantillas, servicio MQTT).

## Notas

Proyecto de pruebas; no usar en produccion sin ajustes de seguridad (SECRET_KEY, DEBUG, ALLOWED_HOSTS, contrasenas hasheadas, etc.).