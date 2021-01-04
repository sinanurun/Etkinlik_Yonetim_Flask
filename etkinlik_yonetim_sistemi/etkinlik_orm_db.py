from flask import *
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import os

YUKLEME_KLASORU = 'static/yuklemeler'
UZANTILAR = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///etkinlik_otomasyon_sistemi.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = YUKLEME_KLASORU
app.debug = True
db = SQLAlchemy(app)
dbsession = db.session()

# tüm personeller ve yöneticiler sistemde yönetici olarak tanımlanacak olup
# yönetici durum bilgisine göre bir kişi yönetici ve ya personel olarak sistemde yer alacaktır.
class Yonetici(db.Model):
    yonetici_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    yonetici_adi_soyadi = db.Column(db.String(50), nullable=False)
    yonetici_tc = db.Column(db.String(11), unique=True, nullable=False)
    yonetici_sifre = db.Column(db.String(10), nullable=False)
    yonetici_email = db.Column(db.String(50))
    yonetici_tel = db.Column(db.String(12))

    birim_id = db.Column(db.Integer, db.ForeignKey('birim.birim_id'), nullable=False)
    yonetici_birim = db.relationship('Birim', backref=db.backref('yonetici_birim', lazy=True),
                                      foreign_keys=[birim_id])
    yonetici_durum = db.Column(db.Integer, default=1)


# sistemde oluşturulacak etkinliklere ait bilgilerin tutulacak olduğu tablo olarak kullanılacaktır
class Etkinlik(db.Model):
    etkinlik_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    etkinlik_adi = db.Column(db.String(50))
    etkinlik_aciklama = db.Column(db.String(500))

    etkinlik_birimleri = db.Column(db.String(500))
    etkinlik_kategori_id = db.Column(db.Integer, db.ForeignKey('kategori.kategori_id'), nullable=False)
    etkinlik_kategori = db.relationship('Kategori', backref=db.backref('etkinlik_kategori', lazy=True))

    etkinlik_kontenjan_sayisi = db.Column(db.Integer)

    etkinlik_foto_01 = db.Column(db.String(500))
    etkinlik_foto_02 = db.Column(db.String(500))
    etkinlik_foto_03 = db.Column(db.String(500))

    etkinlik_yonetici_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    etkinlik_yonetici = db.relationship('Yonetici', backref=db.backref('etkinlik_yonetici', lazy=True),
                               foreign_keys=[etkinlik_yonetici_id])

    etkinlik_tarihi = db.Column(db.Date, nullable=False, default=datetime.date(datetime.today()))
    etkinlik_son_basvuru_tarihi = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    etkinlik_durum = db.Column(db.Integer, nullable=False, default=1)

# personelin ve etkinliklerin birimlerini belirlemek için birim bilgileri tutulacaktır.
class Birim(db.Model):
    birim_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    birim_adi = db.Column(db.String(50))

# etkinliklerin kategorileri bilgilerinin tutulması için gerekli alan
class Kategori(db.Model):
    kategori_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    kategori_adi = db.Column(db.String(50))


# etkinlik dışında ki duyurular
class Duyuru(db.Model):
    duyuru_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    duyuru_yonetici_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    duyuru_yonetici = db.relationship('Yonetici', backref=db.backref('duyuru_yonetici', lazy=True),
                                    foreign_keys=[duyuru_yonetici_id])
    duyuru_basligi = db.Column(db.String(500), nullable=False)
    duyuru_tarihi = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    duyuru_aciklama = db.Column(db.String(500), nullable=False)
    duyuru_foto_01 = db.Column(db.String(500))
    duyuru_durum = db.Column(db.Integer, default=1)

class Dilek(db.Model):
    dilek_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    dilek_personel_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    dilekpersonel = db.relationship('Yonetici', backref=db.backref('dilek_personel', lazy=True),
                               foreign_keys=[dilek_personel_id])
    dilek_basligi = db.Column(db.String(500), nullable=False)
    dilek_tarihi = db.Column(db.Date, nullable=False, default=datetime.date(datetime.today()))
    dilek_aciklama = db.Column(db.String(500), nullable=False)

class Basvuru(db.Model):
    basvuru_id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    basvuru_etkinlik_id = db.Column(db.Integer, db.ForeignKey('etkinlik.etkinlik_id'), nullable=False)
    basvuruetkinlik = db.relationship('Etkinlik', backref=db.backref('basvuru_etkinlik', lazy=True),
                                      foreign_keys=[basvuru_etkinlik_id])
    basvuru_personel_id = db.Column(db.Integer, db.ForeignKey('yonetici.yonetici_id'), nullable=False)
    basvurupersonel = db.relationship('Yonetici', backref=db.backref('basvuru_personel', lazy=True),
                                    foreign_keys=[basvuru_personel_id])
    basvuru_tarihi = db.Column(db.Date, nullable=False, default=datetime.date(datetime.today()))
    basvuru_durumu = db.Column(db.Integer, nullable=False, default=1)

# veri tabanını oluşturmak için tabloyu oluşturmak için
db.create_all()

