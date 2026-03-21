# -*- coding: utf-8 -*-
# from odoo import api, fields, models, _
# from odoo.tools import date_utils
# from odoo.tools.float_utils import float_compare
# import math
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class SaAttendance(models.Model):
#     _inherit = "hr.attendance"
#
#     currency_id = fields.Many2one(
#         'res.currency', 'Currency',
#         store=True, related='employee_id.company_id.currency_id', tracking=True
#     )
#     waved = fields.Boolean(default=False, tracking=True)
#     late_minutes = fields.Integer(readonly=False, pre_compute=True, store=True, compute="_compute_late_minutes", tracking=True)
#     deduction_amount = fields.Monetary(store=True, pre_compute=True, compute="_compute_deduction", readonly=False, tracking=True)
#     display_late_minutes = fields.Float(readonly=False, string="Late", pre_compute=True, store=True, compute="_compute_late_minutes")
#
#     # ✅ NEW (Tracking flag only - does NOT replace ICP logic)
#     late_deducted = fields.Boolean(default=False, copy=False, tracking=True)
#
#     @api.depends("employee_id", "check_in")
#     def _compute_late_minutes(self):
#         for r in self:
#             r.late_minutes = 0
#             r.display_late_minutes = 0
#
#             if not r.employee_id.resource_calendar_id or not r.check_in or not r.employee_id:
#                 r.late_minutes = 0
#                 r.display_late_minutes = 0
#                 continue
#
#             if not r.employee_id.tz:
#                 r.late_minutes = 0
#                 r.display_late_minutes = 0
#                 continue
#
#             working_hours = r.employee_id.resource_calendar_id
#             check_in = date_utils._softatt_localize(r.check_in, r.employee_id.tz)
#             current_day = check_in.weekday()
#             result = working_hours._softatt_get_shift_start_and_end_bot(current_day, check_in)
#             if not result:
#                 r.late_minutes = 0
#                 r.display_late_minutes = 0
#                 return
#
#             shift_start_datetime = result[0]
#             time_difference = check_in - shift_start_datetime
#             difference_in_minutes = time_difference.total_seconds() / 60
#             r.late_minutes = difference_in_minutes
#             r.display_late_minutes = (difference_in_minutes / 60) if difference_in_minutes > 0 else 0.0
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         result = super(SaAttendance, self).create(vals_list)
#         result._compute_late_minutes()
#         result._compute_deduction()
#         return result
#
#     @api.depends("employee_id", "late_minutes")
#     def _compute_deduction(self):
#         for r in self:
#             if not r.employee_id.attendance_rule_id or r.late_minutes == 0:
#                 r.deduction_amount = 0.0
#                 return
#             r.deduction_amount = r.employee_id.attendance_rule_id._compute_deduction(
#                 r.employee_id, r.check_in, r.late_minutes
#             )
#
#     def get_compute_deduction(self):
#         for r in self:
#             r._compute_deduction()
#
#     def action_wave_deduction(self):
#         for r in self:
#             r.waved = True
#
#     def action_unwave_deduction(self):
#         for r in self:
#             r.waved = False
#
#
#     def _get_hours_per_day(self, employee):
#         cal = employee.resource_calendar_id
#         return float(cal.hours_per_day) if cal and cal.hours_per_day else 8.0
#
#     def _get_hours_to_deduct_from_late(self, late_hours):
#
#         if not late_hours or late_hours < 0.25:
#             return 0.0
#         h = float(math.ceil(late_hours))
#         if h > 8:
#             h = 8.0
#         return h
#
#     def _get_annual_leave_type_artifex(self):
#         return self.env['hr.leave.type'].sudo().search([
#             ('artifex_annual_allocation', '=', True)
#         ], limit=1)
#
#     @api.model
#     def cron_deduct_late_from_annual_allocation_direct(self, run_date=None):
#
#         annual_type = self._get_annual_leave_type_artifex()
#         if not annual_type:
#             return True
#
#         ICP = self.env['ir.config_parameter'].sudo()
#         Allocation = self.env['hr.leave.allocation'].sudo()
#
#         attendances = self.env['hr.attendance'].sudo().search([
#             ('check_in', '!=', False),
#             ('employee_id', '!=', False),
#             ('waved', '=', False),
#             ('display_late_minutes', '>=', 0.25),
#         ], order="check_in asc", limit=800)
#
#         for att in attendances:
#             emp = att.employee_id
#
#             dt_local = date_utils._softatt_localize(att.check_in, emp.tz or 'UTC')
#             day_str = fields.Date.to_string(dt_local.date())
#             key = f"late_deduct_day:{emp.id}:{day_str}"
#             if ICP.get_param(key):
#                 if not att.late_deducted:
#                     att.write({'late_deducted': True})
#                 continue
#
#             late_hours = float(att.display_late_minutes or 0.0)
#             deduct_hours = att._get_hours_to_deduct_from_late(late_hours)
#             if not deduct_hours:
#                 att.write({'late_deducted': True})
#                 ICP.set_param(key, "no_deduct")
#                 continue
#
#             hours_per_day = att._get_hours_per_day(emp)
#             deduct_days = deduct_hours / hours_per_day
#
#             alloc = Allocation.search([
#                 ('employee_id', '=', emp.id),
#                 ('holiday_status_id', '=', annual_type.id),
#                 ('state', '=', 'validate'),
#             ], order="id desc", limit=1)
#
#             if not alloc:
#                 emp.message_post(body=f"[AUTO] ما في Allocation سنوي (Artifex) لخصم {deduct_hours:.2f} ساعة (≈ {deduct_days:.3f} يوم) بتاريخ {day_str}.")
#                 ICP.set_param(key, "no_alloc")
#                 continue
#
#             taken = float(getattr(alloc, 'leaves_taken', 0.0) or 0.0)
#             current_days = float(alloc.number_of_days or 0.0)
#             new_days = current_days - deduct_days
#
#             if float_compare(new_days, taken, precision_digits=6) < 0:
#                 emp.message_post(body=f"[AUTO] الرصيد غير كافي لخصم {deduct_hours:.2f} ساعة (≈ {deduct_days:.3f} يوم) بتاريخ {day_str}.")
#                 ICP.set_param(key, "insufficient")
#                 continue
#
#             alloc.write({'number_of_days': new_days})
#
#             msg = (
#                 f"[AUTO] تم خصم {deduct_hours:.2f} ساعة من رصيد الإجازة السنوية "
#                 f"(≈ {deduct_days:.3f} يوم) بسبب التأخير بتاريخ {day_str}."
#             )
#             emp.message_post(body=msg)
#
#             day_atts = self.env['hr.attendance'].sudo().search([
#                 ('employee_id', '=', emp.id),
#                 ('check_in', '!=', False),
#             ])
#             att.write({'late_deducted': True})
#
#             ICP.set_param(key, f"{deduct_days:.6f}")
#
#         return True
# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import date_utils
from odoo.tools.float_utils import float_compare
import math
import logging

