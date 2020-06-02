import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

class Data:
        def __init__(self, api_key, project_token):
                self.api_key = api_key
                self. project_token = project_token
                self. params = {
                        "api_key" : self.api_key
                }
                self.data = self.get_data()
        
        def get_data(self):
                response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data', params=self.params)
                data = json.loads(response.text)
                return data
        def get_total_cases(self):
                total = self.data['total'][0]
                return total['value']
        def get_total_deaths(self):
                total = self.data['total'][1]
                return total['value']
        def get_total_recovered(self):
                total = self.data['total'][2]
                return total['value']
        def get_country_data(self, country_name):
                countryData = self.data['country']
                
                for country in countryData:
                        if country["name"].lower() == country_name.lower():
                                return country
        def get_list_of_countries(self):
                countries = []
                for country in self.data["country"]:
                        countries.append(country["name"].lower())
                return countries

        def update_data(self):
                response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run', params=self.params)

                def poll():
                        time.sleep(0.1)
                        old_data = self.data
                        while True:
                                new_data = self.get_data()
                                if new_data != old_data:
                                        self.data = new_data
                                        print("Data updated")
                                        break
                                time.sleep(5)


                t = threading.Thread(target=poll)
                t.start()






def getAPI():
        with open("api.txt", "r") as fp:
                tokens = fp.readlines() 
                return tokens
        
def speak(text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

def get_audio():
        r = sr.Recognizer()
        with sr.Microphone() as source:
                audio = r.listen(source)
                said =""

                try:
                        said = r.recognize_google(audio)
                except Exception as e:
                        print("Exception", str(e))
        return said.lower()

def main():
        #Read your api key, project token and run token
        authList = getAPI()
        API_KEY = authList[0].strip()
        PROJECT_TOKEN = authList[1].strip()
        RUN_TOKEN = authList[0].strip()
        data = Data(API_KEY, PROJECT_TOKEN)
        countries = data.get_list_of_countries()

        print("Welcom to the Covid-19 voice assistant")
        speak("Welcom to the Covid-19 voice assistant")
        END_PHRASE = "done"
        
        TOTAL_PATTERNS = {
                re.compile("[\w\s]+ total [\w\s]+ cases") :data.get_total_cases,
                re.compile("[\w\s]+ cases") :data.get_total_cases,
                re.compile("[\w\s]+ total cases"): data.get_total_cases,
                re.compile("[\w\s]+ total [\w\s]+ deaths") :data.get_total_deaths,
                re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
                re.compile("[\w\s]+ deaths"): data.get_total_deaths,
        }

        COUNTRY_PATTERNS = {
                re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)['total_cases'],
                re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)['total_deaths'],

        }

        UPDATE_COMMAND = "update"
        while True:
                print("Listening...")
                audioText = get_audio()
                print(audioText)
                result = None
                run_total_cases = True
                for pattern, func in COUNTRY_PATTERNS.items():
                        if pattern.match(audioText):
                                words = set(audioText.split(" "))
                                for country in countries:
                                        if country in words:
                                                result = func(country)
                                                run_total_cases = False
                                                break
                if run_total_cases:
                        for pattern, func in TOTAL_PATTERNS.items():
                                if pattern.match(audioText):
                                        result = func()
                                        break

                if audioText.find(UPDATE_COMMAND) != -1:
                        data.update_data()
                        result = "Data is being updated. This may take a moment"
        
                
                if result:   
                        print(result)
                        speak(result)

                if audioText.find(END_PHRASE) != -1:
                        print("Exit...")
                        speak("Thank you for using the Covid 19 voice assistant")
                        exit()      
                        

        


if __name__ == "__main__":
    main()