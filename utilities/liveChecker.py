import requests

def isLive(username):
    contents = requests.get(f'https://twitch.tv/{username}').content.decode('utf-8')

    if 'isLiveBroadcast' in contents:
        return True
    
    return False


if __name__ == "__main__":
    print(isLive('nitthenat'))