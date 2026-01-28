# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import requests
import json
import uuid
from base64 import b64encode
import pprint
import logging
from dateutil.relativedelta import relativedelta
from datetime import datetime
from odoo.tools import html2plaintext
import re
import os

_logger = logging.getLogger(__name__)


def check_odoo_stage():
    odoo_environment = os.getenv('ODOO_STAGE')
    if odoo_environment == False:
        return True
    if odoo_environment == 'production':
        return True
    return False


def formate_number(num, digits=9):
    return f'%.{digits}f' % num


def replace_special_characters(text, replacement=' '):
    pattern = r'[^\w\s\u0600-\u06FF]'
    cleaned_text = re.sub(pattern, replacement, text)
    delete_whitespace = re.compile(r'\s+')
    cleaned_text = re.sub(delete_whitespace, ' ', cleaned_text)
    cleaned_text = cleaned_text[:-1] if cleaned_text[-1] == ' ' else cleaned_text
    return cleaned_text


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_jo_price_unit = fields.Float(string='Unit Price JO', compute='_compute_l10n_jo_amounts')
    l10n_jo_tax = fields.Float(string='Tax Amount JO', compute='_compute_l10n_jo_amounts')
    l10n_jo_discount = fields.Float(string='Discount Amount JO', compute='_compute_l10n_jo_amounts')
    l10n_jo_subtotal = fields.Float(string='Subtotal JO', compute='_compute_l10n_jo_amounts')
    l10n_jo_total = fields.Float(string='Total JO', compute='_compute_l10n_jo_amounts')

    @api.depends('price_unit', 'quantity', 'tax_ids', 'discount')
    def _compute_l10n_jo_amounts(self):
        for line in self:
            qty = round(line.quantity, 9)
            first_tax = line.tax_ids[:1] if line.tax_ids else False
            tax = round(first_tax.amount, 9) if first_tax else 0.00
            calc_tax = round(((tax / 100) + 1), 9)
            price_unit = round(line.price_unit, 9)
            if first_tax:
                price_unit = round(price_unit / calc_tax, 9) if first_tax.price_include else price_unit
            price_unit_qty = price_unit * qty
            disc = price_unit_qty * (line.discount * 0.01)
            discount = round(disc, 9)
            tax_amount = round(((qty * price_unit) - discount) * (tax * 0.01), 9)
            sub_after_tax = round((qty * price_unit) - discount, 9)
            sub_before_tax = round(sub_after_tax + tax_amount, 9)
            rounding_amount = round(sub_before_tax, 9)
            line.l10n_jo_price_unit = price_unit
            line.l10n_jo_tax = tax_amount
            line.l10n_jo_discount = discount
            line.l10n_jo_subtotal = sub_after_tax
            line.l10n_jo_total = rounding_amount


