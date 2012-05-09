 #-*- encoding: utf-8 -*-
import netsvc
import pooler, tools
import math
import decimal_precision as dp
from tools.translate import _

from osv import fields, osv


class sale_order(osv.osv):
    _inherit = 'sale.order'
    _columns={
                'cod_esenzione_iva':fields.many2one('account.tax', 'Codice Iva Esenzione', required=False, readonly=False),
                'scad_esenzione_iva': fields.date('Data Scadenza Esenzione Iva', required=False, readonly=False),
              }
    
    def onchange_partner_id(self, cr, uid, ids, part):
        res = super(sale_order,self).onchange_partner_id(cr, uid, ids, part)
        val = res.get('value', False)
        warning = res.get('warning', False)
        #import pdb;pdb.set_trace()
        if part: 
             part = self.pool.get('res.partner').browse(cr, uid, part)
             if part.cod_esenzione_iva: #esiste un codice di esenzione conai
                 val['cod_esenzione_iva']= part.cod_esenzione_iva.id
                 val['scad_esenzione_iva']=part.scad_esenzione_iva
        
        return {'value': val,'warning':warning}               
    
    
    
sale_order()



class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        
        res = super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax, date_order, fiscal_position=fiscal_position, flag=flag)
        
        result = res.get('value', False)
        domain = res.get('domain', False)
        warning = res.get('warning', False)
        #import pdb;pdb.set_trace()
        if ids:
          for line in self.browse(cr,uid,ids):
            if line.order_id.cod_esenzione_iva and line.order_id.scad_esenzione_iva>=line.order_id.date_order:
                result['tax_id']=[line.order_id.cod_esenzione_iva.id]
        else:
            partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
            if partner.cod_esenzione_iva: 
                result['tax_id']=[partner.cod_esenzione_iva.id]
               
         # result['totale_conai'] = prz_conai * art_obj.peso * result['product_uos_qty']
          #import pdb;pdb.set_trace()
        return {'value': result, 'domain': domain, 'warning': warning}
       
    
    
    
    
sale_order_line()
