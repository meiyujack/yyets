from yyets import YYETS

def main():
    yyets=YYETS()
    t=yyets.getMovieBasic()
    yyets.getMovieInfo()
    url=yyets.getKeyURL(t[0])
    yyets.getDownloadURL(url)

if __name__=='__main__':
    main()