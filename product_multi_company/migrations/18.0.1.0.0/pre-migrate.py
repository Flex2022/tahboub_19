# Copyright 2025 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from logging import getLogger

from odoo import api
from odoo.tools import safe_eval

SUPERUSER_UID = 1

_logger = getLogger(__name__)


PREVIOUS_DOMAIN = [
    "|",
    ("company_ids", "in", "COMPANY_IDS"),
    ("company_ids", "=", False),
]


UPSTREAM_DOMAIN = (
    "['|', ('company_id', 'parent_of', company_ids), ('company_id', '=', False)]"
)


def migrate(cr, version):
    """Restore upstream partner rule without openupgradelib."""
    env = api.Environment(cr, SUPERUSER_UID, {})
    rule = env.ref("product.product_comp_rule", raise_if_not_found=False)

    if not rule:
        return

    try:
        domain = safe_eval(rule.domain_force, locals_dict={"company_ids": "COMPANY_IDS"})
    except Exception:
        _logger.warning("Unable to evaluate domain_force")
        return

    if domain == PREVIOUS_DOMAIN:
        rule.domain_force = UPSTREAM_DOMAIN
        _logger.info("Restored upstream partner rule")
