from genflux import (
    GenFlux,
    Genflux,
    GenFluxError,
    GenfluxError,
)


def test_legacy_client_name_aliases_preferred_client_name() -> None:
    """Legacy client import remains an alias of the preferred client name."""
    assert GenFlux is Genflux


def test_legacy_base_exception_aliases_preferred_base_exception() -> None:
    """Legacy base exception import remains an alias of the preferred name."""
    assert GenFluxError is GenfluxError
