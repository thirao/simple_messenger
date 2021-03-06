import sqlite3
import uuid

#アカウント管理
class AccountDao:
    dbname = 'account.db'
    def __init__(self):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        # アカウント管理テーブル
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
        cur.execute("SELECT name FROM account WHERE name=? AND password=?;", (user, password,))
        result = cur.fetchall()
        conn.close()
        if len(result) != 0:
            return True
        else:
            return False

    def is_exist_user(self, user):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT name FROM account WHERE name=?;", (user,))
        result = cur.fetchall()
        conn.close()
        if len(result) != 0:
            return True
        else:
            return False

# アカウント全件取得
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
        cur.execute("CREATE TABLE IF NOT EXISTS friends(my_user, your_user);")
        conn.commit()
        conn.close()

# 友人リスト取得
    def get_friend_list(self, username):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("SELECT * FROM friends WHERE my_user = ? ;", (username,))
        result = cur.fetchall()
        conn.close()
        return result

# 友人リスト登録
    def set_friend_list(self, from_user, to_user):
        conn = sqlite3.connect(self.dbname)
        cur = conn.cursor()
        cur.execute("INSERT INTO friends VALUES (?,?);", (from_user, to_user,))
        conn.commit()
        conn.close()


if __name__ == "__main__":
    a = AccountDao()
    print(a.get_all_account())
    b = MessageDao()
    for x in range(10):
        m = {
            "from": "thirao2",
            "to": "thirao",
            "message": "てすと",
            "date": str(1523348346672 + x)
        }
        b.set_message(m)


    # print(b.set_message(m))
    print(b.get_message())
