# SMS-Based Two-Factor Authentication (2FA) Implementation in pgAdmin

## 1. Frontend Components and State Management

**File:** `pgadmin4/web/pgadmin/static/js/SecurityPages/MfaRegisterPage.jsx`

- Created a new function for `SmsRegisterView` by studying the structure of `EmailRegisterView`.

**Before Change:**  
![image](https://github.com/user-attachments/assets/f44ba55c-6761-4e6e-88e4-cf813481b51e)  
![image](https://github.com/user-attachments/assets/ed07809e-cd4b-4538-8558-90e9ab068ca2)  
*Fig 1.1 Before change*

**After Change:**  
![Screenshot 2025-03-29 210730](https://github.com/user-attachments/assets/bbb826e0-7526-4522-96eb-5b8b2c7d1f5a)  
*Fig 1.2 After change*

---
## 2. Phone Number Input View

- When selecting the SMS setup, users are redirected to a new page for authentication registration.

**SMS Registration Page:**  
![image1](https://github.com/user-attachments/assets/2c936853-1c70-4730-99f4-801f4c7de8c7)  
*Fig 2.1 SMS Registration page*

### Page Rendering Logic:
- **When `phone_number_placeholder` exists:** Displays the phone input field.
- **When `otp_placeholder` exists:** Displays the verification code input field.

![Screenshot 2025-03-29 195236](https://github.com/user-attachments/assets/55a95f06-a8bb-4db7-abf4-9c667805803e)  
*Fig 2.2 `phone_number_placeholder` - renders the SMS Registration page*

---
## 3. Form Submission

- Introduced a function `handleSubmit()` in `MfaRegisterPage.jsx` to ensure entered values are correctly stored.

![Screenshot 2025-03-29 170813](https://github.com/user-attachments/assets/4b2866c4-f5c2-405d-9c6e-8846b5befd5b)  
*Fig 3.1 Data entered is registered correctly (Triggered when the form is submitted)*

### Validations:
- **Phone Number Format Validation:**
  - Regex pattern: `^\+[1-9]\d{1,14}$`
  - Implemented in `sms.py`, where `send_to` retrieves the phone number from the form submission.

---
## 4. Backend Implementation

**File:** `pgadmin4/web/pgadmin/authenticate/mfa/sms/sms.py`

### Key Functions:
- **Backend Entry Point:** `def send_sms_code() -> Response:`
- **OTP Generation:** `def __generate_otp()`
- **SMS Sending:** `def _send_code_to_phone(_phone: str = None) -> (bool, int, str):`
- **Code Verification:** `def validate(self, **kwargs):`

---
## 5. Testing Twilio API Integration

**File:** `test_sms_manual.py`

- Verifies that the Twilio API logic works correctly.
- Ensures that SMS messages are sent and received successfully.

![WhatsApp Image 2025-03-29 at 21 51 09_ede26dd1](https://github.com/user-attachments/assets/33a4c7d1-3e2f-4089-948b-941b61dbaeb0)  
*Fig 5.1 SMS received correctly*

---
## 6. SMS Authentication Flow

```
Frontend (MfaRegisterPage.jsx)
  ↓
User enters phone number
  ↓
handleSubmit() sends POST to /send_sms_code
  ↓
Backend (sms.py)
  ↓
send_sms_code() validates request
  ↓
_send_code_to_phone() called
  ↓
__generate_otp() creates 6-digit code
  ↓
Twilio sends SMS
  ↓
Frontend (MfaRegisterPage.jsx)
  ↓
User enters verification code
  ↓
handleSubmit() sends POST with code
  ↓
Backend (sms.py)
  ↓
validate() checks code
  ↓
Success/Failure response
```

This document outlines the key implementations, frontend and backend changes, as well as the flow of SMS-based 2FA in **pgAdmin**.

