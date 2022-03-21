class Book:
    def __init__(self):
        self.info_page_url = None
        self.title = None

        # 這裡的 gid *不是* 網址上的號碼，而是以下 CSS_Selector 前面的號碼
        # img[src^="https://"][src$="/cover.jpg"],img[src^="https://"][src$="/cover.png"]
        self.gid = None
        self.max_page = 0

        # {'1.jpg', '2.png' ...}
        self.image_names: set = set()
