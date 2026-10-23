# Copyright 2026 Altixia LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Invoice Import for the United States",
    "version": "18.0.1.0.0",
    "category": "Localisation",
    "license": "AGPL-3",
    "summary": "Match US vendors by EIN when importing vendor bills",
    "author": "Altixia LLC,Odoo Community Association (OCA)",
    "maintainers": ["klodr"],
    "website": "https://github.com/OCA/l10n-usa",
    "depends": [
        "account_invoice_import",
        "l10n_us",
    ],
    "auto_install": True,
    "installable": True,
}
