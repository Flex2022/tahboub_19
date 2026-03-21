# -*- coding: utf-8 -*-
{
    "name": "TAH Lot Sub Serial",
    "version": "19.0.1.0.0",
    "summary": "Sub-serial tracking inside batch lots",
    "description": "Track sub-serial numbers inside lot-tracked products.",
    "author": "Tahboub",
    "license": "LGPL-3",
    "depends": ["stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_production_lot_views.xml",
        "views/stock_move_line_views.xml",
        "views/report_deliveryslip.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
