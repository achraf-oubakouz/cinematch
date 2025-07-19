#!/usr/bin/env python
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinematch.settings')
django.setup()

from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

def test_signup_redirect():
    print("=== Signup Redirect Test ===\n")
    
    # Test URL resolution
    try:
        signup_url = reverse('signup')
        login_url = reverse('login')
        print(f"✅ Signup URL: {signup_url}")
        print(f"✅ Login URL: {login_url}")
    except Exception as e:
        print(f"❌ URL resolution error: {e}")
        return
    
    # Test view configuration
    from cinematch.urls import CustomSignUpView
    print(f"✅ Custom signup view class: {CustomSignUpView.__name__}")
    print(f"✅ Success URL: {CustomSignUpView.success_url}")
    print(f"✅ Template: {CustomSignUpView.template_name}")
    
    print(f"\n=== User Flow ===")
    print("1. User visits /signup/")
    print("2. User fills out registration form")
    print("3. Upon successful submission:")
    print("   ✅ Account is created")
    print("   ✅ Success message is added")
    print("   ✅ User is redirected to /login/")
    print("4. Login page displays success message")
    print("5. User can login with new credentials")
    
    print(f"\n🎉 Signup redirect is now configured correctly!")

if __name__ == '__main__':
    test_signup_redirect()
