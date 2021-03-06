import os
from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Length

UPLOAD_FOLDER = 'static/User_Images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
# Install the Bootstrap extension
Bootstrap(app)
# Configure the Secret Key
app.config['SECRET_KEY'] = 'thiskeyissosecretthateveniwillprobablyforgetitxyz'
# Configure the upload folder:
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Configure the database:
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///projectDB.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User Table:
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    characters = db.relationship('Character', backref='creator')
    weapons = db.relationship('Weapon', backref='creator')
    armours = db.relationship('Armour', backref='creator')
    locations = db.relationship('Location', backref='creator')

    def __repr__(self):
        return '<User %r>' % self.id

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
    creatorID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Character %r>' % self.cID

# Weapon Table:
class Weapon(db.Model):
    wID = db.Column(db.Integer, primary_key=True)
    wPicPath = db.Column(db.String(100000))# The path to the weapon picture in the images directory
    wName = db.Column(db.String(100), nullable=False)# Name of the weapon
    wType = db.Column(db.String(50))# Will change to a list of weapon types at a later time, i.e. simple, martial
    wDamage = db.Column(db.String(50))# Will change to a list of damage types at a later time, i.e. bludgeoning, piercing, slashing, etc.
    wDice = db.Column(db.String(10))# Will change to a list of dice types at a later time, i.e. d4, d6, d8, d10, d12.
    # wMagic = db.Column(db.Boolean) Is the weapon magical.
    wDesc = db.Column(db.String(100000))# Description of the weapon, i.e. appearance, effects, magic effects.
    creatorID = db.Column(db.Integer, db.ForeignKey('user.id'))

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
    creatorID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Armour %r>' % self.aID

# Location Table:
# Maybe add more info, such as number of shops, list of factions, etc.
class Location(db.Model):
    lID = db.Column(db.Integer, primary_key=True)
    lName = db.Column(db.String(100), nullable=False)# Name of the location.
    lDesc = db.Column(db.String(100000))# Description of the location.
    creatorID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Location %r>' % self.lID

# Load the user:
@login_manager.user_loader
def load_user(id):
    user = User.query.get_or_404(id)
    return user

class LoginForm(FlaskForm):
    uName = StringField('Username', validators=[InputRequired()])
    pwd = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    rememberUser = BooleanField('Stay Logged In')

class SignUpForm(FlaskForm):
    uName = StringField('Username', validators=[InputRequired()])
    pwd = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
 

# Check that the file's extension is allowed
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html', methods=['POST', 'GET'])
def login():
    loginForm = LoginForm()

    if loginForm.validate_on_submit():
        userSearch = User.query.filter_by(username=loginForm.uName.data).first()
        if userSearch:
            if check_password_hash(userSearch.password, loginForm.pwd.data):
                login_user(userSearch, remember=loginForm.rememberUser.data)
                return redirect('/dashboard.html')
    
    return render_template('login.html', form=loginForm)

@app.route('/signup.html', methods=['POST', 'GET'])
def signup():
    signupForm = SignUpForm()

    if signupForm.validate_on_submit():
        hashPwd = generate_password_hash(signupForm.pwd.data, method='sha256')
        newUser = User(username=signupForm.uName.data, password=hashPwd)

        try:
            db.session.add(newUser)
            db.session.commit()
            return redirect('/login.html')
        except:
            return 'There was an issue adding you to the database.'
    
    return render_template('signup.html', form=signupForm)


@app.route('/dashboard.html')
@login_required
def dashboard():
    return render_template('dashboard.html')

