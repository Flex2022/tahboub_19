from odoo import api, fields, models
import base64
import qrcode
from io import BytesIO

class AccountMove(models.Model):
    _inherit = 'account.move'

    qr_code_base64 = fields.Char(compute="_compute_qr_code", store=False)

    def generate_qr(self, value):
        qr = qrcode.make(value)
        qr_io = BytesIO()
        qr.save(qr_io, format='PNG')
        return base64.b64encode(qr_io.getvalue()).decode()

    def _compute_qr_code(self):
        for record in self:
            record.qr_code_base64 = self.generate_qr(record.istd_qrcode)