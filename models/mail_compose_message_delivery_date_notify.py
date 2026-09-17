# -*- coding: utf-8 -*-
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
""" @version	17.0.1.0.0
	@owner  Hadron for Business
	@author Hadron for Business sp. z o.o.
	@date   2026.09.17

	Delivery Date Change Notification
	Once the delivery-date-change email is actually sent from the composer
	opened by sale.order.action_ddn_send(), clears the pending flag and
	moves the baseline date forward.
"""
from odoo import models


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    def _action_send_mail(self, auto_commit=False):
        res = super()._action_send_mail(auto_commit=auto_commit)

        order_id = self.env.context.get('x_ddn_order_id')
        if order_id:
            order = self.env['sale.order'].browse(order_id).exists()
            if order and order.x_ddn_pending:
                order.with_context(x_ddn_skip=True).write({
                    'x_ddn_pending': False,
                    'x_ddn_baseline_date': order.commitment_date,
                })
        return res

#EoF
