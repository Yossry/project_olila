
from odoo import api, fields, models,_

class PostApprovalExplosive(models.Model):
	_name = "post.approval.explosive"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Post Insurance Details"

	name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New') 
	pre_approval_date = fields.Date(string="Approval Date", copy=False)
	purchase_order_no = fields.Many2one('purchase.order', string='Purchase No', copy=False)
	purchase_order_date = fields.Datetime(string='Purchase order Date', copy=False)
	institute_name = fields.Char(string="Institute Name", copy=False)
	lc_no = fields.Char(string="LC No")
	zip = fields.Char(change_default=True)
	street = fields.Char()
	street2 = fields.Char()
	city = fields.Char()
	state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('approve','Approve'),('done','Done'),('amendment', 'Amendment'),('cancel','Cancel')], 
		string='Status', readonly=True, index=True, 
		copy=False, default='draft', tracking=True)
	country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
	remark = fields.Text(string="Remark", copy=False)
	explosive_lines = fields.One2many("approval.explosive.line", 'approval_explosive_id', string="Lines")
	commercial_invoice = fields.Char(string="Commercial Invoice")
	packing_list = fields.Char(string="Packing List")
	bill_of_lading  =  fields.Char(string="Bill Of Lading")
	certificate_of_origin = fields.Char(string="Certificate Of Origin")   
	arrival_date = fields.Char(string="Arrival Date")
	lc_requisition_id = fields.Many2one("lc.opening.fund.requisition")
	post_approval_id = fields.Many2one("approval.explosive")
	pi_no = fields.Char(string="PI Number", copy=False)
	pi_date = fields.Date(string="PI Date", copy=False)

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('post.approval.explosive') or '/'
		return super(PostApprovalExplosive, self).create(vals)


	@api.onchange('state_id')
	def onchange_state_id(self):
		for record in self:
			if record.state_id:
				record.country_id = record.state_id.country_id or False
			else:
				record.country_id = False

	def button_confirm(self):
		self.write({'state' : 'confirm'})

	def button_approve(self):
		self.write({'state' : 'approve'})

	# def button_re_approval(self):
	#     self.write({'state' : 're_approval'})

	def button_cancel(self):
		self.write({'state' : 'cancel'})

	def button_done(self):
		self.write({'state' : 'done'})
	

class PostApprovalExplosiveLine(models.Model):
	_name="post.approval.explosive.line"
	_description="post approval explosive line"

	approval_explosive_id = fields.Many2one("post.approval.explosive", string='Approval Explosive')
	product_id = fields.Many2one('product.product', 'Item', required=True)
	item_code = fields.Char(string='Item Code')
	importable_quantity = fields.Float(string='Importable Qty')
	stock_before_approval = fields.Float(string='Stock Before Approval')
	applic_quantity = fields.Float(string='Qty')
	stock_after_import =fields.Float(string='Stock After Import')
	arrival_days_required = fields.Integer(string='Arrival Days Required')
	factory_stock_report_date = fields.Date(string='Report Date')
	import_quantity = fields.Float(string='Import Qty')  
	application_no = fields.Char(string='Application No')
	application_date = fields.Date(string='Application Date')
	speed_money_am = fields.Float(string='Amount')

