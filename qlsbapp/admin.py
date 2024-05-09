from qlsbapp import app, db
from flask_admin import Admin
from qlsbapp.models import Sanbong
from flask_admin.contrib.sqla import ModelView

admin = Admin(app=app, name="QLSB Admin", template_mode='bootstrap4')

class SanbongView(ModelView):
    can_view_details = True


admin.add_view(SanbongView(Sanbong, db.session))