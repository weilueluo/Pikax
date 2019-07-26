

from pikax.pikax import Pikax, settings


def main():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)
    results_a = pixiv.search(keyword='arknights', limit=600, mode='r18')
    results_b = pixiv.search(keyword='Fate/GrandOrder', limit=1000, mode='r18')

    new_results = (((results_b.views > 10000).likes > 1000).comments <= 500) - ((results_a.likes > 1000).views >= 50000)
    pixiv.download(new_results)



if __name__ == '__main__':
    main()
