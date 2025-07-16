#!/usr/bin/env python3
"""
Simple test script to check QR code generation
"""

import qrcode
import os

def test_qr_generation():
    """Test basic QR code generation."""
    try:
        # Test data
        test_data = "http://localhost:8000/story/segment/test-segment-id"
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(test_data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to test file
        test_filename = "test_qr.png"
        img.save(test_filename)
        
        print(f"✅ QR code generated successfully: {test_filename}")
        print(f"✅ File exists: {os.path.exists(test_filename)}")
        print(f"✅ File size: {os.path.getsize(test_filename)} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating QR code: {e}")
        return False

if __name__ == "__main__":
    print("Testing QR code generation...")
    success = test_qr_generation()
    if success:
        print("✅ QR code generation test passed!")
    else:
        print("❌ QR code generation test failed!") 