# Character-related functionality:
@app.route('/characters.html', methods=['POST', 'GET'])
@login_required
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

        # Edit Character's Stats based on Race/Subrace
        if c_Race == "Dragonborn":
            c_Str = int(c_Str) + 2
            c_Cha = int(c_Cha) + 1
        elif c_Race == "Gray Dwarf (Duergar)":
            c_Str = int(c_Str) + 1
            c_Con = int(c_Con) + 2
        elif c_Race == "Hill Dwarf":
            c_Con = int(c_Con) + 2
            c_Wis = int(c_Wis) + 1
        elif c_Race == "Mountain Dwarf":
            c_Str = int(c_Str) + 2
            c_Con = int(c_Con) + 2
        elif c_Race == "Dark Elf (Drow)":
            c_Dex = int(c_Dex) + 2
            c_Cha = int(c_Cha) + 1
        elif c_Race == "High Elf":
            c_Dex = int(c_Dex) + 2
            c_Int = int(c_Int) + 1
        elif c_Race == "Wood Elf":
            c_Dex = int(c_Dex) + 2
            c_Wis = int(c_Wis) + 1
        elif c_Race == "Deep Gnome (Svirfneblin)":
            c_Dex = int(c_Dex) + 1
            c_Int = int(c_Int) + 1
        elif c_Race == "Forest Gnome":
            c_Dex = int(c_Dex) + 1
            c_Int = int(c_Int) + 1
        elif c_Race == "Rock Gnome":
            c_Con = int(c_Con) + 1
            c_Int = int(c_Int) + 1
        elif c_Race == "Half-Elf":
            c_Dex = int(c_Dex) + 1
            c_Int = int(c_Int) + 1
            c_Cha = int(c_Cha) + 2
        elif c_Race == "Lightfoot Halfling":
            c_Dex = int(c_Dex) + 2
            c_Cha = int(c_Cha) + 1
        elif c_Race == "Stout Halfling":
            c_Dex = int(c_Dex) + 2
            c_Con = int(c_Con) + 1
        elif c_Race == "Half-Orc":
            c_Str = int(c_Str) + 2
            c_Con = int(c_Con) + 1
        elif c_Race == "Human":
            c_Str = int(c_Str) + 1
            c_Dex = int(c_Dex) + 1
            c_Con = int(c_Con) + 1
            c_Int = int(c_Int) + 1
            c_Wis = int(c_Wis) + 1
            c_Cha = int(c_Cha) + 1
        elif c_Race == "Tiefling":
            c_Int = int(c_Int) + 1
            c_Cha = int(c_Cha) + 2

        new_character = Character(creatorID=current_user.id, cPicPath=c_Pic_Path, cName=c_Name, cAge=c_Age, cGender=c_Gender, cRace=c_Race, cClass=c_Class, cDesc=c_Desc, cStr=c_Str, cDex=c_Dex, cCon=c_Con, cInt=c_Int, cWis=c_Wis, cCha=c_Cha)

        try:
            db.session.add(new_character)
            db.session.commit()
            return redirect('/characters.html')
        except:
            return 'There was an issue adding your character to the database.'
    else:
        characters = Character.query.filter_by(creatorID=current_user.id).order_by(Character.cID).all()
        return render_template('characters.html', characters=characters)

@app.route('/deleteCharacter/<int:id>')
@login_required
def deleteCharacter(id):
    character_to_delete = Character.query.get_or_404(id)

    try:
        db.session.delete(character_to_delete)
        db.session.commit()
        return redirect('/characters.html')
    except:
        return 'There was a problem deleting your character.'

@app.route('/viewCharacter/<int:id>')
@login_required
def viewCharacter(id):
    characterToDisplay = Character.query.get_or_404(id)

    try:
        return render_template('viewCharacter.html', character=characterToDisplay)
    except:
        return 'There was a problem displaying your character.'