class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_jo_amount_untaxed = fields.Float(string='Untaxed Amount JO', compute='_compute_istd_amounts', digits=(12, 10))
    l10n_jo_amount_tax = fields.Float(string='Tax Amount JO', compute='_compute_istd_amounts', digits=(12, 10))
    l10n_jo_amount_total = fields.Float(string='Total Amount JO', compute='_compute_istd_amounts', digits=(12, 10))
    l10n_jo_amount_discount = fields.Float(string='Total Discount JO', compute='_compute_istd_amounts', digits=(12, 10))
    l10n_jo_amount_b4_discount = fields.Float(string='Amount Before Discount JO', compute='_compute_istd_amounts',
                                              digits=(12, 10))
    l10n_jo_uuid = fields.Char(string='Invoice UUID', copy=False)
    istd_invoice_sent = fields.Boolean(string='Invoice Sent', copy=False)
    istd_date_sent = fields.Datetime(string='Invoice Sending Time', copy=False)
    istd_einvoice = fields.Text(string='ISTD E-Invoice', copy=False)
    istd_qrcode = fields.Text(string='QR Code', copy=False)

    def button_draft(self):
        """
        Reset the invoice sent flag when the invoice is reset to draft
        """
        if self.istd_invoice_sent:
            raise UserError(_('You cannot reset the invoice sent flag on a draft invoice'))
        return super(AccountMove, self).button_draft()

    @api.model_create_multi
    def create(self, vals_list):
        """
        Generating UUID for each record being created
        """
        for vals in vals_list:
            vals['l10n_jo_uuid'] = uuid.uuid4().hex
        return super(AccountMove, self).create(vals_list)

    @api.depends('invoice_line_ids.l10n_jo_subtotal',
                 'invoice_line_ids.l10n_jo_tax',
                 'invoice_line_ids.l10n_jo_total',
                 'invoice_line_ids.l10n_jo_discount',
                 )
    def _compute_istd_amounts(self):
        for move in self:
            move.l10n_jo_amount_untaxed = sum(move.invoice_line_ids.mapped('l10n_jo_subtotal'))
            move.l10n_jo_amount_tax = sum(move.invoice_line_ids.mapped('l10n_jo_tax'))
            move.l10n_jo_amount_total = sum(move.invoice_line_ids.mapped('l10n_jo_total'))
            move.l10n_jo_amount_discount = sum(move.invoice_line_ids.mapped('l10n_jo_discount'))
            move.l10n_jo_amount_b4_discount = move.l10n_jo_amount_untaxed + move.l10n_jo_amount_discount

    def _post(self, soft=True):
        """
        Send invoices for if option (Send At Confirm) activated (with respect to company)
        :return:
        """

        for invoice in self.filtered(lambda m: m.move_type in ('out_invoice', 'out_refund')):
            for line in invoice.invoice_line_ids.filtered(
                    lambda x: x.display_type not in ('line_note', 'line_section')):
                if len(line.tax_ids) > 1:
                    raise UserError(_('Each invoice must one or no tax per line'))
        # if any(len(line.tax_ids) != 1 for line in self.filtered(lambda m: m.type in ['out_invoice', 'out_refund']).invoice_line_ids):
        #     raise UserError(_('Each invoice must contain one and only one tax per line'))
        result = super(AccountMove, self)._post(soft=soft)
        self.filtered(lambda m: m.company_id.l10n_jo_send_invoices_at_confirm).send_invoices_istd()
        return result

    @api.model
    def send_daily_invoices_istd(self):
        """
        This function will be called from a cron job to send daily invoices (depending on creation date)
        :return:
        """
        yesterday = (fields.Date.today() + relativedelta(days=-1)).strftime('%Y-%m-%d')
        datetime_from = datetime.strptime(yesterday, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        datetime_to = datetime.strptime(yesterday, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        domain = [('create_date', '>=', datetime_from), ('create_date', '<=', datetime_to)]
        invoices = self.search(domain)
        invoices.send_invoices_istd()

    def send_invoices_istd(self):
        invoices = self.filtered(lambda m: m.country_code == 'JO'
                                           and m.state == 'posted'
                                           and not m.istd_invoice_sent
                                           and m.move_type in ['out_invoice', 'out_refund'])
        for invoice in invoices:
            invoice._send_invoice_istd()

    def _send_invoice_istd(self):
        """
        Send invoice to ISTD
        """
        is_production = check_odoo_stage()
        if is_production == False:
            # If the environment is not production, then return True without sending the invoice (skip sending)
            return True

        if any(line.price_unit == 0.0 for line in self.invoice_line_ids.filtered(
                lambda x: x.display_type not in ('line_note', 'line_section'))):
            raise UserError(
                _('Each invoice must contain price unit greater than 0, if the product is bonus or free please add the unit price and discount it'))

        if any(len(line.tax_ids) > 1 for line in self.invoice_line_ids.filtered(
                lambda x: x.display_type not in ('line_note', 'line_section'))):
            raise UserError(_('Each invoice must one or no tax per line'))

        if any(not line.partner_id.property_account_position_id for line in self):
            raise UserError(_('Please set fiscal position for the partner'))

        invoice_xml = self._prepare_invoice_xml()
        encoded_invoice = b64encode((invoice_xml).encode()).decode('utf-8')
        # print(encoded_invoice)
        # url = "https://backend.jofotara.gov.jo/core/invoices/"
        url = "https://jofotara.flex-ops.com/core/invoices/"
        headers = {
            'Content-Type': 'application/json',
            'Client-id': f'{self.company_id.l10n_jo_client_id}',
            'Secret-Key': f'{self.company_id.l10n_jo_client_secret}',
        }
        payload = json.dumps({
            "invoice": f"{encoded_invoice}"
        })
        _logger.info(f"\n--> encoded_invoice: {encoded_invoice}")
        _logger.info(f"\n--> encoded_invoice: {invoice_xml}")
        response = requests.request(method='POST', url=url, headers=headers, data=payload, verify=False)
        if response.status_code == 200:
            response = response.json()
            _logger.info(f"\n--> ISTD request success:\n{pprint.pformat(response)}")
            if response['EINV_RESULTS']['status'] == 'PASS':
                self.istd_qrcode = response.get('EINV_QR', False)
                self.l10n_jo_uuid = response.get('EINV_INV_UUID', False)
                self.istd_invoice_sent = True
                self.istd_date_sent = fields.Datetime.now()

            if response['EINV_STATUS'] == 'SUBMITTED':
                self.message_post(
                    body="Invoice hase been sent to ISTD successfully",
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )
            if response['EINV_STATUS'] == 'ALREADY_SUBMITTED':
                self.message_post(
                    body="Invoice hase been ALREADY SUBMITTED to ISTD",
                    message_type='comment',
                    subtype_xmlid='mail.mt_note'
                )
        else:
            status_code = response.status_code
            response = response.json()
            _logger.info(f"ISTD request failed with status code: {status_code}")
            _logger.info(f"\n--> ISTD response:\n{pprint.pformat(response)}")
            raise UserError(
                _(f'ISTD request failed with status code: {status_code}, Error Message: {response}'))

    def _prepare_invoice_xml(self):
        self.ensure_one()

        code_l10n_jo_account_move = self.fiscal_position_id.code_l10n_jo if self.fiscal_position_id else ''
        code_l10n_jo_partner = self.partner_id.property_account_position_id.code_l10n_jo if self.partner_id.property_account_position_id else ''
        code_l10n_jo = code_l10n_jo_account_move or code_l10n_jo_partner

        if code_l10n_jo == False:
            raise UserError(_(f'Code is Unkown, code_l10n_jo is empty'))

        invoice_type = "388" if self.move_type == 'out_invoice' else "381"
        notes = html2plaintext(self.narration or "")
        notes = replace_special_characters(notes)
        xml_string = f"""<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2" xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2" xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2" xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2">
                <cbc:ProfileID>reporting:1.0</cbc:ProfileID>
                <cbc:ID>{self.name.replace('/', '')}</cbc:ID>
                <cbc:UUID>{self.l10n_jo_uuid or uuid.uuid4().hex}</cbc:UUID>
                <cbc:IssueDate>{self.invoice_date.strftime('%Y-%m-%d')}</cbc:IssueDate>
                <cbc:InvoiceTypeCode name="{code_l10n_jo}">{invoice_type}</cbc:InvoiceTypeCode>
                <cbc:Note>{notes}</cbc:Note>
                <cbc:DocumentCurrencyCode>{self.currency_id.name if self.currency_id else 'JOD'}</cbc:DocumentCurrencyCode>
                <cbc:TaxCurrencyCode>{self.currency_id.name if self.currency_id else 'JOD'}</cbc:TaxCurrencyCode>
                {self._get_origin_invoice_details()}
                <cac:AdditionalDocumentReference>
                    <cbc:ID>ICV</cbc:ID>
                    <cbc:UUID>{'1'}</cbc:UUID>
                </cac:AdditionalDocumentReference>
                {self._get_supplier_party()}
                {self._get_customer_party()}
                <cac:SellerSupplierParty>
                    <cac:Party>
                        <cac:PartyIdentification>
                            <cbc:ID>{self.company_id.l10n_jo_activity_number or ''}</cbc:ID>
                        </cac:PartyIdentification>
                    </cac:Party>
                </cac:SellerSupplierParty>
                {self._get_payment_means()}
                <cac:AllowanceCharge>
                    <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                    <cbc:AllowanceChargeReason>discount</cbc:AllowanceChargeReason>
                    <cbc:Amount currencyID="JO">{formate_number(self.l10n_jo_amount_discount)}</cbc:Amount>
                </cac:AllowanceCharge>
                <cac:TaxTotal>
                    <cbc:TaxAmount currencyID="JO">{formate_number(self.l10n_jo_amount_tax)}</cbc:TaxAmount>
                </cac:TaxTotal>
                <cac:LegalMonetaryTotal>
                    <cbc:TaxExclusiveAmount currencyID="JO">{formate_number(self.l10n_jo_amount_b4_discount)}</cbc:TaxExclusiveAmount>
                    <cbc:TaxInclusiveAmount currencyID="JO">{formate_number(self.l10n_jo_amount_total)}</cbc:TaxInclusiveAmount>
                    <cbc:AllowanceTotalAmount currencyID="JO">{formate_number(self.l10n_jo_amount_discount)}</cbc:AllowanceTotalAmount>
                    <cbc:PayableAmount currencyID="JO">{formate_number(self.l10n_jo_amount_total)}</cbc:PayableAmount>
                </cac:LegalMonetaryTotal>
                {self._prepare_invoice_lines_xml()}
            </Invoice>
            """
        return xml_string

    def get_counter_id_for_invoice_lines_xml(self, product_id):
        '''
        Get the index of the line in the invoice lines
        :param product_id:
        :return:
            index: int
        '''
        invoice_line_ids = self.reversed_entry_id.invoice_line_ids.filtered(
            lambda x: x.display_type not in ('line_note', 'line_section')
        )
        for index, line in enumerate(invoice_line_ids, start=1):  # Start from 1 for human-readable indexing
            if line.product_id.id == product_id:
                _logger.info(f"\n--> ISTD index: {index}")
                return index
        return None

    def _prepare_invoice_lines_xml(self):
        self.ensure_one()
        lines_as_xml = ""
        counter = 1
        for line in self.invoice_line_ids:
            if line.display_type not in ('line_note', 'line_section'):
                schemeAgencyID = line.tax_ids[:1].l10n_type
                if not schemeAgencyID:
                    raise UserError(_(f'Tax Type is Unkown, {schemeAgencyID}'))
                if len(line.tax_ids) > 1 and len(set(line.tax_ids.mapped('l10n_type'))) > 1:
                    raise UserError(_('Each invoice must contain one and only one tax per line'))
                _logger.info(f"\n--> ISTD schemeAgencyID: {schemeAgencyID}")
                counter_refund = 0
                if self.move_type == 'out_refund':
                    counter_refund = self.get_counter_id_for_invoice_lines_xml(line.product_id.id)
                lines_as_xml += f"""<cac:InvoiceLine>
                        <cbc:ID>{counter if self.move_type == 'out_invoice' else counter_refund}</cbc:ID>
                        <cbc:InvoicedQuantity unitCode="PCE">{formate_number(line.quantity, 3)}</cbc:InvoicedQuantity>
                        <cbc:LineExtensionAmount currencyID="JO">{formate_number(line.l10n_jo_subtotal)}</cbc:LineExtensionAmount>
                        <cac:TaxTotal>
                            <cbc:TaxAmount currencyID="JO">{formate_number(line.l10n_jo_tax)}</cbc:TaxAmount>
                            <cbc:RoundingAmount currencyID="JO">{formate_number(line.l10n_jo_total)}</cbc:RoundingAmount>
                            <cac:TaxSubtotal>
                                <cbc:TaxAmount currencyID="JO">{formate_number(line.l10n_jo_tax)}</cbc:TaxAmount>
                                <cac:TaxCategory>
                                    <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5305">{schemeAgencyID}</cbc:ID>
                                    <cbc:Percent>{line.tax_ids[:1].amount if line.tax_ids else '0.00'}</cbc:Percent>
                                    <cac:TaxScheme>
                                        <cbc:ID schemeAgencyID="6" schemeID="UN/ECE 5153">VAT</cbc:ID>
                                    </cac:TaxScheme>
                                </cac:TaxCategory>
                            </cac:TaxSubtotal>
                        </cac:TaxTotal>
                        <cac:Item>
                            <cbc:Name>{replace_special_characters(str(line.name)) or replace_special_characters(str(line.product_id.name))}</cbc:Name>
                        </cac:Item>
                        <cac:Price>
                            <cbc:PriceAmount currencyID="JO">{formate_number(line.l10n_jo_price_unit)}</cbc:PriceAmount>
                            <cac:AllowanceCharge>
                                <cbc:ChargeIndicator>false</cbc:ChargeIndicator>
                                <cbc:AllowanceChargeReason>DISCOUNT</cbc:AllowanceChargeReason>
                                <cbc:Amount currencyID="JO">{formate_number(line.l10n_jo_discount)}</cbc:Amount>
                            </cac:AllowanceCharge>
                        </cac:Price>
                    </cac:InvoiceLine>"""
                counter += 1
        return lines_as_xml

    def _get_origin_invoice_details(self):
        '''
        This part related to credit note
        :return:
        '''
        self.ensure_one()
        if self.move_type != 'out_refund':
            return ''
        details_as_xml = f"""
        <cac:BillingReference>
          <cac:InvoiceDocumentReference>
            <cbc:ID>{self.reversed_entry_id and replace_special_characters(str(self.reversed_entry_id.name.replace('/', ''))) or ''}</cbc:ID>
            <cbc:UUID>{self.reversed_entry_id.l10n_jo_uuid or ''}</cbc:UUID>
            <cbc:DocumentDescription>{formate_number(self.amount_total)}</cbc:DocumentDescription>
          </cac:InvoiceDocumentReference>
        </cac:BillingReference>
        """
        return details_as_xml

    def _get_payment_means(self):
        '''
        This part related to credit note
        :return:
        '''
        self.ensure_one()
        if self.move_type != 'out_refund':
            return ''
        details_as_xml = f"""
        <cac:PaymentMeans>
            <cbc:PaymentMeansCode listID="UN/ECE 4461">10</cbc:PaymentMeansCode>
            <cbc:InstructionNote>In cash</cbc:InstructionNote>
        </cac:PaymentMeans>
        """
        return details_as_xml

    def _get_supplier_party(self):
        self.ensure_one()
        vat_no = self.company_id.vat or ''
        partner_name = replace_special_characters(str(self.company_id.name))
        details_as_xml = f"""
        <cac:AccountingSupplierParty>
            <cac:Party>
                <cac:PostalAddress>
                    <cac:Country>
                        <cbc:IdentificationCode>JO</cbc:IdentificationCode>
                    </cac:Country>
                </cac:PostalAddress>
                <cac:PartyTaxScheme>
                    <cbc:CompanyID>{vat_no}</cbc:CompanyID>
                    <cac:TaxScheme>
                        <cbc:ID>VAT</cbc:ID>
                    </cac:TaxScheme>
                </cac:PartyTaxScheme>
                <cac:PartyLegalEntity>
                    <cbc:RegistrationName>{partner_name}</cbc:RegistrationName>
                </cac:PartyLegalEntity>
            </cac:Party>
        </cac:AccountingSupplierParty>
        """
        return details_as_xml

    def _get_customer_party(self):
        self.ensure_one()
        # if self.move_type == 'out_invoice':
        vat_no = self.partner_id.vat or ''
        zip_no = self.partner_id.zip if len(self.partner_id.zip or '') == 5 else ''
        state_code = self.partner_id.state_id.code or ''
        partner_name = replace_special_characters(str(self.partner_id.display_name))
        partner_phone = self.partner_id.phone or ''
        details_as_xml = f"""
        <cac:AccountingCustomerParty>
            <cac:Party>
                <cac:PartyIdentification>
                    <cbc:ID schemeID="{'TN'}">{vat_no}</cbc:ID>
                </cac:PartyIdentification>
                <cac:PostalAddress>
                    <cbc:PostalZone>{zip_no}</cbc:PostalZone>
                    <cbc:CountrySubentityCode>{state_code}</cbc:CountrySubentityCode>
                    <cac:Country>
                        <cbc:IdentificationCode>JO</cbc:IdentificationCode>
                    </cac:Country>
                </cac:PostalAddress>
                <cac:PartyTaxScheme>
                    <cbc:CompanyID>{'1'}</cbc:CompanyID>
                    <cac:TaxScheme>
                        <cbc:ID>VAT</cbc:ID>
                    </cac:TaxScheme>
                </cac:PartyTaxScheme>
                <cac:PartyLegalEntity>
                    <cbc:RegistrationName>{partner_name}</cbc:RegistrationName>
                </cac:PartyLegalEntity>
            </cac:Party>
            <cac:AccountingContact>
                <cbc:Telephone>{partner_phone}</cbc:Telephone>
            </cac:AccountingContact>
        </cac:AccountingCustomerParty>
        """
        return details_as_xml

# -*- coding: utf-8 -*-