_logger = logging.getLogger(__name__)


class SaAttendance(models.Model):
    _inherit = "hr.attendance"

    currency_id = fields.Many2one(
        'res.currency', 'Currency',
        store=True, related='employee_id.company_id.currency_id', tracking=True
    )
    waved = fields.Boolean(default=False, tracking=True)
    late_minutes = fields.Integer(readonly=False, pre_compute=True, store=True, compute="_compute_late_minutes", tracking=True)
    deduction_amount = fields.Monetary(store=True, pre_compute=True, compute="_compute_deduction", readonly=False, tracking=True)
    display_late_minutes = fields.Float(readonly=False, string="Late", pre_compute=True, store=True, compute="_compute_late_minutes")

    # ✅ NEW (Tracking flag only - does NOT replace ICP logic)
    late_deducted = fields.Boolean(default=False, copy=False, tracking=True)

    @api.depends("employee_id", "check_in")
    def _compute_late_minutes(self):
        for r in self:
            r.late_minutes = 0
            r.display_late_minutes = 0

            if not r.employee_id.resource_calendar_id or not r.check_in or not r.employee_id:
                r.late_minutes = 0
                r.display_late_minutes = 0
                continue

            if not r.employee_id.tz:
                r.late_minutes = 0
                r.display_late_minutes = 0
                continue

            working_hours = r.employee_id.resource_calendar_id
            check_in = date_utils._softatt_localize(r.check_in, r.employee_id.tz)
            current_day = check_in.weekday()
            result = working_hours._softatt_get_shift_start_and_end_bot(current_day, check_in)
            if not result:
                r.late_minutes = 0
                r.display_late_minutes = 0
                return

            shift_start_datetime = result[0]
            time_difference = check_in - shift_start_datetime
            difference_in_minutes = time_difference.total_seconds() / 60
            r.late_minutes = difference_in_minutes
            r.display_late_minutes = (difference_in_minutes / 60) if difference_in_minutes > 0 else 0.0

    @api.model_create_multi
    def create(self, vals_list):
        result = super(SaAttendance, self).create(vals_list)
        result._compute_late_minutes()
        result._compute_deduction()
        return result

    @api.depends("employee_id", "late_minutes")
    def _compute_deduction(self):
        for r in self:
            if not r.employee_id.attendance_rule_id or r.late_minutes == 0:
                r.deduction_amount = 0.0
                return
            r.deduction_amount = r.employee_id.attendance_rule_id._compute_deduction(
                r.employee_id, r.check_in, r.late_minutes
            )

    def get_compute_deduction(self):
        for r in self:
            r._compute_deduction()

    def action_wave_deduction(self):
        for r in self:
            r.waved = True

    def action_unwave_deduction(self):
        for r in self:
            r.waved = False


    def _get_hours_per_day(self, employee):
        cal = employee.resource_calendar_id
        return float(cal.hours_per_day) if cal and cal.hours_per_day else 8.0

    def _get_hours_to_deduct_from_late(self, late_hours):

        if not late_hours or late_hours < 0.25:
            return 0.0
        h = float(math.ceil(late_hours))
        if h > 8:
            h = 8.0
        return h

    def _get_annual_leave_type_artifex(self):
        return self.env['hr.leave.type'].sudo().search([
            ('artifex_annual_allocation', '=', True)
        ], limit=1)

    @api.model
    def cron_deduct_late_from_annual_allocation_direct(self, run_date=None):

        annual_type = self._get_annual_leave_type_artifex()
        if not annual_type:
            return True

        ICP = self.env['ir.config_parameter'].sudo()
        Allocation = self.env['hr.leave.allocation'].sudo()

        attendances = self.env['hr.attendance'].sudo().search([
            ('check_in', '!=', False),
            ('employee_id', '!=', False),
            ('waved', '=', False),
            ('display_late_minutes', '>=', 0.25),
        ], order="check_in asc", limit=800)

        for att in attendances:
            emp = att.employee_id

            dt_local = date_utils._softatt_localize(att.check_in, emp.tz or 'UTC')
            day_str = fields.Date.to_string(dt_local.date())
            key = f"late_deduct_day:{emp.id}:{day_str}"
            if ICP.get_param(key):
                if not att.late_deducted:
                    att.write({'late_deducted': True})
                continue

            late_hours = float(att.display_late_minutes or 0.0)
            deduct_hours = att._get_hours_to_deduct_from_late(late_hours)
            if not deduct_hours:
                att.write({'late_deducted': True})
                ICP.set_param(key, "no_deduct")
                continue

            hours_per_day = att._get_hours_per_day(emp)
            deduct_days = deduct_hours / hours_per_day

            alloc = Allocation.search([
                ('employee_id', '=', emp.id),
                ('holiday_status_id', '=', annual_type.id),
                ('state', '=', 'validate'),
            ], order="id desc", limit=1)

            if not alloc:
                emp.message_post(body=f"[AUTO] ما في Allocation سنوي (Artifex) لخصم {deduct_hours:.2f} ساعة (≈ {deduct_days:.3f} يوم) بتاريخ {day_str}.")
                ICP.set_param(key, "no_alloc")
                continue

            taken = float(getattr(alloc, 'leaves_taken', 0.0) or 0.0)
            current_days = float(alloc.number_of_days or 0.0)
            new_days = current_days - deduct_days

            if float_compare(new_days, taken, precision_digits=6) < 0:
                emp.message_post(body=f"[AUTO] الرصيد غير كافي لخصم {deduct_hours:.2f} ساعة (≈ {deduct_days:.3f} يوم) بتاريخ {day_str}.")
                ICP.set_param(key, "insufficient")
                continue

            alloc.write({'number_of_days': new_days})

            msg = (
                f"[AUTO] تم خصم {deduct_hours:.2f} ساعة من رصيد الإجازة السنوية "
                f"(≈ {deduct_days:.3f} يوم) بسبب التأخير بتاريخ {day_str}."
            )
            emp.message_post(body=msg)

            day_atts = self.env['hr.attendance'].sudo().search([
                ('employee_id', '=', emp.id),
                ('check_in', '!=', False),
            ])
            att.write({'late_deducted': True})

            ICP.set_param(key, f"{deduct_days:.6f}")

        return True


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    artifex_annual_allocation = fields.Boolean(string="Artifex Annual Allocation", default=False,
                                               help="If checked, the leave type will have an annual allocation for employees.")


