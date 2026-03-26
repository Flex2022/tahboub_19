"""Compatibility migration shim for Odoo 19 without openupgradelib."""

from odoo import api
from odoo.tools.convert import convert_file

SUPERUSER_UID = 1


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_UID, {})
    convert_file(
        env,
        "stock_request",
        "migrations/15.0.1.4.0/noupdate_changes.xml",
        {},
        "init",
        noupdate=True,
    )
