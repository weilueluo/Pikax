

from pikax.pikax import Pikax, settings
from pikax.items import User


def main():
    pixiv = Pikax()
    pixiv.login(settings.username, settings.password)  # 不必要但强烈推荐
    results = pixiv.rank(limit=20, content='illust', type='daily', mode='safe')
    pixiv.download(results, folder='#Pixiv_daily_ranking')



if __name__ == '__main__':
    main()
