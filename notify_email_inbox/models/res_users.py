# -*- coding: utf-8 -*-

from odoo import api, Command, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    notification_type = fields.Selection(
        selection_add=[('email_inbox', "Handle by Emails and Sreenidhiraja")],
        ondelete={'email_inbox': 'set inbox'},
    )

    @api.depends('share', 'groups_id')
    def _compute_notification_type(self):
        """Preserve email+inbox preference while aligning group membership."""
        inbox_group_id = self.env['ir.model.data']._xmlid_to_res_id('mail.group_mail_notification_type_inbox')

        self.filtered_domain([
            ('groups_id', 'in', inbox_group_id),
            ('notification_type', 'not in', ['inbox', 'email_inbox']),
        ]).notification_type = 'inbox'

        self.filtered_domain([
            ('groups_id', 'not in', inbox_group_id),
            ('notification_type', 'in', ['inbox', 'email_inbox']),
        ]).notification_type = 'email'

        self.filtered_domain([
            ('share', '=', True),
            ('notification_type', 'in', ['inbox', 'email_inbox']),
        ]).notification_type = 'email'

    def _inverse_notification_type(self):
        """Keep inbox group for both inbox and email+inbox notification types."""
        inbox_group = self.env.ref('mail.group_mail_notification_type_inbox')
        inbox_users = self.filtered(lambda user: user.notification_type in ('inbox', 'email_inbox'))
        inbox_users.write({"groups_id": [Command.link(inbox_group.id)]})
        (self - inbox_users).write({"groups_id": [Command.unlink(inbox_group.id)]})
