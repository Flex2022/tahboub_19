# -*- coding: utf-8 -*-
from odoo import fields, models, api

ARABIC_WEEKDAYS = {
    0: 'الاثنين',
    1: 'الثلاثاء',
    2: 'الأربعاء',
    3: 'الخميس',
    4: 'الجمعة',
    5: 'السبت',
    6: 'الأحد',
}
class SaleOrder(models.Model):
    _inherit = "sale.order"

    fiscal_position_id = fields.Many2one(
        'account.fiscal.position', string='Fiscal Position',
        domain="[('company_id', '=', company_id)]", check_company=True,
        help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices."
             "The default value comes from the customer.",groups="base.group_user")

    kitchen_type_id = fields.Many2one('sale.spec', string="Kitchen Type", domain="[('spec_type', '=', 'kitchen_type')]")
    sliding_wood_id = fields.Many2one('sale.spec', string="Sliding Wood", domain="[('spec_type', '=', 'sliding_wood')]")
    door_model_id = fields.Many2one('sale.spec', string="Door Model", domain="[('spec_type', '=', 'door_model')]")
    pillar_sold_id = fields.Many2one('sale.spec', string=" Solid Column", domain="[('spec_type', '=', 'solid_column')]")
    laminate_grains_id = fields.Many2one('sale.spec', string="Laminate Grains",
                                         domain="[('spec_type', '=', 'laminate_grains')]")
    wood_color_id = fields.Char(string=" Wood Color")
    wood_color2_id = fields.Char(string="Wood Color 2")
    cornice_type_id = fields.Many2one('sale.spec', string="Cornice Type", domain="[('spec_type', '=', 'cornice_type')]")
    light_pelmets_id = fields.Many2one('sale.spec', string="Light Pelmets",
                                       domain="[('spec_type', '=', 'light_pelmets')]")
    glass_cabinets_type_id = fields.Many2one('sale.spec', string="Glass Cabinets Type",
                                             domain="[('spec_type', '=', 'glass_cabinets_type')]")
    glass_color_id = fields.Many2one('sale.spec', string="Glass Color", domain="[('spec_type', '=', 'glass_color')]")
    bench_upholstery_id = fields.Many2one('sale.spec', string="Bench Upholstery",
                                          domain="[('spec_type', '=', 'bench_upholster')]")
    worktop_type_id = fields.Many2one('sale.spec', string="Worktop Type", domain="[('spec_type', '=', 'worktop_type')]")
    worktop_edge_id = fields.Many2one('sale.spec', string="worktop Edge", domain="[('spec_type', '=', 'worktop_edge')]")
    worktop_thickness_id = fields.Many2one('sale.spec', string="Worktop Thickness",
                                           domain="[('spec_type', '=', 'worktop_thickness')]")
    worktop_color_id = fields.Many2one('sale.spec', string="Worktop Color", domain="[('spec_type', '=', 'worktop_color')]")
    sink_id = fields.Many2one('sale.spec', string="Sink 1", domain="[('spec_type', '=', 'sink')]")
    mixer_id = fields.Many2one('sale.spec', string="Mixer", domain="[('spec_type', '=', 'mixer')]")
    installation_method_id = fields.Many2one('sale.spec', string="Installation Method",
                                             domain="[('spec_type', '=', 'installation_method')]")
    installation_method_id2 = fields.Many2one('sale.spec', string="Installation Method 2",
                                                domain="[('spec_type', '=', 'installation_method')]")
    installation_method_id3 = fields.Many2one('sale.spec', string="Installation Method 3",
                                                domain="[('spec_type', '=', 'installation_method')]")
    table_base_id = fields.Many2one('sale.spec', string="Table Base", domain="[('spec_type', '=', 'table_base')]")
    panel_type_id = fields.Many2one('sale.spec', string="Panel Type", domain="[('spec_type', '=', 'panel_type')]")
    panel_color_id = fields.Many2one('sale.spec', string="Panel Color", domain="[('spec_type', '=', 'panel_color')]")
    food_disposer_id = fields.Many2one('sale.spec', string="Food Disposer",
                                       domain="[('spec_type', '=', 'food_disposer')]")
    water_filter_id = fields.Many2one('sale.spec', string="Water Filter", domain="[('spec_type', '=', 'water_filter')]")
    installation_id = fields.Many2one('sale.spec', string="Installation", domain="[('spec_type', '=', 'installation')]")
    hands_type_id = fields.Many2one('sale.spec', string="Hands 1", domain="[('spec_type', '=', 'hands_type')]")
    # supplier_id_hand1 = fields.Many2one('res.partner', string="Supplier 1")
    supplier_id_hand1_text = fields.Char(string="Supplier 1")
    count = fields.Integer(string="Count")
    chairs = fields.Many2one('sale.spec', string="Chairs", domain="[('spec_type', '=', 'chairs')]")
    wood_color3_id = fields.Char(string="Wood Color 3")
    wood_color4_id = fields.Char(string="Wood Color 4")
    sink2_id = fields.Many2one('sale.spec', string="Sink 2", domain="[('spec_type', '=', 'sink')]")
    mixer2_id = fields.Many2one('sale.spec', string="Mixer 2", domain="[('spec_type', '=', 'mixer')]")
    handle2_id = fields.Many2one('sale.spec', string="Handle 2", domain="[('spec_type', '=', 'hands_type2')]")
    # supplier_id_hand2 = fields.Many2one('res.partner', string="Supplier 2")
    supplier_id_hand2_text = fields.Char(string="Supplier 2")
    count2 = fields.Integer(string="Count 2")
    handle3_id = fields.Char(string="Handle 3")
    # supplier_id_hand3 = fields.Many2one('res.partner', string="Supplier 3")
    supplier_id_hand3_text = fields.Char(string="Supplier 3")
    count3 = fields.Integer(string="Count 3")
    handle4_id = fields.Many2one('sale.spec', string="Handle 4", domain="[('spec_type', '=', 'hands_type')]")
    # handle_installation = fields.Many2one('sale.spec', string="Handle Installation",
    #                                       domain="[('spec_type', '=', 'installation')]")
    handle_installation_text = fields.Char(string="Handle Installation")
    # handle_installation2 = fields.Many2one('sale.spec', string="Handle Installation 2",
    #                                         domain="[('spec_type', '=', 'installation')]")
    handle_installation2_text = fields.Char(string="Handle Installation 2")
    # handle_installation3 = fields.Many2one('sale.spec', string="Handle Installation 3",
    #                                         domain="[('spec_type', '=', 'installation')]")
    handle_installation3_text = fields.Char(string="Handle Installation 3")
    plan_location = fields.Char(string="Plan Location")
    date_order_day = fields.Char(compute='_compute_date_order_day')

    def _compute_date_order_day(self):
        for rec in self:
            if rec.date_order:
                weekday = rec.date_order.weekday()  # Monday = 0
                rec.date_order_day = ARABIC_WEEKDAYS.get(weekday, '')

    #Devices
    chopper = fields.Char(string="Chopper")
    oven = fields.Char(string="Oven")
    cooktop = fields.Char(string="Cooktop")
    stove = fields.Char(string="Stove")
    extractor_fan = fields.Char(string="Extractor Fan")
    microwave = fields.Char(string="Microwave")
    dishwasher = fields.Char(string="Dishwasher")
    washing_dryer_machine = fields.Char(string="Washing & Dryer Machine")
    refrigerator = fields.Char(string="Refrigerator")
    filter = fields.Char(string="Filter")
    freezer = fields.Char(string="Freezer")
    water_cooler = fields.Char(string="Water Cooler")
    heater = fields.Char(string="Heater")
    warming_drawer = fields.Char(string="Warming Drawer")
    coffee_maker = fields.Char(string="Coffee Maker")
    grill_fryer = fields.Char(string="Grill Fryer")
    note_device = fields.Char(string="Note")

    #accessories
    accessories = fields.Char(string="Accessories")
    accessories_count = fields.Integer(string="Accessories Count")
    accessories2 = fields.Char(string="Accessories 2")
    accessories_count2 = fields.Integer(string="Accessories Count 2")
    accessories3 = fields.Char(string="Accessories 3")
    accessories_count3 = fields.Integer(string="Accessories Count 3")
    accessories4 = fields.Char(string="Accessories 4")
    accessories_count4 = fields.Integer(string="Accessories Count 4")
    accessories5 = fields.Char(string="Accessories 5")
    accessories_count5 = fields.Integer(string="Accessories Count 5")
    accessories6 = fields.Char(string="Accessories 6")
    accessories_count6 = fields.Integer(string="Accessories Count 6")
    accessories_note = fields.Char(string="Accessories Note")

    #Lighting
    lighting1 = fields.Many2one('sale.spec', string="Lighting 1", domain="[('spec_type', '=', 'light_type')]")
    # lighting1_installation = fields.Many2one('sale.spec', string="Lighting Installation",
    #                                             domain="[('spec_type', '=', 'installation_method')]")
    lighting1_installation_text = fields.Char(string="Lighting Installation")
    lighting1_count = fields.Integer(string="Lighting Count")
    lighting2 = fields.Many2one('sale.spec', string="Lighting 2", domain="[('spec_type', '=', 'light_type')]")
    # lighting2_installation = fields.Many2one('sale.spec', string="Lighting Installation 2",
    #                                             domain="[('spec_type', '=', 'installation_method')]")
    lighting2_installation_text = fields.Char(string="Lighting Installation 2")
    lighting2_count = fields.Integer(string="Lighting Count 2")
    lighting3 = fields.Char(string="Lighting 3")
    lighting3_installation = fields.Char(string="Lighting Installation 3")
    lighting3_count = fields.Integer(string="Lighting Count 3")
    lighting_note = fields.Text(string="Lighting Note")

