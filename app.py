import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.utils import secure_filename
# Might use Flask Bootstrap

UPLOAD_FOLDER = 'static/Images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# Configure the upload folder:
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure the database:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectDB.db'
db = SQLAlchemy(app)

'''
# User Table:
class User(db.Model):
    userID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    userEmail = db.Column(db.String(50)) <--> Do I need this?

    def __repr__(self):
        return '<User %r>' % self.userID
'''
# Character Table:
class Character(db.Model):
    cID = db.Column(db.Integer, primary_key=True)
    cPicPath = db.Column(db.String(100000))# The path to the character photo in the images directory
    cName = db.Column(db.String(100), nullable=False)# Name of the character
    cAge = db.Column(db.Integer)# Age of the character
    cGender = db.Column(db.String(20))# The character's gender
    cRace = db.Column(db.String(20))# Will change to a list of races at a later date, i.e. Human, Elf, Dwarf, Halfling, etc.
    cClass = db.Column(db.String(50))# The character's class, chosen from a list.
    cDesc = db.Column(db.String(100000))# Description of the character, i.e. appearance, backstory
    cStr = db.Column(db.Integer, default=8)# The character's Strength stat
    cDex = db.Column(db.Integer, default=8)# The character's Dexterity stat
    cCon = db.Column(db.Integer, default=8)# The character's Constitution stat
    cInt = db.Column(db.Integer, default=8)# The character's Intelligence stat
    cWis = db.Column(db.Integer, default=8)# The character's Wisdom stat
    cCha = db.Column(db.Integer, default=8)# The character's Charisma stat

    def __repr__(self):
        return '<Character %r>' % self.cID

# Weapon Table:
class Weapon(db.Model):
    wID = db.Column(db.Integer, primary_key=True)
    wName = db.Column(db.String(100), nullable=False)# Name of the weapon
    wType = db.Column(db.String(50))# Will change to a list of weapon types at a later time, i.e. simple, martial
    wDamage = db.Column(db.String(50))# Will change to a list of damage types at a later time, i.e. bludgeoning, piercing, slashing, etc.
    wDice = db.Column(db.String(10))# Will change to a list of dice types at a later time, i.e. d4, d6, d8, d10, d12.
    # wMagic = db.Column(db.Boolean) Is the weapon magical.
    wDesc = db.Column(db.String(100000))# Description of the weapon, i.e. appearance, effects, magic effects.

    def __repr__(self):
        return '<Weapon %r>' % self.wID

# Armour Table:
class Armour(db.Model):
    aID = db.Column(db.Integer, primary_key=True)
    aName = db.Column(db.String(100), nullable=False)# Name of the armour.
    aType = db.Column(db.String(50))# Will change to a list of armour types at a later date, i.e. light, medium, heavy.
    aBase = db.Column(db.Integer)# Base Armour Class (AC).
    # aDexYN = db.Column(db.Boolean) Does the armour use the DEX modifier.
    # aMod = db.Column(db.Integer) The maximum DEX mod to apply if it uses it.
    # aMagic = db.Column(db.Boolean) Is the armour magical.
    aDesc = db.Column(db.String(100000))# Description of the armour, i.e. appearance, effects, magic effects.

    def __repr__(self):
        return '<Armour %r>' % self.aID

# Location Table:
# Maybe add more info, such as number of shops, list of factions, etc.
class Location(db.Model):
    lID = db.Column(db.Integer, primary_key=True)
    lName = db.Column(db.String(100), nullable=False)# Name of the location.
    lDesc = db.Column(db.String(100000))# Description of the location.

    def __repr__(self):
        return '<Location %r>' % self.lID

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

# Character-related functionality:
@app.route('/characters.html', methods=['POST', 'GET'])
def characters():
    if request.method == 'POST':
        c_Pic = request.files['cPic']
        c_Name = request.form['cName']
        c_Age = request.form['cAge']
        c_Gender = request.form['cGender']
        c_Race = request.form['cRace']
        c_Class = request.form['cClass']
        c_Desc = request.form['cDesc']
        c_Str = request.form['cStr']
        c_Dex = request.form['cDex']
        c_Con = request.form['cCon']
        c_Int = request.form['cInt']
        c_Wis = request.form['cWis']
        c_Cha = request.form['cCha']

        filename = secure_filename(c_Pic.filename)
        c_Pic_Path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if c_Pic and allowed_file(c_Pic.filename):
            c_Pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_character = Character(cPicPath=c_Pic_Path, cName=c_Name, cAge=c_Age, cGender=c_Gender, cRace=c_Race, cClass=c_Class, cDesc=c_Desc, cStr=c_Str, cDex=c_Dex, cCon=c_Con, cInt=c_Int, cWis=c_Wis, cCha=c_Cha)

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
        character.cGender = request.form['cGender']
        character.cRace = request.form['cRace']
        character.cClass = request.form['cClass']
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

