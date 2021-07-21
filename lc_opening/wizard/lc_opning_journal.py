# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,fields,api, _
from odoo.exceptions import UserError


class LcOpeningWizard(models.TransientModel):
    _name = 'lc.opening.wizard'
    _description = 'LC Opening Wizard'

    journal_id = fields.Many2one('account.journal', string='Journal', required=True)
    journal_date = fields.Date(string="Date", default=fields.Date.today(), required=True)

    def _prepare_move_line(self, opening_id):
        move_line_dict = []
        company_id = self.env.user.company_id
        if not company_id.lc_charges_account and not company_id.lc_agent_charges_account:
            raise UserError(_("Cannot create journal entry pls configure account in company"))
        move_line_dict.append({
            'account_id' : company_id.lc_charges_account.id or False,
            'partner_id' : opening_id.order_id.partner_id.id or False,
            'name' : opening_id.name + 'Total Charges',
            'currency_id' : opening_id.currency_id.id,
            'debit' : sum(opening_id.lc_charges_lines.mapped('total_charges_price')),
            'date_maturity' : self.journal_date,
            'ref' :  opening_id.name + 'Total Charges',
            'date' : self.journal_date,
        })
        move_line_dict.append({
            'account_id' : opening_id.order_id.partner_id and opening_id.order_id.partner_id.property_account_payable_id.id or False,
            'partner_id' : opening_id.order_id.partner_id.id or False,
            'name' : opening_id.name,
            'currency_id' : opening_id.currency_id.id,
            'credit' : sum(opening_id.lc_charges_lines.mapped('total_charges_price')),
            'date_maturity' : self.journal_date,
            'ref' : opening_id.name,
            'date' : self.journal_date,
        })
        for aggent in opening_id.cf_aggent_ids:
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

    def create_account(self):
        opening_id = self.env['lc.opening'].browse(self.env.context['active_id'])
        move_line_dict = self._prepare_move_line(opening_id)
        if not opening_id.lc_charges_lines and not opening_id.cf_aggent_ids:
            raise UserError(_("Plese enter lc charges and lc aggent charges"))
        vals = {
            'move_type' : 'entry',
            'currency_id' : opening_id.currency_id.id or False,
            'date' : self.journal_date,
            'journal_id' : self.journal_id.id or False,
            'opening_id' : opening_id.id,
            'line_ids': [(0, 0, line_data) for line_data in move_line_dict]            
        }
        move_id = self.env['account.move'].create(vals)
        return True