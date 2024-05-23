from qlsbapp import app, db
from flask_admin import Admin, BaseView, expose
from qlsbapp.models import Sanbong, UserRole, User, Receipt
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, render_template, url_for, request, flash

admin = Admin(app=app, name="QLSB Admin", template_mode='bootstrap4')

class AuthenticatedModelView(ModelView):
    # list_template = 'admin/list.html'
    # create_template = 'admin/create.html'
    # edit_template = 'admin/edit.html'
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

class SanbongView(BaseView):
    @expose('/')
    def index(self):
        sanbongs = Sanbong.query.filter_by(active = True)
        return self.render('admin/sanbong.html', sanbongs=sanbongs)

    @expose('/add', methods=('GET', 'POST'))
    def add(self):
        if request.method == 'POST':
            name = request.form['name']
            type_pitch = request.form['type_pitch']
            surface_pitch = request.form['surface_pitch']
            price = request.form['price']
            address = request.form['address']
            image = request.form['image']
            new_sanbong = Sanbong(name=name, type_pitch=type_pitch, surface_pitch=surface_pitch, price=price, address=address, image=image)
            db.session.add(new_sanbong)
            db.session.commit()
            flash('Sân bóng đã được thêm thành công!')
            return redirect(url_for('.index'))
        return self.render('admin/add_sanbong.html')

    @expose('/edit/<int:id>', methods=('GET', 'POST'))
    def edit(self, id):
        sanbong = Sanbong.query.get_or_404(id)
        if request.method == 'POST':
            sanbong.name = request.form['name']
            sanbong.type_pitch = request.form['type_pitch']
            sanbong.surface_pitch = request.form['surface_pitch']
            sanbong.price = request.form['price']
            sanbong.address = request.form['address']
            sanbong.image = request.form['image']
            db.session.commit()
            flash('Sân bóng đã được cập nhật!')
            return redirect(url_for('.index'))
        return self.render('admin/edit_sanbong.html', sanbong=sanbong)

    @expose('/delete/<int:id>', methods=('POST',))
    def delete(self, id):
        sanbong = Sanbong.query.get_or_404(id)
        sanbong.active = False
        db.session.commit()
        flash('Sân bóng đã được xóa!')
        return redirect(url_for('.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class UserView(BaseView):
    @expose('/')
    def index(self):
        users = User.query.filter(User.user_role != UserRole.ADMIN)
        return self.render('admin/user.html', users=users)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN
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
        # receipts = Receipt.query.all()
        users = User.query.all()
        sanbongs = Sanbong.query.all()
        return self.render('admin/receipt.html', receipts=receipts, sanbongs=sanbongs, users=users)

    @expose('/confirm/<int:receipt_id>', methods=['POST'])
    def confirm(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đặt thành công'
        db.session.commit()
        return redirect(url_for('.index'))

    @expose('/canceled/<int:receipt_id>', methods=['POST'])
    def canceled(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đã bị hủy'
        db.session.commit()
        return redirect(url_for('.index'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

class AllReceiptView(BaseView):
    @expose('/')
    def index(self):
        # receipts = Receipt.query.filter_by(status='Chờ xác nhận').all()
        receipts = Receipt.query.all()
        users = User.query.all()
        sanbongs = Sanbong.query.all()
        return self.render('admin/all_receipt.html', receipts=receipts, sanbongs=sanbongs, users=users)
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin.add_view(UserView(name='Người Dùng'))
# admin.add_view(ReceiptView(Receipt, db.session, name='Đơn hàng'))
admin.add_view(AllReceiptView(name='Tất cả đơn hàng'))
admin.add_view(SanbongView(name='Sân bóng'))
admin.add_view(ReceiptView(name='Đơn hàng'))
admin.add_view(LogoutView(name='Đăng xuất'))