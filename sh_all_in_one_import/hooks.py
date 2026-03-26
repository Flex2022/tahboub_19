from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """Cleanup stale menu actions that point to models not present in registry.

    This keeps upgraded databases usable when old XMLIDs remain from previous versions
    but some legacy wizard models were dropped or moved.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    model_names = set(env.registry.models)

    action_data = env['ir.model.data'].sudo().search([
        ('module', '=', 'sh_all_in_one_import'),
        ('model', '=', 'ir.actions.act_window'),
    ])

    for data in action_data:
        action = env['ir.actions.act_window'].sudo().browse(data.res_id)
        if not action.exists():
            continue
        if action.res_model and action.res_model not in model_names:
            action_ref = f'ir.actions.act_window,{action.id}'
            menus = env['ir.ui.menu'].sudo().with_context(active_test=False).search([
                ('action', '=', action_ref),
            ])
            if menus:
                menus.write({'action': False})
            action.unlink()

