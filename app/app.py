from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import datetime
from werkzeug.utils import secure_filename
import os
from PIL import Image

app = Flask(__name__)

# 初始化数据库
def init_db():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY,
            floor INTEGER,
            number INTEGER,
            ensuite BOOLEAN,
            air_conditioning BOOLEAN,
            external_window BOOLEAN,
            large_room BOOLEAN,
            twin_room BOOLEAN,
            long_term BOOLEAN,
            occupied BOOLEAN,
            tenant_name TEXT,
            rent_start_date TEXT,
            rent_end_date TEXT,
            status TEXT NOT NULL DEFAULT 'available', -- 表示房间状态
            room_image TEXT, -- 房间照片路径
            standard_price REAL NOT NULL DEFAULT 0, -- 标准价格
            UNIQUE(floor, number)
        )
    ''')
    # 租客表
    c.execute('''
        CREATE TABLE IF NOT EXISTS tenants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            room_id INTEGER NOT NULL,
            tenant_name TEXT NOT NULL,
            tenant_phone TEXT NOT NULL,
            rent_start_date TEXT NOT NULL,
            rent_end_date TEXT NOT NULL,
            lease_type TEXT NOT NULL, -- 区分长租和短租
            id_card_image_path TEXT, -- 租客身份证图片路径
            price REAL NOT NULL, -- 租金
            FOREIGN KEY(room_id) REFERENCES rooms(id)
        )
    ''')
    
    # 押金记录表
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tenant_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL, -- 交易类型（如租金、押金等）
            description TEXT,
            FOREIGN KEY(tenant_id) REFERENCES tenants(id)
        )
    ''')

    conn.commit()
    conn.close()

# 首页，显示所有房间
@app.route('/')
def index():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('SELECT * FROM rooms ORDER BY floor, number')
    rooms = c.fetchall()
    # 检查租期是否即将到期
    for i, room in enumerate(rooms):
        # if room[8]:  # 如果是长租房间
        #     c.execute('''
        #         SELECT date FROM transactions
        #         WHERE room_id = ? AND transaction_type = 'rent'
        #         ORDER BY date DESC LIMIT 1
        #     ''', (room[0],))

        #     last_rent_payment = c.fetchone()
        #     if last_rent_payment:
        #         last_payment_date = datetime.strptime(last_rent_payment[0], '%Y-%m-%d')
        #         next_payment_date = last_payment_date + timedelta(days=30)  # 假设每月交租
        #         rooms[i] += (next_payment_date.strftime('%Y-%m-%d'),)
        #         if next_payment_date <= datetime.now() + timedelta(days=7):  # 如果租金在一周内到期
        #             rooms[i] += ('租金即将到期！',)
        #         else:
        #             rooms[i] += ('',)
        #     else:
        #         rooms[i] += ('', '')
        # else:
        rooms[i] += ('', '')
    conn.close()
    return render_template('index.html', rooms=rooms, datetime=datetime)

