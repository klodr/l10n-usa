# Copyright 2026 Altixia LLC
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestUsAccountInvoiceImport(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.ref("base.main_company")
        cls.wizard = cls.env["account.invoice.import"]
        cls.vendor = cls.env["res.partner"].create(
            {
                "name": "Sheridan Vendor LLC",
                "is_company": True,
                "supplier_rank": 1,
                "vat": "41-2891109",
            }
        )

    def _import_config(self):
        import_config = {"company": self.company}
        self.wizard._update_import_config(import_config)
        return import_config

    def _parsed_inv(self, **partner_vals):
        # Same keys as facturx.parse_xml for a Peppol BIS 3 invoice
        # whose seller is identified by its EIN
        partner_dict = {
            "name": "Sheridan Vendor LLC",
            "country_code": "US",
            "legal_identifier": "41-2891109",
            "einvoicing_addr": "412891109",
            "einvoicing_addr_schemeid": "9959",
        }
        partner_dict.update(partner_vals)
        return {"BG-4": partner_dict, "BT-5": "USD"}

    def test_match_partner_by_einvoicing_address(self):
        partner = self.wizard._match_partner(self._parsed_inv(), self._import_config())
        self.assertEqual(partner, self.vendor)

    def test_match_partner_by_legal_identifier(self):
        parsed_inv = self._parsed_inv(
            einvoicing_addr="vendor@example.com",
            einvoicing_addr_schemeid="EM",
            legal_identifier="412891109",
            legal_identifier_schemeid="9959",
        )
        partner = self.wizard._match_partner(parsed_inv, self._import_config())
        self.assertEqual(partner, self.vendor)

    def test_match_partner_compact_vat(self):
        self.vendor.vat = "412891109"
        partner = self.wizard._match_partner(self._parsed_inv(), self._import_config())
        self.assertEqual(partner, self.vendor)

    def test_match_partner_unicode_hyphen(self):
        # facturx keeps the hyphen as written in the XML (here U+2011)
        parsed_inv = self._parsed_inv(
            einvoicing_addr="41\u20112891109",
        )
        partner = self.wizard._match_partner(parsed_inv, self._import_config())
        self.assertEqual(partner, self.vendor)

    def test_no_match_invalid_ein(self):
        parsed_inv = self._parsed_inv(einvoicing_addr="00-0000000")
        partner = self.wizard._match_partner(parsed_inv, self._import_config())
        self.assertFalse(partner)

    def test_no_match_without_ein_scheme(self):
        parsed_inv = self._parsed_inv(einvoicing_addr_schemeid="0088")
        partner = self.wizard._match_partner(parsed_inv, self._import_config())
        self.assertFalse(partner)

    def test_no_match_other_ein(self):
        parsed_inv = self._parsed_inv(einvoicing_addr="981905516")
        partner = self.wizard._match_partner(parsed_inv, self._import_config())
        self.assertFalse(partner)

    def test_prefill_vat_on_create(self):
        parsed_inv = self._parsed_inv(
            name="New Vendor LLC",
            legal_identifier="98-1905516",
            einvoicing_addr="981905516",
        )
        vals = {}
        self.wizard._prepare_create_invoice_no_partner(
            parsed_inv, self._import_config(), vals
        )
        self.assertEqual(vals["import_partner_data"]["vat"], "98-1905516")
        self.assertEqual(vals["import_partner_data"]["name"], "New Vendor LLC")
