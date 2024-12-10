{
    'name': 'Quản lý tài sản doanh nghiệp 1',
    'version': '1.0',
    'category': 'Operations/Asset Management',
    'summary': 'Quản lý tài sản và yêu cầu bảo trì',
    'description': 'Module để quản lý tài sản doanh nghiệp và yêu cầu bảo trì.',
    'author': 'Bao',
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/asset_management_views.xml',
        'views/maintenance_request_views.xml',
        'views/asset_dashboard_views.xml',
    ],
    'installable': True,
    'application': True,
}
