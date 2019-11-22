from instagrim.db import get_db
class Post:

    def __init__(self, id, imagefile, user_id, message, date, likes):
        db = get_db()
        c = db.cursor()
        c.execute('''SELECT * FROM users WHERE id=?''', (str(user_id), ))
        user = c.fetchone()['username']

        self.id = id
        self.imagefile = imagefile
        self.username = user
        self.message = message
        self.date = date
        self.likes = likes


def create_post(entry, likes=0):
    return Post(entry['id'], entry['url'], entry['user_id'], entry['message'], entry['date'], likes)
