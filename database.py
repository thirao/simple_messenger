import sqlite3
import uuid

#アカウント管理
class AccountDao:
    dbname = 'account.db'
    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS account(id, name, password);")
        conn.commit()
        conn.close()

    # アカウント作成
    def create_account(self, user, password):
        import uuid
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        uid = uuid.uuid4()
        print(uid)
        if self.is_account(user, password):
            return "Error"
        else:
            pass

        cur.execute("INSERT INTO account VALUES (?,?,?);", (str(uid), str(user), str(password),))
        conn.commit()
        conn.close()

    # アカウント認証
    def is_account(self, user, password):
        import uuid
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        uid = uuid.uuid4()

        cur.execute("SELECT name FROM account WHERE name=? AND password=?;", (user, password,))
        result = cur.fetchall()
        conn.close()
        if len(result) != 0:
            return True
        else:
            return False

# 全件取得
    def get_all_account(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM account;")
        result = cur.fetchall()
        conn.close()
        return result


# メッセージIO管理
class MessageDao:
    dbname = 'messages.db'
    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS messages(m_from, m_to, message, date);")
        conn.commit()
        conn.close()

    def get_message_by_name(self, username):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages WHERE m_to = ? OR m_from = ?;", (username, username, ))
        result = cur.fetchall()
        r = [{"from": x[0], "to": x[1], "message": x[2], "date": x[3]} for x in result]
        conn.close()
        return r

    def set_message(self, message):
        if not message.get('from', False) and message.get('to', False) and message.get('date', False) and message.get('message', False):
            return "Error"

        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO messages VALUES (?,?,?,?);",
            (message['from'], message['to'], message['message'], str(message['date']))
        )
        conn.commit()
        conn.close()

    def get_message(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages;")
        result = cur.fetchall()
        conn.close()
        return result


# フレンドリスト管理
class FriendDao:
    dbname = 'account.db'
    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS friends(m_from, m_to, message, date);")
        conn.commit()
        conn.close()


if __name__ =="__main__":
    a = AccountDao()

    a.create_account('thirao','1111')
    print(a.get_all_account())

    m = {
        "from": "thirao",
        "to": "thirao2",
        "message": "てすと",
        "date": "1523348346.672"
    }

    b = MessageDao()
    print(b.set_message(m))
    print(b.get_message_by_name('thirao'))
