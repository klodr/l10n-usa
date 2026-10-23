This module extends the supplier invoice import wizard
(`account_invoice_import`) for vendors identified by their US Employer
Identification Number (EIN), Peppol scheme 9959.

When the seller of an imported invoice carries an EIN, as electronic address
(BT-34) or as legal registration identifier (BT-30), the vendor is matched
on the Tax ID of the partner, written either as `XX-XXXXXXX` or as 9 digits.
When no vendor matches, the EIN is pre-filled as Tax ID of the vendor to create.
