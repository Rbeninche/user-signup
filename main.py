from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route("/")
def display_form():
    return render_template('signup.html')


@app.route("/", methods=['POST'])
def validate_form():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['password-confirm']
    username_error = ''
    email_error = ''
    password_error = ''
    confirm_password_error = ''

    if username == '':
        username_error = "Username cannot be left empty"
    elif len(username) < 3:
        username_error = "Username cannot be less than 3 characters"
    elif len(username) > 20:
        username_error = "Username cannot be more than 20 characters"
    elif ' ' in username:
        username_error = "Username contains space"

    if email != '':
        if "@" not in email:
            email_error = "Email does not have '@'"
        elif "." not in email:
            email_error = "email does not contain any '. (Period)'"
        elif ' ' in email:
            email_error = "email contains space"
        elif len(email) < 3:
            username_error = "Email cannot have less than 3 characters"
        elif len(email) > 20:
            username_error = "Email cannot have more than 20 characters"

    if password == '':
        password_error = "Password field cannot be left empty"
    elif len(password) < 3:
        password_error = "Password cannot be less than 3 characters"
    elif len(password) > 20:
        password_error = "Password cannot be more than 20 characters"
    elif ' ' in password:
        password_error = "Password contains space"
    if not password_error:
        if confirm_password == '':
            confirm_password_error = "Please Confirm your password"
        elif confirm_password != password:
            confirm_password_error = "Password does not match"

    if not username_error and not email_error and not password_error and not confirm_password_error:
        return redirect('/thank_you?username=' + username)
    else:
        return render_template('signup.html', username_error=username_error, email_error=email_error, password_error=password_error, confirm_password_error=confirm_password_error)


@app.route("/thank_you")
def thank_you():
    username = request.args.get("username")
    return render_template('thankyou.html', username=username)


if __name__ == "__main__":
    app.run(debug=True)
