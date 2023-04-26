class VideoInfo:
    ''' Describe details of an video which includes:

        'designatio' 'title' 'cover_url' 'date' 'length'
        'director' 'maker' 'label' 'genres' 'cast'
    '''

    def __init__(self, designatio):
        # Video attributes
        self.designatio = designatio.upper()
        self.title = ""
        self.outline = ""
        self.fanart = bytes()
        self.poster = bytes()
        self.thumb = bytes()
        self.fanart_path = ""
        self.poster_path = ""
        self.thumb_path = ""
        self.cover_url = ""
        self.date = ""
        self.length = ""
        self.director = ""
        self.maker = ""
        self.label = ""
        self.review = ""
        self.mpaa = "JP-18+"
        self.series = []
        self.genres = []
        self.cast = []
        self.is_subtitle = False
        self.is_uncensored = False
        self.is_4K = False

    def __str__(self):
        return '''\n
    番号\t{0.designatio}
    标题\t{0.title}
    发行日期\t{0.date}
    影片长度\t{0.length}
    导演\t{0.director}
    制作商\t{0.maker}
    发行商\t{0.label}
    评分\t{0.review}
    系列\t{0.series}
    类别\t{0.genres}
    演员\t{0.cast}
    简介\t{0.outline}\n'''.format(self)

    def todict(self):
        vars_dict = vars(self)
        if self.is_subtitle:
            vars_dict['genres'].append("中文字幕")

        if self.is_uncensored:
            vars_dict['genres'].append("无码流出")

        if self.is_4K:
            vars_dict['genres'].append("4K")

        return vars_dict
