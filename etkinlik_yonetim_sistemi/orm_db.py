from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

YUKLEME_KLASORU = 'static/yuklemeler'
UZANTILAR = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usta_rehber_otomasyon_sistemi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = YUKLEME_KLASORU
app.debug = True
db = SQLAlchemy(app)
dbsession = db.session()

class Yonetici(db.Model):

    yonetici_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    yonetici_adi_soyadi = db.Column(db.String(50), nullable=False)
    yonetici_tc = db.Column(db.String(11), unique=True, nullable=False)
    yonetici_sifre = db.Column(db.String(10), nullable=False)
    yonetici_email = db.Column(db.String(50))
    yonetici_tel = db.Column(db.String(12))
    yonetici_durum = db.Column(db.Integer, nullable=False)

class Isyeri(db.Model):

    isyeri_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    isyeri_adi = db.Column(db.String(50))
    isyeri_adresi = db.Column(db.String(500))
    isyeri_telefon = db.Column(db.String(500))
    isyeri_websitesi = db.Column(db.String(500))
    isyeri_aciklama = db.Column(db.String(500))

    isyeri_semt_id = db.Column(db.Integer, db.ForeignKey('semt.semt_id'), nullable=False)
    semt_id = db.relationship('Semt', backref=db.backref('isyeri_semti', lazy=True))

    isyeri_kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.kategori_id'), nullable=False)
    kategori_id = db.relationship('Kategori', backref=db.backref('isyeri_kategori', lazy=True))

    isyeri_goruntulenme_sayisi = db.Column(db.Integer, nullable=False,default=0)

    isyeri_foto_01 = db.Column(db.String(500)) # logo olarak tanımlanacak
    isyeri_foto_02 = db.Column(db.String(500))
    isyeri_foto_03 = db.Column(db.String(500))
    isyeri_foto_04 = db.Column(db.String(500))
    isyeri_foto_05 = db.Column(db.String(500))

    isyeri_durum = db.Column(db.Integer, nullable=False, default=1)

    isyeri_yonetici_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    yonetici = db.relationship('Yonetici', backref=db.backref('isyeri_yonetici', lazy=True),
                               foreign_keys=[isyeri_yonetici_id])

class Semt(db.Model):
    semt_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    semt_adi = db.Column(db.String(50))

class Kategori(db.Model):
    kategori_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    kategori_adi = db.Column(db.String(50))

class Yorum(db.Model):
    yorum_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    yorum_yapan_adi = db.Column(db.String(50))
    yorum_yapan_eposta = db.Column(db.String(500))
    yorum_aciklama = db.Column(db.String(500))
    yorum_isyeri_id = db.Column(db.Integer, db.ForeignKey('isyeri.isyeri_id'), nullable=False)
    isyeri_id = db.relationship('Isyeri', backref=db.backref('yorum_isyeri', lazy=True))
    yorum_durum = db.Column(db.Integer, default=1)

class Duyuru(db.Model):
    duyuru_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    duyuru_yonetici_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    duyuru_yonetici = db.relationship('Yonetici', backref=db.backref('duyuru_yonetici', lazy=True),
                                    foreign_keys=[duyuru_yonetici_id])
    duyuru_basligi = db.Column(db.String(500), nullable=False)
    duyuru_tarihi = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    duyuru_aciklama = db.Column(db.String(500), nullable=False)

# veri tabanını oluşturmak için tabloyu oluşturmak için
db.create_all()