# 添加房间页面
@app.route('/add_room', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        floor = request.form['floor']
        number = request.form['number']
        ensuite = 'ensuite' in request.form
        air_conditioning = 'air_conditioning' in request.form
        external_window = 'external_window' in request.form
        large_room = 'large_room' in request.form
        twin_room = 'twin_room' in request.form
        long_term = 'long_term' in request.form
        occupied = False
        tenant_name = ''
        rent_start_date = request.form.get('rent_start_date')
        rent_end_date = request.form.get('rent_end_date')

        if rent_start_date is None:
            rent_start_date = '2024-02-07'
        if rent_end_date is None:
            rent_end_date = '2024-02-08'
        

        standard_price = request.form['standard_price']
        tenant_phone = request.form.get('tenant_phone')
        # 获取当前日期
        today = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        print(today)
        # 处理房间照片上传
        room_image = request.files['room_image']
        if room_image and allowed_file(room_image.filename):
            # 构造新的房间照片文件名
            room_image_filename = f"room_{number}_{today}{get_file_extension(room_image.filename)}"
            room_image_path = os.path.join(app.config['ROOM_UPLOAD_FOLDER'], room_image_filename)
            room_image.save(room_image_path)
            # ...保存房间照片路径到数据库
            
            with Image.open(room_image_path) as img:
                img.save(room_image_path, quality=40)
        else:
            room_image_path = ''

        
        # # 处理身份证照片上传
        # id_card_image = request.files['id_card_image']
        # if id_card_image and allowed_file(id_card_image.filename):
        #     # 构造新的身份证照片文件名
        #     id_card_image_filename = f"id_{tenant_phone}_{today}{get_file_extension(id_card_image.filename)}"
        #     id_card_image_path = os.path.join(app.config['ID_UPLOAD_FOLDER'], id_card_image_filename)
        #     id_card_image.save(id_card_image_path)
        #     # ...保存身份证照片路径到数据库
        
        conn = sqlite3.connect('hotel.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO rooms (floor, number, ensuite, air_conditioning, external_window, large_room, twin_room, long_term, occupied, rent_start_date, rent_end_date, room_image, standard_price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (floor, number, ensuite, air_conditioning, external_window, large_room, twin_room, long_term, occupied, rent_start_date, rent_end_date, room_image_path, standard_price))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_room.html')


# 获取/更新某房间信息
@app.route('/room/<int:room_id>', methods=['GET', 'POST'])
def room(room_id):
    if request.method == 'POST':
        # 更新房间信息
        floor = request.form['floor']
        number = request.form['number']
        ensuite = 'ensuite' in request.form
        air_conditioning = 'air_conditioning' in request.form
        external_window = 'external_window' in request.form
        large_room = 'large_room' in request.form
        twin_room = 'twin_room' in request.form
        long_term = 'long_term' in request.form
        occupied = 'occupied' in request.form
        standard_price = request.form['standard_price']
        room_image = request.files['room_image']
        if room_image and allowed_file(room_image.filename):
            room_image_filename = f"room_{number}_{datetime.datetime.now().strftime('%Y%m%d')}{get_file_extension(room_image.filename)}"
            room_image_path = os.path.join(app.config['ROOM_UPLOAD_FOLDER'], room_image_filename)
            # 图片需要压缩到500k以下处理后保存 
            room_image.save(room_image_path)
            with Image.open(room_image_path) as img:
                img.save(room_image_path, quality=40)

        else:
            room_image_path = ''
        conn = sqlite3.connect('hotel.db')
        c = conn.cursor()
        # 不是空值就更新，是空值就不更新        
        
        c.execute('''
            UPDATE rooms
            SET floor = ?, number = ?, ensuite = ?, air_conditioning = ?, external_window = ?, large_room = ?, twin_room = ?, long_term = ?, occupied = ?, room_image = ?, standard_price = ? 
            WHERE id = ?
        ''', (floor, number, ensuite, air_conditioning, external_window, large_room, twin_room, long_term, occupied, room_image_path, standard_price, room_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
    room = c.fetchone()
    room = {
        'id': room[0],
        'floor': room[1],
        'number': room[2],
        'ensuite': room[3],
        'air_conditioning': room[4],
        'external_window': room[5],
        'large_room': room[6],
        'twin_room': room[7],
        'long_term': room[8],
        'occupied': room[9],
        'tenant_name': room[10],
        'rent_start_date': room[11],
        'rent_end_date': room[12],
        'room_image': room[14],
        'standard_price': room[15],
    }
    conn.close()
    return room


# 返回所有房间信息
@app.route('/rooms')
def rooms():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('SELECT * FROM rooms ORDER BY floor, number')
    rooms = c.fetchall()
    conn.close()
    # 返回结构性map json列表，方便前端渲染
    for i, room in enumerate(rooms):
        rooms[i] = {
            'id': room[0],
            'floor': room[1],
            'number': room[2],
            'ensuite': room[3],
            'air_conditioning': room[4],
            'external_window': room[5],
            'large_room': room[6],
            'twin_room': room[7],
            'long_term': room[8],
            'occupied': room[9],
            'tenant_name': room[10],
            'rent_start_date': room[11],
            'rent_end_date': room[12],
            'status': room[13],
            'room_image': room[14],
            'standard_price': room[15]
        }
        if room[12] is not None and room[12] > datetime.datetime.now().strftime('%Y-%m-%d'):
            rooms[i]['status'] = 'occupied'
    return rooms

# 入住登记 
@app.route('/check_in/<int:room_id>', methods=['GET', 'POST'])
def check_in(room_id):
    # 如果房间不空是不可以住的 
    conn = sqlite3.connect('hotel.db')
    d = conn.cursor()
    d.execute('SELECT * FROM rooms WHERE id = ?', (room_id,))
    room = d.fetchone()
    conn.close()
    
    room_price = room[15]
    if request.method == 'POST':
        if room[9] == 1:
            return redirect(url_for('index'))
        tenant_name = request.form['tenant_name']
        tenant_phone = request.form['tenant_phone']
        rent_start_date = request.form['rent_start_date']
        rent_end_date = request.form['rent_end_date']
        lease_type = request.form['lease_type']
        price = request.form['price']
        id_card_image = request.files['id_card_image']
        if id_card_image and allowed_file(id_card_image.filename):
            id_card_image_filename = f"id_{tenant_phone}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}{get_file_extension(id_card_image.filename)}"
            id_card_image_path = os.path.join(app.config['ID_UPLOAD_FOLDER'], id_card_image_filename)
            # 图片需要压缩到500k以下处理后保存 
            id_card_image.save(id_card_image_path)
            with Image.open(id_card_image_path) as img:
                img.save(id_card_image_path, quality=40)

        else:
            id_card_image_path = ''
        conn = sqlite3.connect('hotel.db')

        # 如果房间不空是不可以住的 
        c = conn.cursor()
        c.execute('''
            INSERT INTO tenants (room_id, tenant_name, tenant_phone, rent_start_date, rent_end_date, lease_type, id_card_image_path, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (room_id, tenant_name, tenant_phone, rent_start_date, rent_end_date, lease_type, id_card_image_path, price))
        c.execute('''
            UPDATE rooms
            SET occupied = 1, tenant_name = ?, rent_start_date = ?, rent_end_date = ?, status = 'occupied'
            WHERE id = ? and occupied = 0 
        ''', (tenant_name, rent_start_date, rent_end_date, room_id))


        # 如果有押金需要创建押金记录
        deposit_price = request.form.get('deposit_price')
        if deposit_price:
            c.execute('''
                INSERT INTO transactions (tenant_id, date, amount, transaction_type, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (c.lastrowid, rent_start_date, deposit_price, 'deposit', '押金'))


        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('check_in.html', room_id=room_id, room_price=room_price)

# 分页展示所有入住信息，以及押金信息
@app.route('/tenants')
def tenants():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    # 需要获取房间信息 租客信息 和 租客在房间的押金信息 
    
    c.execute('''
        SELECT tenants.id, tenants.room_id, tenants.tenant_name, tenants.tenant_phone, tenants.rent_start_date, tenants.rent_end_date, tenants.lease_type, tenants.id_card_image_path, tenants.price, rooms.floor, rooms.number, transactions.date, transactions.amount, transactions.transaction_type, transactions.description
        FROM tenants
        JOIN rooms ON tenants.room_id = rooms.id JOIN transactions ON tenants.id = transactions.tenant_id
    ''')
    tenants = c.fetchall()
    conn.close()
    return render_template('tenants.html', tenants=tenants)
 


# 添加交易记录页面
@app.route('/add_transaction/<int:room_id>', methods=['GET', 'POST'])
def add_transaction(room_id):
    if request.method == 'POST':
        date = request.form['date']
        amount = request.form['amount']
        description = request.form['description']
        transaction_type = request.form['transaction_type']
        
        conn = sqlite3.connect('hotel.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO transactions (room_id, date, amount, description, transaction_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (room_id, date, amount, description, transaction_type))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_transaction.html', room_id=room_id)


# 查看特定房间的交易记录页面
@app.route('/transactions/<int:room_id>')
def transactions(room_id):
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    c.execute('SELECT * FROM transactions WHERE room_id = ? ORDER BY date DESC', (room_id,))
    transactions = c.fetchall()
    conn.close()
    return render_template('transactions.html', transactions=transactions, room_id=room_id)

# 查看统计信息页面
@app.route('/statistics')
def statistics():
    conn = sqlite3.connect('hotel.db')
    c = conn.cursor()
    # 获取每个房间的总收入
    c.execute('''
        SELECT room_id, SUM(amount) as total_income
        FROM transactions
        GROUP BY room_id
    ''')
    income_per_room = c.fetchall()
    # 获取每月的总收入
    c.execute('''
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as monthly_income
        FROM transactions
        GROUP BY month
    ''')
    income_per_month = c.fetchall()
    conn.close()
    return render_template('statistics.html', income_per_room=income_per_room, income_per_month=income_per_month)


# 设置身份证照片的保存路径
ID_UPLOAD_FOLDER = 'static/id_card_image'
ROOM_UPLOAD_FOLDER = 'static/room_image'

app.config['ID_UPLOAD_FOLDER'] = ID_UPLOAD_FOLDER
app.config['ROOM_UPLOAD_FOLDER'] = ROOM_UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def get_file_extension(filename):
    return os.path.splitext(filename)[1]



# 初始化数据库
init_db()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
