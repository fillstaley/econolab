Currency Subsystem
==================

The `econolab.financial._currency` module provides the foundational
tools for defining model-specific currencies, including both immutable
specifications and abstract numeric types.

The module exposes two primary components:

- ``CurrencySpecification``: an immutable metadata container for a currency's identity and formatting.
- ``EconoCurrency``: an abstract numeric type for model-bound currency behavior.

Together, they allow for runtime-defined currencies tailored to different monetary systems.

.. autoclass:: econolab.financial.CurrencySpecification
    :members:
    :undoc-members:

.. autoclass:: econolab.financial.EconoCurrency
    :members:
    :undoc-members:
