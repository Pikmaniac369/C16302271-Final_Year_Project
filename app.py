from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
# Might use Flask Bootstrap

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectDB.db'
db = SQLAlchemy(app)

'''
class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    userEmail = db.Column(db.String(50)) <--> Do I need this?

    def __repr__(self):
        return '<User %r>' % self.userID
'''

class Character(db.Model):
    cID = db.Column(db.Integer, primary_key=True)
    cName = db.Column(db.String(100), nullable=False)
    cAge = db.Column(db.Integer)
    # Don't know how to use Enums yet. Will be implemented once I do.
    #cGender = db.Column(db.Enum('Male', 'Female', 'Other'), default='Male')
    cRace = db.Column(db.String(20))# Will change to a list at a later date
    cDesc = db.Column(db.String(100000))
    cStr = db.Column(db.Integer, default=8)
    cDex = db.Column(db.Integer, default=8)
    cCon = db.Column(db.Integer, default=8)
    cInt = db.Column(db.Integer, default=8)
    cWis = db.Column(db.Integer, default=8)
    cCha = db.Column(db.Integer, default=8)

    def __repr__(self):
        return '<Character %r>' % self.cID

class Weapon(db.Model):
    wID = db.Column(db.Integer, primary_key=True)
    wName = db.Column(db.String(100), nullable=False)
    wType = db.Column(db.String(50))# Will change to a list of weapon types at a later time
    wDamage = db.Column(db.String(50))# Will change to a list of damage types at a later time
    wDice = db.Column(db.String(10))# Will change to a list of dice types at a later time
    wDesc = db.Column(db.String(100000))
    # Might add a boolean for 'Magical Weapon?' at a later time

    def __repr__(self):
        return '<Weapon %r>' % self.wID

class Armour(db.Model):
    aID = db.Column(db.Integer, primary_key=True)
    aName = db.Column(db.String(100), nullable=False)
    aType = db.Column(db.String(50))# Will change to a list of armour types at a later date
    aBase = db.Column(db.Integer)
    # aDexYN = db.Column(db.Boolean) Does the armour use the DEX modifier
    # aMod = db.Column(db.Integer) The maximum DEX mod to apply if it uses it
    aDesc = db.Column(db.String(100000))

    def __repr__(self):
        return '<Armour %r>' % self.aID

class Location(db.Model):
    lID = db.Column(db.Integer, primary_key=True)
    lName = db.Column(db.String(100), nullable=False)
    lDesc = db.Column(db.String(100000))

    def __repr__(self):
        return '<Location %r>' % self.lID

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/characters.html', methods=['POST', 'GET'])
def characters():
    if request.method == 'POST':
        c_Name = request.form['cName']
        c_Age = request.form['cAge']
        c_Race = request.form['cRace']
        c_Desc = request.form['cDesc']
        c_Str = request.form['cStr']
        c_Dex = request.form['cDex']
        c_Con = request.form['cCon']
        c_Int = request.form['cInt']
        c_Wis = request.form['cWis']
        c_Cha = request.form['cCha']

        new_character = Character(cName=c_Name, cAge=c_Age, cRace=c_Race, cDesc=c_Desc, cStr=c_Str, cDex=c_Dex, cCon=c_Con, cInt=c_Int, cWis=c_Wis, cCha=c_Cha)

        try:
            db.session.add(new_character)
            db.session.commit()
            return redirect('/characters.html')
        except:
            return 'There was an issue adding your character to the database.'
    else:
        characters = Character.query.order_by(Character.cID).all()
        return render_template('characters.html', characters=characters)

@app.route('/deleteCharacter/<int:id>')
def deleteCharacter(id):
    character_to_delete = Character.query.get_or_404(id)

    try:
        db.session.delete(character_to_delete)
        db.session.commit()
        return redirect('/characters.html')
    except:
        return 'There was a problem deleting your character.'

@app.route('/updateCharacter/<int:id>', methods=['GET', 'POST'])
def updateCharacter(id):
    character = Character.query.get_or_404(id)

    if request.method == 'POST':
        character.cName = request.form['cName']
        character.cAge = request.form['cAge']
        character.cRace = request.form['cRace']
        character.cDesc = request.form['cDesc']
        character.cStr = request.form['cStr']
        character.cDex = request.form['cDex']
        character.cCon = request.form['cCon']
        character.cInt = request.form['cInt']
        character.cWis = request.form['cWis']
        character.cCha = request.form['cCha']

        try:
            db.session.commit()
            return redirect('/characters.html')
        except:
            return 'There was a problem updating your character.'
    else:
        return render_template('updateCharacter.html', character=character)


@app.route('/weapons.html')
def weapons():
    if request.method == 'POST':
        w_Name = request.form['wName']
        w_Type = request.form['wType']
        w_Damage = request.form['wDamage']
        w_Dice = request.form['wDice']
        w_Desc = request.form['wDesc']

        new_weapon = Weapon(wName=w_Name, wType=w_Type, wDamage=w_Damage, wDice=w_Dice, wDesc=w_Desc)

        try:
            db.session.add(new_weapon)
            db.session.commit()
            return redirect('/weapons.html')
        except:
            return 'There was an issue adding your weapon to the database.'
    else:
        weapons = Weapon.query.order_by(Weapon.wID).all()
        return render_template('weapons.html', weapons=weapons)

@app.route('/armours.html')
def armours():
    return render_template('armours.html')

@app.route('/locations.html')
def locations():
    return render_template('locations.html')

if __name__ == "__main__":
    app.run(debug=True)