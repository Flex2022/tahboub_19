from odoo import SUPERUSER_ID, http, _, exceptions, fields
from odoo.http import request

import base64
import json
from odoo.tools import file_path

class OdooAPI(http.Controller):

    @http.route('/api/get_purchase_order', type='http', auth='none', methods=['GET'], csrf=False)
    def get_purchase_order(self, **params):
        company_id = params.get('company_id')
        limit = int(params.get('limit') or 10)  # Ensure `limit` is also treated as an integer

        font_path = file_path('flex_currencies_reports', 'static/src/fonts/arial.ttf')

        if not company_id:
            return http.Response(json.dumps({'error': 'company_id is required'}), content_type='application/json')

        try:
            company_id = int(company_id)  # Convert company_id to an integer
        except ValueError:
            return http.Response(json.dumps({'error': 'Invalid company_id'}), content_type='application/json')

        purchase_orders = request.env['purchase.order'].sudo().search([('company_id', '=', company_id)], limit=limit)

        # Generate HTML table
        table_rows = ""
        for order in purchase_orders:
            order_lines = "".join(
                f"""
                <tr>
                    <td>{line.order_id.name}</td>
                    <td>{line.product_id.name}</td>
                    <td>{line.product_qty}</td>
                    <td>{line.price_unit}</td>
                    <td>{line.price_subtotal}</td>
                    <td>{line.price_total}</td>
                    <td>{line.additional_currency.name if line.additional_currency else ''}</td>
                    <td>{line.price_unit_iqd}</td>
                    <td>{line.price_subtotal_iqd}</td>
                    <td>{line.price_total_iqd}</td>
                </tr>
                """
                for line in order.order_line
            )
            table_rows += f"""
            <tr>
                <td>{order.name}</td>
                <td>{order.date_order.strftime('%Y-%m-%d %H:%M:%S') if order.date_order else ''}</td>
                <td>{order.partner_id.name}</td>
                <td>{order.currency_id.name}</td>
                <td>{order.additional_currency.name if order.additional_currency else ''}</td>
                <td>{order.additional_currency_rate}</td>
                <td>{order.amount_untaxed}</td>
                <td>{order.amount_tax}</td>
                <td>{order.amount_total}</td>
                <td>{order.state}</td>
            </tr>
            <tr>
                <td colspan="10">
                    <table border="1">
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Product</th>
                                <th>Quantity</th>
                                <th>Unit Price</th>
                                <th>Subtotal</th>
                                <th>Total</th>
                                <th>Additional Currency</th>
                                <th>Unit Price (IQD)</th>
                                <th>Subtotal (IQD)</th>
                                <th>Total (IQD)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {order_lines}
                        </tbody>
                    </table>
                </td>
            </tr>
            """

        # Embed the font into the HTML using @font-face
        html_response = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Purchase Orders</title>
            <style>
                @font-face {{
                    font-family: 'CustomArial';
                    src: url('data:font/ttf;base64,{base64.b64encode(open(font_path, "rb").read()).decode()}') format('truetype');
                }}
                body {{
                    font-family: 'CustomArial', Arial, sans-serif;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <h1>Purchase Orders</h1>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Date Order</th>
                        <th>Partner</th>
                        <th>Currency</th>
                        <th>Additional Currency</th>
                        <th>Additional Currency Rate</th>
                        <th>Amount Untaxed</th>
                        <th>Amount Tax</th>
                        <th>Amount Total</th>
                        <th>State</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </body>
        </html>
        """

        return http.Response(html_response, content_type='text/html; charset=utf-8')