class PreApprovalExplosive(models.Model):
	_name = "approval.explosive"
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_description = "Insurance Details"

	name = fields.Char('Name', required=True, index=True, readonly=True, copy=False, default='New') 
	pre_approval_date = fields.Date(string="Approval Date", copy=False)
	purchase_order_no = fields.Many2one('purchase.order', string='Purchase No', copy=False)
	purchase_order_date = fields.Datetime(string='Purchase Date', copy=False)
	institute_name = fields.Char(string="Institute Name", copy=False)
	lc_no = fields.Char(string="LC No")
	zip = fields.Char(change_default=True)
	street = fields.Char()
	street2 = fields.Char()
	city = fields.Char()
	state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
	state = fields.Selection([('draft','Draft'), ('confirm','Confirm'), ('approve','Approve'), ('re_approval','Re Approval'), ('amendment', 'Amendment'),('done','Done'), ('cancel','Cancel')], 
		string='Status', readonly=True, index=True, 
		copy=False, default='draft', tracking=True)
	country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
	lc_requisition_id = fields.Many2one("lc.opening.fund.requisition")
	pi_no = fields.Char(string="PI Number", copy=False)
	pi_date = fields.Date(string="PI Date", copy=False)
	remark = fields.Text(string="Remark", copy=False)
	re_approval_count = fields.Integer(compute='_re_approve_count', string='Re-Approval')
	explosive_lines = fields.One2many("approval.explosive.line", 'approval_explosive_id', string="Lines")

	def _re_approve_count(self):
		for rec in self:
			approval_ids = self.env['post.approval.explosive'].search([('post_approval_id', '=', rec.id)])
			rec.re_approval_count = len(approval_ids.ids)

	@api.model
	def create(self, vals):
		if vals.get('name', 'New') == 'New':
			vals['name'] = self.env['ir.sequence'].next_by_code('approval.explosive') or '/'
		return super(PreApprovalExplosive, self).create(vals)

	@api.onchange('state_id')
	def onchange_state_id(self):
		for record in self:
			if record.state_id:
				record.country_id = record.state_id.country_id or False
			else:
				record.country_id = False

	def button_confirm(self):
		self.write({'state' : 'confirm'})

	def button_approve(self):
		self.write({'state' : 'approve'})

	def view_post_approval(self):
		approval_ids = self.env['post.approval.explosive'].search([('post_approval_id', 'in', self.ids)])
		return {
			'name': _('Re-Approvals'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'post.approval.explosive',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', approval_ids.ids)],
		}

	def _prepare_apporval_lines(self, line):
		return{
			'product_id' : line.product_id.id or False,
			'item_code' : line.item_code,
			'importable_quantity' : line.importable_quantity,
			'stock_before_approval': line.stock_before_approval,
			'applic_quantity': line.applic_quantity,
			'stock_after_import': line.stock_after_import,
			'arrival_days_required': line.arrival_days_required,
			'factory_stock_report_date': line.factory_stock_report_date,
			'import_quantity': line.import_quantity,
			'application_date': line.application_date,
			'speed_money_am': line.speed_money_am,
		}

	def _prepare_post_apporval_data(self):
		lines = [(0, 0, self._prepare_apporval_lines(line)) for line in self.explosive_lines]
		return {
			'institute_name' : self.institute_name or False,
			'post_approval_id' : self.id,
			'street': self.street,
			'street2': self.street2,
			'city': self.city,
			'state_id': self.state_id and self.state_id.id,
			'zip': self.zip,
			'country_id': self.country_id and self.country_id.id,
			'pre_approval_date': self.pre_approval_date,
			'purchase_order_no': self.purchase_order_no and self.purchase_order_no.id,
			'purchase_order_date': self.purchase_order_date,
			'lc_requisition_id': self.lc_requisition_id and self.lc_requisition_id.id,
			'pi_no': self.purchase_order_no.partner_ref,
			'pi_date': self.purchase_order_no.pi_date,
			'explosive_lines' : lines or False

		}

	def button_re_approval(self):
		data = self._prepare_post_apporval_data()
		self.env['post.approval.explosive'].create(data)
		self.write({'state' : 're_approval'})

	def button_cancel(self):
		self.write({'state' : 'cancel'})

	def button_done(self):
		self.write({'state' : 'done'})
	

class PreApprovalExplosiveLine(models.Model):
	_name="approval.explosive.line"
	_description="approval.explosive.line"

	approval_explosive_id = fields.Many2one("approval.explosive", string='Approval Explosive')
	product_id = fields.Many2one('product.product', 'Item', required=True)
	item_code = fields.Char(string='Item Code')
	importable_quantity = fields.Float(string='Importable Qty')
	stock_before_approval = fields.Float(string='Stock Before Approval')
	applic_quantity = fields.Float(string='Qty')
	stock_after_import =fields.Float(string='Stock After Import')
	arrival_days_required = fields.Integer(string='Arrival Days Required')
	factory_stock_report_date = fields.Date(string='Report Date')
	import_quantity = fields.Float(string='Import Qty')  
	application_no = fields.Char(string='Application No')
	application_date = fields.Date(string='Application Date')
	speed_money_am = fields.Float(string='Amount')