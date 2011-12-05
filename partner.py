# -*- encoding: utf-8 -*-
import netsvc
import pooler, tools
import math

from tools.translate import _

from osv import fields, osv

class partner(osv.osv):

    _inherit = 'res.partner'
    
    _columns = {                            
                'cod_esenzione_iva':fields.many2one('account.tax', 'Codice Iva Esenzione', required=False, readonly=False),
                'dati_es_iva':fields.char('Dati di Esenzione iva', size=100),
                'scad_esenzione_iva': fields.date('Data Scadenza Esenzione Iva', required=False, readonly=False),
                }
partner()
