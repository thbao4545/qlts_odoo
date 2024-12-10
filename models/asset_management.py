from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Asset(models.Model):
    _name = 'qlts.asset'
    _description = 'Quản lý tài sản doanh nghiệp'

    name = fields.Char('Tên tài sản', required=True)
    code = fields.Char('Mã tài sản', required=True)
    cate_id = fields.Selection([
        ('office_supplies', 'Văn phòng phẩm'),
        ('computer', 'Máy tính'),
        ('real_estate', 'Bất động sản'),
        ('vehicle', 'Xe cộ'),
        ('other', 'Khác')
    ], string='Nhóm sản phẩm', required=True)
    purchase_date = fields.Date('Ngày mua')
    value = fields.Float('Giá trị', required=True)
    depreciation = fields.Float('Khấu hao', readonly=True)
    state = fields.Selection([
        ('new', 'Mới'),
        ('in_use', 'Đang sử dụng'),
        ('under_maintenance', 'Đang bảo trì'),
        ('retired', 'Đã thanh lý'),
    ], default='new', string='Trạng thái')

    maintenance_ids = fields.One2many('request.maintance', 'asset_id', string='Yêu cầu bảo trì')

    buyer_id = fields.Many2one('hr.employee', string='Người mua',required=False, ondelete='set null')
    holder_id = fields.Many2one('hr.employee', string='Người nắm giữ', required=False, ondelete='set null')

    image = fields.Image('Hình ảnh')

    # Thống kê
    count = fields.Integer('Tổng số tài sản', compute='_compute_dashboard_data', store=False)
    highest_value = fields.Many2one('qlts.asset', string='Tài sản giá trị nhất', compute='_compute_dashboard_data', store=False)
    lowest_value = fields.Many2one('qlts.asset', string='Tài sản giá trị thấp nhất', compute='_compute_dashboard_data', store=False)

    @api.depends('value')
    def _compute_dashboard_data(self):
        """Tính toán số lượng, tài sản giá trị cao nhất và thấp nhất."""
        all_assets = self.search([])  # Lấy tất cả tài sản
        if all_assets:
            max_asset = max(all_assets, key=lambda x: x.value)
            min_asset = min(all_assets, key=lambda x: x.value)
        else:
            max_asset = min_asset = self.env['qlts.asset']

        for record in self:
            record.count = len(all_assets)
            record.highest_value = max_asset.id
            record.lowest_value = min_asset.id

    @api.onchange('purchase_date')
    def _onchange_purchase_date(self):
        """Tự động tính khấu hao khi thay đổi ngày mua."""
        if self.purchase_date:
            self.depreciation = self.calculate_depreciation()

    def calculate_depreciation(self):
        """Tính khấu hao dựa trên thời gian sử dụng."""
        if self.purchase_date:
            years_used = (fields.Date.today() - self.purchase_date).days / 365
            return max(0.0, self.value * 0.1 * years_used)  # Đảm bảo không âm
        return 0.0

    @api.constrains('value')
    def _check_positive_value(self):
        """Đảm bảo giá trị tài sản không âm."""
        for record in self:
            if record.value < 0:
                raise ValidationError(_('Giá trị tài sản không được âm.'))


class MaintenanceRequest(models.Model):
    _name = 'request.maintance'
    _description = 'Yêu cầu bảo trì'

    name = fields.Char('Tên yêu cầu', required=True)
    asset_id = fields.Many2one('qlts.asset', string='Tài sản', required=True, ondelete='cascade')
    description = fields.Text('Mô tả')
    state = fields.Selection([
        ('new', 'Mới'),
        ('in_progress', 'Đang xử lý'),
        ('done', 'Đã hoàn thành'),
    ], default='new', string='Trạng thái')
    maintenance_date = fields.Date('Ngày bảo trì')

    @api.constrains('maintenance_date')
    def _check_maintenance_date(self):
        """Đảm bảo ngày bảo trì không nhỏ hơn ngày hiện tại."""
        for record in self:
            if record.maintenance_date and record.maintenance_date < fields.Date.today():
                raise ValidationError(_('Ngày bảo trì không được nhỏ hơn ngày hiện tại.'))
            
    def action_set_in_progress(self):
        for record in self:
            if record.state == 'new':
                record.state = 'in_progress'

    def action_set_done(self):
        for record in self:
            if record.state == 'in_progress':
                record.state = 'done'

