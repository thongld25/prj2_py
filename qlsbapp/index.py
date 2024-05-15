from flask import render_template, request, redirect, url_for, session, flash
from qlsbapp import app, login_manager, db
import utils
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from qlsbapp.models import UserRole, Sanbong, User, Receipt



@app.route("/")
def index():
    kw = request.args.get('keyword')
    page = request.args.get('page', 1)
    sanbongs = utils.load_sanbongs(kw=kw, page=int(page))
    user = current_user


    return render_template('index.html', sanbongs=sanbongs, user =user)


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        avatar_path = None

        try:
            if User.query.filter(User.email == email).first() is None:
                if User.query.filter(User.phone == phone).first() is None:
                    if User.query.filter(User.username == username).first() is None:
                        if password.strip().__eq__(confirm.strip()):
                            avatar = request.files.get('avatar')
                            if avatar:
                                res = cloudinary.uploader.upload(avatar)
                                avatar_path = res['secure_url']

                            utils.add_user(name=name, username=username,
                                           password=password, email=email,
                                           phone=phone,
                                           avatar=avatar_path)
                            return redirect(url_for('user_signin'))
                        else:
                            err_msg = 'Mật khẩu không khớp!!!'
                    else:
                        err_msg = 'Tên tài khoản đã tồn tại'
                else:
                    err_msg = 'Số điện thoại đã tồn tại'
            else:
                err_msg = 'Email đã tồn tại'
        except Exception as ex:
            err_msg = 'Hệ thống có lỗi' + str(ex)

    return render_template('register.html', err_msg=err_msg)

@app.route('/user_login', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_login(username=username, password=password, role=UserRole.USER)
        if user:
            login_user(user=user)
            return redirect(url_for('index'))
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không chính xác'

    return render_template('login.html', err_msg=err_msg)


@app.route('/admin-login', methods=['post'])
def admin_signin():
        # if not current_user.user_role == UserRole.ADMIN:
        username = request.form['username']
        password = request.form['password']

        user = utils.check_login(username=username, password=password, role=UserRole.ADMIN)
        if user:
            login_user(user=user)

        return redirect('/admin')



@app.route('/datsan/<int:sb_id>', methods=['get', 'post'])
def datsan(sb_id):
    user = current_user

    if current_user.is_anonymous:
        return redirect(url_for('user_signin'))
    sanbong_id = Sanbong.query.get(sb_id)
    err_msg = ''
    if request.method.__eq__('POST'):
        time_play = request.form.get('time_play')
        time_frame = request.form.get('khung_gio')
        try:
            if Receipt.query.filter(Receipt.time_play == time_play, Receipt.time_frame == time_frame).first() is None:
                utils.add_receipt(user_id=current_user.id, sanbong_id=sb_id, time_play=time_play, time_frame=time_frame, status='Chờ xác nhận')
                return redirect(url_for('lich_su'))
            else:
                err_msg = 'Giờ này đã được đặt'
        except Exception as ex:
            err_msg = 'Hệ thống có lỗi' + str(ex)

    return render_template('datsan.html', sanbong_id=sanbong_id, err_msg=err_msg)


@login_manager.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)

@app.route('/user_logout')
def user_signout():
    logout_user()
    return redirect(url_for('user_signin'))

@app.route('/lich_su', methods=['get'])
def lich_su():
    user_id = current_user.id
    receipts = utils.load_receipt(user_id)
    # for receipt in receipts:
    #     print(receipt.user_id)
    # sanbong_id = receipt.sanbong_id
    # print(receipt)
    # sanbong = utils.get_sanbong_by_id(sanbong_id)
    sanbongs = []
    for r in receipts:
        sanbong = utils.get_sanbong_by_id(r.sanbong_id)
        sanbongs.append(sanbong)
    # sanbong = utils.load_sanbongs()

    # if 'cancel' in request.args:
    #     receipt_id = request.args.get('cancel')
    #     receipt = Receipt.query.get_or_404(receipt_id)
    #     receipt.status = 'Đã bị hủy'
    #     db.session.commit()
    #     flash('Đơn hàng đã được hủy thành công.', 'success')

    return render_template('lich_su.html', receipts=receipts, sanbongs=sanbongs)
    return "Hello world"

# @app.route('/cancel/<int:receipt_id>', methods=['POST'])
# def cancel(receipt_id):
#     receipt = Receipt.query.get_or_404(receipt_id)
#     receipt.status = 'Đã hủy'
#     db.session.commit()
#     return redirect(url_for('your_blueprint_name.lichsu'))  # Thay 'your_blueprint_name' bằng tên blueprint thực tế của bạn nếu sử dụng


@app.route("/sanbong")
def sanbong_list():
    sanbong = utils.load_sanbongs()
    return render_template('sanbong.html', sanbong=sanbong)

if __name__ == '__main__':
    from qlsbapp.admin import *
    app.run(debug=True)