@app.route('/updateCharacter/<int:id>', methods=['GET', 'POST'])
@login_required
def updateCharacter(id):
    character = Character.query.get_or_404(id)

    # Remove racial bonus to stats from previous race:
    if character.cRace == "Dragonborn":
        character.cStr = int(character.cStr) - 2
        character.cCha = int(character.cCha) - 1
    elif character.cRace == "Gray Dwarf (Duergar)":
        character.cStr = int(character.cStr) - 1
        character.cCon = int(character.cCon) - 2
    elif character.cRace == "Hill Dwarf":
        character.cCon = int(character.cCon) - 2
        character.cWis = int(character.cWis) - 1
    elif character.cRace == "Mountain Dwarf":
        character.cStr = int(character.cStr) - 2
        character.cCon = int(character.cCon) - 2
    elif character.cRace == "Dark Elf (Drow)":
        character.cDex = int(character.cDex) - 2
        character.cCha = int(character.cCha) - 1
    elif character.cRace == "High Elf":
        character.cDex = int(character.cDex) - 2
        character.cInt = int(character.cInt) - 1
    elif character.cRace == "Wood Elf":
        character.cDex = int(character.cDex) - 2
        character.cWis = int(character.cWis) - 1
    elif character.cRace == "Deep Gnome (Svirfneblin)":
        character.cDex = int(character.cDex) - 1
        character.cInt = int(character.cInt) - 2
    elif character.cRace == "Forest Gnome":
        character.cDex = int(character.cDex) - 1
        character.cInt = int(character.cInt) - 2
    elif character.cRace == "Rock Gnome":
        character.cCon = int(character.cCon) - 1
        character.cInt = int(character.cInt) - 2
    elif character.cRace == "Half-Elf":
        character.cDex = int(character.cDex) - 1
        character.cInt = int(character.cInt) - 1
        character.cCha = int(character.cCha) - 2
    elif character.cRace == "Lightfoot Halfling":
        character.cDex = int(character.cDex) - 2
        character.cCha = int(character.cCha) - 1
    elif character.cRace == "Stout Halfling":
        character.cDex = int(character.cDex) - 2
        character.cCon = int(character.cCon) - 1
    elif character.cRace == "Half-Orc":
        character.cStr = int(character.cStr) - 2
        character.cCon = int(character.cCon) - 1
    elif character.cRace == "Human":
        character.cStr = int(character.cStr) - 1
        character.cDex = int(character.cDex) - 1
        character.cCon = int(character.cCon) - 1
        character.cInt = int(character.cInt) - 1
        character.cWis = int(character.cWis) - 1
        character.cCha = int(character.cCha) - 1
    elif character.cRace == "Tiefling":
        character.cInt = int(character.cInt) - 1
        character.cCha = int(character.cCha) - 2

    if request.method == 'POST':
        c_Pic = request.files['cPic']
        filename = secure_filename(c_Pic.filename)

        if c_Pic and allowed_file(c_Pic.filename):
            c_Pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if c_Pic.filename == "":
            character.cPicPath = character.cPicPath
        else:
            character.cPicPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

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

        # Edit Character's Stats based on Race/Subrace
        if character.cRace == "Dragonborn":
            character.cStr = int(character.cStr) + 2
            character.cCha = int(character.cCha) + 1
        elif character.cRace == "Gray Dwarf (Duergar)":
            character.cStr = int(character.cStr) + 1
            character.cCon = int(character.cCon) + 2
        elif character.cRace == "Hill Dwarf":
            character.cCon = int(character.cCon) + 2
            character.cWis = int(character.cWis) + 1
        elif character.cRace == "Mountain Dwarf":
            character.cStr = int(character.cStr) + 2
            character.cCon = int(character.cCon) + 2
        elif character.cRace == "Dark Elf (Drow)":
            character.cDex = int(character.cDex) + 2
            character.cCha = int(character.cCha) + 1
        elif character.cRace == "High Elf":
            character.cDex = int(character.cDex) + 2
            character.cInt = int(character.cInt) + 1
        elif character.cRace == "Wood Elf":
            character.cDex = int(character.cDex) + 2
            character.cWis = int(character.cWis) + 1
        elif character.cRace == "Deep Gnome (Svirfneblin)":
            character.cDex = int(character.cDex) + 1
            character.cInt = int(character.cInt) + 1
        elif character.cRace == "Forest Gnome":
            character.cDex = int(character.cDex) + 1
            character.cInt = int(character.cInt) + 1
        elif character.cRace == "Rock Gnome":
            character.cCon = int(character.cCon) + 1
            character.cInt = int(character.cInt) + 1
        elif character.cRace == "Half-Elf":
            character.cDex = int(character.cDex) + 1
            character.cInt = int(character.cInt) + 1
            character.cCha = int(character.cCha) + 2
        elif character.cRace == "Lightfoot Halfling":
            character.cDex = int(character.cDex) + 2
            character.cCha = int(character.cCha) + 1
        elif character.cRace == "Stout Halfling":
            character.cDex = int(character.cDex) + 2
            character.cCon = int(character.cCon) + 1
        elif character.cRace == "Half-Orc":
            character.cStr = int(character.cStr) + 2
            character.cCon = int(character.cCon) + 1
        elif character.cRace == "Human":
            character.cStr = int(character.cStr) + 1
            character.cDex = int(character.cDex) + 1
            character.cCon = int(character.cCon) + 1
            character.cInt = int(character.cInt) + 1
            character.cWis = int(character.cWis) + 1
            character.cCha = int(character.cCha) + 1
        elif character.cRace == "Tiefling":
            character.cInt = int(character.cInt) + 1
            character.cCha = int(character.cCha) + 2

        try:
            db.session.commit()
            return redirect('/characters.html')
        except:
            return 'There was a problem updating your character.'
    else:
        return render_template('updateCharacter.html', character=character)

