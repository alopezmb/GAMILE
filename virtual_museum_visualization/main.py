from subprocess import check_output
from flask import request, redirect, jsonify
from flask_restful import Resource
from controllers.controllers import *
from settings.settings import app, api, mesa_manager_api_endpoint
import requests


# LOAD APP SETTINGS

# #################################################################
# Resources
###################################################################


class Home(Resource):

    def get(self):
        return render('login.html')


class Login(Resource):

    def get(self):
        return render('login.html')

    def post(self):
        data = request.form
        login_successful = process_login(data["username"], data["password"])
        return redirect('/museum') if login_successful else render('login.html',
                                                                   error_message='Username/password incorrect')


class Logout(Resource):

    def get(self):
        process_logout()
        return redirect('/login')


class Register(Resource):

    def get(self):
        return render('register.html')
        pass

    def post(self):
        data = request.form
        success, message = process_registration(
            data["username"],
            data["password"],
            data["password_confirmation"])
        return render('register.html', success=success, error_message=message)


@login_class
class Museum(Resource):

    def get(self):
        visitor = self.get_user()
        # (Re)initialize model
        requests.post(mesa_manager_api_endpoint,
                      json={"instruction_type": "reset"})
        # Show virtual museum html
        return render('museum.html', user=visitor)


@login_class
class MuseumResetter(Resource):

    def get(self):
        return redirect('/museum')


####################################################################
# Routes
###################################################################


api.add_resource(Home, '/')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Register, '/register')
api.add_resource(Museum, '/museum')
api.add_resource(MuseumResetter, '/museum-reset-tour')
