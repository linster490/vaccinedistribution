from kivy.uix.screenmanager import Screen,ScreenManager
import requests
import json
import re
from kivymd.uix.dialog import MDDialog
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDFlatButton
from kivymd.uix.list import OneLineAvatarListItem
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import IRightBodyTouch, OneLineAvatarIconListItem
from kivymd.uix.snackbar import Snackbar

class SignupPage(Screen):
    Builder.load_file('Signup.kv')
    url = "https://covidpriority-default-rtdb.firebaseio.com/.json"
    auth_key = "Z98flbpTP0dtaTZLF1TETqM7r1FktS74xOydjbWg"

    def back_to_loginpage(self,*args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_page'

    def check_email(self, email):
        regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'
        if re.search(regex, email):
            return True
        return False

    def create_patch(self, email, password, username):
        self.ids.email.text = ''
        self.ids.password.text = ''
        self.ids.username.text = ''

        forbidden_characters = '.$[]#/'

        request = requests.get(self.url + '?auth=' + self.auth_key)
        curr_account_emails = [request.json()[str(users)]["email"] for users in request.json()]
        curr_account_usernames = request.json()

        if email.strip() == '':
            Snackbar(text="You Must Enter an Email").open()
        elif password.strip() == '':
            Snackbar(text="You Must Enter A Password").open()
        elif not self.check_email(email.strip()):
            Snackbar(text="Invalid Email").open()
        elif ' ' in email.strip():
            Snackbar(text="No Spaces Allowed in Email Address").open()
        elif ' ' in password.strip():
            Snackbar(text="No Spaces Allowed in Password").open()
        elif not all([i not in forbidden_characters for i in username.strip()]):
            Snackbar(text="No Special Characters in Username").open()
        elif (curr_account_usernames is not None) and (username.strip() in curr_account_usernames):
            Snackbar(text="This Username is Already Taken").open()
        elif (curr_account_emails is not None) and (email.strip() in curr_account_emails):
            Snackbar(text="This Email is Already in Use").open()
        else:
            json_data = {username.strip(): {"email": email.strip(), "password": password.strip(),"medical":None,"age":None}}
            json_data = json.dumps(json_data)
            res = requests.patch(url=self.url, json=json.loads(json_data))
            Snackbar(text="Account Created").open()
            self.manager.transition.direction = 'right'
            self.manager.current = 'login_page'

class LoginPage(Screen):
    Builder.load_file('Login.kv')
    url = "https://covidpriority-default-rtdb.firebaseio.com/.json"
    auth_key = "Z98flbpTP0dtaTZLF1TETqM7r1FktS74xOydjbWg"

    def sign_up(self,*args):
        self.manager.transition.direction = 'left'
        self.manager.current = "signup_page"

    def on_login(self,email,password):
        request = requests.get(self.url + '?auth=' + self.auth_key)

        if email.strip() == "linster749@gmail.com" and password.strip()=="10020293":
            self.ids.email.text = ""
            self.ids.password.text = ""
            self.manager.transition.direction = 'left'
            self.manager.current = "admin_page"
        else:
            for i in request.json():
                if request.json()[i]["email"] == email.strip() and request.json()[i]["password"] == password.strip():
                    username = i
                    self.ids.email.text = ""
                    self.ids.password.text = ""
                    self.manager.current = "content_page"
                    self.manager.get_screen('content_page').username = username
                    break
            else:
                Snackbar(text="Invalid Credentials").open()

class ContentPage(Screen):

    Builder.load_file('Content.kv')
    url = "https://covidpriority-default-rtdb.firebaseio.com/.json"
    auth_key = "Z98flbpTP0dtaTZLF1TETqM7r1FktS74xOydjbWg"

    username = None

    def logout(self,*args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_page'
        
    def on_update_age(self,*args):
        self.age_popup = MDDialog(title="Select Age", type="custom",content_cls=AgePopup(),buttons=[MDFlatButton(text="CANCEL", on_release=self.close_age_dialog),MDFlatButton(text="ADD", on_release=self.patch_age)])
        self.age_popup.open()

    def close_age_dialog(self,*args):
        self.age_popup.dismiss()

    def patch_age(self,*args):
        age = self.age_popup.content_cls.ids.entered_age.text
        if not age.isdigit() or (int(age)<=0 or int(age)>150):
            Snackbar(text="Invalid Age").open()
        else:
            request = requests.get(self.url + '?auth=' + self.auth_key)

            new_patch = request.json()[self.username]
            new_patch["age"] = age
            new_patch = {self.username:new_patch}

            new_patch = json.dumps(new_patch)
            res = requests.patch(url=self.url, json=json.loads(new_patch))

            self.age_popup.content_cls.ids.entered_age.text = ''
            self.age_popup.dismiss()

    def on_update_job(self,*args):
        self.job_popup = MDDialog(title="Are You an Essential Worker?",text="Ex: Teacher, Healthcare Personnel, Truck Driver ...",buttons=[MDFlatButton(text="Yes",on_release=self.is_ew),MDFlatButton(text="No",on_release=self.not_ew)])
        self.job_popup.open()

    def show_details(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        information = []
        for i in request.json()[self.username]:
            if i=="medical condition":
                medical_list = ""
                for index,m in enumerate(request.json()[self.username]["medical condition"]):
                    if index == len(request.json()[self.username]["medical condition"])-1:
                        medical_list += m
                    else:
                        medical_list += m + ", "
                information.append(OneLineAvatarListItem(text=i + ": " + medical_list))
            else:
                information.append(OneLineAvatarListItem(text=i + ": " + request.json()[self.username][i]))
        self.details_dialog = MDDialog(title="personal details",type="simple",items=information)
        self.details_dialog.open()



    def is_ew(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        new_patch = request.json()[self.username]
        new_patch["essential worker"] = "Yes"
        new_patch = {self.username: new_patch}

        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))

        self.job_popup.dismiss()
    def not_ew(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)

        new_patch = request.json()[self.username]
        new_patch["essential worker"] = "No"
        new_patch = {self.username: new_patch}

        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))
        self.job_popup.dismiss()

    def checkforvac(self,*args):
        eligibility = None
        request = requests.get(self.url + '?auth=' + self.auth_key)
        d = request.json()
        if len(d[self.username]) < 5:
            Snackbar(text="Please Enter All Personal Info Before Checking for Eligibility").open()
        else:
            for key in d["MASTERACCOUNT"]:
                if key == "mc restrict":
                    if d["MASTERACCOUNT"]["mc restrict"] == ["None"]:
                        continue
                    else:
                        for medical in d["MASTERACCOUNT"]["mc restrict"]:
                            if medical not in d[self.username]["medical condition"]:
                                eligibility=False
                                break
                        break

                if key == "ew_restrict":
                    if d["MASTERACCOUNT"]["ew_restrict"] == "Yes" and d[self.username]["essential worker"] == "No":
                        eligibility = False
                        break
                if key == "age_restrict":
                    age_range = d["MASTERACCOUNT"]["age_restrict"].split()
                    lower = int(age_range[0])
                    upper = int(age_range[1])
                    if not (lower <= int(d[self.username]["age"]) <= upper):
                        eligibility = False
                        break
            if eligibility is None:
                self.eligibility_dialog = MDDialog(title="Eligibilty Status", text="You are eligible to be vaccinated")
                self.eligibility_dialog.open()
            else:
                self.eligibility_dialog = MDDialog(title="Eligibilty Status", text="You are not eligible to be vaccinated yet")
                self.eligibility_dialog.open()

    def update_mc(self,*args):
        conditions = ["Cancer","Kidney Disease","Lung Diseases","Dementia","Diabetes","Down Syndrome","Heart Conditions","HIV","Weak Immune System","Liver Disease","Obese","Pregnant","Sickle Cell Disease","None"]
        medical_items = [Item(text=i) for i in conditions]
        self.dialog = MDDialog(title="Select Applicable Medical Conditions",type="confirmation",items=medical_items,buttons=[MDFlatButton(text="CANCEL",on_release=self.close_medical_dialog),MDFlatButton(text="OK",on_release=self.patch_conditions),],)
        self.dialog.open()
    def patch_conditions(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        new_patch = request.json()[self.username]

        new_patch["medical condition"] = MemberCheckbox().checked_medical_items
        new_patch = {self.username: new_patch}
        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))
        MemberCheckbox.checked_medical_items = []
        self.dialog.dismiss()

    def close_medical_dialog(self,*args):
        self.dialog.dismiss()

