# Copyright 2018, 2020 Heliconia Solutions Pvt Ltd (https://heliconia.io)

import logging

from odoo import api, models
from odoo.http import request

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    def _login(self, credential, user_agent_env=None):
        login = credential.get("login")
        ip = request.httprequest.environ.get("REMOTE_ADDR") if request else "n/a"
        try:
            auth_info = super()._login(credential, user_agent_env=user_agent_env)
        except Exception:
            _logger.info("Login failed for login:%s from %s", login, ip)
            raise
        _logger.info("Login successful for login:%s from %s", login, ip)
        return auth_info

    @api.model
    def check_for_user_simulation(self, user_id):
        # got the call here : we will check here the group and if it is simulated or not
        if (
            user_id
            in self.env.ref("hspl_user_simulation.group_user_simulation").users.ids
        ):
            return True
        if (
            self.env.ref("hspl_user_simulation.group_user_simulation").users.ids
            and user_id
            not in self.env.ref("hspl_user_simulation.group_user_simulation").users.ids
            and request.session.get("is_simulated")
        ):
            return True
        request.session["is_simulated"] = False
        return False

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        if self.env.context.get("user_simulation_context"):
            user_ids = self.env.ref("base.group_user").users.ids
            args = args or []
            args += [("id", "in", user_ids)]
        return super(ResUsers, self).name_search(
            name=name, args=args, operator=operator, limit=limit
        )
