# -*- coding: utf-8 -*-
# vim: tabstop=4 softtabstop=0 shiftwidth=4 smarttab expandtab fileformat=unix
#################################################################################
#
# Odoo, Open Source Management Solution
# Copyright (C) 2017-2026 Hadron for Business sp. z o.o. (http://hadronforbusiness.com)
#
# This program is proprietary software, licensed under the Odoo Proprietary
# License v1.0 (OPL-1). Its use is governed by the Odoo Apps terms available
# at https://www.odoo.com/documentation/user/legal/licenses.html and the
# license agreement accepted at purchase / installation.
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the
# Software or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in
# all copies or substantial portions of the Software.
#
#################################################################################
{
    'name': "Delivery Date Change Notification",
    'summary': "Let salespeople notify customers when a confirmed order's delivery date changes",
    'description': """
Delivery Date Change Notification
====================================

When the delivery date on a confirmed sale order changes, the order is
flagged and the salesperson gets two buttons on the form: send a
notification email to the customer, or dismiss it (accepting the new date
as already known to them, no email sent).

Two ready-made, editable email templates are included - one for a delayed
delivery, one for an earlier delivery - picked automatically based on
whether the new date is later or earlier than the one last communicated.
""",
    'version': "20.0.1.0.0",
    'author': "Hadron for Business sp. z o.o.",
    'website': "http://hadronforbusiness.com",
    'license': "OPL-1",
    'category': "Sales/Sales",
    'depends': [
        'sale',
    ],
    'data': [
        'data/mail_template_delivery_date_notify.xml',
        'views/sale_order_delivery_date_notify_views.xml',
    ],
    'images': [
        'static/description/banner_screenshot.png',
    ],
    'installable': True,
    'application': False,
}
