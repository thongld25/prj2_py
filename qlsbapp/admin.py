from sqlalchemy import Float

from qlsbapp import app, db
import utils
from flask_admin import Admin, BaseView, expose, AdminIndexView
from qlsbapp.models import Sanbong, UserRole, User, Receipt
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, logout_user
from flask import redirect, render_template, url_for, request, flash, jsonify
from datetime import datetime, timedelta
from sqlalchemy.sql import func, extract


class AuthenticatedModelView(ModelView):
    # list_template = 'admin/list.html'
    # create_template = 'admin/create.html'
    # edit_template = 'admin/edit.html'
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)

# class HomeAdminView(AdminIndexView):
#     @expose('/')
#     def index(self):
#         # if not current_user.is_authenticated:
#         #     return redirect(url_for('admin_signin'))
#         sanbongs = Sanbong.query.all()
#
#         return self.render('admin/index.html', sanbongs=sanbongs)
#



class HomeAdminView(AdminIndexView):
    @expose('/')
    def index(self):
        sanbongs = Sanbong.query.all()
        return self.render('admin/index.html', sanbongs=sanbongs)

    @expose('/sales_data')
    def sales_data(self):
        # Fetch total sales per month
        total_sales_per_month = db.session.query(
            func.extract('month', Receipt.time_play).label('month'),
            func.sum(Sanbong.price).label('total_sales')
        ).join(Sanbong, Sanbong.id == Receipt.sanbong_id).filter(
            Receipt.status == 'Đã Thanh Toán'
        ).group_by('month').all()

        # Fetch sales per month for each football field
        sales_per_field_per_month = db.session.query(
            Sanbong.name.label('field_name'),
            func.extract('month', Receipt.time_play).label('month'),
            func.sum(Sanbong.price).label('field_sales')
        ).join(Sanbong, Sanbong.id == Receipt.sanbong_id).filter(
            Receipt.status == 'Đã Thanh Toán'
        ).group_by(Sanbong.name, 'month').all()

        # Format data for Chart.js
        data = {
            'total_sales': {month: 0 for month in range(1, 13)},
            'fields': {}
        }

        for sale in total_sales_per_month:
            data['total_sales'][int(sale.month)] = float(sale.total_sales)

        for sale in sales_per_field_per_month:
            if sale.field_name not in data['fields']:
                data['fields'][sale.field_name] = {month: 0 for month in range(1, 13)}
            data['fields'][sale.field_name][int(sale.month)] = float(sale.field_sales)

        return jsonify(data)


    @expose('/revenue_data', methods=['GET'])
    def revenue_data(self):
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        sales_data = db.session.query(
            Sanbong.name,
            func.sum(Sanbong.price).label('total_sales')
        ).join(Receipt).filter(
            Receipt.status == 'Đã Thanh Toán',
            Receipt.time_play >= start_date,
            Receipt.time_play <= end_date
        ).group_by(Sanbong.name).all()

        sales_data = [{'sanbong': name, 'total_sales': total_sales} for name, total_sales in sales_data]

        return jsonify(sales_data)
    # def is_accessible(self):
    #     return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)




