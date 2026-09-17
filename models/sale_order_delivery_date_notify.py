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
	Flags a confirmed sale order when its delivery date changes and lets
	the salesperson decide whether to email the customer about it, using
	one of two ready-made templates (delayed / moved up).
"""
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import format_date

# Context flag that suppresses change detection - set on this module's own
# writes, and available for integrations (imports, sync jobs) that need to
# update commitment_date without triggering a false notification.
SKIP_CTX = 'x_ddn_skip'

TEMPLATE_XMLID_BY_DIRECTION = {
    'delay': 'hfb_app_delivery_date_notify.mail_template_delivery_date_delay',
    'earlier': 'hfb_app_delivery_date_notify.mail_template_delivery_date_earlier',
}


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    x_ddn_pending = fields.Boolean(
        string="Awaiting Delivery Date Notification",
        copy=False,
        help="The delivery date (commitment_date) changed on a confirmed "
             "order. The salesperson decides whether to notify the "
             "customer.",
    )
    x_ddn_baseline_date = fields.Datetime(
        string="Delivery Date Known To Customer",
        copy=False,
        help="The delivery date the customer was last informed about (or "
             "the value from before the first still-unsent change).",
    )
    x_ddn_direction = fields.Selection(
        selection=[('delay', 'Delay'), ('earlier', 'Earlier')],
        string="Delivery Date Change Direction",
        compute='_compute_x_ddn_direction',
    )
    x_ddn_summary = fields.Char(compute='_compute_x_ddn_direction')
    x_ddn_show_button = fields.Boolean(compute='_compute_x_ddn_show_button')

    @api.depends('commitment_date', 'x_ddn_baseline_date')
    def _compute_x_ddn_direction(self):
        for order in self:
            base, new = order.x_ddn_baseline_date, order.commitment_date
            if base and new and base != new:
                days = abs((new.date() - base.date()).days)
                if new > base:
                    order.x_ddn_direction = 'delay'
                    order.x_ddn_summary = _(
                        "Delivery date changed from %(old)s to %(new)s "
                        "(delayed by %(days)s days).",
                        old=format_date(order.env, base),
                        new=format_date(order.env, new), days=days,
                    )
                else:
                    order.x_ddn_direction = 'earlier'
                    order.x_ddn_summary = _(
                        "Delivery date changed from %(old)s to %(new)s "
                        "(moved up by %(days)s days).",
                        old=format_date(order.env, base),
                        new=format_date(order.env, new), days=days,
                    )
            else:
                order.x_ddn_direction = False
                order.x_ddn_summary = False

    @api.depends('x_ddn_pending', 'state')
    def _compute_x_ddn_show_button(self):
        for order in self:
            order.x_ddn_show_button = bool(
                order.x_ddn_pending and order.state == 'sale'
            )

    def write(self, vals):
        if 'commitment_date' not in vals or self.env.context.get(SKIP_CTX):
            return super().write(vals)

        new_date = fields.Datetime.to_datetime(vals.get('commitment_date'))
        baseline_by_order = {}
        if new_date:  # clearing the date doesn't generate a notification
            for order in self:
                old = order.commitment_date
                if (
                    order.state == 'sale'
                    and old and old != new_date
                    and order.partner_id
                ):
                    baseline_by_order[order.id] = order.x_ddn_baseline_date or old

        res = super().write(vals)

        for order in self:
            if order.id not in baseline_by_order:
                continue
            baseline = baseline_by_order[order.id]
            order_ctx = order.with_context(**{SKIP_CTX: True})
            if order.commitment_date == baseline:
                # back to the date the customer already knows - nothing to tell them
                order_ctx.write({'x_ddn_pending': False, 'x_ddn_baseline_date': False})
            else:
                order_ctx.write({
                    'x_ddn_pending': True,
                    'x_ddn_baseline_date': order.x_ddn_baseline_date or baseline,
                })
        return res

    def _ddn_template(self):
        self.ensure_one()
        xmlid = TEMPLATE_XMLID_BY_DIRECTION.get(self.x_ddn_direction)
        template = self.env.ref(xmlid, raise_if_not_found=False) if xmlid else False
        if not template:
            raise UserError(_(
                "No delivery date notification email template found "
                "(direction: %s). Check Settings > Technical > Email "
                "Templates.", self.x_ddn_direction))
        return template

    def action_ddn_send(self):
        """Opens the mail composer pre-filled with the right template
        (delay / earlier). Once the composer actually sends the message,
        the flag and baseline date are updated - see
        mail_compose_message_delivery_date_notify.py."""
        self.ensure_one()
        if not self.x_ddn_pending:
            raise UserError(_("There is no pending notification for this order."))
        if not self.x_ddn_direction:
            raise UserError(_("There is no delivery date change to communicate."))

        template = self._ddn_template()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Delivery Date Change Notification"),
            'res_model': 'mail.compose.message',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_model': 'sale.order',
                'default_res_ids': self.ids,
                'default_composition_mode': 'comment',
                'default_template_id': template.id,
                'default_email_layout_xmlid': 'mail.mail_notification_layout',
                'force_email': True,
                'x_ddn_order_id': self.id,
            },
        }

    def action_ddn_dismiss(self):
        for order in self.filtered('x_ddn_pending'):
            order.message_post(body=_(
                "Delivery date change notification dismissed - not sent "
                "(new date accepted as known to the customer)."))
            order.with_context(**{SKIP_CTX: True}).write({
                'x_ddn_pending': False,
                'x_ddn_baseline_date': order.commitment_date,
            })
        return True

#EoF
