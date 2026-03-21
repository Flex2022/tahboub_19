from datetime import datetime

from odoo import fields, models
from odoo.exceptions import AccessDenied
from odoo.http import request
from user_agents import parse


class res_users(models.Model):
    _inherit = 'res.users'

    login_log_ids = fields.One2many('login.log', 'user_id', 'Sessions')

    def action_kill_all_session(self):
        for record in self:
            return record.login_log_ids.logout_button()

    def _login(self, credential, user_agent_env=None):
        try:
            auth_info = super()._login(credential, user_agent_env=user_agent_env)
        except ValueError:
            # Corrupted hash should not crash /web/login with a 500.
            raise AccessDenied()

        # Keep custom session logging, but never break authentication flow.
        try:
            uid = auth_info.get('uid')
            if not uid or not request:
                return auth_info

            user = self.sudo().browse(uid)
            if not user or user.has_group('base.group_portal'):
                return auth_info

            sid = request.session.sid if request.session else False
            if not sid:
                return auth_info

            login_log_obj = self.env['login.log'].sudo()
            if login_log_obj.search([('user_agent', '=', sid)], limit=1):
                return auth_info

            user_agent = parse(request.httprequest.environ.get('HTTP_USER_AGENT', ''))
            device = user_agent.device.family
            if device == 'Other':
                if user_agent.is_pc:
                    device = 'PC'
                elif user_agent.is_mobile:
                    device = 'Mobile'
                elif user_agent.is_tablet:
                    device = 'Tablet'

            login_log_obj.create({
                'login_date': datetime.now(),
                'user_id': uid,
                'user_agent': sid,
                'state': 'active',
                'browser': user_agent.browser.family,
                'device': device,
                'os': user_agent.os.family,
            })
        except Exception:
            # Do not block user login due to optional audit log errors.
            self.env.cr.rollback()

        return auth_info