class AdministrationPage(Screen):

    Builder.load_file('Admin.kv')
    url = "https://covidpriority-default-rtdb.firebaseio.com/.json"
    auth_key = "Z98flbpTP0dtaTZLF1TETqM7r1FktS74xOydjbWg"

    def on_restrict_age(self,*args):
        self.age_restrict_popup = MDDialog(title="Set Age Parameters", type="custom",content_cls=RestrictAgePopup(),buttons=[MDFlatButton(text="CANCEL", on_release=self.close_age_dialog),MDFlatButton(text="ADD", on_release=self.restrict_age)])
        self.age_restrict_popup.open()

    def close_age_dialog(self):
        self.age_restrict_popup.dismiss()

    def restrict_age(self,*args):
        min_age = self.age_restrict_popup.content_cls.ids.min_age.text
        max_age = self.age_restrict_popup.content_cls.ids.max_age.text
        if (not min_age.isdigit()) or (not max_age.isdigit()) or (int(max_age)>150) or (int(min_age)<1) or (int(max_age) < int(min_age)):
            Snackbar(text="Invalid Age Range").open()
        else:
            request = requests.get(self.url + '?auth=' + self.auth_key)
            new_patch = request.json()["MASTERACCOUNT"]
            new_patch["age_restrict"] = min_age + ' ' + max_age
            new_patch = {"MASTERACCOUNT": new_patch}
            new_patch = json.dumps(new_patch)
            res = requests.patch(url=self.url, json=json.loads(new_patch))

        self.age_restrict_popup.dismiss()

    def on_restrict_job(self,*args):
        self.ew_popup = MDDialog(title="Occupation Parameters",text="Limit to Only Essential Workers?",buttons=[MDFlatButton(text="Yes", on_release=self.only_ew),MDFlatButton(text="No", on_release=self.all_workers)])
        self.ew_popup.open()

    def only_ew(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        new_patch = request.json()["MASTERACCOUNT"]
        new_patch["ew_restrict"] = "Yes"
        new_patch = {"MASTERACCOUNT": new_patch}
        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))
        self.ew_popup.dismiss()

    def all_workers(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        new_patch = request.json()["MASTERACCOUNT"]
        new_patch["ew_restrict"] = "No"
        new_patch = {"MASTERACCOUNT": new_patch}
        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))
        self.ew_popup.dismiss()

    def on_restrict_mc(self,*args):
        conditions = ["Cancer","Kidney Disease","Lung Diseases","Dementia","Diabetes","Down Syndrome","Heart Conditions","HIV","Weak Immune System","Liver Disease","Obese","Pregnant","Sickle Cell Disease","None"]
        medical_items = [Item2(text=i) for i in conditions]
        self.mc_restict_dialog = MDDialog(title="Select Medical Condition Parameters",type="confirmation",items=medical_items,buttons=[MDFlatButton(text="CANCEL",on_release=self.close_medical_dialog),MDFlatButton(text="OK",on_release=self.patch_restrict_conditions),],)
        self.mc_restict_dialog.open()

    def patch_restrict_conditions(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        new_patch = request.json()["MASTERACCOUNT"]
        if "None" in AdminCheckbox().checked_parameter_items:
            new_patch["mc restrict"] = ["None"]
        else:
            new_patch["mc restrict"] = AdminCheckbox().checked_parameter_items
        new_patch = {"MASTERACCOUNT": new_patch}
        new_patch = json.dumps(new_patch)
        res = requests.patch(url=self.url, json=json.loads(new_patch))

        AdminCheckbox.checked_parameter_items = []

        self.mc_restict_dialog.dismiss()

    def close_medical_dialog(self):
        self.mc_restict_dialog.dismiss()

    def logout(self,*args):
        self.manager.transition.direction = 'right'
        self.manager.current = 'login_page'

    def show_parameters(self,*args):
        request = requests.get(self.url + '?auth=' + self.auth_key)
        information = []
        for i in request.json()["MASTERACCOUNT"]:
            if i == "age_restrict":
                information.append(OneLineAvatarListItem(text=f'Eligible Ages: {request.json()["MASTERACCOUNT"]["age_restrict"].split()[0]} to {request.json()["MASTERACCOUNT"]["age_restrict"].split()[1]}'))
            elif i == "ew_restrict":
                information.append(OneLineAvatarListItem(text=f'Must Be Essential Workers?: {request.json()["MASTERACCOUNT"]["ew_restrict"]}'))
            elif i=="mc restrict":
                medical_list = ""
                for index,m in enumerate(request.json()["MASTERACCOUNT"]["mc restrict"]):
                    if index == len(request.json()["MASTERACCOUNT"]["mc restrict"])-1:
                        medical_list += m
                    else:
                        medical_list += m + ", "
                information.append(OneLineAvatarListItem(text="Required Medical Conditions: " + medical_list))
        self.paramter_dialog = MDDialog(title="Required Parameters for Eligibility",type="simple",items=information)
        self.paramter_dialog.open()

class MemberCheckbox(IRightBodyTouch, MDBoxLayout):
    Builder.load_file('Right.kv')

    icon = StringProperty()
    text = StringProperty()
    checked_medical_items = []
    def on_checkbox_active(self,checkbox,value,text):
        if value:
            self.checked_medical_items.append(text)
        else:
            self.checked_medical_items.remove(text)
class Item(OneLineAvatarIconListItem):
    Builder.load_file('Item.kv')

    right_icon = StringProperty()
    right_text = StringProperty()
class Item2(OneLineAvatarIconListItem):
    Builder.load_file('Item2.kv')

    right_icon = StringProperty()
    right_text = StringProperty()
class AdminCheckbox(IRightBodyTouch, MDBoxLayout):
    Builder.load_file('Right2.kv')

    icon = StringProperty()
    text = StringProperty()
    checked_parameter_items = []
    def on_restrict_checkbox_active(self,checkbox,value,text):
        if value:
            self.checked_parameter_items.append(text)
        else:
            self.checked_parameter_items.remove(text)

class AgePopup(BoxLayout):
    Builder.load_file('AgePopup.kv')
class RestrictAgePopup(BoxLayout):
    Builder.load_file('RestrictAgePopup.kv')


class MainApp(MDApp):

    def build(self):
        screen_manager = ScreenManager()
        screen_manager.add_widget(LoginPage(name='login_page'))
        screen_manager.add_widget(SignupPage(name='signup_page'))
        screen_manager.add_widget(ContentPage(name='content_page'))
        screen_manager.add_widget(AdministrationPage(name='admin_page'))
        return screen_manager



if __name__ == '__main__':
    MainApp().run()
