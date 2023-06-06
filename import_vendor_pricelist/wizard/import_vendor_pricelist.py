# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import tempfile
import binascii
from odoo import api, fields, models, tools, _
from odoo.exceptions import Warning, UserError, ValidationError
import datetime

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class ImportVendorPircelistWizard(models.TransientModel):
    _name = 'import.vendor.pricelist'
    _description = 'import vendor pricelist'

    file = fields.Binary(string="Upload File",required=True)
    file_name = fields.Char(string="File Name")

    def import_file(self):
        product_obj = self.env['product.product']
        supplier_info_obj = self.env['product.supplierinfo']

        header = ['Vendor Name','Internal Reference','Vendor Product Name','Currency',
                  'Vendor Price','Public Price','Vendor Product Code','Delivery Lead Time',
                  'Quantity','Discount','Validity from','Validity to']

        if not self.file:
            raise ValidationError(_("Please Upload File to Import sale price!"))

        if self.file and not self.file_name.endswith('.xlsx'):
            raise Warning("Unsupported file format, Import only supports xlsx")
        try:
            file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            file.write(binascii.a2b_base64(self.file))
            file.seek(0)
            workbook = xlrd.open_workbook(file.name)
            sheet = workbook.sheet_by_index(0)
        except Exception:
            raise ValidationError(_("Please Select Valid File Format !"))

        for row_no in range(sheet.nrows):
            if row_no == 0:
                file_header = sheet.row_values(0)
                if file_header != header:
                    raise Warning(_("File Header is not Proper"))
            else:
                line=sheet.row_values(row_no)
                product = product_obj.search([('default_code','=',line[1])])
                if product:
                    start_date = False
                    end_date = False
                    product.write({'lst_price':line[5]})
                    partner = self.env['res.partner'].search([('name','=',line[0].strip())])
                    currency_id = self.env['res.currency'].search([('name','=',line[3].strip())])
                    if line[10]:
                        start_date = datetime.date(1899, 12, 30) + datetime.timedelta(days=line[10])
                    if line[11]:
                        end_date = datetime.date(1899, 12, 30) + datetime.timedelta(days=line[11])
                    # if start_date and end_date:
                    #     vendor_pricelist =supplier_info_obj.search(
                    #         [('name','=',partner.id),('product_id','=',product.id),
                    #          ('currency_id','=',currency_id.id),('date_start','=',start_date),
                    #          ('date_end','=',end_date)])
                    # else:
                    #     vendor_pricelist = supplier_info_obj.search(
                    #         [('name', '=', partner.id), ('product_id', '=', product.id),
                    #          ('currency_id', '=', currency_id.id)])

                    vendor_pricelist = supplier_info_obj.search(
                            [('name', '=', partner.id), ('product_id', '=', product.id)])
                    if partner and not vendor_pricelist:
                        vals={
                            'name':partner.id,
                            'product_name':line[2].strip() or False,
                            'product_code':line[6].strip() or False,
                            'delay':line[7] or False,
                            'min_qty':line[8] or 0.0,
                            'price':line[4] or 0.0,
                            'currency_id':currency_id.id if currency_id else False,
                            'product_id':product.id,
                            'product_tmpl_id':product.product_tmpl_id.id,
                            'discount':float(line[9]),
                            'date_start':start_date if start_date else False,
                            'date_end': end_date if end_date else False,
                        }
                        try:
                            vendor_pricelist_id=supplier_info_obj.create(vals)
                            _logger.info("\nVendor pricelist id: {0}".format(vendor_pricelist_id.id))
                        except Exception as e:
                            _logger.info("\nError: While Create Vendor Pricelist Line No:{0}".format(row_no+1))
                    if vendor_pricelist:
                        vendor_pricelist.write({
                            'price':line[4] or 0.0,
                            'discount':float(line[9]),
                            'currency_id': currency_id.id if currency_id else False,
                            # 'date_start': start_date if start_date else False,
                            # 'date_end': end_date if end_date else False,
                        })
        self.file = False
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
