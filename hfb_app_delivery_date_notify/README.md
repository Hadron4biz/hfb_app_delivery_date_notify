# Delivery Date Change Notification

Flags a confirmed sale order when its delivery date changes, and gives the
salesperson a one-click way to tell the customer - or to dismiss it.

## The problem

A delivery date slips, or gets pulled forward, and someone has to remember
to tell the customer - by digging up their email, writing a message, and
sending it by hand. Easy to forget, especially when the order was already
confirmed a while ago.

## How it works

- `sale.order.write()` watches for `commitment_date` changes on confirmed
  orders and sets `x_ddn_pending` + a baseline date (the date the customer
  was last actually told about).
- Two buttons appear on the order form while a change is pending: **Send
  Delivery Date Notification** (opens the mail composer, pre-filled with
  the right template) and **Dismiss Notification** (accepts the new date as
  known to the customer, no email sent).
- The right template - delay or earlier - is picked automatically by
  comparing the new date to the baseline.
- Once the composer actually sends the email, the flag clears and the
  baseline moves to the new date.
- A search filter ("Awaiting Delivery Date Notification") helps find orders
  with a pending notification.

## Technical

- `models/sale_order_delivery_date_notify.py` - the flag/baseline/direction
  fields, the `write()` override, and the two button actions.
- `models/mail_compose_message_delivery_date_notify.py` - clears the flag
  once the composer sends the email.
- `data/mail_template_delivery_date_notify.xml` - two editable
  `mail.template` records (delay / earlier), looked up by fixed XML ID.
- `views/sale_order_delivery_date_notify_views.xml` - form buttons/banner +
  search filter.
- No new models, no security rules.
- Depends on: `sale`.

## Status

Extracted from a client-specific module (`hfb_bannerstop_invoice_total`) as
part of the generic app extraction workflow, and simplified along the way:
the source picked its template by searching for a marker field
(`x_bs_ddn_kind`) instead of `env.ref()`, to work around a module-name
mismatch between two client deployments that doesn't exist in this repo's
topology - here the templates are looked up directly by their (fixed)
`env.ref()` XML ID instead.

Missing `static/description/icon.png` (and optionally a
`*_screenshot.png`) before it can be submitted to Odoo Apps. The email
templates ship in English only; a Polish (or other language) version of
the *email content* itself can be added per-template via Odoo's built-in
Translate feature after install - `i18n/pl.po` here only covers the UI
strings (fields, buttons, filter, error messages).
