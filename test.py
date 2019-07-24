

from pikax.pikax import Pikax, settings


def main():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)
    results = pixiv.search(keyword='初音', limit=200, mode='r18', popularity=1000)
    new_results = (results.likes > 1000) - (results.views < 50000)
    pixiv.download(new_results)



if __name__ == '__main__':
    main()
