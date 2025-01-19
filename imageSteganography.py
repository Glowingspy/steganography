import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTextEdit,
    QMessageBox
)

from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from PIL import Image # For image processing

class ImageUploader(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stetnography Tool: Encrypt & Decrypt Messages")
        self.setGeometry(100, 100,1000,700)

        #Initialize variables
        self.image_path = None

        # Create a central widget and set up a horizontal layout(split into two sections)
        central_widget = QWidget(self)
        layout = QHBoxLayout()


        # Left half: for uploading and displaying the image
        self.image_label = QLabel("No image uploaded", self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #0078d4; background-color: #f0f8ff; color: #0078d4; font-size: 16px;")

        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.setStyleSheet("background-color: #0078d4; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.upload_button.clicked.connect(self.upload_image)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_label, stretch = 5)
        left_layout.addWidget(self.upload_button, stretch=1)


        # Right half: for entering the message and decrypting
        right_layout = QVBoxLayout()


        # Add a title label
        title_label = QLabel("Message Input and Actions")
        title_label.setFont(QFont("Ariel", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #333333;")

        self.message_input = QTextEdit(self)
        self.message_input.setPlaceholderText("Enter the message to encrypt in the message...")
        self.message_input.setFixedHeight(150)
        self.message_input.setStyleSheet("font-size: 14px; border: 1px solid #cccccc; padding: 10px;")

        self.encrypt_button = QPushButton("Encrypt", self)
        self.encrypt_button.setStyleSheet("background-color: #38a745; color: white; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.encrypt_button.clicked.connect(self.encrypt_message)


        self.decrypt_button = QPushButton("Decrypt", self)
        self.decrypt_button.setStyleSheet("background-color: #ffc107; color: black; font-size: 14px; padding: 10px; border-radius: 5px;")
        self.decrypt_button.clicked.connect(self.decrypt_message)



        #Add title, input and buttons to the right layout
        right_layout.addWidget(title_label)
        right_layout.addWidget(self.message_input)
        right_layout.addWidget(self.encrypt_button)
        right_layout.addWidget(self.decrypt_button)
        right_layout.addStretch()



        #Add the lft and right sections to the horizontal layout

        layout.addLayout(left_layout, stretch = 3)
        layout.addLayout(right_layout, stretch = 2)

        #Set the cental widget to the layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


        # Apply a global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa
            }
            QPushButton:hover {
               background-color: #0056b3
            }
            QLabel {
               font-size: 14px;
            }               
            """)



    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select an Image", "", "Image FIles(*.png *.jpg *.jpeg *.bmp)")

        if file_path:
            self.image_path = file_path
            # Display the selected image
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(
                pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio,
                )
            )
            self.image_label.setText("")



    
    def encrypt_message(self):
        if not self.image_path:
            QMessageBox.warning(self, "Error","Please upload an image first.")
            return
        

        message = self.message_input.toPlainText()
        if not message:
            QMessageBox.warning(self, "Error", "Please enter a message to encrypt.")
            return
        

        # Append a delimiter to the message
        message += '###'


        try:
            #Load the image
            img = Image.open(self.image_path)
            encoded_img = self.encode_message(img, message)

            # Save the encoded image
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Encryptped Image", "", "Image Files (*.png *.bmp)")

            if save_path:
                encoded_img.save(save_path)
                QMessageBox.information(self, "Success", "Message encrypted and image saved successfully")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"And error occured: {str(e)}")



    def encode_message(Self, img, message):
        """Encodes a message into the least significant bits of an image"""
        # Converts the message to binary
        binary_message = ''.join(format(ord(c), '08b') for c in message)
        binary_message_len = len(binary_message)

        pixels = img.load() # Access image pixels
        width, height = img.size

        message_index = 0
        for y in range(height):
            for x in range(width):
                # Checks if all bits of the binary message have been encoded
                if message_index >= binary_message_len:
                    break


                r, g, b = pixels[x, y][:3] # Get RGB values
                new_pixel = []

                for color in (r, g, b):
                    if message_index < binary_message_len:
                        new_color = (color & ~1) | int(binary_message[message_index]) #Modify LSB
                        new_pixel.append(new_color)
                        message_index += 1

                    else:
                        new_pixel.append(color) #Just appends the old color for all other unmodified pixels


                pixels[x,y] = tuple(new_pixel) + ((pixels[x,y][3],)if len(pixels[x,y]) == 4 else ()) # Checks if an alpha channel exists


            if message_index < binary_message_len:
                raise ValueError("The image is too small to encode the entire message.")
            

            return img
        

    def decrypt_message(self):
        # Open a file dialog to select and encrypted image
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select and Encypted Image", 
            "", # Initial directory empty(starts at last used directory)
            "Image Files (*.png *.bmp)"
        )

        if not file_path:
            return
        

        try:
            # Load the image

            img = Image.open(file_path)
            message = self.decode_message(img)


            QMessageBox.information(self, "Decrypted Message", f"The hidden message is : \n\n {message}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")




    def decode_message(Self, img):
        """Decodes a hidden message from the least significant bits of an image."""
        pixels = img.load() # Access image pixels
        width, height = img.size

        binary_message = ""

        for y in range(height):
            for x in range(width):
                r, g, b = pixels[x, y][:3] # Get RGB values
                for color in (r, g, b): # Iterate through RGB channels
                    binary_message += str(color & 1) # Extract LSB


        # Convert binary message to string
        message = ""
        for i in range(0, len(binary_message), 8):
            byte= binary_message [i:i+8]
            char = chr(int(byte, 2)) # Converts it to a decimal integer, then to ASCII
            if message.endswith("###"): #Stop at the delimtier
                return message[:-3] # Removes the delimiter from the message
            message += char

        
        raise ValueError("No valid message found in the image")
    
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageUploader()
    window.show()
    sys.exit(app.exec())