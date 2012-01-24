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
        warning = res.get('warning', False)
        #import pdb;pdb.set_trace()
        if part: 
             part = self.pool.get('res.partner').browse(cr, uid, part)
             if part.cod_esenzione_iva: #esiste un codice di esenzione conai
                 val['cod_esenzione_iva']= part.cod_esenzione_iva.id
                 val['scad_esenzione_iva']=part.scad_esenzione_iva
        
        return {'value': val, 'warning': warning}            
    
FiscalDocHeader()


class FiscalDocRighe(osv.osv):
    _inherit = 'fiscaldoc.righe'
    
    def onchange_articolo(self, cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom):
                res = super(FiscalDocRighe, self).onchange_articolo(cr, uid, ids, product_id, listino_id, qty, partner_id, data_doc, uom)
                v = res.get('value', False)
                if product_id:
                    partner = self.pool.get('res.partner').browse(cr,uid,partner_id)
                    #import pdb;pdb.set_trace()
                    if partner.cod_esenzione_iva and partner.scad_esenzione_iva >= data_doc: 
                        v['codice_iva']=partner.cod_esenzione_iva.id
                return {'value':v}    
            
    
FiscalDocRighe()



class FiscalDocIva(osv.osv):
    _inherit = 'fiscaldoc.iva'
    
    
    def agg_righe_iva(self, cr, uid, ids, context):
        
        def get_perc_iva(self, cr, uid, ids, idiva, context):
            dati = self.pool.get('account.tax').read(cr, uid, [idiva], (['amount', 'type']), context=context)
            return dati[0]['amount']
        #import pdb;pdb.set_trace()
        # PRIMA SCORRE TUTTE LE RIGHE DI ARTICOLI
        lines = self.pool.get('fiscaldoc.righe').search(cr, uid, [('name', '=', ids)])      
        righe_iva = {}
        for riga in self.pool.get('fiscaldoc.righe').browse(cr, uid, lines, context=context):
          if riga.codice_iva.id:
            if righe_iva.get(riga.codice_iva.id, False):
                # esiste gia la riga con questo codice
                dati_iva = righe_iva[riga.codice_iva.id]
                dati_iva['imponibile'] = dati_iva['imponibile'] + riga.totale_riga
                righe_iva[riga.codice_iva.id] = dati_iva
            else:
                dati_iva = {'imponibile':riga.totale_riga}
                righe_iva.update({riga.codice_iva.id:dati_iva}) 
        # QUI DEVE CALCOLARE LE POSIZIONI IVA DI TUTTE LE SPESE ACCESSORIE
           
        id = ids[0]
        testata = self.pool.get('fiscaldoc.header').browse(cr, uid, id)
        company_id = self.pool.get('res.users').browse(cr, uid, uid, context).company_id.id
        codici_iva_accessori = self.pool.get('res.company').read(cr, uid, company_id , (['civa_spe_inc', 'civa_spe_imb', 'civa_spe_tra', 'civa_fc']), context=context)
        if testata.spese_incasso:
         if testata.cod_esenzione_iva:
             if righe_iva.get(testata.cod_esenzione_iva.id, False):
                dati_iva = righe_iva[testata.cod_esenzione_iva.id]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_incasso
                righe_iva[testata.cod_esenzione_iva.id] = dati_iva

             else:
                dati_iva = {'imponibile':testata.spese_incasso}
                righe_iva.update({testata.cod_esenzione_iva.id:dati_iva}) 
                 
             
         else:
          if codici_iva_accessori['civa_spe_inc'][0]:
            #import pdb;pdb.set_trace()  
            if righe_iva.get(codici_iva_accessori['civa_spe_inc'][0], False):
                # esiste gia la riga con questo codice
                dati_iva = righe_iva[codici_iva_accessori['civa_spe_inc'][0]]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_incasso
                righe_iva[codici_iva_accessori['civa_spe_inc'][0]] = dati_iva
            else:
                dati_iva = {'imponibile':testata.spese_incasso}
                righe_iva.update({codici_iva_accessori['civa_spe_inc'][0]:dati_iva}) 

        if testata.spese_imballo:
         if testata.cod_esenzione_iva:
             if righe_iva.get(testata.cod_esenzione_iva.id, False):
                dati_iva = righe_iva[testata.cod_esenzione_iva.id]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_imballo
                righe_iva[testata.cod_esenzione_iva.id] = dati_iva

             else:
                dati_iva = {'imponibile':testata.spese_imballo}
                righe_iva.update({testata.cod_esenzione_iva.id:dati_iva}) 
                 
             
         else:
            
          if codici_iva_accessori['civa_spe_imb'][0]:
            if righe_iva.get(codici_iva_accessori['civa_spe_imb'][0], False):
                # esiste gia la riga con questo codice
                dati_iva = righe_iva[codici_iva_accessori['civa_spe_imb'][0]]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_imballo
                righe_iva[codici_iva_accessori['civa_spe_imb'][0]] = dati_iva
            else:
                dati_iva = {'imponibile':testata.spese_imballo}
                righe_iva.update({codici_iva_accessori['civa_spe_imb'][0]:dati_iva})                 

        if testata.spese_trasporto:
         if testata.cod_esenzione_iva:
             if righe_iva.get(testata.cod_esenzione_iva.id, False):
                dati_iva = righe_iva[testata.cod_esenzione_iva.id]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_trasporto
                righe_iva[testata.cod_esenzione_iva.id] = dati_iva

             else:
                dati_iva = {'imponibile':testata.spese_trasporto}
                righe_iva.update({testata.cod_esenzione_iva.id:dati_iva}) 
                 
             
         else:
            
            
          if codici_iva_accessori['civa_spe_tra'][0]:
            if righe_iva.get(codici_iva_accessori['civa_spe_tra'][0], False):
                # esiste gia la riga con questo codice
                dati_iva = righe_iva[codici_iva_accessori['civa_spe_tra'][0]]
                dati_iva['imponibile'] = dati_iva['imponibile'] + testata.spese_trasporto
                righe_iva[codici_iva_accessori['civa_spe_tra'][0]] = dati_iva
            else:
                dati_iva = {'imponibile':testata.spese_trasporto}
                righe_iva.update({codici_iva_accessori['civa_spe_tra'][0]:dati_iva})                    
        
        # HA FINITO DI CALCOLARE GLI IMPONIBILI ORA CALCOLA L'IMPOSTA RIGA PER RIGA
        for rg_iva in righe_iva:
            perc_iva = get_perc_iva(self, cr, uid, ids, rg_iva, context)
            dati_iva = righe_iva[rg_iva]
            #Andre@
            #AGGIUNTO PER LA GESTIONE DEL FLAG OMAGGI
            
            if dati_iva['imponibile'] < 0:
                dati_iva.update({'imposta':dati_iva['imponibile'] * perc_iva * -1})
                righe_iva[rg_iva] = dati_iva 
            else:
                dati_iva.update({'imposta':dati_iva['imponibile'] * perc_iva})
                righe_iva[rg_iva] = dati_iva   
           
        # ORA SCRIVE I RECORD CANCELLA COMUNQUE TUTTE LE REGHE E POI LE RICREA AGGIORNATE QUESTO SALVA LA CONDIZIONE IN CUI SCOMPAIA COMPLETAMENTE 
        # UNA RIGA DI ALIQUOTA IVA
        lines = self.pool.get('fiscaldoc.iva').search(cr, uid, [('name', '=', ids)])
        if lines:
            res = self.pool.get('fiscaldoc.iva').unlink(cr, uid, lines, context) 
        else:
            # E' LA CREATE QUINDI CREA LE SCADENZE 
            totaledoc = 0
            for riga in righe_iva:
                totaledoc += righe_iva[riga]['imponibile'] + righe_iva[riga]['imposta']
            
            ok = self.pool.get('fiscaldoc.scadenze').agg_righe_scad(cr, uid, ids, totaledoc, context)
         
        for riga in righe_iva:
            
            record = {
                    'name':ids[0],
                    'codice_iva':riga,
                    'imponibile':righe_iva[riga]['imponibile'],
                    'imposta':righe_iva[riga]['imposta'],
                    }
            res = self.pool.get('fiscaldoc.iva').create(cr, uid, record)
        #import pdb;pdb.set_trace()  
        return True
    
    
FiscalDocIva()    