#     Bedroom Specifications

#panal
    side_panel_color = fields.Char(string="Side Panel Color")
    grain = fields.Char(string="Grain")


#Carcass
    carcass_color = fields.Char(string="Carcass Color")
    carcass_grain = fields.Char(string="Grain")
#Door Leaves & Hinges
    #  grounded door
    # ground_door_one_id = fields.Many2one('bedroom.spec', string="Ground Door", domain="[('bedroom_type', '=', 'ground_door')]")
    door_ground_model_one_id = fields.Many2one('bedroom.spec', string="Door Model", domain="[('bedroom_type', '=', 'door_model')]")
    wood_ground_one_frame_color_one = fields.Char(string="Wood One Frame Color")
    frame_color_one = fields.Char(string="Frame Color")
    glass_ground_one_model_one_id = fields.Many2one('bedroom.spec', string="Glass Model", domain="[('bedroom_type', '=', 'glass_model')]")
    # ground_door_two_id = fields.Many2one('bedroom.spec', string="Ground Door 2", domain="[('bedroom_type', '=', 'ground_door')]")
    door_ground_model_two_id = fields.Many2one('bedroom.spec', string="Door Model 2", domain="[('bedroom_type', '=', 'door_model')]")
    wood_ground_two_frame_color_one = fields.Char(string="Wood Two Frame Color")
    frame_color_two = fields.Char(string="Frame Color")
    glass_ground_two_model_one_id = fields.Many2one('bedroom.spec', string="Glass Model 2", domain="[('bedroom_type', '=', 'glass_model')]")
    #  floor2 door
    # floor2_door_one_id = fields.Many2one('bedroom.spec', string="Floor 2 Door", domain="[('bedroom_type', '=', 'floor2_door')]")
    door_floor2_model_one_id = fields.Many2one('bedroom.spec', string="Door Model", domain="[('bedroom_type', '=', 'door_model')]")
    wood_floor2_one_frame_color_one = fields.Char(string="Wood One Frame Color")
    frame_floor2_color_one = fields.Char(string="Frame Color")
    glass_floor2_one_model_one_id = fields.Many2one('bedroom.spec', string="Glass Model", domain="[('bedroom_type', '=', 'glass_model')]")
    # floor2_door_two_id = fields.Many2one('bedroom.spec', string="Floor 2 Door 2", domain="[('bedroom_type', '=', 'floor2_door')]")
    door_floor2_model_two_id = fields.Many2one('bedroom.spec', string="Door Model 2", domain="[('bedroom_type', '=', 'door_model')]")
    wood_floor2_two_frame_color_one = fields.Char(string="Wood Two Frame Color")
    frame_floor2_color_two = fields.Char(string="Frame Color 2")
    glass_floor2_two_model_one_id = fields.Many2one('bedroom.spec', string="Glass Model 2", domain="[('bedroom_type', '=', 'glass_model')]")
    # sliding door/1+3
    # piece one
    sliding_door_one_id = fields.Many2one('bedroom.spec', string="Sliding Door", domain="[('bedroom_type', '=', 'door_model_1_3')]")
    frame_color_one_sliding = fields.Many2one('bedroom.spec', string="Frame Color", domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_one = fields.Char(string="Piece Color")
    piece_height_one = fields.Char(string="Piece Height")
    # piece two
    sliding_door_two_id = fields.Many2one('bedroom.spec', string="Sliding Door 2", domain="[('bedroom_type', '=', 'door_model_1_3')]")
    frame_color_two_sliding = fields.Many2one('bedroom.spec', string="Frame Color 2", domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_two = fields.Char(string="Piece Color 2")
    piece_height_two = fields.Char(string="Piece Height 2")
    # piece three
    sliding_door_three_id = fields.Many2one('bedroom.spec', string="Sliding Door 3", domain="[('bedroom_type', '=', 'door_model_1_3')]")
    frame_color_three = fields.Many2one('bedroom.spec', string="Frame Color 3", domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_three = fields.Char(string="Piece Color 3")
    piece_height_three = fields.Char(string="Piece Height 3")
    # sliding door/2+4
    # piece one
    sliding_door_four_id = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'door_model_2_4')]")
    frame_color_four = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_four = fields.Char()
    piece_height_four = fields.Char()
    # piece two
    sliding_door_five_id = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'door_model_2_4')]")
    frame_color_five = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_five = fields.Char()
    piece_height_five = fields.Char()
    # piece three
    sliding_door_six_id = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'door_model_2_4')]")
    frame_color_six = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'sliding_frame_color')]")
    piece_color_six = fields.Char()
    piece_height_six = fields.Char()

