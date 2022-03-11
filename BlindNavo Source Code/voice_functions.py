import Mic_functs
from Mic_functs import Speak, TextToSpeech, mic_record

def ask_directions():
    Speak('/home/pi/Directions_for_the_blind/Audio_Files/ask.mp3')
    user_destination = mic_record()
    print(user_destination)
    confirm = 'Is this where you would like to go? ' + str(user_destination)
    print(confirm)
    TextToSpeech(confirm, 'confirm')

    Speak('/home/pi/Directions_for_the_blind/Audio_Files/confirm.mp3')

    ##Question Y/N
    user_response = mic_record()
    print(user_response)
    confirmation = True

    if user_response == 'yes' or user_response == 'yeah':
        charting_for = 'Calculating for destination ' + str(user_destination)
        TextToSpeech(charting_for, 'Chart')
        print(user_destination)
        Speak('/home/pi/Directions_for_the_blind/Audio_Files/Chart.mp3')
        confirmation = False


    return confirmation, user_destination

def say_objects(object_list):
    master_text = ""
    for i in object_list:
        master_text = master_text + i + ' '

    master_text = 'There is a ' + master_text + 'in front of you'
    
    TextToSpeech(master_text, 'list objects')
    Speak('/home/pi/Directions_for_the_blind/Audio_Files/list objects.mp3')


