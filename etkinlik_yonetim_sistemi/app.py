from etkinlik_orm_db import *
kullanici = {}

# Giriş işlemlerinin yer alacak olduğu işlemler
#giriş karşılama sayfası
@app.route('/', methods=['GET', 'POST'])
@app.route('/')
def index():
    if request.method == 'POST':
        tc = request.form.get('tcno')
        sifre = request.form.get('sifre')
        if True:
            user = Yonetici.query.filter_by(yonetici_tc=tc, yonetici_sifre=sifre).first()
            if user.yonetici_durum == 0:
                session['yonetici'] = user.yonetici_id
                kullanici['yonetici'] = user
                return redirect(url_for('yonetici_sayfasi'))
            elif user.yonetici_durum == 1:
                session['personel'] = user.yonetici_id
                kullanici['personel'] = user
                return redirect(url_for('personel_sayfasi'))

            else:
                return render_template('index.html', mesaj="Giriş Yapmak İstediğiniz Kullanıcı Aktif Değil")
        else:
            return render_template('index.html', mesaj="Hatalı giriş Yapmaktasınız")
    else:
        return render_template('index.html', mesaj="Hoş Geldiniz")

#çıkış işlemleri sayfası
@app.route('/cikis')
def cikis():
    session.clear()
    kullanici.clear()
    return redirect(url_for('index'))


#Aşağıdaki ilk bölümde yöneticilerin yapabilecek olduğu iş ve işlemlerin sayfa erişimleri yer almaktadır

#yönetici sayfası işlemleri
@app.route('/yonetici_sayfasi', methods=['GET', 'POST'])
@app.route('/yonetici_sayfasi')
def yonetici_sayfasi():
    try:
        etkinlikler = Etkinlik.query.all()
        duyurular = Duyuru.query.all()
        dilekler = Dilek.query.all()
        return render_template("yonetici.html",yonetici=kullanici['yonetici'],etkinlikler=etkinlikler,
                               duyurular=duyurular,dilekler=dilekler)
    except:
        return render_template('index.html', mesaj="Hoş Geldiniz")


# Personel İşlemleri Aşağıda Bölümde Yer Alacaktır

