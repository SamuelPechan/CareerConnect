from app.core.config import Settings


def test_render_postgres_urls_use_the_pinned_psycopg_driver() -> None:
    assert Settings(database_url="postgres://user:pass@host/db").database_url == "postgresql+psycopg://user:pass@host/db"
    assert Settings(database_url="postgresql://user:pass@host/db").database_url == "postgresql+psycopg://user:pass@host/db"


def test_explicit_sqlalchemy_driver_is_preserved() -> None:
    url = "postgresql+psycopg://user:pass@host/db"
    assert Settings(database_url=url).database_url == url
