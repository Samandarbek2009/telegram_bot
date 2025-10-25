pip install psycopg2-binary
import urllib.request
import json
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from flask import Flask, request, abort
app = Flask(__name__)

# Bot tokeni va admin IDlar
TOKEN = os.getenv('TOKEN', '8201394886:AAGU_updxee1aAzOE5lzB_Sq2JrSHP4Tek8')
ADMIN_IDS = [7869559383, 8023582744]
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

# PostgreSQL ma'lumotlar bazasi funksiyasi
def db(query, params=(), fetchall=True):
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
        if fetchall:
            result = cursor.fetchall()
        else:
            result = cursor.fetchone()
    except Exception as e:
        print(f"Ma'lumotlar bazasi xatosi: {e}")
        result = None
    finally:
        conn.close()
    return result

# Ma'lumotlar bazasini boshlash
def init_db():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'), cursor_factory=RealDictCursor)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS data (
        id SERIAL PRIMARY KEY,
        savol TEXT,
        javob TEXT,
        javob_type TEXT DEFAULT 'text',
        category TEXT DEFAULT 'Umumiy'
    )''')
    # Check if columns exist
    cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'data'")
    columns = [row['column_name'] for row in cursor.fetchall()]
    if 'javob_type' not in columns:
        cursor.execute('ALTER TABLE data ADD COLUMN javob_type TEXT DEFAULT \'text\'')
        cursor.execute('UPDATE data SET javob_type = \'text\' WHERE javob_type IS NULL')
    if 'category' not in columns:
        cursor.execute('ALTER TABLE data ADD COLUMN category TEXT DEFAULT \'Umumiy\'')
        cursor.execute('UPDATE data SET category = \'Umumiy\' WHERE category IS NULL')
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        queries_count INTEGER DEFAULT 0
    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS feedback (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        feedback_text TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# Quyidagi funksiyalar o‘zgarishsiz qoladi (oldingi koddan nusxalang)
def format_data(rows, page=0, per_page=5):
    start = page * per_page
    end = start + per_page
    paginated_rows = rows[start:end]
    formatted = '\n'.join('ID: %s\nKategoriya: %s\nSavol: %s\nJavob: %s (%s)\n' % (r['id'], r['category'], r['savol'], r['javob'], r['javob_type'] or 'text') for r in paginated_rows) or 'Ma\'lumot yo‘q.'
    total_pages = (len(rows) + per_page - 1) // per_page
    return formatted, total_pages

def send_message(chat_id, text, reply_markup=None):
    try:
        url = BASE_URL + 'sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        if reply_markup:
            data['reply_markup'] = reply_markup
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        urllib.request.urlopen(req)
    except Exception as e:
        print(f"Xabar yuborishda xato (chat_id: {chat_id}): {e}")

def send_photo(chat_id, photo_id, caption=None, reply_markup=None):
    try:
        print(f"Rasm yuborilmoqda: chat_id={chat_id}, photo_id={photo_id}")
        url = BASE_URL + 'sendPhoto'
        data = {'chat_id': chat_id, 'photo': photo_id}
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        print(f"Rasm yuborildi: {response.read().decode()}")
    except Exception as e:
        print(f"Rasm yuborishda xato (chat_id: {chat_id}, photo_id: {photo_id}): {e}")
        send_message(chat_id, f"Rasm yuborishda xato: {e}")

def send_video(chat_id, video_id, caption=None, reply_markup=None):
    try:
        print(f"Video yuborilmoqda: chat_id={chat_id}, video_id={video_id}")
        url = BASE_URL + 'sendVideo'
        data = {'chat_id': chat_id, 'video': video_id}
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        print(f"Video yuborildi: {response.read().decode()}")
    except Exception as e:
        print(f"Video yuborishda xato (chat_id: {chat_id}, video_id: {video_id}): {e}")
        send_message(chat_id, f"Video yuborishda xato: {e}")

def send_voice(chat_id, voice_id, caption=None, reply_markup=None):
    try:
        print(f"Ovozli xabar yuborilmoqda: chat_id={chat_id}, voice_id={voice_id}")
        url = BASE_URL + 'sendVoice'
        data = {'chat_id': chat_id, 'voice': voice_id}
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        print(f"Ovozli xabar yuborildi: {response.read().decode()}")
    except Exception as e:
        print(f"Ovozli xabar yuborishda xato (chat_id: {chat_id}, voice_id: {voice_id}): {e}")
        send_message(chat_id, f"Ovozli xabar yuborishda xato: {e}")

def send_audio(chat_id, audio_id, caption=None, reply_markup=None):
    try:
        print(f"Audio yuborilmoqda: chat_id={chat_id}, audio_id={audio_id}")
        url = BASE_URL + 'sendAudio'
        data = {'chat_id': chat_id, 'audio': audio_id}
        if caption:
            data['caption'] = caption
        if reply_markup:
            data['reply_markup'] = reply_markup
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        response = urllib.request.urlopen(req)
        print(f"Audio yuborildi: {response.read().decode()}")
    except Exception as e:
        print(f"Audio yuborishda xato (chat_id: {chat_id}, audio_id: {audio_id}): {e}")
        send_message(chat_id, f"Audio yuborishda xato: {e}")

def get_main_keyboard(is_admin=False):
    keyboard = {
        'keyboard': [['/start', '/info'], ['/search_savol', '/search_javob'], ['/feedback']],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    if is_admin:
        keyboard['keyboard'].append(['/add', '/edit', '/delete', '/stats', '/broadcast', '/export', '/import', '/view_feedback'])
    return json.dumps(keyboard)

def get_category_keyboard():
    categories = db('SELECT DISTINCT category FROM data')
    buttons = [[{'text': cat['category'], 'callback_data': f'cat_{cat["category"]}'}] for cat in categories]
    buttons.append([{'text': 'Barchasi', 'callback_data': 'cat_all'}])
    return json.dumps({'inline_keyboard': buttons})

def get_delete_confirmation_keyboard(id_to_delete):
    return json.dumps({
        'inline_keyboard': [
            [{'text': 'Tasdiqlash', 'callback_data': f'delete_confirm_{id_to_delete}'},
             {'text': 'Bekor qilish', 'callback_data': 'delete_cancel'}]
        ]
    })

def get_pagination_keyboard(page, total_pages, is_admin=False):
    buttons = []
    if page > 0:
        buttons.append({'text': '⬅️ Oldingi', 'callback_data': f'prev_{page}'})
    if page < total_pages - 1:
        buttons.append({'text': 'Keyingi ➡️', 'callback_data': f'next_{page}'})
    return json.dumps({'inline_keyboard': [buttons] if buttons else []})

def update_user_stats(user_id, username, first_name):
    try:
        existing = db('SELECT * FROM users WHERE user_id=%s', (user_id,), fetchall=False)
        if existing:
            db('UPDATE users SET last_login=CURRENT_TIMESTAMP, queries_count=queries_count+1 WHERE user_id=%s', (user_id,))
        else:
            db('INSERT INTO users (user_id, username, first_name, queries_count) VALUES (%s, %s, %s, 1)', (user_id, username, first_name))
    except Exception as e:
        print(f"Foydalanuvchi statistikasini yangilashda xato (user_id: {user_id}): {e}")

def get_all_users():
    return db('SELECT user_id FROM users')

def format_stats():
    try:
        total_users = len(db('SELECT * FROM users') or [])
        total_queries_result = db('SELECT SUM(queries_count) FROM users', fetchall=False)
        total_queries = total_queries_result['sum'] if total_queries_result and total_queries_result['sum'] is not None else 0
        total_data = len(db('SELECT * FROM data') or [])
        total_feedback = len(db('SELECT * FROM feedback') or [])
        return f'Foydalanuvchilar soni: {total_users}\nJami qidiruvlar: {total_queries}\nMa\'lumotlar soni: {total_data}\nFeedbacklar soni: {total_feedback}'
    except Exception as e:
        print(f"Statistikada xato: {e}")
        return f"Statistikani olishda xato yuz berdi: {e}"

def export_data():
    try:
        data = db('SELECT id, savol, javob, javob_type, category FROM data')
        with open('data_export.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True, 'Ma\'lumotlar data_export.json fayliga eksport qilindi.'
    except Exception as e:
        print(f"Eksportda xato: {e}")
        return False, f"Eksport qilishda xato: {e}"

def import_data():
    try:
        if not os.path.exists('data_export.json'):
            return False, 'data_export.json fayli topilmadi.'
        with open('data_export.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        db('DELETE FROM data')  # Eski ma'lumotlarni o'chirish
        for row in data:
            db('INSERT INTO data (id, savol, javob, javob_type, category) VALUES (%s, %s, %s, %s, %s)', 
               (row['id'], row['savol'], row['javob'], row['javob_type'], row['category']))
        return True, f'{len(data)} ta ma\'lumot import qilindi.'
    except Exception as e:
        print(f"Importda xato: {e}")
        return False, f"Import qilishda xato: {e}"

# Webhook sozlash
def set_webhook():
    webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'your-app.onrender.com')}/webhook"
    url = BASE_URL + f'setWebhook?url={webhook_url}'
    try:
        response = urllib.request.urlopen(url)
        print(f"Webhook sozlandi: {response.read().decode()}")
    except Exception as e:
        print(f"Webhook sozlashda xato: {e}")

# Update ishlov berish
def process_update(update):
    if 'callback_query' in update:
        callback = update['callback_query']
        chat_id = callback['message']['chat']['id']
        data = callback['data']
        message_id = callback['message']['message_id']
        is_admin = (callback['from']['id'] in ADMIN_IDS)

        # Pagination
        if data.startswith('prev_') or data.startswith('next_'):
            if chat_id in pagination_states:
                page, rows = pagination_states[chat_id]
                new_page = page - 1 if data.startswith('prev_') else page + 1
                formatted, total_pages = format_data(rows, new_page)
                pagination_states[chat_id] = (new_page, rows)
                edit_url = BASE_URL + 'editMessageText'
                edit_data = {
                    'chat_id': chat_id,
                    'message_id': message_id,
                    'text': formatted,
                    'reply_markup': get_pagination_keyboard(new_page, total_pages, is_admin)
                }
                req = urllib.request.Request(
                    edit_url,
                    data=json.dumps(edit_data).encode(),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                urllib.request.urlopen(req)
        # Category filter
        elif data.startswith('cat_'):
            category = data[4:] if data != 'cat_all' else None
            rows = db('SELECT id, savol, javob, javob_type, category FROM data' + (' WHERE category=%s' if category else ''), 
                      (category,) if category else ())
            formatted, total_pages = format_data(rows)
            pagination_states[chat_id] = (0, rows)
            edit_url = BASE_URL + 'editMessageText'
            edit_data = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': formatted,
                'reply_markup': get_pagination_keyboard(0, total_pages, is_admin)
            }
            req = urllib.request.Request(
                edit_url,
                data=json.dumps(edit_data).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            urllib.request.urlopen(req)
        # Delete confirmation
        elif data.startswith('delete_confirm_'):
            if not is_admin:
                send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
                return
            try:
                id_to_delete = int(data.split('_')[2])
                row = db('SELECT savol FROM data WHERE id=%s', (id_to_delete,), fetchall=False)
                if row:
                    db('DELETE FROM data WHERE id=%s', (id_to_delete,))
                    send_message(chat_id, f'O‘chirildi: {row["savol"]}', reply_markup=get_main_keyboard(is_admin))
                else:
                    send_message(chat_id, f'ID {id_to_delete} topilmadi.', reply_markup=get_main_keyboard(is_admin))
            except ValueError:
                send_message(chat_id, 'ID noto‘g‘ri!', reply_markup=get_main_keyboard(is_admin))
        elif data == 'delete_cancel':
            send_message(chat_id, 'O‘chirish bekor qilindi.', reply_markup=get_main_keyboard(is_admin))
        return

    if 'message' not in update:
        return
    msg = update['message']
    chat_id = msg['chat']['id']
    text = msg.get('text', '').strip()
    user_id = msg['from']['id']
    username = msg['from'].get('username', '')
    first_name = msg['from'].get('first_name', '')
    is_admin = (user_id in ADMIN_IDS)

    update_user_stats(user_id, username, first_name)

    # /start
    if text == '/start':
        reply = 'Salom!\n/info - Ma\'lumotlarni ko‘rish\n/search_savol - Savol bo\'yicha qidiruv\n/search_javob - Javob bo\'yicha qidiruv\n/feedback - Fikr bildirish\nQidiruv uchun so‘z kiriting'
        if is_admin:
            reply += '\n/add - Yangi qo‘shish\n/edit - Tahrirlash\n/delete - O‘chirish\n/stats - Statistika\n/broadcast - Omma xabari\n/export - Ma\'lumotlarni eksport qilish\n/import - Ma\'lumotlarni import qilish\n/view_feedback - Feedbacklarni ko‘rish'
        send_message(chat_id, reply, reply_markup=get_main_keyboard(is_admin))

    # /info with category filter
    elif text == '/info':
        send_message(chat_id, 'Kategoriyani tanlang:', reply_markup=get_category_keyboard())

    # /search_savol
    elif text == '/search_savol':
        send_message(chat_id, 'Savol bo\'yicha qidiruv uchun so‘z kiriting:', reply_markup={'remove_keyboard': True})
        state[chat_id] = ('search_savol',)

    # /search_javob
    elif text == '/search_javob':
        send_message(chat_id, 'Javob bo\'yicha qidiruv uchun so‘z kiriting:', reply_markup={'remove_keyboard': True})
        state[chat_id] = ('search_javob',)

    # /add (admin only)
    elif text == '/add':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        send_message(chat_id, 'Savolni kiriting:', reply_markup={'remove_keyboard': True})
        state[chat_id] = ('add_savol',)

    # /edit (admin only)
    elif text == '/edit':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        rows = db('SELECT id, savol, javob, javob_type, category FROM data')
        if rows:
            formatted, total_pages = format_data(rows)
            pagination_states[chat_id] = (0, rows)
            send_message(chat_id, 'Tahrirlash uchun ID kiriting:\n' + formatted,
                         reply_markup=get_pagination_keyboard(0, total_pages, is_admin))
            state[chat_id] = ('edit_id',)
        else:
            send_message(chat_id, 'Ma\'lumotlar topilmadi.', reply_markup=get_main_keyboard(is_admin))

    # /delete (admin only)
    elif text == '/delete':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        rows = db('SELECT id, savol, javob, javob_type, category FROM data')
        if rows:
            formatted, total_pages = format_data(rows)
            pagination_states[chat_id] = (0, rows)
            send_message(chat_id, 'O‘chirish uchun ID kiriting:\n' + formatted,
                         reply_markup=get_pagination_keyboard(0, total_pages, is_admin))
            state[chat_id] = ('delete',)
        else:
            send_message(chat_id, 'Ma\'lumotlar topilmadi.', reply_markup=get_main_keyboard(is_admin))

    # /stats (admin only)
    elif text == '/stats':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        send_message(chat_id, format_stats(), reply_markup=get_main_keyboard(is_admin))

    # /broadcast (admin only)
    elif text == '/broadcast':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        send_message(chat_id, 'Omma xabarini kiriting:', reply_markup={'remove_keyboard': True})
        state[chat_id] = ('broadcast',)

    # /export (admin only)
    elif text == '/export':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        success, message = export_data()
        send_message(chat_id, message, reply_markup=get_main_keyboard(is_admin))

    # /import (admin only)
    elif text == '/import':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        success, message = import_data()
        send_message(chat_id, message, reply_markup=get_main_keyboard(is_admin))

    # /feedback
    elif text == '/feedback':
        send_message(chat_id, 'Iltimos, fikringizni yozing:', reply_markup={'remove_keyboard': True})
        state[chat_id] = ('feedback',)

    # /view_feedback (admin only)
    elif text == '/view_feedback':
        if not is_admin:
            send_message(chat_id, 'Faqat admin!', reply_markup=get_main_keyboard(is_admin))
            return
        feedback_rows = db('SELECT id, user_id, feedback_text, created_at FROM feedback')
        formatted = '\n'.join(f'ID: {r["id"]}\nFoydalanuvchi ID: {r["user_id"]}\nFikr: {r["feedback_text"]}\nVaqt: {r["created_at"]}' for r in feedback_rows) or 'Feedback yo‘q.'
        send_message(chat_id, formatted, reply_markup=get_main_keyboard(is_admin))

    # Holatlar boshqaruvi
    elif chat_id in state:
        step = state[chat_id][0]
        if step == 'add_savol':
            savol = text
            send_message(chat_id, 'Kategoriyani kiriting (masalan, "Umumiy", "Texnik", "Sozlamalar"):', reply_markup={'remove_keyboard': True})
            state[chat_id] = ('add_category', savol)
        elif step == 'add_category':
            category = text
            send_message(chat_id, 'Endi javobni kiriting (matn, rasm, video, ovozli xabar yoki audio fayl yuboring):')
            state[chat_id] = ('add_javob', state[chat_id][1], category)
        elif step == 'add_javob':
            javob = text
            javob_type = 'text'
            if 'photo' in msg:
                if isinstance(msg['photo'], list) and msg['photo']:
                    javob = msg['photo'][-1]['file_id']
                    javob_type = 'photo'
                    print(f"Rasm qabul qilindi: file_id={javob}")
                else:
                    send_message(chat_id, 'Rasm noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'video' in msg:
                if 'file_id' in msg['video']:
                    javob = msg['video']['file_id']
                    javob_type = 'video'
                    print(f"Video qabul qilindi: file_id={javob}")
                else:
                    send_message(chat_id, 'Video noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'voice' in msg:
                if 'file_id' in msg['voice']:
                    javob = msg['voice']['file_id']
                    javob_type = 'voice'
                    print(f"Ovozli xabar qabul qilindi: file_id={javob}")
                else:
                    send_message(chat_id, 'Ovozli xabar noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'audio' in msg:
                if 'file_id' in msg['audio']:
                    javob = msg['audio']['file_id']
                    javob_type = 'audio'
                    print(f"Audio qabul qilindi: file_id={javob}")
                else:
                    send_message(chat_id, 'Audio noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            savol, category = state[chat_id][1], state[chat_id][2]
            db('INSERT INTO data (savol, javob, javob_type, category) VALUES (%s, %s, %s, %s)', (savol, javob, javob_type, category))
            send_message(chat_id, 'Muvaffaqiyatli qo‘shildi!', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]
        elif step == 'edit_id':
            try:
                id_to_edit = int(text)
                row = db('SELECT savol, javob, javob_type, category FROM data WHERE id=%s', (id_to_edit,), fetchall=False)
                if row:
                    send_message(chat_id, f'Tahrirlash uchun yangi savolni kiriting (eski savol: {row["savol"]}):',
                                 reply_markup={'remove_keyboard': True})
                    state[chat_id] = ('edit_savol', id_to_edit, row['javob'], row['javob_type'], row['category'])
                else:
                    send_message(chat_id, f'ID {id_to_edit} topilmadi.', reply_markup=get_main_keyboard(is_admin))
                    del state[chat_id]
            except ValueError:
                send_message(chat_id, 'Iltimos, faqat raqamli ID kiriting.', reply_markup=get_main_keyboard(is_admin))
                del state[chat_id]
        elif step == 'edit_savol':
            savol = text
            id_to_edit = state[chat_id][1]
            old_javob = state[chat_id][2]
            old_javob_type = state[chat_id][3]
            old_category = state[chat_id][4]
            send_message(chat_id, f'Yangi kategoriyani kiriting (eski kategoriya: {old_category}):')
            state[chat_id] = ('edit_category', id_to_edit, savol, old_javob, old_javob_type)
        elif step == 'edit_category':
            category = text
            id_to_edit = state[chat_id][1]
            savol = state[chat_id][2]
            old_javob = state[chat_id][3]
            old_javob_type = state[chat_id][4]
            send_message(chat_id, f'Endi yangi javobni kiriting (eski javob: {old_javob}, turi: {old_javob_type}):')
            state[chat_id] = ('edit_javob', id_to_edit, savol, category, old_javob_type)
        elif step == 'edit_javob':
            javob = text
            javob_type = 'text'
            if 'photo' in msg:
                if isinstance(msg['photo'], list) and msg['photo']:
                    javob = msg['photo'][-1]['file_id']
                    javob_type = 'photo'
                    print(f"Rasm tahrirlandi: file_id={javob}")
                else:
                    send_message(chat_id, 'Rasm noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'video' in msg:
                if 'file_id' in msg['video']:
                    javob = msg['video']['file_id']
                    javob_type = 'video'
                    print(f"Video tahrirlandi: file_id={javob}")
                else:
                    send_message(chat_id, 'Video noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'voice' in msg:
                if 'file_id' in msg['voice']:
                    javob = msg['voice']['file_id']
                    javob_type = 'voice'
                    print(f"Ovozli xabar tahrirlandi: file_id={javob}")
                else:
                    send_message(chat_id, 'Ovozli xabar noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            elif 'audio' in msg:
                if 'file_id' in msg['audio']:
                    javob = msg['audio']['file_id']
                    javob_type = 'audio'
                    print(f"Audio tahrirlandi: file_id={javob}")
                else:
                    send_message(chat_id, 'Audio noto‘g‘ri formatda, iltimos qayta urinib ko‘ring.', reply_markup=get_main_keyboard(is_admin))
                    return
            id_to_edit = state[chat_id][1]
            savol = state[chat_id][2]
            category = state[chat_id][3]
            db('UPDATE data SET savol=%s, javob=%s, javob_type=%s, category=%s WHERE id=%s', (savol, javob, javob_type, category, id_to_edit))
            send_message(chat_id, 'Muvaffaqiyatli tahrirlandi!', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]
        elif step == 'delete':
            try:
                id_to_delete = int(text)
                row = db('SELECT savol FROM data WHERE id=%s', (id_to_delete,), fetchall=False)
                if row:
                    send_message(chat_id, f'O‘chirishni tasdiqlang: {row["savol"]}', reply_markup=get_delete_confirmation_keyboard(id_to_delete))
                else:
                    send_message(chat_id, f'ID {id_to_delete} topilmadi.', reply_markup=get_main_keyboard(is_admin))
                del state[chat_id]
            except ValueError:
                send_message(chat_id, 'Iltimos, faqat raqamli ID kiriting.', reply_markup=get_main_keyboard(is_admin))
                del state[chat_id]
        elif step == 'broadcast':
            broadcast_text = text
            users = get_all_users()
            if users:
                for user in users:
                    try:
                        send_message(user['user_id'], broadcast_text)
                    except:
                        pass
                send_message(chat_id, 'Omma xabari yuborildi!', reply_markup=get_main_keyboard(is_admin))
            else:
                send_message(chat_id, 'Foydalanuvchilar topilmadi.', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]
        elif step == 'feedback':
            feedback_text = text
            db('INSERT INTO feedback (user_id, feedback_text) VALUES (%s, %s)', (user_id, feedback_text))
            send_message(chat_id, 'Fikringiz uchun rahmat!', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]
        elif step == 'search_savol':
            term = '%' + text + '%'
            rows = db('SELECT id, savol, javob, javob_type, category FROM data WHERE savol LIKE %s', (term,))
            if rows:
                for row in rows:
                    javob_type = row['javob_type'] or 'text'
                    if javob_type == 'text':
                        send_message(chat_id, f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}\nJavob: {row["javob"]}')
                    elif javob_type == 'photo':
                        send_photo(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'video':
                        send_video(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'voice':
                        send_voice(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'audio':
                        send_audio(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
            else:
                send_message(chat_id, 'Hech narsa topilmadi.')
            send_message(chat_id, 'Qidiruv tugadi.', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]
        elif step == 'search_javob':
            term = '%' + text + '%'
            rows = db('SELECT id, savol, javob, javob_type, category FROM data WHERE javob LIKE %s', (term,))
            if rows:
                for row in rows:
                    javob_type = row['javob_type'] or 'text'
                    if javob_type == 'text':
                        send_message(chat_id, f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}\nJavob: {row["javob"]}')
                    elif javob_type == 'photo':
                        send_photo(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'video':
                        send_video(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'voice':
                        send_voice(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                    elif javob_type == 'audio':
                        send_audio(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
            else:
                send_message(chat_id, 'Hech narsa topilmadi.')
            send_message(chat_id, 'Qidiruv tugadi.', reply_markup=get_main_keyboard(is_admin))
            del state[chat_id]

    # Standart qidiruv
    else:
        term = '%' + text + '%'
        rows = db('SELECT id, savol, javob, javob_type, category FROM data WHERE savol LIKE %s OR javob LIKE %s', (term, term))
        if rows:
            for row in rows:
                javob_type = row['javob_type'] or 'text'
                if javob_type == 'text':
                    send_message(chat_id, f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}\nJavob: {row["javob"]}')
                elif javob_type == 'photo':
                    send_photo(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                elif javob_type == 'video':
                    send_video(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                elif javob_type == 'voice':
                    send_voice(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
                elif javob_type == 'audio':
                    send_audio(chat_id, row['javob'], caption=f'ID: {row["id"]}\nKategoriya: {row["category"]}\nSavol: {row["savol"]}')
        else:
            send_message(chat_id, 'Hech narsa topilmadi.')
        send_message(chat_id, 'Qidiruv tugadi.', reply_markup=get_main_keyboard(is_admin))

# Webhook endpoint
state = {}
pagination_states = {}

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = json.loads(json_string)
        process_update(update)
        return '', 200
    else:
        abort(403)

# Asosiy ishga tushirish
if __name__ == '__main__':
    init_db()
    set_webhook()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
