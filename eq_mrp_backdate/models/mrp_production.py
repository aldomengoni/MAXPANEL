# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright 2019 EquickERP
#
##############################################################################

from odoo import models, fields, api

 
class Stock_Move(models.Model):
    _inherit = 'stock.move'

    def _action_done(self, cancel_backorder=False):
        res = super(Stock_Move, self)._action_done(cancel_backorder)
        move_fields = self.env['stock.move']._fields.keys()
        for each_move in res:
            production_id = False
            if each_move.production_id:
                production_id = each_move.production_id
            if each_move.raw_material_production_id:
                production_id = each_move.raw_material_production_id
            if production_id and production_id.backdated:
                backdated = production_id.backdated or fields.Datetime.now()
                note = production_id.remark or production_id.name
                each_move.write({'date': backdated, 'date_deadline': backdated, 'origin': note})
                each_move.move_line_ids.write({'date':backdated, 'origin':note})
                if 'stock_valuation_layer_ids' in move_fields:
                    for valuation_layer in each_move.stock_valuation_layer_ids:
                        self.env.cr.execute("update stock_valuation_layer set create_date = %s where id = %s", (backdated, valuation_layer.id))
        return res

    def _prepare_account_move_vals(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        res = super(Stock_Move, self)._prepare_account_move_vals(credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost)
        production_id = False
        move_fields = self.env['stock.move']._fields.keys()
        if self.production_id:
            production_id = self.production_id
        if self.raw_material_production_id:
            production_id = self.raw_material_production_id
        if production_id and production_id.backdated:
            backdated = production_id.backdated or fields.Datetime.now()
            res.update({'date': backdated.date()})
        return res


class mrp_production(models.Model):
    _inherit = 'mrp.production'

    backdated = fields.Datetime(string="Backdate", copy=False)
    remark = fields.Char(string="Remark", copy=False)

    def _post_inventory(self, cancel_backorder=False):
        dt = fields.Datetime.now()
        for prod in self:
            if prod.backdated:
                dt = prod.backdated
        res = super(mrp_production, self.with_context(force_period_date=dt))._post_inventory(cancel_backorder)
        for order in self:
            if order.backdated:
                order.date_planned_finished = order.backdated
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: