from flask import render_template, request, redirect, url_for, session, flash
from qlsbapp import app, login_manager, db
import utils, hashlib
import cloudinary.uploader
from flask_login import login_user, logout_user, current_user
from qlsbapp.models import UserRole, Sanbong, User, Receipt
from werkzeug.security import  check_password_hash, generate_password_hash



@app.route("/")
def index():
    kw = request.args.get('keyword')
    sanbongs = Sanbong.query.filter_by(active = True)
    user = current_user


    return render_template('index.html', sanbongs=sanbongs, user =user)


@app.route('/register', methods=['GET', 'POST'])
def user_register():
    err_msg = ""
    name = ""
    email = ""
    phone = ""
    username = ""

    if request.method == 'POST':
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
                        if password.strip() == confirm.strip():
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

    return render_template('register.html', err_msg=err_msg, name=name, email=email, phone=phone, username=username)


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


@app.route('/admin_signin', methods=['POST'])
def admin_signin():
        # if not current_user.user_role == UserRole.ADMIN:
        print("admin_signin route called")
        print("Request method:", request.method)
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
        # r =  Receipt.query.filter(Receipt.time_play == time_play, Receipt.time_frame == time_frame).first()
        # print(r.time_play)
        # print(time_play)

        try:
            if Receipt.query.filter(Receipt.time_play == time_play, Receipt.time_frame == time_frame).first() is None:
                utils.add_receipt(user_id=current_user.id, sanbong_id=sb_id, time_play=time_play, time_frame=time_frame, status='Chờ xác nhận')
                return redirect(url_for('wait_confirm'))
            else:
                print('123')
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
    sanbongs = []
    for r in receipts:
        sanbong = utils.get_sanbong_by_id(r.sanbong_id)
        sanbongs.append(sanbong)

    return render_template('lich_su.html', receipts=receipts, sanbongs=sanbongs)

@app.route('/wait_confirm', methods=['get', 'post'])
def wait_confirm():
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

    return render_template('wait_confirm.html', receipts=receipts, sanbongs=sanbongs)

@app.route('/cancel/<int:receipt_id>', methods=['POST'])
def cancel(receipt_id):
        receipt = Receipt.query.get_or_404(receipt_id)
        receipt.status = 'Đã hủy'
        db.session.commit()
        flash('Đã hủy đặt sân thành công')
        return redirect(url_for('wait_confirm'))



@app.route("/sanbong")
def sanbong_list():
    sanbong = utils.load_sanbongs()
    return render_template('sanbong.html', sanbong=sanbong)

@app.route('/profile', methods=['GET', 'POST'])
def edit_profile():
    user = current_user
    if request.method == 'POST':
        err_msg = ""
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        username = request.form.get('username')

        try:
            if User.query.filter(User.email == email).first() is None or user.email == email:
                if User.query.filter(User.phone == phone).first() is None or user.phone == phone:
                    if User.query.filter(User.username == username).first() is None or user.username == username:
                        user.name = name
                        user.email = email
                        user.phone = phone
                        user.username = username
                        db.session.commit()
                        flash('Đã chỉnh sửa thông tin thành công!', 'success')
                        return redirect(url_for('edit_profile'))
                    else:
                        err_msg = 'Tên tài khoản đã tồn tại'
                else:
                    err_msg = 'Số điện thoại đã tồn tại'
            else:
                err_msg = 'Email đã tồn tại'
        except Exception as ex:
            err_msg = 'Hệ thống có lỗi: ' + str(ex)
            flash(err_msg, 'danger')

    return render_template('edit_profile.html', user=user)

@app.route('/change_password', methods= ['get', 'post'])
def change_password():
    user = current_user
    if request.method == 'POST':
        err_msg = ''
        current = request.form.get('current')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        current = str(hashlib.md5(current.strip().encode('utf-8')).hexdigest())
        if user.password == current:
            print('123434')
            if password == confirm:
                password = password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
                user.password = password
                db.session.commit()
                print(123)
                flash('Đổi mật khẩu thành công', 'success')
                return redirect(url_for('index'))
            else:
                err_msg = 'Mật khẩu không khớp!'
        else:
            err_msg = 'Mật khẩu hiện tại không đúng!'
        flash(err_msg, 'error')

    return render_template('change_password.html', user=user)



if __name__ == '__main__':
    from qlsbapp.admin import *
    app.run(debug=True)

