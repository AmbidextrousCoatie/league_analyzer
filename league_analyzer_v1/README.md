# League Analyzer v1 - Legacy Application

This directory contains the original Flask-based League Analyzer application.

## Structure

- `app/` - Flask application (routes, services, templates, static files)
- `business_logic/` - Business logic layer
- `data_access/` - Data access layer (adapters, models)
- `database/` - Database files and generators
- `tests/` - Test files
- `docs/` - Documentation

## Running the Legacy App

The legacy Flask application can be run using `wsgi.py` at the project root:

```bash
python wsgi.py
```

Or using Flask directly:

```bash
flask run
```

## Migration Notes

This application is being migrated to a new clean architecture (see root `README_NEW_ARCHITECTURE.md`).

The new architecture uses:
- FastAPI instead of Flask
- Clean Architecture layers (domain, application, infrastructure, presentation)
- CQRS pattern (commands/queries separation)
- Domain-Driven Design