# Weapon-related functionality:
@app.route('/weapons.html', methods=['POST', 'GET'])
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

@app.route('/deleteWeapon/<int:id>')
def deleteWeapon(id):
    weapon_to_delete = Weapon.query.get_or_404(id)

    try:
        db.session.delete(weapon_to_delete)
        db.session.commit()
        return redirect('/weapons.html')
    except:
        return 'There was a problem deleting your weapon.'

@app.route('/updateWeapon/<int:id>', methods=['GET', 'POST'])
def updateWeapon(id):
    weapon = Weapon.query.get_or_404(id)

    if request.method == 'POST':
        weapon.wName = request.form['wName']
        weapon.wType = request.form['wType']
        weapon.wDamage = request.form['wDamage']
        weapon.wDice = request.form['wDice']
        weapon.wDesc = request.form['wDesc']

        try:
            db.session.commit()
            return redirect('/weapons.html')
        except:
            return 'There was a problem updating your weapon.'
    else:
        return render_template('updateWeapon.html', weapon=weapon)

# Armour-related functionality:
@app.route('/armours.html', methods=['POST', 'GET'])
def armours():
    if request.method == 'POST':
        a_Name = request.form['aName']
        a_Type = request.form['aType']
        a_Base = request.form['aBase']
        a_Desc = request.form['aDesc']

        new_armour = Armour(aName=a_Name, aType=a_Type, aBase=a_Base, aDesc=a_Desc)

        try:
            db.session.add(new_armour)
            db.session.commit()
            return redirect('/armours.html')
        except:
            return 'There was an issue adding your armour to the database.'
    else:
        armours = Armour.query.order_by(Armour.aID).all()
        return render_template('armours.html', armours=armours)

@app.route('/deleteArmour/<int:id>')
def deleteArmour(id):
    armour_to_delete = Armour.query.get_or_404(id)

    try:
        db.session.delete(armour_to_delete)
        db.session.commit()
        return redirect('/armours.html')
    except:
        return 'There was a problem deleting your armour.'

@app.route('/updateArmour/<int:id>', methods=['GET', 'POST'])
def updateArmour(id):
    armour = Armour.query.get_or_404(id)

    if request.method == 'POST':
        armour.aName = request.form['aName']
        armour.aType = request.form['aType']
        armour.aBase = request.form['aBase']
        armour.aDesc = request.form['aDesc']

        try:
            db.session.commit()
            return redirect('/armours.html')
        except:
            return 'There was a problem updating your armour.'
    else:
        return render_template('updateArmour.html', armour=armour)

# Location-related functionality:
@app.route('/locations.html', methods=['POST', 'GET'])
def locations():
    if request.method == 'POST':
        l_Name = request.form['lName']
        l_Desc = request.form['lDesc']

        new_location = Location(lName=l_Name, lDesc=l_Desc)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect('/locations.html')
        except:
            return 'There was an issue adding your location to the database.'
    else:
        locations = Location.query.order_by(Location.lID).all()
        return render_template('locations.html', locations=locations)

@app.route('/deleteLocation/<int:id>')
def deleteLocation(id):
    location_to_delete = Location.query.get_or_404(id)

    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect('/locations.html')
    except:
        return 'There was a problem deleting your location.'

@app.route('/updateLocation/<int:id>', methods=['GET', 'POST'])
def updateLocation(id):
    location = Location.query.get_or_404(id)

    if request.method == 'POST':
        location.lName = request.form['lName']
        location.lDesc = request.form['lDesc']

        try:
            db.session.commit()
            return redirect('/locations.html')
        except:
            return 'There was a problem updating your location.'
    else:
        return render_template('updateLocation.html', location=location)

# Run the app in debug mode:
if __name__ == "__main__":
    app.run(debug=True)