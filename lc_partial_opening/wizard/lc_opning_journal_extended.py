# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo.exceptions import UserError

class LcOpeningWizard(models.TransientModel):
    _inherit = 'lc.opening.wizard'

    def _prepare_move_line(self, opening_id):
        move_line_dict = []
        amount = 0.0
        company_id = self.env.user.company_id
        if not company_id.lc_charges_account and not company_id.lc_agent_charges_account:
            raise UserError(_("Cannot create journal entry pls configure account in company"))
        lc_charge_ids = opening_id.lc_charges_lines.filtered(lambda x: not x.is_processed)
        amount = sum(lc_charge_ids.mapped('total_charges_price'))
        move_line_dict.append({
            'account_id' : company_id.lc_charges_account.id or False,
            'partner_id' : opening_id.order_id.partner_id.id or False,
            'name' : opening_id.name + 'Total Charges',
            'currency_id' : opening_id.currency_id.id,
            'debit' : amount,
            'date_maturity' : self.journal_date,
            'ref' :  opening_id.name + 'Total Charges',
            'date' : self.journal_date,
        })
        move_line_dict.append({
            'account_id' : opening_id.order_id.partner_id and opening_id.order_id.partner_id.property_account_payable_id.id or False,
            'partner_id' : opening_id.order_id.partner_id.id or False,
            'name' : opening_id.name,
            'currency_id' : opening_id.currency_id.id,
            'credit' : amount,
            'date_maturity' : self.journal_date,
            'ref' : opening_id.name,
            'date' : self.journal_date,
        })
        lc_charge_ids.write({'is_processed' : True})
        for aggent in opening_id.cf_aggent_ids.filtered(lambda x: not x.is_processed):
            aggent.is_processed = True
            for line in aggent.agents_charge_ids:
                move_line_dict.append({
                    'account_id' : line.user_id and line.user_id.property_account_payable_id.id or False,
                    'partner_id' : line.user_id.id or False,
                    'name' : aggent.name,
                    'currency_id' : aggent.currency_id.id,
                    'credit' : line.sub_total,
                    'date_maturity' : self.journal_date,
                    'ref' : aggent.name,
                    'date' : self.journal_date,
                })
                move_line_dict.append({
                    'account_id' : company_id.lc_agent_charges_account.id or False,
                    'partner_id' : line.user_id.id or False,
                    'name' : aggent.name,
                    'currency_id' : aggent.currency_id.id,
                    'debit' : line.sub_total,
                    'date_maturity' : self.journal_date,
                    'ref' : aggent.name,
                    'date' : self.journal_date,
                })
        return move_line_dict