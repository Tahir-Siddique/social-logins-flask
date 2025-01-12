# Social Login Module with Flask

This project provides a social login module using **Flask** with support for Google, Facebook, and LinkedIn OAuth authentication. It includes both frontend (HTML/CSS) and backend logic, making it easy to integrate into any Python web application.

### **NOTE**
This documentation is generated using ChatGPT. I have created all of the secret IDs and client IDs using this guide. Please follow it accordingly so you can get the setup easily.

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/Tahir-Siddique/social-logins-flask.git
cd social-logins-flask
```

### **2. Create a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment Variables**
1. Create a `.env` file by copying the `.env.example` file:
   ```bash
   cp .env.example .env
   ```
2. Add your OAuth credentials for Google, Facebook, and LinkedIn in the `.env` file:
   ```ini
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   FACEBOOK_CLIENT_ID=your_facebook_app_id
   FACEBOOK_CLIENT_SECRET=your_facebook_app_secret
   LINKEDIN_CLIENT_ID=your_linkedin_client_id
   LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
   ```

### **5. Run the Application**
```bash
flask run
```
The application will be available at `http://127.0.0.1:5000/`.

## **Guide to Obtain OAuth Client ID and Secret**

### **Google OAuth**
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Navigate to **"APIs & Services" > "Credentials"**.
4. Click **"Create Credentials" > "OAuth Client ID"**.
5. Set up the consent screen if not already done.
6. Choose **"Web Application"** as the application type.
7. Add the redirect URI, e.g., `http://localhost:5000/auth/google/callback`.
8. Copy the **Client ID** and **Client Secret**.

### **Facebook OAuth**
1. Go to the [Facebook Developer Portal](https://developers.facebook.com/).
2. Click **"Create App"** and choose **"Consumer"**.
3. Provide required details and create the app.
4. Add the **"Facebook Login"** product.
5. Under **"Settings" > "Basic"**, find the **App ID** and **App Secret**.
6. In **"Facebook Login" > "Settings"**, add the redirect URI, e.g., `http://localhost:5000/auth/facebook/callback`.

### **LinkedIn OAuth**
1. Go to the [LinkedIn Developer Portal](https://www.linkedin.com/developers/).
2. Click **"Create App"** and fill in the necessary details.
3. Once the app is created, go to the **"Auth"** tab.
4. Enable **"Sign In with LinkedIn"**.
5. Add the redirect URI, e.g., `http://localhost:5000/auth/linkedin/callback`.
6. Copy the **Client ID** and **Client Secret**.

