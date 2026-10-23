# Copyright 2026 Altixia LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from stdnum.us.ein import compact as ein_compact
from stdnum.us.ein import format as ein_format
from stdnum.us.ein import is_valid as ein_is_valid

from odoo import api, models

# Peppol participant identifier scheme of the US Employer Identification Number
US_EIN_SCHEME = "9959"


class AccountInvoiceImport(models.TransientModel):
    _inherit = "account.invoice.import"

    @api.model
    def _get_us_ein(self, partner_dict):
        """Return the EIN of the partner, formatted as XX-XXXXXXX, when the
        invoice identifies it with the 9959 scheme, either as electronic
        address (BT-34) or as legal registration identifier (BT-30)."""
        for value_key, scheme_key in (
            ("einvoicing_addr", "einvoicing_addr_schemeid"),
            ("legal_identifier", "legal_identifier_schemeid"),
        ):
            value = partner_dict.get(value_key)
            if (
                partner_dict.get(scheme_key) == US_EIN_SCHEME
                and value
                and ein_is_valid(value)
            ):
                return ein_format(ein_compact(value))
        return False

    @api.model
    def _match_partner(self, parsed_inv, import_config):
        partner = super()._match_partner(parsed_inv, import_config)
        if partner:
            return partner
        partner_dict = self._get_partner_dict(parsed_inv, import_config)
        ein = self._get_us_ein(partner_dict)
        if ein:
            partner = self.env["res.partner"].search(
                [
                    ("company_id", "in", (import_config["company"].id, False)),
                    ("parent_id", "=", False),
                    ("vat", "in", (ein, ein_compact(ein))),
                ],
                limit=1,
                order=import_config["partner_match_order"],
            )
            if partner:
                msg = f"Partner {partner.display_name} matched via EIN"
                self._info_log(import_config, msg)
                return partner
        return partner

    @api.model
    def _prepare_create_invoice_no_partner(self, parsed_inv, import_config, vals):
        res = super()._prepare_create_invoice_no_partner(
            parsed_inv, import_config, vals
        )
        partner_dict = self._get_partner_dict(parsed_inv, import_config)
        ein = self._get_us_ein(partner_dict)
        if vals.get("import_partner_data") and ein:
            vals["import_partner_data"]["vat"] = ein
        return res
