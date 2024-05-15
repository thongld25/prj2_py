from qlsbapp import app, db
from flask_admin import Admin, BaseView, expose
from qlsbapp.models import Sanbong, UserRole, User, Receipt
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, render_template, url_for

admin = Admin(app=app, name="QLSB Admin", template_mode='bootstrap4')

class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class SanbongView(AuthenticatedModelView):
    can_view_details = True


class UserView(AuthenticatedModelView):
    can_view_details = True

# class ReceiptView(AuthenticatedModelView):
#     can_view_details = True

class LogoutView(BaseView):
    @expose('/')
    def index(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated

class ReceiptView(BaseView):
    @expose('/')
    def index(self):
        receipts = Receipt.query.filter_by(status='Chờ xác nhận').all()
        users = User.query.all()
        sanbongs = Sanbong.query.all()

        return self.render('admin/receipt.html', receipts=receipts, sanbongs=sanbongs, users=users)

    @expose('/confirm/<int:receipt_id>', methods=['POST'])
    def confirm(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đặt thành công'
        db.session.commit()
        return redirect(url_for('.index'))

    @expose('/cancel/<int:receipt_id>', methods=['POST'])
    def cancel(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đã bị hủy'
        db.session.commit()
        return redirect(url_for('.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN





admin.add_view(UserView(User, db.session, name='Người Dùng'))
admin.add_view(SanbongView(Sanbong, db.session, name='Sân Bóng'))
# admin.add_view(ReceiptView(Receipt, db.session, name='Đơn hàng'))
admin.add_view(LogoutView(name='Đăng xuất'))
admin.add_view(ReceiptView(name='Đơn hàng'))