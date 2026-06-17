from flask import Flask, request, jsonify, render_template
import subprocess
import os
import tempfile

app = Flask(__name__)

# হোম পেজে HTML ফাইল দেখাবে
@app.route('/')
def index():
    return render_template('index.html')

# সিগনেচার ভেরিফাই করার API
@app.route('/verify', methods=['POST'])
def verify_signature():
    if 'pdf_file' not in request.files:
        return jsonify({'error': 'কোনো ফাইল আপলোড করা হয়নি'}), 400

    file = request.files['pdf_file']
    if file.filename == '':
        return jsonify({'error': 'ফাইল নির্বাচন করা হয়নি'}), 400

    # টেম্পোরারি ফাইল সেভ করুন
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        # pdfsig কমান্ড চালান
        result = subprocess.run(
            ['pdfsig', tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout

        # আউটপুট পার্স করুন
        if 'Signature is valid' in output:
            status = 'valid'
            details = '✅ সিগনেচারটি সম্পূর্ণ বৈধ (Valid)'
        elif 'Signature is invalid' in output:
            status = 'invalid'
            details = '❌ সিগনেচারটি অবৈধ (Invalid)'
        else:
            status = 'unknown'
            details = output or 'সিগনেচারের অবস্থা নির্ণয় করা যায়নি।'

        return jsonify({'status': status, 'details': details})

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'ভেরিফিকেশন টাইমআউট হয়েছে'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

if __name__ == '__main__':
    # ডিবাগ মোডে চালান (ব্রাউজারে http://127.0.0.1:5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
