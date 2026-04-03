import qrcode
# Jo roll number tumne website par add kiya hai, wahi yahan likho
img = qrcode.make("101") 
img.save("test_qr.png")
print("QR Code ban gaya hy! Folder check karein.")