# Bedside Tables
    bedside_table_model = fields.Char()
    beside_table_color = fields.Char()
    beside_table_count = fields.Char()
    beside_table_beech_wood_bases = fields.Char()
    beside_table_additional_note = fields.Char()
    beside_table_beech_wood_bases_color = fields.Char()
    beside_table_beech_wood_bases_model = fields.Many2one('bedroom.spec', string="Beside Table Model", domain="[('bedroom_type', '=', 'type_of_beech_wood_bases')]")
    beside_table_drawer_color = fields.Char()
    beside_table_wood_box = fields.Char()

#Vanity
    vanity_carcass_color = fields.Char()
    vanity_beech_wood_bases = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'type_of_beech_wood_bases')]")
    vanity_mirror = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'mirror')]")
    vanity_Leaves = fields.Char()
    vanity_top_color = fields.Char()
    vanity_mirror_type = fields.Char()

#Hands
    hand_one_type_id = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'hand_type')]")
    hand_one_code = fields.Char()
    hand_one_vendor = fields.Char()
    hand_one_count = fields.Char()
    hand_one_installation_place = fields.Char()
    hand_one_installation_type = fields.Char()
    #Hand Two
    hand_two_type = fields.Char()
    hand_two_code = fields.Char()
    hand_two_vendor = fields.Char()
    hand_two_count = fields.Char()
    hand_two_installation_place = fields.Char()
    hand_two_installation_type = fields.Char()

    #Hand Three
    hand_three_type = fields.Char()
    hand_three_code = fields.Char()
    hand_three_vendor = fields.Char()
    hand_three_count = fields.Char()
    hand_three_installation_place = fields.Char()
    hand_three_installation_type = fields.Char()