# personel ekleme işlemleri
@app.route('/personel_ekle', methods=['GET', 'POST'])
@app.route('/personel_ekle')
def personel_ekle():
    try:
        if request.method == 'POST':
            try:
                bilgiler = request.form.to_dict()
                yeni_personel = Yonetici(yonetici_adi_soyadi=bilgiler['yonetici_adi_soyadi'], yonetici_tc=bilgiler['yonetici_tc'],
                                 yonetici_sifre=bilgiler['yonetici_sifre'], yonetici_email=bilgiler['yonetici_email'],
                                 yonetici_tel=bilgiler['yonetici_tel'], birim_id=int(bilgiler['birim_id']),
                                )
                dbsession.add(yeni_personel)
                dbsession.commit()
                return render_template("personel_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
            except:
                return render_template("personel_ekle.html", yonetici=kullanici['yonetici'] , mesaj="Başarısızlık")
        else:
            birimler = Birim.query.all()
            return render_template("personel_ekle.html", yonetici=kullanici['yonetici'],birimler=birimler)
    except:
        return render_template("personel_ekle.html", yonetici=kullanici['yonetici'])

# personel güncelleme ve silme işlemleri
@app.route('/personel_guncelle_sil/<int:id>')
@app.route('/personel_guncelle_sil')
def personel_guncelle_sil(id=0):
    if id == 0:
        personeller = Yonetici.query.all()
        return render_template("personel_guncelle_sil.html", yonetici=kullanici['yonetici'], personeller=personeller)
    else:
        return redirect(url_for('personel_guncelle_sil'))


@app.route('/personel_guncelle/<int:id>')
@app.route('/personel_guncelle', methods=['GET', 'POST'])
def personel_guncelle(id=0):
    if id != 0:
        personel = Yonetici.query.filter_by(yonetici_id=id).first()
        birimler = Birim.query.all()
        return render_template("personel_guncelle.html", yonetici=kullanici['yonetici'], personel=personel,birimler=birimler)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        bilgiler['birim_id'] = int(bilgiler['birim_id'])
        dbsession.query(Yonetici).filter(Yonetici.yonetici_id==bilgiler['yonetici_id']).update(bilgiler)
        dbsession.commit()
        return redirect(url_for('personel_guncelle_sil'))
    else:
        return redirect(url_for('personel_guncelle'))

#personel silme işlemi yapmak için aşağıdaki kod bloğu
@app.route('/personel_sil/<int:sil>')
def personel_sil(sil=0):
    if sil != 0:
        dbsession.query(Yonetici).filter(Yonetici.yonetici_id == sil).delete()
        dbsession.commit()
        return redirect(url_for('personel_guncelle_sil'))
    else:
        return redirect(url_for('personel_guncelle_sil'))

def uzanti_kontrol(dosyaadi):
   return '.' in dosyaadi and \
   dosyaadi.rsplit('.', 1)[1].lower() in UZANTILAR

# Yönetici etkinlik İşlemleri
# Yönetici Etkinlik ekleme işlemleri
@app.route('/yonetici_etkinlik_ekle', methods=['GET', 'POST'])
@app.route('/yonetici_etkinlik_ekle')
def yonetici_etkinlik_ekle():
    if request.method == 'POST':
        bilgiler = request.form.to_dict()
        resimler=[]
        resimler.append(request.files['dosya01'])
        resimler.append(request.files['dosya02'])
        resimler.append(request.files['dosya03'])
        i = 1
        for dosya in resimler:
            if dosya and uzanti_kontrol(dosya.filename):
                dosyaadi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
                dosya_yolu = "/" +app.config['UPLOAD_FOLDER'] + "/" + dosyaadi
                deger = "etkinlik_foto_0"+str(i)
                bilgiler[deger] = dosya_yolu
                i+=1
        if True:
            yonetici = kullanici['yonetici']
            yeni_etkinlik = Etkinlik()
            yeni_etkinlik.etkinlik_adi = bilgiler['etkinlik_adi']
            yeni_etkinlik.etkinlik_aciklama = bilgiler['etkinlik_aciklama']
            yeni_etkinlik.etkinlik_kategori_id = int(bilgiler['etkinlik_kategori_id'])
            yeni_etkinlik.etkinlik_kontenjan_sayisi = int(bilgiler['etkinlik_kontenjan_sayisi'])
            yeni_etkinlik.etkinlik_foto_01 = bilgiler['etkinlik_foto_01']
            yeni_etkinlik.etkinlik_foto_02 = bilgiler['etkinlik_foto_02']
            yeni_etkinlik.etkinlik_foto_03 = bilgiler['etkinlik_foto_03']
            yeni_etkinlik.etkinlik_yonetici_id = yonetici.yonetici_id
            yeni_etkinlik.etkinlik_durum = 0

            yeni_etkinlik.etkinlik_birimleri = str(request.form.getlist('etkinlik_birimleri'))

            tarih = datetime.strptime(bilgiler['etkinlik_tarihi'], '%d/%m/%Y')
            yeni_etkinlik.etkinlik_tarihi = datetime.date(tarih)

            tarih = datetime.strptime(bilgiler['etkinlik_son_basvuru_tarihi'], '%d/%m/%Y')
            yeni_etkinlik.etkinlik_son_basvuru_tarihi = datetime.date(tarih)

            dbsession.add(yeni_etkinlik)
            dbsession.commit()
            return render_template("yonetici_etkinlik_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
        else:
            return render_template("yonetici_etkinlik_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarısızlık")
    else:
        birimler = Birim.query.all()
        kategoriler = Kategori.query.all()
        return render_template("yonetici_etkinlik_ekle.html", yonetici=kullanici['yonetici'],
                               birimler=birimler, kategoriler=kategoriler)

 # etkinlik güncelleme ve silme işlemleri
@app.route('/yonetici_etkinlik_guncelle_sil/<int:id>')
@app.route('/yonetici_etkinlik_guncelle_sil')
def yonetici_etkinlik_guncelle_sil(id=0):
    if id == 0:
        etkinlikler = Etkinlik.query.all()
        return render_template("yonetici_etkinlik_guncelle_sil.html", yonetici=kullanici['yonetici'], etkinlikler=etkinlikler)
    else:
        dbsession.query(Etkinlik).filter(Etkinlik.etkinlik_id==id).delete()
        dbsession.commit()
        return redirect(url_for('yonetici_etkinlik_guncelle_sil'))
#
@app.route('/yonetici_etkinlik_guncelle/<int:id>')
@app.route('/yonetici_etkinlik_guncelle', methods=['GET', 'POST'])
def yonetici_firma_guncelle(id=0):
    if id != 0:
        birimler = Birim.query.all()
        kategoriler = Kategori.query.all()
        etkinlik = Etkinlik.query.filter_by(etkinlik_id=id).first()
        return render_template("yonetici_etkinlik_guncelle.html", yonetici=kullanici['yonetici'],
                               etkinlik=etkinlik,birimler=birimler,kategoriler=kategoriler)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        resimler = []
        resimler.append(request.files['dosya01'])
        resimler.append(request.files['dosya02'])
        resimler.append(request.files['dosya03'])
        i = 1
        for dosya in resimler:
            if dosya and uzanti_kontrol(dosya.filename):
                dosyaadi = secure_filename(dosya.filename)
                dosya.save(os.path.join(app.config['UPLOAD_FOLDER'], dosyaadi))
                dosya_yolu = "/" + app.config['UPLOAD_FOLDER'] + "/" + dosyaadi
                deger = "etkinlik_foto_0" + str(i)
                bilgiler[deger] = dosya_yolu
                i += 1
        if True:

            bilgiler['etkinlik_kategori_id']= int(bilgiler['etkinlik_kategori_id'])
            bilgiler['etkinlik_kontenjan_sayisi'] = int(bilgiler['etkinlik_kontenjan_sayisi'])
            etkinlik_durum = int(bilgiler['etkinlik_durum'])
            bilgiler['etkinlik_birimleri'] = str(request.form.getlist('etkinlik_birimleri'))
            tarih = datetime.strptime(bilgiler['etkinlik_tarihi'], '%d/%m/%Y')
            bilgiler['etkinlik_tarihi'] = datetime.date(tarih)
            tarih = datetime.strptime(bilgiler['etkinlik_son_basvuru_tarihi'], '%d/%m/%Y')
            bilgiler['etkinlik_son_basvuru_tarihi'] = datetime.date(tarih)
        if True:
            dbsession.query(Etkinlik).filter(Etkinlik.etkinlik_id == bilgiler['etkinlik_id']).update(bilgiler)
            dbsession.commit()
            return render_template("yonetici_etkinlik_guncelle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
        else:
            return render_template("yonetici_etkinlik_guncelle.html", yonetici=kullanici['yonetici'], mesaj="Başarısızlık")

    else:
        return redirect(url_for('yonetici_etkinlik_guncelle_sil'))

# Yönetici Duyuru İşlemleri
# duyuru listeleme işlemleri yönetici
@app.route('/yonetici_duyuru_listesi')
def yonetici_duyuru_listesi():
    try:
        uye_id = session['yonetici']
        duyurular = Duyuru.query.all()
        return render_template("yonetici_duyuru_listesi.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    except:
        return render_template("yonetici_duyuru_listesi.html", yonetici=kullanici['yonetici'])

#duyuru ekleme işlemleri
@app.route('/yonetici_duyuru_ekle', methods=['GET', 'POST'])
@app.route('/yonetici_duyuru_ekle')
def yonetici_duyuru_ekle():
    tarih = datetime.today().utcnow()
    tarih = tarih.strftime("%d/%m/%Y")
    try:
        if request.method == 'POST':
            try:
                bilgiler = request.form.to_dict()
                tarih = datetime.strptime(bilgiler['duyuru_tarihi'], '%d/%m/%Y')
                tarih = datetime.date(tarih)
                yeni_duyuru = Duyuru(duyuru_yonetici_id=session['yonetici'],
                                   duyuru_basligi=bilgiler['duyuru_basligi'],
                                   duyuru_tarihi=tarih,
                                   duyuru_aciklama=bilgiler['duyuru_aciklama'])
                dbsession.add(yeni_duyuru)
                dbsession.commit()
                return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], mesaj="Başarı")
            except:
                return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'] , mesaj="Başarısızlık")
        else:
            return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], tarih=tarih)
    except:
        return render_template("yonetici_duyuru_ekle.html", yonetici=kullanici['yonetici'], tarih=tarih)

