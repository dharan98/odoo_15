# -*- coding: utf-8 -*-
{
    'name' : 'Import Vendor Pricelist',
    'version' : '1.0',
    'summary': 'import the vendor pricelist',
    'description': """it used to import the vendor pricelist""",
    'author' : "Dhara Nakum",
    'category': 'inventory',
    'website': '',
    'depends' : ['stock'],
    'data': [
        'security/ir.model.access.csv',
         'wizard/import_vendor_pricelist.xml'
            ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
