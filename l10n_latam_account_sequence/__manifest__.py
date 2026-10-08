# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (c) 2011 CCI Connect asbl (http://www.cciconnect.be) All Rights Reserved.
#                       Philmer <philmer@cciconnect.be>

{
    'name': 'Accounting Sequence - Latam Documents',
    'version': '19.0.1.0.0',
    'author': 'Odoo SA',
    'category': 'Hidden',
    'description': "Módulo puente: en Odoo 19 los índices de nombre único para documentos LATAM los gestiona el núcleo (l10n_latam_invoice_document).",
    'depends': ['l10n_latam_invoice_document', 'account'],
    'installable': True,
    'auto_install': True,
    'license': 'LGPL-3',
}
