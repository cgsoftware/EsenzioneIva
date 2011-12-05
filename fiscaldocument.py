#-*- encoding: utf-8 -*-
import netsvc
import pooler, tools
import math
import decimal_precision as dp
from tools.translate import _

from osv import fields, osv

class FiscalDocHeader(osv.osv):
    _inherit = 'fiscaldoc.header'

    _columns={
                'cod_esenzione_iva':fields.many2one('account.tax', 'Codice Iva Esenzione', required=False, readonly=False),
                'scad_esenzione_iva': fields.date('Data Scadenza Esenzione Iva', required=False, readonly=False),
              }
    
    def onchange_partner_id(self, cr, uid, ids, part,context):
        res = super(FiscalDocHeader,self).onchange_partner_id(cr, uid, ids, part,context)
        val = res.get('value', False)
        #import pdb;pdb.set_trace()
        if part: 
             part = self.pool.get('res.partner').browse(cr, uid, part)
             if part.cod_esenzione_iva: #esiste un codice di esenzione conai
                 val['cod_esenzione_iva']= part.cod_esenzione_iva.id
                 val['scad_esenzione_iva']=part.scad_esenzione_iva
        
        return {'value': val}               
    
FiscalDocHeader()


class FiscalDocRighe(osv.osv):
    _inherit = 'fiscaldoc.righe'
    
    def onchange_articolo(self, cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom):
                res = super(FiscalDocRighe, self).onchange_articolo(cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom)
                v = res.get('value', False)
                if product_id:
                    partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
                    if partner.cod_esenzione_iva and partner.scad_esenzione_iva >= data_doc: 
                        v['codice_iva']=partner.cod_esenzione_iva.id
                return {'value':v}    
    
FiscalDocRighe()