# duyuru güncelleme ve silme işlemleri
@app.route('/yonetici_duyuru_guncelle_sil/<int:id>')
@app.route('/yonetici_duyuru_guncelle_sil')
def yonetici_duyuru_guncelle_sil(id=0):
    if id == 0:
        duyurular = Duyuru.query.all()

        return render_template("yonetici_duyuru_guncelle_sil.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    else:
        return redirect(url_for('yonetici_duyuru_listesi'))

#yönetici bölümü duyuru güncelleme
@app.route('/yonetici_duyuru_guncelle/<int:id>')
@app.route('/yonetici_duyuru_guncelle', methods=['GET', 'POST'])
def yonetici_duyuru_guncelle(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("yonetici_duyuru_guncelle.html", yonetici=kullanici['yonetici'], duyurular=duyurular)
    elif request.method == 'POST':
        bilgiler = request.form.to_dict()
        tarih = datetime.strptime(bilgiler['duyuru_tarihi'], '%d/%m/%Y')
        tarih = datetime.date(tarih)
        dbsession.query(Duyuru).filter(Duyuru.duyuru_id == bilgiler['duyuru_id']).update(
            {Duyuru.duyuru_basligi: bilgiler['duyuru_basligi'],
             Duyuru.duyuru_tarihi: tarih, Duyuru.duyuru_aciklama: bilgiler['duyuru_aciklama']})
        dbsession.commit()
        return redirect(url_for('yonetici_duyuru_guncelle_sil'))
    else:
        return redirect(url_for('yonetici_duyuru_guncelle'))

#yönetici bölümü duyuru goruntuleme
@app.route('/yonetici_duyuru_goruntuleme/<int:id>')
@app.route('/yonetici_duyuru_goruntuleme', methods=['GET', 'POST'])
def yonetici_duyuru_goruntuleme(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("yonetici_duyuru_goruntuleme.html", yonetici=kullanici['yonetici'], duyuru=duyurular)
    else:
        return redirect(url_for('yonetici_duyuru_listesi'))

#yönetici paneli duyuru silme bölümü
@app.route('/yonetici_duyuru_sil/<int:sil>')
def yonetici_duyuru_sil(sil=0):
    if sil != 0:
        dbsession.query(Duyuru).filter(Duyuru.duyuru_id == sil).delete()
        dbsession.commit()
        return redirect(url_for('yonetici_duyuru_guncelle_sil'))

# duyuru listeleme işlemleri yönetici
@app.route('/duyuru_listesi')
def duyuru_listesi():
    try:
        duyurular = Duyuru.query.all()
        return render_template("duyuru_listesi.html",duyurular=duyurular)
    except:
        return render_template("duyuru_listesi.html")

# duyuru goruntuleme
@app.route('/duyuru_goruntuleme/<int:id>')
@app.route('/duyuru_goruntuleme', methods=['GET', 'POST'])
def duyuru_goruntuleme(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("duyuru_goruntuleme.html", duyuru=duyurular)
    else:
        return redirect(url_for('duyurular'))

# dilek güncelleme ve silme işlemleri
@app.route('/yonetici_dilek_guncelle_sil/<int:id>')
@app.route('/yonetici_dilek_guncelle_sil')
def yonetici_dilek_guncelle_sil(id=0):
    if id == 0:
        dilekler = Dilek.query.all()

        return render_template("yonetici_dilek_guncelle_sil.html", yonetici=kullanici['yonetici'], dilekler=dilekler)
    else:
        return redirect(url_for('yonetici_dilek_listesi'))

#personel sayfası işlemleri
@app.route('/personel_sayfasi', methods=['GET', 'POST'])
@app.route('/personel_sayfasi')
def personel_sayfasi():
    try:
        birim_id = str(kullanici['personel'].birim_id)
        etkinlikler = Etkinlik.query.filter_by(etkinlik_durum=0).all()
        personel_etkinlikleri = []
        for etkinlik in etkinlikler:
            birim_idleri = eval(etkinlik.etkinlik_birimleri)
            if birim_id in birim_idleri:
                personel_etkinlikleri.append(etkinlik)

        duyurular = Duyuru.query.all()
        dilekler = Dilek.query.filter_by(dilek_personel_id=session['personel']).all()

        return render_template("personel.html",personel=kullanici['personel'],
                               etkinlikler=personel_etkinlikleri,
                               duyurular=duyurular,
                               dilekler=dilekler)
    except:
        return render_template('index.html', mesaj="Hoş Geldiniz")

 # etkinlik güncelleme ve silme işlemleri
@app.route('/personel_etkinlik_listesi/<int:id>')
@app.route('/personel_etkinlik_listesi')
def personel_etkinlik_listesi(id=0):
    if id == 0:
        birim_id = str(kullanici['personel'].birim_id)
        etkinlikler = Etkinlik.query.filter_by(etkinlik_durum=0).all()
        personel_etkinlikleri = []
        for etkinlik in etkinlikler:
            birim_idleri = eval(etkinlik.etkinlik_birimleri)
            if birim_id in birim_idleri:
                personel_etkinlikleri.append(etkinlik)
        return render_template("personel_etkinlik_listesi.html",
                               personel=kullanici['personel'],
                               etkinlikler=personel_etkinlikleri)
    else:
        return redirect(url_for('personel_sayfasi'))

 # etkinlik güncelleme ve silme işlemleri
@app.route('/personel_pasif_etkinlikler/<int:id>')
@app.route('/personel_pasif_etkinlikler')
def personel_pasif_etkinlikler(id=0):
    if id == 0:
        birim_id = str(kullanici['personel'].birim_id)
        etkinlikler = Etkinlik.query.filter_by(etkinlik_durum=1).all()
        personel_etkinlikleri = []
        for etkinlik in etkinlikler:
            birim_idleri = eval(etkinlik.etkinlik_birimleri)
            if birim_id in birim_idleri:
                personel_etkinlikleri.append(etkinlik)
        return render_template("personel_pasif_etkinlikler.html",
                               personel=kullanici['personel'],
                               etkinlikler=personel_etkinlikleri)
    else:
        return redirect(url_for('personel_sayfasi'))

 # etkinlik güncelleme ve silme işlemleri
@app.route('/personel_basvurulan_etkinlikler')
def personel_basvurulan_etkinlikler():
    if session['personel']:
        basvurulan = Basvuru.query.filter_by(basvuru_personel_id=session['personel']).all()
        personel_etkinlikleri = []
        if basvurulan != None:
            for basvuru in basvurulan:
                etkinlik = Etkinlik.query.filter_by(etkinlik_id=basvuru.basvuru_etkinlik_id).first()
                personel_etkinlikleri.append(etkinlik)
        return render_template("personel_basvurulan_etkinlikler.html",
                               personel=kullanici['personel'],
                               etkinlikler=personel_etkinlikleri)
    else:
        return redirect(url_for('personel_sayfasi'))

# duyuru listeleme işlemleri yönetici
@app.route('/personel_duyuru_listesi')
def personel_duyuru_listesi():
    try:
        duyurular = Duyuru.query.all()
        return render_template("personel_duyuru_listesi.html",duyurular=duyurular,personel=kullanici['personel'])
    except:
        return render_template("personel_duyuru_listesi.html",personel=kullanici['personel'])

# duyuru goruntuleme
@app.route('/personel_duyuru_goruntuleme/<int:id>')
@app.route('/personel_duyuru_goruntuleme', methods=['GET', 'POST'])
def personel_duyuru_goruntuleme(id=0):
    if id != 0:
        duyurular = Duyuru.query.filter_by(duyuru_id=id).first()
        return render_template("personel_duyuru_goruntuleme.html", duyuru=duyurular,personel=kullanici['personel'])
    else:
        return redirect(url_for('personel_duyuru_listesi'))

# personel dilek ekleme işlemleri
@app.route('/personel_dilek_ekle', methods=['GET', 'POST'])
@app.route('/personel_dilek_ekle')
def personel_dilek_ekle():
    tarih = datetime.date(datetime.today())
    # tarih = datetime.date(tarih,"%d/%m/%Y")
    try:
        if request.method == 'POST':
            try:
                bilgiler = request.form.to_dict()
                yeni_dilek = Dilek(dilek_personel_id=session['personel'],
                                   dilek_basligi=bilgiler['dilek_basligi'],
                                   dilek_tarihi=tarih,
                                   dilek_aciklama=bilgiler['dilek_aciklama'])
                dbsession.add(yeni_dilek)
                dbsession.commit()
                return render_template("personel_dilek_ekle.html", personel=kullanici['personel'],
                                       mesaj="Başarı")
            except TypeError:
                print(TypeError)
                return render_template("personel_dilek_ekle.html", personel=kullanici['personel'],
                                       mesaj="Başarısızlık")
        else:
            return render_template("personel_dilek_ekle.html", personel=kullanici['personel'])
    except:
        return render_template("personel_dilek_ekle.html", personel=kullanici['personel'])

# dilek güncelleme ve silme işlemleri
@app.route('/personel_dilek_guncelle_sil/<int:id>')
@app.route('/personel_dilek_guncelle_sil')
def personel_dilek_guncelle_sil(id=0):
    if id == 0:
        dilekler = Dilek.query.filter_by(dilek_personel_id=session['personel']).all()
        return render_template("personel_dilek_guncelle_sil.html", personel=kullanici['personel'], dilekler=dilekler)
    else:
        dbsession.query(Dilek).filter_by(dilek_id=id).delete()
        dbsession.commit()
        return redirect(url_for('personel_dilek_guncelle_sil'))

# duyuru goruntuleme
@app.route('/personel_dilek_goruntule/<int:id>')
@app.route('/personel_dilek_goruntule', methods=['GET', 'POST'])
def personel_dilek_goruntule(id=0):
    if id != 0:
        dilek = Dilek.query.filter_by(dilek_id=id).first()
        return render_template("personel_dilek_goruntuleme.html", dilek=dilek,personel=kullanici['personel'])
    else:
        return redirect(url_for('personel_dilek_guncelle_sil'))

# duyuru goruntuleme
@app.route('/yonetici_dilek_goruntule/<int:id>')
@app.route('/yonetici_dilek_goruntule', methods=['GET', 'POST'])
def yonetici_dilek_goruntule(id=0):
    if id != 0:
        dilek = Dilek.query.filter_by(dilek_id=id).first()
        return render_template("yonetici_dilek_goruntuleme.html", dilek=dilek,yonetici=kullanici['yonetici'])
    else:
        return redirect(url_for('yonetici_dilek_guncelle_sil'))

# etkinlik detay goruntuleme
@app.route('/personel_etkinlik_detay/<int:etkinlik_id>/<int:personel_id>')
@app.route('/personel_etkinlik_detay/<int:etkinlik_id>')
@app.route('/personel_etkinlik_detay', methods=['GET', 'POST'])
def personel_etkinlik_detay(etkinlik_id=0,personel_id=0):
    if etkinlik_id > 0 and personel_id == 0:
        etkinlik = Etkinlik.query.filter_by(etkinlik_id=etkinlik_id).first()
        basvuru = Basvuru.query.filter_by(basvuru_etkinlik_id=etkinlik_id,basvuru_personel_id=session['personel']).first()
        basvuru = True if basvuru == None else False
        return render_template("personel_etkinlik_detay.html", etkinlik=etkinlik,personel=kullanici['personel'],basvuru=basvuru)
    elif etkinlik_id > 0 and personel_id > 0:
        basvuru = Basvuru.query.filter_by(basvuru_etkinlik_id=etkinlik_id,
                                          basvuru_personel_id=session['personel']).first()
        if basvuru == None:
            basvuru = Basvuru(basvuru_etkinlik_id=etkinlik_id,basvuru_personel_id=personel_id)
            dbsession.add(basvuru)
            dbsession.commit()
            basvuru = False
        else:
            dbsession.query(Basvuru).filter_by(basvuru_etkinlik_id=etkinlik_id,
                                          basvuru_personel_id=session['personel']).delete()
            dbsession.commit()
            basvuru = True
        etkinlik = Etkinlik.query.filter_by(etkinlik_id=etkinlik_id).first()
        return render_template("personel_etkinlik_detay.html", etkinlik=etkinlik,personel=kullanici['personel'],basvuru=basvuru)
    else:
        return redirect(url_for('personel_etkinlik_detay'))

# Yönetici etkinlik detay goruntuleme
@app.route('/yonetici_etkinlik_detay/<int:etkinlik_id>/<int:personel_id>')
@app.route('/yonetici_etkinlik_detay/<int:etkinlik_id>')
@app.route('/yonetici_etkinlik_detay', methods=['GET', 'POST'])
def yonetici_etkinlik_detay(etkinlik_id=0,personel_id=0):
    if etkinlik_id > 0 and personel_id == 0:
        etkinlik = Etkinlik.query.filter_by(etkinlik_id=etkinlik_id).first()
        basvuru = Basvuru.query.filter_by(basvuru_etkinlik_id=etkinlik_id).all()
        basvurular = basvuru if basvuru != None else []
        return render_template("yonetici_etkinlik_detay.html", etkinlik=etkinlik,
                               yonetici=kullanici['yonetici'],basvurular=basvurular)
    elif etkinlik_id > 0 and personel_id > 0:
        dbsession.query(Basvuru).filter_by(basvuru_etkinlik_id=etkinlik_id,
                                          basvuru_personel_id=personel_id).delete()
        dbsession.commit()
        etkinlik = Etkinlik.query.filter_by(etkinlik_id=etkinlik_id).first()
        basvuru = Basvuru.query.filter_by(basvuru_etkinlik_id=etkinlik_id).all()
        basvurular = basvuru if basvuru != None else []
        return render_template("yonetici_etkinlik_detay.html", etkinlik=etkinlik,
                               yonetici=kullanici['yonetici'], basvurular=basvurular)
    else:
        return redirect(url_for('yonetici_etkinlik_detay'))


if __name__ == '__main__':
    app.run(debug=True)
