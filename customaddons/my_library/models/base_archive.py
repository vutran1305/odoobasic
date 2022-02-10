from odoo import models, fields, api
from datetime import timedelta

class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    active = fields.Boolean(default=True)

    def do_archive(self):
        for record in self:
            record.active = not record.active


"""
Khi tách ra file mới ntn thì kế thừa bị lỗi :
TypeError: Model 'library.book' inherits from non-existing model 'base.archive'.
"""