# Accessories
    accessories_one_type_id = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'accessories')]")
    accessories_one_count = fields.Char()
    accessories_two_type = fields.Char()
    accessories_two_count = fields.Char()
    accessories_three_type = fields.Char()
    accessories_three_count = fields.Char()
    accessories_four_type = fields.Char()
    accessories_four_count = fields.Char()
    accessories_five_type = fields.Char()
    accessories_five_count = fields.Char()
    accessories_six_type = fields.Char()
    accessories_six_count = fields.Char()

#Headboard-Bedbox
    headboard_type = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'headboard')]")
    headboard_count = fields.Char()
    bed_box_type = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'bed_box')]")
    bed_box_count = fields.Char()
    textile_color = fields.Char()

#bed dimensions
    # head
    bed_head_width = fields.Char()
    bed_head_height = fields.Char()
    bed_head_length = fields.Char()
    bed_head_type = fields.Char()
    bed_head_upholstery = fields.Image(max_width=128, max_height=128)

    #box
    bed_box_width = fields.Char()
    bed_box_height = fields.Char()
    bed_box_length = fields.Char()
    bed_box_one_type = fields.Char()
    bed_box_upholstery = fields.Image(max_width=128, max_height=128)

    #Mattress
    mattress_width = fields.Char()
    mattress_height = fields.Char()
    mattress_length = fields.Char()
    mattress_type = fields.Char()
    mattress_upholstery = fields.Image(max_width=128, max_height=128)

    #legs
    legs_width = fields.Char()
    legs_height = fields.Char()
    legs_length = fields.Char()
    legs_type = fields.Char()
    legs_upholstery = fields.Image(max_width=128, max_height=128)

    bed_additional_note = fields.Char()

    #lighting
    lighting_type = fields.Many2one('bedroom.spec', domain="[('bedroom_type', '=', 'lighting')]")
    lighting_installation_place = fields.Char(string="Lighting Installation Place")
    lighting_two_type = fields.Char()
    lighting_two_installation_place = fields.Char(string="Lighting Two Installation Place")
    additional_lighting_note = fields.Text(string="Additional Lighting Note")







