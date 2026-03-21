from odoo import api, fields, models


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    artifex_annual_allocation = fields.Boolean(string="Artifex Annual Allocation", default=False,
                                               help="If checked, the leave type will have an annual allocation for employees.")


class HrLeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    lastcall = fields.Date("Date of the last accrual allocation", default=fields.Date.context_today)
    nextcall = fields.Date("Date of the next accrual allocation", default=False)