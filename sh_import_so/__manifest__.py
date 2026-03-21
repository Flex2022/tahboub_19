{
    "name": "Import Sale Order Wizard",
    "summary": "Provides import.so.wizard model used by legacy Sale Order import actions",
    "version": "19.0.1.0.0",
    "author": "Migration Patch",
    "license": "LGPL-3",
    "depends": ["sale"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/import_so_wizard_views.xml"
    ],
    "installable": True,
    "application": False,
}