class SaleSpec(models.Model):
    _name = 'sale.spec'
    _description = 'Sale Spec'

    name = fields.Char(string="English Name", required=True)
    name_ar = fields.Char(string="Arabic Name")
    spec_type = fields.Selection([
        ('kitchen_type', 'Kitchen Type'),
        ('door_model', 'Door Model'),
        ('solid_column', 'Solid Column'),
        ('laminate_grains', 'Laminate Grains'),
        ('wood_color', 'Wood Color'),
        ('sliding_wood', 'Sliding Wood'),
        ('glass_color', 'Glass Color'),
        ('panel_color', 'Panel Color'),
        ('worktop_color', 'Worktop Color'),
        ('cornice_type', 'Cornice Type'),
        ('light_pelmets', 'Light Pelmets'),
        ('light_type', 'Light Type'),
        ('glass_cabinets_type', 'Glass Cabinets Type'),
        ('bench_upholster', 'Bench & Upholster'),
        ('worktop_type', 'Worktop Type'),
        ('worktop_edge', 'Worktop Edge'),
        ('worktop_thickness', 'Worktop Thickness'),
        ('sink', 'Sink'),
        ('mixer', 'Mixer'),
        ('installation_method', 'Installation Method'),
        ('table_base', 'Table Base'),
        ('panel_type', 'Panel Type'),
        ('food_disposer', 'Food Disposer'),
        ('water_filter', 'Water Filter'),
        ('installation', 'Installation'),
        ('hands_type', 'Hands Type'),
        ('hands_type2', 'Hands Type2'),
        ('chairs', 'Chairs'),
    ], string="Type", required=True)

class BedRoomSpec(models.Model):
    _name = 'bedroom.spec'
    _description = 'Bedroom Spec'

    name = fields.Char(string="Name", required=True,translate=True)
    name_ar = fields.Char(string="Arabic Name", translate=True)
    bedroom_type = fields.Selection([
        ('door_model', 'Door Model'),
        ('door_model_1_3', 'Door Model 1+3'),
        ('door_model_2_4', 'Door Model 2+4'),
        ('frame_color', 'Frame Color'),
        ('glass_model', 'Glass Model'),
        ('ground_door', 'Ground Door'),
        ('floor2_door', 'Floor 2 Door'),
        ('sliding_frame_color', 'Sliding Frame Color'),
        ('type_of_beech_wood_bases', 'Type of Beech Wood Bases'),
        ('mirror', 'Mirror'),
        ('accessories', 'Accessories'),
        ('accessories_count', 'Accessories Count'),
        ('headboard', 'Headboard'),
        ('bed_box', 'Bed Box'),
        ('hand_type', 'Hand Type'),
        ('lighting', 'Lighting')], string="Bedroom Types", required=True)
