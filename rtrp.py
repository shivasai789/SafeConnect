import os
from decouple import config
from twilio.rest import Client
from flask import Flask, render_template, request, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Load credentials from environment variables
account_sid = config('ACCOUNT_SID')  # Twilio Account SID
auth_token = config('AUTH_TOKEN')    # Twilio Auth Token
your_phone = config('YOUR_PHONE')    # Twilio Phone Number

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Default emergency contact and unsafe number
emergency_contact = config('EMERGENCY_CONTACT')  # Default Emergency Contact
unsafe_number = config('UNSAFE_NUMBER')          # Default Unsafe Number

@app.route('/', methods=['GET', 'POST'])
def home():
    global emergency_contact, unsafe_number

    if request.method == 'POST':
        if 'update_contact' in request.form:
            # Update the unsafe number if provided
            updated_unsafe = request.form.get('unsafe_number')
            if updated_unsafe:
                unsafe_number = updated_unsafe
                print(f"Unsafe number updated to: {unsafe_number}")

            # Update the emergency contact if provided
            updated_emergency = request.form.get('emergency_number')
            if updated_emergency:
                emergency_contact = updated_emergency
                print(f"Emergency contact updated to: {emergency_contact}")

            return redirect(url_for('home'))

        elif 'trigger_alert' in request.form:
            # Trigger SMS and call alerts
            print(f"Triggering alert for: {emergency_contact} by {unsafe_number}")
            send_emergency_sms()
            make_emergency_call()
            return redirect(url_for('home'))

    return render_template('index.html', current_contact=emergency_contact, your_contact=unsafe_number)


def send_emergency_sms():
    """
    Sends an emergency SMS alert to the specified emergency contact.
    """
    try:
        print("Sending emergency SMS...")
        # SMS content
        message_body = (
            f"🚨 Emergency Alert! 🚨\n"
            f"An unsafe situation has been detected.\n"
            f"Triggering Number: {unsafe_number}.\n"
            f"Please respond immediately and check the situation."
        )

        # Send the SMS
        message = client.messages.create(
            body=message_body,  # Message content
            from_=your_phone,  # Twilio phone number
            to=emergency_contact  # Recipient's phone number
        )

        # Log the successful message SID
        print(f"SMS sent successfully! SID: {message.sid}")

    except Exception as e:
        print(f"Failed to send SMS: {e}")


def make_emergency_call():
    """
    Makes an emergency call to the specified emergency contact.
    The call will read out a pre-defined safety message.
    """
    try:
        print("Making an emergency call...")
        # Call content using Twilio's TwiML for Text-to-Speech
        call = client.calls.create(
            twiml='<Response><Say>This is an emergency alert. Please respond to the unsafe situation immediately.</Say></Response>',
            from_=your_phone,  # Twilio phone number
            to=emergency_contact  # Recipient's phone number
        )

        # Log the successful call SID
        print(f"Call initiated successfully! SID: {call.sid}")

    except Exception as e:
        print(f"Failed to make a call: {e}")


if __name__ == '__main__':
    app.run(debug=True)