# Weapon-related functionality:
@app.route('/weapons.html', methods=['POST', 'GET'])
@login_required
def weapons():
    if request.method == 'POST':
        w_Pic = request.files['wPic']
        w_Name = request.form['wName']
        w_Type = request.form['wType']
        w_Damage = request.form['wDamage']
        w_Dice = request.form['wDice']
        w_Desc = request.form['wDesc']

        filename = secure_filename(w_Pic.filename)
        w_Pic_Path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if w_Pic and allowed_file(w_Pic.filename):
            w_Pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_weapon = Weapon(creatorID=current_user.id, wPicPath=w_Pic_Path, wName=w_Name, wType=w_Type, wDamage=w_Damage, wDice=w_Dice, wDesc=w_Desc)

        try:
            db.session.add(new_weapon)
            db.session.commit()
            return redirect('/weapons.html')
        except:
            return 'There was an issue adding your weapon to the database.'
    else:
        weapons = Weapon.query.filter_by(creatorID=current_user.id).order_by(Weapon.wID).all()
        return render_template('weapons.html', weapons=weapons)

@app.route('/deleteWeapon/<int:id>')
@login_required
def deleteWeapon(id):
    weapon_to_delete = Weapon.query.get_or_404(id)

    try:
        db.session.delete(weapon_to_delete)
        db.session.commit()
        return redirect('/weapons.html')
    except:
        return 'There was a problem deleting your weapon.'

@app.route('/viewWeapon/<int:id>')
@login_required
def viewWeapon(id):
    weaponToDisplay = Weapon.query.get_or_404(id)

    try:
        return render_template('viewWeapon.html', weapon=weaponToDisplay)
    except:
        return 'There was a problem displaying your weapon.'


@app.route('/updateWeapon/<int:id>', methods=['GET', 'POST'])
@login_required
def updateWeapon(id):
    weapon = Weapon.query.get_or_404(id)

    if request.method == 'POST':
        w_Pic = request.files['wPic']
        filename = secure_filename(w_Pic.filename)

        if w_Pic and allowed_file(w_Pic.filename):
            w_Pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if w_Pic.filename == "":
            weapon.wPicPath = weapon.wPicPath
        else:
            weapon.wPicPath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
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
@login_required
def armours():
    if request.method == 'POST':
        a_Name = request.form['aName']
        a_Type = request.form['aType']
        a_Base = request.form['aBase']
        a_Desc = request.form['aDesc']

        new_armour = Armour(creatorID=current_user.id, aName=a_Name, aType=a_Type, aBase=a_Base, aDesc=a_Desc)

        try:
            db.session.add(new_armour)
            db.session.commit()
            return redirect('/armours.html')
        except:
            return 'There was an issue adding your armour to the database.'
    else:
        armours = Armour.query.filter_by(creatorID=current_user.id).order_by(Armour.aID).all()
        return render_template('armours.html', armours=armours)

@app.route('/deleteArmour/<int:id>')
@login_required
def deleteArmour(id):
    armour_to_delete = Armour.query.get_or_404(id)

    try:
        db.session.delete(armour_to_delete)
        db.session.commit()
        return redirect('/armours.html')
    except:
        return 'There was a problem deleting your armour.'

@app.route('/viewArmour/<int:id>')
@login_required
def viewArmour(id):
    armourToDisplay = Armour.query.get_or_404(id)

    try:
        return render_template('viewArmour.html', armour=armourToDisplay)
    except:
        return 'There was a problem displaying your armour.'

@app.route('/updateArmour/<int:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def locations():
    if request.method == 'POST':
        l_Name = request.form['lName']
        l_Desc = request.form['lDesc']

        new_location = Location(creatorID=current_user.id, lName=l_Name, lDesc=l_Desc)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect('/locations.html')
        except:
            return 'There was an issue adding your location to the database.'
    else:
        locations = Location.query.filter_by(creatorID=current_user.id).order_by(Location.lID).all()
        return render_template('locations.html', locations=locations)

@app.route('/deleteLocation/<int:id>')
@login_required
def deleteLocation(id):
    location_to_delete = Location.query.get_or_404(id)

    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect('/locations.html')
    except:
        return 'There was a problem deleting your location.'

@app.route('/updateLocation/<int:id>', methods=['GET', 'POST'])
@login_required
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

# Run the app in debug mode:
if __name__ == "__main__":
    app.run(debug=True)