class SanbongView(BaseView):
    @expose('/')
    def index(self):
        sanbongs = Sanbong.query.filter_by(active = True)
        return self.render('admin/sanbong.html', sanbongs=sanbongs)

    @expose('/add', methods=('GET', 'POST'))
    def add(self):
        name = ""
        type_pitch = ""
        surface_pitch = ""
        price = ""
        address = ""
        image = ""
        if request.method == 'POST':
            name = request.form['name']
            type_pitch = request.form['type_pitch']
            surface_pitch = request.form['surface_pitch']
            price = request.form['price']
            address = request.form['address']
            image = request.form['image']
            if Sanbong.query.filter_by(name=name).first() != None:
                flash('Tên sân bóng đã tồn tại!', 'error')
            else:
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

    @expose('/profile_user/<int:u_id>', methods=['get'])
    def profile_user(self, u_id):
        user = User.query.get_or_404(u_id)
        receipts = Receipt.query.filter_by(user_id=u_id).all()
        sanbongs = {}
        for r in receipts:
            sanbong = utils.get_sanbong_by_id(r.sanbong_id)
            if sanbong:
                sanbongs[r.sanbong_id] = sanbong

        return self.render('admin/profile_user.html', receipts=receipts, user=user, sanbongs=sanbongs)

    @expose('/black-list')
    def blacklist(self):
        subquery = db.session.query(
            Receipt.user_id,
            func.count(Receipt.id).label('bung_count')
        ).filter(
            Receipt.status == 'Bùng'
        ).group_by(
            Receipt.user_id
        ).subquery()

        # Tạo truy vấn để lấy thông tin người dùng có số lượng biên lai 'Bùng' >= 5
        query = db.session.query(
            User,
            subquery.c.bung_count
        ).join(
            subquery,
            User.id == subquery.c.user_id
        ).filter(
            subquery.c.bung_count >= 5
        ).all()

        return self.render('admin/blacklist.html', users=query)

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

    @expose('/all_receipt')
    def all_receipt(self):
        # receipts = Receipt.query.filter_by(status='Chờ xác nhận').all()
        receipts = Receipt.query.all()
        users = User.query.all()
        sanbongs = Sanbong.query.all()
        return self.render('admin/all_receipt.html', receipts=receipts, sanbongs=sanbongs, users=users)

    @expose('/chuathanhtoan')
    def chuathanhtoan(self):
        receipts = Receipt.query.filter_by(status='Đặt thành công').all()
        users = User.query.all()
        sanbongs = Sanbong.query.all()
        return self.render('admin/chuathanhtoan.html', receipts=receipts, users=users, sanbongs=sanbongs)

    @expose('/paid/<int:receipt_id>', methods=['POST'])
    def paid(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đã thanh toán'
        db.session.commit()
        return redirect(url_for('.chuathanhtoan'))

    @expose('/notpaid/<int:receipt_id>', methods=['POST'])
    def notpaid(self, receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Bùng'
        db.session.commit()
        return redirect(url_for('.chuathanhtoan'))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

# class AllReceiptView(BaseView):
#     @expose('/')
#     def index(self):
#         # receipts = Receipt.query.filter_by(status='Chờ xác nhận').all()
#         receipts = Receipt.query.all()
#         users = User.query.all()
#         sanbongs = Sanbong.query.all()
#         return self.render('admin/all_receipt.html', receipts=receipts, sanbongs=sanbongs, users=users)
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

# class ThanhToanView(BaseView):
#     @expose('/')
#     def index(self):
#         receipts = Receipt.query.filter_by(status='Đặt thành công').all()
#         users = User.query.all()
#         sanbongs = Sanbong.query.all()
#         return self.render('admin/chuathanhtoan.html', receipts=receipts, users=users, sanbongs=sanbongs)
#
#     @expose('/paid/<int:receipt_id>', methods=['POST'])
#     def paid(self, receipt_id):
#         receipt = Receipt.query.get_or_404(receipt_id)
#         receipt.status = 'Đã thanh toán'
#         db.session.commit()
#         return redirect(url_for('.index'))
#
#     @expose('/notpaid/<int:receipt_id>', methods=['POST'])
#     def notpaid(self, receipt_id):
#         receipt = Receipt.query.get_or_404(receipt_id)
#         receipt.status = 'Bùng'
#         db.session.commit()
#         return redirect(url_for('.index'))
#
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

# class DanhsachdenView(BaseView):
#     @expose('/')
#     def index(self):
#         subquery = db.session.query(
#             Receipt.user_id,
#             func.count(Receipt.id).label('bung_count')
#         ).filter(
#             Receipt.status == 'Bùng'
#         ).group_by(
#             Receipt.user_id
#         ).subquery()
#
#         # Tạo truy vấn để lấy thông tin người dùng có số lượng biên lai 'Bùng' >= 5
#         query = db.session.query(
#             User,
#             subquery.c.bung_count
#         ).join(
#             subquery,
#             User.id == subquery.c.user_id
#         ).filter(
#             subquery.c.bung_count >= 5
#         ).all()
#
#         return self.render('admin/blacklist.html', users=query)
#
#     def is_accessible(self):
#         return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN

admin = Admin(app=app, name="Quản lý sân bóng",index_view=HomeAdminView(name='Trang chủ'), template_mode='bootstrap4')
admin.add_view(UserView(name='Người Dùng'))
admin.add_view(SanbongView(name='Sân bóng'))
# admin.add_view(ReceiptView(Receipt, db.session, name='Đơn hàng'))
# admin.add_view(AllReceiptView(name='Tất cả đơn hàng'))
admin.add_view(ReceiptView(name='Đơn hàng'))
# admin.add_view(ThanhToanView(name='Chưa thanh toán'))
admin.add_view(LogoutView(name='Đăng xuất'))
