"""
Generate SSL Certificate for HTTPS
Creates a self-signed certificate for local development
"""

from OpenSSL import crypto
import os


def generate_ssl_certificate(cert_dir: str = "."):
    """Generate a self-signed SSL certificate"""
    
    cert_file = os.path.join(cert_dir, "cert.pem")
    key_file = os.path.join(cert_dir, "key.pem")
    
    # Check if already exists
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print("✅ SSL certificate sudah ada")
        return cert_file, key_file
    
    print("🔐 Generating SSL certificate...")
    
    # Generate key
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)
    
    # Generate certificate
    cert = crypto.X509()
    cert.get_subject().C = "ID"
    cert.get_subject().ST = "Indonesia"
    cert.get_subject().L = "Jakarta"
    cert.get_subject().O = "Kaell Assistant"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    
    # Set validity
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365 * 24 * 60 * 60)  # Valid for 1 year
    
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')
    
    # Write certificate
    with open(cert_file, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    # Write key
    with open(key_file, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))
    
    print(f"✅ Certificate generated: {cert_file}")
    print(f"✅ Key generated: {key_file}")
    
    return cert_file, key_file


if __name__ == "__main__":
    generate_ssl_certificate()
