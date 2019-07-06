from yyets import YYETS
from multiprocessing import Process
import sys
from time import ctime

class Schedule:

    def threads(self):
        p = Process(target=self.geted2k())
        p.start()

    def geted2k(self):
        # print('开始执行info。{}'.format(ctime()))
        data = yyets.getMovieInfo()
        yyets.insertTable(data)
        # print('开始执行ed2k。{}'.format(ctime()))
        keyAPI = yyets.getKeyAPI(yyets.id)
        # print(keyAPI)
        ed2kURL = yyets.getDownloadURL(keyAPI)
        # print(ed2kURL)
        print('《{0}》电影地址为：\n{1}'.format(yyets.name, ed2kURL))
        data = dict(zip(('movieID', 'name', 'originalName'), (yyets.id, yyets.name, yyets.originalName)))
        data.update(ed2k=ed2kURL)
        yyets.insertTable(data, table='getmovie')

    def main(self):
        while True:
            movieName = input('请输入要查询的电影名字以获取下载地址，e退出：')
            if movieName == 'e':
                sys.exit()
            else:
                if movieName.isalpha():
                    movieNameSQL = '%' + movieName + '%'
                else:
                    i = len(movieName) - 1
                    movieNameSQL = '%' + movieName[:i] + '%' + movieName[i] + '%'
                cursor = yyets.selectTable('getmovie', 'name', movieNameSQL)
                n = cursor.rowcount
                if n == 0:
                    print('该影片在数据库中没有，将在网上查找……')
                    yyets.getMovieBasic(keyword=movieName)
                    self.threads()
                if n >= 1:
                    t = []
                    row = cursor.fetchone()
                    while row:
                        key = input('《{0}》({1}),是这部么？(y确定，n继续)'.format(row[1], row[2]))
                        if key == 'y':
                            cursor = yyets.selectTable('movieinfo', 'movieID', row[0])
                            inforow = cursor.fetchone()
                            t = ['名称', '原名', '地区', '语言', '首播', '类型', 'IMDB', '导演', '主演', '内容介绍']
                            tell = [inforow[1], inforow[2], inforow[4], inforow[5], inforow[6], inforow[8], inforow[9],
                                    inforow[12], inforow[13], inforow[14]]
                            for i in range(10):
                                print(t[i] + '：' + tell[i])
                            print(row[3])
                            break
                        elif key == 'n':
                            t.append('《' + row[1] + '》')
                            row = cursor.fetchone()
                            continue
                        else:
                            sys.exit()
                    if row == None:
                        print('将在网上为您查找……')
                        yyets.getMovieBasic(movieName, t)
                        self.threads()

if __name__=='__main__':
    yyets=YYETS()
    schedule=Schedule()
    schedule.main()
