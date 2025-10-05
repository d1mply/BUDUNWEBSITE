#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BUDUN Sigorta Poliçe Takip Web Sitesi
Flask Backend + Supabase Database
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from supabase import create_client, Client
import os
from datetime import datetime
import json

# Flask uygulaması oluştur
app = Flask(__name__)
app.secret_key = 'budun-secret-key-2024'

# Supabase bağlantısı
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'your-supabase-key')

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase baglantisi basarili!")
except Exception as e:
    print(f"Supabase baglanti hatasi: {e}")
    supabase = None

# Ana sayfa
@app.route('/')
def index():
    """Ana sayfa - Giriş yapmış kullanıcıları dashboard'a yönlendir"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

# Giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı girişi"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            flash('Kullanıcı adı ve şifre gereklidir!', 'error')
            return render_template('login.html')
        
        # Supabase'den kullanıcıyı kontrol et
        try:
            result = supabase.table('users').select('*').eq('username', username).execute()
            
            if result.data and len(result.data) > 0:
                user = result.data[0]
                
                # Şifre kontrolü (basit hash kontrolü)
                if user.get('password') == password:  # Gerçek uygulamada hash kullanılmalı
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['is_admin'] = user.get('is_admin', False)
                    session['company_id'] = user.get('company_id')
                    
                    flash(f'Hoş geldiniz, {user["username"]}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Hatalı şifre!', 'error')
            else:
                flash('Kullanıcı bulunamadı!', 'error')
                
        except Exception as e:
            print(f"Giriş hatası: {e}")
            flash('Giriş sırasında hata oluştu!', 'error')
    
    return render_template('login.html')

# Çıkış
@app.route('/logout')
def logout():
    """Kullanıcı çıkışı"""
    session.clear()
    flash('Başarıyla çıkış yapıldı!', 'info')
    return redirect(url_for('index'))

# Dashboard
@app.route('/dashboard')
def dashboard():
    """Ana panel - Kullanıcı girişi gerekli"""
    if 'user_id' not in session:
        flash('Giriş yapmanız gerekiyor!', 'error')
        return redirect(url_for('login'))
    
    # Kullanıcı bilgilerini al
    user_info = {
        'username': session['username'],
        'is_admin': session.get('is_admin', False),
        'company_id': session.get('company_id')
    }
    
    # Şirket bilgisini al
    company_name = "Bilinmeyen Şirket"
    if user_info['company_id']:
        try:
            company_result = supabase.table('companies').select('name').eq('id', user_info['company_id']).execute()
            if company_result.data:
                company_name = company_result.data[0]['name']
        except Exception as e:
            print(f"Şirket bilgisi alınamadı: {e}")
    elif user_info['is_admin']:
        company_name = "Super Admin"
    
    return render_template('dashboard.html', 
                         user=user_info, 
                         company_name=company_name)

# Poliçeler sayfası
@app.route('/policies')
def policies():
    """Poliçe yönetimi - Kullanıcı girişi gerekli"""
    if 'user_id' not in session:
        flash('Giriş yapmanız gerekiyor!', 'error')
        return redirect(url_for('login'))
    
    # Kullanıcının şirketindeki poliçeleri al
    company_id = session.get('company_id')
    is_admin = session.get('is_admin', False)
    
    try:
        if is_admin:
            # Admin tüm poliçeleri görebilir
            policies_result = supabase.table('policies').select('*').execute()
        else:
            # Normal kullanıcı sadece kendi şirketinin poliçelerini görebilir
            if company_id:
                policies_result = supabase.table('policies').select('*').eq('company_id', company_id).execute()
            else:
                policies_result = {'data': []}
        
        policies = policies_result.data if policies_result.data else []
        
    except Exception as e:
        print(f"Poliçeler alınamadı: {e}")
        policies = []
    
    return render_template('policies.html', policies=policies, user=session)

# API: Yeni poliçe ekle
@app.route('/api/policies', methods=['POST'])
def add_policy():
    """Yeni poliçe ekleme API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        
        # Poliçe verilerini hazırla
        policy_data = {
            'customer_name': data.get('customer_name'),
            'customer_tc': data.get('customer_tc'),
            'plate_number': data.get('plate_number'),
            'policy_number': data.get('policy_number'),
            'product': data.get('product'),
            'insurance_company': data.get('insurance_company'),
            'salesperson': data.get('salesperson'),
            'gross_premium': data.get('gross_premium'),
            'end_date': data.get('end_date'),
            'notes': data.get('notes'),
            'company_id': session.get('company_id'),
            'created_at': datetime.now().isoformat()
        }
        
        # Supabase'e ekle
        result = supabase.table('policies').insert(policy_data).execute()
        
        if result.data:
            return jsonify({'success': True, 'message': 'Poliçe başarıyla eklendi!'})
        else:
            return jsonify({'error': 'Poliçe eklenemedi!'}), 500
            
    except Exception as e:
        print(f"Poliçe ekleme hatası: {e}")
        return jsonify({'error': str(e)}), 500

# API: Şirketler listesi
@app.route('/api/companies')
def get_companies():
    """Şirketler listesi API"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        result = supabase.table('companies').select('*').eq('active', True).execute()
        companies = result.data if result.data else []
        return jsonify({'companies': companies})
    except Exception as e:
        print(f"Şirketler alınamadı: {e}")
        return jsonify({'error': str(e)}), 500

# API: Satışçılar listesi
@app.route('/api/salespeople')
def get_salespeople():
    """Satışçılar listesi API - Şirket bazlı filtreleme"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        company_id = session.get('company_id')
        is_admin = session.get('is_admin', False)
        
        if is_admin:
            # Admin tüm satışçıları görebilir
            result = supabase.table('salespeople').select('*').eq('active', True).execute()
        else:
            # Normal kullanıcı sadece kendi şirketinin satışçılarını görebilir
            if company_id:
                result = supabase.table('salespeople').select('*').eq('company_id', company_id).eq('active', True).execute()
            else:
                result = {'data': []}
        
        salespeople = result.data if result.data else []
        return jsonify({'salespeople': salespeople})
        
    except Exception as e:
        print(f"Satışçılar alınamadı: {e}")
        return jsonify({'error': str(e)}), 500

# Hata sayfaları
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Ana çalıştırma
if __name__ == '__main__':
    # Vercel için gerekli
    app.run(debug=True, host='0.0.0.0', port=5000)
